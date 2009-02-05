#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import sys
import System
import Microsoft
import Common

# strings
WelcomeMessage = 'Welcome to Intellipad.'

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def InitializeCore(value):
    global Core
    Core = value
    Common.Initialize(Core)

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectManager')
def InitializeProjectManager(value):
    global ProjectManager
    ProjectManager = value

def RunAllTests():
    metadata = Core.ComponentDomain.TryGetImportInfos('{Microsoft.Intellipad}UnitTest').GetValueIfSucceeded()
    class Test:
        def __init__(self, test):
            (hasName,self.Name) = test.Metadata.TryGetValue('{Microsoft.Intellipad.UnitTest}Name')
            self.Test = test
        def GetTest(self):
            return self.Test.TryGetBoundValue().GetValueIfSucceeded()
    Tests = [Test(test) for test in metadata]
    Common.RunTests(Tests)

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}RunTests', 'Ctrl+R,A')
def RunTests(target, sender, args):
    RunAllTests()

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
        
def ContextSensitiveHelp(view):
    handled = False
    symbol = None
    languageServiceItem = view.LanguageServiceItem
    if languageServiceItem is not None:
        caretPosition = view.EditorPrimitives.Caret.AdvancedTextPoint
        symbol = languageServiceItem.GetSymbol(caretPosition)
        
    domain = view.Mode.ComponentDomain
    helpProvider = domain.TryGetBoundValue[Microsoft.Intellipad.LanguageServices.ILanguageHelpProvider]()
    if helpProvider.Succeeded:
        handled = helpProvider.Value.ProvideHelp(symbol)
    return handled;
    
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}HelpContext', 'F1')
def HelpContext(target, bufferView, args):
    from Microsoft.Intellipad.Host import HostWindow
    from Microsoft.Intellipad.Shell import NamedCommands 
    
    handled = ContextSensitiveHelp(bufferView)
    if handled is False:
        hostWindow = HostWindow.GetHostWindowForBufferView(bufferView)
        NamedCommands.FromName("{Microsoft.Intellipad}HelpCommands").Execute(hostWindow, None)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}HelpCommands', 'Alt+F1')
def HelpCommands(target, window, args):
    from Microsoft.Intellipad.Shell import CommandMetadata

    help = Common.BufferManager.GetBuffer(System.Uri('transient://helpcommands'))
    view = Common.GetView(window, help)
    if view is not None:
        Common.SetActiveView(view)
        return
    
    Common.Clear(help)
    
    miniBufferMode = Core.ComponentDomain.GetBoundValue[System.Object]("{Microsoft.Intellipad}MiniBufferMode");
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
    Common.WriteLine(help, commandHeader)    
    
    Common.WriteLine(help, '-' * commandNameLength)    
    for commandName in sorted(commandList , lambda x,y: x > y):
        Common.WriteLine(help, (" " * commandIndent) + commandName)    
    
    def GetHelp(binding):
        name = CommandMetadata.GetCommandName(binding)
        key = CommandMetadata.GetCommandKey(binding)
        return {'name': name, 'key': key }
        
    commandBindingsProvider = Core.ComponentDomain.GetBoundValue[System.Object]("{Microsoft.Intellipad.Shell}CommandBindingsProvider")
    bindings = commandBindingsProvider.GetCommandBindings()
    dict = [GetHelp(binding) for binding in bindings]
    
    header = {'key': 'Key Gesture', 'name': 'Command Name' }
    
    keyLength = len(str(header['key']))
    nameLength = len(str(header['name']))
    
    for binding in dict:
        if len(str(binding['key'])) > keyLength :
            keyLength  = len(str(binding['key']))
        if len(str(binding['name'])) > nameLength:
            nameLength = len(str(binding['name']))
    
    keyLength += 2
    nameLength += 2
    
    headerFormatText = '%(key)' + str(keyLength) + 's %(name)s'
    formatText = '%(key)' + str(keyLength) + 's: %(name)s'
    spacerText = ('-' * keyLength) + ' ' + ('-' * nameLength)
    
    Common.WriteLine(help, headerFormatText % header)
    Common.WriteLine(help, spacerText)
    for binding in sorted(dict, lambda x,y: str(x['name']) > str(y['name'])):
        Common.WriteLine(help, formatText % binding)
    
    Common.SetReadOnly(help)

    window.ShowInRoot(help, 40.0)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}CloseBuffer', 'Ctrl+F4')
