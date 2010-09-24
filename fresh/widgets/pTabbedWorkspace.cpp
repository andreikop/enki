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
#include "pTabbedWorkspace.h"
#include "pTabbedWorkspaceRightCorner.h"

#include <QBoxLayout>
#include <QStackedLayout>
#include <QStackedWidget>
#include <QWorkspace>
#include <QIcon>
#include <QCloseEvent>
#include <QFile>
#include <QMenu>

pTabbedWorkspace::pTabbedWorkspace( QWidget* p, pTabbedWorkspace::TabMode m )
	: QWidget( p )
{
	// tab widget
	mTabLayout = new QBoxLayout( QBoxLayout::LeftToRight );
	mTabLayout->setSpacing( 3 );
	mTabLayout->setMargin( 0 );
	mTabLayout->addWidget( ( mTabBar = new pTabBar ) );

	// document widget
	mStackedLayout = new QStackedLayout;
	mStackedLayout->addWidget( ( mStackedWidget = new QStackedWidget ) );
	mStackedLayout->addWidget( ( mWorkspaceWidget = new QWorkspace ) );
	mWorkspaceWidget->setScrollBarsEnabled( true );

	// main layout
	mLayout = new QBoxLayout( QBoxLayout::TopToBottom, this );
	mLayout->setSpacing( 0 );
	mLayout->setMargin( 0 );
	mLayout->addLayout( mTabLayout );
	mLayout->addLayout( mStackedLayout );

	// connections
	connect( mTabBar, SIGNAL( midButtonPressed( int, const QPoint& ) ), this, SLOT( internal_midButtonPressed( int, const QPoint& ) ) );
	connect( mTabBar, SIGNAL( closeButtonClicked( int ) ), this, SLOT( internal_closeButtonClicked( int ) ) );
	connect( mTabBar, SIGNAL( rightButtonPressed( int, const QPoint& ) ), this, SLOT( internal_rightButtonPressed( int, const QPoint& ) ) );
	connect( mTabBar, SIGNAL( tabDropped( int, int ) ), this, SLOT( internal_tabDropped( int, int ) ) );
	connect( mTabBar, SIGNAL( currentChanged( int ) ), this, SLOT( internal_currentChanged( int ) ) );
	connect( mWorkspaceWidget, SIGNAL( windowActivated( QWidget* ) ), this, SLOT( workspaceWidget_windowActivated( QWidget* ) ) );
	
	// init view
	setAttribute( Qt::WA_DeleteOnClose );
	mTabBar->setDrawBase( false );
	mTabBar->setSizePolicy( QSizePolicy( QSizePolicy::Expanding, QSizePolicy::Preferred ) );
	setCornerWidget( pTabbedWorkspaceRightCorner::instance( this ) );
	setTabMode( m );
	setDocumentMode( pTabbedWorkspace::dmMaximized );
}

pTabbedWorkspace::~pTabbedWorkspace()
{
	// close all document
	closeAllTabs( true );

	// delete all unclose document, if user click cancel
	qDeleteAll( mDocuments );

	// delete containers
	delete mStackedWidget;
	delete mWorkspaceWidget;
}

bool pTabbedWorkspace::eventFilter( QObject* o, QEvent* e )
{
	// get event type
	QEvent::Type t = e->type();
	
	// get document
	QWidget* td = qobject_cast<QWidget*>( o );
	
	// child modified state
	if ( t == QEvent::ModifiedChange )
		mTabBar->setTabText( indexOf( td ), td->windowTitle().append( td->isWindowModified() ? QString( "*" ) : QString::null ) );

	// if mode is toplevel and event is activate, activate correct window if needed
	else if ( mTabMode == tmTopLevel && t == QEvent::WindowActivate )
	{
		if ( td && td != currentDocument() )
			setCurrentDocument( td );
	}

	// remove document from workspace
	else if ( t == QEvent::Close && td )
	{
		// get closeevent
		QCloseEvent* ce = static_cast<QCloseEvent*>( e );
		
		// emit that document will be close, giving event so user can cancel it
		emit aboutToCloseTab( indexOf( td ), ce );
		emit aboutToCloseDocument( td, ce );
		
		// close document if accepted
		if ( !ce->isAccepted() && td->property( "ForceClose" ).toBool() && !td->testAttribute( Qt::WA_DeleteOnClose ) )
			td->deleteLater();
		else if ( ce->isAccepted() && !td->testAttribute( Qt::WA_DeleteOnClose ) )
			removeDocument( td );
		else
			return true;
	}

	// return default event filter
	return QWidget::eventFilter( o, e );
}

