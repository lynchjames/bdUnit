#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import sys
import System
import Microsoft
import Common

CannotDisplayMxGrammar = "Cannot load the grammar as it was published from a compiled file."
CannotOpenGrammarFile = "Cannot open grammar file {0}."
CannotFindGrammar = "Could not locate the grammar for {0}."

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def InitializeCore(value):
    global Core, Host
    Core = value
    Host = Core.Host

@Metadata.ImportSingleValue('{Microsoft.Intellipad}MGrammarMode')
def InitializeMGrammarMode(value):
    global GrammarMode
    GrammarMode = value

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}SwitchToOutputMode', None)
def SwitchToOutputMode(target, sender, args):
    bufferView = sender
    inputMode = bufferView.Mode

    # We only work on bufferviews in a DslMode
    expectedType = System.Type.GetType("Microsoft.Intellipad.LanguageServices.DslMode, Microsoft.Intellipad.Core")
    if expectedType is None:
        return

    outputMode = Microsoft.Intellipad.LanguageServices.DslOutputMode.FindPublishedMode(inputMode.Core, inputMode.Uri, inputMode.LanguageName)
    if outputMode is None:
        if inputMode.Core.Host is not None:
            inputMode.Core.Host.Notify(System.String.Format(System.Globalization.CultureInfo.CurrentCulture, CannotFindGrammar, bufferView.Buffer.Uri.AbsolutePath))
        return

    bufferView.Mode = outputMode


@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ShowGrammarFromInput', None)
def ShowGrammarFromInput(target, sender, args):
    bufferView = sender
    inputMode = bufferView.Mode

    # We only work on bufferviews in a DslMode
    expectedType = System.Type.GetType("Microsoft.Intellipad.LanguageServices.DslMode, Microsoft.Intellipad.Core")
    if expectedType is None:
        return

    # find/load the grammar buffer that originally generated this mode
    if IsMxFile(inputMode.Uri):
        if inputMode.Core.Host is not None:
            inputMode.Core.Host.Notify(CannotDisplayMxGrammar)
        return

    grammarBuffer = inputMode.Core.BufferManager.GetBuffer(inputMode.Uri)
    if grammarBuffer is None:
        if inputMode.Core.Host is not None:
            inputMode.Core.Host.Notify(System.String.Format(System.Globalization.CultureInfo.CurrentCulture, CannotOpenGrammarFile, inputMode.Uri.AbsolutePath))
            return

    # We see if we can find and activate an existing view with the grammar
    if Host is not None:
        window = Host.TopLevelWindows[0]
        if window is not None:
            view = Common.GetView(window, grammarBuffer)
            if view is not None:
                view.Mode = GrammarMode
                Common.SetActiveView(view)
                return

    # if we can't find an existing view with the grammar buffer, we reuse the caller
    # We force the BufferView to GrammarMode as it may not choose it automatically
    # (e.g. if the grammar is in an unsaved buffer with no file extension)
    bufferView.Buffer = grammarBuffer
    bufferView.Mode = GrammarMode

def IsMxFile(uri):
    filename = uri.Segments[uri.Segments.Length - 1] # last segment
    return (filename.Length > 2) and (filename.Substring(filename.Length - 2).ToUpperInvariant() == "MX")
