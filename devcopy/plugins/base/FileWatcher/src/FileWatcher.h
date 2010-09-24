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
    \file FileWatcher.h
    \date 2009-10-06
    \author Filipe AZEVEDO
    \brief Header file for FileWatcher plugin
'''
#ifndef FILEBROWSER_H
#define FILEBROWSER_H

#include <pluginsmanager/BasePlugin.h>

#include <QPointer>

class pAbstractChild
class QFileSystemWatcher

'''!
    Main class of FileWatcher plugin

    Plugin track opened files for external modification, and propose some actions.
'''
class FileWatcher : public BasePlugin
    Q_OBJECT
    Q_INTERFACES( BasePlugin )

public:
    enum WatchState
        None,
        Modified,
        Deleted


    virtual QWidget* settingsWidget()

protected:
    QPointer<QFileSystemWatcher> mFileWatcher
    QMap<QString, mExternallyModified

    virtual void fillPluginInfos()
    virtual bool install()
    virtual bool uninstall()

    void updateDocumentState( pAbstractChild* document )

protected slots:
    void fileChanged(  QString& path )
    void documentOpened( pAbstractChild* document )
    void documentChanged( pAbstractChild* document )
    void documentModifiedChanged( pAbstractChild* document, modified )
    void documentAboutToClose( pAbstractChild* document )
    void documentClosed( pAbstractChild* document )
    void documentReloaded( pAbstractChild* document )
    void currentDocumentChanged( pAbstractChild* document )


#endif
