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
#include "pMainWindow.h"
#include "objects/pSettings.h"
#include "pMenuBar.h"
#include "pDockToolBarManager.h"
#include "pDockToolBar.h"

/*!
	\details Create a new pMainWindow object
	\param parent The parent widget
	\param windowFlags The window flags
*/
pMainWindow::pMainWindow( QWidget* parent, Qt::WindowFlags windowFlags )
	: QMainWindow( parent, windowFlags ), mSettings( 0 )
{
	// set menu bar
	setMenuBar( new pMenuBar( this ) );
	// init toolbar
	dockToolBar( Qt::TopToolBarArea );
	dockToolBar( Qt::BottomToolBarArea );
	dockToolBar( Qt::LeftToolBarArea );
	dockToolBar( Qt::RightToolBarArea );
}
#include <QDebug>
pMainWindow::~pMainWindow( )
{
	qDebug() << "python main window deleted";
}

void pMainWindow::hideEvent( QHideEvent* event )
{
	Q_UNUSED( event );
	saveState();
}

/*!
	\details Return the pMenuBar object
*/
pMenuBar* pMainWindow::menuBar()
{ return qobject_cast<pMenuBar*>( QMainWindow::menuBar() ); }

/*!
	\details Return the pDockToolBarManager object
*/
pDockToolBarManager* pMainWindow::dockToolBarManager()
{ return pDockToolBarManager::instance( this ); }

/*!
	\details Return the pDockToolBar object for \c area
	\param area The area of the bar to get
*/
pDockToolBar* pMainWindow::dockToolBar( Qt::ToolBarArea area )
{ return dockToolBarManager()->bar( area ); }

/*!
	\details Set the pSettings object to use by this pMainWindow
	\details restoreState() is automatically called after.
	\param settings The pSettings object
*/
void pMainWindow::setSettings( pSettings* settings )
{
	if ( mSettings != settings )
	{
		mSettings = settings;
		dockToolBarManager()->setSettings( settings );
		restoreState();
	}
}

/*!
	\details Return the pSettings object
*/
pSettings* pMainWindow::settings()
{ return mSettings; }

/*!
	\details Save the pMainWindow state.
	\details Concretly pDockToolBarManager::saveState() and
	\details pSettings::saveState() are called.
*/
void pMainWindow::saveState()
{
	if ( settings() )
	{
		dockToolBarManager()->saveState();
		settings()->saveState( this );
	}
}

/*!
	\details Restore the pMainWindow state.
	\details Concretly pDockToolBarManager::restoreState() and
	\details pSettings::restoreState() are called.
*/
void pMainWindow::restoreState()
{
	if ( settings() )
	{
		dockToolBarManager()->restoreState();
		settings()->restoreState( this );
	}
}
