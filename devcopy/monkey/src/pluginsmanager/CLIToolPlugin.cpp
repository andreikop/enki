'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, KOPATS aka hlamer <hlamer@tut.by>
** Project   : Monkey Studio IDE
** FileName  : BuilderPlugin.cpp
** Date      : 2009-12-09T00:37:00
** License   : GPL
** Comment   : 
** Home Page : http:#www.monkeystudio.org
**
**
***************************************************************************'''
#include "CLIToolPlugin.h"
#include "ui/UICLIToolSettings.h"

CLIToolPlugin.CLIToolPlugin( BasePlugin* plugin )
    Q_ASSERT( plugin )
    mPlugin = plugin


CLIToolPlugin.~CLIToolPlugin()


def userCommands(self):
    # commands list
    pCommandList cmds
    # get settings object
    settings = MonkeyCore.settings()
    
    # read user commands for self plugin
    size = settings.beginReadArray( mPlugin.settingsKey( "Commands" ) )
    for ( i = 0; i < size; i++ )
        settings.setArrayIndex( i )
        pCommand cmd
        
        cmd.setText( settings.value( "Text" ).toString() )
        cmd.setCommand( settings.value( "Command" ).toString() )
        cmd.setArguments( settings.value( "Arguments" ).toString() )
        cmd.setWorkingDirectory( settings.value( "WorkingDirectory" ).toString() )
        cmd.setParsers( settings.value( "Parsers" ).toStringList() )
        cmd.setTryAllParsers( settings.value( "TryAll" ).toBool() )
        cmd.setSkipOnError( settings.value( "SkipOnError" ).toBool() )
        
        cmds << cmd

    settings.endArray()
    
    # if no user commands get global ones
    if  cmds.isEmpty() :
        cmds << defaultCommands()

    
    # return list
    return cmds


def setUserCommands(self, cmds ):
    # get settings object
    settings = MonkeyCore.settings()
    
    # remove old key
    settings.remove( mPlugin.settingsKey( "Commands" ) )
    
    # write user commands for self plugin
    settings.beginWriteArray( mPlugin.settingsKey( "Commands" ) )
    for ( i = 0; i < cmds.count(); i++ )
        settings.setArrayIndex( i )
         cmd = cmds[i]
        
        settings.setValue( "Text", cmd.text() )
        settings.setValue( "Command", cmd.command() )
        settings.setValue( "Arguments", cmd.arguments() )
        settings.setValue( "WorkingDirectory", cmd.workingDirectory() )
        settings.setValue( "Parsers", cmd.parsers() )
        settings.setValue( "TryAll", cmd.tryAllParsers() )
        settings.setValue( "SkipOnError", cmd.skipOnError() )

    settings.endArray()


def cliToolSettingsWidget(self):
    return UICLIToolSettings( mPlugin, defaultCommands(), userCommands(), QApplication.activeWindow() )


def availableParsers(self):
    return QStringList()


def getParser(self, name ):
    Q_UNUSED( name )
    return 0

