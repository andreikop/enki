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
#include "pDockToolBar.h"
#include "pDockToolBarManager.h"
#include "pTabbedWorkspaceCornerButton.h"

#include <QButtonGroup>
#include <QFrame>
#include <QBoxLayout>
#include <QEvent>
#include <QDockWidget>
#include <QAction>
#include <QMainWindow>
#include <QKeyEvent>

/*!
	\details Create a new object
	\param manager The pDockToolBarManager manager
	\param orientation The toolbar orientation
	\param window The main window
*/
pDockToolBar::pDockToolBar( pDockToolBarManager* manager, Qt::Orientation orientation, QMainWindow* window )
	: QToolBar( window ), mManager( manager ), mUniqueId( 0 )
{
	// need docktoolbar manager
	Q_ASSERT( manager != 0 );
	Q_UNUSED( manager );
	
	toggleViewAction()->setEnabled( false );
	toggleViewAction()->setVisible( false );
	
	// always show button text
	mTextAlwaysVisible = true;

	// toolbar is not movable
	setMovable( false );
	
	// toggle exclusive action
	aToggleExclusive = new QAction( this );
	aToggleExclusive->setCheckable( true );
	aToggleExclusive->setChecked( true );

	// change font
	QFont f( font() );
	f.setPixelSize( 11 );
	setFont( f );

	// set icon size
	setIconSize( QSize( 16, 16 ) );

	// create button frame
	mFrame = new QFrame;

	// create buttons layout
	mLayout = new QBoxLayout( QBoxLayout::LeftToRight, mFrame );
	mLayout->setMargin( 0 );
	mLayout->setSpacing( 0 );

	// add frame to toolbar
	aDockFrame = addWidget( mFrame );

	// connect orientation change
	connect( this, SIGNAL( orientationChanged( Qt::Orientation ) ), this, SLOT( internal_orientationChanged( Qt::Orientation ) ) );

	// set toolbar/layout orientation
	setOrientation( orientation );
}

bool pDockToolBar::eventFilter( QObject* object, QEvent* event )
{
	// get event type
	QEvent::Type type = event->type();
	// try casting object to dockwidget
	QDockWidget* dock = qobject_cast<QDockWidget*>( object );

	// if it s a dock widget
	if ( dock )
	{
		if ( type == QEvent::Show || type == QEvent::Hide )
		{
			// if exclusive, hide all except this one
			if ( type == QEvent::Show && aToggleExclusive->isChecked() )
			{
				foreach ( QDockWidget* dw, docks() )
				{
					if ( dw != dock && dw->isVisible() )
						dw->hide();
				}
			}

			// get dock button
			QAbstractButton* btn = button( dock );

			// check the dock button
			btn->setChecked( type == QEvent::Show );

			// check button text
			internal_checkButtonText( btn );

			// check toolbar visibility
			internal_checkVisibility();
		}
		else if ( type == QEvent::KeyPress )
		{
			if ( static_cast<QKeyEvent*>( event )->key() == Qt::Key_Escape )
				dock->hide();
		}
	}

	// deturn default event filter
	return QToolBar::eventFilter( object, event );
}

/*!
	\details Add an action into this pDockToolBar
	\param action The action to add, if null create a new separator action
	\param insert If true the action is inserted before the dock buttons, else it's append
	\return The added action
*/
QAction* pDockToolBar::addAction( QAction* action, bool insert )
{
	// create a separator if no action
	if ( !action )
	{
		action = new QAction( this );
		action->setSeparator( true );
	}

	if ( insert )
		QToolBar::insertAction( aDockFrame, action );
	else
		QToolBar::addAction( action );

	internal_checkVisibility();
	
	return action;
}

/*!
	\details Add actions into this pDockToolBar
	\param actions The actions to add
	\param insert If true the actions are inserted before the dock buttons, else they are append
*/
void pDockToolBar::addActions( QList<QAction*> actions, bool insert )
{
	if ( insert )
		QToolBar::insertActions( aDockFrame, actions );
	else
		QToolBar::addActions( actions );

	internal_checkVisibility();
}

