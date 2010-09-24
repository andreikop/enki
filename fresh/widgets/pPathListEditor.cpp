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
#include "pPathListEditor.h"

#include <QToolBar>
#include <QAction>
#include <QFileDialog>
#include <QListWidgetItem>

/*!
	\details Create a new pPathListEditor instance
	\param parent The parent widget
	\param title The editor title
	\param  path The editor path
*/
pPathListEditor::pPathListEditor( QWidget* parent, const QString& title, const QString& path ):
	pFileListEditor( parent, title, path, QString() )
{ findChild<QToolBar*>()->actions().last()->setIcon( QIcon( ":/listeditor/icons/listeditor/folder.png" ) ); }

void pPathListEditor::onAddItem()
{
	// get directory
	QString s = QFileDialog::getExistingDirectory( window(), tr( "Choose directory" ), mPath );
	
	if ( !s.isEmpty() )
	{
		QListWidgetItem* it = new QListWidgetItem( s, mList );
		it->setFlags( it->flags() | Qt::ItemIsEditable );
		mList->setCurrentItem( it );
		mList->scrollToItem( it );
		emit edited();
	}
}

void pPathListEditor::onEditItem()
{
	if ( QListWidgetItem* it = mList->selectedItems().value( 0 ) )
	{
		QString s= QFileDialog::getExistingDirectory( window(), tr( "Choose directory" ), mPath );
		if ( !s.isEmpty() )
		{
			it->setText( s );
			emit edited();
		}
	}
}
