#include "XUPProjectItemHelper.h"
#include "XUPProjectItem.h"
#include "pMonkeyStudio.h"

#include <QDir>
#include <QDebug>

def projectCommandsScope(self, project, create ):
    settingsScope = project.projectSettingsScope( create )
    
    if  not settingsScope :
        return 0

    
    for child in settingsScope.childrenList():
        if  child.type() == XUPItem.Scope and child.attribute( "name" ) == CommandsScopeName :
            return child


    
    if  not create :
        return 0

    
    commandsScope = settingsScope.addChild( XUPItem.Scope )
    commandsScope.setAttribute( "name", CommandsScopeName )
    commandsScope.setAttribute( "nested", "False" )
    return commandsScope


def addCommandProperty(self, variableItem, value ):
    valueItem = variableItem.addChild( XUPItem.Value )
    valueItem.setAttribute( "content", value )


def setProjectCommands(self, project, commands ):
    emptyCommands = True
    
    foreach (  BasePlugin.Type& type, commands.keys() )
        if  commands[ type ].isEmpty() :
            continue

        
        emptyCommands = False
        break

    
    commandsScope = projectCommandsScope( project, emptyCommands )
    
    if  not commandsScope :
        return

    
    # delete scope if no commands
    if  emptyCommands :
        commandsScope.parent().removeChild( commandsScope )
        return

    
    # clear existing commands
    for child in commandsScope.childrenList():
        commandsScope.removeChild( child )

    
    # create ones
    foreach (  BasePlugin.Type& type, commands.keys() )
        foreach (  pCommand& command, commands[ type ] )
            variable = commandsScope.addChild( XUPItem.Variable )
            variable.setAttribute( "name", CommandScopeName )
            variable.setAttribute( "operator", "=" )
            variable.setAttribute( "multiline", "True" )
            
            addCommandProperty( variable, QString.number( type ) )
            addCommandProperty( variable, command.text() )
            addCommandProperty( variable, command.command() )
            addCommandProperty( variable, command.arguments() )
            addCommandProperty( variable, command.workingDirectory() )
            addCommandProperty( variable, command.parsers().join( ";" ) )
            addCommandProperty( variable, command.skipOnError() ? "1" : "0" )
            addCommandProperty( variable, command.tryAllParsers() ? "1" : "0" )




def projectCommands(self, project ):
    TypeCommandListMap commands
    commandsScope = projectCommandsScope( project, False )
    
    if  commandsScope :
        for commandVariable in commandsScope.childrenList():
            QVariantList values
            
            for commandValue in commandVariable.childrenList():
                values << commandValue.attribute( "content" )

            
            if  values.count() != 8 :
                qWarning() << "Skip reading incomplete command"
                Q_ASSERT( 0 )
                continue

            
            pCommand command
            
            command.setText( values.at( 1 ).toString() )
            command.setCommand( values.at( 2 ).toString() )
            command.setArguments( values.at( 3 ).toString() )
            command.setWorkingDirectory( values.at( 4 ).toString() )
            command.setParsers( values.at( 5 ).toString().split( ";", QString.SkipEmptyParts ) )
            command.setSkipOnError( values.at( 6 ).toBool() )
            command.setTryAllParsers( values.at( 7 ).toBool() )
            
            commands[ (BasePlugin.Type)values.at( 0 ).toInt() ] << command


    
    return commands


def installProjectCommands(self, project ):
     commands = projectCommands( project )
    
    foreach (  BasePlugin.Type& type, commands.keys() )
        foreach ( pCommand command, commands[ type ] )
            switch ( type )
                case BasePlugin.iBuilder:
                    project.addCommand( command, "mBuilder" )
                    break
                case BasePlugin.iDebugger:
                    project.addCommand( command, "mDebugger" )
                    break
                case BasePlugin.iInterpreter:
                    project.addCommand( command, "mInterpreter" )
                    break
                default:
                    Q_ASSERT( 0 )
                    break