/*!
	\details Add a dock in this toolbar, the dock is moved area if needed
	\param dock The dock to add
	\param title The dock button title
	\param icon The dock button icon
	\return Return the unique id that identify the dock
*/
int pDockToolBar::addDock( QDockWidget* dock, const QString& title, const QIcon& icon )
{	
	// cancel if no dock or dock already managed
	if ( !dock || id( dock ) != -1 )
		return -1;

	// check if this dock is already in another bar, and remove it
	pDockToolBar* tb = mManager->bar( mManager->dockWidgetAreaToToolBarArea( mManager->mainWindow()->dockWidgetArea( dock ) ) );
	if ( tb && tb->id( dock ) != -1 )
		tb->removeDock( dock );

	// set dock title
	if ( !title.isEmpty() )
		dock->setWindowTitle( title );

	// set object name if needed
	if ( dock->objectName().isEmpty() )
		dock->setObjectName( QString( "QDockWidget_%1" ).arg( title ).replace( " ", "_" ).trimmed() );

	// set dock icon
	if ( !icon.isNull() )
		dock->setWindowIcon( icon );

	// create button
	pTabbedWorkspaceCornerButton* pb = new pTabbedWorkspaceCornerButton( this, mManager->toolBarAreaToBoxLayoutDirection( mManager->mainWindow()->toolBarArea( this ) ) );
	pb->setCheckable( true );
	pb->setFont( font() );
	pb->setText( dock->windowTitle() );
	pb->setToolTip( pb->text() );
	pb->setProperty( "Caption", pb->text() );
	pb->setToolButtonStyle( Qt::ToolButtonTextBesideIcon );
	pb->setIconSize( iconSize() );
	pb->setIcon( icon );

	// add button to layout
	mLayout->addWidget( pb );

	// add dock to correct area
	Qt::DockWidgetArea da = mManager->mainWindow()->dockWidgetArea( dock );
	Qt::DockWidgetArea ta = mManager->toolBarAreaToDockWidgetArea( mManager->mainWindow()->toolBarArea( this ) );
	if ( da != ta )
		mManager->mainWindow()->addDockWidget( ta, dock, orientation() );

	// if exclusive, hide all dock except this one
	if ( aToggleExclusive->isChecked() && count() )
	{
		foreach ( QDockWidget* dw, docks() )
		{
			if ( dw->isVisible() )
				dw->hide();
		}
	}

	// check button according to dock visibility
	pb->setChecked( dock->isVisible() );

	// check button text
	internal_checkButtonText( pb );

	// add dock/button to list
	mButtons[mUniqueId] = pb;
	mDocks[mUniqueId] = dock;

	// filter the dock
	dock->installEventFilter( this );

	// connect
	connect( dock->toggleViewAction(), SIGNAL( changed() ), this, SLOT( internal_dockChanged() ) );
	connect( dock, SIGNAL( destroyed( QObject* ) ), this, SLOT( internal_dockDestroyed( QObject* ) ) );
	connect( pb, SIGNAL( clicked( bool ) ), this, SLOT( internal_buttonClicked( bool ) ) );

	// check if we need to hide/show the toolbar
	internal_checkVisibility();

	// return unique auto increment id of the dock
	return mUniqueId++;
}

/*!
	\details Unmanage a dock
	\param id The dock id
*/
void pDockToolBar::removeDock( int id )
{
	removeDock( dock( id ) );
}

/*!
	\details Unmanage a dock
	\param dock The dock to unmanage
*/
void pDockToolBar::removeDock( QDockWidget* dock )
{
	// get dock id
	int i = id( dock );

	// cancel if dock is not acutally own by this toolbar
	if ( i == -1 )
		return;
	
	// remove filter event
	dock->removeEventFilter( this );

	// disconnect
	disconnect( dock->toggleViewAction(), SIGNAL( changed() ), this, SLOT( internal_dockChanged() ) );
	disconnect( dock, SIGNAL( destroyed( QObject* ) ), this, SLOT( internal_dockDestroyed( QObject* ) ) );

	// delete button
	QAbstractButton* btn = button( dock );
	mButtons.remove( i );
	btn->deleteLater();

	// remove dock from list
	mDocks.remove( i );

	// check if we need to hide/show the toolbar
	internal_checkVisibility();
}

