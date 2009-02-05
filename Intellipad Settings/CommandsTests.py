
import clr
import sys
import System
import Microsoft
import Common
import FindHelper
from Microsoft.Intellipad.Scripting import UnitTest
from Microsoft.Intellipad.Shell import NamedCommands

clr.AddReference('ComponentModel')
clr.AddReference('Xaml')

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def Initialize(value):
    global Core
    Core = value
    Common.Initialize(Core)
    FindHelper.Initialize(Core)
    
@Metadata.Export('{Microsoft.Intellipad}TestHelper')
def TestHelperExport():
    return TestHelper

@Metadata.ImportSingleValue('{Microsoft.Intellipad}MMode')
def MMode(value):
    global MMode
    MMode = value
    
class TestHelperClass:
    def AssertCaretLine(self, view, expectedLine):
        from Microsoft.VisualStudio.Text.Editor import ITextCaret
        caret = view.EditorPrimitives.Caret.AdvancedCaret
        actualLine = ITextCaret.ContainingTextViewLine.GetValue(caret).SnapshotLine.LineNumber
        assert expectedLine == actualLine, "Expected to find line %d, but found %d" % (expectedLine, actualLine)

    def AssertSelectionLocation(self, view, line, column, length):
        from Microsoft.VisualStudio.Text.Editor import ITextSelection
        selection = view.EditorPrimitives.Selection.AdvancedSelection
        actual = selection.SelectionSpan.Span
        snapshot = view.Buffer.TextBuffer.CurrentSnapshot
        snapline = snapshot.GetLineFromLineNumber(line - 1)
        expected = Microsoft.VisualStudio.Text.Span(snapline.Start + column, length)
        assert expected == actual, "Expected selection at %s but found %s" % (expected, actual)

    def CloseViews(self, views):
        for view in views:
            if view is not None:
                view.Close()
        
    def Execute(self, name, args, sender):
        NamedCommands.FromName(name).Execute(args, sender)

    def GetText(self, view):
        snap = view.Buffer.TextBuffer.CurrentSnapshot
        return snap.GetText(0, snap.Length)

    def CreateDispatcherEvent(self, completedEvent):
        from System.Windows.Threading import DispatcherFrame, Dispatcher, DispatcherTimer
        class Event:
            def __init__(self, event):
                self.event = event
                self.timeout = True
                self.frame = DispatcherFrame()
                self.event += self.CompletedYes
            def Wait(self, seconds):
                timer = DispatcherTimer()
                timer.Tick += self.CompletedNo
                timer.Interval = System.TimeSpan(0, 0, seconds)
                timer.Start()
                Dispatcher.PushFrame(self.frame)
                self.event -= self.CompletedYes
                return not self.timeout
            def CompletedYes(self, sender,args):
                self.timeout = False
                self.frame.Continue = False
            def CompletedNo(self, sender,args):
                self.frame.Continue = False
        return Event(completedEvent)

    def GetTextTimeout(self, view, completedEvent, expected, seconds):
        """Returns the views text content, waiting some time for it to become 'correct'
        
        GetTextTimeout will wait 'seconds' for the view to contain the
        text 'expected'.  Once the text is 'expected' or the timeout
        elapses, it will return whatever text is in the view.  This
        method uses PushFrame to enter an event loop because threads
        might need to dispatch to the UI thread to complete.
        
        view           - Must have a Buffer with SampleParsed event
        completedEvent - An event that when fired indicates no more waiting is necessary
        expected       - the text we are looking for
        seconds        - how long to wait for it
        """
        from System.Windows.Threading import DispatcherFrame, Dispatcher, DispatcherTimer
        frame = DispatcherFrame()
        def Completed(sender,args):
            frame.Continue = False
        completedEvent += Completed
        actual = TestHelper.GetText(view)
        if actual != expected:
            timer = DispatcherTimer()
            timer.Tick += Completed
            timer.Interval = System.TimeSpan(0, 0, seconds)
            timer.Start()
            Dispatcher.PushFrame(frame)
            actual = TestHelper.GetText(view)
        completedEvent -= Completed
        return actual

    def ResetBufferViews(self, hostWindow):
        for (idx, view) in enumerate(list(hostWindow.BufferViews)):
            if idx != 0:
                view.Close()
        Common.DrainDispatcher()

    def ResetOpenFileBuffers(self, hostWindow):
        for openBuffer in list(hostWindow.Host.BufferManager.OpenBuffers):
            if (Microsoft.Intellipad.IntelliBuffer.Uri.GetValue(openBuffer)).Scheme.Equals(System.Uri.UriSchemeFile, System.StringComparison.OrdinalIgnoreCase): 
                openBuffer.Close()
        if (hostWindow.Host.BufferManager.OpenBuffers.Count == 0):
            hostWindow.ActiveView.Buffer = Common.BufferManager.GetBuffer(System.Uri('file://'))
        Common.DrainDispatcher()

    def SetViewSlotLength(self, view, length):
        hostWindow = Core.Host.TopLevelWindows[0]
        slot = hostWindow.FindSlot(view)
        slot.Length = System.Windows.GridLength(length, System.Windows.GridUnitType.Star)
            
    def Split(self, view, orientation, content):
        hostWindow = Core.Host.TopLevelWindows[0]
        newView = hostWindow.SplitBufferView(view, orientation)
        newView.Buffer = Common.BufferManager.GetBuffer(System.Uri('file://'))
        if content is not "":
            Common.WriteLine(newView.Buffer, content)
        Common.DrainDispatcher()
        return newView

    def SplitWithBuffer(self, view, orientation, buffer):
        hostWindow = Core.Host.TopLevelWindows[0]
        newView = hostWindow.SplitBufferView(view, orientation)
        newView.Buffer = buffer
        Common.DrainDispatcher()
        return newView
    
      