void pTabbedWorkspace::workspaceWidget_windowActivated( QWidget* w )
{ setCurrentDocument( w ); }

void pTabbedWorkspace::removeDocument( QObject* o )
{ removeDocument( qobject_cast<QWidget*>( o ) ); }

pTabBar* pTabbedWorkspace::tabBar() const
{ return mTabBar; }

QTabBar::Shape pTabbedWorkspace::tabShape() const
{ return mTabBar->shape(); }

pTabbedWorkspace::TabMode pTabbedWorkspace::tabMode() const
{ return mTabMode; }

pTabbedWorkspace::DocumentMode pTabbedWorkspace::documentMode() const
{ return mDocumentMode; }

void pTabbedWorkspace::setBackground( const QPixmap& p )
{ mWorkspaceWidget->setBackground( QBrush( p ) ); }

void pTabbedWorkspace::setBackground( const QString& s )
{ mWorkspaceWidget->setBackground( QBrush( QPixmap( s ) ) ); }

void pTabbedWorkspace::setTabShape( QTabBar::Shape s )
{
	if ( tabShape() != s )
	{
		// get sizepolicy
		QSizePolicy sp = mTabBar->sizePolicy();
		
		// update view layout
		switch ( s )
		{
		case QTabBar::RoundedNorth:
		case QTabBar::TriangularNorth:
			mTabLayout->setDirection( QBoxLayout::LeftToRight );
			mLayout->setDirection( QBoxLayout::TopToBottom );
			if ( tabShape() != QTabBar::RoundedSouth && tabShape() != QTabBar::TriangularSouth )
				sp.transpose();
			break;
		case QTabBar::RoundedSouth:
		case QTabBar::TriangularSouth:
			mTabLayout->setDirection( QBoxLayout::LeftToRight );
			mLayout->setDirection( QBoxLayout::BottomToTop );
			if ( tabShape() != QTabBar::RoundedNorth && tabShape() != QTabBar::TriangularNorth )
				sp.transpose();
			break;
		case QTabBar::RoundedWest:
		case QTabBar::TriangularWest:
			mTabLayout->setDirection( QBoxLayout::BottomToTop );
			mLayout->setDirection( QBoxLayout::LeftToRight );
			if ( tabShape() != QTabBar::RoundedEast && tabShape() != QTabBar::TriangularEast )
				sp.transpose();
			break;
		case QTabBar::RoundedEast:
		case QTabBar::TriangularEast:
			mTabLayout->setDirection( QBoxLayout::TopToBottom );
			mLayout->setDirection( QBoxLayout::RightToLeft );
			if ( tabShape() != QTabBar::RoundedWest && tabShape() != QTabBar::TriangularWest )
				sp.transpose();
			break;
		}
		
		// set size policy
		mTabBar->setSizePolicy( sp );
		
		// apply tab shape
		mTabBar->setShape( s );
		
		// update corners
		updateCorners();
		
		// emit shape changed
		emit tabShapeChanged( s );
	}
}

void pTabbedWorkspace::setTabMode( pTabbedWorkspace::TabMode t )
{
	if ( mTabMode != t )
	{
		// retain tab mode
		mTabMode = t;

		// retain current index
		int i = currentIndex();

		// show correct workspace
		switch ( mTabMode )
		{
		case tmSDI:
			if ( mStackedLayout->currentWidget() != mStackedWidget )
				mStackedLayout->setCurrentWidget( mStackedWidget );
			break;
		case tmMDI:
			if ( mStackedLayout->currentWidget() != mWorkspaceWidget )
				mStackedLayout->setCurrentWidget( mWorkspaceWidget );
			break;
		case tmTopLevel:
			if ( mStackedLayout->currentIndex() != -1 )
				mStackedLayout->setCurrentIndex( -1 );
			break;
		}

		// update view
		updateView();

		// restore current index
		setCurrentIndex( i );

		// emit tab mode changed
		emit tabModeChanged( mTabMode );
	}
}

