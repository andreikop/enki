/****************************************************************************
	Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
****************************************************************************/
#include "ToolsManager.h"
#include "ui/UIToolsEdit.h"
#include "ui/UIDesktopTools.h"

#include <coremanager/MonkeyCore.h>
#include <consolemanager/pConsoleManager.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <settingsmanager/Settings.h>
#include <shellmanager/MkSShellInterpreter.h>
#include <widgets/pMenuBar.h>

#include <QFileIconProvider>
#include <QDesktopServices>
#include <QImageReader>
#include <QUrl>
#include <QDebug>

QFileIconProvider* ToolsManager::mIconProvider = 0;

ToolsManager::ToolsManager( QObject* p )
	: QObject( p )
{
	if ( !mIconProvider ) {
		mIconProvider = new QFileIconProvider();
	}
	
	initializeInterpreterCommands( true );
}

ToolsManager::~ToolsManager()
{
	initializeInterpreterCommands( false );
	delete mIconProvider;
	mIconProvider = 0;
	writeTools( mTools );
}

QString ToolsManager::scriptFilePath() const
{
	return MonkeyCore::settings()->homePath( Settings::SP_SCRIPTS ).append( "/tools.mks" );
}

ToolsManager::Tools ToolsManager::tools( ToolsManager::Type type ) const
{
	ToolsManager::Tools tools;
	
	foreach ( const ToolsManager::Tool& tool, mTools ) {
		if ( ( tool.desktopEntry && type == ToolsManager::DesktopEntry ) 
			|| ( !tool.desktopEntry && type == ToolsManager::UserEntry ) ) {
			tools << tool;
		}
	}
	
	return tools;
}

void ToolsManager::setCommand( const QString& caption, const QString& fileIcon, const QString& filePath, const QString& workingPath, bool desktopEntry, bool useConsoleManager )
{
	for ( int i = 0; i < mTools.count(); i++ ) {
		ToolsManager::Tool& tool = mTools[ i ];
		
		if ( tool.caption == caption ) {
			tool.fileIcon = fileIcon;
			tool.filePath = filePath;
			tool.workingPath = workingPath;
			tool.desktopEntry = desktopEntry;
			tool.useConsoleManager = useConsoleManager;
			return;
		}
	}
	
	mTools << ToolsManager::Tool( caption, fileIcon, filePath, workingPath, desktopEntry, useConsoleManager );
}

void ToolsManager::unsetCommand( const QString& caption )
{
	for ( int i = 0; i < mTools.count(); i++ ) {
		ToolsManager::Tool& tool = mTools[ i ];
		
		if ( tool.caption == caption ) {
			mTools.removeAt( i );
			return;
		}
	}
}

void ToolsManager::clearCommand()
{
	mTools.clear();
}

void ToolsManager::updateMenuCommand()
{
	updateMenuActions();
}

QIcon ToolsManager::icon( const QString& filePath, const QString& optionnalFilePath )
{
	const bool filePathValid = filePath.isEmpty() ? false : !QImageReader::imageFormat( filePath ).isEmpty();
	const bool optionnalFilePathValid = optionnalFilePath.isEmpty() ? false : !QImageReader::imageFormat( optionnalFilePath ).isEmpty();
	QIcon icon;
	
	if ( filePathValid ) {
		icon = QIcon( filePath );
#if QT_VERSION >= 0x040600
	}
	else {
		icon = QIcon::fromTheme( filePath, icon );
#endif
	}
	
	if ( icon.isNull() ) {
		if ( optionnalFilePathValid ) {
			icon = QIcon( optionnalFilePath );
#if QT_VERSION >= 0x040600
		}
		else {
			icon = QIcon::fromTheme( optionnalFilePath, icon );
#endif
		}
	}
	
	if ( icon.isNull() && !filePath.isEmpty() ) {
		icon = mIconProvider->icon( filePath );
	}
	
	if ( icon.isNull() && !optionnalFilePath.isEmpty() ) {
		icon = mIconProvider->icon( optionnalFilePath );
	}
	
	return icon;
}

void ToolsManager::updateMenuActions()
{
	// get menu bar
	pMenuBar* mb = MonkeyCore::menuBar();
	
	// clear action
	qDeleteAll( mb->menu( "mTools/mUserTools" )->actions() );
	qDeleteAll( mb->menu( "mTools/mDesktopTools" )->actions() );
	
	// initialize tools
	foreach ( const ToolsManager::Tool& tool, mTools ) {
		QAction* action;
		
		if ( tool.desktopEntry ) {
			action = mb->action( QString( "mTools/mDesktopTools/%1" ).arg( tool.caption ), tool.caption, icon( tool.fileIcon, tool.filePath ), QString::null, tr( "Execute tool '%1': %2" ).arg( tool.caption ).arg( tool.filePath ) );
		}
		else {
			action = mb->action( QString( "mTools/mUserTools/%1" ).arg( tool.caption ), tool.caption, icon( tool.fileIcon, tool.filePath ), QString::null, tr( "Execute tool '%1': %2" ).arg( tool.caption ).arg( tool.filePath ) );
		}
		
		action->setData( QVariant::fromValue<ToolsManager::Tool>( tool ) );
	}
}