TestHelper = TestHelperClass()
 
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'ToggleLineNumberTest')
def ToggleLineNumberTest():
    class Test(UnitTest):
        def Run(self):
            try:
                from System.Windows.Controls import Orientation
                hostWindow = Core.Host.TopLevelWindows[0]
                view = TestHelper.Split(hostWindow.BufferViews[0], Orientation.Horizontal, "")
                
                assert view.Behaviors.Count == 0, "Should be zero behaviors"
                
                TestHelper.Execute('{Microsoft.Intellipad}ToggleLineNumber', None, view)
                
                assert view.Behaviors.Count == 1, "Should be just one behavior"
                
                TestHelper.Execute('{Microsoft.Intellipad}ToggleLineNumber', None, view)
                
                assert view.Behaviors.Count == 0, "Should have zero behavior"
                    
            finally:
                TestHelper.CloseViews([view])
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'ToggleWordWrapTest')
def ToggleWordWrapTest():
    class Test(UnitTest):
        def Run(self):
            try:

                from Microsoft.VisualStudio.Text.Editor import EditorOptionIds, WordWrapStyles             
                from System.Windows.Controls import Orientation

                hostWindow = Core.Host.TopLevelWindows[0]
                view = TestHelper.Split(hostWindow.BufferViews[0], Orientation.Horizontal, '')
                Common.DeactivateWordWrap(view)
                
                assert view.Behaviors.Count == 0, 'Should be zero behaviors'
                
                TestHelper.Execute('{Microsoft.Intellipad}ToggleWordWrap', None, view)
                
                assert view.Behaviors.Count == 1, 'Should be just one behavior - line number'
                result = view.TextEditor.TextView.Options.GetOptionValue[WordWrapStyles](EditorOptionIds.WordWrapStyleId)
                assert result & WordWrapStyles.WordWrap, 'WordWrap style should be on'
                
                TestHelper.Execute('{Microsoft.Intellipad}ToggleWordWrap', None, view)
                
                assert not view.Behaviors.Count, "Should have zero behavior"
                result = view.TextEditor.TextView.Options.GetOptionValue[WordWrapStyles](EditorOptionIds.WordWrapStyleId)
                assert not result & WordWrapStyles.WordWrap, 'WordWrap style should be off'
                    
            finally:
                TestHelper.CloseViews([view])
    return Test()

    
def VerifyAndCloseHelpView(hostWindow, bufferViewModifier, bufferViewCleanupModifier):
    help = None
    try:
        help = Common.BufferManager.GetBuffer(System.Uri('transient://helpcommands'))
        view = Common.GetView(hostWindow, help)
        bufferViewModifier(view)
        assert view is not None, "Command help buffer view should be visible"
        assert len(TestHelper.GetText(view)) > 0, "Command help buffer view should have content"
        bufferViewCleanupModifier(view)
    finally:
        if help is not None:
            help.Close()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'HelpContextDefault')
def HelpContextDefault():
    class Test(UnitTest):
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            tempBuffer = None
            try:
                hostWindow = Core.Host.TopLevelWindows[0]
                tempBuffer = Common.BufferManager.GetBuffer(System.Uri('transient://temp'))
                view = hostWindow.ShowBuffer(tempBuffer)
                Common.SetActiveView(view)
                bufferViewModifier(view)
                TestHelper.Execute('{Microsoft.Intellipad}HelpContext', None, view)
                Common.DrainDispatcher()
            
                # Fall through should be to show the commands
                VerifyAndCloseHelpView(hostWindow, bufferViewModifier, bufferViewCleanupModifier)
                bufferViewCleanupModifier(view)
                
            finally:
                if tempBuffer is not None:
                    tempBuffer.Close()
                
    return Test()
    
