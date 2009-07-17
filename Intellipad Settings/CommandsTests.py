
#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import clr
import sys
import System
import Microsoft
import Common
import FindHelper
from Microsoft.Intellipad.Scripting import UnitTest
from Microsoft.Intellipad.Shell import NamedCommands

clr.AddReference('System.ComponentModel.Composition')
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

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ErrorListManager')
def InitializeErrorListManager(value):
    global ErrorListManager
    ErrorListManager = value

class TestHelperClass:
    def AssertCaretLine(self, view, expectedLine):
        from Microsoft.VisualStudio.Text.Editor import ITextCaret
        caret = view.EditorPrimitives.Caret.AdvancedCaret
        actualLine = ITextCaret.ContainingTextViewLine.GetValue(caret).SnapshotLine.LineNumber
        assert expectedLine == actualLine, "Expected to find line %d, but found %d" % (expectedLine, actualLine)

    def AssertSelectionLocation(self, view, line, column, length):
        snapshot = view.Buffer.TextBuffer.CurrentSnapshot
        snapline = snapshot.GetLineFromLineNumber(line - 1)
        self.AssertSelectionLocationByPosition(view, snapline.Start + column, length)
        
    def AssertSelectionLocationByPosition(self, view, position, length):
        from Microsoft.VisualStudio.Text.Editor import ITextSelection
        selection = view.EditorPrimitives.Selection.AdvancedSelection
        actual = selection.SelectionSpan.Span
        snapshot = view.Buffer.TextBuffer.CurrentSnapshot
        expected = Microsoft.VisualStudio.Text.Span(position, length)
        assert expected == actual, "Expected selection at %s but found %s" % (expected, actual)

    def AssertVisibleText(self, bufferView):
        from Microsoft.VisualStudio.Text.Formatting import VisibilityState
        for line in bufferView.TextEditor.TextView.TextViewLines:
            if line.VisibilityState == VisibilityState.FullyVisible and line.SnapshotLine.GetText().Length > 0:
                return                
        assert False, 'No visible lines contained any text.' 

    def CloseBuffers(self, buffers):
        hostWindow = Core.Host.TopLevelWindows[0]
        for buffer in buffers:
            if buffer is not None:
                if (hostWindow.Host.BufferManager.OpenBuffers.Count == 1):
                    hostWindow.ActiveView.Buffer = Common.BufferManager.GetBuffer(System.Uri('file://'))
                buffer.Close()

    def CloseViews(self, views):
        hostWindow = Core.Host.TopLevelWindows[0]
        buffers = list([view.Buffer for view in views if view is not None])
        for view in views:
            if (view is not None) and (hostWindow.BufferViews.Count > 1):
                view.Close()
        self.CloseBuffers(buffers)
        
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
        
    def DispatcherCheckPredicatePolling(self, predicate, optionalEvent, timeoutSeconds):
        from System.Windows.Threading import DispatcherFrame, Dispatcher, DispatcherTimer
        class Countdown:
            def __init__(self, startingSeconds):
                self.remaining = startingSeconds
            def Decrement(self):
                self.remaining = self.remaining - 1
                return self.remaining

        frame = DispatcherFrame()

        if optionalEvent is not None:
            def Completed(sender,args):
                frame.Continue = False
            optionalEvent += Completed
                    
        countdown = Countdown(timeoutSeconds)
        interval = System.TimeSpan.FromSeconds(1)
        def OnTick(sender, args):
            if countdown.Decrement() <= 0 or predicate():
                frame.Continue = False;

        if not predicate():
            timer = DispatcherTimer()
            timer.Tick += OnTick;
            timer.Interval = interval;
            timer.Start();
            Dispatcher.PushFrame(frame);
            
            timer.Tick -= OnTick;
            timer.Stop();
            
        if optionalEvent is not None:
            optionalEvent -= Completed

        return predicate();

    def Execute(self, name, args, sender):
        NamedCommands.FromName(name).Execute(args, sender)

    def GetNotificationText(self):
        buffer = Core.BufferManager.GetBuffer(System.Uri('transient://notification'))
        snap = buffer.TextBuffer.CurrentSnapshot
        return snap.GetText(0, snap.Length)
        
    def GetText(self, view):
        snap = view.TextBuffer.CurrentSnapshot
        return snap.GetText(0, snap.Length)

    def GetTextPredicateTimeout(self, view, completedEvent, predicate, seconds):
        """Returns the result of applying predicate to the view's text        
        GetTextTimeout will wait 'seconds' for the view to contain the
        text that returns true when passed to 'predicate'.  Once the 
        predicate is true or the timeout elapses it will return the 
        true or false returned by the predicate. This method uses PushFrame 
        to enter an event loop because threads might need to dispatch to the 
        UI thread to complete.
        
        view           - Must have a Buffer with SampleParsed event
        completedEvent - An event that when fired indicates no more waiting is necessary
        predicate      - The function that takes text and returns bool
        seconds        - how long to wait for it
        """
        
        def PredicateFunc():
            return predicate(TestHelper.GetText(view))
        return self.DispatcherCheckPredicatePolling(PredicateFunc, completedEvent, seconds);

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
        def PredicateFunc():
            return expected == TestHelper.GetText(view)
        self.DispatcherCheckPredicatePolling(PredicateFunc, completedEvent, seconds);
        return TestHelper.GetText(view)


    def GetTextTimeoutPolling(self, view, expected, seconds):
        from System.Windows.Threading import DispatcherFrame, Dispatcher, DispatcherTimer
        frame = DispatcherFrame()

        def PredicateFunc():
            return expected == TestHelper.GetText(view)
        self.DispatcherCheckPredicatePolling(PredicateFunc, None, seconds)
        return TestHelper.GetText(view)


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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'ToggleLineNumberTest')
def ToggleLineNumberTest():
    class Test(UnitTest):
        def Run(self):
            try:
            
                from System.Windows.Controls import Orientation
                from Microsoft.Intellipad.Host import LineNumberBehaviorProvider
                hostWindow = Core.Host.TopLevelWindows[0]
                view = TestHelper.Split(hostWindow.BufferViews[0], Orientation.Horizontal, "")               
                
                (result, behaviorInfo) = Common.TryFindBehaviorInfo(LineNumberBehaviorProvider.UniqueId, view)
                assert result
                assert not behaviorInfo.IsEnabled, "Line number behavior should be off"
                TestHelper.Execute('{Microsoft.Intellipad}ToggleLineNumber', None, view)
                assert behaviorInfo.IsEnabled, "Line number behavior should be on"
                TestHelper.Execute('{Microsoft.Intellipad}ToggleLineNumber', None, view)
                assert not behaviorInfo.IsEnabled, "Line number behavior should be off"
                    
            finally:
                TestHelper.CloseViews([view])
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'ToggleWordWrapTest')
def ToggleWordWrapTest():
    class Test(UnitTest):
        def Run(self):
            view = None
            try:

                from Microsoft.VisualStudio.Text.Editor import DefaultTextViewOptions, WordWrapStyles             
                from System.Windows.Controls import Orientation
                from Microsoft.Intellipad.Host import WordWrapBehaviorProvider

                hostWindow = Core.Host.TopLevelWindows[0]
                view = TestHelper.Split(hostWindow.BufferViews[0], Orientation.Horizontal, '')
                Common.DeactivateWordWrap(view)
                
                (result, behaviorInfo) = Common.TryFindBehaviorInfo(WordWrapBehaviorProvider.UniqueId, view)
                assert result
                assert not behaviorInfo.IsEnabled, "Wordwrap behavior should be off"
                TestHelper.Execute('{Microsoft.Intellipad}ToggleWordWrap', None, view)
                assert behaviorInfo.IsEnabled, "Wordwrap behavior should be on"
                result = view.TextEditor.TextView.Options.GetOptionValue[WordWrapStyles](DefaultTextViewOptions.WordWrapStyleId)
                assert result & WordWrapStyles.WordWrap, 'WordWrap style should be on'

                TestHelper.Execute('{Microsoft.Intellipad}ToggleWordWrap', None, view)
                assert not behaviorInfo.IsEnabled, "Wordwrap behavior should be off"
                result = view.TextEditor.TextView.Options.GetOptionValue[WordWrapStyles](DefaultTextViewOptions.WordWrapStyleId)
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'HelpCommandsTest')
def HelpCommandsTest():
    class Test(UnitTest):
        def Run(self):
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.Execute('{Microsoft.Intellipad}HelpCommands', None, hostWindow)
            Common.DrainDispatcher()
            
            VerifyAndCloseHelpView(hostWindow, bufferViewModifier, bufferViewCleanupModifier)
    return Test()
            
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'FindNextPreviousTests')
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
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.Setup()
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'FindTests')
def FindTests():
    from System.Windows.Controls import Orientation
    from Microsoft.VisualStudio.Text.Editor import ITextCaret
    class Test(UnitTest):
    
        def Find(self, text):
            FindHelper.FindImpl(self.findview, text)
            
        def Run(self):
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            self.findview = None
            try:
                self.hostWindow = Core.Host.TopLevelWindows[0]
                self.findview = TestHelper.Split(self.hostWindow.BufferViews[0], Orientation.Horizontal, "")
                
                #Put in long strings so it will word wrap
                Common.WriteLine(self.findview.Buffer, "abc\r\ndef\r\nabc\r\nghi\r\nabc\r\njkl\r\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxz\r\n")
                caret = self.findview.EditorPrimitives.Caret.AdvancedCaret
                ITextCaret.MoveTo(caret, 0)
                Common.SetActiveView(self.findview)

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
            finally:
                TestHelper.CloseViews([self.findview])
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'GotoTests')
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
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.Setup()
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            bufferViewModifier(self.gotoview)
            
            TestHelper.AssertCaretLine(self.gotoview, 0)
            
            self.Goto(3)
            
            TestHelper.AssertCaretLine(self.gotoview, 2)

            self.Goto(0)
            
            TestHelper.AssertCaretLine(self.gotoview, 0)

            self.Goto(100)
            
            TestHelper.AssertCaretLine(self.gotoview, 8)
            
            self.Goto(1e99)
            
            TestHelper.AssertCaretLine(self.gotoview, 8)
          
            self.Goto(10000)
            
            TestHelper.AssertCaretLine(self.gotoview, 8)
            
            self.Goto('a')
            
            TestHelper.AssertCaretLine(self.gotoview, 0)
            
            self.Goto(100000)
            
            TestHelper.AssertCaretLine(self.gotoview, 8)

            self.Goto(-100)
            
            TestHelper.AssertCaretLine(self.gotoview, 0)
            
            
            bufferViewCleanupModifier(self.gotoview)
        def Cleanup(self):
            TestHelper.CloseViews([self.gotoview])
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'ReplaceTests')
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
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.Setup()
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))
            
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'ShrinkExpandNavigateBufferViewTests')
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
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.Setup()
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))

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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SplitTests')
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
            TestHelper.ResetOpenFileBuffers(self.hostWindow)
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
                self.newview = args.NewItems[0]
                if self.bufferViewModifier is not None:
                    self.newview.EnsureEditorIsValid()
                    self.bufferViewModifier(self.newview)    
        
        def Run(self):
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.Setup()
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))

        def RunImpl(self, bufferViewModifier = lambda view : view, bufferViewCleanupModifier = lambda view : view):
            self.bufferViewModifier = bufferViewModifier
            self.bufferViewCleanupModifier = bufferViewCleanupModifier
            self.bufferViewModifier(self.viewfirst)
            
            self.TestCreateHorizontalSplit();
            self.TestCreateVerticalSplit();
            self.TestModePreservingSplit();
    
        def TestCreateHorizontalSplit(self):
            TestHelper.Execute('{Microsoft.Intellipad}SplitHorizontal', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 2, "Expect split view to be one of two children: %d" % len(slot.Parent.Children)
            self.viewsecond = self.newview
            
            TestHelper.Execute('{Microsoft.Intellipad}SplitHorizontal', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 3, "Expect split view to be one of three children: %d" % len(slot.Parent.Children)
            self.viewthird = self.newview
            
        def TestCreateVerticalSplit(self):
            TestHelper.Execute('{Microsoft.Intellipad}SplitVertical', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 2, "Expect split view to be one of two children: %d" % len(slot.Parent.Children)
            self.viewfourth = self.newview
            
            TestHelper.Execute('{Microsoft.Intellipad}SplitVertical', None, self.viewfirst)
            Common.DrainDispatcher()
            slot = self.hostWindow.FindSlot(self.viewfirst)
            assert len(slot.Parent.Children) == 3, "Expect split view to be one of three children: %d" % len(slot.Parent.Children)
            self.viewfifth = self.newview        

        def TestModePreservingSplit(self):
            TestHelper.ResetBufferViews(self.hostWindow)
            self.viewfirst = self.hostWindow.BufferViews[0]
            TestHelper.Execute('{Microsoft.Intellipad}SplitHorizontal', None, self.viewfirst)
            Common.DrainDispatcher()
            assert self.viewfirst.Mode == self.newview.Mode, "Expect default mode carried over to the splitted view"
            
            self.viewfirst.Mode = MMode
            TestHelper.Execute('{Microsoft.Intellipad}SplitHorizontal', None, self.viewfirst)
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'YankLineTest')
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
            self.RunImpl()
            #turn on WordWrap
            TestHelper.ResetBufferViews(Core.Host.TopLevelWindows[0])
            self.Setup()
            self.RunImpl(lambda view : Common.ActivateWordWrap(view), lambda view: Common.DeactivateWordWrap(view))

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
            
            # Test selection/Caret positions
            assert self.testView.TextEditor.TextView.Selection.IsEmpty, "Selection should be empty."
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, self.testView)
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\nSix' + self.longStringWithTrailingZ)
            assert self.testView.TextEditor.TextView.Selection.SelectionSpan.Length == 7, "Selection should be 7 long."
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, self.testView)
            self.AssertText('One\r\nFive\r\nSix'  + self.longStringWithTrailingZ)
            
            # Paste
            TestHelper.Execute('{Microsoft.Intellipad}Paste', None, self.testView)
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\nSix' + self.longStringWithTrailingZ)
            
            # Last line
            self.MoveCaretTo(32)
            self.YankLine()
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\n')
            
            # Selection/Caret Preservation across Undo
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, self.testView)
            assert self.testView.TextEditor.TextView.Caret.Position.Index == 32, "Caret Position should be 32."
            assert self.testView.TextEditor.TextView.Selection.IsEmpty, "Selection should be empty."
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\nSix' + self.longStringWithTrailingZ)
            
            TestHelper.Execute('{Microsoft.Intellipad}Redo', None, self.testView)
            self.AssertText('One\r\nThree\r\nFour\r\nFive\r\n')

            bufferViewCleanupModifier(self.testView)
        def Cleanup(self):
            TestHelper.CloseViews([self.testView])
            
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'OpenStartFilesTest')
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'NewTest')
def NewTest():
    class Test(UnitTest):
        def Setup(self):
            self.newBuffer = None
            self.bufferOpenedCalled = False

        def BufferOpened(self, o, e):
            self.bufferOpenedCalled = True
            if e.NewItems != None:
                assert len(e.NewItems) == 1, "Incorrect Number of buffers added"
                self.newBuffer = e.NewItems[0]
            
        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            existingBuffers = list(Common.BufferManager.OpenBuffers)
            
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'CloseBufferTest')
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SelectToNextCharacterTest')
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SelectToPreviousCharacterTest')
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SelectToStartOfLineTest')
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SelectToEndOfLineTest')
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
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'UndoRedoTests')
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
            view.EditorOperations.InsertNewLine(view.UndoHistory)
            assert TestHelper.GetText(view) == 'abc\r\n'
            
            view.EditorOperations.InsertText('def', view.UndoHistory)
            view.EditorOperations.InsertNewLine(view.UndoHistory)
            assert TestHelper.GetText(view) == 'abc\r\ndef\r\n'
            
            view.EditorPrimitives.Caret.MoveToStartOfDocument(False)
            view.EditorOperations.InsertText('123', view.UndoHistory)
            view.EditorOperations.InsertNewLine(view.UndoHistory)
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
    
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveTest')
def SaveTest():
    class Test(UnitTest):
        def Run(self):

            self.tempFileName = System.IO.Path.GetTempFileName()
            System.IO.File.WriteAllText(self.tempFileName, 'abc')   
            uri = System.Uri('file://' + self.tempFileName)

            hostWindow = Core.Host.TopLevelWindows[0]
            buffer = Common.BufferManager.GetBuffer(uri)
            view = hostWindow.ShowBuffer(buffer)
            Common.DrainDispatcher()
        
            view.EditorOperations.InsertText('abc', view.UndoHistory)
            Common.DrainDispatcher()
            assert buffer.IsDirty == True, "Buffer should become dirty after inserting some text"
        
            TestHelper.Execute('{Microsoft.Intellipad}Save', None, view)
            Common.DrainDispatcher()
            assert buffer.IsDirty == False, "Buffer should not be dirty after save"

            #should be no-op
            TestHelper.Execute('{Microsoft.Intellipad}Escape', None, view)
            Common.DrainDispatcher()

            buffer.Close()            

        def Cleanup(self):
            System.IO.File.Delete(self.tempFileName)
            
    return Test()
    

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveACopyTest')
def SaveACopyTest():
    class Test(UnitTest):
        def Run(self):
            from System.IO import File, Path
            from System.Threading import Thread
            from System.Windows.Controls import Orientation

            initialBuffer = Common.BufferManager.GetBuffer(System.Uri('file:///C:/foo'))
            initialBufferUri = initialBuffer.Uri     
            hostWindow = Core.Host.TopLevelWindows[0]
            view = hostWindow.ShowBuffer(initialBuffer)
            Common.DrainDispatcher()
            bufferText = 'abc'
            initialBuffer.TextBuffer.Insert(0, bufferText)
            Common.DrainDispatcher()
            copyBuffer = None
            
            secondView = hostWindow.SplitBufferView(view, Orientation.Horizontal)
            Common.DrainDispatcher()

            file = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString('N'))
            Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), file)
            try:
                TestHelper.Execute('{Microsoft.Intellipad}SaveACopy', None, view)
                Common.DrainDispatcher()
                copyBuffer = view.Buffer
                assert copyBuffer.Uri.LocalPath == file, 'Copied file was not opened in active view'
                assert secondView.Buffer is initialBuffer, 'Original buffer should have remained open in other view'
                assert initialBuffer.IsDirty, 'Original buffer was not marked dirty'
                assert initialBuffer.TextBuffer.CurrentSnapshot.GetText() == bufferText, 'Text in original buffer should not have been modified'
                assert copyBuffer.TextBuffer.CurrentSnapshot.GetText() == bufferText, 'Text was not copied to new buffer'
                assert not copyBuffer.IsDirty, 'Copied buffer was wrongly marked dirty'
                assert File.ReadAllText(file) == bufferText, 'text content was not saved to file'
                if not hostWindow.Settings.MostRecentlyUsed.Contains(copyBuffer.Uri):
                    # notification buffer has reason
                    text = TestHelper.GetNotificationText()
                    assert False, "Copied buffer was not added to MRU, notification buffer contents:\r\n%s" % text

            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), None)
                secondView.Close()
                if initialBuffer is not None:
                    initialBuffer.Close()
                if copyBuffer is not None:
                    copyBuffer.Close()
                if File.Exists(file):
                    File.Delete(file)
    return Test()

    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveAsTest')
