/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : FileBrowser.cpp
** Date      : 2008-01-14T00:39:54
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
/*!
	\file FileBrowser.cpp
	\date 2008-01-14T00:40:08
	\author Filipe AZEVEDO, Andrei KOPATS
	\brief FileBrowser plugin main class. Implementing plugin interface for the
	core
*/

#include "FileBrowser.h"
#include "pDockFileBrowser.h"
#include "FileBrowserSettings.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <pMonkeyStudio.h>
#include <widgets/pDockToolBar.h>
#include <widgets/pActionsManager.h>

#include <QIcon>

void FileBrowser::fillPluginInfos()
{
	mPluginInfos.Caption = tr( "File Browser" );
	mPluginInfos.Description = tr( "Plugin for browsing file outside the project" );
	mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>, Kopats Andei aka hlamer <hlamer@tut.by>";
	mPluginInfos.Type = BasePlugin::iBase;
	mPluginInfos.Name = PLUGIN_NAME;
	mPluginInfos.Version = "1.0.0";
	mPluginInfos.FirstStartEnabled = true;
	mPluginInfos.HaveSettingsWidget = true;
	mPluginInfos.Pixmap = QPixmap( ":/icons/browser.png" );
}


/*!
	Install plugin to the system
	\return Status code of action
	\retval true Successfull
	\retval false Some error ocurred
*/
bool FileBrowser::install()
{
	// create dock
	mDock = new pDockFileBrowser();
	// add dock to dock toolbar entry
	MonkeyCore::mainWindow()->dockToolBar( Qt::LeftToolBarArea )->addDock( mDock, infos().Caption, QIcon( infos().Pixmap ) );
	// create menu action for the dock
	pActionsManager::setDefaultShortcut( mDock->toggleViewAction(), QKeySequence( "F7" ) );
	// restore settings
	restoreSettings();
	return true;
}

/*!
	Uninstall plugin from the system
	\return Status code of action
	\retval true Successfull
	\retval false Some error ocurred
*/
bool FileBrowser::uninstall()
{
	// save settings
	saveSettings();
	// it will remove itself from dock toolbar when deleted
	mDock->deleteLater();
	return true;
}

/*!
	Get settings widget of plugin
	\return Pointer to created settings widget for plugin
*/
QWidget* FileBrowser::settingsWidget()
{ return new FileBrowserSettings( this ); }

/*!
	Get filter wildcards, which using for filtering out some files, which should be removed
	from view (object files, temporary files, ...)
	\return StringList of wildcards, which should be removed from tree
*/
QStringList FileBrowser::filters() const
{ return settingsValue( "Wildcards", QStringList() << "*~" << "*.o" << "*.pyc" << "*.bak" ).toStringList(); }

/*!
	Set wildcards for filtering unneeded files from tree
	\param filters New set of filters
	\param updateDock If true - UI will be updated according with new filters
*/
void FileBrowser::setFilters( const QStringList& filters, bool updateDock )
{
	setSettingsValue( "Wildcards", filters );
	if ( updateDock && mDock )
		mDock->setFilters( filters );
}

QStringList FileBrowser::bookmarks() const
{
	return settingsValue( "Bookmarks", QStringList() << QDir::homePath() ).toStringList();
}

void FileBrowser::setBookmarks( const QStringList& bookmarks, bool updateDock )
{
	setSettingsValue( "Bookmarks", bookmarks );
	if ( updateDock && mDock )
		mDock->setBookmarks( bookmarks );
}

/*!
	Get current path (root of the tree) from the settings
	\return Dirrectory path
*/
QString FileBrowser::path() const
{ return settingsValue( "Path" ).toString(); }

/*!
	Set current path (root of the tree) in the settings
	\param path Current path
	\param updateDock Update UI according with new path
*/
void FileBrowser::setPath( const QString& path, bool updateDock )
{
	setSettingsValue( "Path", path );
	if ( updateDock && mDock )
		mDock->setCurrentPath( path );
}

/*!
	Get current file path from the settings
	\return Directory/File path
*/
QString FileBrowser::filePath() const
{ return settingsValue( "FilePath" ).toString(); }

/*!
	Set current file path in the settings
	\param path/file Current index
	\param updateDock Update UI according with new path
*/
void FileBrowser::setFilePath( const QString& filePath, bool updateDock )
{
	setSettingsValue( "FilePath", filePath );
	if ( updateDock && mDock )
		mDock->setCurrentFilePath( filePath );
}

/*!
	Read current path and filters from UI dock object and save it in the settings
*/
void FileBrowser::saveSettings()
{
	if ( mDock )
	{
		setPath( mDock->currentPath() );
		setFilePath( mDock->currentFilePath() );
		setFilters( mDock->filters() );
		setBookmarks( mDock->bookmarks() );
	}
}

/*!
	Read current path and filters from settings and apply it for UI dock
*/
void FileBrowser::restoreSettings()
{
	if ( mDock )
	{
		mDock->setCurrentPath( path() );
		mDock->setCurrentFilePath( filePath() );
		mDock->setFilters( filters() );
		mDock->setBookmarks( bookmarks() );
	}
}

Q_EXPORT_PLUGIN2( BaseFileBrowser, FileBrowser )