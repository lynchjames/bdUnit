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
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}BuildProject', 'F6')
def BuildProject(target, sender, args):
    from Microsoft.Build.BuildEngine import ConsoleLogger, WriteHandler
    from Microsoft.Intellipad.LanguageServices import ListBufferHelper
    
    hostWindow = Microsoft.Intellipad.Host.HostWindow.GetHostWindowForBufferView(sender)
    outputBuffer = Core.Host.BufferManager.GetBuffer(System.Uri('transient://output'))

    view = Common.GetView(hostWindow, outputBuffer)
    if view is None:
        hostWindow.ShowInRoot(outputBuffer, 50.0)

    context = ProjectManager.GetProjectContextForBufferView(sender)
    if context is None:
        context = ProjectManager.GetContextFromProject(sender.Buffer)
    if context is None:
        Common.WriteLine(outputBuffer, "Active buffer '%s' is not a project or a member of a project" % sender.Buffer.Uri.ToString())
        return

    errorBuffer = Core.BufferManager.GetBuffer(System.Uri("transient://errors"))
    listBufferHelper = ListBufferHelper.Create(errorBuffer)
        
    def Invoke(callback): hostWindow.Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Normal, System.Action(callback))

    class WorkLogger(ConsoleLogger):
        def __init__(self):
            handler = WriteHandler(self.Write)
            ConsoleLogger.set_WriteHandler(self, handler)
            self.foundError = False
        def Initialize(self, eventSource, procCount):
            ConsoleLogger.Initialize(self, eventSource, procCount)
            eventSource.ErrorRaised += self.OnError
            eventSource.WarningRaised += self.OnWarning
            eventSource.BuildStarted += self.OnBuildStarted
        def OnBuildStarted(self, sender, args):
            Invoke(lambda: listBufferHelper.Items.Clear())
        def OnErrorOrWarning(self, args, type):
            if not self.foundError:
                self.foundError = True
                listBufferHelper.Items.Clear()

            if args.File is None or len(args.File) == 0:
                text = args.Message
            else:
                try:
                    if args.EndLineNumber == 0 or args.EndColumnNumber == 0:
                        text = "[%s#%s,%s] %s : %s" % (
                               System.Uri(args.File),
                               args.LineNumber, args.ColumnNumber,
                               type,
                               args.Message)
                    else:
                        text = "[%s#%s,%s-%s,%s] %s : %s" % (
                               System.Uri(args.File),
                               args.LineNumber, args.ColumnNumber,
                               args.EndLineNumber, args.EndColumnNumber,
                               type,
                               args.Message)
                except System.UriFormatException:
                    text = args.Message

            listBufferHelper.Items.Add(text)
        def OnError(self, sender, args):
            Invoke(lambda: self.OnErrorOrWarning(args, "Error"))
        def OnWarning(self, sender, args):
            Invoke(lambda: self.OnErrorOrWarning(args, "Warning"))
        def Write(self, message):
            Invoke(lambda: Common.Write(outputBuffer, message))

    logger = WorkLogger()
    
    context.BuildAsync(logger, None)
