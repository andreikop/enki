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
	\file pExtendedWorkspace.h
	\date 2008-01-14T00:27:43
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief An extended container for SDI, MDI, TopLevel children
*/
#ifndef PEXTENDEDWORKSPACE_H
#define PEXTENDEDWORKSPACE_H

#include "objects/MonkeyExport.h"
#include "pTabBar.h"

#include <QWidget>
#include <QList>
#include <QIcon>

class QBoxLayout;
class QStackedLayout;
class QStackedWidget;
class QMdiArea;
class QMdiSubWindow;
class pAction;
class pFilesListWidget;

/*!
	\brief An extended container for SDI, MDI, TopLevel children
	\details The container is like a QStackedWidget that can at runtime be switched
	\details in many views like SDI, MDI and independant TopLevel window.
	\details Call closeAllDocuments when destroyed.
*/
class Q_MONKEY_EXPORT pExtendedWorkspace : public QWidget
{
	Q_OBJECT
	Q_ENUMS( TabMode DocumentMode )
	
public:
	enum DocumentMode { dmSDI = 0, dmMDI, dmTopLevel };

	pExtendedWorkspace( QWidget* parent, pExtendedWorkspace::DocumentMode mode = pExtendedWorkspace::dmSDI );
	~pExtendedWorkspace();
	
	virtual bool eventFilter( QObject* object, QEvent* event );

	//getters
	pTabBar* tabBar() const;
	pFilesListWidget* listWidget() const;
	
	pExtendedWorkspace::DocumentMode docMode() const;
	QTabBar::Shape tabShape() const;

	QWidgetList documents() const;	
	QWidget* document( int id ) const;
	int count() const;
	
	int currentIndex() const;
	QWidget* currentDocument() const;
	int indexOf( QWidget* widget ) const;

	void setBackground( const QPixmap& pixmap );
	void setBackground( const QString& fileName );
	
	int addDocument( QWidget* widget, const QString& title, const QIcon& icon = QIcon() );
	int insertDocument( int id, QWidget* widget, const QString& title, const QIcon& icon = QIcon() );
	
	QWidget* takeDocument( int id );
	void removeDocument( int id );
	void moveDocument( int fromId, int toId );
	
public slots:
	void setDocMode( pExtendedWorkspace::DocumentMode mode );
	void setTabShape( QTabBar::Shape shape );

	void setCurrentIndex( int id );
	void setCurrentDocument( QWidget* widget );

	/*
	Do not make this functions virtual!!
	closeAllDocuments must not call functions of child classes
	*/
	virtual void closeDocument( QWidget* document );
	virtual void closeDocument( int id );
	virtual bool closeAllDocuments();
	virtual void closeCurrentDocument();

	void activateNextDocument();
	void activatePreviousDocument();

	void setSDI();
	void setMDI();
	void setTopLevel();
	void cascade();
	void tile();
	void minimize();
	void restore();

protected:
	// workspace properties
	pExtendedWorkspace::DocumentMode mDocMode;

	QList<QWidget*> mDocuments;
	QWidget* mLastDocument;

	// main layout
	QBoxLayout* mLayout;
	// tab widget
	pTabBar* mTabBar;
	QBoxLayout* mTabLayout;
	//list widget
	pFilesListWidget* mFilesList;
	// document widget
	QStackedLayout* mStackedLayout;
	/* Stacked widget used for SDI mode, because we can't use maximized windows on QMdiArea on Mac*/
	QStackedWidget* mStackedWidget; 
	QMdiArea* mMdiAreaWidget;

protected slots:
	void mdiArea_subWindowActivated( QMdiSubWindow* window );
	void internal_currentChanged( int id );

signals:
	void documentInserted( int id, const QString& title, const QIcon& icon );
	void documentAboutToBeRemoved( int id );
	void documentAboutToClose( int id );
	// -1 if last file was closed
	void currentChanged( int id );
	void tabShapeChanged( QTabBar::Shape shape );
	void docModeChanged( pExtendedWorkspace::DocumentMode mode );
	void modifiedChanged( int id, bool modified );
	void docTitleChanged( int id, const QString& title );
	
//	void aboutToCloseAll ();
};

#endif // PEXTENDEDWORKSPACE_H