/*!
	\details Check a dock visibility
	\param id The dock id to check
*/
bool pDockToolBar::isDockVisible( int id ) const
{
	return isDockVisible( dock( id ) );
}

/*!
	\details Check a dock visibility
	\param dock The dock to check
*/
bool pDockToolBar::isDockVisible( QDockWidget* dock ) const
{
	// if dock is in internal list
	if ( id( dock ) != -1 )
		return button( dock )->isChecked();

	// else return widget visibility
	return dock ? dock->isVisible() : false;
}

/*!
	\details Set a dock visibility
	\param dock The dock
	\param visible The visible state
*/
void pDockToolBar::setDockVisible( QDockWidget* dock, bool visible )
{
	dock->setVisible( visible );
}

/*!
	\details Return true if the pDockToolBar buttons are exclusive, else false
*/
bool pDockToolBar::exclusive() const
{
	return aToggleExclusive->isChecked();
}

/*!
	\details Set this pDockToolBar exclusive, ie each dock button are exclusive meaning activating one will deactivate all others
	\param exclusive exclusive or not
*/
void pDockToolBar::setExclusive( bool exclusive )
{
	if ( aToggleExclusive->isChecked() == exclusive )
		return;
	aToggleExclusive->setChecked( exclusive );

	// if exclusive, hide all
	if ( aToggleExclusive->isChecked() && count() )
	{
		foreach ( QDockWidget* dw, docks() )
		{
			if ( dw->isVisible() )
				dw->hide();
		}
	}
}

/*!
	\details If parameter is yes, the text on button will always be shown, else they will be shwn only when they are active
	\param visible Text visibility
*/
void pDockToolBar::setTextAlwaysVisible( bool visible )
{
	mTextAlwaysVisible = visible;
	foreach ( QAbstractButton* ab, mButtons )
	{
		if ( mTextAlwaysVisible )
		{
			if ( ab->text().isEmpty() )
				ab->setText( ab->property( "Caption" ).toString() );
		}
		else
		{
			if ( ab->isChecked() && ab->text().isEmpty() )
				ab->setText( ab->property( "Caption" ).toString() );
			else if ( !ab->isChecked() && !ab->text().isEmpty() )
				ab->setText( QString() );
		}
	}
}

/*!
	\details Return true if button text is always shown, else false
*/
bool pDockToolBar::textAlwaysVisible() const
{
	return mTextAlwaysVisible;
}

/*!
	\details Return the id of the dock given in parameter
	\param dock The dock to get id from
*/
int pDockToolBar::id( QDockWidget* dock ) const
{
	return mDocks.values().contains( dock ) ? mDocks.key( dock ) : -1;
}

/*!
	\details Return the id of the button given in parameter
	\param button The button to get id from
*/
int pDockToolBar::id( QAbstractButton* button ) const
{
	return mButtons.values().contains( button ) ? mButtons.key( button ) : -1;
}

/*!
	\details Return the dock associated with the id given in parameter
	\param id The id of the dock to get
*/
QDockWidget* pDockToolBar::dock( int id ) const
{
	return mDocks.value( id );
}

/*!
	\details Return the dock associated with the button given in parameter
	\param button The button of the dock to get
*/
QDockWidget* pDockToolBar::dock( QAbstractButton* button ) const
{
	return dock( id( button ) );
}

/*!
	\details Return the button associated with the id given in parameter
	\param id The id of the button to get
*/
QAbstractButton* pDockToolBar::button( int id ) const
{
	return mButtons.value( id );
}

/*!
	\details Return the button associated with the dock given in parameter
	\param dock The dock of the button to get
*/
QAbstractButton* pDockToolBar::button( QDockWidget* dock ) const
{
	return button( id( dock ) );
}

