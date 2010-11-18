#include "MkSShellInterpreter.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <widgets/pQueuedMessageToolBar.h>

#include <QFileInfo>
#include <QDir>
#include <QDebug>

const QString MkSShell_DirName = "mks_scripts";
QPointer<MkSShellInterpreter> MkSShellInterpreter::mInstance = 0;

QString MkSShellInterpreter::interpretHelp( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data )
{
	Q_UNUSED( command );
	Q_UNUSED( data );
	
	if ( arguments.isEmpty() ) // all available commands
	{
		QStringList answer = QStringList( tr( "Available commands:" ) );
		answer << interpreter->mCommandImplementations.keys();
		
		if ( result )
		{
			*result = MkSShellInterpreter::NoError;
		}
		
		return answer.join( "\n" );
	}
	else if ( arguments.count() == 1 ) // help for command
	{
		const QString cmd = arguments.first();
		const QString& usage = interpreter->usage( cmd );
		
		if ( result )
		{
			*result = interpreter->mCommandHelps.contains( cmd ) ? MkSShellInterpreter::NoError : MkSShellInterpreter::InvalidCommand;
		}
		
		return usage;
	}
	
	// error
	if ( result )
	{
		*result = MkSShellInterpreter::InvalidCommand;
	}
	
	return tr( "'help' command accepts only one parameter. %1 given" ).arg( arguments.count() );
}

QString MkSShellInterpreter::interpretEcho( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data )
{
	Q_UNUSED( command );
	Q_UNUSED( interpreter );
	Q_UNUSED( data );
	
	if ( result )
	{
		*result = MkSShellInterpreter::NoError;
	}
	
	QStringList answer;
	
	foreach ( const QString& arg, arguments )
	{
		answer << QString( "Argument: <%1>" ).arg( arg );
	}
	
	return answer.join( "\n" );
}

MkSShellInterpreter* MkSShellInterpreter::instance( QObject* parent )
{
	if ( !mInstance )
	{
		mInstance = new MkSShellInterpreter( parent );
	}
	
	return mInstance;
}

MkSShellInterpreter::MkSShellInterpreter( QObject* parent )
	: QObject( parent ), pConsoleCommand()
{
	addCommandImplementation( "help", interpretHelp, tr( "Type 'help' and name of command" ), this );
	addCommandImplementation( "echo", interpretEcho, tr( "Print back arguments" ), this );
}

bool MkSShellInterpreter::loadScript( const QString& fileName )
{
	QFile file( fileName );
	
	// open file in text mode
	if ( !file.open( QIODevice::ReadOnly | QIODevice::Text ) )
	{
		return false;
	}
	
	QString buffer = QString::fromUtf8( file.readAll() );
	
	// execute each command line
	foreach ( const QString& command, buffer.split( "\n" ) )
	{
		// ignore comments
		if ( command.trimmed().startsWith( "#" ) )
		{
			continue;
		}
		
		interpret( command, 0 );
	}
	
	file.close();
	return true;
}

void MkSShellInterpreter::loadHomeScripts()
{
	const QString path = MonkeyCore::settings()->homePath( Settings::SP_SCRIPTS );
	QFileInfoList files = QDir( path ).entryInfoList( QStringList( "*.mks" ) );
	
	foreach ( const QFileInfo& file, files )
	{
		if ( !loadScript( file.absoluteFilePath() ) )
		{
			MonkeyCore::messageManager()->appendMessage( tr( "An error occur while loading script: '%1'" ).arg( file.fileName() ) );
		}
	}
}

QString MkSShellInterpreter::usage( const QString& command ) const
{
	if ( mCommandHelps.contains( command ) )
	{
		return mCommandHelps[ command ];
	}
	
	return tr( "%1: No help available." ).arg( command );
}

QString MkSShellInterpreter::interpret( const QString& command, int* result ) const
{
	QStringList parts = parseCommand( command );
	
	if ( parts.isEmpty() || !mCommandImplementations.contains( parts.first() ) )
	{
		if ( result )
		{
			*result = MkSShellInterpreter::InvalidCommand;
		}
		
		return tr( "Invalid command: %1" ).arg( command );
	}
	
	MkSShellInterpreter* instance = const_cast<MkSShellInterpreter*>( this );
	const QString cmd = parts.takeFirst();
	void* data = mCommandImplementationsData.value( cmd );
	const QString commandOutput = mCommandImplementations[ cmd ]( cmd, parts, result, instance, data );
	
	emit instance->commandExecuted( command, commandOutput, result ? *result : MkSShellInterpreter::NoResultVariable );
	
	return commandOutput;
}

void MkSShellInterpreter::addCommandImplementation( const QString& command, CommandImplementationPtr function, const QString& help, void* data )
{
	Q_ASSERT( !mCommands.contains( command ) );
	
	mCommands << command;
	mCommandImplementations[ command ] = function;
	mCommandImplementationsData[ command ] = data;
	
	setCommandHelp( command, help );
}

void MkSShellInterpreter::removeCommandImplementation( const QString& command )
{
	mCommands.removeOne( command );
	mCommandImplementations.remove( command );
	mCommandImplementationsData.remove( command );
	mCommandHelps.remove( command );
}

void MkSShellInterpreter::setCommandHelp( const QString& command, const QString& help )
{
	mCommandHelps[ command ] = help;
}
