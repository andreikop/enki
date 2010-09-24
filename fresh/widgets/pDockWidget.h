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
	\file pDockWidget.h
	\date 2008-01-14T00:27:42
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A QDockWidget that keep it's size
*/
#ifndef PDOCKWIDGET_H
#define PDOCKWIDGET_H

#include "objects/MonkeyExport.h"

#include <QDockWidget>

class pActionsManager;
class pDockWidgetTitleBar;

/*!
	\brief A QDockWidget that keep it's size
	\details when hidden then shown when docked
*/
class Q_MONKEY_EXPORT pDockWidget : public QDockWidget
{
	Q_OBJECT
	
public:
	pDockWidget( const QString& title, QWidget* parent = 0, Qt::WindowFlags flags = 0 );
	pDockWidget( QWidget* parent = 0, Qt::WindowFlags flags = 0 );
	~pDockWidget();

	virtual QSize sizeHint() const;
	
	pDockWidgetTitleBar* titleBar() const;
	
	void setActionsManager( pActionsManager* manager );
	pActionsManager* actionsManager() const;
	
public slots:
	virtual void setVisible( bool visible );

protected:
	pDockWidgetTitleBar* mTitleBar;
	pActionsManager* mActionsManager;
	QSize mSize;
	
	void init();
	QSize contentsSize() const;
	virtual void paintEvent( QPaintEvent* event );

protected slots:
	void toggleViewAction_toggled( bool toggled );
	void handleWindowActivation();
	void handleFocusProxy();
};

#endif // PDOCKWIDGET_H
