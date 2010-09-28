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
/*!
    \file FileWatcher.cpp
    \date 2009-10-06
    \author Filipe AZEVEDO
    \brief FileWatcher plugin main class. Implementing plugin interface for the core
*/

#include "FileWatcher.h"

#include <objects/pIconManager.h>
#include <coremanager/MonkeyCore.h>
#include <workspace/pFileManager.h>
#include <workspace/pAbstractChild.h>
#include <workspace/pOpenedFileExplorer.h>

#include <QFileSystemWatcher>
#include <QDebug>

/*!
    Get settings widget of plugin
    \return Pointer to created settings widget for plugin
*/
QWidget* FileWatcher::settingsWidget()
{
    return 0;
}

void FileWatcher::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "File Watcher" );
    mPluginInfos.Description = tr( "Plugin for tracking opened documents changes." );
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>";
    mPluginInfos.Type = BasePlugin::iBase;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "1.0.0";
    mPluginInfos.FirstStartEnabled = true;
    mPluginInfos.HaveSettingsWidget = false;
    mPluginInfos.Pixmap = pIconManager::pixmap( "filewatcher.png" );
}

/*!
    Install plugin to the system
    \return Status code of action
    \retval true Successfull
    \retval false Some error ocurred
*/
bool FileWatcher::install()
{
    mFileWatcher = MonkeyCore::workspace()->fileWatcher();
    pFileManager* fm = MonkeyCore::fileManager();
    
    connect( mFileWatcher, SIGNAL( fileChanged( const QString& ) ), this, SLOT( fileChanged( const QString& ) ) );
    connect( fm, SIGNAL( documentOpened( pAbstractChild* ) ), this, SLOT( documentOpened( pAbstractChild* ) ) );
    connect( fm, SIGNAL( documentChanged( pAbstractChild* ) ), this, SLOT( documentChanged( pAbstractChild* ) ) );
    connect( fm, SIGNAL( documentModifiedChanged( pAbstractChild*, bool ) ), this, SLOT( documentModifiedChanged( pAbstractChild*, bool ) ) );
    connect( fm, SIGNAL( documentAboutToClose( pAbstractChild* ) ), this, SLOT( documentAboutToClose( pAbstractChild* ) ) );
    connect( fm, SIGNAL( documentClosed( pAbstractChild* ) ), this, SLOT( documentClosed( pAbstractChild* ) ) );
    connect( fm, SIGNAL( documentReloaded( pAbstractChild* ) ), this, SLOT( documentReloaded( pAbstractChild* ) ) );
    connect( fm, SIGNAL( currentDocumentChanged( pAbstractChild* ) ), this, SLOT( currentDocumentChanged( pAbstractChild* ) ) );
    
    return true;
}

/*!
    Uninstall plugin from the system
    \return Status code of action
    \retval true Successfull
    \retval false Some error ocurred
*/
bool FileWatcher::uninstall()
{
    pFileManager* fm = MonkeyCore::fileManager();
    
    disconnect( mFileWatcher, SIGNAL( fileChanged( const QString& ) ), this, SLOT( fileChanged( const QString& ) ) );
    disconnect( fm, SIGNAL( documentOpened( pAbstractChild* ) ), this, SLOT( documentOpened( pAbstractChild* ) ) );
    disconnect( fm, SIGNAL( documentChanged( pAbstractChild* ) ), this, SLOT( documentChanged( pAbstractChild* ) ) );
    disconnect( fm, SIGNAL( documentModifiedChanged( pAbstractChild*, bool ) ), this, SLOT( documentModifiedChanged( pAbstractChild*, bool ) ) );
    disconnect( fm, SIGNAL( documentAboutToClose( pAbstractChild* ) ), this, SLOT( documentAboutToClose( pAbstractChild* ) ) );
    disconnect( fm, SIGNAL( documentClosed( pAbstractChild* ) ), this, SLOT( documentClosed( pAbstractChild* ) ) );
    disconnect( fm, SIGNAL( documentReloaded( pAbstractChild* ) ), this, SLOT( documentReloaded( pAbstractChild* ) ) );
    disconnect( fm, SIGNAL( currentDocumentChanged( pAbstractChild* ) ), this, SLOT( currentDocumentChanged( pAbstractChild* ) ) );
    
    mFileWatcher = 0;
    
    return true;
}

