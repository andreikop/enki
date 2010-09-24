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
#include "pTabBar.h"

#include <QMouseEvent>
#include <QApplication>
#include <QIcon>
#include <QPainter>
#include <QAction>

/*!
	\details Create a new pTabBar object
	\param parent The parent widget
*/
pTabBar::pTabBar( QWidget* parent )
	: QTabBar( parent )
{
	// set default colors
	mTabsColor = Qt::black;
	mCurrentTabColor = Qt::blue;
	
#ifdef Q_CC_MSVC
#pragma message("Deprecated uncomment code if needed this class")
#else
#warning Deprecated, uncomment code if needed this class
#endif

	/*
	// close button
	aToggleTabsHaveCloseButton = new pAction( "aTabbedTabsHaveShortcut", tr( "Tabs Have &Close Button" ), QKeySequence(), tr( "Tabbed Workspace" ) );
	aToggleTabsHaveCloseButton->setCheckable( true );
	
	// create actions for right tab
	aToggleTabsHaveShortcut = new pAction( "aTabbedTabsHaveShortcut", tr( "Tabs Have &Shortcut" ), QKeySequence(), tr( "Tabbed Workspace" ) );
	aToggleTabsHaveShortcut->setCheckable( true );
	
	// elid
	aToggleTabsElided = new pAction( "aTabbedTabsElided", tr( "Tabs Are &Elided" ), QKeySequence(), tr( "Tabbed Workspace" ) );
	aToggleTabsElided->setCheckable( true );
	*/
	
	// for accepting drop
	setAcceptDrops( true );
	
	// set mouse tracking
	setMouseTracking( true );
	
	// update tab text color on current changed
	connect( this, SIGNAL( currentChanged( int ) ), this, SLOT( resetTabsColor() ) );
	connect( this, SIGNAL( tabsColorChanged( const QColor& ) ), this, SLOT( resetTabsColor() ) );
	connect( this, SIGNAL( currentTabColorChanged( const QColor& ) ), this, SLOT( resetTabsColor() ) );
	connect( this, SIGNAL( tabsHaveCloseButtonChanged( bool ) ), this, SLOT( update() ) );
#ifdef Q_CC_MSVC
#pragma message("Uncomment")
#else
#warning Uncomment
#endif
	/*
	connect( aToggleTabsHaveCloseButton, SIGNAL( toggled( bool ) ), this, SLOT( setTabsHaveCloseButton( bool ) ) );
	connect( aToggleTabsHaveShortcut, SIGNAL( toggled( bool ) ), this, SLOT( setTabsHaveShortcut( bool ) ) );
	connect( aToggleTabsElided, SIGNAL( toggled( bool ) ), this, SLOT( setTabsElided( bool ) ) );
	*/
}

void pTabBar::paintEvent( QPaintEvent* event )
{
	// draw tabs
	QTabBar::paintEvent( event );
	
	// update button close
	if ( !aToggleTabsHaveCloseButton->isChecked() )
		return;
	
	// get tab
	int i = tabAt( mapFromGlobal( QCursor::pos() ) );
	if ( i != -1 )
	{
		// get close button rect
		QRect ir = iconRectForTab( i );
		
		// if mouse in close button rect
		if ( ir.contains( mapFromGlobal( QCursor::pos() ) ) )
		{
			// draw button
			QPainter p( this );
			p.drawPixmap( ir.topLeft(), QIcon( ":/file/icons/file/closeall.png" ).pixmap( iconSize(), QIcon::Active, isTabEnabled( i ) ? QIcon::On : QIcon::Off ) );
		}
	}
}

void pTabBar::mousePressEvent( QMouseEvent* event )
{
	// reset drag position
	dragStartPosition = QPoint();
	
	// get tab under cursor
	int i = tabAt( event->pos() );
	
	// if tab
	if ( i != -1 )
	{
		// emit left button pressed
		if ( event->button() == Qt::LeftButton )
			emit leftButtonPressed( i, event->globalPos() );
		
		// emit mid button pressed
		if ( event->button() == Qt::MidButton )
			emit midButtonPressed( i, event->globalPos() );
		
		// emit right button pressed and drag position
		if ( event->button() == Qt::RightButton )
		{
			emit rightButtonPressed( i, event->globalPos() );
			dragStartPosition = event->pos();
		}
	}
	
	// default event
	QTabBar::mousePressEvent( event );
}

void pTabBar::mouseReleaseEvent( QMouseEvent* event )
{
	// check button close clicked
	if ( aToggleTabsHaveCloseButton->isChecked() )
	{
		// get tab under cursor
		int i = tabAt( event->pos() );
		
		// if tab and left button and  tab icon pressed
		if ( i != -1 )
			if ( event->button() == Qt::LeftButton && inCloseButtonRect( i, event->pos() ) )
				emit closeButtonClicked( i );
	}
	
	// default event
	QTabBar::mouseReleaseEvent( event );
}

