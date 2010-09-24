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
#include "pDockToolBarManager.h"
#include "pDockToolBar.h"
#include "objects/pSettings.h"

#include <QMainWindow>
#include <QDockWidget>
#include <QAbstractButton>
#include <QAction>

/*!
	\details Create a new pDockToolBarManager
	\param window The QMainWindow where this manager operate
*/
pDockToolBarManager::pDockToolBarManager( QMainWindow* window )
	: QObject( window ), mMain( window ), mSettings( 0 )
{ Q_ASSERT( window != 0 ); }

/*!
	\details Return the mainwindow where this manager operate
*/
QMainWindow* pDockToolBarManager::mainWindow() const
{ return mMain; }

/*!
	\details Set the pSettings object for this manager
	\param settings The pSettings object to use
*/
void pDockToolBarManager::setSettings( pSettings* settings )
{
	if ( mSettings != settings )
		mSettings = settings;
}

/*!
	\details Return the pSettings object used by this manager
*/
pSettings* pDockToolBarManager::settings()
{ return mSettings; }

/*!
	\details Return a pDockToolBar for the area, creating it if needed.
	\details Return null if area is invalid
	\param area The area to get/create the pDockToolBar
*/
pDockToolBar* pDockToolBarManager::bar( Qt::ToolBarArea area )
{
	// if toolbar not exists, create it
	if ( !mBars.contains( area ) )
	{
		switch ( area )
		{
		case Qt::TopToolBarArea:
			mBars[area] = new pDockToolBar( this, Qt::Horizontal, mMain );
			mBars[area]->setObjectName( "pDockToolBarTop" );
			mBars[area]->setWindowTitle( tr( "Top toolbar" ) );
			mBars[area]->toggleViewAction()->setText( tr( "Top toolbar visible" ) );
			break;
		case Qt::BottomToolBarArea:
			mBars[area] = new pDockToolBar( this, Qt::Horizontal, mMain );
			mBars[area]->setObjectName( "pDockToolBarBottom" );
			mBars[area]->setWindowTitle( tr( "Bottom toolbar" ) );
			mBars[area]->toggleViewAction()->setText( tr( "Bottom toolbar visible" ) );
			break;
		case Qt::LeftToolBarArea:
			mBars[area] = new pDockToolBar( this, Qt::Vertical, mMain );
			mBars[area]->setObjectName( "pDockToolBarLeft" );
			mBars[area]->setWindowTitle( tr( "Left toolbar" ) );
			mBars[area]->toggleViewAction()->setText( tr( "Left toolbar visible" ) );
			break;
		case Qt::RightToolBarArea:
			mBars[area] = new pDockToolBar( this, Qt::Vertical, mMain );
			mBars[area]->setObjectName( "pDockToolBarRight" );
			mBars[area]->setWindowTitle( tr( "Right toolbar" ) );
			mBars[area]->toggleViewAction()->setText( tr( "Right toolbar visible" ) );
			break;
		default:
			return 0;
			break;
		}
		// add toolbar to mainwindow
		mMain->addToolBar( area, mBars[area] );
		// hide
		mBars[area]->hide();
		// track dock bar changed
		connect( mBars[area], SIGNAL( dockWidgetAreaChanged( QDockWidget*, pDockToolBar* ) ), this, SLOT( dockWidgetAreaChanged( QDockWidget*, pDockToolBar* ) ) );
	}
	// return existings toolbar
	return mBars[area];
}

/*!
	\details Convert a DockWidgetArea to a ToolBarArea and return it.
	\details Return BottomToolBarArea if area is invalid
	\param area The DockWidgetArea to convert
*/
Qt::ToolBarArea pDockToolBarManager::dockWidgetAreaToToolBarArea( Qt::DockWidgetArea area )
{
	switch ( area )
	{
	case Qt::LeftDockWidgetArea:
		return Qt::LeftToolBarArea;
		break;
	case Qt::RightDockWidgetArea:
		return Qt::RightToolBarArea;
		break;
	case Qt::TopDockWidgetArea:
		return Qt::TopToolBarArea;
		break;
	case Qt::BottomDockWidgetArea:
		return Qt::BottomToolBarArea;
		break;
	default:
		return Qt::BottomToolBarArea;
		break;
	}
}

