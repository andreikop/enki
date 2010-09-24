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
	\file pDockWidgetTitleBar.h
	\date 2008-01-14T00:27:42
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A custom title bar for pDockWidget
*/
#ifndef PDOCKWIDGETTITLEBAR_H
#define PDOCKWIDGETTITLEBAR_H

#include "objects/MonkeyExport.h"
#include "pDockWidget.h"

#include <QToolBar>

class QWidgetAction;

/*!
	\brief A custom title bar for pDockWidget
	\details that herits QToolBar so custom actions can be added in the title bar.
*/
class Q_MONKEY_EXPORT pDockWidgetTitleBar : public QToolBar
{
	Q_OBJECT

public:
	pDockWidgetTitleBar( pDockWidget* parent = 0 );
	
	virtual bool event( QEvent* event );
	virtual QSize minimumSizeHint() const;
	virtual QSize sizeHint() const;
	
	QWidget* addAction( QAction* action, int index = -1 );
	void addSeparator( int index = -1 );

protected:
	pDockWidget* mDock;
	QWidgetAction* mSpacer;
	QAction* aOrientation;
	QAction* aFloat;
	QAction* aClose;
	
	virtual void paintEvent( QPaintEvent* event );
	void transposeSize( QRect& rect );
	void updateStandardIcons();

protected slots:
	void aOrientation_triggered();
	void aFloat_triggered();
	void dockWidget_featuresChanged( QDockWidget::DockWidgetFeatures features );
};

#endif // PDOCKWIDGETTITLEBAR_H
