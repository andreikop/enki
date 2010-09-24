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
	\file pDockToolBar.h
	\date 2008-01-14T00:27:40
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A toolbar that can manage dock visibility by adding buttons in it
*/
#ifndef PDOCKTOOLBAR_H
#define PDOCKTOOLBAR_H

#include "objects/MonkeyExport.h"

#include <QToolBar>
#include <QIcon>
#include <QHash>

class QDockWidget;
class QAbstractButton;
class QFrame;
class QBoxLayout;
class pDockToolBarManager;

/*!
	\brief A toolbar that can manage dock visibility by adding buttons in it
	\details The doc ktoolbars are managed by a pDockToolBarManager for top, right, bottom, left
*/
class Q_MONKEY_EXPORT pDockToolBar : public QToolBar
{
	Q_OBJECT

public:
	pDockToolBar( pDockToolBarManager* manager, Qt::Orientation orientation = Qt::Horizontal, QMainWindow* window = 0 );

	virtual bool eventFilter( QObject* object, QEvent* event );

	QAction* addAction( QAction* action = 0, bool insert = true );
	void addActions( QList<QAction*> actions, bool insert = true );

	int addDock( QDockWidget* dock, const QString& title = QString(), const QIcon& icon = QIcon() );

	bool isDockVisible( int id ) const;
	bool isDockVisible( QDockWidget* dock ) const;

	bool exclusive() const;
	bool textAlwaysVisible() const;

	int id( QDockWidget* dock ) const;
	int id( QAbstractButton* button ) const;

	QDockWidget* dock( int id ) const;
	QDockWidget* dock( QAbstractButton* button ) const;

	QAbstractButton* button( int id ) const;
	QAbstractButton* button( QDockWidget* dock ) const;
	
	QList<QDockWidget*> docks() const;
	QList<QAbstractButton*> buttons() const;

	int count() const;
	
	QAction* toggleExclusiveAction() const;

private:
	pDockToolBarManager* mManager;
	int mUniqueId;
	bool mTextAlwaysVisible;
	QFrame* mFrame;
	QBoxLayout* mLayout;
	QAction* aDockFrame;
	QAction* aToggleExclusive;
	QHash<int, QAbstractButton*> mButtons;
	QHash<int, QDockWidget*> mDocks;

public slots:
	void removeDock( int id );
	void removeDock( QDockWidget* dock );
	void setDockVisible( QDockWidget* dock, bool visible );
	void setExclusive( bool exclusive );
	void setTextAlwaysVisible( bool visible );

private slots:
	void internal_checkVisibility();
	void internal_checkButtonText( QAbstractButton* button );
	void internal_orientationChanged( Qt::Orientation orientation );
	void internal_dockChanged();
	void internal_dockDestroyed( QObject* object );
	void internal_buttonClicked( bool checked );

signals:
	void buttonClicked( int id );
	void dockWidgetAreaChanged( QDockWidget* dock, pDockToolBar* toolBar );
};

#endif // PDOCKTOOLBAR_H
