/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : pDockFileBrowser.cpp
** Date      : 2008-01-14T00:39:57
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
    \file pDockFileBrowser.cpp
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, Andrei KOPATS
    \brief UI of FileBrowser plugin
*/
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

/*!
    Create UI
    \param w Pointer to parent widget
*/
pDockFileBrowser::pDockFileBrowser( QWidget* w )
    : pDockWidget( w )
{
    // restrict areas
    setAllowedAreas( Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea );
    
    // actions
    // cdup action
    QAction* aUp = new QAction( tr( "Go Up" ), this );
    aUp->setIcon( pIconManager::icon( "up.png", ":/icons" ) );
    aUp->setToolTip( aUp->text() );
    titleBar()->addAction( aUp, 0 );
    
    // go to action
    QAction* aGoTo = new QAction( tr( "Select a root folder" ), this );
    aGoTo->setIcon( pIconManager::icon( "browser.png", ":/icons" ) );
    aGoTo->setToolTip( aGoTo->text() );
    titleBar()->addAction( aGoTo, 1 );
    
    // set current path action
    QAction* aRoot = new QAction( tr( "Set selected item as root" ), this );
    aRoot->setIcon( pIconManager::icon( "goto.png", ":/icons" ) );
    aRoot->setToolTip( aRoot->text() );
    titleBar()->addAction( aRoot, 2 );
    
    // add separator
    titleBar()->addSeparator( 3 );
    
    // add bookmark
    QAction* aAdd = new QAction( tr( "Add the current selected folder to bookmarks" ), this );
    aAdd->setIcon( pIconManager::icon( "add.png" ) );
    aAdd->setToolTip( aAdd->text() );
    titleBar()->addAction( aAdd, 4 );
    
    // remove bookmark
    QAction* aRemove = new QAction( tr( "Remove the current selected folder from bookmarks" ), this );
    aRemove->setIcon( pIconManager::icon( "remove.png" ) );
    aRemove->setToolTip( aRemove->text() );
    titleBar()->addAction( aRemove, 5 );
    
    // bookmarks menu
    mBookmarksMenu = new QMenu( this );
    QAction* aBookmarks = new QAction( tr( "Bookmarks..." ), this );
    aBookmarks->setIcon( pIconManager::icon( "bookmark.png" ) );
    aBookmarks->setToolTip( aBookmarks->text() );
    QToolButton* tb = qobject_cast<QToolButton*>( titleBar()->addAction( aBookmarks, 6 ) );
    tb->setPopupMode( QToolButton::InstantPopup );
    aBookmarks->setMenu( mBookmarksMenu );
    
    // add separator
    titleBar()->addSeparator( 7 );

    // central widget
    QWidget* wdg = new QWidget( this );
    setWidget( wdg );
    
    // vertical layout
    QVBoxLayout* vl = new QVBoxLayout( wdg );
    vl->setMargin( 5 );
    vl->setSpacing( 3 );
    
    // lineedit
    mLineEdit = new QLineEdit;
    mLineEdit->setAttribute( Qt::WA_MacShowFocusRect, false );
    mLineEdit->setAttribute( Qt::WA_MacSmallSize );
    mLineEdit->setReadOnly( true );
    vl->addWidget( mLineEdit );
    
    // hline
    QFrame* hline = new QFrame( this );
    hline->setFrameStyle( QFrame::HLine | QFrame::Sunken );
    vl->addWidget( hline );
    
    // dir model
    mDirsModel = new QFileSystemModel( this );
    mDirsModel->setNameFilterDisables( false );
    mDirsModel->setFilter( QDir::AllDirs | QDir::AllEntries | QDir::CaseSensitive | QDir::NoDotAndDotDot );
    
    // create proxy model
    mFilteredModel = new FileBrowserFilteredModel( this );
    mFilteredModel->setSourceModel( mDirsModel );
    
    // files view
    mTree = new QTreeView;
    mTree->setAttribute( Qt::WA_MacShowFocusRect, false );
    mTree->setAttribute( Qt::WA_MacSmallSize );
    mTree->setContextMenuPolicy( Qt::ActionsContextMenu );
    mTree->setHeaderHidden( true );
    mTree->setUniformRowHeights( true );
    vl->addWidget( mTree );
    
    // assign model to views
    mTree->setModel( mFilteredModel );
    
    // set root index
#ifndef Q_OS_WIN
    mDirsModel->setRootPath( "/" );
#else
    mDirsModel->setRootPath( QString::null );
#endif
    
    // set lineedit path
    setCurrentPath( mDirsModel->filePath( mDirsModel->index( 0, 0 ) ) );
    
    // redirirect focus proxy
    setFocusProxy( mTree );
    
    // set tree actions
    mTree->addAction( aUp );
    mTree->addAction( aGoTo );
    mTree->addAction( aRoot );
    mTree->addAction( aAdd );
    mTree->addAction( aRemove );
    mTree->addAction( aBookmarks );
    
    // shortcut accessible only when mTree has focus
    QShortcut* aUpShortcut = new QShortcut( QKeySequence( "BackSpace" ), mTree );
    aUpShortcut->setContext( Qt::WidgetShortcut );
    
    // connections
    connect( aUpShortcut, SIGNAL( activated() ), aUp, SIGNAL( triggered() ) );
    connect( aUp, SIGNAL( triggered() ), this, SLOT( aUp_triggered() ) );
    connect( aGoTo, SIGNAL( triggered() ), this, SLOT( aGoTo_triggered() ) );
    connect( aRoot, SIGNAL( triggered() ), this, SLOT( aRoot_triggered() ) );
    connect( aAdd, SIGNAL( triggered() ), this, SLOT( aAdd_triggered() ) );
    connect( aRemove, SIGNAL( triggered() ), this, SLOT( aRemove_triggered() ) );
    connect( mBookmarksMenu, SIGNAL( triggered( QAction* ) ), this, SLOT( bookmark_triggered( QAction* ) ) );
    connect( mTree, SIGNAL( activated( const QModelIndex& ) ), this, SLOT( tv_activated( const QModelIndex& ) ) );
    connect( mTree, SIGNAL( doubleClicked( const QModelIndex& ) ), this, SLOT( tv_doubleClicked( const QModelIndex& ) ) );
}

