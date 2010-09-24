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
#ifndef PACTIONSSHORTCUTSMANAGER_H
#define PACTIONSSHORTCUTSMANAGER_H

#include "objects/MonkeyExport.h"

#include <QDialog>
#include <QMap>

class pActionsManager;
class QTreeWidget;
class QTreeWidgetItem;
class QPushButton;
class QLineEdit;

class Q_MONKEY_EXPORT pActionsShortcutsManager : public QDialog
{
	Q_OBJECT

public:
	pActionsShortcutsManager( pActionsManager* manager, QWidget* parent = 0 );
	
	virtual QSize sizeHint() const;
	static QString strippedText( const QString& text );

protected:
	QMap<QString, QTreeWidgetItem*> mItems;
	QLineEdit* leFilter;
	QTreeWidget* twShortcuts;
	QPushButton* pbRestore;
	QPushButton* pbClear;
	QLineEdit* leShortcut;
	QPushButton* pbSet;
	QPushButton* pbClose;
	pActionsManager* mManager;

private slots:
	void on_leFilter_textChanged( const QString& text );
	void on_twShortcuts_itemSelectionChanged();
	void pbRestore_pbSet_clicked();
	void on_leShortcut_textChanged( const QString& text );
};

#endif // PACTIONSSHORTCUTSMANAGER_H
