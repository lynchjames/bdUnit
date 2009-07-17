#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import sys
import System
import Microsoft
import Common
import FindHelper

# strings
WelcomeMessage = 'Welcome to Intellipad.'
RunTestWithDirtyBufferMessage = 'Error: Self Test is not run because there are unsaved buffers. Please save or discard them and try again.'
FilesOpeningNotSupportedMessage = 'The following file(s) were not opened:'

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def InitializeCore(value):
    global Core, Host
    Core = value
    Host = Core.Host
    Common.Initialize(Core)
    FindHelper.Initialize(Core)

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectManager')
def InitializeProjectManager(value):
    global ProjectManager
    ProjectManager = value

@Metadata.ImportSingleValue('{Microsoft.Intellipad}BufferManager')
def InitializeBufferManager(value):
    global BufferManager
    BufferManager = value

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ActivateOrOpenBuffer', None)
def ActivateOrOpenBuffer(target, sender, args):
    Common.ActivateOrOpenBuffer(sender, args)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ActivateOrOpenBufferFromBufferView', None)
def ActivateOrOpenBufferFromBufferView(target, sender, args):
    from Microsoft.Intellipad.Shell import NamedCommands
    NamedCommands.FromName('{Microsoft.Intellipad}ActivateOrOpenBuffer').Execute(args.Parameter, Core.Host.TopLevelWindows[0])

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}DragDrop', None)
def DragDrop(target, sender, args):
    previousCursor = System.Windows.Input.Mouse.OverrideCursor
    System.Windows.Input.Mouse.OverrideCursor = System.Windows.Input.Cursors.Wait

    data = args.Parameter    
    if data.GetDataPresent(System.Windows.DataFormats.FileDrop):
        filePaths = data.GetData(System.Windows.DataFormats.FileDrop)
        filePathsWithNoDirectory = [filePath for filePath in filePaths if System.IO.File.Exists(filePath)]
        filePathsWithDirectory = [filePath for filePath in filePaths if not System.IO.File.Exists(filePath)]
        Common.OpenFilesInActiveView(filePathsWithNoDirectory, sender)
        if filePathsWithDirectory.Count > 0:
            Host.Notify(FilesOpeningNotSupportedMessage)
            for dir in filePathsWithDirectory:
                Host.Notify(' ' + dir)
        
    elif data.GetDataPresent(System.Windows.DataFormats.StringFormat):
        text = data.GetData(System.Windows.DataFormats.StringFormat)
        buffer = Common.BufferManager.GetBuffer(System.Uri('file://'))
        buffer.TextBuffer.Insert(0, text)
        
        Common.OpenBufferInActiveView(buffer, sender)
    
    System.Windows.Input.Mouse.OverrideCursor = previousCursor
    
@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}DragDrop')
def CanDragDrop(target, sender, args):
    data = args.Parameter
    if data.GetDataPresent(System.Windows.DataFormats.FileDrop):
        args.CanExecute = True
        filePaths = data.GetData(System.Windows.DataFormats.FileDrop)
        
    elif data.GetDataPresent(System.Windows.DataFormats.StringFormat):
        args.CanExecute = True
    else:
        args.CanExecute = False
        
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}OpenMru', None)
def OpenMru(target, sender, args):
    uri = args.Parameter
    if uri != None:
        Common.OpenMruInActiveView(uri, sender)
   
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}OpenProjectItem', None)
def OpenProjectItem(target, sender, args):
    Common.OpenProjectItemHandler(args.Parameter, sender)
  
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}OpenStartFiles', None)
def OpenStartFiles(target, sender, args):
    hostWindow = Core.Host.TopLevelWindows[0]
    previousCursor = System.Windows.Input.Mouse.OverrideCursor
    System.Windows.Input.Mouse.OverrideCursor = System.Windows.Input.Cursors.Wait
    
    activeView = hostWindow.ActiveView
    if activeView == None: activeView = hostWindow.BufferViews[0]
    
    for uri in args.Parameter:
        Common.OpenUriInActiveView(uri, activeView)
        
    System.Windows.Input.Mouse.OverrideCursor = previousCursor   
   
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Open', 'Ctrl+O')
def OpenBuffer(target, sender, args):
    Common.OpenBuffer(sender, args)
            
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShowScriptWindow', None)
def ShowScriptWindow(target, sender, args):
    from Microsoft.Intellipad.Host import HostWindow
    
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    
    script = Common.BufferManager.GetBuffer(System.Uri('transient://Script'))
    sender.Buffer = script
    sender.Mode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}PythonInteractiveMode')   
                
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}RunTests', 'Ctrl+R,A')
def RunTests(target, sender, args):
    if Common.HasDirtyBuffers():
        Host.Notify(RunTestWithDirtyBufferMessage)
        return
        
    Common.RunAllTests()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShrinkBufferViewHorizontal', 'Ctrl+OemComma')