/*!
	\details Return the docks list
*/
QList<QDockWidget*> pDockToolBar::docks() const
{
	return mDocks.values();
}

/*!
	\details Return the buttons list
*/
QList<QAbstractButton*> pDockToolBar::buttons() const
{
	return mButtons.values();
}

/*!
	\details Return the number of docks managed by this pDockToolBar
*/
int pDockToolBar::count() const
{
	return docks().count();
}

/*!
	\details Return the togglabe exclusive action associated with this pDockToolBar
*/
QAction* pDockToolBar::toggleExclusiveAction() const 
{
	// set action text
	aToggleExclusive->setText( tr( "%1 exclusive" ).arg( windowTitle() ) );
	return aToggleExclusive;
}

void pDockToolBar::internal_checkVisibility()
{
	// count toolbar actions, if 1 it s dockframe
	int i = actions().count();

	// need show ?!
	if ( !isVisible() && ( i > 1 || ( i == 1 && count() ) ) )
		show();
	// need hide ?!
	else if ( isVisible() && ( i == 1 && !count() ) )
		hide();
}

void pDockToolBar::internal_checkButtonText( QAbstractButton* b )
{
	// cancel if no button
	if ( !b )
		return;
	// show text when checked, else not
	if ( !mTextAlwaysVisible )
	{
		if ( b->isChecked() && b->text().isEmpty() )
			b->setText( b->property( "Caption" ).toString() );
		else if ( !b->isChecked() && !b->text().isEmpty() )
			b->setText( QString() );
	}
}

void pDockToolBar::internal_orientationChanged( Qt::Orientation o )
{
	// change layout direction
	switch ( o )
	{
		case Qt::Horizontal:
			mLayout->setDirection( QBoxLayout::LeftToRight );
			break;
		case Qt::Vertical:
			mLayout->setDirection( QBoxLayout::TopToBottom );
			break;
	}

	// layout docks
	foreach ( QDockWidget* d, mDocks )
		mManager->mainWindow()->addDockWidget( mManager->mainWindow()->dockWidgetArea( d ), d, o );
}

void pDockToolBar::internal_dockChanged()
{
	// get dock action
	QAction* a = qobject_cast<QAction*>( sender() );

	// get dock
	QDockWidget* d = qobject_cast<QDockWidget*>( a->parent() );

	// no position changed, return
	if ( !d || d->isFloating() || pDockToolBarManager::dockWidgetAreaToToolBarArea( mManager->mainWindow()->dockWidgetArea( d ) ) == mManager->mainWindow()->toolBarArea( this ) )
		return;
	else
		emit dockWidgetAreaChanged( d, this );
}

void pDockToolBar::internal_dockDestroyed( QObject* o )
{
	QDockWidget* d = reinterpret_cast<QDockWidget*>( o ); // qobject_cast<QDockWidget*>( o ); qobject_cast don't work with QDockWidget in destroyed emits :|
	
	// get dock id
	int i = id( d );

	// cancel if dock is not acutally own by this toolbar
	if ( i == -1 )
		return;
	
	// remove filter event
	d->removeEventFilter( this );

	// delete button
	QAbstractButton* b = button( d );
	mButtons.remove( i );
	b->deleteLater();

	// remove dock from list
	mDocks.remove( i );

	// check if we need to hide/show the toolbar
	internal_checkVisibility();
}

void pDockToolBar::internal_buttonClicked( bool b )
{
	// get button
	QAbstractButton* ab = qobject_cast<QAbstractButton*>( sender() );

	// get dock
	QDockWidget* d = dock( ab );

	// return if no dock
	if ( !d )
		return;

	if ( aToggleExclusive->isChecked() )
	{
		foreach ( QDockWidget* dw, docks() )
		{
			if ( dw != d && dw->isVisible() )
				dw->hide();
		}
	}

	// update button text
	internal_checkButtonText( ab );

	// show/hide dock according to b
	if ( d->isVisible() != b )
		d->setVisible( b );

	// emit button clicked
	emit buttonClicked( id( dock( ab ) ) );
}