void pTabBar::mouseMoveEvent( QMouseEvent* event )
{
	if ( aToggleTabsHaveCloseButton->isChecked() )
	{
		// update icon state
		update();
	
		// change cursor if over button
		if ( inCloseButtonRect( tabAt( event->pos() ), event->pos() ) )
			setCursor( Qt::PointingHandCursor );
		else
			unsetCursor();
	}
	
	// need left button
	if ( event->buttons() != Qt::LeftButton )
		return;
	
	// need target tab and minimum drag distance
	if ( tabAt( event->pos() ) == -1 || ( event->pos() -dragStartPosition ).manhattanLength() < QApplication::startDragDistance() )
		return;

	// create mime
	QMimeData* m = new QMimeData;
	m->setData( "x-tabindex", QByteArray::number( tabAt( event->pos() ) ) );
	m->setData( "x-tabbar", QByteArray::number( reinterpret_cast<quintptr>( this ) ) );
	
	// create drag and set mime
	QDrag* d = new QDrag( this );
	d->setMimeData( m );
	
	// execute drag
	d->exec( Qt::MoveAction );
	
	// default event
	QTabBar::mouseMoveEvent( event );
}

void pTabBar::dragEnterEvent( QDragEnterEvent* event )
{
	// if correct mime and same tabbar
	if ( ( event->mimeData()->hasFormat( "x-tabindex" ) && event->mimeData()->hasFormat( "x-tabbar" ) 
		&& reinterpret_cast<pTabBar*>( QVariant( event->mimeData()->data( "x-tabbar" ) ).value<quintptr>() ) == this 
		&& tabAt( event->pos() ) != -1 ) || event->mimeData()->hasUrls() )
	{
		// accept drag
		event->acceptProposedAction();
	}
	
	// default event
	QTabBar::dragEnterEvent( event );
}

void pTabBar::dropEvent( QDropEvent* event )
{
	if ( !event->mimeData()->hasUrls() )
	{
		// get drop tab
		int ni = tabAt( event->pos() );
		
		// if get it
		if ( ni != -1 )
		{
			// get original tab infos
			int oi = event->mimeData()->data( "x-tabindex" ).toInt();
			QVariant otd = tabData( oi );
			QIcon oti = tabIcon( oi );
			QString ott = tabText( oi );
			QColor ottc = tabTextColor( oi );
			QString ottt = tabToolTip( oi );
			QString otwt = tabWhatsThis( oi );
			
			// remove original tab
			removeTab( oi );
			
			// insert new one with correct infos
			int i = insertTab( ni, oti, ott );
			setTabData( i, otd );
			setTabTextColor( i, ottc );
			setTabToolTip( i, ottt );
			setTabWhatsThis( i, otwt );
			
			//accept
			event->acceptProposedAction();
			
			// emit signal
			emit tabDropped( oi, i );
			
			// set new current index
			setCurrentIndex( i );
		}
	}
	else
		emit urlsDropped( event->mimeData()->urls () );
	
	// default event
	QTabBar::dropEvent( event );
}

void pTabBar::tabInserted( int i )
{
	// set chortcut if needed
	if ( tabsHaveShortcut() )
		updateTabsNumber( i );
}

void pTabBar::tabRemoved( int i )
{
	// set chortcut if needed
	if ( tabsHaveShortcut() )
		updateTabsNumber( i );
}

QRect pTabBar::iconRectForTab( int i )
{
	// get tab infos
	int x = 0, y = 0;
	QRect tr = tabRect( i );
	QSize sh = tr.size();
	
	switch ( shape() )
	{
		case QTabBar::RoundedNorth:
		case QTabBar::TriangularNorth:
			// calcul positions
			x = sh.width() -iconSize().width();
			y = ( sh.height() -iconSize().height() ) / 2;
			if ( currentIndex() == i )
			{
				y++;
				x -= 2;
			}
			else if ( currentIndex() != i )
			{
				y += 2;
				x--;
			}
			break;
		case QTabBar::RoundedSouth:
		case QTabBar::TriangularSouth:
			// calcul positions
			x = sh.width() -iconSize().width();
			y = ( sh.height() -iconSize().height() ) / 2;
			if ( currentIndex() == i )
				x -= 2;
			else if ( currentIndex() != i )
				x--;
			break;
		case QTabBar::RoundedWest:
		case QTabBar::TriangularWest:
			// calcul positions
			x = ( sh.width() -iconSize().height() ) / 2;
			if ( currentIndex() == i )
			{
				x++;
				y += 2;
			}
			else if ( currentIndex() != i )
			{
				x += 2;
				y += 2;
			}
			break;
		case QTabBar::RoundedEast:
		case QTabBar::TriangularEast:
			// calcul positions
			x = ( sh.width() -iconSize().height() ) / 2;
			y = sh.height() -iconSize().width();
			if ( currentIndex() == i )
			{
				x++;
				y -= 2;
			}
			else if ( currentIndex() != i )
			{
				x--;
				y -= 2;
			}
			break;
	}
	
	// return icon rect
	return QRect( tr.topLeft() +QPoint( x, y ), iconSize() );
}

