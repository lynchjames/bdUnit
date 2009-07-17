#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import clr
import sys
import System
import Microsoft
import Common
from Microsoft.Intellipad.Scripting import UnitTest

simpleInput = """\
<Project DefaultTargets="Compile" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
    <Target Name = "Compile">
        <Message Text="This is a test"/>
    </Target>
</Project>
""".replace("\n", "\r\n")

simpleOutput = """This is a test"""

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def Initialize(value):
    global Core
    Core = value
    Common.Initialize(Core)

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectMode')
def ImportProjectMode(value):
    global ProjectMode
    ProjectMode = value

@Metadata.ImportSingleValue('{Microsoft.Intellipad}TestHelper')
def TestHelperImport(value):
    global TestHelper
    TestHelper = value
    
@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectManager')
def InitializeProjectManager(value):
    global ProjectManager
    ProjectManager = value
    
def BuildProjectTest(input, expected):
    from System.IO import File
    from System.Windows.Controls import Orientation

    view = outputView = None
    projectFile = WriteFile(input, '.mproj')
    try:
        hostWindow = Core.Host.TopLevelWindows[0]
        view = TestHelper.Split(hostWindow.BufferViews[0], Orientation.Horizontal, "")
        view.Buffer = Common.BufferManager.GetBuffer(System.Uri(projectFile))
        context = ProjectManager.RegisterProject(view.Buffer)
        
        done = System.Threading.ManualResetEvent(False)
        
        def OnCompleted(sender, args):
            context.BuildAsyncCompleted -= OnCompleted
            done.Set()
        
        context.BuildAsyncCompleted += OnCompleted

        TestHelper.Execute('{Microsoft.Intellipad}BuildProject', None, view)
        
        done.WaitOne(30 * 1000, False)
        Common.DrainDispatcher()
        
        output = Common.BufferManager.GetBuffer(System.Uri('transient://output'))
        outputView = Common.GetView(hostWindow, output)
        assert outputView is not None, "Output view should be visible"
        
        assert outputView.EditorPrimitives.Caret.IsVisible, "The caret should be visible in the output view"
        assert outputView.EditorPrimitives.Caret.CurrentPosition == outputView.TextBuffer.CurrentSnapshot.Length, \
            "The caret should be at the end of the buffer (%d), but is instead at (%d)" % \
            (outputView.TextBuffer.CurrentSnapshot.Length, outputView.EditorPrimitives.Caret.CurrentPosition)
        TestHelper.AssertVisibleText(outputView)

        actual = TestHelper.GetText(outputView)
        assert actual.find(expected) != -1, "Expected '%s' but found '%s'" % (expected, actual)
    finally:
        if view.Buffer.Uri == System.Uri(projectFile):
            view.Buffer.Close()
        TestHelper.CloseViews([view, outputView])
        if File.Exists(projectFile):
            File.Delete(projectFile)
        
        
def BuildProjectSavesFilesTest():
    from System.IO import File, Path
    from System.Threading import Thread
    from System.Windows.Controls import Orientation
    from Microsoft.VisualStudio.Text import Span
    
    text = """module foo
{
    id : Integer32;
    name : Text;""".replace("\n", "\r\n")    # note missing \r\n}\r\n
    
    mSourceFile = WriteFile(text, '.m')
   
    text = """\
<Project DefaultTargets="Compile" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <!-- -->
  </ItemGroup>
</Project>
""".replace("\n", "\r\n")

    mProjectFile = WriteFile(text, '.mproj')
    
    hostWindow = Core.Host.TopLevelWindows[0]
    sourceView = hostWindow.ActiveView
    sourceView.Buffer = Common.BufferManager.GetBuffer(System.Uri(mSourceFile))

    projectBuffer = Common.BufferManager.GetBuffer(System.Uri(mProjectFile))
    projectView = TestHelper.SplitWithBuffer(hostWindow.BufferViews[0], Orientation.Horizontal, projectBuffer)
    assert Common.GetProject(projectBuffer) is not None, 'Must call RegisterProject to create projectContext for this test'
    
    text = text.replace('<!-- -->', '<Compile Include=\"%s\" />' % mSourceFile)
    span = Span(0, projectView.Buffer.TextBuffer.CurrentSnapshot.Length)
    projectView.Buffer.TextBuffer.Replace(span, text)
    Common.DrainDispatcher()
    
    sourceView.Buffer.TextBuffer.Insert(sourceView.Buffer.TextBuffer.CurrentSnapshot.Length, '\r\n}\r\n')
    Common.DrainDispatcher()

    try:
        assert projectView.Buffer.IsDirty, 'Project buffer was not marked dirty after edit'    
        assert sourceView.Buffer.IsDirty, 'M source buffer was not marked dirty after edit'

        TestHelper.Execute('{Microsoft.Intellipad}BuildProject', None, projectView)
        Common.DrainDispatcher()
        
        assert not projectView.Buffer.IsDirty, 'Dirty flag was not removed from Project buffer by Build'    
        assert not sourceView.Buffer.IsDirty, 'Dirty flag was not removed from M file buffer by Build'
        assert File.Exists(mProjectFile), 'Project file was not saved by build'
        
    finally:
        sourceView.Buffer.Close()
        projectView.Buffer.Close()
        projectView.Close()
        if File.Exists(mProjectFile):
            File.Delete(mProjectFile)
        File.Delete(mSourceFile)
    
    
def WriteFile(content, dotExtension):
    from System.IO import File, Path
    filename = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString('N'))
    filename = filename + dotExtension    
    File.WriteAllText(filename, content, System.Text.Encoding.UTF8)
    return filename   

        
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'TestBuildProject')
def TestBuildProject():
    class Test(UnitTest):
        def Run(self):
            BuildProjectTest(simpleInput, simpleOutput)
    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'TestBuildProjectSavesFiles')
def TestBuildProjectSavesFiles():
    class Test(UnitTest):
        def Run(self):
            BuildProjectSavesFilesTest()
    return Test()