class TestHelpProvider(Microsoft.Intellipad.LanguageServices.ILanguageHelpProvider): 
    def __init__(self):
        self.LastHelpMessage = "";
    def ProvideHelp(self, symbol):
        if symbol is not None:
            self.LastHelpMessage = "Name='" + symbol.Name + "' SymbolType='" + symbol.SymbolType + "'"
        else:
            self.LastHelpMessage = "No Symbol"
        return True    

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'HelpContextSymbol')
def HelpContextSymbol():
    from System.ComponentModel.Composition import CompositionServices
    from System.Threading import ManualResetEvent
    class Test(UnitTest):
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            buffer = None
            exportKey = None
            self.evt = None
            textWritten = False
            try:
                simpleDefinition = """\
module Test
{
    type T1 {
        A : Text;
    } where identity A;

    t_one_s : T1*;
    
    type T2
    {
        B : T1;
    }
    
    t_two_s : T2* where item.B in t_one_s;
    
}
""".replace("\n", "\r\n")


                tempFileName = System.IO.Path.GetTempFileName()
                System.IO.File.WriteAllText(tempFileName, simpleDefinition)   
                uri = System.Uri('file://' + tempFileName)

                hostWindow = Core.Host.TopLevelWindows[0]
                buffer = Common.BufferManager.GetBuffer(uri)

                view = hostWindow.ShowBuffer(buffer)
                view.Mode = Core.ComponentDomain.GetBoundValue[System.Object]('{Microsoft.Intellipad}MMode');
                view.EnsureEditorIsValid()
                bufferViewModifier(view)
                Common.DrainDispatcher()
                
                domain = view.Mode.ComponentDomain;
                helpProvider = TestHelpProvider()
                helpProviderExportName = CompositionServices.GetContractName(Microsoft.Intellipad.LanguageServices.ILanguageHelpProvider )
                exportKey = domain.AddValue(helpProviderExportName, helpProvider);
                domain.Bind()

                Common.DrainDispatcher()
                
                #               v
                #        module Test
                caret = view.EditorPrimitives.Caret;
                findResults = caret.Find('Test')                
                startPoint = list(findResults)[0]
                assert startPoint.CurrentPosition > 0, 'expecting to navigate into the document'
                caret.MoveTo(startPoint.CurrentPosition)                
                Common.SetActiveView(view)

                Common.DrainDispatcher()

                languageServiceItem = view.LanguageServiceItem
                assert languageServiceItem is not None
                languageServiceItem.Project.UpdateProject()
                
                Common.DrainDispatcher()

                TestHelper.Execute('{Microsoft.Intellipad}HelpContext', None, view)
                Common.DrainDispatcher()
                expectedHelp = "Name='module Test' SymbolType='ModuleDeclaration'"
                actualHelp = helpProvider.LastHelpMessage
                assert expectedHelp == actualHelp, "Expected '%s' but found '%s'" % (expectedHelp, actualHelp)
                
                bufferViewCleanupModifier(view)                 
            finally:
                if buffer is not None:
                    buffer.Close()
                if exportKey is not None:
                    domain.RemoveValue(exportKey)
                    domain.Bind()

    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'HelpCommandsTest')