bool pTabBar::inCloseButtonRect( int i, const QPoint& p )
{ return iconRectForTab( i ).contains( p ); }

/*!
	\details Redo the tabs color
*/
void pTabBar::resetTabsColor()
{
	for ( int i = 0; i < count(); i++ )
		setTabTextColor( i, i == currentIndex() ? currentTabColor() : tabsColor() );
}

/*!
	\details Return the tabs text color
*/
QColor pTabBar::tabsColor() const
{ return mTabsColor; }

/*!
	\details Set the tabs text color
	\param color The text color
*/
void pTabBar::setTabsColor( const QColor& color )
{
	if ( mTabsColor == color )
		return;
	mTabsColor = color;
	emit tabsColorChanged( mTabsColor );
}

/*!
	\details Return the current tab text color
*/
QColor pTabBar::currentTabColor() const
{ return mCurrentTabColor; }

/*!
	\details Set the current tab text color
	\param color The text color
*/
void pTabBar::setCurrentTabColor( const QColor& color )
{
	if ( mCurrentTabColor == color )
		return;
	mCurrentTabColor = color;
	emit currentTabColorChanged( mCurrentTabColor );
}

/*!
	\details Return true if tabs have a small close button else false
*/
bool pTabBar::tabsHaveCloseButton() const
{ return aToggleTabsHaveCloseButton->isChecked(); }

/*!
	\details Set if tabs have or not a small close button
	\param buttons True for buttons, else false
*/
void pTabBar::setTabsHaveCloseButton( bool buttons )
{
	if ( aToggleTabsHaveCloseButton->isChecked() == buttons && sender() != aToggleTabsHaveCloseButton )
		return;
	aToggleTabsHaveCloseButton->setChecked( buttons );
	setTabText( 0, tabText( 0 ) ); // workaround for tabs update
	emit tabsHaveCloseButtonChanged( aToggleTabsHaveCloseButton->isChecked() );
}

/*!
	\details Return true if tabs have shortcut else false
*/
bool pTabBar::tabsHaveShortcut() const
{ return aToggleTabsHaveShortcut->isChecked(); }

/*!
	\details Set if tabs have or not shortcut
	\param shortcuts True for shortcuts, else false
*/
void pTabBar::setTabsHaveShortcut( bool shortcuts )
{
	if ( aToggleTabsHaveShortcut->isChecked() == shortcuts && sender() != aToggleTabsHaveShortcut )
		return;
	aToggleTabsHaveShortcut->setChecked( shortcuts );
	updateTabsNumber();
	emit tabsHaveShortcutChanged( aToggleTabsHaveShortcut->isChecked() );
}

/*!
	\details Return true if tabs text is elided else false
*/
bool pTabBar::tabsElided() const
{ return  aToggleTabsElided->isChecked(); }

/*!
	\details Set if tabs text is elided or not
	\param elided True for elided text, else false
*/
void pTabBar::setTabsElided( bool elided )
{
	if ( aToggleTabsElided->isChecked() == elided && sender() != aToggleTabsElided )
		return;
	aToggleTabsElided->setChecked( elided );
	setElideMode( elided ? Qt::ElideMiddle : Qt::ElideNone );
	setTabText( 0, tabText( 0 ) ); // workaround for tabs update
	emit tabsElidedChanged( aToggleTabsElided->isChecked() );
}

void pTabBar::updateTabsNumber( int i )
{
	// fill i if i = -1 for complete update
	if ( i == -1 )
		i = 0;

	// loop documents starting at id i
	for ( int j = i; j < count(); j++ )
	{
		// only 10 tabs can have shortcut
		if ( j > 9 )
			return;

		// got tab text
		QString s = tabText( j );

		// look index of cut part
		int k = s.indexOf( ":" );

		// set new tab caption
		if ( tabsHaveShortcut() )
			setTabText( j, QString( "&%1: %2" ).arg( j ).arg( s.mid( k != -1 ? k +2 : 0 ) ) );
		else
			setTabText( j, s.mid( k != -1 ? k +2 : 0 ) );
	}
}

/*!
	\details Return a togglable QAction for managing the "Have close button" property
*/
QAction* pTabBar::toggleTabsHaveCloseButtonAction() const
{ return aToggleTabsHaveCloseButton; }

/*!
	\details Return a togglable QAction for managing the "Have shortcut" property
*/
QAction* pTabBar::toggleTabsHaveShortcutAction() const
{ return aToggleTabsHaveShortcut; }

/*!
	\details Return a togglable QAction for managing the "Text elided" property
*/
QAction* pTabBar::toggleTabsElidedAction() const
{ return aToggleTabsElided; }
