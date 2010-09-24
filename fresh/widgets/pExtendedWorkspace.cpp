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
#include "pExtendedWorkspace.h"
#include "pFilesListWidget.h"

#include <QBoxLayout>
#include <QMdiArea>
#include <QMdiSubWindow>
#include <QIcon>
#include <QCloseEvent>
#include <QFile>
#include <QMenu>
#include <QMainWindow>
#include <QStackedLayout>
#include <QStackedWidget>
#include <QDockWidget>
#include <Qt>
#include <QApplication>

/*!
	\details Create a new pExtendedWorkspace instance
	\param parent The parent widget
	\param mode The current mode
*/
pExtendedWorkspace::pExtendedWorkspace( QWidget* parent, pExtendedWorkspace::DocumentMode mode )
	: QWidget( parent )
{
	mLastDocument = 0;
	// tab widget
	mTabLayout = new QBoxLayout( QBoxLayout::LeftToRight );
	mTabLayout->setSpacing( 3 );
	mTabLayout->setMargin( 0 );
	//mTabBar = new pTabBar (this);
	//mTabLayout->addWidget( ( mTabBar ) );

	mFilesList = new pFilesListWidget( tr( "Files List"), this );
	
	// document widget
	mStackedLayout = new QStackedLayout;
	mStackedLayout->addWidget( ( mStackedWidget = new QStackedWidget ) );
	mStackedLayout->addWidget( ( mMdiAreaWidget = new QMdiArea ) );

	// main layout
	mLayout = new QBoxLayout( QBoxLayout::TopToBottom, this );
	mLayout->setSpacing( 0 );
	mLayout->setMargin( 0 );
	mLayout->addLayout( mTabLayout );
	mLayout->addLayout( mStackedLayout );
	
	// init view
	//mTabBar->setDrawBase( false );
	//mTabBar->setSizePolicy( QSizePolicy( QSizePolicy::Expanding, QSizePolicy::Preferred ) );
	
	mDocMode = (DocumentMode) -1; //for avoid return on start method setDocMode (m)
	setDocMode( mode );
	
	connect( mMdiAreaWidget, SIGNAL( subWindowActivated( QMdiSubWindow* ) ), this, SLOT( mdiArea_subWindowActivated( QMdiSubWindow* ) ) );
	connect( this, SIGNAL( currentChanged( int ) ), this, SLOT( internal_currentChanged( int ) ) );
}

pExtendedWorkspace::~pExtendedWorkspace()
{
	// close all document
	closeAllDocuments();

	// delete container
	delete mMdiAreaWidget;
}

bool pExtendedWorkspace::eventFilter( QObject* object, QEvent* event )
{
	// get document
	if ( QWidget* td = qobject_cast<QWidget*>( object ) )
	{
		if ( td->inherits( "QMdiSubWindow" ) && event->type() == QEvent::Close )
		{
			event->ignore();
			closeCurrentDocument();
			return true;
		}
		else
		{
			if ( indexOf( td ) == -1 )
				return QWidget::eventFilter( object, event );
			
			// get event type
			QEvent::Type type = event->type();
			
			// child modified state
			switch ( type )
			{
			case QEvent::ModifiedChange:
				emit modifiedChanged( indexOf( td ), td->isWindowModified() );
				break;
			case QEvent::Close:
				closeDocument( td );
				return true;
				break;
			case QEvent::WindowActivate:
				if ( mDocMode == dmTopLevel )
					emit currentChanged( indexOf( td ) );
				break;
			case QEvent::WindowTitleChange:
				emit docTitleChanged( indexOf( td ), td->windowTitle().replace( "[*]", QString() ) );
			default:
				break;
			}
		}
	}

	// return default event filter
	return QWidget::eventFilter( object, event );
}

/*!
	\details Return the QTabbar associated with the workspace.
	\details Can be null.
*/
pTabBar* pExtendedWorkspace::tabBar() const
{ return NULL;}//mTabBar; }

/*!
	\details Return the pFilesListWidget widget used by the workspace.
*/
pFilesListWidget* pExtendedWorkspace::listWidget() const
{ return mFilesList; }

