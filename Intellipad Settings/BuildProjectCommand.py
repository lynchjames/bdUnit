#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import clr

clr.AddReference('Microsoft.Build.Engine, Version=3.5.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a')
clr.AddReference('IronPython')
clr.AddReference('System.Core, Version=3.5.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089')
clr.AddReference('Xaml')

import System
import Microsoft
import IronPython
import Common

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def InitializeCore(value):
    global Core
    Core = value
    Common.Initialize(Core)

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectManager')
def InitializeProjectManager(value):
    global ProjectManager
    ProjectManager = value
    
@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}BuildProject')
def CanBuildProject(target, sender, args):
    context = Common.GetProject(sender.Buffer)
    
    if context is None:
        args.CanExecute = False
        return
    else:
        # We do this after fetching the context to ensure that the Assembly is loaded
        expectedType = System.Type.GetType("Microsoft.Intellipad.Host.MSBuildProjectContext, Microsoft.Intellipad.Core")
        if expectedType is None:
            args.CanExecute = False
            return
        args.CanExecute = context.GetType() == expectedType

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}BuildProject', 'F6')
def BuildProject(target, sender, args):
    from Microsoft.Build.BuildEngine import ConsoleLogger, WriteHandler
    
    hostWindow = Microsoft.Intellipad.Host.HostWindow.GetHostWindowForBufferView(sender)
    outputBuffer = Core.Host.BufferManager.GetBuffer(System.Uri('transient://output'))

    view = Common.GetView(hostWindow, outputBuffer)
    if view is None:
        view = hostWindow.ShowInRoot(outputBuffer, System.Windows.Controls.Orientation.Horizontal, 50.0)
        Common.DrainDispatcher()

    context = Common.GetProject(sender.Buffer)
    
    if context is None:
        Common.WriteLine(outputBuffer, "Active buffer '%s' is not a project or a member of a project" % sender.Buffer.Title)
        return
            
    for buffer in Core.BufferManager.OpenBuffers:
        if Common.GetProject(buffer) is context and buffer.IsDirty: 
            buffer.Save()

    def BeginInvokeOnDispatcherThread(callback): 
        hostWindow.Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Normal, System.Action(callback))

    class OutputBufferLogger(ConsoleLogger):
        def __init__(self):
            self.WriteHandler = WriteHandler(self.Write)

        def Write(self, message):
            def WriteAndScroll():
                Common.Write(outputBuffer, message)
                view.EditorPrimitives.Caret.MoveToEndOfDocument()
                view.CenterEditor()
            BeginInvokeOnDispatcherThread(WriteAndScroll)

    logger = OutputBufferLogger()
    
    context.BuildAsync(logger, None)
