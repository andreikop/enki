'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : FileBrowser.h
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
    \file FileBrowser.h
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, KOPATS
    \brief Header file for FileBrowser plugin
'''
#ifndef FILEBROWSER_H
#define FILEBROWSER_H

#include <pluginsmanager/BasePlugin.h>

#include <QPointer>

class pDockFileBrowser

'''!
    Main class of FileBrowser plugin

    Plugin allows to see file system contents and open files
'''
class FileBrowser : public BasePlugin
    Q_OBJECT
    Q_INTERFACES( BasePlugin )

protected:
    void fillPluginInfos()
    virtual bool install()
    virtual bool uninstall()
public:
    virtual QWidget* settingsWidget()

    QStringList filters()
    void setFilters(  QStringList& filters, updateDock = False )

    QStringList bookmarks()
    void setBookmarks(  QStringList& bookmarks, updateDock = False )

    QString path()
    void setPath(  QString& path, updateDock = False )

    QString filePath()
    void setFilePath(  QString& filePath, updateDock = False )

protected:
    QPointer<pDockFileBrowser> mDock

protected slots:
    void saveSettings()
    void restoreSettings()


#endif