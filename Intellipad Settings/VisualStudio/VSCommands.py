#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import sys
import System
import Microsoft
import Common

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def InitializeCore(value):
    global Core
    Core = value
    Common.Initialize(Core)

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ActivateOrOpenBuffer', None)
def ActivateOrOpenBuffer(target, sender, args):
    Common.ActivateOrOpenBufferHandler(True, sender, args)
            
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CloseBufferView', 'Ctrl+Shift+W')
def CloseBufferView(target, sender, args):
    from Microsoft.Intellipad.Host import HostWindow
  
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)  
    if hostWindow.BufferViews.Count == 1:
        hostWindow.Close()
        return
    
    buffer = sender.Buffer
    views = [view for view in hostWindow.BufferViews if view.Buffer is buffer]
    if len(views) > 1:
        sender.Close()
    else:
        from Microsoft.Intellipad.Shell import NamedCommands 
        NamedCommands.FromName("{Microsoft.Intellipad}CloseBuffer").Execute(None, sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}DragDrop', None)
def DragDrop(target, sender, args):
    data = args.Parameter
    previousCursor = System.Windows.Input.Mouse.OverrideCursor
    System.Windows.Input.Mouse.OverrideCursor = System.Windows.Input.Cursors.Wait
    
    if data.GetDataPresent(System.Windows.DataFormats.FileDrop):
        filePaths = data.GetData(System.Windows.DataFormats.FileDrop)
        Common.OpenFilesInViewOrTab(True, filePaths, sender)
        
    elif data.GetDataPresent(System.Windows.DataFormats.StringFormat):
        text = data.GetData(System.Windows.DataFormats.StringFormat)
        buffer = Common.BufferManager.GetBuffer(System.Uri('file://'))
        buffer.TextBuffer.Insert(0, text)
        
        Common.OpenBufferInViewOrTab(True, buffer, sender)
    
    System.Windows.Input.Mouse.OverrideCursor = previousCursor
    
@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}DragDrop')
def CanDragDrop(target, sender, args):
    data = args.Parameter
    if data.GetDataPresent(System.Windows.DataFormats.FileDrop):
        args.CanExecute = True
        filePaths = data.GetData(System.Windows.DataFormats.FileDrop)
        
        # Specifically disallow directory drop
        for file in filePaths:
            if System.IO.Directory.Exists(file):
                args.CanExecute = False
                break         
    elif data.GetDataPresent(System.Windows.DataFormats.StringFormat):
        args.CanExecute = True
    else:
        args.CanExecute = False
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}OpenMru', None)
def OpenMru(target, sender, args):
    uri = args.Parameter
    if uri != None:
        Common.OpenMruInViewOrTab(True, uri, sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Open', 'Ctrl+O')
def OpenInNewTab(target, sender, args):
    Common.OpenBufferHandler(True, sender, args)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}OpenProjectItem', None)
def OpenProjectItem(target, sender, args):
    Common.OpenProjectItemHandler(True, args.Parameter, sender)
  
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}OpenStartFiles', None)
def OpenStartFiles(target, sender, args):
    hostWindow = Core.Host.TopLevelWindows[0]
    previousCursor = System.Windows.Input.Mouse.OverrideCursor
    System.Windows.Input.Mouse.OverrideCursor = System.Windows.Input.Cursors.Wait
    
    activeView = hostWindow.ActiveView
    if activeView == None: activeView = hostWindow.BufferViews[0]
    
    for uri in args.Parameter:
        Common.OpenUriInViewOrTab(True, uri, activeView)
            
    System.Windows.Input.Mouse.OverrideCursor = previousCursor
    
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ShowScriptWindow', None)
def ShowScriptWindow(target, sender, args):
    from Microsoft.Intellipad.Host import HostWindow
    
    hostWindow = sender
    
    script = Common.BufferManager.GetBuffer(System.Uri('transient://Script'))
    if not Common.HasView(hostWindow, script):
        view = hostWindow.ShowInRoot(script, 20.0)
        view.Mode = Core.ComponentDomain.GetBoundValue[System.Object]('{Microsoft.Intellipad}ScriptIMode')
    
