#include "MkSShellInterpreter.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <widgets/pQueuedMessageToolBar.h>

#include <QFileInfo>
#include <QDir>
#include <QDebug>

 MkSShell_DirName = "mks_scripts"
QPointer<MkSShellInterpreter> MkSShellInterpreter.mInstance = 0

def interpretHelp(self, command, arguments, result, interpreter, data ):
    Q_UNUSED( command )
    Q_UNUSED( data )
    
    if ( arguments.isEmpty() ) # all available commands
        answer = QStringList( tr( "Available commands:" ) )
        answer << interpreter.mCommandImplementations.keys()
        
        if  result :
            *result = MkSShellInterpreter.NoError

        
        return answer.join( "\n" )

    elif ( arguments.count() == 1 ) # help for command
         cmd = arguments.first()
         usage = interpreter.usage( cmd )
        
        if  result :
            *result = interpreter.mCommandHelps.contains( cmd ) ? MkSShellInterpreter.NoError : MkSShellInterpreter.InvalidCommand

        
        return usage

    
    # error
    if  result :
        *result = MkSShellInterpreter.InvalidCommand

    
    return tr( "'help' command accepts only one parameter. %1 given" ).arg( arguments.count() )


def interpretEcho(self, command, arguments, result, interpreter, data ):
    Q_UNUSED( command )
    Q_UNUSED( interpreter )
    Q_UNUSED( data )
    
    if  result :
        *result = MkSShellInterpreter.NoError

    
    QStringList answer
    
    for arg in arguments:
        answer << QString( "Argument: <%1>" ).arg( arg )

    
    return answer.join( "\n" )


def instance(self, parent ):
    if  not mInstance :
        mInstance = MkSShellInterpreter( parent )

    
    return mInstance


MkSShellInterpreter.MkSShellInterpreter( QObject* parent )
    : QObject( parent ), pConsoleCommand()
    addCommandImplementation( "help", interpretHelp, tr( "Type 'help' and name of command" ), self )
    addCommandImplementation( "echo", interpretEcho, tr( "Print back arguments" ), self )


def loadScript(self, fileName ):
    QFile file( fileName )
    
    # open file in text mode
    if  not file.open( QIODevice.ReadOnly | QIODevice.Text ) :
        return False

    
    buffer = QString.fromUtf8( file.readAll() )
    
    # execute each command line
    foreach (  QString& command, buffer.split( "\n" ) )
        # ignore comments
        if  command.trimmed().startsWith( "#" ) :
            continue

        
        interpret( command, 0 )

    
    file.close()
    return True


def loadHomeScripts(self):
     path = MonkeyCore.settings().homePath( Settings.SP_SCRIPTS )
    files = QDir( path ).entryInfoList( QStringList( "*.mks" ) )
    
    for file in files:
        if  not loadScript( file.absoluteFilePath() ) :
            MonkeyCore.messageManager().appendMessage( tr( "An error occur while loading script: '%1'" ).arg( file.fileName() ) )




def usage(self, command ):
    if  mCommandHelps.contains( command ) :
        return mCommandHelps[ command ]

    
    return tr( "%1: No help available." ).arg( command )


def interpret(self, command, result ):
    parts = parseCommand( command )
    
    if  parts.isEmpty() or not mCommandImplementations.contains( parts.first() ) :
        if  result :
            *result = MkSShellInterpreter.InvalidCommand

        
        return tr( "Invalid command: %1" ).arg( command )

    
    instance = const_cast<MkSShellInterpreter*>( self )
     cmd = parts.takeFirst()
    data = mCommandImplementationsData.value( cmd )
     commandOutput = mCommandImplementations[ cmd ]( cmd, parts, result, instance, data )
    
    instance.emit.commandExecuted( command, commandOutput, result ? *result : MkSShellInterpreter.NoResultVariable )
    
    return commandOutput


def addCommandImplementation(self, command, function, help, data ):
    Q_ASSERT( not mCommands.contains( command ) )
    
    mCommands << command
    mCommandImplementations[ command ] = function
    mCommandImplementationsData[ command ] = data
    
    setCommandHelp( command, help )


def removeCommandImplementation(self, command ):
    mCommands.removeOne( command )
    mCommandImplementations.remove( command )
    mCommandImplementationsData.remove( command )
    mCommandHelps.remove( command )


def setCommandHelp(self, command, help ):
    mCommandHelps[ command ] = help

