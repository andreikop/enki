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
	\file pTabBar.h
	\date 2008-01-14T00:27:50
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A extended QTabBar
*/
#ifndef PTABBAR_H
#define PTABBAR_H

#include "objects/MonkeyExport.h"

#include <QTabBar>
#include <QList>
#include <QUrl>

class QAction;

/*!
	\brief A extended QTabBar
	\details that allow tab drag and drop, shortcuts, text elided, tabs color, current tab color and close button
*/
class Q_MONKEY_EXPORT pTabBar : public QTabBar
{
	Q_OBJECT

public:
	pTabBar( QWidget* parent = 0 );

	QColor tabsColor() const;
	QColor currentTabColor() const;
	bool tabsHaveCloseButton() const;
	bool tabsHaveShortcut() const;
	bool tabsElided() const;
	QAction* toggleTabsHaveCloseButtonAction() const;
	QAction* toggleTabsHaveShortcutAction() const;
	QAction* toggleTabsElidedAction() const;

public slots:
	void resetTabsColor();
	void setTabsColor( const QColor& color );
	void setCurrentTabColor( const QColor& color );
	void setTabsHaveCloseButton( bool buttons );
	void setTabsHaveShortcut( bool shortcuts );
	void setTabsElided( bool elided );

protected:
	virtual void paintEvent( QPaintEvent* event );
	virtual void mousePressEvent( QMouseEvent* event );
	virtual void mouseReleaseEvent( QMouseEvent* event );
	virtual void mouseMoveEvent( QMouseEvent* event );
	virtual void dragEnterEvent( QDragEnterEvent* event );
	virtual void dropEvent( QDropEvent* event );
	virtual void tabInserted( int id );
	virtual void tabRemoved( int id );
	virtual QRect iconRectForTab( int id );
	virtual bool inCloseButtonRect( int id, const QPoint& pos );
	void updateTabsNumber( int id = -1 );

	QPoint dragStartPosition;
	QColor mTabsColor;
	QColor mCurrentTabColor;

	QAction* aToggleTabsHaveCloseButton;
	QAction* aToggleTabsHaveShortcut;
	QAction* aToggleTabsElided;

signals:
	void leftButtonPressed( int id, const QPoint& pos );
	void midButtonPressed( int id, const QPoint& pos );
	void rightButtonPressed( int id, const QPoint& pos );
	void tabDropped( int from, int to );
	void tabsColorChanged( const QColor& color );
	void currentTabColorChanged( const QColor& color );
	void closeButtonClicked( int id );
	void tabsHaveCloseButtonChanged( bool buttons );
	void tabsHaveShortcutChanged( bool shortcuts );
	void tabsElidedChanged( bool elided );
	void urlsDropped( const QList<QUrl>& urls );
};

#endif // PTABBAR_H