/*!
	\details Return the workspace mode
*/
pExtendedWorkspace::DocumentMode pExtendedWorkspace::docMode() const
{ return mDocMode; }

/*!
	\details Return the tabbar shape
*/
QTabBar::Shape pExtendedWorkspace::tabShape () const
{ return (QTabBar::Shape)0;}//mTabBar->shape(); }

/*!
	\details return the widgets list
*/
QWidgetList pExtendedWorkspace::documents() const
{ return mDocuments; }

/*!
	\details Return a widget or null if id is invalid
	\param id The id of the widget to get
*/
QWidget* pExtendedWorkspace::document( int id ) const
{ return mDocuments.value( id ); }

/*!
	\details Return the number of widget in this workspace
*/
int pExtendedWorkspace::count() const
{ return mDocuments.count(); }

/*!
	\details Return the id of the current widget
*/
int pExtendedWorkspace::currentIndex() const
{ return indexOf( currentDocument() ); }


/*!
	\details Return the current widget
*/
QWidget* pExtendedWorkspace::currentDocument() const
{
	switch ( mDocMode )
	{
		case dmSDI:
			return mStackedWidget->currentWidget();
			break;
		case dmMDI:
			return mMdiAreaWidget->currentSubWindow() ? mMdiAreaWidget->currentSubWindow()->widget() : 0;
			break;
		case dmTopLevel:
			foreach ( QWidget* w, mDocuments )
				if ( qApp->activeWindow() == w )
					return w;
			if ( mDocuments.contains( mLastDocument ) )
				return mLastDocument;
			break;
	}
	return 0;
}

/*!
	\details Return a widget id, if widget is not managed by the workspace, -1 is returned.
	\param widget The widget to get id
*/
int pExtendedWorkspace::indexOf( QWidget* widget ) const
{ return mDocuments.indexOf( widget ); }

/*!
	\details Set the worksapce background pixmap
	\param pixmap The pixmap used for background
*/
void pExtendedWorkspace::setBackground( const QPixmap& pixmap )
{ mMdiAreaWidget->setBackground( QBrush( pixmap ) ); }

/*!
	\details Set the worksapce background pixmap
	\param fileName The pixmap fileName to load
*/
void pExtendedWorkspace::setBackground( const QString& fileName )
{ mMdiAreaWidget->setBackground( QBrush( QPixmap( fileName ) ) ); }

/*!
	\details Add a new widget to the workspace
	\param widget The widget to add
	\param title The windowTitle to set
	\param icon The windowIcon to set
*/
int pExtendedWorkspace::addDocument(QWidget* widget, const QString& title,  const QIcon& icon )
{ return insertDocument( count(), widget, title, icon ); }

/*!
	\details Insert a new widget to the workspace at the given index
	\param id The widget position to add to
	\param widget The widget to add
	\param title The windowTitle to set
	\param icon The windowIcon to set
*/
int pExtendedWorkspace::insertDocument( int id, QWidget* widget, const QString& /*title*/,  const QIcon& icon )
{
	// filter the document
	widget->installEventFilter( this );
	widget->setAttribute( Qt::WA_DeleteOnClose, true );

	// append to document list
	mDocuments.insert( id, widget );
	
	switch ( mDocMode )
	{
	case dmSDI:
		mStackedLayout->setCurrentWidget( mStackedWidget );
		mStackedWidget->addWidget( widget );
		//mStackedWidget->setCurrentWidget( widget );
		break;
	case dmMDI:
	{
		QMdiSubWindow* w = mMdiAreaWidget->addSubWindow( widget );
		w->installEventFilter( this );
		w->showNormal();
		if ( !widget->isVisible() )
			widget->show();
		break;
	}
	case dmTopLevel:
		widget->setParent( 0 );
		widget->showNormal();
		break;
	}	
	
	// emit tab inserted
	emit documentInserted( id, /*title*/widget->windowTitle ().replace("[*]", "" ), icon );

	// emit tab current changed
	emit currentChanged( id );
	
	return id;
}

