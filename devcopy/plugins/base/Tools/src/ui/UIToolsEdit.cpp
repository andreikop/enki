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
#include "UIToolsEdit.h"
#include "ToolsManager.h"

#include <pMonkeyStudio.h>

#include <QMessageBox>
#include <QCloseEvent>
#include <QFileInfo>
#include <QUrl>
#include <QWhatsThis>

UIToolsEdit::UIToolsEdit( ToolsManager* manager, QWidget* parent )
    : QDialog( parent )
{
    Q_ASSERT( manager );
    mToolsManager = manager;
    
    // init dialog
    setupUi( this );
    setAttribute( Qt::WA_DeleteOnClose );
    
    // event filters
    leCaption->installEventFilter( this );
    tbFileIcon->installEventFilter( this );
    leFilePath->installEventFilter( this );
    leWorkingPath->installEventFilter( this );
    
    // create items
    foreach ( const ToolsManager::Tool& tool, mToolsManager->tools( ToolsManager::UserEntry ) ) {
        // create item
        QListWidgetItem* item = new QListWidgetItem( ToolsManager::icon( tool.fileIcon ), tool.caption, lwTools );
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
    }
    
    // modified state
    setWindowModified( false );
    
    // connection
    connect( dbbButtons, SIGNAL( helpRequested() ), this, SLOT( helpRequested() ) );
}

void UIToolsEdit::closeEvent( QCloseEvent* event )
{
    // ask user confirmation if we have pending modification
    if ( isWindowModified()
        && QMessageBox::question( QApplication::activeWindow(), QString::null, tr( "You're about to discard all changes. Are you sure ?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::No ) == QMessageBox::No ) {
            event->ignore();
            return;
    }
    
    QDialog::closeEvent( event );
}

bool UIToolsEdit::eventFilter( QObject* object, QEvent* event )
{
    // accept drag enter event
    if ( event->type() == QEvent::DragEnter ) {
        event->accept();
    }
    
    // got the event as drop event
    QDropEvent* de = static_cast<QDropEvent*>( event );
    
    // if not a drop event or has urls, return
    if ( event->type() != QEvent::Drop || !de->mimeData()->hasUrls() ) {
        return QDialog::eventFilter( object, event );
    }
    
    // if there is no current item selected, ask to create one
    QListWidgetItem* item = lwTools->selectedItems().value( 0 );
    
    if ( !item ) {
        const QMessageBox::StandardButton button = QMessageBox::question( this, QString::null, tr( "There is no current tool, do you want to add a new one ?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::No );
        
        // filter the even to avoid default drop event
        if ( button == QMessageBox::No ) {
            return true;
        }
        
        item = new QListWidgetItem( tr( "new Tool" ), lwTools );
    }
    
    // get link info
    QFileInfo fi( de->mimeData()->urls().at( 0 ).toLocalFile() );
    
    // drag for tbFileIcon
    ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
    
    if ( tool.caption.isEmpty() ) {
        tool.caption = item->text();
    }
    
    if ( object == tbFileIcon ) {
        if ( fi.isFile() ) {
            tool.fileIcon = fi.absoluteFilePath();
        }
    }
    // others
    else {
        if ( fi.isFile() ) {
            tool.caption = fi.baseName();
            tool.filePath = fi.absoluteFilePath();
            tool.workingPath = fi.absolutePath();
        }
        else if ( fi.isDir() ) {
            tool.workingPath = fi.absoluteFilePath();
        }
    }
    
    // update item data
    item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
    updateGui( item, true );
    
    // modified state
    setWindowModified( true );
    
    // we finish
    return QDialog::eventFilter( object, event );
}

void UIToolsEdit::updateGui( QListWidgetItem* item, bool makeCurrent )
{
    const ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
    
    item->setText( tool.caption );
    item->setIcon( ToolsManager::icon( tool.fileIcon ) );
    leCaption->setText( tool.caption );
    tbFileIcon->setIcon( item->icon() );
    leFilePath->setText( tool.filePath );
    leWorkingPath->setText( tool.workingPath );
    cbUseConsoleManager->setChecked( tool.useConsoleManager );
    
    if ( makeCurrent ) {
        lwTools->clearSelection();
        lwTools->setCurrentItem( item );
        item->setSelected( true );
    }
}

void UIToolsEdit::on_lwTools_itemSelectionChanged()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        updateGui( item );
    }
}

void UIToolsEdit::on_aNew_triggered()
{
    QListWidgetItem* item = new QListWidgetItem( tr( "new Tool" ), lwTools );
    ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
    tool.caption = item->text();
    item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
    updateGui( item, true );
    
    // modified state
    setWindowModified( true );
}

void UIToolsEdit::on_aDelete_triggered()
{
    delete lwTools->selectedItems().value( 0 );
    
    if ( lwTools->count() ) {
        updateGui( lwTools->item( 0 ), true );
    }
    
    // modified state
    setWindowModified( true );
}

void UIToolsEdit::on_aUp_triggered()
{
    QListWidgetItem* item = lwTools->selectedItems().value( 0 );
    
    if ( !item || lwTools->row( item ) == 0 ) {
        return;
    }
    
    const int row = lwTools->row( item );
    item = lwTools->takeItem( row );
    lwTools->insertItem( row -1, item );
    lwTools->setCurrentRow( row -1 );
    
    // modified state
    setWindowModified( true );
}

void UIToolsEdit::on_aDown_triggered()
{
    QListWidgetItem* item = lwTools->selectedItems().value( 0 );
    
    if ( !item || lwTools->row( item ) == lwTools->count() -1 ) {
        return;
    }
    
    const int row = lwTools->row( item );
    item = lwTools->takeItem( row );
    lwTools->insertItem( row +1, item );
    lwTools->setCurrentRow( row +1 );
    
    // modified state
    setWindowModified( true );
}

void UIToolsEdit::helpRequested()
{
    QString help = tr( "<b>Tools Editor</b> give you the possibility to use variables<br><br>"
        "<b>$cpp$</b> : Current project path<br>"
        "<b>$cp$</b> : Current project filepath<br>"
        "<b>$cfp$</b> : Current tab path<br>"
        "<b>$cf$</b> : Current tab filepath<br>"
        "<b>$cip$</b> : Current item path<br>"
        "<b>$ci$</b> : Current item filepath" );
    
    QWhatsThis::showText( mapToGlobal( rect().center() ), help );
}

void UIToolsEdit::on_leCaption_editingFinished()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
        tool.caption = leCaption->text();
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
        updateGui( item );
        
        // modified state
        setWindowModified( true );
    }
}