def SaveAsTest():
    class Test(UnitTest):
        def Run(self):
            from System.Windows.Controls import Orientation
            from System.Threading import Thread
            from System.IO import File, Path

            pollingSeconds = 60
            mInput = "module M { type T { Id : Integer32; X : Text; } Ts : T* where identity (Id); }"
            origFileName = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString("N"))
            origFileName = origFileName + '.m'
            File.WriteAllText(origFileName, mInput)
            filesToDelete = [origFileName]
            try:
                buffer = Common.BufferManager.GetBuffer(System.Uri(origFileName))
                bufferToClose = buffer
                hostWindow = Core.Host.TopLevelWindows[0]
                view = hostWindow.ShowBuffer(buffer)
                secondView = hostWindow.SplitBufferView(view, Orientation.Horizontal)
                Common.DrainDispatcher()

                TestHelper.Execute('{Microsoft.Intellipad}MoveToEndOfDocument', None, view)
                TestHelper.Execute('{Microsoft.Intellipad}Backspace', None, view)
            
                TestHelper.Execute('{Microsoft.Intellipad}ShowErrorList', None, hostWindow)
                Common.DrainDispatcher()

                errorBuffer = Common.GetOrCreateErrorBuffer()
                errorView = Common.GetView(hostWindow, errorBuffer)
                assert errorView is not None, 'no error view'
                
                def IsNotEmpty(text):
                    return text.Length > 0
                    
                TestHelper.GetTextPredicateTimeout(errorView, errorBuffer.TextBuffer.Changed, IsNotEmpty, pollingSeconds)
                assert ErrorListManager.GetErrorsForBuffer(buffer).Count > 0, 'No errors after } deleted'
                
                savedFileName = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString("N"))
                savedFileName = savedFileName + '.m'
                filesToDelete = filesToDelete + [savedFileName]
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), savedFileName)
                TestHelper.Execute('{Microsoft.Intellipad}SaveAs', None, view)
                Common.DrainDispatcher()
                
                (result, buffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + origFileName))
                assert not result, 'original buffer not closed'
                (result, buffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + savedFileName))
                assert result, 'saved-as buffer not opened'
                assert view.Buffer == buffer, 'buffer not opened in previous view'
                assert secondView.Buffer == buffer, 'buffer not opened in all previous views'
                bufferToClose = buffer

                buffer.TextBuffer.Insert(buffer.TextBuffer.CurrentSnapshot.Length, '}')
                
                def IsEmpty(text):
                    return text.Length == 0
                TestHelper.GetTextPredicateTimeout(errorView, errorBuffer.TextBuffer.Changed, IsEmpty, pollingSeconds)
                assert ErrorListManager.GetErrorsForBuffer(buffer).Count == 0, 'Errors remain after } replaced'
                assert File.ReadAllText(origFileName) == mInput, 'Edits should not have been saved on original buffer'
                
                standardMode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}StandardMode');
                view.Mode = standardMode
                secondView.Mode = standardMode
                savedFileName = savedFileName.Replace('.m', ' 2.m')
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), savedFileName)
                TestHelper.Execute('{Microsoft.Intellipad}SaveAs', None, view)
                Common.DrainDispatcher()

                filesToDelete = filesToDelete + [savedFileName]
                assert view.Buffer.Uri.LocalPath.EndsWith(' 2.m'), 'new buffer not set in view'
                bufferToClose = view.Buffer
                assert view.Mode == standardMode, 'View should have the set mode regardless of file extension'
                assert secondView.Mode == standardMode, 'View should have the set mode regardless of file extension'
                                
            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), None)
                if bufferToClose is not None:
                    bufferToClose.Close()
                for filename in filesToDelete:
                    File.Delete(filename)
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveAsWithCancelTest')
def SaveAsWithCancelTest():
    class Test(UnitTest):
        def Run(self):
            from System.Threading import Thread
            
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(hostWindow)
            TestHelper.ResetOpenFileBuffers(hostWindow)
            
            try:
                buffer = Common.BufferManager.GetBuffer(System.Uri("file://"))
                buffer.TextBuffer.Insert(0,"Hello World")
                bufferToClose = buffer
                view = hostWindow.ShowBuffer(buffer)
                Common.DrainDispatcher()
                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}CancelFileOverride'), True)
                TestHelper.Execute('{Microsoft.Intellipad}SaveAs', None, view)
                
                assert view.IsKeyboardFocusWithin, "Focus should be on the same window after a cancel on Save As"
            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}CancelFileOverride'), None)
                if bufferToClose is not None:
                    bufferToClose.Close()
    return Test()



