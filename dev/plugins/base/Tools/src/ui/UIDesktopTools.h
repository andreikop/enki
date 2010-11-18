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
#ifndef UIDesktopTools_H
#define UIDesktopTools_H

#include "ui_UIDesktopTools.h"

class ToolsManager;
class DesktopApplications;
class DesktopFolder;
class QTreeWidgetItem;

class UIDesktopTools : public QDialog, public Ui::UIDesktopTools
{
	Q_OBJECT

public:
	UIDesktopTools( ToolsManager* manager, QWidget* parent = 0 );
	~UIDesktopTools();

protected:
	ToolsManager* mToolsManager;
	DesktopApplications* mStartMenu;
	QSet<QString> mApplications;
	bool mShown;

	void showEvent( QShowEvent* event );
	void closeEvent( QCloseEvent* event );
	void applyFilters();

protected slots:
	void populateTree( QTreeWidgetItem* item, DesktopFolder* folder );
	void scanApplications();
	void on_leNameFilter_textChanged( const QString& text );
	void on_leCategoriesFilters_textChanged( const QString& text );
	void on_tbRight_clicked();
	void on_tbLeft_clicked();
	void on_tbUp_clicked();
	void on_tbDown_clicked();
	virtual void accept();
};

#endif // UIDesktopTools_H
