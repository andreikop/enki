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
/*!
	\file pDockToolBarManager.h
	\date 2008-01-14T00:27:41
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief This class manage a set of pDockToolBar ( left, top, right and bottom ) of a QMainWindow
*/
#ifndef PDOCKTOOLBARMANAGER_H
#define PDOCKTOOLBARMANAGER_H

#include "objects/MonkeyExport.h"
#include "objects/QSingleton.h"

#include <QHash>
#include <QBoxLayout>

class QMainWindow;
class pDockToolBar;
class QDockWidget;
class pSettings;

/*!
	\brief This class manage a set of pDockToolBar ( left, top, right and bottom ) of a QMainWindow
	\details It provide usefull member ( bar() ) to directly create a unique pDockToolBar for the corresponding area.
	\details It allow to save/restore state of pDockToolBar using a pSettings class.
*/
class Q_MONKEY_EXPORT pDockToolBarManager : public QObject, public QSingleton<pDockToolBarManager>
{
	Q_OBJECT
	friend class QSingleton<pDockToolBarManager>;

public:
	QMainWindow* mainWindow() const;
	pDockToolBar* bar( Qt::ToolBarArea area );

	void setSettings( pSettings* settings );
	pSettings* settings();

	static Qt::ToolBarArea dockWidgetAreaToToolBarArea( Qt::DockWidgetArea area );
	static Qt::DockWidgetArea toolBarAreaToDockWidgetArea( Qt::ToolBarArea area );
	static QBoxLayout::Direction toolBarAreaToBoxLayoutDirection( Qt::ToolBarArea area );

protected:
	QMainWindow* mMain;
	QHash<Qt::ToolBarArea, pDockToolBar*> mBars;
	pSettings* mSettings;

	pDockToolBarManager( QMainWindow* window );

public slots:
	void dockWidgetAreaChanged( QDockWidget* dock, pDockToolBar* bar );
	virtual void restoreState( pDockToolBar* bar = 0 );
	virtual void saveState( pDockToolBar* bar = 0 );
};

#endif // PDOCKTOOLBARMANAGER_H