@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveAllMultipleNewFileTest')
def SaveAllMultipleNewFileTest():
    class Test(UnitTest):
        def Run(self):
            from System.Threading import Thread
            from System.IO import File, Path
            
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(hostWindow)
            TestHelper.ResetOpenFileBuffers(hostWindow)
            
            def createAndEditBufferWithText(text):
                newBuffer = Common.BufferManager.GetBuffer(System.Uri("file://"))
                newBuffer.TextBuffer.Insert(0,text)
                return newBuffer
            
            try:
                buffers = [createAndEditBufferWithText("Hello")]
                buffers = buffers + [createAndEditBufferWithText("World")]
                buffers = buffers + [createAndEditBufferWithText("This")]
                buffers = buffers + [createAndEditBufferWithText("Is")]
                buffers = buffers + [createAndEditBufferWithText("A")]
                buffers = buffers + [createAndEditBufferWithText("Test")]
                buffers = buffers + [createAndEditBufferWithText("Case")]
                buffersToClose = buffers
                
                Common.DrainDispatcher()
                
                filesToSave = []
                for buffer in buffers:
                    savedFName = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString("N"))
                    savedFName = savedFName + '.m'
                    filesToSave = filesToSave + [savedFName]
                
                filesToDelete = filesToSave
                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), filesToSave)
                           
                TestHelper.Execute('{Microsoft.Intellipad}SaveAll', None, hostWindow)
                Common.DrainDispatcher()
                
                fileCount = 0
                while fileCount < len(buffers):
                    (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + buffers[fileCount].Title))
                    assert not result, 'original ' + buffers[fileCount].Title + ' not closed'
                    (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + filesToSave[fileCount]))
                    assert result, 'saved-as ' + filesToSave[fileCount] + ' not opened'
                    buffersToClose = buffersToClose + [resultBuffer]
                    fileCount = fileCount + 1
                
            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), None)
                for buf in buffersToClose:
                    buf.Close()
                for filename in filesToDelete:
                    File.Delete(filename)
    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveAllSingleFileTest')
