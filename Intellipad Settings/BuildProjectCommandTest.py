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

@Metadata.ImportSingleValue('{Microsoft.Intellipad}MSBuildProjectMode')
def MSBuildProjectMode(value):
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

    from System.Windows.Controls import Orientation
    view = outputView = None
    try:
        hostWindow = Core.Host.TopLevelWindows[0]
        view = TestHelper.Split(hostWindow.BufferViews[0], Orientation.Horizontal, "")
        Common.WriteLine(view, input)
        
        # manually wire this up as a "MSBuild Project"
        view.Mode = ProjectMode
        provider = view.LocalDomain.GetBoundValue[System.Object]("{Microsoft.Intellipad}ProjectContextProvider")
        context = provider.CreateProjectContext(view.Buffer)
        ProjectManager.TrackProject(context)
        
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
        
        actual = TestHelper.GetText(outputView)
        assert actual.find(expected) != -1, "Expected '%s' but found '%s'" % (expected, actual)
    finally:
        TestHelper.CloseViews([view, outputView])

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'TestBuildProject')
def TestBuildProject():
    class Test(UnitTest):
        def Run(self):
            BuildProjectTest(simpleInput, simpleOutput)
    return Test()