def ShrinkBufferViewHorizontal(target, sender, args):
    Common.ChangeBufferViewLength(sender, 0.9, System.Windows.Controls.Orientation.Horizontal)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ExpandBufferViewHorizontal', 'Ctrl+OemPeriod')
def ExpandBufferViewHorizontal(target, sender, args):
    Common.ChangeBufferViewLength(sender, 1.0/0.9, System.Windows.Controls.Orientation.Horizontal)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShrinkBufferViewVertical', 'Ctrl+Shift+OemComma')
def ShrinkBufferViewVertical(target, sender, args):
    Common.ChangeBufferViewLength(sender, 0.9, System.Windows.Controls.Orientation.Vertical)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ExpandBufferViewVertical', 'Ctrl+Shift+OemPeriod')
def ExpandBufferViewVertical(target, sender, args):
    Common.ChangeBufferViewLength(sender, 1.0/0.9, System.Windows.Controls.Orientation.Vertical)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}New', 'Ctrl+N')
def New(target, sender, args):
    buffer = Common.BufferManager.GetBuffer(System.Uri("file://"))
    Common.Host.TopLevelWindows[0].ShowBuffer(buffer)
        
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}HelpCommands', 'F1')
def HelpCommands(target, window, args):
    from Microsoft.Intellipad.Shell import CommandMetadata
    from Microsoft.Intellipad.Shell import KeyChordGestureCollectionConverter

    help = Common.BufferManager.GetBuffer(System.Uri('transient://helpcommands'))
    view = Common.GetView(window, help)
    if view is not None:
        Common.SetActiveView(view)
        return
    
    Common.Clear(help)
     
    miniBufferMode = Core.ComponentDomain.GetExportedObject[System.Object]("{Microsoft.Intellipad}MiniBufferMode");
    miniBuffer = Common.BufferManager.GetBuffer(System.Uri('transient://mini-buffer'))
    commandList = miniBufferMode.GetCommands(miniBuffer)

    commandHeader = 'Mini Buffer Commands'
    commandIndent = 2
    commandNameLength = len(commandHeader)
    for commandName in commandList:
        if len(commandName) + commandIndent > commandNameLength:
            commandNameLength = len(commandName) + commandIndent 
    commandNameLength += commandIndent 

    Common.WriteLine(help, '')
    Common.WriteLine(help, '<heading1>' + commandHeader + '</heading1>')    
    
    for commandName in sorted(commandList , lambda x,y: x > y):
        openBracketPos = commandName.find("(")
        openBracketPos = openBracketPos + 1
        closeBracketPos = commandName.find(")")

        if openBracketPos >= 0:
            Common.Write(help, " " * commandIndent + "<normal>" + commandName[0:openBracketPos])
            Common.Write(help, "<subtleEmphasis>" + commandName[openBracketPos:closeBracketPos] + "</subtleEmphasis>")
            Common.WriteLine(help, commandName[closeBracketPos:] + "</normal>")
        else:
            Common.WriteLine(help, (" " * commandIndent) + "<normal>" + commandName + "</normal>")
    
    def GetHelp(binding):
        name = CommandMetadata.GetCommandName(binding)
        keyGestures = CommandMetadata.GetCommandKeys(binding)
        keys = KeyChordGestureCollectionConverter.GesturesToString(keyGestures)
        if len(keys) == 0 :
            keys = 'none'
        return {'name': name, 'key': keys }
        
    commandBindingsProvider = Core.ComponentDomain.GetExportedObject[System.Object]("{Microsoft.Intellipad.Shell}CommandBindingsProvider")
    bindings = commandBindingsProvider.GetCommandBindings()
    dict = [GetHelp(binding) for binding in bindings]
    
    nameLength = 0
    keyLength = 0
    
    for binding in dict:
        if len(str(binding['key'])) > keyLength :
            keyLength  = len(str(binding['key']))
        if len(str(binding['name'])) > nameLength:
            nameLength = len(str(binding['name']))
    
    keyLength += 2
    nameLength += 2
    
    formatText = '<heading3>%(key)' + str(keyLength) + 's</heading3>: <normal>%(name)s</normal>'
    
    Common.WriteLine(help, '')
    Common.WriteLine(help, "<heading1>Commands and Gestures</heading1>")
    for binding in sorted(dict, lambda x,y: str(x['name']) > str(y['name'])):
        Common.WriteLine(help, formatText % binding)
    
        
    class AssemblyInfo:
        attributeDict = {  "AssemblyTitle" : "Title", "AssemblyFileVersion" : "Version", "AssemblyProduct" : "Product", "AssemblyCopyright" : "Copyright" }
        def __init__(self, assembly):
            self.assembly = assembly
        
        def has_key(self, key)  :
            return key in self.attributeDict
                    
        def __getitem__(self, key):
            if(key not in self.attributeDict): return ''
            attributeType = System.Type.GetType('System.Reflection.%sAttribute' % key)
            attribute = System.Attribute.GetCustomAttribute(self.assembly, attributeType)
            if(attribute is None) : return ''
            else: return getattr(attribute, self.attributeDict[key])
        
        def __contains__(self, item)  :
            return self.has_key(item)
    
    ipadAssembly = System.Reflection.Assembly.GetEntryAssembly()
    ipadAssemblyInfo = AssemblyInfo(ipadAssembly)
    
    infoTemplate1 = u'''<subtle>%(AssemblyTitle)s (%(AssemblyFileVersion)s), %(AssemblyProduct)s</subtle>'''
    infoTemplate2 = u'''<subtle>%(AssemblyCopyright)s</subtle>'''
    
    Common.WriteLine(help, '')
    Common.WriteLine(help, infoTemplate1 % ipadAssemblyInfo)
    Common.WriteLine(help, infoTemplate2 % ipadAssemblyInfo)
    
    Common.SetReadOnly(help)

    rtMode = Core.ComponentDomain.GetExportedObjectOrDefault[System.Object]("{Microsoft.Intellipad}RichTextMode")
    if rtMode is not None:
        help.SetDefaultMode(rtMode)

    window.ActiveView.Buffer = help
        
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CloseBuffer', 'Ctrl+F4')
def CloseBuffer(target, sender, args):
    from Microsoft.Intellipad.Host import HostWindow
    
    if args.Parameter != None:
        buffer = args.Parameter
        hostWindow = Core.Host.TopLevelWindows[0]
    else:
        buffer = sender.Buffer
        hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    
    Common.CloseBuffer(buffer, sender)
    
    if hostWindow.BufferViews.Count == 0:
        hostWindow.Close()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CloseBufferView', 'Ctrl+Shift+W')