def SaveAllSingleFileTest():
    class Test(UnitTest):
        def Run(self):
            from System.Threading import Thread
            from System.IO import File, Path
            
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(hostWindow)
            TestHelper.ResetOpenFileBuffers(hostWindow)
            
            try:
                buffer1 = Common.BufferManager.GetBuffer(System.Uri("file://"))
                bufferName1 = buffer1.Title
                buffer1.TextBuffer.Insert(0,"Hello World")
                buffersToClose = [buffer1]
                
                Common.DrainDispatcher()
                
                savedFileName1 = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString("N"))
                savedFileName1 = savedFileName1 + '.m'
                filesToSave = [savedFileName1]
                filesToDelete = filesToSave
                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), filesToSave)
                TestHelper.Execute('{Microsoft.Intellipad}SaveAll', None, hostWindow)
                Common.DrainDispatcher()
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + bufferName1))
                assert not result, 'original buffer1 not closed'
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + savedFileName1))
                assert result, 'saved-as buffer1 not opened'
                buffersToClose = buffersToClose + [resultBuffer]
                
            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), None)
                for buf in buffersToClose:
                    buf.Close()
                for filename in filesToDelete:
                    File.Delete(filename)
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveAllWithCancel')
def SaveAllWithCancel():
    class Test(UnitTest):
        def Run(self):
            from System.Threading import Thread
            from System.IO import File, Path
            
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(hostWindow)
            TestHelper.ResetOpenFileBuffers(hostWindow)
  
            try:
                buffer1 = Common.BufferManager.GetBuffer(System.Uri("file://"))
                bufferName1 = buffer1.Title
                buffer1.TextBuffer.Insert(0,"Hello")
                buffersToClose = [buffer1]
                
                buffer2 = Common.BufferManager.GetBuffer(System.Uri("file://"))
                bufferName2 = buffer2.Title
                buffer2.TextBuffer.Insert(0, "World")
                buffersToClose = buffersToClose + [buffer2]
                
                buffer3 = Common.BufferManager.GetBuffer(System.Uri("file://"))
                bufferName3 = buffer3.Title
                buffer3.TextBuffer.Insert(0, "!!!!!")
                buffersToClose = buffersToClose + [buffer3]
                
                Common.DrainDispatcher()
                
                savedFileName1 = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString("N"))
                savedFileName1 = savedFileName1 + '.m'
                filesToSave = [savedFileName1]
                filesToDelete = filesToSave
                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), filesToSave)
                TestHelper.Execute('{Microsoft.Intellipad}SaveAll', None, hostWindow)
                Common.DrainDispatcher()
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + bufferName1))
                assert not result, 'original buffer1 not closed'
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + savedFileName1))
                assert result, 'saved-as buffer1 not opened'
                buffersToClose = buffersToClose + [resultBuffer]
                buffer1 = resultBuffer
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file://' + bufferName2 + '/'))
                assert result, 'original buffer2 was closed'
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file://' + bufferName3 + '/'))
                assert result, 'original buffer3 was closed'

                buffer1.TextBuffer.Insert(0, "More Text")

                savedFileName2 = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString("N"))
                savedFileName2 = savedFileName2 + '.m'
                filesToSave = [savedFileName2]
                Common.DrainDispatcher()
                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), filesToSave)
                TestHelper.Execute('{Microsoft.Intellipad}SaveAll', None, hostWindow)
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + bufferName2))
                assert not result, 'original buffer2 not closed'
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + savedFileName2))
                assert result, 'saved-as buffer2 not opened'
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + savedFileName1))
                assert resultBuffer.IsDirty, 'buffer1 is not supposed to be saved'
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file://' + bufferName3 + '/'))
                assert result, 'original buffer3 was closed'
                
            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), None)
                for buf in buffersToClose:
                    buf.Close()
                for filename in filesToDelete:
                    File.Delete(filename)
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SaveAllMultipleViews')
def SaveAllMultipleViews():
    class Test(UnitTest):
        def Run(self):
            from System.Threading import Thread
            from System.IO import File, Path
            from System.Windows.Controls import Orientation
            
            hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(hostWindow)
            TestHelper.ResetOpenFileBuffers(hostWindow)
            
            def createAndEditBufferWithText(text):
                newBuffer = Common.BufferManager.GetBuffer(System.Uri("file://"))
                newBuffer.TextBuffer.Insert(0,text)
                return newBuffer
            
            def saveBufferName(name):
                savedFName = Path.Combine(Path.GetTempPath(), name)
                savedFName = savedFName + '.m'
                return savedFName
            
            try:
                buffers = [createAndEditBufferWithText("TestFile1")]
                buffers = buffers + [createAndEditBufferWithText("TestFile2")]
                buffers = buffers + [createAndEditBufferWithText("TestFile3")]
                
                view1 = hostWindow.SplitBufferView(hostWindow.BufferViews[0], Orientation.Horizontal)
                view2 = hostWindow.SplitBufferView(hostWindow.BufferViews[0], Orientation.Horizontal)
                view3 = hostWindow.SplitBufferView(hostWindow.BufferViews[0], Orientation.Horizontal)
                
                Common.DrainDispatcher()
                
                openBuffers = list(hostWindow.Host.BufferManager.OpenBuffers)
                
                view1.Buffer = buffers[0]
                view2.Buffer = buffers[1]
                view3.Buffer = buffers[1]
                
                filesToSave = []
                filesToSave = filesToSave + [saveBufferName("SaveAllFile1")]
                filesToSave = filesToSave + [saveBufferName("SaveAllFile2")]
                filesToSave = filesToSave + [saveBufferName("SaveAllFile3")]
                
                # add a Non dirty buffer after since we don't want to override the save
                buffers = buffers + [Common.BufferManager.GetBuffer(System.Uri("file://"))]
                buffersToClose = buffers
                
                filesToDelete = filesToSave
                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), filesToSave)
                           
                TestHelper.Execute('{Microsoft.Intellipad}SaveAll', None, hostWindow)
                Common.DrainDispatcher()
                
                assert view1.Buffer.Title == "SaveAllFile1.m", 'The bufferview is displaying the wrong buffer'
                assert view2.Buffer.Title == "SaveAllFile2.m", 'The bufferview is displaying the wrong buffer'
                assert view3.Buffer.Title == "SaveAllFile2.m", 'The bufferview is displaying the wrong buffer'

                fileCount = 0
                # check 3 of the 4 buffers since the last one is not dirty so won't be saved
                while fileCount < (len(buffers)-1):
                    (result, resultBuffer) = Common.BufferManager.TryGetBuffer(buffers[fileCount].Uri)
                    assert not result, 'original ' + buffers[fileCount].Title + ' not closed'
                    (result, resultBuffer) = Common.BufferManager.TryGetBuffer(System.Uri('file:///' + filesToSave[fileCount]))
                    assert result, 'saved-as ' + filesToSave[fileCount] + ' not opened'
                    buffersToClose = buffersToClose + [resultBuffer]
                    fileCount = fileCount + 1
                
                (result, resultBuffer) = Common.BufferManager.TryGetBuffer(buffers[3].Uri)
                assert result, 'original ' + buffers[3].Title + ' closed'

            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), None)
                for buf in buffersToClose:
                    buf.Close()
                for filename in filesToDelete:
                    File.Delete(filename)
    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'BuiltInVSEditorCommandTest')
