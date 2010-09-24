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
#include "pTabbedMainWindow.h"
#include "pTabbedWorkspace.h"

/*!
	\details Create a new pTabbedMainWindow object
	\param parent The parent widget
	\param windowFlags The window flags
*/
pTabbedMainWindow::pTabbedMainWindow( QWidget* parent, Qt::WindowFlags windowFlags )
	: pMainWindow( parent, windowFlags ), mWorkspace( new pTabbedWorkspace )
{
	// init tabbed workspace
	setCentralWidget( mWorkspace );
}

/*!
	\details Return the pTabbedWorkspace object
*/
pTabbedWorkspace* pTabbedMainWindow::tabbedWorkspace()
{
	return mWorkspace;
}

/*!
	\details Save the window state
*/
void pTabbedMainWindow::saveState()
{
	pMainWindow::saveState();
}

/*!
	\details Restore the window state
*/
void pTabbedMainWindow::restoreState()
{
	pMainWindow::restoreState();
}
