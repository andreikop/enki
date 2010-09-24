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
#include "pActionsShortcutsManager.h"
#include "pActionsManager.h"
#include "pKeySequenceInput.h"

#include <QGridLayout>
#include <QTreeWidget>
#include <QHeaderView>
#include <QPushButton>
#include <QMessageBox>
#include <QSettings>
#include <QLabel>

#include <QDebug>

pActionsShortcutsManager::pActionsShortcutsManager( pActionsManager* manager, QWidget* parent )
	: QDialog( parent )
{
	Q_ASSERT( manager );
	mManager = manager;
	setWindowTitle( tr( "Shortcuts Editor" ) );
	
	QLabel* lFilter = new QLabel( tr( "Action filter:" ), this );
	
	leFilter = new QLineEdit( this );
	leFilter->setObjectName( "leFilter" );

	twShortcuts = new QTreeWidget( this );
	twShortcuts->setObjectName( "twShortcuts" );
	twShortcuts->setColumnCount( 2 );	
	twShortcuts->setHeaderLabels( QStringList() << tr( "Action" ) << tr( "Shortcut" ) );
	twShortcuts->header()->setResizeMode( QHeaderView::ResizeToContents );
	//twShortcuts->setHeaderHidden( true );
	twShortcuts->setRootIsDecorated( false );
	twShortcuts->setItemsExpandable( false );
	twShortcuts->setAlternatingRowColors( true );
	twShortcuts->setUniformRowHeights( true );

	pbRestore = new QPushButton( tr( "Restore default" ), this );
	pbRestore->setObjectName( "pbRestore" );
	pbRestore->setEnabled( false );

	pbClear = new QPushButton( tr( "Clear" ), this );
	pbClear->setObjectName( "pbClear" );
	pbClear->setEnabled( false );

	leShortcut = new pKeySequenceInput( this );
	leShortcut->setObjectName( "leShortcut" );
	leShortcut->setEnabled( false );

	pbSet = new QPushButton( tr( "Set" ), this );
	pbSet->setObjectName( "pbSet" );
	pbSet->setEnabled( false );

	pbClose = new QPushButton( tr( "Close" ), this );
	pbClose->setObjectName( "pbClose" );

	// filter layout
	QHBoxLayout* hlFilter = new QHBoxLayout;
	hlFilter->setMargin( 0 );
	hlFilter->setSpacing( 3 );
	
	hlFilter->addWidget( lFilter );
	hlFilter->addWidget( leFilter );
	
	// shortcut layout
	QHBoxLayout* hlShortcut = new QHBoxLayout;
	hlShortcut->setMargin( 0 );
	hlShortcut->setSpacing( 3 );
	
	hlShortcut->addWidget( leShortcut );
	hlShortcut->addWidget( pbSet );
	hlShortcut->addWidget( pbClear );
	
	// buttons layout
	QHBoxLayout* hlButtons = new QHBoxLayout;
	hlButtons->setMargin( 0 );
	hlButtons->setSpacing( 3 );
	
	hlButtons->addWidget( pbRestore );
	hlButtons->addStretch( 100 );
	hlButtons->addWidget( pbClose );
	
	// global layout
	QVBoxLayout* vlLayout = new QVBoxLayout( this );
	vlLayout->setMargin( 5 );
	vlLayout->setSpacing( 3 );
	
	vlLayout->addLayout( hlFilter );
	vlLayout->addWidget( twShortcuts );
	vlLayout->addLayout( hlShortcut );
	vlLayout->addLayout( hlButtons );
	
	// create items
	QPalette pal = twShortcuts->viewport()->palette();
	
	foreach ( QAction* action, mManager->actions() )
	{
		const QString mPath = mManager->pathTranslation( action );
		QTreeWidgetItem* pathItem = mItems.value( mPath );
		
		if ( !pathItem )
		{
			pathItem = new QTreeWidgetItem( twShortcuts );
			pathItem->setFirstColumnSpanned( true );
			pathItem->setFlags( pathItem->flags() ^ Qt::ItemIsSelectable );
			pathItem->setTextAlignment( 0, Qt::AlignCenter );
			pathItem->setText( 0, strippedText( mPath ) );
			pathItem->setBackground( 0, pal.mid() );
			pathItem->setForeground( 0, pal.text().color().lighter( 400 ) );
			
			mItems[ mPath ] = pathItem;
		}
		
		if ( action->isSeparator() )
		{
			continue;
		}
		
		QTreeWidgetItem* item = new QTreeWidgetItem( pathItem );
		item->setIcon( 0, action->icon() );
		item->setText( 0, strippedText( action->text() ) );
		item->setData( 0, Qt::UserRole, QVariant::fromValue( action ) );
		item->setTextAlignment( 1, Qt::AlignVCenter | Qt::AlignRight );
		item->setText( 1, action->shortcut().toString() );
	}
	
	twShortcuts->sortItems( 0, Qt::AscendingOrder );
	twShortcuts->expandAll();

	// connections
	connect( pbClear, SIGNAL( clicked() ), leShortcut, SLOT( clear() ) );
	connect( pbRestore, SIGNAL( clicked() ), this, SLOT( pbRestore_pbSet_clicked() ) );
	connect( pbSet, SIGNAL( clicked() ), this, SLOT( pbRestore_pbSet_clicked() ) );
	connect( pbClose, SIGNAL( clicked() ), this, SLOT( close() ) );
	QMetaObject::connectSlotsByName( this );
}