def HelpCommandsTest():
    class Test(UnitTest):
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.Execute('{Microsoft.Intellipad}HelpCommands', None, hostWindow)
            Common.DrainDispatcher()
            
            VerifyAndCloseHelpView(hostWindow, bufferViewModifier, bufferViewCleanupModifier)
    return Test()
            
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'FindNextPreviousTests')
def FindNextPreviousTests():
    from System.Windows.Controls import Orientation
    from Microsoft.VisualStudio.Text.Editor import ITextCaret, ITextSelection
    class Test(UnitTest):
        def __init__(self):
            self.findview = None
            
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            self.findview = TestHelper.Split(self.hostWindow.BufferViews[0], Orientation.Horizontal, "")
            Common.SetActiveView(self.findview)
            #Put in long strings so it will word wrap
            Common.WriteLine(self.findview.Buffer, "abc\r\ndef\r\nabc\r\nghi\r\nabc\r\njkl\r\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            selection = self.findview.EditorPrimitives.Selection.AdvancedSelection
            ITextSelection.Select(selection, Microsoft.VisualStudio.Text.Span(0, 3), False)
    
            caret = self.findview.EditorPrimitives.Caret.AdvancedCaret
            ITextCaret.MoveTo(caret, 3)
            
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            Setup(self)
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            bufferViewModifier(self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)
            
            TestHelper.Execute('{Microsoft.Intellipad}FindSelectedNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 2)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindSelectedNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 4)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindSelectedNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindSelectedPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 4)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindSelectedPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 2)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindSelectedPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindSelectedPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 4)
    
            # Now we have a search stored from SelectedNext, SelectedPrevious, so we can just use Next/Previous
            # to continue searching
    
            TestHelper.Execute('{Microsoft.Intellipad}FindNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 2)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 4)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)

            TestHelper.Execute('{Microsoft.Intellipad}FindPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 4)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 2)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 4)
            
            bufferViewCleanupModifier(self.findview)
        def Cleanup(self):
            TestHelper.CloseViews([self.findview])
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'FindTests')
def FindTests():
    from System.Windows.Controls import Orientation
    from Microsoft.VisualStudio.Text.Editor import ITextCaret
    class Test(UnitTest):
        def __init__(self):
            self.findview = None
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            self.findview = TestHelper.Split(self.hostWindow.BufferViews[0], Orientation.Horizontal, "")
            
            #Put in long strings so it will word wrap
            Common.WriteLine(self.findview.Buffer, "abc\r\ndef\r\nabc\r\nghi\r\nabc\r\njkl\r\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxz\r\n")
    
            caret = self.findview.EditorPrimitives.Caret.AdvancedCaret
            ITextCaret.MoveTo(caret, 0)
           
            Common.SetActiveView(self.findview)

        def Find(self, text):
            FindHelper.FindImpl(self.findview, text)
            
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            Setup(self)
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            bufferViewModifier(self.findview)
            
            TestHelper.AssertCaretLine(self.findview, 0)
            
            self.Find('abc')
            
            TestHelper.AssertCaretLine(self.findview, 0)

            self.Find('ghi')
            
            TestHelper.AssertCaretLine(self.findview, 3)

            self.Find('abc')
            
            TestHelper.AssertCaretLine(self.findview, 4)

            TestHelper.Execute('{Microsoft.Intellipad}FindNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindNext', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 2)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 0)
    
            TestHelper.Execute('{Microsoft.Intellipad}FindPrevious', None, self.findview)
            TestHelper.AssertCaretLine(self.findview, 4)
            
            self.Find('z')
            TestHelper.AssertCaretLine(self.findview, 6)

            
            bufferViewCleanupModifier(self.findview)
        def Cleanup(self):
            TestHelper.CloseViews([self.findview])
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'GotoTests')
def GotoTests():
    from System.Windows.Controls import Orientation
    from Microsoft.VisualStudio.Text.Editor import ITextCaret
    class Test(UnitTest):
        def __init__(self):
            self.gotoview = None
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            self.gotoview = TestHelper.Split(self.hostWindow.BufferViews[0], Orientation.Horizontal, "")
            
            #Put in long strings so it will word wrap
            Common.WriteLine(self.gotoview.Buffer, "abc\r\ndef\r\nabc\r\nghi\r\nabc\r\njkl\r\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxz\r\n")
    
            caret = self.gotoview.EditorPrimitives.Caret.AdvancedCaret
            ITextCaret.MoveTo(caret, 0)

            Common.SetActiveView(self.gotoview)
            
        def Goto(self, line):
            FindHelper.GotoImpl(self.gotoview, line)
            
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            Setup(self)
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            bufferViewModifier(self.gotoview)
            
            TestHelper.AssertCaretLine(self.gotoview, 0)
            
            self.Goto(3)
            
            TestHelper.AssertCaretLine(self.gotoview, 2)

            self.Goto(0)
            
            TestHelper.AssertCaretLine(self.gotoview, 0)

            self.Goto(100)
            
            TestHelper.AssertCaretLine(self.gotoview, 8)
            bufferViewCleanupModifier(self.gotoview)
        def Cleanup(self):
            TestHelper.CloseViews([self.gotoview])
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'ReplaceTests')
def ReplaceTests():
    from System.Windows.Controls import Orientation
    from Microsoft.VisualStudio.Text.Editor import ITextCaret
    class Test(UnitTest):
        def __init__(self):
            self.replaceview = None
            self.longStringWithTrailingZ = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxz"
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            self.replaceview = TestHelper.Split(self.hostWindow.BufferViews[0], Orientation.Horizontal, "")          
            
            Common.Write(self.replaceview.Buffer, "abc def abc ghi abc jkl " + self.longStringWithTrailingZ)
            caret = self.replaceview.EditorPrimitives.Caret.AdvancedCaret
            ITextCaret.MoveTo(caret, 0)
            Common.SetActiveView(self.replaceview)
            Common.DrainDispatcher()
            
        def Replace(self, before, after):
            FindHelper.ReplaceImpl(self.replaceview, before, after)
            
        def AssertText(self, expectedText):
            actualText = TestHelper.GetText(self.replaceview)
            assert expectedText == actualText, "Expected '%s' but found '%s'" % (expectedText, actualText)
            
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            Setup(self)
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            bufferViewModifier(self.replaceview)
        
            self.AssertText('abc def abc ghi abc jkl ' + self.longStringWithTrailingZ)           
            self.Replace('abc', '123')
            Common.DrainDispatcher()

            self.AssertText('123 def abc ghi abc jkl ' + self.longStringWithTrailingZ)

            TestHelper.Execute('{Microsoft.Intellipad}ReplaceNext', None, self.replaceview)
            Common.DrainDispatcher()

            self.AssertText('123 def 123 ghi abc jkl ' + self.longStringWithTrailingZ)

    
            TestHelper.Execute('{Microsoft.Intellipad}ReplacePrevious', None, self.replaceview)
            Common.DrainDispatcher()

            self.AssertText('123 def 123 ghi 123 jkl ' + self.longStringWithTrailingZ)
            self.Replace(self.longStringWithTrailingZ, 'z')
            Common.DrainDispatcher()
            
            self.AssertText('123 def 123 ghi 123 jkl z')

            bufferViewCleanupModifier(self.replaceview)
        def Cleanup(self):
            TestHelper.CloseViews([self.replaceview])
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'ShrinkExpandNavigateBufferViewTests')
def ShrinkExpandNavigateBufferViewTests():
    from System.Windows.Controls import Orientation
    global Core
    class Test(UnitTest):
        def __init__(self):
            self.viewtop = self.viewleft = self.viewbottom = self.viewmiddle = self.viewright = None
        def Setup(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(hostWindow)
            Common.DrainDispatcher()
            self.viewtop = TestHelper.Split(hostWindow.BufferViews[0], Orientation.Horizontal, "Top")
            self.viewleft = TestHelper.Split(self.viewtop, Orientation.Vertical, "Left")
            self.viewbottom = TestHelper.Split(self.viewleft, Orientation.Vertical, "Bottom")
            self.viewmiddle = TestHelper.Split(self.viewleft, Orientation.Horizontal, "Middle")
            self.viewright = TestHelper.Split(self.viewmiddle, Orientation.Horizontal, "Right")
        def ResetSize(self):
            def SetParentSize(view):
                hostWindow = Core.Host.TopLevelWindows[0]
                slot = hostWindow.FindSlot(view)
                slot.Parent.Length = System.Windows.GridLength(200.0, System.Windows.GridUnitType.Star)
            def SetSize(view):
                hostWindow = Core.Host.TopLevelWindows[0]
                slot = hostWindow.FindSlot(view)
                slot.Length = System.Windows.GridLength(200.0, System.Windows.GridUnitType.Star)
            SetSize(self.viewtop)
            SetSize(self.viewleft)
            SetSize(self.viewbottom)
            SetSize(self.viewmiddle)
            SetParentSize(self.viewmiddle)
            SetSize(self.viewright)
            Common.DrainDispatcher()
        def AssertWidthLess(self):
            assert self.viewmiddle.ActualWidth < self.viewleft.ActualWidth and self.viewmiddle.ActualWidth < self.viewright.ActualWidth, "%d < %d and %d < %d" % (self.viewmiddle.ActualWidth, self.viewleft.ActualWidth, self.viewmiddle.ActualWidth, self.viewright.ActualWidth)
        def AssertWidthMore(self):
            assert self.viewmiddle.ActualWidth > self.viewleft.ActualWidth and self.viewmiddle.ActualWidth > self.viewright.ActualWidth, "%d > %d and %d > %d" % (self.viewmiddle.ActualWidth, self.viewleft.ActualWidth, self.viewmiddle.ActualWidth, self.viewright.ActualWidth)
        def AssertHeightLess(self):
            assert self.viewmiddle.ActualHeight < self.viewtop.ActualHeight and self.viewmiddle.ActualHeight < self.viewbottom.ActualHeight, "%d < %d and %d < %d" % (self.viewmiddle.ActualHeight, self.viewtop.ActualHeight, self.viewmiddle.ActualHeight, self.viewbottom.ActualHeight)
        def AssertHeightMore(self):
            assert self.viewmiddle.ActualHeight > self.viewtop.ActualHeight and self.viewmiddle.ActualHeight > self.viewbottom.ActualHeight, "%d > %d and %d > %d" % (self.viewmiddle.ActualHeight, self.viewtop.ActualHeight, self.viewmiddle.ActualHeight, self.viewbottom.ActualHeight)


        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            Setup(self)
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))

        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
        
            bufferViewModifier(self.viewtop)
            bufferViewModifier(self.viewleft)
            bufferViewModifier(self.viewbottom)
            bufferViewModifier(self.viewmiddle)
            bufferViewModifier(self.viewright)

            hostWindow = Core.Host.TopLevelWindows[0]
                                
            # Shrink and Expand
            self.ResetSize()
            TestHelper.Execute('{Microsoft.Intellipad}ShrinkBufferViewHorizontal', None, self.viewmiddle)
            Common.DrainDispatcher()
            self.AssertWidthLess()
            
            self.ResetSize()
            TestHelper.Execute('{Microsoft.Intellipad}ExpandBufferViewHorizontal', None, self.viewmiddle)
            Common.DrainDispatcher()
            self.AssertWidthMore()
            
            self.ResetSize()
            TestHelper.Execute('{Microsoft.Intellipad}ShrinkBufferViewVertical', None, self.viewmiddle)
            Common.DrainDispatcher()
            self.AssertHeightLess()
            
            self.ResetSize()
            TestHelper.Execute('{Microsoft.Intellipad}ExpandBufferViewVertical', None, self.viewmiddle)
            Common.DrainDispatcher()
            self.AssertHeightMore()
            
            # Navigate
            Common.SetActiveView(self.viewtop)
            TestHelper.Execute('{Microsoft.Intellipad}FocusBufferViewDown', None, self.viewtop)
            assert TestHelper.GetText(hostWindow.ActiveView).startswith('Left')
            
            TestHelper.Execute('{Microsoft.Intellipad}FocusBufferViewRight', None, self.viewleft)
            assert TestHelper.GetText(hostWindow.ActiveView).startswith('Middle')
            
            TestHelper.Execute('{Microsoft.Intellipad}FocusBufferViewLeft', None, self.viewmiddle)
            assert TestHelper.GetText(hostWindow.ActiveView).startswith('Left')
            
            TestHelper.Execute('{Microsoft.Intellipad}FocusBufferViewUp', None, self.viewleft)
            assert TestHelper.GetText(hostWindow.ActiveView).startswith('Top')
            
            bufferViewCleanupModifier(self.viewtop)
            bufferViewCleanupModifier(self.viewleft)
            bufferViewCleanupModifier(self.viewbottom)
            bufferViewCleanupModifier(self.viewmiddle)
            bufferViewCleanupModifier(self.viewright)

        def Cleanup(self):
            TestHelper.CloseViews([self.viewtop, self.viewmiddle, self.viewbottom, self.viewleft, self.viewright])
    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'SplitTests')