def BuiltInVSEditorCommandTest():
    from System import Uri
    class Test(UnitTest):
        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            buffer = Common.BufferManager.GetBuffer(Uri('file://'))
            view = hostWindow.ShowBuffer(buffer)
            Common.DrainDispatcher()

            view.EditorOperations.InsertText('1\r\n2\r\n3\r\n4\r\n', view.UndoHistory)
            Common.DrainDispatcher()

            #Move to start of document
            TestHelper.Execute('{Microsoft.Intellipad}MoveToStartOfDocument', None, view)
            Common.DrainDispatcher()
            
            #Select Line '1\r\n'
            TestHelper.Execute('{Microsoft.Intellipad}SelectLineDown', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1\r\n', 'Selected 1st line'

            #Select Line '1\r\n2\r\n'
            TestHelper.Execute('{Microsoft.Intellipad}SelectLineDown', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1\r\n2\r\n', 'Selected 1st and 2nd line'

            #Move to end of document
            TestHelper.Execute('{Microsoft.Intellipad}MoveToEndOfDocument', None, view)
            Common.DrainDispatcher()

            #Select Line '4\r\n'
            TestHelper.Execute('{Microsoft.Intellipad}SelectLineUp', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '4\r\n', 'Selected 4th'

            #Select Line '3\r\n4\r\n'
            TestHelper.Execute('{Microsoft.Intellipad}SelectLineUp', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '3\r\n4\r\n', 'Selected 3rd and 4th'

            TestHelper.Execute('{Microsoft.Intellipad}SelectLineUp', None, view)
            TestHelper.Execute('{Microsoft.Intellipad}SelectLineUp', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1\r\n2\r\n3\r\n4\r\n', 'It should select all 4 lines'
            
            TestHelper.Execute('{Microsoft.Intellipad}ResetSelection', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '', 'It should select nothing'
                        
            TestHelper.Execute('{Microsoft.Intellipad}SelectAll', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1\r\n2\r\n3\r\n4\r\n', 'It should select all 4 lines'
            
            TestHelper.Execute('{Microsoft.Intellipad}CutSelection', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '', 'It should select nothing'
            
            TestHelper.Execute('{Microsoft.Intellipad}Paste', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}SelectAll', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1\r\n2\r\n3\r\n4\r\n', 'It should select all 4 lines'

            TestHelper.Execute('{Microsoft.Intellipad}CopySelection', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}Paste', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '', 'It should select nothing'
            
            buffer.Close()
                        
        def GetSelectedText(self, view):
            return view.EditorOperations.TextView.Selection.SelectionSpan.GetText()
            
        def Cleanup(self):
            return
    return Test()
    
    
    
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'BuiltInVSEditorCommandTest2')
def BuiltInVSEditorCommandTest2():
    from System import Uri
    class Test(UnitTest):
        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            buffer = Common.BufferManager.GetBuffer(Uri('file://'))
            view = hostWindow.ShowBuffer(buffer)
            Common.DrainDispatcher()
            
            TestHelper.Execute('{Microsoft.Intellipad}SetStandardMode', None, view)
            Common.DrainDispatcher()
            
            view.EditorOperations.InsertText('1 a b c\r\n2 b\r\n3 c\r\n4 d\r\n', view.UndoHistory)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MoveToStartOfDocument', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MoveToEndOfLine', None, view)
            Common.DrainDispatcher()
            
            TestHelper.Execute('{Microsoft.Intellipad}MoveToNextWord', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}SelectToStartOfDocument', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1 a b c\r\n', 'Should select up to 2'
            
            TestHelper.Execute('{Microsoft.Intellipad}MoveToEndOfLine', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MoveToPreviousWord', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}SelectToStartOfDocument', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1 a b ', 'Should select up to B'
            
            TestHelper.Execute('{Microsoft.Intellipad}ResetSelection', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MoveToNextWord', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}DeleteWordToRight', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == '1 b c\r\n2 b\r\n3 c\r\n4 d\r\n', 'first line should be 1 b c'
            
            TestHelper.Execute('{Microsoft.Intellipad}DeleteWordToLeft', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == 'b c\r\n2 b\r\n3 c\r\n4 d\r\n', 'first line should be b c'
            view.EditorOperations.InsertText('1 a ', view.UndoHistory)
            
            TestHelper.Execute('{Microsoft.Intellipad}MoveToStartOfLine', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}Indent', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == '    1 a b c\r\n2 b\r\n3 c\r\n4 d\r\n', 'It will unindent the 1st line'

            TestHelper.Execute('{Microsoft.Intellipad}Unindent', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == '1 a b c\r\n2 b\r\n3 c\r\n4 d\r\n', 'It will unindent the 1st line'

            TestHelper.Execute('{Microsoft.Intellipad}Delete', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}Undo', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == '1 a b c\r\n2 b\r\n3 c\r\n4 d\r\n', 'Delete and undo should cancel out each other'

            TestHelper.Execute('{Microsoft.Intellipad}SelectToEndOfDocument', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1 a b c\r\n2 b\r\n3 c\r\n4 d\r\n', 'Should select the whole document'

            TestHelper.Execute('{Microsoft.Intellipad}ResetSelection', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MoveToStartOfDocument', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}InsertNewline', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == '\r\n1 a b c\r\n2 b\r\n3 c\r\n4 d\r\n', 'It will insert a new line'

            TestHelper.Execute('{Microsoft.Intellipad}SelectToNextWord', None, view)
            TestHelper.Execute('{Microsoft.Intellipad}SelectToNextWord', None, view)
            TestHelper.Execute('{Microsoft.Intellipad}SelectToNextWord', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MakeUppercase', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == '\r\n1 A B c\r\n2 b\r\n3 c\r\n4 d\r\n', 'Make uppercase'

            TestHelper.Execute('{Microsoft.Intellipad}SelectToPreviousWord', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MakeLowercase', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == '\r\n1 a B c\r\n2 b\r\n3 c\r\n4 d\r\n', 'Make lowercase'

            TestHelper.Execute('{Microsoft.Intellipad}SelectToStartOfLine', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '', 'Nothing should be selected'

            TestHelper.Execute('{Microsoft.Intellipad}SelectToEndOfLine', None, view)
            Common.DrainDispatcher()
            assert self.GetSelectedText(view) == '1 a B c', '2nd line should be selected'

            buffer.Close()
           
        def GetSelectedText(self, view):
            return view.EditorOperations.TextView.Selection.SelectionSpan.GetText()

        def GetCurrentSnapshotText(self, view):
            return view.TextBuffer.CurrentSnapshot.GetText(0, view.TextBuffer.CurrentSnapshot.Length)
            
        def Cleanup(self):
            return
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'BuiltInVSEditorCommandTest3')
def BuiltInVSEditorCommandTest3():
    from System import Uri
    class Test(UnitTest):
        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            buffer = Common.BufferManager.GetBuffer(Uri('file://'))
            view = hostWindow.ShowBuffer(buffer)
            Common.DrainDispatcher()
                        
            view.EditorOperations.InsertText('abcd\r\nefgh', view.UndoHistory)
            Common.DrainDispatcher()
            
            TestHelper.Execute('{Microsoft.Intellipad}MoveToStartOfDocument', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MoveToNextCharacter', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}MoveToNextCharacter', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}TransposeCharacter', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == 'acbd\r\nefgh', '1st line should be acbd'
            
            TestHelper.Execute('{Microsoft.Intellipad}Backspace', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == 'acd\r\nefgh', '1st line should be acd'
            
            TestHelper.Execute('{Microsoft.Intellipad}MoveLineDown', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}TransposeCharacter', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}TransposeLine', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == 'egfh\r\nacd', '1st line should be egfh'

            TestHelper.Execute('{Microsoft.Intellipad}MoveLineUp', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}TransposeCharacter', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == 'eghf\r\nacd', '1st line should be eghf'

            TestHelper.Execute('{Microsoft.Intellipad}MoveToPreviousCharacter', None, view)
            TestHelper.Execute('{Microsoft.Intellipad}MoveToPreviousCharacter', None, view)
            TestHelper.Execute('{Microsoft.Intellipad}MoveToPreviousCharacter', None, view)
            TestHelper.Execute('{Microsoft.Intellipad}MoveToPreviousCharacter', None, view)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}TransposeCharacter', None, view)
            Common.DrainDispatcher()
            assert self.GetCurrentSnapshotText(view) == 'gehf\r\nacd', '1st line should be gehf'

            buffer.Close()

            
        def GetSelectedText(self, view):
            return view.EditorOperations.TextView.Selection.SelectionSpan.GetText()

        def GetCurrentSnapshotText(self, view):
            return view.TextBuffer.CurrentSnapshot.GetText(0, view.TextBuffer.CurrentSnapshot.Length)
            
        def Cleanup(self):
            return
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'BufferViewHostCloseButtonTest')
def BufferViewHostCloseButtonTest():
    from System.Windows.Controls import Orientation
    from System.Windows import Visibility
    
    global Core
    class Test(UnitTest):
        def __init__(self):
            self.viewzero = None
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(self.hostWindow)

            from System.Collections.Specialized import INotifyCollectionChanged
            INotifyCollectionChanged.add_CollectionChanged(self.hostWindow.BufferViews, self.OnViewsChanged)    
            
        def OnViewsChanged(self, sender, args):
            if args.NewItems != None:
                assert len(args.NewItems) == 1, "We should only get one new view at a time in this test"
                self.newview = args.NewItems[0]
                            
        def Run(self):
        
            # 1 slot only
            self.originalview = self.hostWindow.BufferViews[0]
            self.orientation = Orientation.Vertical
            assert self.CloseButtonEnabledOnViewHost(self.originalview) == False, "When there is only 1 slot and 1 buffer, close button should not be Enabled"

            TestHelper.Execute('{Microsoft.Intellipad}New', None, self.originalview)
            Common.DrainDispatcher()
            assert self.CloseButtonEnabledOnViewHost(self.originalview) == False, "When there is only 1 slot but multiple buffers, close button should not be enabled"

            # 2 slots
            Common.SetActiveView(self.originalview)   
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}SplitHorizontal', None, self.originalview)         
            Common.DrainDispatcher()
            self.secondview = self.newview
            assert self.CloseButtonEnabledOnViewHost(self.originalview) == True, "When there is 2 slots, close button should be visible"
            assert self.CloseButtonEnabledOnViewHost(self.secondview) == True, "When there is 2 slots, close button should be visible"


            # 3 slots
            Common.SetActiveView(self.originalview)   
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad}SplitVertical', None, self.originalview)         
            Common.DrainDispatcher()
            self.thirdview = self.newview
            assert self.CloseButtonEnabledOnViewHost(self.originalview) == True, "When there are 3 slots, close button should be visible"
            assert self.CloseButtonEnabledOnViewHost(self.secondview) == True, "When there are 3 slots, close button should be visible"
            assert self.CloseButtonEnabledOnViewHost(self.thirdview) == True, "When there are 3 slots, close button should be visible"
            
            # close 2 of the views
            self.secondview.Close()
            self.thirdview.Close()
            Common.DrainDispatcher()
            assert self.CloseButtonEnabledOnViewHost(self.originalview) == False, "When there is only 1 slot but multiple buffers, close button should not be enabled"
            
        def CloseButtonEnabledOnViewHost(self, bufferView):           
            viewHost = Common.FindParent(Microsoft.Intellipad.Host.BufferViewHost, bufferView)
            closeButton = viewHost.Template.FindName("closeButton", viewHost)
            return closeButton.Command.CanExecute(viewHost, None)
                                 
        def Cleanup(self):
            from System.Collections.Specialized import INotifyCollectionChanged
            INotifyCollectionChanged.remove_CollectionChanged(self.hostWindow.BufferViews, self.OnViewsChanged)    
            TestHelper.ResetBufferViews(self.hostWindow)

            
    return Test()

@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Ignore', True)
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'SquiggleFilteringTest')
def SquiggleFilteringTest():
    from Microsoft.Intellipad.LanguageServices import ListBufferHelper
    class Test(UnitTest):

        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(self.hostWindow) 
            TestHelper.ResetOpenFileBuffers(self.hostWindow)

        def Run(self):
            content = """\
module M
{
  E : Integer;
  F : Logical;
  G = E.Count == 1 && F ? -1 : 1;
}
""".replace("\n", "\r\n")

            self.tempFileName = System.IO.Path.GetTempFileName()
            uri = System.Uri('file://' + self.tempFileName)
            self.fileBuffer = Core.Host.BufferManager.GetBuffer(uri)
            
            hostWindow = Core.Host.TopLevelWindows[0]
            self.fileView = hostWindow.ShowBuffer(self.fileBuffer)
            self.fileView.Mode = MMode
            
            Common.WriteLine(self.fileView.Buffer, content)

            TestHelper.Execute('{Microsoft.Intellipad}ShowErrorList', None, self.fileView)
            Common.DrainDispatcher()
 
            #error should be similar to this: error: Cannot resolve the reference to 'Count'
            shouldContainText = 'Count' 
            
            self.errorBuffer = Core.Host.BufferManager.GetBuffer(System.Uri('transient://errors'))
            self.errorView = Common.GetView(hostWindow, self.errorBuffer)

            def CheckContains(text):
                return text.Contains(shouldContainText)

            actual = TestHelper.GetTextPredicateTimeout(self.errorView, self.errorBuffer.TextBuffer.Changed, CheckContains, 10)            
            assert actual, "Expected contains \'%s\' but  \'%s\'" % (shouldContainText, TestHelper.GetText(self.errorView))
            self.listBufferHelper = ListBufferHelper.GetOrCreate(self.errorBuffer)
            assert self.listBufferHelper.Items.Count == 1, "Expected only 1 semantic error and newline at the end, but got %d" % (self.listBufferHelper.Items.Count)

        def Cleanup(self):
            if self.fileBuffer is not None: self.fileBuffer.Close()
            if self.tempFileName is not None:
                if System.IO.File.Exists(self.tempFileName): System.IO.File.Delete(self.tempFileName)
            
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'MiniBufferCommandPromptTest')
def MiniBufferCommandPromptTest():
    class Test(UnitTest):

        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            #TestHelper.ResetBufferViews(self.hostWindow) 
            TestHelper.ResetOpenFileBuffers(self.hostWindow)

            # we don't want any pre existing minibuffer text            
            self.miniBuffer = Core.Host.BufferManager.GetBuffer(System.Uri('transient://mini-buffer'))
            if self.miniBuffer is not None:
                Common.Clear(self.miniBuffer)
                
            # create a new untitled buffer which will become the last ActiveView
            TestHelper.Execute('{Microsoft.Intellipad}New', None, self.hostWindow.ActiveView)
            Common.DrainDispatcher()
            
        def Run(self):
            expected = 'hello world'
            
            targetView = self.hostWindow.ActiveView
            Common.ActivateMiniBuffer(False)
            Common.DrainDispatcher()
            
            self.miniBuffer.TextBuffer.Insert(self.miniBuffer.TextBuffer.CurrentSnapshot.Length, "Core.Host.TopLevelWindows[0].PreviousActiveView.TextBuffer.Insert(0, 'hello world')")
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad.Scripting}Execute', None, Common.GetView(self.hostWindow, self.miniBuffer))
            Common.DrainDispatcher()
            
            actual = TestHelper.GetTextTimeout(targetView, targetView.TextBuffer.Changed, expected, 10)
            assert actual.Contains(expected), "Expected \'%s\' but contains \'%s\'" % (expected, actual)
            Common.DeactivateMiniBuffer()
            
        def Cleanup(self):
            TestHelper.ResetBufferViews(self.hostWindow) 
            TestHelper.ResetOpenFileBuffers(self.hostWindow)
            
    return Test()
    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'MiniBufferOpenCommandTest')
def MiniBufferOpenCommandTest():
    from System.ComponentModel.Composition.Hosting import CompositionServices 
    class Test(UnitTest):

        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            #We don't want to reset the buffer views in this case
            #TestHelper.ResetBufferViews(self.hostWindow) 
            TestHelper.ResetOpenFileBuffers(self.hostWindow)

            # we don't want any pre existing minibuffer text            
            self.miniBuffer = Core.Host.BufferManager.GetBuffer(System.Uri('transient://mini-buffer'))
            Common.DrainDispatcher()            
            
        def Run(self):
            requestedName = 'jdkirtubndhll' # use only lowercase since AbsoluteUri gives lowercase
            requestedBadScheme = requestedName + '2'
            
            Common.ActivateMiniBuffer(False)
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad.Scripting}Execute', None, Common.GetView(self.hostWindow, self.miniBuffer))
            Common.DrainDispatcher()
            self.miniBuffer.TextBuffer.Insert(self.miniBuffer.TextBuffer.CurrentSnapshot.Length, "Open('transient://" + requestedName + "')")
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad.Scripting}Execute', None, Common.GetView(self.hostWindow, self.miniBuffer))
            Common.DrainDispatcher()
            
            activeBufferAfterGoodRequest = self.hostWindow.ActiveView.Buffer #don't assert here so can close buffer if open, below

            self.miniBuffer = Core.Host.BufferManager.GetBuffer(System.Uri('transient://mini-buffer'))
            if self.miniBuffer is not None:
                Common.Clear(self.miniBuffer)
            Common.DrainDispatcher()           
            Common.ActivateMiniBuffer(False)
            Common.DrainDispatcher()            
            self.miniBuffer.TextBuffer.Insert(self.miniBuffer.TextBuffer.CurrentSnapshot.Length, "Open('scheme://" + requestedBadScheme + "')")
            Common.DrainDispatcher()
            TestHelper.Execute('{Microsoft.Intellipad.Scripting}Execute', None, Common.GetView(self.hostWindow, self.miniBuffer))
            Common.DrainDispatcher()

            expectedBuffer = None
            unexpectedBuffer = None
            notificationBuffer = None
            buffernames = ''
            for openBuffer in Core.Host.BufferManager.OpenBuffers:
                buffernames = "%s, %s" % (buffernames, openBuffer.Uri.AbsoluteUri)
                if openBuffer.Uri.AbsoluteUri.TrimEnd('/').EndsWith(requestedName):
                    expectedBuffer = openBuffer
                elif openBuffer.Uri.AbsoluteUri.TrimEnd('/').EndsWith(requestedBadScheme):
                    unexpectedBuffer = openBuffer
                elif openBuffer.Title == 'notification':
                    notificationBuffer = openBuffer

            testFailMessage = ''
            if expectedBuffer is not None: 
                if activeBufferAfterGoodRequest != expectedBuffer:
                    testFailMessage = requestedName + ' was opened but not active. '
                expectedBuffer.Close()  # ResetOpenFileBuffers only closes file:// buffers
            else:
                testFailMessage = testFailMessage + requestedName + " not found among " + buffernames + '. '
                
            if unexpectedBuffer is not None:
                unexpectedBuffer.Close()   
                testFailMessage = testFailMessage + requestedBadScheme + " unexpectedly found among " + buffernames + '. '
            
            snapshot = self.miniBuffer.TextBuffer.CurrentSnapshot
            text = snapshot.GetText(0, snapshot.Length)
            if text.IndexOf(requestedBadScheme) < 0:
                testFailMessage = testFailMessage + 'No notification was made for unsupported scheme ' + requestedBadScheme + '. '  
                
            assert len(testFailMessage) == 0, testFailMessage
            Common.DeactivateMiniBuffer()
            
        def Cleanup(self):
            #TestHelper.ResetBufferViews(self.hostWindow) 
            TestHelper.ResetOpenFileBuffers(self.hostWindow)
            
    return Test()    

    
@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'BehaviorSettingsTest')
def BehaviorSettingsTest():
    class Test(UnitTest):

        def Run(self):
            hostWindow = Core.Host.TopLevelWindows[0]
            view = hostWindow.ActiveView
            
            buffer1 = buffer2 = buffer3 = newView = None;

            originalSettings = {}
            for info in view.AvailableBehaviors:
                originalSettings[info.UniqueId] = info.IsEnabled

            try:
                buffer1 = Common.BufferManager.GetBuffer(System.Uri("transient://BehaviorSettingsTest1"))
                buffer2 = Common.BufferManager.GetBuffer(System.Uri("transient://BehaviorSettingsTest2"))
                buffer3 = Common.BufferManager.GetBuffer(System.Uri("transient://BehaviorSettingsTest3"))
                
                view.Buffer = buffer1
                self.SetAll(view, False)
                self.VerifyAll(view, False)

                view.Buffer = buffer2
                self.VerifyAll(view, False)
                self.SetAll(view, True)
                self.VerifyAll(view, True)

                view.Buffer = buffer1
                self.VerifyAll(view, True)
                
                from System.Windows.Controls import Orientation
                newView = TestHelper.SplitWithBuffer(view, Orientation.Vertical, buffer3)
                Common.DrainDispatcher()
                self.VerifyAll(view, True)
                
            finally:
                for info in view.AvailableBehaviors:
                    if originalSettings.has_key(info.UniqueId):
                        if originalSettings[info.UniqueId]:
                            info.Enable()
                        else:
                            info.Disable()
                TestHelper.CloseBuffers([buffer1, buffer2, buffer3])
                TestHelper.CloseViews([newView])
        
        def SetAll(self, view, value):
            for info in view.AvailableBehaviors:
                if value:
                    info.Enable()
                else:
                    info.Disable()
                    
        def VerifyAll(self, view, value):
            for info in view.AvailableBehaviors:
                if value:
                    assert info.IsEnabled, "All behaviors in this view were disabled, now one is enabled: %s" % info.UniqueId
                else:
                    assert not info.IsEnabled, "All behaviors in this view were enabled, now one is disabled: %s" % info.UniqueId

    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'EditorStateCaptureTest')
def EditorStateCaptureTest():
    class Test(UnitTest):

        def Run(self):
            from Microsoft.Intellipad.Host import WordWrapBehaviorProvider
            from Microsoft.VisualStudio.Text.Editor import ITextView, ITextSelection
            
            hostWindow = Core.Host.TopLevelWindows[0]
            startingBufferCount = Common.BufferManager.OpenBuffers.Count
            
            buffer1 = Common.BufferManager.GetBuffer(System.Uri("transient://editorStateCaptureTest1"))
            buffer2 = Common.BufferManager.GetBuffer(System.Uri("transient://editorStateCaptureTest2"))
            
            for i in range(100, 200):
                buffer1.TextBuffer.Insert(0, i.ToString() + "\r\n")
            for i in range(300, 500):
                buffer2.TextBuffer.Insert(0, i.ToString() + "\r\n")
                
            buffer2.TextBuffer.Insert(210, "This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  This is a moderately long line.  ")
            
            hostWindow.ShowBuffer(buffer1)
            Common.DrainDispatcher()
            
            view = Common.GetView(hostWindow, buffer1)
            Common.DeactivateBehavior(WordWrapBehaviorProvider.UniqueId, view)
            view.EditorPrimitives.Caret.MoveTo(200)
            Common.DrainDispatcher()
            
            view.Buffer = buffer2
            Common.DrainDispatcher()
            
            assert view.EditorPrimitives.Caret.CurrentPosition == 0, "The editor state for buffer2 should be empty."
            
            selectionSpan = Microsoft.VisualStudio.Text.Span(50, 2)
            ITextSelection.Select(view.TextEditor.TextView.Selection, selectionSpan, False)
            ITextView.DisplayTextLineContainingCharacter(view.TextEditor.TextView, 200, 0, Microsoft.VisualStudio.Text.Editor.ViewRelativePosition.Top)
            view.TextEditor.TextView.ViewportLeft = 30
            Common.DrainDispatcher()
            
            view.Buffer = buffer1
            Common.DrainDispatcher()
            assert view.EditorPrimitives.Caret.CurrentPosition == 200, "Editor state should have left caret position at 200."
            
            view.Buffer = buffer2
            Common.DrainDispatcher()
            assert view.TextEditor.TextView.Selection.SelectionSpan.Span == selectionSpan, "Selection span shoud have been restored."
            assert view.TextEditor.TextView.FirstVisibleCharacterPosition == 200, "Editor state should have scrolled the editor vertically to 200th position."
            assert view.TextEditor.TextView.ViewportLeft == 30, "Editor state should have scrolled the editor horizontally to 30px."
            
            buffer1.Close()
            buffer2.Close()
            Common.DrainDispatcher()
            assert startingBufferCount == Common.BufferManager.OpenBuffers.Count, "End buffer count not equivalent to starting buffer count"
        
    return Test()

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'ProjectFilesFilterTest')
def ProjectFilesFilterTest():
    class Test(UnitTest):
        def Run(self):
            from Microsoft.Intellipad import FileExtensionEntry
            expectedExtension = '.exp'
            expectedDescription = 'description'
            unexpectedExtension = '.any'
            unexpectedDescription = 'other'
            fee0 = FileExtensionEntry()
            fee0.FileExtension = unexpectedExtension
            fee0.ModeName = 'not msbuild'
            fee0.Description = unexpectedDescription
            fee1 = FileExtensionEntry()
            fee1.FileExtension = expectedExtension
            fee1.ModeName = 'MS Build Project Mode'
            fee1.Description = expectedDescription
            
            result = Common.GetProjectFileFilter((fee0, fee1))
            assert expectedExtension in result, 'Filter {0} did not contain expected extension {1}'.format(result, expectedExtension) 
            assert expectedDescription in result, 'Filter {0} did not contain expected description {1}'.format(result, expectedDescription) 
            assert unexpectedExtension not in result, 'Filter {0} contained unexpected text {1}'.format(result, unexpectedExtension) 
            assert unexpectedDescription not in result, 'Filter {0} contained unexpected text {1}'.format(result, unexpectedDescription) 
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'ToggleProjectViewTest')
def ToggleProjectViewTest():
    class Test(UnitTest):
        def Run(self):
            from System.IO import Path, File 

            projXml = """<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="3.5" DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <MTarget>Repository</MTarget>
    <MPackageScript>true</MPackageScript>
    <MPackageImage>true</MPackageImage>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <MTargetsPath Condition="$(MTargetsPath) == ''">$(MSBuildExtensionsPath32)\\Microsoft\\M\\v1.0</MTargetsPath>
    <ProjectName>Project11</ProjectName>
    <RootNamespace>Project11</RootNamespace>
    <AssemblyName>Project11</AssemblyName>
    <TargetFrameworkVersion>v3.5</TargetFrameworkVersion>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)' == 'Debug' ">
    <OutputPath>bin\Debug\</OutputPath>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)' == 'Release' ">
    <OutputPath>bin\Release\</OutputPath>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="Movies.m" />
  </ItemGroup>
  <Import Condition="Exists('$(MTargetsPath)')" Project="$(MTargetsPath)\Microsoft.M.targets" />
</Project>
"""
            projFile = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString('N'))
            projFile = projFile + '.mproj'
            File.WriteAllText(projFile, projXml, System.Text.Encoding.UTF8)
            hostWindow = Core.Host.TopLevelWindows[0]
            xmlBuffer = Common.BufferManager.GetBuffer(System.Uri(projFile))
            view = hostWindow.ShowBuffer(xmlBuffer)
            Common.SetActiveView(view)
            Common.DrainDispatcher()
            projectViewMode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}ProjectViewMode')
            projectMode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}ProjectMode')
            standardMode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}StandardMode');

            assert projectViewMode is not None, 'Failed to get ProjectViewMode'
            assert projectMode is not None, 'Failed to get ProjectMode'
            def CheckBufferToggle(mode, pView, count):
                assert pView.Mode == mode, 'Expected view to be in %s but was in %s (%d)' % (mode.Name, pView.Mode.Name, count) 
                if mode == projectViewMode:
                    expectedScheme = 'projectview'
                else:
                    expectedScheme = 'file'
                assert pView.Buffer.Uri.Scheme == expectedScheme, 'Expected scheme %s but was %s (%d)' % (expectedScheme, pView.Buffer.Uri.Scheme, count)
                
            try:
                CheckBufferToggle(projectMode, view, 1)
                TestHelper.Execute('{Microsoft.Intellipad}ToggleProjectView', None, view)
                Common.DrainDispatcher()
                CheckBufferToggle(projectViewMode, view, 2)
                projectViewBuffer = view.Buffer
                assert projectViewBuffer != xmlBuffer, 'Should have 2 different buffers for the project'
                
                view.Mode = standardMode
                view.Buffer = xmlBuffer
                Common.DrainDispatcher()
                TestHelper.Execute('{Microsoft.Intellipad}ToggleProjectView', None, view)
                Common.DrainDispatcher()
                CheckBufferToggle(projectViewMode, view, 3)

                view.Buffer = xmlBuffer
                view.Mode = standardMode
                Common.DrainDispatcher()
                view.Buffer = projectViewBuffer
                # standard mode was mapped as preferred, so now have to set the mode to make cmd available
                view.Mode = projectViewMode
                Common.DrainDispatcher()
                TestHelper.Execute('{Microsoft.Intellipad}ToggleProjectView', None, view)
                Common.DrainDispatcher()
                CheckBufferToggle(projectMode, view, 4)

            finally:
                xmlBuffer.Close()
                File.Delete(projFile)
            
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'AddProjectItemTests')
def AddProjectItemTests():
    class Test(UnitTest):
        def Run(self):
            from System.IO import File, Path
            from System.Threading import Thread
                        
            mSource = """module foo
{
    bar : 
    {
        Id : Integer64 = AutoNumber();
        Name : Text;
    }* where identity Id;   
}
"""
            mFileName = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString('N'))
            mFileName = mFileName + '.m'
            File.WriteAllText(mFileName, mSource, System.Text.Encoding.UTF8)
            hostWindow = Core.Host.TopLevelWindows[0]
            projectFile = projectBuffer = mBuffer = mFile2 = mFile3 = None

            try:
                mBuffer = Common.BufferManager.GetBuffer(System.Uri(mFileName))
                mView = hostWindow.ShowBuffer(mBuffer)
                Common.SetActiveView(mView)
                Common.DrainDispatcher()

                TestHelper.Execute('{Microsoft.M}CreateNewProjectFromBuffer', None, mView)
                Common.DrainDispatcher()
                projectView = None
                projectViewMode =  Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}ProjectViewMode')
                for view in hostWindow.BufferViews:
                    if view.Mode == projectViewMode:
                        projectView = view
                        break
                assert projectView is not None, 'Could not get project view'
                projectBuffer = projectView.Buffer
                projectFile = System.Uri(projectBuffer.Uri.Query.Split('=')[1])
                projectContext = Core.ProjectManager.GetProject(projectFile)
                assert projectContext is not None, 'Failed to get projectContext for ' + projectFile.ToString()
                projectFile = projectFile.LocalPath
                assert hostWindow.ActiveView == projectView, 'Create new project did not activate project view'
                
                projectString = Path.GetFileName(projectFile)
                mFileString = Path.GetFileName(mFileName)
                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), mFileName)
                TestHelper.Execute('{Microsoft.Intellipad}AddProjectItem', None, projectView)
                Common.DrainDispatcher()
                notificationBuffer = Core.BufferManager.GetBuffer(System.Uri('transient://notification'))
                notificationLength = notificationBuffer.TextBuffer.CurrentSnapshot.Length
                assert notificationBuffer.TextBuffer.CurrentSnapshot.GetText(0, notificationLength).Contains(mFileString + ' already exists in the project ' + projectString), 'Expected notification when trying to add file already in project.' 

                mFile2 = mFileName + ' 2.m'
                itemUri = System.Uri('file:///' + mFile2)
                assert not projectContext.ContainsItem(itemUri)
                File.Copy(mFileName, mFile2, True)                                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), mFile2)
                TestHelper.Execute('{Microsoft.Intellipad}AddProjectItem', None, projectView)
                Common.DrainDispatcher()
                assert projectContext.ContainsItem(itemUri)
                CheckItemCondition(projectContext, Path.GetFileName(mFile2), 'Compile')

                TestHelper.Execute('{Microsoft.Intellipad}AddProjectReference', None, projectView)
                Common.DrainDispatcher()
                notificationBuffer = Core.BufferManager.GetBuffer(System.Uri('transient://notification'))
                notificationLength2 = notificationBuffer.TextBuffer.CurrentSnapshot.Length
                assert notificationLength2 > notificationLength, 'no notice made when trying to add existing item as reference'
                mFileString = Path.GetFileName(mFile2)
                assert notificationBuffer.TextBuffer.CurrentSnapshot.GetText(notificationLength, notificationLength2 - notificationLength).Contains(mFileString + ' already exists in the project ' + projectString), 'Expected notification when trying to add reference already in project.' 

                mFile3 = mFileName + ' 3.m'
                itemUri = System.Uri('file:///' + mFile3)
                assert not projectContext.ContainsItem(itemUri)
                File.Copy(mFileName, mFile3, True)                                
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), mFile3)
                TestHelper.Execute('{Microsoft.Intellipad}AddProjectReference', None, projectView)
                Common.DrainDispatcher()
                assert projectContext.ContainsItem(itemUri)
                CheckItemCondition(projectContext, Path.GetFileName(mFile3), 'Reference')

            finally:
                Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetOneFileOverride'), None)
                if mBuffer is not None:
                    mBuffer.Close()
                if projectBuffer is not None:
                    projectBuffer.Close()
                File.Delete(mFileName)
                if mFile2 is not None:
                    File.Delete(mFile2)
                if mFile3 is not None:
                    File.Delete(mFile3)
                if projectFile is not None:
                    File.Delete(projectFile)
                
    return Test()