void UIToolsEdit::on_tbFileIcon_clicked()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
        const QString fn = pMonkeyStudio::getImageFileName( tr( "Choose an icon for this tool" ), tool.fileIcon, this );
        
        if ( fn.isEmpty() ) {
            return;
        }
        
        tool.fileIcon = fn;
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
        updateGui( item );
        
        // modified state
        setWindowModified( true );
    }
}

void UIToolsEdit::on_leFilePath_editingFinished()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
        tool.filePath = leFilePath->text();
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
        updateGui( item );
        
        // modified state
        setWindowModified( true );
    }
}

void UIToolsEdit::on_tbFilePath_clicked()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
        const QString fn = pMonkeyStudio::getOpenFileName( tr( "Choose the file to execute for this tool" ), tool.filePath, QString::null, this );
        
        if ( fn.isEmpty() ) {
            return;
        }
        
        tool.filePath = fn;
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
        updateGui( item );
        leFilePath->setFocus();
        
        // modified state
        setWindowModified( true );
    }
}

void UIToolsEdit::on_tbUpdateWorkingPath_clicked()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        const QFileInfo fi( leFilePath->text() );
        
        if ( fi.exists() && fi.absolutePath() != leWorkingPath->text() ) {
            ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
            tool.workingPath = fi.absolutePath();
            item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
            updateGui( item );
            leWorkingPath->setFocus();
            
            // modified state
            setWindowModified( true );
        }
    }
}

void UIToolsEdit::on_leWorkingPath_editingFinished()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
        tool.workingPath = leWorkingPath->text();
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
        updateGui( item );
        
        // modified state
        setWindowModified( true );
    }
}

void UIToolsEdit::on_tbWorkingPath_clicked()
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
        const QString path = pMonkeyStudio::getExistingDirectory( tr( "Choose the working path for this tool" ), tool.workingPath, this );
        
        if ( path.isEmpty() ) {
            return;
        }
        
        tool.workingPath = path;
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
        updateGui( item );
        leWorkingPath->setFocus();
        
        // modified state
        setWindowModified( true );
    }
}

void UIToolsEdit::on_cbUseConsoleManager_clicked( bool clicked )
{
    if ( QListWidgetItem* item = lwTools->selectedItems().value( 0 ) ) {
        ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
        tool.useConsoleManager = clicked;
        item->setData( Qt::UserRole, QVariant::fromValue( tool ) );
        updateGui( item );
        
        // modified state
        setWindowModified( true );
    }
}

void UIToolsEdit::accept()
{
    if ( isWindowModified() )
    {
        ToolsManager::Tools tools = mToolsManager->tools( ToolsManager::DesktopEntry );
        
        for ( int i = 0; i < lwTools->count(); i++ ) {
            QListWidgetItem* item = lwTools->item( i );
            const ToolsManager::Tool tool = item->data( Qt::UserRole ).value<ToolsManager::Tool>();
            tools << tool;
        }
        
        mToolsManager->mTools = tools;
        mToolsManager->updateMenuActions();
        mToolsManager->writeTools( tools );
    }
    
    // close dialog
    QDialog::accept();
}
