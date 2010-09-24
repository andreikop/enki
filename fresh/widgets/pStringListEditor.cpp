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
**
****************************************************************************/
#include "pStringListEditor.h"

#include <QVBoxLayout>
#include <QToolBar>
#include <QAction>
#include <QListWidget>

/*!
	\details Create a new pStringListEditor instance
	\param parent The parent widget
	\param title The editor title
*/
pStringListEditor::pStringListEditor( QWidget* parent, const QString& title )
	: QGroupBox( title, parent )
{
	// create layout
	mLayout = new QVBoxLayout( this );
	mLayout->setMargin( 5 );
	mLayout->setSpacing( 3 );
	
	// create toolbar
	QToolBar* tb = new QToolBar;
	tb->layout()->setMargin( 0 );
	tb->layout()->setSpacing( 0 );
	tb->setIconSize( QSize( 16, 16 ) );
	mLayout->addWidget( tb );

	
	// create listwidget
	mList = new QListWidget;
	mList->setMinimumHeight( 40 );
	mList->setHorizontalScrollBarPolicy( Qt::ScrollBarAlwaysOff );
	mLayout->addWidget( mList );
	
	// create actions
	QAction* aAdd = new QAction( QIcon( ":/listeditor/icons/listeditor/add.png" ), tr( "Add Item" ), tb );
	QAction* aRemove = new QAction( QIcon( ":/listeditor/icons/listeditor/remove.png" ), tr( "Remove Item" ), tb );
	QAction* aClear = new QAction( QIcon( ":/listeditor/icons/listeditor/clear.png" ), tr( "Clear Items" ), tb );
	QAction* aUp = new QAction( QIcon( ":/listeditor/icons/listeditor/up.png" ), tr( "Move Item Up" ), tb );
	QAction* aDown = new QAction( QIcon( ":/listeditor/icons/listeditor/down.png" ), tr( "Move Item Down" ), tb );
	QAction* aEdit = new QAction( QIcon( ":/listeditor/icons/listeditor/edit.png" ), tr( "Edit Item" ), tb );
	
	// add actions to toolbar
	tb->addAction( aAdd );
	tb->addAction( aRemove );
	tb->addAction( aClear );
	tb->addAction( aUp );
	tb->addAction( aDown );
	tb->addAction( aEdit );
	
	// connections
	connect( aAdd, SIGNAL( triggered() ), this, SLOT( onAddItem() ) );
	connect( aRemove, SIGNAL( triggered() ), this, SLOT( onRemoveItem() ) );
	connect( aClear, SIGNAL( triggered() ), this, SLOT( onClearItem() ) );
	connect( aUp, SIGNAL( triggered() ), this, SLOT( onMoveUpItem() ) );
	connect( aDown, SIGNAL( triggered() ), this, SLOT( onMoveDownItem() ) );
	connect( aEdit, SIGNAL( triggered() ), this, SLOT( onEditItem() ) );
	connect( mList, SIGNAL( itemChanged( QListWidgetItem* ) ), this, SIGNAL( edited() ) );
	connect( this, SIGNAL( edited() ), this, SLOT( onEdited() ) );
}

QVBoxLayout* pStringListEditor::verticalLayout() const
{
	return mLayout;
}

/*!
	\details Set the editor values
	\param values The string list to set as values
*/
void pStringListEditor::setValues( const QStringList& values )
{
	mList->clear();
	foreach ( QString value, values )
	{
		QListWidgetItem* it = new QListWidgetItem( value, mList );
		it->setFlags( it->flags() | Qt::ItemIsEditable );
		mList->setCurrentItem( it );
		mList->scrollToItem( it );
	}
	emit edited();
}

/*!
	\details Return the editor QStringList values
*/
QStringList pStringListEditor::values() const
{
	QStringList values;
	foreach ( QListWidgetItem* it, mList->findItems( "*", Qt::MatchWildcard | Qt::MatchRecursive ) )
		values << it->text();
	return values;
}

void pStringListEditor::onEdited()
{
	for ( int i = 0; i < mList->count(); i++ )
	{
		QListWidgetItem* item = mList->item( i );
		item->setToolTip( item->text() );
	}
}

void pStringListEditor::onAddItem()
{
	QListWidgetItem* it = new QListWidgetItem( tr( "New item" ), mList );
	it->setFlags( it->flags() | Qt::ItemIsEditable );
	mList->setCurrentItem( it );
	mList->scrollToItem( it );
	mList->editItem( it );
	emit edited();
}

void pStringListEditor::onRemoveItem()
{
	if ( QListWidgetItem* it = mList->selectedItems().value( 0 ) )
	{
		delete it;
		emit edited();
	}
}

void pStringListEditor::onClearItem()
{
	if ( mList->count() )
	{
		mList->clear();
		emit edited();
	}
}

void pStringListEditor::onMoveUpItem()
{
	if ( QListWidgetItem* it = mList->selectedItems().value( 0 ) )
	{
		int i = mList->row( it );
		if ( i != 0 )
			mList->insertItem( i -1, mList->takeItem( i ) );
		mList->setCurrentItem( it );
		emit edited();
	}
}

void pStringListEditor::onMoveDownItem()
{
	if ( QListWidgetItem* it = mList->selectedItems().value( 0 ) )
	{
		int i = mList->row( it );
		if ( i != mList->count() -1 )
			mList->insertItem( i +1, mList->takeItem( i ) );
		mList->setCurrentItem( it );
		emit edited();
	}
}

void pStringListEditor::onEditItem()
{
	if ( QListWidgetItem* it = mList->selectedItems().value( 0 ) )
		mList->editItem( it );
}
