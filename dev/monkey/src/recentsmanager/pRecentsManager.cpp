/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pRecentsManager.cpp
** Date      : 2008-01-14T00:37:07
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
**
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
**
****************************************************************************/
#include "pRecentsManager.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"
#include "pMonkeyStudio.h"

#include <widgets/pMenuBar.h>

#include <QAction>
#include <QFileInfo>
#include <QTimer>

pRecentsManager::pRecentsManager( QObject* p )
	: QObject( p )
{
	// set maximum
	setMaxRecentFiles( maxRecentFiles() );
	setMaxRecentProjects( maxRecentProjects() );
	// update actions
	updateRecentFiles();
	updateRecentProjects();
	// connections
	connect( MonkeyCore::menuBar()->menu( "mFile/mRecents" ), SIGNAL( triggered( QAction* ) ), this, SLOT( recentFiles_triggered( QAction* ) ) );
	connect( MonkeyCore::menuBar()->menu( "mProject/mRecents" ), SIGNAL( triggered( QAction* ) ), this, SLOT( recentProjects_triggered( QAction* ) ) );
}

void pRecentsManager::delayedUpdateRecentFiles()
{
	QTimer::singleShot( 0, this, SLOT( updateRecentFiles() ) );
}

void pRecentsManager::delayedUpdateRecentProjects()
{
	QTimer::singleShot( 0, this, SLOT( updateRecentProjects() ) );
}

int pRecentsManager::maxRecentFiles() const
{ return MonkeyCore::settings()->value( "Recents/MaxFiles", 15 ).toInt(); }

int pRecentsManager::maxRecentProjects() const
{ return MonkeyCore::settings()->value( "Recents/MaxProjects", 15 ).toInt(); }

void pRecentsManager::setMaxRecentFiles( int i )
{
	if ( i != MonkeyCore::settings()->value( "Recents/MaxFiles" ).toInt() )
	{
		MonkeyCore::settings()->setValue( "Recents/MaxFiles", i );
		delayedUpdateRecentFiles();
	}
}

void pRecentsManager::setMaxRecentProjects( int i )
{
	if ( i != MonkeyCore::settings()->value( "Recents/MaxProjects" ).toInt() )
	{
		MonkeyCore::settings()->setValue( "Recents/MaxProjects", i );
		delayedUpdateRecentProjects();
	}
}

void pRecentsManager::recentFiles_triggered( QAction* a )
{
	if ( a->objectName() != "aClear" )
		emit openFileRequested( a->data().toString(), pMonkeyStudio::defaultCodec() );
	else if ( a->objectName() == "aClear" )
	{
		MonkeyCore::settings()->setValue( "Recents/Files", QStringList() );
		delayedUpdateRecentFiles();
	}
}

void pRecentsManager::updateRecentFiles()
{
	// clears actions
	qDeleteAll( mRecentFiles );
	mRecentFiles.clear();
	// get recents files
	QStringList l = MonkeyCore::settings()->value( "Recents/Files" ).toStringList();
	for ( int i = 0; i < maxRecentFiles(); i++ )
	{
		if ( i < l.count() )
		{
			QFileInfo f( l.at( i ).simplified() );
			if ( f.exists() )
			{
				// create action
				QString s = QString( "%1 %2" ).arg( i +1 ).arg( f.fileName() );
				QAction* a = new QAction( s, this );
				a->setData( l.at( i ) );
				a->setStatusTip( l.at( i ) );
				mRecentFiles.append( a );
				// add action
				MonkeyCore::menuBar()->menu( "mFile/mRecents" )->addAction( a );
			}
		}
	}
}

void pRecentsManager::addRecentFile( const QString& s )
{
	// get recents files
	QStringList f = MonkeyCore::settings()->value( "Recents/Files" ).toStringList();
	// remove s and prepend it
	f.removeAll( s );
	f.prepend( s );
	// remove files > maxrecentfiles
	while ( f.size() > maxRecentFiles() )
		f.removeLast();
	// store recents files
	MonkeyCore::settings()->setValue( "Recents/Files", f );
	// update menu
	delayedUpdateRecentFiles();
}

void pRecentsManager::removeRecentFile( const QString& s )
{
	// get recents files
	QStringList f = MonkeyCore::settings()->value( "Recents/Files" ).toStringList();
	// remove s
	f.removeAll( s );
	// remove files > maxrecent files
	while ( f.size() > maxRecentFiles() )
		f.removeLast();
	// store recents files
	MonkeyCore::settings()->setValue( "Recents/Files", f );
	// update menu
	delayedUpdateRecentFiles();
}

void pRecentsManager::recentProjects_triggered( QAction* a )
{
	if ( a->objectName() != "aClear" )
		emit openProjectRequested( a->data().toString(), pMonkeyStudio::defaultCodec() );
	else if ( a->objectName() == "aClear" )
	{
		MonkeyCore::settings()->setValue( "Recents/Projects", QStringList() );
		delayedUpdateRecentProjects();
	}
}

void pRecentsManager::updateRecentProjects()
{
	// clear actions
	qDeleteAll( mRecentProjects );
	mRecentProjects.clear();
	// get recents projects
	QStringList l = MonkeyCore::settings()->value( "Recents/Projects" ).toStringList();
	for ( int i = 0; i < maxRecentProjects(); i++ )
	{
		if ( i < l.count() )
		{
			QFileInfo f( l.at( i ).simplified() );
			if ( f.exists() )
			{
				// create action
				QString s = QString( "%1 %2" ).arg( i +1 ).arg( f.fileName() );
				QAction* a = new QAction( s, this );
				a->setData( l.at( i ) );
				a->setStatusTip( l.at( i ) );
				mRecentProjects.append( a );
				// add action
				MonkeyCore::menuBar()->menu( "mProject/mRecents" )->addAction( a );
			}
		}
	}
}

void pRecentsManager::addRecentProject( const QString& s )
{
	// get recent proejcts
	QStringList f = MonkeyCore::settings()->value( "Recents/Projects" ).toStringList();
	// remove s and prepend it
	f.removeAll( s );
	f.prepend( s );
	// remvoe proejcts > maxrecentprojects
	while ( f.size() > maxRecentProjects() )
		f.removeLast();
	// store recents projects
	MonkeyCore::settings()->setValue( "Recents/Projects", f );
	// update menu
	delayedUpdateRecentProjects();
}

void pRecentsManager::removeRecentProject( const QString& s )
{
	// get recents projects
	QStringList f = MonkeyCore::settings()->value( "Recents/Projects" ).toStringList();
	// remove s
	f.removeAll( s );
	// remove files > maxrecentsproejcts
	while ( f.size() > maxRecentProjects() )
		f.removeLast();
	// store recents proejcts
	MonkeyCore::settings()->setValue( "Recents/Projects", f );
	// update menu
	delayedUpdateRecentProjects();
}