QSize pActionsShortcutsManager::sizeHint() const
{
	return QSize( 640, 480 );
}

QString pActionsShortcutsManager::strippedText( const QString& text )
{
	const QString tag = "***|MkS|***";
	QString s = text;
	
	s.replace( "&&", tag );
	s.replace( "&", QString::null );
	s.replace( tag, "&&" );
	
	return s;
}

void pActionsShortcutsManager::on_leFilter_textChanged( const QString& text )
{
	foreach ( QTreeWidgetItem* pathItem, mItems.values() )
	{
		for ( int i = 0; i < pathItem->childCount(); i++ )
		{
			QTreeWidgetItem* item = pathItem->child( i );
			item->setHidden( !item->text( 0 ).contains( text, Qt::CaseInsensitive ) );
		}
	}
}

void pActionsShortcutsManager::on_twShortcuts_itemSelectionChanged()
{
	// get selected item
	QTreeWidgetItem* item = twShortcuts->selectedItems().value( 0 );
	
	// get action
	QAction* action = item ? item->data( 0, Qt::UserRole ).value<QAction*>() : 0;

	// set button state according to item is an action
	pbRestore->setEnabled( action );
	pbClear->setEnabled( action );
	leShortcut->setEnabled( action );
	leShortcut->clear();
	pbSet->setEnabled( action );

	// return if no action
	if ( !action )
	{
		return;
	}

	// set shortcut
	leShortcut->setText( action->shortcut().toString() );

	// give focus to lineedit
	leShortcut->setFocus();
}

void pActionsShortcutsManager::pbRestore_pbSet_clicked()
{
	// get selected item
	QTreeWidgetItem* item = twShortcuts->selectedItems().value( 0 );

	// get action
	QAction* action = item ? item->data( 0, Qt::UserRole ).value<QAction*>() : 0;

	if ( action )
	{
		// get default action shortcut
		QString shortcut = sender() == pbRestore ? mManager->defaultShortcut( action ).toString() : leShortcut->text();
		
		// try asigning new shortcut
		if ( pActionsManager::setShortcut( action, QKeySequence( shortcut ) ) )
		{
			item->setText( 1, shortcut );
			leShortcut->setText( shortcut );
			pbSet->setEnabled( false );
		}
		// show warning
		else
		{
			QMessageBox::warning( window(), tr( "Error" ), strippedText( mManager->lastError() ), QMessageBox::Close );
			leShortcut->setText( action->shortcut().toString() );
		}
	}
}

void pActionsShortcutsManager::on_leShortcut_textChanged( const QString& )
{
	pbSet->setEnabled( true );
}