def projectDynamicFolderSettingsItem(self, project, create ):
    for child in project.childrenList():
        if  child.type() == XUPItem.Variable and child.attribute( "name" ) == DynamicFolderSettingsName :
            return child


    
    if  not create :
        return 0

    
    dynamicFolderSettingsItem = project.addChild( XUPItem.Variable )
    dynamicFolderSettingsItem.setAttribute( "name", DynamicFolderSettingsName )
    dynamicFolderSettingsItem.setAttribute( "operator", "=" )
    dynamicFolderSettingsItem.setAttribute( "multiline", "True" )
    return dynamicFolderSettingsItem


def addDynamicFolderSettingsProperty(self, dynamicFolderSettingsItem, value ):
    valueItem = dynamicFolderSettingsItem.addChild( XUPItem.Value )
    valueItem.setAttribute( "content", value )


def projectDynamicFolderSettings(self, project ):
    XUPDynamicFolderSettings folder
    dynamicFolderSettingsItem = projectDynamicFolderSettingsItem( project, False )
    
    if  dynamicFolderSettingsItem :
        QVariantList values
        
        for valueItem in dynamicFolderSettingsItem.childrenList():
            values << valueItem.attribute( "content" )

        
        if  values.count() != 3 :
            qWarning() << "Skip reading incomplete dynamic folder settings"
            Q_ASSERT( 0 )
            return folder

        
        folder.Active = values.at( 0 ).toBool()
        folder.AbsolutePath = project.filePath( values.at( 1 ).toString() )
        folder.FilesPatterns = values.at( 2 ).toString().split( ";", QString.SkipEmptyParts )
        
        if  folder.AbsolutePath.isEmpty() and folder.Active :
            folder.AbsolutePath = project.path()


    
    return folder


def setProjectDynamicFolderSettings(self, project, folder ):
    dynamicFolderSettingsItem = projectDynamicFolderSettingsItem( project, folder.isNull() )
    
    if  dynamicFolderSettingsItem :
        # clear existing values
        for child in dynamicFolderSettingsItem.childrenList():
            dynamicFolderSettingsItem.removeChild( child )

        
        addDynamicFolderSettingsProperty( dynamicFolderSettingsItem, folder.Active ? "1" : "0" )
        addDynamicFolderSettingsProperty( dynamicFolderSettingsItem, folder.AbsolutePath )
        addDynamicFolderSettingsProperty( dynamicFolderSettingsItem, folder.FilesPatterns.join( ";" ) )



def projectDynamicFolderItem(self, project, create ):
    for child in project.childrenList():
        if  child.type() == XUPItem.DynamicFolder and child.attribute( "name" ) == DynamicFolderName :
            return child


    
    if  not create :
        return 0

    
    dynamicFolderItem = project.addChild( XUPItem.DynamicFolder )
    dynamicFolderItem.setAttribute( "name", DynamicFolderName )
    dynamicFolderItem.setAttribute( "operator", "=" )
    dynamicFolderItem.setAttribute( "multiline", "True" )
    return dynamicFolderItem


def addDynamicFolderProperty(self, dynamicFolderItem, value ):
    valueItem = dynamicFolderItem.addChild( XUPItem.File )
    valueItem.setAttribute( "content", value )


def updateDynamicFolder(self, project, path ):
    dynamicFolderItem = projectDynamicFolderItem( project, True )
     folder = projectDynamicFolderSettings( project )
     samePath = QDir.cleanPath( path ) == QDir.cleanPath( folder.AbsolutePath )
    
    if  not dynamicFolderItem or not samePath :
        return

    
    for child in dynamicFolderItem.childrenList():
        dynamicFolderItem.removeChild( child )

    
    QDir dir( path )
    files = pMonkeyStudio.getFiles( dir, folder.FilesPatterns, False )
    
    if  not folder.Active or files.isEmpty() :
        project.removeChild( dynamicFolderItem )
        return

    
    for file in files:
        addDynamicFolderProperty( dynamicFolderItem, file.absoluteFilePath() )



def stripDynamicFolderFiles(self, document ):
    doc = document.cloneNode().toDocument()
     nodesToRemove = doc.elementsByTagName( "dynamicfolder" )
    
    for ( i = 0; i < nodesToRemove.count(); i++ )
         node = nodesToRemove.at( i )
        node.parentNode().removeChild( node )

    
    return doc

