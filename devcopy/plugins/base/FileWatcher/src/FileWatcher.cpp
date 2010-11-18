'''***************************************************************************
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
***************************************************************************'''
'''!
    \file FileWatcher.cpp
    \date 2009-10-06
    \author Filipe AZEVEDO
    \brief FileWatcher plugin main class. Implementing plugin interface for the core
'''

#include "FileWatcher.h"

#include <objects/pIconManager.h>
#include <coremanager/MonkeyCore.h>
#include <workspace/pFileManager.h>
#include <workspace/pAbstractChild.h>
#include <workspace/pOpenedFileExplorer.h>

#include <QFileSystemWatcher>
#include <QDebug>

'''!
    Get settings widget of plugin
    \return Pointer to created settings widget for plugin
'''
def settingsWidget(self):
    return 0


def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "File Watcher" )
    mPluginInfos.Description = tr( "Plugin for tracking opened documents changes." )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = False
    mPluginInfos.Pixmap = pIconManager.pixmap( "filewatcher.png" )


'''!
    Install plugin to the system
    \return Status code of action
    \retval True Successfull
    \retval False Some error ocurred
'''
def install(self):
    mFileWatcher = MonkeyCore.workspace().fileWatcher()
    fm = MonkeyCore.fileManager()
    
    mFileWatcher.fileChanged.connect(self.fileChanged)
    fm.documentOpened.connect(self.documentOpened)
    fm.documentChanged.connect(self.documentChanged)
    fm.documentModifiedChanged.connect(self.documentModifiedChanged)
    fm.documentAboutToClose.connect(self.documentAboutToClose)
    fm.documentClosed.connect(self.documentClosed)
    fm.documentReloaded.connect(self.documentReloaded)
    fm.currentDocumentChanged.connect(self.currentDocumentChanged)
    
    return True


'''!
    Uninstall plugin from the system
    \return Status code of action
    \retval True Successfull
    \retval False Some error ocurred
'''
def uninstall(self):
    fm = MonkeyCore.fileManager()
    
    dismFileWatcher.fileChanged.connect(self.fileChanged)
    disfm.documentOpened.connect(self.documentOpened)
    disfm.documentChanged.connect(self.documentChanged)
    disfm.documentModifiedChanged.connect(self.documentModifiedChanged)
    disfm.documentAboutToClose.connect(self.documentAboutToClose)
    disfm.documentClosed.connect(self.documentClosed)
    disfm.documentReloaded.connect(self.documentReloaded)
    disfm.currentDocumentChanged.connect(self.currentDocumentChanged)
    
    mFileWatcher = 0
    
    return True


def updateDocumentState(self, document ):
    dock = MonkeyCore.workspace().dockWidget()
    model = dock.model()
     path = document.filePath()
    QIcon icon
    
    switch ( mExternallyModified[ path ] )
        case FileWatcher.None:
            break
        case FileWatcher.Modified:
            icon = pIconManager.icon( "modified.png" )
            break
        case FileWatcher.Deleted:
            icon = pIconManager.icon( "deleted.png" )
            break

    
    if  mExternallyModified[ path ] == FileWatcher.Modified and document.isModified() :
        icon = pIconManager.icon( "modified-externally-modified.png" )

    elif  mExternallyModified[ path ] == FileWatcher.Deleted and document.isModified() :
        icon = pIconManager.icon( "modified-externally-deleted.png" )

    
    QStringList toolTip( path )
    
    if  document.isModified() :
        toolTip << QString( "<font color='blue'>%1</font>" ).arg( tr( "Locally Modified" ) )

    
    if  mExternallyModified[ path ] == FileWatcher.Modified :
        toolTip << QString( "<font color='red'>%1</font>" ).arg( tr( "Externally Modified" ) )

    
    if  mExternallyModified[ path ] == FileWatcher.Deleted :
        toolTip << QString( "<font color='red'>%1</font>" ).arg( tr( "Externally Deleted" ) )

    
    model.setDocumentIcon( document, icon )
    model.setDocumentToolTip( document, toolTip.join( "<br />" ) )


def fileChanged(self, path ):
    document = MonkeyCore.fileManager().openedDocument( path )
    
    if  not document :
        return

    
    mExternallyModified[ path ] = QFile.exists( path ) ? FileWatcher.Modified : FileWatcher.Deleted
    
    if  mExternallyModified[ path ] == FileWatcher.Modified :
         documentBuffer = document.fileBuffer()
        QString fileBuffer
        
        QFile file( path )
        file.open( QIODevice.ReadOnly )
        fileBuffer = document.codec().toUnicode( file.readAll() )
        file.close()
        
        if  documentBuffer == fileBuffer and not document.isModified() :
            mExternallyModified[ path ] = FileWatcher.None


    
    documentChanged( document )


def documentOpened(self, document ):
     path = document.filePath()
    mExternallyModified[ path ] = FileWatcher.None
    
    updateDocumentState( document )


def documentChanged(self, document ):
    updateDocumentState( document )


def documentModifiedChanged(self, document, modified ):
    Q_UNUSED( modified )
    documentChanged( document )


def documentAboutToClose(self, document ):
    mExternallyModified.remove( document.filePath() )


def documentClosed(self, document ):
    Q_UNUSED( document )


def documentReloaded(self, document ):
    documentOpened( document )


def currentDocumentChanged(self, document ):
    Q_UNUSED( document )


Q_EXPORT_PLUGIN2( BaseFileWatcher, FileWatcher )