/*!
	\details Remove a widget at index from the workspace, and return it.
	\details The widget is not deleted.
	\details if id is invalid, null is returned
	\param id The id of the widget to take
*/
QWidget* pExtendedWorkspace::takeDocument( int id )
{
	if ( QWidget* w = mDocuments.value( id ) )
	{
		emit documentAboutToBeRemoved( id );
		mDocuments.removeAt( id );
		w->removeEventFilter( this );
		
		if ( mDocMode == dmMDI )
			foreach ( QMdiSubWindow* sw, mMdiAreaWidget->subWindowList() )
				if ( sw == w->parent() )
					sw->deleteLater();
		
		w->setParent( 0 );
		w->close();
		emit currentChanged( currentIndex() );
		return w;
	}
	return 0;
}

/*!
	\details remove a widget from workspace at the given index
	\param id The widget index, do nothing if index is invalid
*/
void pExtendedWorkspace::removeDocument( int id )
{ takeDocument( id ); }

/*!
	\details Swap 2 widgets position inside the workspace
	\param fromId The source widget index
	\param toId The target widget index
*/
void pExtendedWorkspace::moveDocument( int fromId, int toId )
{
	QWidget* w = mDocuments[fromId];
	mDocuments.insert( toId, mDocuments.takeAt( fromId ) );
	if ( mDocMode == dmSDI )
		mStackedWidget->insertWidget( toId, w );
}

/*!
	\details Close a widget ( ie: inform about to close, and remvoe it form workspace )
	\param id The widget id to remove
*/
void pExtendedWorkspace::closeDocument( int id )
{
	emit documentAboutToClose( id );
	removeDocument( id );
}

/*!
	\details Close a widget ( ie: inform about to close, and remvoe it form workspace )
	\param widget The widget to remove
*/
void pExtendedWorkspace::closeDocument( QWidget* widget )
{
	closeDocument( indexOf( widget ) );
}

/*!
	\details Close all documents
*/
bool pExtendedWorkspace::closeAllDocuments()
{
	for (int i = count()-1; i>=0; i--)
		closeDocument (i);
	return true;
}

/*!
	\details Close the current document
*/
void pExtendedWorkspace::closeCurrentDocument()
{
	closeDocument( currentIndex() );
}

/*!
	\details Change the workspace mode
	\param mode The new mode
*/
void pExtendedWorkspace::setDocMode( pExtendedWorkspace::DocumentMode mode )
{
	if ( mDocMode == mode )
		return;
	
	mDocMode = mode;

	if (mDocMode == dmSDI)
		mStackedLayout->setCurrentWidget( mStackedWidget );
	else if (mDocMode ==dmMDI )
		mStackedLayout->setCurrentWidget( mMdiAreaWidget );

	if (!count())
		return;
	
	int i = currentIndex(); //for avoid return from function because index not changed

	// add document to correct workspace
	foreach ( QWidget* td, mDocuments )
	{
		switch ( mDocMode )
		{
		case dmSDI:
			mStackedWidget->addWidget( td );
			//foreach (QAction* act, mMainWindow->actions ()) // not working !!! FIXME
			//	td->removeAction (act);
			break;
		case dmMDI:
		{
			QMdiSubWindow* w = mMdiAreaWidget->addSubWindow( td );
			w->installEventFilter( this );
			w->showNormal();
			if ( !td->isVisible() )
				td->show();
			//foreach (QAction* act, mMainWindow->actions ())
			//	td->removeAction (act);
			break;
		}
		case dmTopLevel:
			td->setParent( 0 );
			//td->addActions (mMainWindow->actions());
			td->showNormal();
			break;
		}	
	}
	
	//cleanup QMdiArea - remove it's empty QMdiSubWindows
	if ( mDocMode != dmMDI )
		foreach (QMdiSubWindow* sw, mMdiAreaWidget->subWindowList ())
			delete  sw; //if just remove - widget will not be deleted
	
	// restore current index
	setCurrentIndex( i );
	
	// emit tab mode changed
	emit docModeChanged( mDocMode );
}

