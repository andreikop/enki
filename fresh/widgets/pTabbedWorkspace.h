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
	\file pTabbedWorkspace.h
	\date 2008-01-14T00:27:52
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief An extended workspace
	\brief This class and its associated classes are obsolete
*/
#ifndef PTABBEDWORKSPACE_H
#define PTABBEDWORKSPACE_H

#include "objects/MonkeyExport.h"

#include <QWidget>
#include "pTabBar.h"
#include <QList>

class QBoxLayout;
class QStackedLayout;
class QStackedWidget;
class QWorkspace;
class pTabbedWorkspaceCorner;
class pAction;
class pTabBar;

/*!
	\brief An extended workspace
	\details that can at run time be switched to SDI/MDI/TopLevel Window.
	\details See pExtendedWorkspace
*/
class Q_MONKEY_EXPORT pTabbedWorkspace : public QWidget
{
	Q_OBJECT
	Q_ENUMS( TabMode DocumentMode )
	
public:
	enum TabMode { tmSDI = 0, tmMDI, tmTopLevel };
	enum DocumentMode { dmMaximized = 0, dmCascade, dmTile, dmIcons, dmMinimizeAll, dmRestoreAll };

	pTabbedWorkspace( QWidget* = 0, pTabbedWorkspace::TabMode = pTabbedWorkspace::tmMDI );
	~pTabbedWorkspace();
	
	virtual bool eventFilter( QObject*, QEvent* );

	pTabBar* tabBar() const;
	QTabBar::Shape tabShape() const;
	pTabbedWorkspace::TabMode tabMode() const;
	pTabbedWorkspace::DocumentMode documentMode() const;
	int currentIndex() const;
	QWidget* currentDocument() const;
	int indexOf( QWidget* ) const;
	QWidget* document( int ) const;
	int count() const;
	QList<QWidget*> documents() const;
	pTabbedWorkspaceCorner* cornerWidget( Qt::Corner = Qt::TopRightCorner ) const;
	int addTab( QWidget*, const QString& );
	int addTab( QWidget*, const QIcon&, const QString& );
	int insertTab( int, QWidget*, const QString& );
	int insertTab( int, QWidget*, const QIcon&, const QString& );

public slots:
	void setBackground( const QPixmap& );
	void setBackground( const QString& );
	void setTabShape( QTabBar::Shape );
	void setTabMode( pTabbedWorkspace::TabMode );
	void setDocumentMode( pTabbedWorkspace::DocumentMode );
	void setCurrentIndex( int );
	void setCurrentDocument( QWidget* );
	void setCornerWidget( pTabbedWorkspaceCorner*, Qt::Corner = Qt::TopRightCorner );
	void removeTab( int );
	void removeDocument( QWidget* );
	void closeCurrentTab();
	void closeAllTabs( bool = false, bool = false );
	void activateNextDocument();
	void activatePreviousDocument();

protected:
	void updateCorners();
	void updateView( QWidget* = 0 );
	void addDocument( QWidget* d, int = -1 );

	// workspace properties
	pTabbedWorkspace::TabMode mTabMode;
	pTabbedWorkspace::DocumentMode mDocumentMode;
	// main layout
	QBoxLayout* mLayout;
	QList<QWidget*> mDocuments;
	// tab widget
	pTabBar* mTabBar;
	QBoxLayout* mTabLayout;
	// document widget
	QStackedLayout* mStackedLayout;
	QStackedWidget* mStackedWidget;
	QWorkspace* mWorkspaceWidget;

protected slots:
	void internal_midButtonPressed( int, const QPoint& );
	void internal_closeButtonClicked( int );
	void internal_rightButtonPressed( int, const QPoint& );
	void internal_tabDropped( int, int );
	void internal_currentChanged( int );
	void workspaceWidget_windowActivated( QWidget* );
	void removeDocument( QObject* );

signals:
	void tabInserted( int );
	void aboutToCloseTab( int, QCloseEvent* );
	void aboutToCloseDocument( QWidget*, QCloseEvent* );
	void tabRemoved( int );
	void currentChanged( int );
	void tabShapeChanged( QTabBar::Shape );
	void tabModeChanged( pTabbedWorkspace::TabMode );
	void documentModeChanged( pTabbedWorkspace::DocumentMode );
	void closeAllRequested();
};

#endif // PTABBEDWORKSPACE_H
