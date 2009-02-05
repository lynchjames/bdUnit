#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import clr
import sys
import System
import Microsoft
import Common

projectContent = """\
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="3.5" DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <MTarget>Repository</MTarget>
    <MPackageScript>true</MPackageScript>
    <MPackageImage>true</MPackageImage>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">AnyCPU</Platform>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <MTargetsPath Condition="$(MTargetsPath) == ''">$(MSBuildExtensionsPath32)\\Microsoft\\M\\v1.0</MTargetsPath>
    <ProjectName>Models</ProjectName>
    <RootNamespace>Models</RootNamespace>
    <AssemblyName>Models</AssemblyName>
    <TargetFrameworkVersion>v3.5</TargetFrameworkVersion>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug|AnyCPU' ">
    <OutputPath>bin\\Debug\\</OutputPath>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Release|AnyCPU' ">
    <OutputPath>bin\\Release\\</OutputPath>
  </PropertyGroup>
  <Import Project="$(MTargetsPath)\\MProject.targets" />
</Project>
""".replace('\n','\r\n')

Project = None

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def InitializeCore(value):
    global Core
    Core = value
    Common.Initialize(Core)

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectManager')
def InitializeProjectManager(value):
    global ProjectManager
    ProjectManager = value

def Save(projectContext):
    buffer = projectContext.ProjectBuffer
    Common.Clear(buffer)
    Common.Write(buffer, projectContext.MSBuildProject.Xml)
    # hack to replace utf-16 with utf-8
    buffer.TextBuffer.Replace(Microsoft.VisualStudio.Text.Span(30, 6), "utf-8")
    buffer.Save()

def ResetProjectContext(hostWindow, projectContext):
    clr.AddReferenceToFileAndPath('components\Microsoft.M.IntellipadPlugin\Microsoft.M.IntellipadPlugin')
    from Microsoft.M.IntellipadPlugin import MLanguageServiceItem
    from System.Xaml import AttachedPropertyServices

    #HACK: We need to reload the project context of all buffer-views already open. Bug 64045
    AttachedPropertyServices.RemoveProperty(projectContext, MLanguageServiceItem.MProjectInstanceProperty)
    for view in hostWindow.BufferViews:
        tempMode = view.Mode
        view.Mode = None
        view.Mode = tempMode # Triggers new Language Service Item

def MakeUniqueDir(path):
    for i in range(1, 100):
        dir = '%s%d' % (path, i)
        if not System.IO.Directory.Exists(dir):
            System.IO.Directory.CreateDirectory(dir)
            return (dir, i)
    raise ("Unable to create a new unique directory with prefix '%s'" % path)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}AddCurrentFileToProject', 'Ctrl+Shift+F1')
def AddCurrentFileToProject(target, sender, args):
    from System.Windows import MessageBox, MessageBoxButton, MessageBoxImage
    from Microsoft.Intellipad.Host import HostWindow
    from System.Xaml import AttachedPropertyServices
    from Microsoft.Intellipad.Shell import NamedCommands 
    
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    
    global Project
    if Project is None:
        projectsDir = System.Environment.ExpandEnvironmentVariables('%UserProfile%\Documents\Visual Studio 2008\Projects\Models')
        (dir, index) = MakeUniqueDir(projectsDir)
        tempFileName = "%s\Models%d.mproj" % (dir, index)
        System.IO.File.WriteAllText(tempFileName, projectContent, System.Text.Encoding.Unicode)   
        projectUri = System.Uri('file://' + tempFileName)
        NamedCommands.FromName("{Microsoft.Intellipad}OpenProject").Execute(projectUri, sender)
        projectBuffer = Common.BufferManager.GetBuffer(projectUri)
        Project = ProjectManager.GetContextFromProject(projectBuffer)
    
    if isinstance(Project, Microsoft.Intellipad.Host.MSBuildProjectContext):
        if isinstance(sender.Buffer, Microsoft.Intellipad.Host.FileBuffer) and sender.Buffer.IsUntitled:
            Common.SaveBuffer(sender.Buffer, sender)
            
        Project.MSBuildProject.AddNewItem('Compile', sender.Buffer.Uri.AbsolutePath)
        Save(Project)
    
    Project.AddItem(sender.Buffer.Uri)    
    AttachedPropertyServices.SetProperty(sender, Microsoft.Intellipad.LanguageServices.ProjectManager.ProjectContextProperty, Project)
    ResetProjectContext(hostWindow, Project)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}AddMReference', 'Ctrl+Shift+F2')
def AddMReference(target, sender, args):
    from System.Windows import MessageBox, MessageBoxButton, MessageBoxImage
    from Microsoft.Intellipad.Host import HostWindow
    from System.Xaml import AttachedPropertyServices
    from Microsoft.Intellipad.Shell import NamedCommands 
    
    (result, projectContext) = AttachedPropertyServices.TryGetProperty(sender, Microsoft.Intellipad.LanguageServices.ProjectManager.ProjectContextProperty)
    if not result:
        MessageBox.Show('There is no project context associated with this view', 'Intellipad', MessageBoxButton.OK, MessageBoxImage.Information)
        return
        
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    ofd = Microsoft.Win32.OpenFileDialog()
    ofd.Filter = 'M References (*.mx)|*.mx'
    
    if ofd.ShowDialog(hostWindow) == False:
        return
    
    if isinstance(projectContext, Microsoft.Intellipad.Host.MSBuildProjectContext):
        projectContext.MSBuildProject.AddNewItem('MReference', ofd.FileName)
        Save(projectContext)
    
    projectContext.AddItem(System.Uri(ofd.FileName))
    ResetProjectContext(hostWindow, projectContext)

def GetPropertyFinalValue(projectContext, property):
    for value in [item.FinalValue for item in projectContext.MSBuildProject.EvaluatedProperties if item.Name == property]:
        return value
    return None
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}DeployToRepository', 'Ctrl+Shift+F9')
def DeployToRepository(target, sender, args):
    if Project is None:
        Core.Notify('There is no project to deploy to the repository')

    projectDir = Project.MSBuildProject.GetEvaluatedProperty('MSBuildProjectDirectory')
    imageItem = list(Project.MSBuildProject.GetEvaluatedItemsByName('_MImageOutput'))[0]
    imagePath = projectDir + '\\' + imageItem.FinalItemSpec
    mtaskPath = GetPropertyFinalValue(Project, 'MTaskPath')
    mxPath = mtaskPath + '\\mx.exe'
    
    arguments = '/f /db:Repository /i:"%s"' % imagePath

    outputBuffer = Core.Host.BufferManager.GetBuffer(System.Uri('transient://output'))
    
    Common.WriteLine(outputBuffer, "Launching ""%s"" %s" % (mxPath, arguments))
    
    def ProcessOutput(sender, args):
        if args.Data != None:
            Common.WriteLine(outputBuffer, args.Data)
    
    from System.Diagnostics import Process
    process = Process()
    process.StartInfo.FileName = mxPath
    process.StartInfo.Arguments = arguments
    process.StartInfo.UseShellExecute = False
    process.StartInfo.RedirectStandardOutput = True
    process.EnableRaisingEvents = True
    process.OutputDataReceived += ProcessOutput
    process.Exited += lambda sender, args: Common.WriteLine(outputBuffer, "Done.")
    process.Start()
    process.BeginOutputReadLine()