def CloseBufferView(target, sender, args):
    from Microsoft.Intellipad.Host import HostWindow
  
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)  
    if hostWindow.BufferViews.Count == 1:
        hostWindow.Close()
    else:
        sender.Close()
        
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}Exit', 'Alt+F4')
def Exit(target, sender, args):
    sender.Close()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewRight', 'Alt+Right')
def FocusBufferViewRight(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindRight(sender), lambda point: point.Y)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewLeft', 'Alt+Left')
def FocusBufferViewLeft(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindLeft(sender), lambda point: point.Y)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewUp', 'Alt+Up')
def FocusBufferViewUp(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindUp(sender), lambda point: point.X)
  
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewDown', 'Alt+Down')
def FocusBufferViewDown(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindDown(sender), lambda point: point.X)
  
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}Primer', None)
def Primer(target, window, args):
    primerPath = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}CorePath')
    primerBuffer = Common.BufferManager.GetBuffer(System.Uri('file://' + primerPath + '\\Settings\\IntellipadPrimer.ipadhelp'))
    
    rtMode = Core.ComponentDomain.GetExportedObjectOrDefault[System.Object]("{Microsoft.Intellipad}RichTextMode")
        
    view = Common.GetView(window, primerBuffer)
    if view is not None:
        Common.SetActiveView(view)
        return

    Common.SetReadOnly(primerBuffer)
    window.ActiveView.Buffer = primerBuffer
    Common.ActivateWordWrap(window.ActiveView)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleBehavior', None)
