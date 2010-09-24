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
#include "BuilderPlugin.h"
#include "ui/UIBuilderSettings.h"

BuilderPlugin.BuilderPlugin()
        : BasePlugin(), CLIToolPlugin( self )


def buildCommand(self):
    # get settings object
    settings = MonkeyCore.settings()
    pCommand cmd

    cmd.setText( settings.value( settingsKey( "BuildCommand/Text" ) ).toString() )
    cmd.setCommand( settings.value( settingsKey( "BuildCommand/Command" ) ).toString() )
    cmd.setArguments( settings.value( settingsKey( "BuildCommand/Arguments" ) ).toString() )
    cmd.setWorkingDirectory( settings.value( settingsKey( "BuildCommand/WorkingDirectory" ) ).toString() )
    cmd.setParsers( settings.value( settingsKey( "BuildCommand/Parsers" ) ).toStringList() )
    cmd.setTryAllParsers( settings.value( settingsKey( "BuildCommand/TryAll" ), False ).toBool() )
    cmd.setSkipOnError( settings.value( settingsKey( "BuildCommand/SkipOnError" ), False ).toBool() )

    # if no user commands get global ones
    if  not cmd.isValid() :
        cmd = defaultBuildCommand()


    return cmd


def setBuildCommand(self, cmd ):
    settings = MonkeyCore.settings()

    settings.setValue( settingsKey( "BuildCommand/Text" ), cmd.text() )
    settings.setValue( settingsKey( "BuildCommand/Command" ), cmd.command() )
    settings.setValue( settingsKey( "BuildCommand/Arguments" ), cmd.arguments() )
    settings.setValue( settingsKey( "BuildCommand/WorkingDirectory" ), cmd.workingDirectory() )
    settings.setValue( settingsKey( "BuildCommand/Parsers" ), cmd.parsers() )
    settings.setValue( settingsKey( "BuildCommand/TryAll" ), cmd.tryAllParsers() )
    settings.setValue( settingsKey( "BuildCommand/SkipOnError" ), cmd.skipOnError() )


def builderSettingsWidget(self):
    return UIBuilderSettings( self, QApplication.activeWindow() )