void pExtendedWorkspace::setTabShape( QTabBar::Shape )
{
/*	if ( tabShape() == s )
		return;
	
	// get sizepolicy
	QSizePolicy sp = mTabBar->sizePolicy();
	
	// update view layout
	switch ( s )
	{
	case QTabBar::RoundedNorth:
	case QTabBar::TriangularNorth:
		mLayout->setDirection( QBoxLayout::TopToBottom );
		break;
	case QTabBar::RoundedSouth:
	case QTabBar::TriangularSouth:
		mLayout->setDirection( QBoxLayout::BottomToTop );
		break;
	default:
		Q_ASSERT (0);
	}
	
	// apply tab shape
	mTabBar->setShape( s );
	
	// update corners
	//updateCorners();
	
	// emit shape changed
	emit tabShapeChanged( s );*/
}

/*!
	\details Change the current indexwidget
	\param id The widget id to set current
*/
void pExtendedWorkspace::setCurrentIndex( int id )
{
	if ( currentIndex() == id )
		return;
	
	// get document
	QWidget* w = document( id );
	
	// update gui if needed
	if ( id != -1 )
	{
		switch ( mDocMode )
		{
			case dmSDI:
				mStackedWidget->setCurrentWidget( w );
			case dmMDI:
				mMdiAreaWidget->setActiveSubWindow( qobject_cast<QMdiSubWindow*>( w ? w->parent() : 0 ) );
				break;
			case dmTopLevel:
				if ( w && !w->isActiveWindow() )
					w->activateWindow();
				break;
		}
	}
	
	// emit document change
	emit currentChanged( id );
}

/*!
	\details Set the current widget
	\param widget The widget to set current
*/
void pExtendedWorkspace::setCurrentDocument( QWidget* widget )
{ setCurrentIndex( indexOf( widget ) ); }

void pExtendedWorkspace::mdiArea_subWindowActivated( QMdiSubWindow* w )
{ emit currentChanged( w ? indexOf( w->widget() ) : -1 ); }

void pExtendedWorkspace::internal_currentChanged( int id )
{ mLastDocument = document( id ); }

/*!
	\details Set the next widget the current one, the process is wrapping ( ie, if at last activate first )
*/
void pExtendedWorkspace::activateNextDocument()
{
	int currIndex = currentIndex();
	if ( currIndex +1 == count() )
		setCurrentIndex( 0 );
	else
		setCurrentIndex( currIndex +1 );
}

/*!
	\details Set the previous widget the current one, the process is wrapping ( ie, if at first activate last )
*/
void pExtendedWorkspace::activatePreviousDocument()
{
	int currIndex = currentIndex();
	if ( currIndex -1 == -1 )
		setCurrentIndex( count() -1 );
	else
		setCurrentIndex( currIndex -1 );
}

/*!
	\details Change the workspace mode to SDI
*/
void pExtendedWorkspace::setSDI()
{
	setDocMode (dmSDI);
}

/*!
	\details Change the workspace mode to MDI
*/
void pExtendedWorkspace::setMDI()
{
	setDocMode (dmMDI);
}

/*!
	\details Change the workspace mode to TopLevel
*/
void pExtendedWorkspace::setTopLevel()
{
	setDocMode (dmTopLevel);
}

/*!
	\details Cascade the documents, switching to MDI mode if needed first.
*/
void pExtendedWorkspace::cascade()
{
	setDocMode( dmMDI );
	mMdiAreaWidget->cascadeSubWindows();
};

/*!
	\details Tile the documents, switching to MDI mode if needed first.
*/
void pExtendedWorkspace::tile()
{
	setDocMode( dmMDI );
	mMdiAreaWidget->tileSubWindows();
};

/*!
	\details Minimize the documents, switching to MDI mode if needed first.
*/
void pExtendedWorkspace::minimize()
{
	setDocMode( dmMDI );
	foreach ( QWidget* w, mDocuments )
		w->showMinimized();
};

/*!
	\details Restore the documents, switching to MDI mode if needed first.
*/
void pExtendedWorkspace::restore()
{
	setDocMode( dmMDI );
	foreach ( QWidget* w, mDocuments )
		w->showNormal();
};