def CheckItemCondition(projectContext, fileName, condition):
    items = projectContext.MSBuildProject.EvaluatedItems.ToArray()
    foundItem = False
    for item in items:
        if item.Name == condition and item.FinalItemSpec == fileName:
            foundItem = True
            break
    assert foundItem, fileName + ' was not added with condition ' + condition
        

@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'ShowReferencesListTest')
def ShowReferencesListTest():
    class Test(UnitTest):
        def Run(self):
            from System.Windows.Controls import Orientation
            view = buffer1 = symbolsBuffer = None
            try:
                symbolsUri = System.Uri('transient://showsymbols')
                (result, symbolsBuffer) = Common.BufferManager.TryGetBuffer(symbolsUri)
                if result:
                    symbolsBuffer.Close()

                hostWindow = Core.Host.TopLevelWindows[0]
                buffer1 = Common.BufferManager.GetBuffer(System.Uri('file://'))
                mExportText = """
module Keyword.ExportingModule
{
    type ExportType
    {
        Id : Integer32; 
        x : Text;
    } where identity Id;

}
"""
                symbolPosition = 43
                buffer1.TextBuffer.Insert(0, mExportText)
                view = hostWindow.ShowInRoot(buffer1, Orientation.Horizontal, 20.0)
                Common.DrainDispatcher()               
                assert hostWindow.ActiveView == view, 'Expected GetView to show in active view'
                view.EditorPrimitives.Caret.MoveTo(symbolPosition);
                
                Common.DrainDispatcher()
                TestHelper.Execute('{Microsoft.Intellipad}ShowReferencesList', None, view)
                Common.DrainDispatcher()
                
                (result, symbolsBuffer) = Common.BufferManager.TryGetBuffer(symbolsUri)
                assert not result, 'Symbols list should not be shown when no symbols (no lang service item)'

                view.Mode = MMode
                Common.DrainDispatcher()
                def ReadyForTest():
                    return view.LanguageServiceItem.ReadyForTestRun
                    
                success = TestHelper.DispatcherCheckPredicatePolling(ReadyForTest, None, 30)
                assert success, 'LanguageServiceItem is not ready after 30 seconds'
                Common.DrainDispatcher()
                symbol = view.LanguageServiceItem.GetSymbol(view.EditorPrimitives.Caret.AdvancedTextPoint)
                assert symbol is not None, 'Should have symbol after languageServiceItem ready for test'

                Common.DrainDispatcher()
                TestHelper.Execute('{Microsoft.Intellipad}ShowReferencesList', None, view)
                Common.DrainDispatcher()
                (result, symbolsBuffer) = Common.BufferManager.TryGetBuffer(symbolsUri)
                assert not result, 'Symbols list should not be shown when one symbol found'
                TestHelper.AssertSelectionLocationByPosition(view, symbolPosition, 10)
                
                noSymbolPosition = symbolPosition - 1
                view.EditorPrimitives.Caret.MoveTo(noSymbolPosition);
                Common.DrainDispatcher()
                TestHelper.Execute('{Microsoft.Intellipad}ShowReferencesList', None, view)
                Common.DrainDispatcher()
                (result, symbolsBuffer) = Common.BufferManager.TryGetBuffer(symbolsUri)
                assert not result, 'Symbols list should not be shown when one symbol found'
                assert view.EditorPrimitives.Caret.CurrentPosition == noSymbolPosition, 'Caret should not move when no result found.'
                                
                symbolPosition = 69
                view.EditorPrimitives.Caret.MoveTo(symbolPosition);
                Common.DrainDispatcher()
                TestHelper.Execute('{Microsoft.Intellipad}ShowReferencesList', None, view)
                Common.DrainDispatcher()
                (result, symbolsBuffer) = Common.BufferManager.TryGetBuffer(symbolsUri)
                assert result, 'Symbols list should have been shown when 2+ references found'

            finally:
                if buffer1 is not None:
                    buffer1.Close()
                if symbolsBuffer is not None:
                    symbolsBuffer.Close()
                TestHelper.CloseViews([view])
    return Test()


