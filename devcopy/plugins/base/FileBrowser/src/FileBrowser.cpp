'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : FileBrowser.cpp
** Date      : 2008-01-14T00:39:54
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
'''!
    \file FileBrowser.cpp
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, KOPATS
    \brief FileBrowser plugin main class. Implementing plugin interface for the
    core
'''

#include "FileBrowser.h"
#include "pDockFileBrowser.h"
#include "FileBrowserSettings.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <pMonkeyStudio.h>
#include <widgets/pDockToolBar.h>
#include <widgets/pActionsManager.h>

#include <QIcon>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "File Browser" )
    mPluginInfos.Description = tr( "Plugin for browsing file outside the project" )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>, Andei aka hlamer <hlamer@tut.by>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = True
    mPluginInfos.Pixmap = QPixmap( ":/icons/browser.png" )



'''!
    Install plugin to the system
    \return Status code of action
    \retval True Successfull
    \retval False Some error ocurred
'''
def install(self):
    # create dock
    mDock = pDockFileBrowser()
    # add dock to dock toolbar entry
    MonkeyCore.mainWindow().dockToolBar( Qt.LeftToolBarArea ).addDock( mDock, infos().Caption, QIcon( infos().Pixmap ) )
    # create menu action for the dock
    pActionsManager.setDefaultShortcut( mDock.toggleViewAction(), QKeySequence( "F7" ) )
    # restore settings
    restoreSettings()
    return True


'''!
    Uninstall plugin from the system
    \return Status code of action
    \retval True Successfull
    \retval False Some error ocurred
'''
def uninstall(self):
    # save settings
    saveSettings()
    # it will remove itself from dock toolbar when deleted
    mDock.deleteLater()
    return True


'''!
    Get settings widget of plugin
    \return Pointer to created settings widget for plugin
'''
def settingsWidget(self):
    return FileBrowserSettings( self )


'''!
    Get filter wildcards, using for filtering out some files, should be removed
    from view (object files, files, ...)
    \return StringList of wildcards, should be removed from tree
'''
def filters(self):
    return settingsValue( "Wildcards", QStringList() << "*~" << "*.o" << "*.pyc" << "*.bak" ).toStringList()


'''!
    Set wildcards for filtering unneeded files from tree
    \param filters New set of filters
    \param updateDock If True - UI will be updated according with filters
'''
def setFilters(self, filters, updateDock ):
    setSettingsValue( "Wildcards", filters )
    if  updateDock and mDock :
        mDock.setFilters( filters )


def bookmarks(self):
    return settingsValue( "Bookmarks", QStringList() << QDir.homePath() ).toStringList()


def setBookmarks(self, bookmarks, updateDock ):
    setSettingsValue( "Bookmarks", bookmarks )
    if  updateDock and mDock :
        mDock.setBookmarks( bookmarks )


'''!
    Get current path (root of the tree) from the settings
    \return Dirrectory path
'''
def path(self):
    return settingsValue( "Path" ).toString()


'''!
    Set current path (root of the tree) in the settings
    \param path Current path
    \param updateDock Update UI according with path
'''
def setPath(self, path, updateDock ):
    setSettingsValue( "Path", path )
    if  updateDock and mDock :
        mDock.setCurrentPath( path )


'''!
    Get current file path from the settings
    \return Directory/File path
'''
def filePath(self):
    return settingsValue( "FilePath" ).toString()


'''!
    Set current file path in the settings
    \param path/file Current index
    \param updateDock Update UI according with path
'''
def setFilePath(self, filePath, updateDock ):
    setSettingsValue( "FilePath", filePath )
    if  updateDock and mDock :
        mDock.setCurrentFilePath( filePath )


'''!
    Read current path and filters from UI dock object and save it in the settings
'''
def saveSettings(self):
    if  mDock :
        setPath( mDock.currentPath() )
        setFilePath( mDock.currentFilePath() )
        setFilters( mDock.filters() )
        setBookmarks( mDock.bookmarks() )



'''!
    Read current path and filters from settings and apply it for UI dock
'''
def restoreSettings(self):
    if  mDock :
        mDock.setCurrentPath( path() )
        mDock.setCurrentFilePath( filePath() )
        mDock.setFilters( filters() )
        mDock.setBookmarks( bookmarks() )



Q_EXPORT_PLUGIN2( BaseFileBrowser, FileBrowser )