void pTabbedWorkspace::setDocumentMode( pTabbedWorkspace::DocumentMode d )
{
	if ( mTabMode == pTabbedWorkspace::tmMDI /*&& mDocumentMode != d*/ )
	{
		// retain document mode
		mDocumentMode = d;

		// apply document layout
		switch( mDocumentMode )
		{
		case dmMaximized:
			foreach ( QWidget* td, documents() )
				if ( !td->isMaximized() )
					td->showMaximized();
			break;
		case dmCascade:
			mWorkspaceWidget->cascade();
			break;
		case dmTile:
			mWorkspaceWidget->tile();
			break;
		case dmIcons:
			mWorkspaceWidget->arrangeIcons();
			break;
		case dmMinimizeAll:
			foreach ( QWidget* td, documents() )
				if ( !td->isMinimized() )
					td->showMinimized();
			break;
		case dmRestoreAll:
			foreach ( QWidget* td, documents() )
				if ( td->isMaximized() || td->isMinimized() )
					td->showNormal();
			break;
		}

		// emit document mode changed
		emit documentModeChanged( mDocumentMode );
	}
}

int pTabbedWorkspace::currentIndex() const
{ return mTabBar->currentIndex(); }

void pTabbedWorkspace::setCurrentIndex( int i )
{
	if ( i != currentIndex() )
		mTabBar->setCurrentIndex( i );
	else if ( currentDocument() != document( i ) )
		internal_currentChanged( i );
}

void pTabbedWorkspace::internal_midButtonPressed( int i, const QPoint& )
{ document( i )->close(); }

void pTabbedWorkspace::internal_closeButtonClicked( int i )
{ document( i )->close(); }

void pTabbedWorkspace::internal_rightButtonPressed( int i, const QPoint& p )
{
	// create menu
	QMenu m( mTabBar );
	
	// create actions
	QAction* ac = m.addAction( tr( "&Close" ) );
	QAction* aca = m.addAction( tr( "Close &All" ) );
	
	// add action from tabbar
	/*
	m.addSeparator();
	m.addAction( mTabBar->toggleTabsHaveCloseButtonAction() );
	m.addAction( mTabBar->toggleTabsHaveShortcutAction() );
	m.addAction( mTabBar->toggleTabsElidedAction() );
	*/
	
	// execute menu
	if ( QAction* a = m.exec( p ) )
	{
		// if close
		if ( a == ac )
			document( i )->close();
		// close all
		else if ( a == aca )
			emit closeAllRequested();
	}
}

void pTabbedWorkspace::internal_tabDropped( int f, int t )
{
	// swap documents
	mDocuments.insert( t, mDocuments.takeAt( f ) );
	
	// reorder the stackedwidget widgets if needed
	if ( mTabMode == pTabbedWorkspace::tmSDI )
	{
		// remove all widget from stacked
		while ( mStackedWidget->count() )
			mStackedWidget->removeWidget( mStackedWidget->widget( 0 ) );
		// re inserts ordered to mDocuments
		foreach ( QWidget* w, mDocuments )
			mStackedWidget->addWidget( w );
	}
}

void pTabbedWorkspace::internal_currentChanged( int i )
{
	// get document
	QWidget* d = document( i );
	// set correct document visible
	if ( currentDocument() != d )
	{
		switch ( mTabMode )
		{
			case tmSDI:
				if ( mStackedWidget->currentIndex() != i )
					mStackedWidget->setCurrentIndex( i );
				break;
			case tmMDI:
				if ( d && mWorkspaceWidget->activeWindow() != d )
					mWorkspaceWidget->setActiveWindow( d );
			break;
			case tmTopLevel:
				if ( d )
				{
					d->raise();
					d->activateWindow();
				}
			break;
		}
	}
	// emit document change
	emit currentChanged( i );
}