def SplitTests():
    from System.Windows.Controls import Orientation
    global Core
    class Test(UnitTest):
        def __init__(self):
            self.viewzero = self.viewfirst = self.viewsecond = self.viewthird = self.viewfourth = self.viewfifth = self.viewsixth = self.viewseventh = None
            self.bufferViewCleanupModifier = None
            self.bufferViewModifier = None
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(self.hostWindow)
            view = self.hostWindow.BufferViews[0]
            slot = self.hostWindow.FindSlot(view)
            self.orientation = Orientation.Vertical
            if slot.Parent.Orientation == Orientation.Horizontal:
                self.viewzero = TestHelper.Split(view, Orientation.Vertical, "Zero")
                TestHelper.SetViewSlotLength(self.viewzero, 50.0)
                self.viewfirst = TestHelper.Split(self.viewzero, Orientation.Horizontal, "First")
            else:
                self.viewfirst = TestHelper.Split(view, Orientation.Horizontal, "First")
            TestHelper.SetViewSlotLength(self.viewfirst, 600.0)
            Common.DrainDispatcher()
            
            from System.Collections.Specialized import INotifyCollectionChanged
            INotifyCollectionChanged.add_CollectionChanged(self.hostWindow.BufferViews, self.OnViewsChanged)    
            
        def OnViewsChanged(self, sender, args):
            if args.NewItems != None:
                assert len(args.NewItems) == 1, "We should only get one new view at a time in this test"
                self.newview = args.NewItems.get_Item(0)
                if self.bufferViewModifier is not None:
                    self.newview.EnsureEditorIsValid()
                    self.bufferViewModifier(self.newview)    
        
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            Setup(self)
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))

        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            self.bufferViewModifier = bufferViewModifier
            self.bufferViewCleanupModifier = bufferViewCleanupModifier
            self.bufferViewModifier(self.viewfirst)
            
            self.TestCreateVerticalSplit();
            self.TestCreateHorizontalSplit();
            self.TestModePreservingSplit();
    
        def TestCreateVerticalSplit(self):
            TestHelper.Execute('{Microsoft.Intellipad}SplitVertically', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 2, "Expect split view to be one of two children: %d" % len(slot.Parent.Children)
            self.viewsecond = self.newview
            
            TestHelper.Execute('{Microsoft.Intellipad}SplitVertically', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 3, "Expect split view to be one of three children: %d" % len(slot.Parent.Children)
            self.viewthird = self.newview
            
        def TestCreateHorizontalSplit(self):
            TestHelper.Execute('{Microsoft.Intellipad}SplitHorizontally', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 2, "Expect split view to be one of two children: %d" % len(slot.Parent.Children)
            self.viewfourth = self.newview
            
            TestHelper.Execute('{Microsoft.Intellipad}SplitHorizontally', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 3, "Expect split view to be one of three children: %d" % len(slot.Parent.Children)
            self.viewfifth = self.newview        

        def TestModePreservingSplit(self):
            TestHelper.ResetBufferViews(self.hostWindow)
            self.viewfirst = self.hostWindow.BufferViews[0]
            TestHelper.Execute('{Microsoft.Intellipad}SplitVertically', None, self.viewfirst)
            Common.DrainDispatcher()
            assert self.viewfirst.Mode == self.newview.Mode, "Expect default mode carried over to the splitted view"
            
            self.viewfirst.Mode = MMode
            TestHelper.Execute('{Microsoft.Intellipad}SplitVertically', None, self.viewfirst)
            Common.DrainDispatcher()
            assert self.viewfirst.Mode == self.newview.Mode, "Expect default mode carried over to the splitted view"
            assert self.viewfirst.Mode.GetType() == MMode.GetType(), "Expect view's modes are set to MMode"

         
        def Cleanup(self):
            from System.Collections.Specialized import INotifyCollectionChanged
            INotifyCollectionChanged.remove_CollectionChanged(self.hostWindow.BufferViews, self.OnViewsChanged)    

            for view in self.hostWindow.BufferViews:
                self.bufferViewCleanupModifier(view)

            TestHelper.ResetBufferViews(self.hostWindow)
                
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'BufferListTest')
def BufferListTest():
    class Test(UnitTest):
        def Setup(self):
            self.tempBuffer = None
            self.bl = None
                            
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))

        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            hostWindow = Core.Host.TopLevelWindows[0]
            self.tempBuffer = Common.BufferManager.GetBuffer(System.Uri('transient://tempforbufferlist'))
            view = hostWindow.ShowBuffer(self.tempBuffer)
            Common.DrainDispatcher()
            
            self.bl = Common.BufferManager.GetBuffer(System.Uri('transient://BufferList'))            
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}ListBuffers', None, view)
            Common.DrainDispatcher()
            self.ListBufferView = hostWindow.ActiveView
            bufferViewModifier(self.ListBufferView)            
            Common.DrainDispatcher()
            
            body = self.bl.TextBuffer.CurrentSnapshot.GetText(0, self.bl.TextBuffer.CurrentSnapshot.Length)
            assert body.Contains("transient://tempforbufferlist"), "Could not locate newly created buffer in buffer list: "
            assert body.Contains("transient://bufferlist"), "Could not locate buffer list in buffer list"
            
            bufferViewCleanupModifier(self.ListBufferView)    
        def Cleanup(self):
            if self.tempBuffer is not None:
                self.tempBuffer.Close()
            if self.bl is not None:
                self.bl.Close()            
        
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'YankLineTest')
def YankLineTest():
    from System.Windows.Controls import Orientation
    from Microsoft.VisualStudio.Text.Editor import ITextCaret
    from Microsoft.VisualStudio.Text.Editor import ITextSelection
    class Test(UnitTest):
        def __init__(self):
            self.testView = None
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            self.testView = TestHelper.Split(self.hostWindow.BufferViews[0], Orientation.Horizontal, "")
            self.longStringWithTrailingZ = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxz"

            Common.Write(self.testView.Buffer, "One\r\nTwo\r\nThree\r\nFour\r\nFive\r\nSix" + self.longStringWithTrailingZ)
            Common.SetActiveView(self.testView)
            
        def YankLine(self):
            TestHelper.Execute('{Microsoft.Intellipad}YankLine', None, self.testView)
            
        def MoveCaretTo(self, position):
            caret = self.testView.EditorPrimitives.Caret.AdvancedCaret
            ITextCaret.MoveTo(caret, position)
            
        def Select(self, start, length):
            selection = self.testView.EditorPrimitives.Selection.AdvancedSelection
            ITextSelection.Select(selection, Microsoft.VisualStudio.Text.Span(start, length), False)
            
        def AssertText(self, expectedText):
            actualText = TestHelper.GetText(self.testView)
            assert expectedText == actualText, "Expected '%s' but found '%s'" % (expectedText, actualText)
            
        def Run(self):
            RunImpl(self)
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            Setup(self)
            RunImpl(self, lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))

        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            bufferViewModifier(self.testView)
        
            # Second line
            self.MoveCaretTo(7)
            self.YankLine()
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\nSix' + self.longStringWithTrailingZ)
            
            # Three & Four
            self.Select(7, 7)
            self.YankLine()
            self.AssertText('One\r\nFive\r\nSix'  + self.longStringWithTrailingZ)
            
            # Paste
            TestHelper.Execute('{Microsoft.Intellipad}Paste', None, self.testView)
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\nSix' + self.longStringWithTrailingZ)
            
            # Last line
            self.MoveCaretTo(32)
            self.YankLine()
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\n')

            bufferViewCleanupModifier(self.testView)
        def Cleanup(self):
            TestHelper.CloseViews([self.testView])
            
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'OpenStartFilesTest')
def OpenStartFilesTest():
    class Test(UnitTest):
        def __init__(self):
            self.testView = None
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(self.hostWindow)
            TestHelper.ResetOpenFileBuffers(self.hostWindow)
            
            #Create the 2 temp files
            tempFile1 = System.IO.Path.GetTempFileName()
            System.IO.File.WriteAllText(tempFile1, 'abc')   
            self.tempFileUri1 = System.Uri('file://' + tempFile1)

            tempFile2 = System.IO.Path.GetTempFileName()
            System.IO.File.WriteAllText(tempFile2, '123')   
            self.tempFileUri2 = System.Uri('file://' + tempFile2)
            
        def Run(self):
            bufferCount = self.hostWindow.Host.BufferManager.OpenBuffers.Count
            TestHelper.Execute('{Microsoft.Intellipad}OpenStartFiles', [self.tempFileUri1, self.tempFileUri2], self.hostWindow.ActiveView)
            Common.DrainDispatcher()          
            assert self.hostWindow.Host.BufferManager.OpenBuffers.Count == bufferCount + 2, 'Expected to find 2 more open buffers'

        def Cleanup(self):
            TestHelper.ResetBufferViews(self.hostWindow)
            TestHelper.ResetOpenFileBuffers(self.hostWindow)
            
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'NewTest')
def NewTest():
    class Test(UnitTest):
        def Setup(self):
            self.newBuffer = None
            self.bufferOpenedCalled = False

        def BufferOpened(self, o, e):
            self.bufferOpenedCalled = True
            if e.NewItems != None:
                assert len(e.NewItems) == 1, "Incorrect Number of buffers added"
                self.newBuffer = e.NewItems.get_Item(0)
            
        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            existingBuffers = list(Common.BufferManager.OpenBuffers)
            hostWindow = Core.Host.TopLevelWindows[0]
            
            from System.Collections.Specialized import INotifyCollectionChanged
            INotifyCollectionChanged.add_CollectionChanged(Common.BufferManager.OpenBuffers, self.BufferOpened)    
            
            TestHelper.Execute('{Microsoft.Intellipad}New', None, hostWindow)            
            Common.DrainDispatcher()
            
            from System.Collections.Specialized import INotifyCollectionChanged
            INotifyCollectionChanged.remove_CollectionChanged(Common.BufferManager.OpenBuffers, self.BufferOpened)
            
            
            assert self.bufferOpenedCalled, "BufferOpened function did not execute"
            assert self.newBuffer != None, "No new buffer was found"
            assert self.newBuffer.Uri.Scheme == "file", 'New File "%s" does not have expected "file://" uri scheme' % newItem.Uri.ToString()
            
            view = Common.GetView(hostWindow, self.newBuffer)
            assert view.IsVisible, "New Buffer is not visible"
            assert hostWindow.ActiveView == view, "New BufferView is not the Active Buffer"                    
            
                            
        def Cleanup(self):
            if self.newBuffer is not None:
                self.newBuffer.Close()
        
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'CloseBufferTest')
def CloseBufferTest():
    class Test(UnitTest):

        def Setup(self):
            self.bufferClosed = False

        def BufferClosed(self, o, e):
            self.bufferClosed = True
                                                    
        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            startingBufferCount = Common.BufferManager.OpenBuffers.Count
            newBuffer = Common.BufferManager.GetBuffer(System.Uri("transient://CloseBufferTest"))
            newBuffer.Closed += self.BufferClosed
            hostWindow.ShowBuffer(newBuffer)
            Common.DrainDispatcher()
            assert Common.BufferManager.OpenBuffers.Count == startingBufferCount + 1, "Error creating buffer for test"
            
            view = Common.GetView(hostWindow, newBuffer)
            TestHelper.Execute('{Microsoft.Intellipad}CloseBuffer', None, view)
            Common.DrainDispatcher()
            assert startingBufferCount == Common.BufferManager.OpenBuffers.Count, "End buffer count not equivalent to starting buffer count"
            assert self.bufferClosed, "BufferClosed event did not fire"
            newBuffer.Closed -= self.BufferClosed
        
    return Test()

