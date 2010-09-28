/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, Andrei KOPATS aka hlamer <hlamer@tut.by>
** Project   : Monkey Studio IDE
** FileName  : InterpreterPlugin.cpp
** Date      : 2009-12-09T00:37:00
** License   : GPL
** Comment   : 
** Home Page : http://www.monkeystudio.org
**
**
****************************************************************************/
#include "InterpreterPlugin.h"
#include "ui/UIInterpreterSettings.h"

InterpreterPlugin::InterpreterPlugin()
    : BasePlugin(), CLIToolPlugin( this )
{
}

pCommand InterpreterPlugin::interpretCommand() const
{
    // get settings object
    pSettings* settings = MonkeyCore::settings();
    pCommand cmd;
    
    cmd.setText( settings->value( settingsKey( "InterpretCommand/Text" ) ).toString() );
    cmd.setCommand( settings->value( settingsKey( "InterpretCommand/Command" ) ).toString() );
    cmd.setArguments( settings->value( settingsKey( "InterpretCommand/Arguments" ) ).toString() );
    cmd.setWorkingDirectory( settings->value( settingsKey( "InterpretCommand/WorkingDirectory" ) ).toString() );
    cmd.setParsers( settings->value( settingsKey( "InterpretCommand/Parsers" ) ).toStringList() );
    cmd.setTryAllParsers( settings->value( settingsKey( "InterpretCommand/TryAll" ), false ).toBool() );
    cmd.setSkipOnError( settings->value( settingsKey( "InterpretCommand/SkipOnError" ), false ).toBool() );
    
    // if no user commands get global ones
    if ( !cmd.isValid() )
    {
        cmd = defaultInterpretCommand();
    }
    
    return cmd;
}

void InterpreterPlugin::setInterpretCommand( const pCommand& cmd )
{
    pSettings* settings = MonkeyCore::settings();
    
    settings->setValue( settingsKey( "InterpretCommand/Text" ), cmd.text() );
    settings->setValue( settingsKey( "InterpretCommand/Command" ), cmd.command() );
    settings->setValue( settingsKey( "InterpretCommand/Arguments" ), cmd.arguments() );
    settings->setValue( settingsKey( "InterpretCommand/WorkingDirectory" ), cmd.workingDirectory() );
    settings->setValue( settingsKey( "InterpretCommand/Parsers" ), cmd.parsers() );
    settings->setValue( settingsKey( "InterpretCommand/TryAll" ), cmd.tryAllParsers() );
    settings->setValue( settingsKey( "InterpretCommand/SkipOnError" ), cmd.skipOnError() );
}

QWidget* InterpreterPlugin::interpreterSettingsWidget()
{
    return new UIInterpreterSettings( this, QApplication::activeWindow() );
}
