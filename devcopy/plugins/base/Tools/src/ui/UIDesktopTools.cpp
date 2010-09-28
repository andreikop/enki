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
#include "UIDesktopTools.h"
#include "ToolsManager.h"
#include "DesktopApplications.h"

#include <pMonkeyStudio.h>
#include <coremanager/MonkeyCore.h>
#include <settingsmanager/Settings.h>

#include <QTimer>
#include <QCloseEvent>
#include <QMessageBox>
#include <QPushButton>
#include <QDebug>

Q_DECLARE_METATYPE( QTreeWidgetItem* )

UIDesktopTools::UIDesktopTools( ToolsManager* manager, QWidget* parent )
    : QDialog( parent )
{
    Q_ASSERT( manager );
    mToolsManager = manager;
    mStartMenu = new DesktopApplications( this );
    mShown = false;
    
    setupUi( this );
    setAttribute( Qt::WA_DeleteOnClose );
    pbLoading->setVisible( false );
    
    if ( !mStartMenu->categoriesAvailable() )
    {
        lCategoriesFilters->hide();
        leCategoriesFilters->hide();
    }
    
    // connection
    connect( twLeft, SIGNAL( itemDoubleClicked( QTreeWidgetItem*, int ) ), this, SLOT( on_tbRight_clicked() ) );
    connect( lwRight, SIGNAL( itemDoubleClicked( QListWidgetItem* ) ), this, SLOT( on_tbLeft_clicked() ) );
}

UIDesktopTools::~UIDesktopTools()
{
}

void UIDesktopTools::showEvent( QShowEvent* event )
{
    QDialog::showEvent( event );
    
    if ( !mShown ) {
        mShown = true;
        QTimer::singleShot( 100, this, SLOT( scanApplications() ) );
    }
}