class SelectionUnitTest(UnitTest):
    def __init__(self):
        self.bufferText = ""

    def Setup(self):
        hostWindow = Core.Host.TopLevelWindows[0]
        self.testBuffer = Common.BufferManager.GetBuffer(System.Uri("transient://SelectUnitTest"))
        hostWindow.ShowBuffer(self.testBuffer)
        self.view = Common.GetView(hostWindow, self.testBuffer)
        self.view.Focus()
        self.view.EditorPrimitives.Caret.MoveToStartOfDocument(False)
        Common.Write(self.testBuffer, self.bufferText)
        Common.DrainDispatcher()

    def Cleanup(self):
        if self.testBuffer is not None:
            self.testBuffer.Close()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'SelectToNextCharacterTest')
def SelectToNextCharacterTest():
    class Test(SelectionUnitTest):
        def __init__(self):
            self.bufferText = "abcd"
            
        def Run(self):
            self.view.EditorPrimitives.Caret.MoveToStartOfDocument(False)
            self.view.EditorPrimitives.Caret.MoveToNextCharacter(False)
            TestHelper.Execute('{Microsoft.Intellipad}SelectToNextCharacter', None, self.view)
            TestHelper.AssertSelectionLocation(self.view, 1, 1, 1)
            
    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'SelectToPreviousCharacterTest')
