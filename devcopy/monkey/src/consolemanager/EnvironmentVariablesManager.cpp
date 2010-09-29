#include "EnvironmentVariablesManager.h"
#include "shellmanager/MkSShellInterpreter.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <QCoreApplication>
#include <QFile>
#include <QDebug>

EnvironmentVariablesManager.EnvironmentVariablesManager()
    : pEnvironmentVariablesManager()
    initializeInterpreterCommands()


def writeVariables(self, variables ):
    # write content in utf8
     fn = MonkeyCore.settings().homePath( Settings.SP_SCRIPTS ).append( "/environment-variables.mks" )
    QFile file( fn )
    QStringList buffer
    
    if  not file.open( QIODevice.WriteOnly ) :        qWarning() << QString( "Can't open file for generating environment variables script: %1" ).arg( file.errorString() ).toLocal8Bit().constData()
        return False

    
    file.resize( 0 )
    
    buffer << "# Monkey Studio IDE Environment Variables"
    buffer << "# reset variables"
    buffer << "environment clear"
    buffer << "# Available commands:"
    buffer << "# environment set\tname\tvalue"
    buffer << "# environment unset\tname"
    buffer << "# environment clear"
    buffer << "# environment enable\tname\tTrue/False"
    buffer << "# introduce ones per name/state"
    
    for name in variables.keys():        buffer << QString( "# %1" ).arg( name )
        buffer << QString( "environment set \"%1\" \"%2\"" )
            .arg( name )
            .arg( variables[ name ].value )
        buffer << QString( "environment enable \"%1\" \"%2\"" )
            .arg( name )
            .arg( QVariant( variables[ name ].enabled ).toString() )

    
    if  file.write( buffer.join( "\n" ).toUtf8() ) == -1 :        qWarning() << QString( "Can't write generated environment variables script: %1" ).arg( file.errorString() ).toLocal8Bit().constData()

    
    file.close()
    
    return True


def readVariables(self, variables ):
    Q_UNUSED( variables )
    return True


def initializeInterpreterCommands(self):
    # register command
    help = MkSShellInterpreter.tr(
        "This command manage the environment variables, usage:\n"
        "\tenvironment set [name] [value]\n"
        "\tenvironment unset [name]\n"
        "\tenvironment clear\n"
        "\tenvironment enable [name] [True/False]\n"
        "\tenvironment list"
    )
    
    MonkeyCore.interpreter().addCommandImplementation( "environment", EnvironmentVariablesManager.commandInterpreter, help, self )


def commandInterpreter(self, command, _arguments, result, interpreter, data ):
    Q_UNUSED( command )
    Q_UNUSED( interpreter )
    manager = static_cast<EnvironmentVariablesManager*>( data )
    arguments = _arguments
     allowedOperations = QStringList( "set" ) << "unset" << "clear" << "enable" << "list"
    
    if  result :        *result = MkSShellInterpreter.NoError

    
    if  arguments.isEmpty() :        if  result :            *result = MkSShellInterpreter.InvalidCommand

        
        return MkSShellInterpreter.tr( "Operation not defined. Available operations are: %1." ).arg( allowedOperations.join( ", " ) )

    
     operation = arguments.takeFirst()
    
    if  not allowedOperations.contains( operation ) :        if  result :            *result = MkSShellInterpreter.InvalidCommand

        
        return MkSShellInterpreter.tr( "Unknown operation: '%1'." ).arg( operation )

    
    if  operation == "set" :        if  arguments.count() != 2 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'set' operation take 2 arguments, %1 given." ).arg( arguments.count() )

        
         name = arguments.at( 0 )
         value = arguments.at( 1 )
        
        manager.setCommand( name, value )

    
    if  operation == "unset" :        if  arguments.count() != 1 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'unset' operation take 1 arguments, %1 given." ).arg( arguments.count() )

        
         name = arguments.at( 0 )
        
        manager.unsetCommand( name )

    
    if  operation == "clear" :        if  arguments.count() != 0 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'clear' operation take no arguments, %1 given." ).arg( arguments.count() )

        
        manager.clearCommand()

    
    if  operation == "enable" :        if  arguments.count() != 2 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'enable' operation take 2 arguments, %1 given." ).arg( arguments.count() )

        
         name = arguments.at( 0 )
         enabled = QVariant( arguments.at( 1 ) ).toBool()
        
        manager.enableCommand( name, enabled )

    
    if  operation == "list" :        if  arguments.count() != 0 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'list' operation take no arguments, %1 given." ).arg( arguments.count() )

        
        QStringList output
        
        foreach (  pEnvironmentVariablesModel.Variable& variable, manager.variables() )            output << QString( "%1(%2)=\"%3\"" )
                .arg( variable.name )
                .arg( QVariant( variable.enabled ).toString() )
                .arg( variable.value )

        
        if  not output.isEmpty() :            output.prepend( MkSShellInterpreter.tr( "Found environment variables:" ) )

        else:
            output << MkSShellInterpreter.tr( "No environment variables found." )

        
        return output.join( "\n" )

    
    return QString.null



def setCommand(self, name, value ):
    variables = self.variables()
    if  not variables.contains( name ) :        variables[ name ].name = name

    variables[ name ].value = value
    setVariables( variables )


def unsetCommand(self, name ):
    variables = self.variables()
    variables.remove( name )
    setVariables( variables )


def clearCommand(self):
    setVariables( pEnvironmentVariablesModel.Variables() )


def enableCommand(self, name, enabled ):
    variables = self.variables()
    if  variables.contains( name ) :        variables[ name ].enabled = enabled

    setVariables( variables )