void UIDesktopTools::closeEvent( QCloseEvent* event )
{
    if ( isWindowModified()
        && QMessageBox::question( this, QString::null, tr( "You're about to discard all changes. Are you sure ?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::No ) == QMessageBox::No ) {
        event->ignore();
        return;
    }
    
    QDialog::closeEvent( event );
}

void UIDesktopTools::applyFilters()
{
    const QList<QTreeWidgetItem*> items = twLeft->findItems( "*", Qt::MatchWildcard | Qt::MatchRecursive );
    const QString nameFilter = leNameFilter->text();
    const QStringList categoriesFilter = leCategoriesFilters->text().split( ";", QString::SkipEmptyParts );
    
    foreach ( QTreeWidgetItem* item, items ) {
        DesktopApplication* da = item->data( 0, Qt::UserRole ).value<DesktopApplication*>();
        
        if ( !da || mApplications.contains( da->parent->applications.key( *da ) ) ) {
            continue;
        }
        
        // validate name filter
        const bool nameFilterMatch = !nameFilter.isEmpty() && item->text( 0 ).contains( nameFilter, Qt::CaseInsensitive );
        bool visible = nameFilter.isEmpty() || nameFilterMatch;
        
        // validate categories filter
        if ( visible ) {
            bool categoriesFilterMatch = false;
            
            foreach ( const QString& filter, categoriesFilter ) {
                if ( da->categories.contains( filter, Qt::CaseInsensitive ) ) {
                    categoriesFilterMatch = true;
                    break;
                }
            }
            
            visible = categoriesFilter.isEmpty() || categoriesFilterMatch;
        }
        
        // set item visibility
        item->setHidden( !visible );
    }
}

void UIDesktopTools::populateTree( QTreeWidgetItem* _item, DesktopFolder* folder )
{
    Q_ASSERT( folder );
    
    // Folders
    foreach ( const QString& folderName, folder->folders.keys() ) {
        DesktopFolder* df = &folder->folders[ folderName ];
        QTreeWidgetItem* item = 0;
        
        if ( _item ) {
            item = new QTreeWidgetItem( _item );
        }
        else {
            item = new QTreeWidgetItem( twLeft );
        }
        
        item->setText( 0, folderName );
        item->setIcon( 0, ToolsManager::icon( df->icon, df->path ) );
        item->setData( 0, Qt::UserRole, QVariant::fromValue( df ) );
        
        populateTree( item, df );
    }
    
    // Applications
    foreach ( const QString& fileName, folder->applications.keys() ) {
        DesktopApplication* da = &folder->applications[ fileName ];
        QTreeWidgetItem* item = 0;
        
        QApplication::processEvents( QEventLoop::ExcludeUserInputEvents );
        
        if ( _item ) {
            item = new QTreeWidgetItem( _item );
        }
        else {
            item = new QTreeWidgetItem( twLeft );
        }
        
        item->setText( 0, da->name );
        item->setIcon( 0, ToolsManager::icon( da->icon, fileName ) );
        item->setToolTip( 0, QString( "<b>%1</b><br />%2<br /><i>%3</i>" )
            .arg( da->genericName.isEmpty() ? da->name : da->genericName )
            .arg( da->comment.isEmpty() ? tr( "No available comment" ) : da->comment )
            .arg( da->categories.isEmpty() ? tr( "No available categories" ) : da->categories.join( ", " ).prepend( ' ' ).prepend( tr( "Categories:" ) ) )
            );
        
        item->setData( 0, Qt::UserRole, QVariant::fromValue( da ) );
        
        pbLoading->setValue( pbLoading->value() +1 );
    }
}

void UIDesktopTools::scanApplications()
{
    // show progressbar
    pbLoading->setVisible( true );
    // set temp progressbar for loading application
    pbLoading->setRange( 0, 0 );
    // populate applications
    mStartMenu->scan();
    // set progressbar range
    pbLoading->setRange( 0, mStartMenu->applicationCount() );
    // clear tree
    twLeft->clear();
    // disable update
    twLeft->setUpdatesEnabled( false );
    // populate tree
    populateTree( 0, mStartMenu->startMenu() );
    // enable update
    twLeft->setUpdatesEnabled( true );
    // hide progressbar
    pbLoading->setVisible( false );
    
    // restore selected applications
    foreach ( const ToolsManager::Tool& tool, mToolsManager->tools( ToolsManager::DesktopEntry ) ) {
        mApplications << tool.filePath;
    }
    
    foreach ( QTreeWidgetItem* item, twLeft->findItems( "*", Qt::MatchWildcard | Qt::MatchRecursive ) ) {
        DesktopApplication* da = item->data( 0, Qt::UserRole ).value<DesktopApplication*>();
        
        if ( !da ) {
            continue;
        }
        
        if ( mApplications.contains( da->parent->applications.key( *da ) ) ) {
            item->setSelected( true );
        }
    }
    
    // simulate click to add items to right
    tbRight->click();
    
    // modified state
    setWindowModified( false );
}

void UIDesktopTools::on_leNameFilter_textChanged( const QString& /*text*/ )
{
    applyFilters();
}

void UIDesktopTools::on_leCategoriesFilters_textChanged( const QString& /*text*/ )
{
    applyFilters();
}

void UIDesktopTools::on_tbRight_clicked()
{
    foreach ( QTreeWidgetItem* item, twLeft->selectedItems() ) {
        DesktopApplication* da = item->data( 0, Qt::UserRole ).value<DesktopApplication*>();
        
        if ( item->isHidden() || !da ) {
            continue;
        }
        
        QListWidgetItem* it = new QListWidgetItem( lwRight );
        it->setText( item->text( 0 ) );
        it->setIcon( item->icon( 0 ) );
        it->setToolTip( item->toolTip( 0 ) );
        it->setData( Qt::UserRole, QVariant::fromValue( da ) );
        it->setData( Qt::UserRole +1, QVariant::fromValue( item ) );
        item->setHidden( true );
        
        mApplications << da->parent->applications.key( *da );
        
        // modified state
        setWindowModified( true );
    }
}

void UIDesktopTools::on_tbLeft_clicked()
{
    foreach ( QListWidgetItem* item, lwRight->selectedItems() ) {
        DesktopApplication* da = item->data( Qt::UserRole ).value<DesktopApplication*>();
        QTreeWidgetItem* it = item->data( Qt::UserRole +1 ).value<QTreeWidgetItem*>();
        
        if ( it ) {
            mApplications.remove( da->parent->applications.key( *da ) );
            
            // modified state
            setWindowModified( true );
        }
        
        delete item;
    }
    
    // revalidate the filters
    if ( isWindowModified() ) {
        applyFilters();
    }
}

void UIDesktopTools::on_tbUp_clicked()
{
    if ( lwRight->selectedItems().count() > 1 ) {
        QMessageBox::warning( QApplication::activeWindow(), QString::null, tr( "Only one item can be move up, please select only one item." ) );
        return;
    }
    
    QListWidgetItem* item = lwRight->selectedItems().value( 0 );
    
    if ( !item || lwRight->row( item ) == 0 ) {
        return;
    }
    
    const int index = lwRight->row( item );
    item = lwRight->takeItem( index );
    lwRight->insertItem( index -1, item );
    lwRight->setCurrentRow( index -1 );
    
    // modified state
    setWindowModified( true );
}

void UIDesktopTools::on_tbDown_clicked()
{
    if ( lwRight->selectedItems().count() > 1 ) {
        QMessageBox::warning( QApplication::activeWindow(), QString::null, tr( "Only one item can be move down, please select only one item." ) );
        return;
    }
    
    QListWidgetItem* item = lwRight->selectedItems().value( 0 );
    
    if ( !item || lwRight->row( item ) == lwRight->count() -1 ) {
        return;
    }
    
    const int index = lwRight->row( item );
    item = lwRight->takeItem( index );
    lwRight->insertItem( index +1, item );
    lwRight->setCurrentRow( index +1 );
    
    // modified state
    setWindowModified( true );
}

void UIDesktopTools::accept()
{
    if ( isWindowModified() )
    {
        ToolsManager::Tools tools = mToolsManager->tools( ToolsManager::UserEntry );
        
        for ( int i = 0; i < lwRight->count(); i++ ) {
            QListWidgetItem* item = lwRight->item( i );
            DesktopApplication* da = item->data( Qt::UserRole ).value<DesktopApplication*>();
            ToolsManager::Tool tool;
            
            tool.caption = item->text();
            tool.fileIcon = da->icon;
            tool.filePath = da->parent->applications.key( *da );
            tool.workingPath = QString::null;
            tool.desktopEntry = true;
            tool.useConsoleManager = false;
            
            tools << tool;
        }
        
        mToolsManager->mTools = tools;
        mToolsManager->updateMenuActions();
        mToolsManager->writeTools( tools );
    }
    
    // close dialog
    QDialog::accept();
}
