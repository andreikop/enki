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
#include "pDockWidget.h"
#include "pDockWidgetTitleBar.h"
#include "pActionsManager.h"

#include <QStyle>
#include <QPainter>
#include <QAction>
#include <QTimer>
#include <QApplication>

#include <QDebug>

/*!
	\brief Create a new pDockWidget instance
	\param title The dock title
	\param parent The dock parent
	\param flags The dock window flags
*/
pDockWidget::pDockWidget( const QString& title, QWidget* parent, Qt::WindowFlags flags )
	: QDockWidget( title, parent, flags )
{
	init();
}

/*!
	\brief Create a new pDockWidget instance
	\param parent The dock parent
	\param flags The dock window flags
*/
pDockWidget::pDockWidget( QWidget* parent, Qt::WindowFlags flags )
	: QDockWidget( parent, flags )
{
	init();
}

void pDockWidget::init()
{
	mTitleBar = new pDockWidgetTitleBar( this );
	setTitleBarWidget( mTitleBar );

	connect( toggleViewAction(), SIGNAL( toggled( bool ) ), this, SLOT( toggleViewAction_toggled( bool ) ) );
}

pDockWidget::~pDockWidget()
{
	setFocusProxy( 0 );
}

QSize pDockWidget::contentsSize() const
{
	QSize contents = size();
	int fw = style()->pixelMetric( QStyle::PM_DockWidgetFrameWidth );
	QSize frame( 2 *fw, fw );
#ifdef Q_OS_WIN
	frame -= QSize( 0, 3 );
#endif
	contents -= frame;
	return contents;
}

void pDockWidget::paintEvent( QPaintEvent* event )
{
	QDockWidget::paintEvent(  event );
	
	if ( isFloating() ) {
		QRect rect = this->rect().adjusted( 0, 0, -1, -1 );
		
		if ( !isFloating() )
		{
			if ( features() & QDockWidget::DockWidgetVerticalTitleBar ) {
				rect.adjust( mTitleBar->width(), 0, 0, 0 );
			}
			else {
				rect.adjust( 0, mTitleBar->height(), 0, 0 );
			}
		}
		
		QPainter painter( this );
		painter.setPen( QColor( 145, 142, 142 ) );
		painter.setBrush( Qt::NoBrush );
		painter.drawRect( rect );
	}
}

void pDockWidget::toggleViewAction_toggled( bool toggled )
{
	if ( toggled && focusProxy() )
	{
		if ( isFloating() )
		{
			QTimer::singleShot( 25, this, SLOT( handleWindowActivation() ) );
		}
		else
		{
			QTimer::singleShot( 25, this, SLOT( handleFocusProxy() ) );
		}
	}
}

void pDockWidget::handleWindowActivation()
{
	activateWindow();
	QTimer::singleShot( 25, this, SLOT( handleFocusProxy() ) );
}

void pDockWidget::handleFocusProxy()
{
	focusProxy()->setFocus();
}

/*!
	\details Return the dock sizeHint
*/
QSize pDockWidget::sizeHint() const
{
	return mSize.isValid() && !isFloating() ? mSize : QDockWidget::sizeHint();
}

pDockWidgetTitleBar* pDockWidget::titleBar() const
{
	return mTitleBar;
}

void pDockWidget::setActionsManager( pActionsManager* manager )
{
	mActionsManager = manager;
}

pActionsManager* pDockWidget::actionsManager() const
{
	return mActionsManager;
}

/*!
	\details Set dock visibility
	\param visible if tru, dock will be visible, else dock is hidden
*/
void pDockWidget::setVisible( bool visible )
{
	if ( !visible && !isFloating() )
		mSize = contentsSize();
	QDockWidget::setVisible( visible );
}