def SelectToPreviousCharacterTest():
    class Test(SelectionUnitTest):
        def __init__(self):
            self.bufferText = "abcd"
            
        def Run(self):
            self.view.EditorPrimitives.Caret.MoveToStartOfDocument(False)
            self.view.EditorPrimitives.Caret.MoveToNextCharacter(False)
            self.view.EditorPrimitives.Caret.MoveToNextCharacter(False)
            TestHelper.Execute('{Microsoft.Intellipad}SelectToPreviousCharacter', None, self.view)
            TestHelper.AssertSelectionLocation(self.view, 1, 1, 1)
            
    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'SelectToStartOfLineTest')
def SelectToStartOfLineTest():
    class Test(SelectionUnitTest):
        def __init__(self):
            self.bufferText = "abcd"
            
        def Run(self):
            self.view.EditorPrimitives.Caret.MoveToStartOfDocument(False)
            self.view.EditorPrimitives.Caret.MoveToNextCharacter(False)
            self.view.EditorPrimitives.Caret.MoveToNextCharacter(False)
            TestHelper.Execute('{Microsoft.Intellipad}SelectToStartOfLine', None, self.view)
            TestHelper.AssertSelectionLocation(self.view, 1, 0, 2)
            
    return Test()
    
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'SelectToEndOfLineTest')
def SelectToEndOfLineTest():
    class Test(SelectionUnitTest):
        def __init__(self):
            self.bufferText = "abcd"
            
        def Run(self):
            self.view.EditorPrimitives.Caret.MoveToStartOfDocument(False)
            self.view.EditorPrimitives.Caret.MoveToNextCharacter(False)
            TestHelper.Execute('{Microsoft.Intellipad}SelectToEndOfLine', None, self.view)
            TestHelper.AssertSelectionLocation(self.view, 1, 1, 3)
            
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportProperty('{Microsoft.Intellipad.UnitTest}Name', 'UndoRedoTests')
def UndoRedoTests():
    class Test(UnitTest):

        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            startingBufferCount = Common.BufferManager.OpenBuffers.Count
            newBuffer = Common.BufferManager.GetBuffer(System.Uri("transient://UndoRedoTests"))
            hostWindow.ShowBuffer(newBuffer)
            Common.DrainDispatcher()
            assert Common.BufferManager.OpenBuffers.Count == startingBufferCount + 1, "Error creating buffer for test"
                        
            view = Common.GetView(hostWindow, newBuffer)
            view.EditorOperations.InsertText('abc', view.UndoHistory)
            view.EditorOperations.InsertNewline(view.UndoHistory)
            assert TestHelper.GetText(view) == 'abc\r\n'
            
            view.EditorOperations.InsertText('def', view.UndoHistory)
            view.EditorOperations.InsertNewline(view.UndoHistory)
            assert TestHelper.GetText(view) == 'abc\r\ndef\r\n'
            
            view.EditorPrimitives.Caret.MoveToStartOfDocument(False)
            view.EditorOperations.InsertText('123', view.UndoHistory)
            view.EditorOperations.InsertNewline(view.UndoHistory)
            assert TestHelper.GetText(view) == '123\r\nabc\r\ndef\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
            assert TestHelper.GetText(view) == '123abc\r\ndef\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
            assert TestHelper.GetText(view) == 'abc\r\ndef\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
            assert TestHelper.GetText(view) == 'abc\r\ndef'
            
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
            assert TestHelper.GetText(view) == 'abc\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
            assert TestHelper.GetText(view) == 'abc'
            
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
            assert TestHelper.GetText(view) == ''
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, view)
            assert TestHelper.GetText(view) == 'abc'
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, view)
            assert TestHelper.GetText(view) == 'abc\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, view)
            assert TestHelper.GetText(view) == 'abc\r\ndef'
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, view)
            assert TestHelper.GetText(view) == 'abc\r\ndef\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, view)
            assert TestHelper.GetText(view) == '123abc\r\ndef\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, view)
            assert TestHelper.GetText(view) == '123\r\nabc\r\ndef\r\n'
            
            for i in range(1, 10):
            	TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
                assert TestHelper.GetText(view) == '123abc\r\ndef\r\n'
                
                TestHelper.Execute('{Microsoft.Intellipad}Redo', None, view)
                assert TestHelper.GetText(view) == '123\r\nabc\r\ndef\r\n'
            
            TestHelper.Execute('{Microsoft.Intellipad}CloseBuffer', None, view)
            Common.DrainDispatcher()
            assert startingBufferCount == Common.BufferManager.OpenBuffers.Count, "End buffer count not equivalent to starting buffer count"
        
    return Test()