/*!
	\details Convert a ToolBarArea to a DockWidgetArea and return it.
	\details Return BottomDockWidgetArea if area is invalid
	\param area The ToolBarArea to convert
*/
Qt::DockWidgetArea pDockToolBarManager::toolBarAreaToDockWidgetArea( Qt::ToolBarArea area )
{
	switch ( area )
	{
	case Qt::LeftToolBarArea:
		return Qt::LeftDockWidgetArea;
		break;
	case Qt::RightToolBarArea:
		return Qt::RightDockWidgetArea;
		break;
	case Qt::TopToolBarArea:
		return Qt::TopDockWidgetArea;
		break;
	case Qt::BottomToolBarArea:
		return Qt::BottomDockWidgetArea;
		break;
	default:
		return Qt::BottomDockWidgetArea;
		break;
	}
}

/*!
	\details Convert a ToolBarArea to a QBoxLayout::Direction and return it.
	\details Return QBoxLayout::LeftToRight if area is invalid
	\param area The ToolBarArea to convert
*/
QBoxLayout::Direction pDockToolBarManager::toolBarAreaToBoxLayoutDirection( Qt::ToolBarArea area )
{
	switch ( area )
	{
	case Qt::LeftToolBarArea:
		return QBoxLayout::BottomToTop;
		break;
	case Qt::RightToolBarArea:
		return QBoxLayout::TopToBottom;
		break;
	case Qt::TopToolBarArea:
	case Qt::BottomToolBarArea:
		return QBoxLayout::LeftToRight;
		break;
	default:
		return QBoxLayout::LeftToRight;
		break;
	}
}

void pDockToolBarManager::dockWidgetAreaChanged( QDockWidget* dock, pDockToolBar* pbar )
{
	// remove dock from old toolbar
	pbar->removeDock( dock );
	// add dock to new toolbar
	bar( dockWidgetAreaToToolBarArea( mMain->dockWidgetArea( dock ) ) )->addDock( dock, dock->windowTitle(), dock->windowIcon().pixmap( QSize( 24, 24 ), QIcon::Normal, QIcon::On ) );
}

/*!
	\details Restore the state of the bar given in parameter.
	\param pbar The bar to restore, if null all bars are restored
*/
void pDockToolBarManager::restoreState( pDockToolBar* pbar )
{
	// need settings
	if ( !settings() )
		return;
	// get the bar to restore
	QStringList areas;
	if ( pbar )
		areas << QString::number( mMain->toolBarArea( pbar ) );
	else
	{
		settings()->beginGroup( "MainWindow/Docks" );
		areas = settings()->childGroups();
		settings()->endGroup();
	}
	// for docktoolbar
	foreach ( QString area, areas )
	{
		// get bar
		pbar = bar( (Qt::ToolBarArea)area.toInt() );
		// if got bar
		if ( pbar )
		{
			// restore exclusive state
			pbar->setExclusive( settings()->value( QString( "MainWindow/Docks/%1/Exclusive" ).arg( area ), true ).toBool() );
			// bar datas
			QStringList docksName = settings()->value( QString( "MainWindow/Docks/%1/Widgets" ).arg( area ), QStringList() ).toStringList();
			// for each entry
			foreach ( QString dockName, docksName )
			{
				// get dock
				QDockWidget* dock = mMain->findChild<QDockWidget*>( dockName );
				// restore dock area
				if ( dock )
					pbar->addDock( dock, dock->windowTitle(), dock->windowIcon() );
			}
		}
	}
}

/*!
	\details Save the state of the bar given in parameter.
	\param bar The bar to save, if null all bars are saved
*/
void pDockToolBarManager::saveState( pDockToolBar* bar )
{
	// need settings
	if ( !settings() )
		return;
	// get the bar to save
	QList<pDockToolBar*> bars;
	if ( bar )
		bars << bar;
	else
		bars << mBars.values();
	// for each docktoolbar
	foreach ( pDockToolBar* tb, bars )
	{
		// list to stock checked button
		QStringList mList;
		// for each dock in docktoolbar
		foreach ( QDockWidget* dock, tb->docks() )
			mList << dock->objectName();
		// write datas
		settings()->setValue( QString( "MainWindow/Docks/%1/Exclusive" ).arg( mMain->toolBarArea( tb ) ), tb->exclusive() );
		settings()->setValue( QString( "MainWindow/Docks/%1/Widgets" ).arg( mMain->toolBarArea( tb ) ), mList );
	}
}