/*!
    Handler of click on Up button.

    Moves root of tree up one level
*/
void pDockFileBrowser::aUp_triggered()
{
    // cd up only if not the root index
    QModelIndex index = mTree->rootIndex();
    
    if ( !index.isValid() )
    {
        return;
    }
    
    index = index.parent();
    index = mFilteredModel->mapToSource( index );
    const QString path = mDirsModel->filePath( index );
    
#ifndef Q_OS_WIN
    if ( path.isEmpty() )
    {
        return;
    }
#endif
    
    setCurrentPath( path );
}

void pDockFileBrowser::aGoTo_triggered()
{
    QAction* action = qobject_cast<QAction*>( sender() );
    const QString path = QFileDialog::getExistingDirectory( window(), action->toolTip(), currentPath() );
    
    if ( !path.isEmpty() )
    {
        setCurrentPath( path );
    }
}

/*!
    Handler of click on Root button. 
    
    If there are selected dirrectory in the tree - it will be set as root
*/
void pDockFileBrowser::aRoot_triggered()
{
    // seet root of model to path of selected item
    QModelIndex index = mTree->selectionModel()->selectedIndexes().value( 0 );
    if ( !index.isValid() )
        return;
    index = mFilteredModel->mapToSource( index );
    if ( !mDirsModel->isDir( index ) )
        index = index.parent();
    setCurrentPath( mDirsModel->filePath( index ) );
}

void pDockFileBrowser::aAdd_triggered()
{
    const QString path = currentPath();
    
    if ( !mBookmarks.contains( path ) && !path.isEmpty() )
    {
        mBookmarks << path;
        updateBookmarks();
    }
}