@Metadata.Export('{Microsoft.Intellipad}UnitTest')
@Metadata.ExportMetadata('{Microsoft.Intellipad.UnitTest}Name', 'MruTest')
def MruTest():
    class Test(UnitTest):
        def __init__(self):
            self.testView = None
        def Setup(self):
            self.hostWindow = Core.Host.TopLevelWindows[0]
            TestHelper.ResetBufferViews(self.hostWindow)
            TestHelper.ResetOpenFileBuffers(self.hostWindow)
            
        def Run(self):
            from System.Threading import Thread
            
            file = System.IO.Path.GetTempFileName()
            System.IO.File.WriteAllText(file, "Temp contents")
            filesToOpen = [file]
            
            Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), filesToOpen)
            TestHelper.Execute('{Microsoft.Intellipad}Open', None, self.hostWindow.ActiveView)
            Common.DrainDispatcher()
            
            assert Core.Settings.MostRecentlyUsed.Contains(System.Uri(file)), 'Expected to find the newly opened file in the MRU list.'
            
            filesList = System.Collections.Generic.List[System.String]()
            for i in range(1, 10):
                file = System.IO.Path.GetTempFileName()
                System.IO.File.WriteAllText(file, "Temp contents")
                filesList.Add(file)
                
            Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), filesList.ToArray())
            TestHelper.Execute('{Microsoft.Intellipad}Open', None, self.hostWindow.ActiveView)
            Common.DrainDispatcher()
            
            for file in filesList:
                assert Core.Settings.MostRecentlyUsed.Contains(System.Uri(file)), 'Expected to find the newly opened file in the MRU list.'

        def Cleanup(self):
            from System.Threading import Thread
            
            Thread.SetData(Thread.GetNamedDataSlot('{Microsoft.Intellipad.FileDialogHelper}GetFilesOverride'), None)
            TestHelper.ResetBufferViews(self.hostWindow)
            TestHelper.ResetOpenFileBuffers(self.hostWindow)
            
    return Test()