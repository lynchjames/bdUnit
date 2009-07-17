#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import clr
import System
import Microsoft

import FindHelper

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def Initialize(value):
    global Core
    Core = value
    FindHelper.Initialize(Core)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Replace', 'Ctrl+H')
def ReplaceCommand(target, sender, args): FindHelper.ReplaceCommand(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ReplaceNext', 'F4')
def ReplaceNext(target, sender, args): FindHelper.ReplaceNext(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ReplacePrevious', 'Shift+F4')
def ReplacePrevious(target, sender, args): FindHelper.ReplacePrevious(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Find', 'Ctrl+F')
def FindCommand(target, sender, args): FindHelper.FindCommand(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FindNext', 'F3')
def FindNext(target, sender, args): FindHelper.FindNext(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FindPrevious', 'Shift+F3')
def FindPrevious(target, sender, args): FindHelper.FindPrevious(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FindSelectedNext', 'Ctrl+F3')
def FindSelectedNext(target, sender, args): FindHelper.FindSelectedNext(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}FindSelectedPrevious', 'Ctrl+Shift+F3')
def FindSelectedPrevious(target, sender, args): FindHelper.FindSelectedPrevious(sender, args)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}Goto', 'Ctrl+G')
def GotoCommand(target, sender, args): FindHelper.GotoCommand(sender, args)