void pDockFileBrowser::aRemove_triggered()
{
    const QString path = currentPath();
    
    if ( mBookmarks.contains( path ) )
    {
        mBookmarks.removeAll( path );
        updateBookmarks();
    }
}

void pDockFileBrowser::bookmark_triggered( QAction* action )
{
    setCurrentPath( action->data().toString() );
}

void pDockFileBrowser::tv_activated( const QModelIndex& idx )
{
    const QModelIndex index = mFilteredModel->mapToSource( idx );
    
    if ( mDirsModel->isDir( index ) )
    {
        setCurrentPath( mDirsModel->filePath( index ) );
    }
    else
    {
        MonkeyCore::fileManager()->openFile( mDirsModel->filePath( index ), pMonkeyStudio::defaultCodec() );
    }
}

/*!
    Handler of click on item in the tree
    
    If there are file doubleclicked - it will be opened
    \param idx Index of clicked tree
*/
void pDockFileBrowser::tv_doubleClicked( const QModelIndex& idx )
{
    // open file corresponding to index
    const QModelIndex index = mFilteredModel->mapToSource( idx );
    
    if ( !mDirsModel->isDir( index ) )
    {
        MonkeyCore::fileManager()->openFile( mDirsModel->filePath( index ), pMonkeyStudio::defaultCodec() );
    }
}

/*!
    Get current path (root of the tree)
    \return Current path (root of the tree)
*/
QString pDockFileBrowser::currentPath() const
{
    QModelIndex index = mTree->rootIndex();
    index = mFilteredModel->mapToSource( index );
    return mDirsModel->filePath( index );
}

/*!
    Set current path (root of the tree)
    \param s New path
*/
void pDockFileBrowser::setCurrentPath( const QString& s )
{
    // get index
    QModelIndex index = mDirsModel->index( s );
    // set current path
    mFilteredModel->invalidate();
    mTree->setRootIndex( mFilteredModel->mapFromSource( index ) );
    // set lineedit path
    mLineEdit->setText( mDirsModel->filePath( index ) );
    mLineEdit->setToolTip( mLineEdit->text() );
}

/*!
    Get current file path (selected item)
    \return Current file path (selected item)
*/
QString pDockFileBrowser::currentFilePath() const
{
    QModelIndex index = mTree->selectionModel()->selectedIndexes().value( 0 );
    index = mFilteredModel->mapToSource( index );
    return mDirsModel->filePath( index );
}

/*!
    Set current file path (selected item)
    \param s New file path
*/
void pDockFileBrowser::setCurrentFilePath( const QString& s )
{
    // get index
    QModelIndex index = mDirsModel->index( s );
    index = mFilteredModel->mapFromSource( index );
    mTree->setCurrentIndex( index );
}

/*!
    Get filter wildcards, which currently using for filtering out unneeded file
    names from tree
    \return List if wildcards for filtering
*/
QStringList pDockFileBrowser::filters() const
{
    return mFilteredModel->filters();
}

/*!
    Set filter wildcards for filtering out unneeded files
    \param filters List of wildcards
*/
void pDockFileBrowser::setFilters( const QStringList& filters )
{
    mFilteredModel->setFilters( filters );
}

QStringList pDockFileBrowser::bookmarks() const
{
    return mBookmarks;
}

void pDockFileBrowser::setBookmarks( const QStringList& bookmarks )
{
    if ( mBookmarks == bookmarks )
    {
        return;
    }
    
    mBookmarks = bookmarks;
    updateBookmarks();
}

void pDockFileBrowser::updateBookmarks()
{
    mBookmarksMenu->clear();
    
    foreach ( const QString& path, mBookmarks )
    {
        QAction* action = mBookmarksMenu->addAction( QDir( path ).dirName() );
        action->setToolTip( path );
        action->setStatusTip( path );
        action->setData( path );
    }
}