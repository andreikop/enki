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
#ifndef UITOOLSEDIT_H
#define UITOOLSEDIT_H

#include "ui_UIToolsEdit.h"

class ToolsManager;

class UIToolsEdit : public QDialog, public Ui::UIToolsEdit
{
	Q_OBJECT

public:
	UIToolsEdit( ToolsManager* manager, QWidget* parent = 0 );

protected:
	ToolsManager* mToolsManager;
	
	virtual void closeEvent( QCloseEvent* event );
	virtual bool eventFilter( QObject* object, QEvent* event );
	void updateGui( QListWidgetItem* item, bool makeCurrent = false );

protected slots:
	void on_aNew_triggered();
	void on_aDelete_triggered();
	void on_aUp_triggered();
	void on_aDown_triggered();
	void on_lwTools_itemSelectionChanged();
	void on_leCaption_editingFinished();
	void on_tbFileIcon_clicked();
	void on_leFilePath_editingFinished();
	void on_tbFilePath_clicked();
	void on_tbUpdateWorkingPath_clicked();
	void on_leWorkingPath_editingFinished();
	void on_tbWorkingPath_clicked();
	void on_cbUseConsoleManager_clicked( bool toggled );
	void helpRequested();
	virtual void accept();
};

#endif // UITOOLSEDIT_H