void ToolsManager::editTools_triggered()
{
	QAction* action = qobject_cast<QAction*>( sender() );
	QDialog* dlg = 0;
	
	switch ( ToolsManager::Type( action->data().toInt() ) )
	{
		case ToolsManager::UserEntry:
			dlg = new UIToolsEdit( this, QApplication::activeWindow() );
			break;
		case ToolsManager::DesktopEntry:
			dlg = new UIDesktopTools( this, QApplication::activeWindow() );
			break;
	}
	
	dlg->open();
}

void ToolsManager::toolsMenu_triggered( QAction* action )
{
	pConsoleManager* cm = MonkeyCore::consoleManager();
	const ToolsManager::Tool tool = action->data().value<ToolsManager::Tool>();
	const QString filePath = cm->processInternalVariables( tool.filePath );
	const QString workingPath = cm->processInternalVariables( tool.workingPath );
	bool ok = false;
	
	if ( filePath.isEmpty() ) {
		ok = false;
	}
	else if ( tool.useConsoleManager ) {
		pCommand cmd;
		cmd.setText( tool.caption );
		QStringList commandAndArgs = filePath.split( ' ' );
		cmd.setCommand( commandAndArgs.takeFirst() );
		cmd.setArguments( commandAndArgs.join( " " ) );
		cmd.setWorkingDirectory( workingPath );
		cmd.setTryAllParsers( true );
		cm->addCommand( cmd );
		ok = true;
	}
	else if ( workingPath.isEmpty() && QFile::exists( filePath ) ) {
		ok = QDesktopServices::openUrl( QUrl::fromLocalFile( filePath ) );
	}
	else if ( workingPath.isEmpty() ) {
		ok = QProcess::startDetached( filePath );
	}
	else {
		QProcess* process = new QProcess( this );
		connect( process, SIGNAL( finished( int ) ), process, SLOT( deleteLater() ) );
		process->setWorkingDirectory( workingPath );
		process->start( filePath );
		ok = process->waitForStarted();
	}
	
	if ( !ok ) {
		MonkeyCore::messageManager()->appendMessage( tr( "Error trying to start tool: '%1'" ).arg( filePath ) );
	}
}

bool ToolsManager::writeTools( const ToolsManager::Tools& tools ) const
{
	// write content in utf8
	const QString fn = scriptFilePath();
	QFile file( fn );
	QStringList buffer;
	
	if ( !file.open( QIODevice::WriteOnly ) ) {
		qWarning() << QString( "Can't open file for generating tools script: %1" ).arg( file.errorString() ).toLocal8Bit().constData();
		return false;
	}
	
	file.resize( 0 );
	
	buffer << "# Monkey Studio IDE Tools";
	buffer << "# reset tools";
	buffer << "tools clear";
	buffer << "# Available commands:";
	buffer << "# tools set\tcaption\tfileIcon\tfilePath\tworkingPath\tdesktopEntry\tuseConsoleManager";
	buffer << "# tools unset\tcaption";
	buffer << "# tools clear";
	buffer << "# tools update-menu";
	buffer << "# tools list";
	buffer << "# introduce new tools";
	
	foreach ( const Tool& tool, tools ) {
		buffer << QString( "# %1" ).arg( tool.caption );
		buffer << QString( "tools set \"%1\" \"%2\" \"%3\" \"%4\" \"%5\" \"%6\"" )
			.arg( tool.caption )
			.arg( tool.fileIcon )
			.arg( tool.filePath )
			.arg( tool.workingPath )
			.arg( tool.desktopEntry )
			.arg( tool.useConsoleManager );
	}
	
	buffer << "# Update the menu";
	buffer << "tools update-menu";
	
	if ( file.write( buffer.join( "\n" ).toUtf8() ) == -1 ) {
		qWarning() << QString( "Can't write generated tools script: %1" ).arg( file.errorString() ).toLocal8Bit().constData();
	}
	
	file.close();
	
	return true;
}