def CloseBuffer(target, sender, args):
    from Microsoft.Intellipad.Host import HostWindow
  
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    
    Common.CloseBuffer(sender.Buffer)
    
    if hostWindow.BufferViews.Count == 0:
        hostWindow.Close()

  
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}Exit', 'Alt+F4')
def Exit(target, sender, args):
    sender.Close()

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewRight', 'Alt+Right')
def FocusBufferViewRight(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindRight(sender), lambda tab: tab.VisualOffset.Y)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewLeft', 'Alt+Left')
def FocusBufferViewLeft(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindLeft(sender), lambda tab: tab.VisualOffset.Y)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewUp', 'Alt+Up')
def FocusBufferViewUp(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindUp(sender), lambda tab: tab.VisualOffset.X)
  
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FocusBufferViewDown', 'Alt+Down')
def FocusBufferViewDown(target, sender, args):
  return Common.FocusBufferViewHelper(sender, Common.FindDown(sender), lambda tab: tab.VisualOffset.X)
  
@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}About', None)
def About(target, sender, args):
    from System.Windows import MessageBox, MessageBoxButton, MessageBoxImage
    MessageBox.Show(WelcomeMessage, 'Intellipad', MessageBoxButton.OK, MessageBoxImage.Information)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleBehavior', None)
def ToggleBehaviorCommand(target, sender, args):
    Common.ToggleBehavior(args.Parameter, sender)  

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleLineNumber', 'Ctrl+Shift+L')
def ToggleLineNumber(target, sender, args):
    Common.ToggleBehavior("Microsoft.Intellipad.Host.LineNumberBehavior", sender)
  
@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Save')
def CanSave(target, sender, args):
    args.CanExecute = (sender.Buffer.CanSave or sender.Buffer.CanSaveAs)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Save', 'Ctrl+S')
def Save(target, sender, args):
    Common.SaveBuffer(sender.Buffer, sender)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SaveAs')
def CanSaveAs(target, sender, args):
    args.CanExecute = sender.Buffer.CanSaveAs
        
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SaveAs', None)
def SaveAs(target, sender, args):
    if sender.Buffer.CanSaveAs:
        Common.SaveAsBuffer(sender.Buffer, sender)
                
@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitVertically')
def CanSplitVertically(target, sender, args):
    args.CanExecute = not sender.ActualHeight < 100
        
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitVertically', 'Ctrl+W,V')
def CreateVerticalSplit(target, sender, args):
    from System.Windows.Controls import Orientation
    from Microsoft.Intellipad.Host import HostWindow
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    hostWindow.SplitBufferView(sender, Orientation.Vertical)

@Metadata.CommandCanExecute('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitHorizontally')
def CanSplitHorizontally(target, sender, args):
    args.CanExecute = not sender.ActualWidth < 100
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SplitHorizontally', 'Ctrl+W,H')
def CreateHorizontalSplit(target, sender, args):
    from System.Windows.Controls import Orientation
    from Microsoft.Intellipad.Host import HostWindow
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    hostWindow.SplitBufferView(sender, Orientation.Horizontal)
    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}MoveCurrentLineToBottom', 'Alt+Home')
def MoveCurrentLineToBottomExecuted(target, sender, args):
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
    sender.EditorOperations.InsertNewline(sender.UndoHistory)

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

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleOverwriteMode', 'Insert')
def ToggleOverwriteModeExecuted(target, sender, args):
    sender.EditorOperations.Options.OverwriteMode = not sender.EditorOperations.Options.OverwriteMode

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}InsertNewline', 'Enter')
def InsertNewlineExecuted(target, sender, args):
    sender.EditorOperations.InsertNewline(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Indent', 'Tab')
def IndentExecuted(target, sender, args):
    sender.EditorOperations.Indent(sender.UndoHistory)

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ToggleFullScreen', 'Shift+Alt+Enter')
def ToggleFullScreen(target, sender, args):
    sender.IsFullScreen = not sender.IsFullScreen

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SetStandardMode', 'Ctrl+Shift+N')
def SetStandardMode(target, sender, args):
    sender.Mode = Core.ComponentDomain.GetBoundValue[System.Object]('{Microsoft.Intellipad}StandardMode')

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}YankLine', 'Ctrl+L')    
def YankCurrentLine(target, sender, args):
    from Microsoft.VisualStudio.Text import Span
    from Microsoft.VisualStudio.Text.Editor import ITextSelection
    
    bufferView = sender
    start = 0
    end = 0
    
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
    
    bufferView.EditorPrimitives.Caret.MoveTo(end, False)
    ITextSelection.Select(bufferView.TextEditor.TextView.Selection, Span(start, end - start), False)
    CutSelectionExecuted(target, sender, args)

