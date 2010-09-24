'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : pDockFileBrowser.cpp
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
    \file pDockFileBrowser.cpp
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, KOPATS
    \brief UI of FileBrowser plugin
'''
#include "pDockFileBrowser.h"

#include <workspace/pWorkspace.h>
#include <coremanager/MonkeyCore.h>
#include <workspace/pFileManager.h>
#include <pMonkeyStudio.h>
#include <widgets/pDockWidgetTitleBar.h>
#include <objects/pIconManager.h>

#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QToolButton>
#include <QComboBox>
#include <QLineEdit>
#include <QListView>
#include <QFileSystemModel>
#include <QScrollArea>
#include <QTabWidget>
#include <QTreeView>
#include <QFileDialog>
#include <QShortcut>

#include <QDebug>

'''!
    Create UI
    \param w Pointer to parent widget
'''
pDockFileBrowser.pDockFileBrowser( QWidget* w )
        : pDockWidget( w )
    # restrict areas
    setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )

    # actions
    # cdup action
    aUp = QAction( tr( "Go Up" ), self )
    aUp.setIcon( pIconManager.icon( "up.png", ":/icons" ) )
    aUp.setToolTip( aUp.text() )
    titleBar().addAction( aUp, 0 )

    # go to action
    aGoTo = QAction( tr( "Select a root folder" ), self )
    aGoTo.setIcon( pIconManager.icon( "browser.png", ":/icons" ) )
    aGoTo.setToolTip( aGoTo.text() )
    titleBar().addAction( aGoTo, 1 )

    # set current path action
    aRoot = QAction( tr( "Set selected item as root" ), self )
    aRoot.setIcon( pIconManager.icon( "goto.png", ":/icons" ) )
    aRoot.setToolTip( aRoot.text() )
    titleBar().addAction( aRoot, 2 )

    # add separator
    titleBar().addSeparator( 3 )

    # add bookmark
    aAdd = QAction( tr( "Add the current selected folder to bookmarks" ), self )
    aAdd.setIcon( pIconManager.icon( "add.png" ) )
    aAdd.setToolTip( aAdd.text() )
    titleBar().addAction( aAdd, 4 )

    # remove bookmark
    aRemove = QAction( tr( "Remove the current selected folder from bookmarks" ), self )
    aRemove.setIcon( pIconManager.icon( "remove.png" ) )
    aRemove.setToolTip( aRemove.text() )
    titleBar().addAction( aRemove, 5 )

    # bookmarks menu
    mBookmarksMenu = QMenu( self )
    aBookmarks = QAction( tr( "Bookmarks..." ), self )
    aBookmarks.setIcon( pIconManager.icon( "bookmark.png" ) )
    aBookmarks.setToolTip( aBookmarks.text() )
    tb = qobject_cast<QToolButton*>( titleBar().addAction( aBookmarks, 6 ) )
    tb.setPopupMode( QToolButton.InstantPopup )
    aBookmarks.setMenu( mBookmarksMenu )

    # add separator
    titleBar().addSeparator( 7 )

    # central widget
    wdg = QWidget( self )
    setWidget( wdg )

    # vertical layout
    vl = QVBoxLayout( wdg )
    vl.setMargin( 5 )
    vl.setSpacing( 3 )

    # lineedit
    mLineEdit = QLineEdit
    mLineEdit.setAttribute( Qt.WA_MacShowFocusRect, False )
    mLineEdit.setAttribute( Qt.WA_MacSmallSize )
    mLineEdit.setReadOnly( True )
    vl.addWidget( mLineEdit )

    # hline
    hline = QFrame( self )
    hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )
    vl.addWidget( hline )

    # dir model
    mDirsModel = QFileSystemModel( self )
    mDirsModel.setNameFilterDisables( False )
    mDirsModel.setFilter( QDir.AllDirs | QDir.AllEntries | QDir.CaseSensitive | QDir.NoDotAndDotDot )

    # create proxy model
    mFilteredModel = FileBrowserFilteredModel( self )
    mFilteredModel.setSourceModel( mDirsModel )

    # files view
    mTree = QTreeView
    mTree.setAttribute( Qt.WA_MacShowFocusRect, False )
    mTree.setAttribute( Qt.WA_MacSmallSize )
    mTree.setContextMenuPolicy( Qt.ActionsContextMenu )
    mTree.setHeaderHidden( True )
    mTree.setUniformRowHeights( True )
    vl.addWidget( mTree )

    # assign model to views
    mTree.setModel( mFilteredModel )

    # set root index
#ifndef Q_OS_WIN
    mDirsModel.setRootPath( "/" )
#else:
    mDirsModel.setRootPath( QString.null )
#endif

    # set lineedit path
    setCurrentPath( mDirsModel.filePath( mDirsModel.index( 0, 0 ) ) )

    # redirirect focus proxy
    setFocusProxy( mTree )

    # set tree actions
    mTree.addAction( aUp )
    mTree.addAction( aGoTo )
    mTree.addAction( aRoot )
    mTree.addAction( aAdd )
    mTree.addAction( aRemove )
    mTree.addAction( aBookmarks )

    # shortcut accessible only when mTree has focus
    aUpShortcut = QShortcut( QKeySequence( "BackSpace" ), mTree )
    aUpShortcut.setContext( Qt.WidgetShortcut )

    # connections
    connect( aUpShortcut, SIGNAL( activated() ), aUp, SIGNAL( triggered() ) )
    aUp.triggered.connect(self.aUp_triggered)
    aGoTo.triggered.connect(self.aGoTo_triggered)
    aRoot.triggered.connect(self.aRoot_triggered)
    aAdd.triggered.connect(self.aAdd_triggered)
    aRemove.triggered.connect(self.aRemove_triggered)
    mBookmarksMenu.triggered.connect(self.bookmark_triggered)
    mTree.activated.connect(self.tv_activated)
    mTree.doubleClicked.connect(self.tv_doubleClicked)


'''!
    Handler of click on Up button.

    Moves root of tree up one level
