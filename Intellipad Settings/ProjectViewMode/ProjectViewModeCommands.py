#----------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#----------------------------------------------------------------

import sys
import System
import Microsoft
import Common

@Metadata.ImportSingleValue('{Microsoft.Intellipad}BufferManager')
def InitializeBufferManager(value):
    global BufferManager
    BufferManager = value

@Metadata.ImportSingleValue('{Microsoft.Intellipad}Core')
def InitializeCore(value):
    global Core, Host
    Core = value
    Host = Core.Host

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectMode')
def ImportProjectMode(value):
    global ProjectMode
    ProjectMode = value

@Metadata.ImportSingleValue('{Microsoft.Intellipad}ProjectViewMode')
def ImportProjectViewMode(value):
    global ProjectViewMode
    ProjectViewMode = value

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}AddProjectItem', None)
def AddProjectItem(target, sender, args):
    project = Common.GetProject(sender.Buffer)
    if project is None:
        Host.Notify('Unable to get Project Context for ' + sender.Title) 
        return
    
    projectItem = GetProjectFile(project, 'M Files (*.m)|*.m')
    if projectItem is not None:
        project.AddCompileItem(projectItem)

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}AddProjectReference', None)
def AddProjectReference(target, sender, args):
    project = Common.GetProject(sender.Buffer)
    if project is None:
        Host.Notify('Unable to get Project Context for ' + sender.Title) 
        return

    projectItem = GetProjectFile(project, 'MX Files (*.mx)|*.mx')
    if projectItem is not None:
        project.AddReferenceItem(projectItem)
        
def GetProjectFile(project, filter):
    ofh = Common.OpenFileHelper(filter)
    fileName = ofh.GetFile()    
    if fileName is not None:
        projectItem = System.Uri(fileName)
        if project.ContainsItem(projectItem):
            Host.Notify(fileName + ' already exists in the project ' + project.ProjectBuffer.Title)
        else:
            return projectItem
    return None

@Metadata.CommandExecuted('{Microsoft.Intellipad}BufferView', '{Microsoft.Intellipad}ToggleProjectView', None)
def ToggleProjectView(target, sender, args):
    projectMode = None
    if isinstance(sender.Buffer, Microsoft.Intellipad.Host.ProjectViewBuffer):
        sender.Buffer = sender.Buffer.Source
        projectMode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}ProjectMode')
    else:
        projectViewUri = System.Uri(System.String.Format('projectview://project?source={0}', sender.Buffer.Uri))
        sender.Buffer = BufferManager.GetBuffer(projectViewUri)
        projectMode = Core.ComponentDomain.GetExportedObject[System.Object]('{Microsoft.Intellipad}ProjectViewMode')
    if projectMode is not None:
        sender.Mode = projectMode