#
# temporary hack until we get a way to add keyboard for non-script events
#    
@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}RouteMiniBuffer', 'Ctrl+Shift+D')
def RouteMiniBuffer(target, sender, args):
    from Microsoft.Intellipad.Shell import NamedCommands 
    executeCommand = NamedCommands.FromName('{Microsoft.Intellipad}ActivateMiniBuffer')
    executeCommand.Execute(sender, sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}OpenProject', 'Ctrl+Shift+O')    
def OpenProject(target, sender, args):
    from Microsoft.Win32 import OpenFileDialog
    from Microsoft.Intellipad.Host import HostWindow
    from System.Xaml import AttachedPropertyServices
    
    hostWindow = HostWindow.GetHostWindowForBufferView(sender)
    
    tab = Common.FindParent(System.Windows.Controls.CloseableTabControl, sender)
    if tab == None:
        # if there is no enclosing tab, we must be some ancilliary view
        sender = hostWindow.BufferViews[len(hostWindow.BufferViews) - 1]
    
    projectUri = args.Parameter
    if projectUri == None:
        ofd = OpenFileDialog()
        s = 'Project Files (*.*proj)|*.*proj'
        for kvp in Core.AvailableFileExtensions:
            s = s + '|' + kvp.ModeName + ' (*' + kvp.FileExtension + ')|*' + kvp.FileExtension
            
        ofd.Multiselect = False
        ofd.Filter = s
        
        if ofd.ShowDialog(hostWindow) == True:
            projectUri = System.Uri(ofd.FileName)
    
    if projectUri != None:
        previousCursor = System.Windows.Input.Mouse.OverrideCursor
        System.Windows.Input.Mouse.OverrideCursor = System.Windows.Input.Cursors.Wait
        
        projectBuffer = Common.BufferManager.GetBuffer(projectUri)
        projectContext = ProjectManager.GetContextFromProject(projectBuffer)
        
        # Construct project view buffer Uri
        projectViewUri = System.Uri(System.String.Format('projectview://projectcontext?source={0}', projectBuffer.Uri))
        projectViewBuffer = Common.BufferManager.GetBuffer(projectViewUri)
        
        projectView = hostWindow.ShowInRoot(projectViewBuffer, 50.0)
        AttachedPropertyServices.SetProperty(projectView, Microsoft.Intellipad.LanguageServices.ProjectManager.ProjectContextProperty, projectContext)
    
        System.Windows.Input.Mouse.OverrideCursor = previousCursor


@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShowDefinitionList', 'F12')
def ShowDefinitionListCommand(target, sender, args):
    Common.ShowDefinitionList(sender)

@Metadata.CommandExecuted('{Microsoft.Intellipad.Host}HostWindow', '{Microsoft.Intellipad}ShowErrorList', 'Ctrl+Shift+E')
def ShowErrorList(target, sender, args):
    from Microsoft.Intellipad.LanguageServices import ListBufferHelper
    
    errorBuffer = Common.BufferManager.GetBuffer(System.Uri('transient://errors'))
    view = Common.GetView(sender, errorBuffer)
    if view is not None:
        Common.SetActiveView(view)
        return
    
    listBufferHelper = ListBufferHelper.Create(errorBuffer)
    view = sender.ShowInRoot(errorBuffer, 50.0)
    view.Mode = Common.Core.ComponentDomain.GetBoundValue[System.Object]('{Microsoft.Intellipad}HyperlinkMode')

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShowReferencesList', 'Shift+F12')
def ShowReferencesListCommand(target, sender, args):
    Common.ShowReferencesList(sender)
    
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

