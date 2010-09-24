'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : pDockFileBrowser.h
** Date      : 2008-01-14T00:39:57
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
    \file pDockFileBrowser.h
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, KOPATS
    \brief UI of FileBrowser plugin
'''

#ifndef PDOCKFILEBROWSER_H
#define PDOCKFILEBROWSER_H

#include <widgets/pDockWidget.h>

#include <QModelIndex>
#include <QSortFilterProxyModel>
#include <QDir>
#include <QMenu>

class pTreeComboBox
class QLineEdit
class QListView
class QFileSystemModel
class QTreeView

'''!
    UI interface of FileBrowser plugin.

    Dock with file system tree, Box, navigation in a file system
    tree, for moving root of tree to currently selected dirrectory and
    up (relatively for current dirrectory)
'''
class pDockFileBrowser : public pDockWidget
    Q_OBJECT

    class FileBrowserFilteredModel : public QSortFilterProxyModel
    public:
        FileBrowserFilteredModel( parent = 0 )
                : QSortFilterProxyModel( parent )
        QStringList filters()
            return mFilters


        void setFilters(  QStringList& filters )
            mFilters = filters
            invalidateFilter()


        int columnCount(  QModelIndex& '''parent''' = QModelIndex() )
            return 1


        virtual bool hasChildren(  parent = QModelIndex() )
            return sourceModel().hasChildren( mapToSource( parent ) )


    protected:
        QStringList mFilters

        bool filterAcceptsRow( int source_row, source_parent )
            if  source_parent == QModelIndex() :
                return True
            return not QDir.match( mFilters, source_parent.child( source_row, 0 ).data().toString() )



public:
    pDockFileBrowser( QWidget* = 0 )

    QString currentPath()
    QString currentFilePath()
    QStringList filters()
    QStringList bookmarks()

protected:
    QLineEdit* mLineEdit
    QTreeView* mTree
    QFileSystemModel* mDirsModel
    FileBrowserFilteredModel* mFilteredModel
    QStringList mBookmarks
    QMenu* mBookmarksMenu

public slots:
    void setCurrentPath(  QString& path )
    void setCurrentFilePath(  QString& filePath )
    void setFilters(  QStringList& filters )
    void setBookmarks(  QStringList& bookmarks )
    void updateBookmarks()

protected slots:
    void aUp_triggered()
    void aGoTo_triggered()
    void aRoot_triggered()
    void aAdd_triggered()
    void aRemove_triggered()
    void bookmark_triggered( QAction* action )
    void tv_activated(  QModelIndex& index )
    void tv_doubleClicked(  QModelIndex& index )


#endif # PDOCKFILEBROWSER_H