void FileWatcher::updateDocumentState( pAbstractChild* document )
{
    pOpenedFileExplorer* dock = MonkeyCore::workspace()->dockWidget();
    pOpenedFileModel* model = dock->model();
    const QString path = document->filePath();
    QIcon icon;
    
    switch ( mExternallyModified[ path ] )
    {
        case FileWatcher::None:
            break;
        case FileWatcher::Modified:
            icon = pIconManager::icon( "modified.png" );
            break;
        case FileWatcher::Deleted:
            icon = pIconManager::icon( "deleted.png" );
            break;
    }
    
    if ( mExternallyModified[ path ] == FileWatcher::Modified && document->isModified() )
    {
        icon = pIconManager::icon( "modified-externally-modified.png" );
    }
    else if ( mExternallyModified[ path ] == FileWatcher::Deleted && document->isModified() )
    {
        icon = pIconManager::icon( "modified-externally-deleted.png" );
    }
    
    QStringList toolTip( path );
    
    if ( document->isModified() )
    {
        toolTip << QString( "<font color='blue'>%1</font>" ).arg( tr( "Locally Modified" ) );
    }
    
    if ( mExternallyModified[ path ] == FileWatcher::Modified )
    {
        toolTip << QString( "<font color='red'>%1</font>" ).arg( tr( "Externally Modified" ) );
    }
    
    if ( mExternallyModified[ path ] == FileWatcher::Deleted )
    {
        toolTip << QString( "<font color='red'>%1</font>" ).arg( tr( "Externally Deleted" ) );
    }
    
    model->setDocumentIcon( document, icon );
    model->setDocumentToolTip( document, toolTip.join( "<br />" ) );
}

void FileWatcher::fileChanged( const QString& path )
{
    pAbstractChild* document = MonkeyCore::fileManager()->openedDocument( path );
    
    if ( !document )
    {
        return;
    }
    
    mExternallyModified[ path ] = QFile::exists( path ) ? FileWatcher::Modified : FileWatcher::Deleted;
    
    if ( mExternallyModified[ path ] == FileWatcher::Modified )
    {
        const QString documentBuffer = document->fileBuffer();
        QString fileBuffer;
        
        QFile file( path );
        file.open( QIODevice::ReadOnly );
        fileBuffer = document->codec()->toUnicode( file.readAll() );
        file.close();
        
        if ( documentBuffer == fileBuffer && !document->isModified() )
        {
            mExternallyModified[ path ] = FileWatcher::None;
        }
    }
    
    documentChanged( document );
}

void FileWatcher::documentOpened( pAbstractChild* document )
{
    const QString path = document->filePath();
    mExternallyModified[ path ] = FileWatcher::None;
    
    updateDocumentState( document );
}

void FileWatcher::documentChanged( pAbstractChild* document )
{
    updateDocumentState( document );
}

void FileWatcher::documentModifiedChanged( pAbstractChild* document, bool modified )
{
    Q_UNUSED( modified );
    documentChanged( document );
}

void FileWatcher::documentAboutToClose( pAbstractChild* document )
{
    mExternallyModified.remove( document->filePath() );
}

void FileWatcher::documentClosed( pAbstractChild* document )
{
    Q_UNUSED( document );
}

void FileWatcher::documentReloaded( pAbstractChild* document )
{
    documentOpened( document );
}

void FileWatcher::currentDocumentChanged( pAbstractChild* document )
{
    Q_UNUSED( document );
}

Q_EXPORT_PLUGIN2( BaseFileWatcher, FileWatcher )