QWidget* pTabbedWorkspace::currentDocument() const
{
	switch ( mTabMode )
	{
		case tmSDI:
			return mStackedWidget->currentWidget();
		case tmMDI:
			return  mWorkspaceWidget->activeWindow();
		case tmTopLevel:
			return QApplication::activeWindow();
		default:
#ifdef Q_CC_GNU
			Q_ASSERT_X( 0, __func__, "not right tab mode" );
#else
			Q_ASSERT( 0 );
#endif
			break;
	}
	return 0;
}

void pTabbedWorkspace::setCurrentDocument( QWidget* d )
{ setCurrentIndex( indexOf( d ) ); }

int pTabbedWorkspace::indexOf( QWidget* d ) const
{ return mDocuments.indexOf( d ); }

QWidget* pTabbedWorkspace::document( int i ) const
{ return mDocuments.value( i ); }

int pTabbedWorkspace::count() const
{ return mDocuments.count(); }

QList<QWidget*> pTabbedWorkspace::documents() const
{ return mDocuments; }

pTabbedWorkspaceCorner* pTabbedWorkspace::cornerWidget( Qt::Corner c ) const
{
	// if only one it s tabbar, no need to check
	if ( mTabLayout->count() == 1 )
		return 0;

	// get corner
	switch ( c )
	{
	case Qt::TopLeftCorner:
	case Qt::BottomLeftCorner:
		if ( mTabLayout->indexOf( mTabBar ) == 0 )
			return 0;
		return qobject_cast<pTabbedWorkspaceCorner*>( mTabLayout->itemAt( 0 )->widget() );
		break;
	case Qt::TopRightCorner:
	case Qt::BottomRightCorner:
		if ( mTabLayout->indexOf( mTabBar ) == mTabLayout->count() -1 )
			return 0;
		return qobject_cast<pTabbedWorkspaceCorner*>( mTabLayout->itemAt( mTabLayout->count() -1 )->widget() );
		break;
	}

	// shut up gcc warning
	return 0;
}

void pTabbedWorkspace::setCornerWidget( pTabbedWorkspaceCorner* w, Qt::Corner c )
{
	switch ( c )
	{
	case Qt::TopLeftCorner:
	case Qt::BottomLeftCorner:
		if ( mTabLayout->indexOf( mTabBar ) == 1 )
			delete mTabLayout->itemAt( 0 )->widget();
		mTabLayout->insertWidget( 0, w );
		break;
	case Qt::TopRightCorner:
	case Qt::BottomRightCorner:
		if ( mTabLayout->indexOf( mTabBar ) != mTabLayout->count() -1 )
			delete mTabLayout->itemAt( mTabLayout->count() -1 )->widget();
		mTabLayout->addWidget( w );
		break;
	}
}

void pTabbedWorkspace::updateCorners()
{
	// temp corner
	pTabbedWorkspaceCorner* c;

	// check left corner
	if ( ( c = cornerWidget( Qt::TopLeftCorner ) ) )
	{
		c->setDirection( mTabLayout->direction() );
		c->setEnabled( count() );
	}

	// check right corner
	if ( ( c = cornerWidget( Qt::TopRightCorner ) ) )
	{
		c->setDirection( mTabLayout->direction() );
		c->setEnabled( count() );
	}
}