def ToggleBehaviorCommand(target, sender, args):
    Common.ToggleBehavior(args.Parameter, sender)  

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleLineNumber', 'Ctrl+Shift+L')
def ToggleLineNumber(target, sender, args):
    from Microsoft.Intellipad.Host import LineNumberBehaviorProvider
    Common.ToggleBehavior(LineNumberBehaviorProvider.UniqueId, sender)
  
@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Save')
def CanSave(target, sender, args):
    canExecute = sender.Buffer.CanSave and sender.BufferTransform == None
    canExecute = canExecute or sender.Buffer.Uri.Scheme == 'file' and not System.IO.File.Exists(sender.Buffer.Uri.LocalPath)
    args.CanExecute = canExecute

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Save', 'Ctrl+S')
def Save(target, sender, args):
    Common.SaveBuffer(sender.Buffer, sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SaveACopy', None)
def SaveACopy(target, sender, args):
    Common.SaveACopy(sender.Buffer, sender)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SaveAs')
def CanSaveAs(target, sender, args):
    args.CanExecute = sender.Buffer.Uri.Scheme == 'file' and sender.BufferTransform == None

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SaveAs', None)
def SaveAs(target, sender, args):
    Common.SaveAsBuffer(sender.Buffer, sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}SaveAll', 'Ctrl+Shift+S')
def SaveAll(target, sender, args):
    Common.SaveAll(sender)
                
@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitHorizontal')
def CanSplitVertical(target, sender, args):
    args.CanExecute = not sender.ActualHeight < 100
        
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitHorizontal', 'Ctrl+W,OemMinus')
def CreateVerticalSplit(target, sender, args):
    from System.Windows.Controls import Orientation
    from Microsoft.Intellipad.Host import HostWindow
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    hostWindow.SplitBufferView(sender, Orientation.Vertical)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitVertical')
def CanSplitHorizontal(target, sender, args):
    args.CanExecute = not sender.ActualWidth < 100
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitVertical', 'Ctrl+W,OemPipe')
def CreateHorizontalSplit(target, sender, args):
    from System.Windows.Controls import Orientation
    from Microsoft.Intellipad.Host import HostWindow
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    hostWindow.SplitBufferView(sender, Orientation.Horizontal)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveCurrentLineToBottomOfView', 'Alt+Home')
def MoveCurrentLineToBottomOfViewExecuted(target, sender, args):
    sender.EditorOperations.MoveCurrentLineToBottom()
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Backspace', 'Shift+Back|Back')
def BackspaceExecuted(target, sender, args):
    sender.EditorOperations.Backspace(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Escape', 'Shift+Escape|Escape')
def EscapeExecuted(target, sender, args):
    return
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToNextCharacter', 'Shift+Right')
def SelectToNextCharacterExecuted(target, sender, args):
    sender.EditorOperations.MoveToNextCharacter(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToPreviousCharacter', 'Shift+Left')
def SelectToPreviousCharacterExecuted(target, sender, args):
    sender.EditorOperations.MoveToPreviousCharacter(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectLineUp', 'Shift+Up')
def SelectLineUpExecuted(target, sender, args):
    sender.EditorOperations.MoveLineUp(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectLineDown', 'Shift+Down')
def SelectLineDownExecuted(target, sender, args):
    sender.EditorOperations.MoveLineDown(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectPageUp', 'Shift+PageUp')
def SelectPageUpExecuted(target, sender, args):
    sender.EditorOperations.PageUp(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectPageDown', 'Shift+PageDown')
def SelectPageDownExecuted(target, sender, args):
    sender.EditorOperations.PageDown(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToEndOfLine', 'Shift+End')
def SelectToEndOfLineExecuted(target, sender, args):
    sender.EditorOperations.MoveToEndOfLine(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToStartOfLine', 'Shift+Home')
def SelectToStartOfLineExecuted(target, sender, args):
    sender.EditorOperations.MoveToStartOfLine(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Unindent', 'Shift+Tab')
def UnindentExecuted(target, sender, args):
    sender.EditorOperations.Unindent(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}InsertNewline', 'Shift+Enter')
def InsertNewlineExecuted(target, sender, args):
    sender.EditorOperations.InsertNewLine(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToNextWord', 'Ctrl+Shift+Right')
def SelectToNextWordExecuted(target, sender, args):
    sender.EditorOperations.MoveToNextWord(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToPreviousWord', 'Ctrl+Shift+Left')
def SelectToPreviousWordExecuted(target, sender, args):
    sender.EditorOperations.MoveToPreviousWord(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToStartOfDocument', 'Ctrl+Shift+Home')
def SelectToStartOfDocumentExecuted(target, sender, args):
    sender.EditorOperations.MoveToStartOfDocument(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectToEndOfDocument', 'Ctrl+Shift+End')
def SelectToEndOfDocumentExecuted(target, sender, args):
    sender.EditorOperations.MoveToEndOfDocument(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MakeUppercase', 'Ctrl+Shift+U')
def MakeUppercaseExecuted(target, sender, args):
    sender.EditorOperations.MakeUppercase(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectNextSiblingExtendSelection', 'Alt+Shift+Down')
def SelectNextSiblingExtendSelectionExecuted(target, sender, args):
    sender.EditorOperations.SelectNextSibling(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectPreviousSiblingExtendSelection', 'Alt+Shift+Up')
def SelectPreviousSiblingExtendSelectionExecuted(target, sender, args):
    sender.EditorOperations.SelectPreviousSibling(True)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}TransposeLine', 'Alt+Shift+T')
def TransposeLineExecuted(target, sender, args):
    sender.EditorOperations.TransposeLine(sender.UndoHistory)

#Alt+(direction) is used for view navigation
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectEnclosing', None)
def SelectEnclosingExecuted(target, sender, args):
    sender.EditorOperations.SelectEnclosing()

#Alt+(direction) is used for view navigation
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectFirstChild', None)
def SelectFirstChildExecuted(target, sender, args):
    sender.EditorOperations.SelectFirstChild()

#Alt+(direction) is used for view navigation
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectNextSibling', None)
def SelectNextSiblingExecuted(target, sender, args):
    sender.EditorOperations.SelectNextSibling(False)

#Alt+(direction) is used for view navigation
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectPreviousSibling', None)
def SelectPreviousSiblingExecuted(target, sender, args):
    sender.EditorOperations.SelectPreviousSibling(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}DeleteWordToLeft', 'Ctrl+Back')
def DeleteWordToLeftExecuted(target, sender, args):
    sender.EditorOperations.DeleteWordToLeft(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}DeleteWordToRight', 'Ctrl+Delete')
def DeleteWordToRightExecuted(target, sender, args):
    sender.EditorOperations.DeleteWordToRight(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectAll', 'Ctrl+A')
def SelectAllExecuted(target, sender, args):
    sender.EditorOperations.SelectAll()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SelectCurrentWord', None)
def SelectCurrentWordExecuted(target, sender, args):
    sender.EditorOperations.SelectCurrentWord()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToNextWord', 'Ctrl+Right')
def MoveToNextWordExecuted(target, sender, args):
    sender.EditorOperations.MoveToNextWord(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToPreviousWord', 'Ctrl+Left')
def MoveToPreviousWordExecuted(target, sender, args):
    sender.EditorOperations.MoveToPreviousWord(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToStartOfDocument', 'Ctrl+Home')
def MoveToStartOfDocumentExecuted(target, sender, args):
    sender.EditorOperations.MoveToStartOfDocument(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToEndOfDocument', 'Ctrl+End')
def MoveToEndOfDocumentExecuted(target, sender, args):
    sender.EditorOperations.MoveToEndOfDocument(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ScrollUpAndMoveCaretIfNecessary', 'Ctrl+Up')
def ScrollUpAndMoveCaretIfNecessaryExecuted(target, sender, args):
    sender.EditorOperations.ScrollUpAndMoveCaretIfNecessary()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ScrollDownAndMoveCaretIfNecessary', 'Ctrl+Down')
def ScrollDownAndMoveCaretIfNecessaryExecuted(target, sender, args):
    sender.EditorOperations.ScrollDownAndMoveCaretIfNecessary()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}TransposeCharacter', 'Ctrl+T')
def TransposeCharacterExecuted(target, sender, args):
    sender.EditorOperations.TransposeCharacter(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MakeLowercase', 'Ctrl+U')
def MakeLowercaseExecuted(target, sender, args):
    sender.EditorOperations.MakeLowercase(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CopySelection', 'Ctrl+C|Ctrl+Ins')
def CopySelectionExecuted(target, sender, args):
    sender.EditorOperations.CopySelection()

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CopySelection')
def CopySelectionCanExecute(target, sender, args):
    args.CanExecute = not sender.EditorPrimitives.Selection.IsEmpty

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CutSelection', 'Ctrl+X|Shift+Del')
def CutSelectionExecuted(target, sender, args):
    sender.EditorOperations.CutSelection(sender.UndoHistory)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CutSelection')
def CutSelectionCanExecute(target, sender, args):
    args.CanExecute = sender.EditorOperations.CanCut

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Paste', 'Ctrl+V|Shift+Ins')
def PasteExecuted(target, sender, args):
    sender.EditorOperations.Paste(sender.UndoHistory)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Paste')
def PasteCanExecute(target, sender, args):
    args.CanExecute = sender.EditorOperations.CanPaste
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Undo', 'Ctrl+Z|Alt+Back')
def UndoExecuted(target, sender, args):
    sender.UndoHistory.Undo(1)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Undo')
def UndoCanExecute(target, sender, args):
    args.CanExecute = sender.UndoHistory.CanUndo

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Redo', 'Ctrl+Y|Shift+Alt+Back')
def RedoExecuted(target, sender, args):
    sender.UndoHistory.Redo(1)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Redo')
def RedoCanExecute(target, sender, args):
    args.CanExecute = sender.UndoHistory.CanRedo

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToNextCharacter', 'Right')
def MoveToNextCharacterExecuted(target, sender, args):
    sender.EditorOperations.MoveToNextCharacter(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToPreviousCharacter', 'Left')
def MoveToPreviousCharacterExecuted(target, sender, args):
    sender.EditorOperations.MoveToPreviousCharacter(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveLineUp', 'Up')
def MoveLineUpExecuted(target, sender, args):
    sender.EditorOperations.MoveLineUp(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveLineDown', 'Down')
def MoveLineDownExecuted(target, sender, args):
    sender.EditorOperations.MoveLineDown(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}PageUp', 'PageUp')
def PageUpExecuted(target, sender, args):
    sender.EditorOperations.PageUp(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}PageDown', 'PageDown')
def PageDownExecuted(target, sender, args):
    sender.EditorOperations.PageDown(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToStartOfLine', 'Home')
def MoveToStartOfLineExecuted(target, sender, args):
    sender.EditorOperations.MoveToStartOfLine(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveToEndOfLine', 'End')
def MoveToEndOfLineExecuted(target, sender, args):
    sender.EditorOperations.MoveToEndOfLine(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ResetSelection', 'Escape')
def ResetSelectionExecuted(target, sender, args):
    sender.EditorOperations.ResetSelection()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Delete', 'Delete')
def DeleteExecuted(target, sender, args):
    sender.EditorOperations.Delete(sender.UndoHistory)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Delete')
def DeleteCanExecuted(target, sender, args):
    args.CanExecute = sender.EditorOperations.CanDelete

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleOverwriteMode', 'Insert')
def ToggleOverwriteModeExecuted(target, sender, args):
    option = Microsoft.VisualStudio.Text.Editor.DefaultTextViewOptions.OverwriteModeId
    options = sender.EditorOperations.Options
    overwriteMode = options.GetOptionValue(option)
    options.SetOptionValue(option, not overwriteMode)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}InsertNewline', 'Enter')
def InsertNewlineExecuted(target, sender, args):
    sender.EditorOperations.InsertNewLine(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Indent', 'Tab')
def IndentExecuted(target, sender, args):
    sender.EditorOperations.Indent(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ToggleFullScreen', 'Shift+Alt+Enter')
def ToggleFullScreen(target, sender, args):
    global previousState
    if sender.IsFullScreen:
        if previousState != None:
            sender.WindowState = previousState
        sender.IsFullScreen = False
    else:
        sender.IsFullScreen = True
        previousState = sender.WindowState
        sender.WindowState = System.Windows.WindowState.Maximized 

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SetStandardMode', 'Ctrl+Shift+N')
def SetStandardMode(target, sender, args):
    sender.Mode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}StandardMode')

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}YankLine', 'Ctrl+L')    
def YankCurrentLine(target, sender, args):
    from Microsoft.VisualStudio.Text import Span
    from Microsoft.VisualStudio.Text.Editor import ITextSelection, ITextCaret
    from Microsoft.VisualStudio.UI.Undo import UndoPrimitive
    
    class YankLineUndoPrimitive(UndoPrimitive):
        def __init__(self, textView):
            self.textView = textView
            self.caretPosition = textView.Caret.Position.Index
            self.selectionSpan = textView.Selection.SelectionSpan.Span
            self.isSelectionReversed = textView.Selection.IsReversed
        
        def GetCanRedo(self):
            return False
            
        def Undo(self):
            ITextCaret.MoveTo(self.textView.Caret, self.caretPosition)
            ITextSelection.Select(self.textView.Selection, self.selectionSpan, self.isSelectionReversed)            
    
    bufferView = sender
    start = 0
    end = 0
    
    yankUndoPrimitive = YankLineUndoPrimitive(bufferView.TextEditor.TextView)
    
    if bufferView.EditorPrimitives.Selection.IsEmpty:
        line = bufferView.TextEditor.TextView.TextSnapshot.GetLineFromPosition(bufferView.EditorPrimitives.Caret.CurrentPosition)
        start = line.Start
        end = line.EndIncludingLineBreak
    else:
        selectionStart = bufferView.TextEditor.TextView.Selection.SelectionSpan.Start
        selectionEnd = bufferView.TextEditor.TextView.Selection.SelectionSpan.End
        
        start = bufferView.TextEditor.TextView.TextSnapshot.GetLineFromPosition(selectionStart).Start
        endLine = bufferView.TextEditor.TextView.TextSnapshot.GetLineFromPosition(selectionEnd)
        
        # Check if we're on the end-boundary of the previous line
        if selectionEnd == endLine.Start: 
            end = endLine.Start
        else:
            end = endLine.EndIncludingLineBreak
    
    bufferView.EditorPrimitives.Caret.MoveTo(end)
    undoTransaction = bufferView.UndoHistory.CreateTransaction("Yank Line")
    
    undoTransaction.AddUndo(yankUndoPrimitive)
    textRange = bufferView.EditorPrimitives.Caret.GetTextRange(start)
    
    ITextSelection.Select(bufferView.TextEditor.TextView.Selection, Span(start, end - start), False)
    bufferView.EditorOperations.CopySelection()
    
    textRange.Delete()
    undoTransaction.Complete()
    undoTransaction.Dispose()

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ToggleMiniBuffer', 'Ctrl+Shift+D')
def ToggleMiniBuffer(target, sender, args):
    Common.ActivateMiniBuffer(True)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ActivateMiniBuffer', None)
def ActivateMiniBuffer(target, sender, args):
    Common.ActivateMiniBuffer(False)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}OpenProject', 'Ctrl+Shift+O')    
def OpenProject(target, sender, args):
    from Microsoft.Intellipad.Host import HostWindow
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    projectUri = args.Parameter
    Common.OpenProject(hostWindow, projectUri)    

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShowCompletions', 'Ctrl+Space')
def ShowCompletionsCommand(target, sender, args):
    Common.ShowCompletions(sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShowDefinitionList', 'F12')
def ShowDefinitionListCommand(target, sender, args):
    Common.ShowDefinitionList(sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ShowErrorList', 'Ctrl+Shift+E')
def ShowErrorList(target, sender, args):
    errorBuffer = Common.GetOrCreateErrorBuffer()

    view = Common.GetView(sender, errorBuffer)
    if view is not None:
        Common.SetActiveView(view)
        return
    
    view = sender.ShowInRoot(errorBuffer, System.Windows.Controls.Orientation.Vertical, 50.0)
    view.Mode = Common.Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}ListMode')

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ShowNotifications', None)
def ShowNotifications(target, sender, args):
    Host.ShowNotificationBuffer()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShowReferencesList', 'Shift+F12')
def ShowReferencesListCommand(target, sender, args):
    Common.ShowReferencesList(sender)


@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ZoomCommand', 'Ctrl+W,Z')
def ZoomCommand(target, sender, args):
    if args.Parameter is not None:
        FindHelper.ZoomCommand(args.Parameter, args)
    else:
        FindHelper.ZoomCommand(Core.Host.TopLevelWindows[0].ActiveView, args)
        
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ZoomUp', 'Ctrl+OemPlus')
def ZoomUp(target, sender, args):
        sender.Scale = sender.Scale * 1.1 # 10%

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ZoomDown', 'Ctrl+OemMinus')
def ZoomDown(target, sender, args):
        sender.Scale = sender.Scale / 1.1 # 10% of original

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleWordWrap', 'Ctrl+W,W')
def ToggleWordWrap(target, sender, args):
    Common.ToggleWordWrap(sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SetBlackBackground', 'Ctrl+B,B') 
def SetBlackBackground(target, bufferView, args):
    bufferView.TextEditor.TextView.Background = System.Windows.Media.Brushes.Black

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleFileChangesNotification', 'Ctrl+W,N')
def ToggleFileChangesNotification(target, sender, args):
    Settings = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}Settings')
    Settings.DisableExternalChangeNotification = not Settings.DisableExternalChangeNotification
    Settings.Save()