void ToolsManager::initializeInterpreterCommands( bool initialize )
{
	if ( initialize ) {
		// register command
		QString help = MkSShellInterpreter::tr(
			"This command manage the tools, usage:\n"
			"\ttools set [caption] [fileIcon] [filePath] [workingPath] [desktopEntry:true|false] [useConsoleManager:true|false]\n"
			"\ttools unset [caption]\n"
			"\ttools clear\n"
			"\ttools update-menu\n"
			"\ttools list"
		);
		
		MonkeyCore::interpreter()->addCommandImplementation( "tools", ToolsManager::commandInterpreter, help, this );
	}
	else {
		MonkeyCore::interpreter()->removeCommandImplementation( "tools" );
	}
}

QString ToolsManager::commandInterpreter( const QString& command, const QStringList& _arguments, int* result, MkSShellInterpreter* interpreter, void* data )
{
	Q_UNUSED( command );
	Q_UNUSED( interpreter );
	ToolsManager* manager = static_cast<ToolsManager*>( data );
	QStringList arguments = _arguments;
	const QStringList allowedOperations = QStringList( "set" ) << "unset" << "clear" << "update-menu" << "list";
	
	if ( result ) {
		*result = MkSShellInterpreter::NoError;
	}
	
	if ( arguments.isEmpty() ) {
		if ( result ) {
			*result = MkSShellInterpreter::InvalidCommand;
		}
		
		return MkSShellInterpreter::tr( "Operation not defined. Available operations are: %1." ).arg( allowedOperations.join( ", " ) );
	}
	
	const QString operation = arguments.takeFirst();
	
	if ( !allowedOperations.contains( operation ) ) {
		if ( result ) {
			*result = MkSShellInterpreter::InvalidCommand;
		}
		
		return MkSShellInterpreter::tr( "Unknown operation: '%1'." ).arg( operation );
	}
	
	if ( operation == "set" ) {
		if ( arguments.count() != 6 ) {
			if ( result ) {
				*result = MkSShellInterpreter::InvalidCommand;
			}
			
			return MkSShellInterpreter::tr( "'set' operation take 6 arguments, %1 given." ).arg( arguments.count() );
		}
		
		const QString caption = arguments.at( 0 );
		const QString fileIcon = arguments.at( 1 );
		const QString filePath = arguments.at( 2 );
		const QString workingPath = arguments.at( 3 );
		const bool desktopEntry = QVariant( arguments.at( 4 ) ).toBool();
		const bool useConsoleManager = QVariant( arguments.at( 5 ) ).toBool();
		
		manager->setCommand( caption, fileIcon, filePath, workingPath, desktopEntry, useConsoleManager );
	}
	
	if ( operation == "unset" ) {
		if ( arguments.count() != 1 ) {
			if ( result ) {
				*result = MkSShellInterpreter::InvalidCommand;
			}
			
			return MkSShellInterpreter::tr( "'unset' operation take 1 arguments, %1 given." ).arg( arguments.count() );
		}
		
		const QString caption = arguments.at( 0 );
		
		manager->unsetCommand( caption );
	}
	
	if ( operation == "clear" ) {
		if ( arguments.count() != 0 ) {
			if ( result ) {
				*result = MkSShellInterpreter::InvalidCommand;
			}
			
			return MkSShellInterpreter::tr( "'clear' operation take no arguments, %1 given." ).arg( arguments.count() );
		}
		
		manager->clearCommand();
	}
	
	if ( operation == "update-menu" ) {
		if ( arguments.count() != 0 ) {
			if ( result ) {
				*result = MkSShellInterpreter::InvalidCommand;
			}
			
			return MkSShellInterpreter::tr( "'update-menu' operation take no arguments, %1 given." ).arg( arguments.count() );
		}
		
		manager->updateMenuCommand();
	}
	
	if ( operation == "list" ) {
		if ( arguments.count() != 0 ) {
			if ( result ) {
				*result = MkSShellInterpreter::InvalidCommand;
			}
			
			return MkSShellInterpreter::tr( "'list' operation take no arguments, %1 given." ).arg( arguments.count() );
		}
		
		QStringList output;
		
		foreach ( const ToolsManager::Tool& tool, manager->mTools ) {
			output << QString( "%1: \"%2\" \"%3\" \"%4\" \"%5\" \"%6\"" )
				.arg( tool.caption )
				.arg( tool.fileIcon )
				.arg( tool.filePath )
				.arg( tool.workingPath )
				.arg( tool.desktopEntry )
				.arg( tool.useConsoleManager );
		}
		
		if ( !output.isEmpty() ) {
			output.prepend( MkSShellInterpreter::tr( "Found tools:" ) );
		}
		else {
			output << MkSShellInterpreter::tr( "No tools found." );
		}
		
		return output.join( "\n" );
	}
	
	return QString::null;
}
