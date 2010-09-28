/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : 
** Project   : Fresh Framework
** FileName  : 
** Date      : 
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
	\file pMainWindow.h
	\date 2008-01-14T00:27:46
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief An extended QMainWindow
*/
#ifndef PMAINWINDOW_H
#define PMAINWINDOW_H

#include "objects/MonkeyExport.h"

#include <QMainWindow>

class pMenuBar;
class pDockToolBarManager;
class pDockToolBar;
class pSettings;

/*!
	\brief An extended QMainWindow.
	\details This extended mainwindow contains some usefull features :
	\details a pMenuBar as menu bar, a pDockToolBarManager for tabbed management of docked widgets
	\details and a pSettings object for storing/reading your settings.
	\details There is also a confortable dockToolBar() member.
*/
class Q_MONKEY_EXPORT pMainWindow : public QMainWindow
{
	Q_OBJECT

public:
	pMainWindow( QWidget* parent = 0, Qt::WindowFlags windowFlags = 0 );
	~pMainWindow();

	pMenuBar* menuBar();
	pDockToolBarManager* dockToolBarManager();
	pDockToolBar* dockToolBar( Qt::ToolBarArea area );

	void setSettings( pSettings* settings );
	pSettings* settings();

protected:
	pSettings* mSettings;

	void hideEvent( QHideEvent* event );

public slots:
	virtual void saveState();
	virtual void restoreState();
};

#endif // PMAINWINDOW_H