void pTabbedWorkspace::updateView( QWidget* nd )
{
	// tmp list
	QList<QWidget*> l;
	if ( nd )
		l << nd;
	else
		l << mDocuments;

	// add document to correct workspace
	foreach ( QWidget* td, l )
	{
		// add to correct container
		switch ( mTabMode )
		{
		case tmSDI:
			mStackedWidget->addWidget( td );
			break;
		case tmMDI:
			mWorkspaceWidget->addWindow( td );
			mWorkspaceWidget->setActiveWindow( td );
			switch ( mDocumentMode )
			{
			case dmMaximized:
				if ( !td->isMaximized() )
					td->showMaximized();
				break;
			case dmCascade:
				if ( !td->isVisible() )
					td->show();
				if ( !l.isEmpty() && td == l.last() )
					mWorkspaceWidget->cascade();
				break;
			case dmTile:
				if ( !td->isVisible() )
					td->show();
				if ( !l.isEmpty() && td == l.last() )
					mWorkspaceWidget->tile();
				break;
			case dmIcons:
				if ( !td->isMinimized() )
					td->showMinimized();
				if ( !l.isEmpty() && td == l.last() )
					mWorkspaceWidget->arrangeIcons();
				break;
			case dmMinimizeAll:
				if ( !td->isMinimized() )
					td->showMinimized();
				break;
			case dmRestoreAll:
				if ( td->isMaximized() || td->isMinimized() )
					nd->showNormal();
				break;
			}
			break;
		case tmTopLevel:
			// remove from container
			if ( td->parent() )
				td->setParent( 0 );
			if ( !td->isVisible() )
				td->show();
			break;
		}	
	}

	// update corners
	updateCorners();
}

void pTabbedWorkspace::addDocument( QWidget* td, int i )
{
	if ( i == -1 )
		i = count();

	// set auto delete true
	td->setAttribute( Qt::WA_DeleteOnClose, true );
	
	// no force close
	td->setProperty( "ForceClose", false );

	// auto remove itself on delete
	connect( td, SIGNAL( destroyed( QObject* ) ), this, SLOT( removeDocument( QObject* ) ) );

	// filter the document
	td->installEventFilter( this );

	// append to document list
	mDocuments.insert( i, td );

	// update view
	updateView( td );

	// emit tab inserted
	emit tabInserted( i );

	// emit tab current changed
	emit currentChanged( i );
}

int pTabbedWorkspace::addTab( QWidget* td, const QString& l )
{ return insertTab( count(), td, l ); }

int pTabbedWorkspace::addTab( QWidget* td, const QIcon& i, const QString& l )
{ return insertTab( count(), td, i, l ); }

int pTabbedWorkspace::insertTab( int i, QWidget* td, const QString& l )
{ return insertTab( i, td, QIcon(), l ); }

int pTabbedWorkspace::insertTab( int j, QWidget* td, const QIcon& i, const QString& l )
{
	// if already in or not existing d, cancel
	if ( !td || mDocuments.contains( td ) )
		return -1;

	// insert document
	j = mTabBar->insertTab( j, l );
	addDocument( td, j );

	// set icon if not available
	mTabBar->setTabIcon( j, i );

	// return true index of the new document
	return j;
}

void pTabbedWorkspace::removeTab( int i )
{ removeDocument( document( i ) ); }

void pTabbedWorkspace::removeDocument( QWidget* td )
{
	if ( !td )
		return;

	// get document index
	int i = indexOf( td );

	// remove document from list
	mDocuments.removeAll( td );

	// remove from stacked to avoid crash
	if ( mTabMode == tmSDI )
		mStackedWidget->removeWidget( td );

	// remove tab and position to new index
	if ( i != -1 )
	{
		mTabBar->removeTab( i );
		updateCorners();

		emit tabRemoved( i );
		setCurrentIndex( currentIndex() );

		// emit current changed
		emit currentChanged( currentIndex() );
	}
}

void pTabbedWorkspace::closeCurrentTab()
{
	QWidget* td = currentDocument();
	if ( td )
		td->close();
}

void pTabbedWorkspace::closeAllTabs( bool b, bool bb )
{
	// block signal if needed
	bool bs = blockSignals( bb );
	
	// close all documents
	foreach ( QWidget* td, mDocuments )
	{
		td->setProperty( "ForceClose", b );
		td->close();
	}
	
	// restore previous block signals state
	blockSignals( bs );
}

void pTabbedWorkspace::activateNextDocument()
{
	int currIndex = currentIndex();
	if ( currIndex +1 == count() )
		setCurrentIndex( 0 );
	else
		setCurrentIndex( currIndex +1 );
}

void pTabbedWorkspace::activatePreviousDocument()
{
	int currIndex = currentIndex();
	if ( currIndex -1 == -1 )
		setCurrentIndex( count() -1 );
	else
		setCurrentIndex( currIndex -1 );
}