'''
def aUp_triggered(self):
    # cd up only if not the root index
    index = mTree.rootIndex()

    if  not index.isValid() :
        return


    index = index.parent()
    index = mFilteredModel.mapToSource( index )
     path = mDirsModel.filePath( index )

#ifndef Q_OS_WIN
    if  path.isEmpty() :
        return

#endif

    setCurrentPath( path )


def aGoTo_triggered(self):
    action = qobject_cast<QAction*>( sender() )
     path = QFileDialog.getExistingDirectory( window(), action.toolTip(), currentPath() )

    if  not path.isEmpty() :
        setCurrentPath( path )



'''!
    Handler of click on Root button.

    If there are selected dirrectory in the tree - it will be set as root
'''
def aRoot_triggered(self):
    # seet root of model to path of selected item
    index = mTree.selectionModel().selectedIndexes().value( 0 )
    if  not index.isValid() :
        return
    index = mFilteredModel.mapToSource( index )
    if  not mDirsModel.isDir( index ) :
        index = index.parent()
    setCurrentPath( mDirsModel.filePath( index ) )


def aAdd_triggered(self):
     path = currentPath()

    if  not mBookmarks.contains( path ) and not path.isEmpty() :
        mBookmarks << path
        updateBookmarks()



def aRemove_triggered(self):
     path = currentPath()

    if  mBookmarks.contains( path ) :
        mBookmarks.removeAll( path )
        updateBookmarks()



def bookmark_triggered(self, action ):
    setCurrentPath( action.data().toString() )


def tv_activated(self, idx ):
     index = mFilteredModel.mapToSource( idx )

    if  mDirsModel.isDir( index ) :
        setCurrentPath( mDirsModel.filePath( index ) )

    else:
        MonkeyCore.fileManager().openFile( mDirsModel.filePath( index ), pMonkeyStudio.defaultCodec() )



'''!
    Handler of click on item in the tree

    If there are file doubleclicked - it will be opened
    \param idx Index of clicked tree
'''
def tv_doubleClicked(self, idx ):
    # open file corresponding to index
     index = mFilteredModel.mapToSource( idx )

    if  not mDirsModel.isDir( index ) :
        MonkeyCore.fileManager().openFile( mDirsModel.filePath( index ), pMonkeyStudio.defaultCodec() )



'''!
    Get current path (root of the tree)
    \return Current path (root of the tree)
'''
def currentPath(self):
    index = mTree.rootIndex()
    index = mFilteredModel.mapToSource( index )
    return mDirsModel.filePath( index )


'''!
    Set current path (root of the tree)
    \param s New path
'''
def setCurrentPath(self, s ):
    # get index
    index = mDirsModel.index( s )
    # set current path
    mFilteredModel.invalidate()
    mTree.setRootIndex( mFilteredModel.mapFromSource( index ) )
    # set lineedit path
    mLineEdit.setText( mDirsModel.filePath( index ) )
    mLineEdit.setToolTip( mLineEdit.text() )


'''!
    Get current file path (selected item)
    \return Current file path (selected item)
'''
def currentFilePath(self):
    index = mTree.selectionModel().selectedIndexes().value( 0 )
    index = mFilteredModel.mapToSource( index )
    return mDirsModel.filePath( index )


'''!
    Set current file path (selected item)
    \param s New file path
'''
def setCurrentFilePath(self, s ):
    # get index
    index = mDirsModel.index( s )
    index = mFilteredModel.mapFromSource( index )
    mTree.setCurrentIndex( index )


'''!
    Get filter wildcards, currently using for filtering out unneeded file
    names from tree
    \return List if wildcards for filtering
'''
def filters(self):
    return mFilteredModel.filters()


'''!
    Set filter wildcards for filtering out unneeded files
    \param filters List of wildcards
'''
def setFilters(self, filters ):
    mFilteredModel.setFilters( filters )


def bookmarks(self):
    return mBookmarks


def setBookmarks(self, bookmarks ):
    if  mBookmarks == bookmarks :
        return


    mBookmarks = bookmarks
    updateBookmarks()


def updateBookmarks(self):
    mBookmarksMenu.clear()

    for path in mBookmarks:
        action = mBookmarksMenu.addAction( QDir( path ).dirName() )
        action.setToolTip( path )
        action.setStatusTip( path )
        action.setData( path )

