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
#include "pTabbedWorkspaceRightCorner.h"

#include <QMenu>
#include <QAction>
#include <QMetaEnum>

pTabbedWorkspaceRightCorner::pTabbedWorkspaceRightCorner( pTabbedWorkspace* p )
	: pTabbedWorkspaceCorner( p )
{
	// need workspace
	Q_ASSERT( p );

	// create menu
	QMenu* menu = new QMenu( this );
	menu->menuAction()->setText( "Close" );
	menu->menuAction()->setIcon( QIcon( ":/Icons/Icons/fileclose.png" ) );

	// create action group
	agTabShape = new QActionGroup( menu );
	agTabMode = new QActionGroup( menu );
	agDocumentMode = new QActionGroup( menu );

#ifdef Q_CC_MSVC
#pragma message("Deprecated, uncomment code if needed")
#else
#warning Deprecated, uncomment code if needed
#endif
	/*
	// fill enums in menu
	QMetaEnum e;

	// tab shape
	e = p->tabBar()->metaObject()->enumerator( p->tabBar()->metaObject()->indexOfEnumerator( "Shape" ) );
	for ( int i = 0; i < e.keyCount(); i++ )
	{
		pAction* a = new pAction( e.key( i ), e.key( i ), QKeySequence(), tr( "Tabbed Workspace/Shape Mode" ) );
		agTabShape->addAction( a );
		a->setCheckable( true );
		if ( p->tabShape() == e.value( i ) )
			a->setChecked( true );
		a->setData( i );
	}

	// tab mode
	e = p->metaObject()->enumerator( p->metaObject()->indexOfEnumerator( "TabMode" ) );
	for ( int i = 0; i < e.keyCount(); i++ )
	{
		pAction* a = new pAction( e.key( i ), e.key( i ), QKeySequence(), tr( "Tabbed Workspace/Tab Mode" ) );
		agTabMode->addAction( a );
		a->setCheckable( true );
		if ( p->tabMode() == e.value( i ) )
			a->setChecked( true );
		a->setData( i );
	}

	// document mode
	e = p->metaObject()->enumerator( p->metaObject()->indexOfEnumerator( "DocumentMode" ) );
	for ( int i = 0; i < e.keyCount(); i++ )
	{
		pAction* a = new pAction( e.key( i ), e.key( i ), QKeySequence(), tr( "Tabbed Workspace/Document Mode" ) );
		agDocumentMode->addAction( a );
		a->setData( i );
	}

	pAction* aTabbedCloseAll = new pAction( "aTabbedCloseAll", tr( "&Close All" ), QKeySequence(), tr( "Tabbed Workspace" ) );

	// add entries
	menu->addMenu( tr( "Tab Shape" ) )->addActions( agTabShape->actions() );
	menu->addMenu( tr( "Tab Mode" ) )->addActions( agTabMode->actions() );
	menu->addMenu( tr( "Document Mode" ) )->addActions( agDocumentMode->actions() );
	menu->addSeparator();
	menu->addAction( p->tabBar()->toggleTabsHaveCloseButtonAction() );
	menu->addAction( p->tabBar()->toggleTabsHaveShortcutAction() );
	menu->addAction( p->tabBar()->toggleTabsElidedAction() );
	menu->addAction( aTabbedCloseAll );

	connect( menu->menuAction(), SIGNAL( triggered() ), p, SLOT( closeCurrentTab() ) );

	connect( agTabShape, SIGNAL( triggered( QAction* ) ), this, SLOT( agTabShape_triggered( QAction* ) ) );
	connect( agTabMode, SIGNAL( triggered( QAction* ) ), this, SLOT( agTabMode_triggered( QAction* ) ) );
	connect( agDocumentMode, SIGNAL( triggered( QAction* ) ), this, SLOT( agDocumentMode_triggered( QAction* ) ) );

	connect( this, SIGNAL( requestChangeTabShape( QTabBar::Shape ) ), p, SLOT( setTabShape( QTabBar::Shape ) ) );
	connect( this, SIGNAL( requestChangeTabMode( pTabbedWorkspace::TabMode ) ), p, SLOT( setTabMode( pTabbedWorkspace::TabMode ) ) );
	connect( this, SIGNAL( requestChangeDocumentMode( pTabbedWorkspace::DocumentMode ) ), p, SLOT( setDocumentMode( pTabbedWorkspace::DocumentMode ) ) );

	connect( p, SIGNAL( tabShapeChanged( QTabBar::Shape ) ), this, SLOT( tabShapeChanged( QTabBar::Shape ) ) );
	connect( p, SIGNAL( tabModeChanged( pTabbedWorkspace::TabMode ) ), this, SLOT( tabModeChanged( pTabbedWorkspace::TabMode ) ) );
	connect( p, SIGNAL( documentModeChanged( pTabbedWorkspace::DocumentMode ) ), this, SLOT( documentModeChanged( pTabbedWorkspace::DocumentMode ) ) );

	connect( aTabbedCloseAll, SIGNAL( triggered() ), p, SIGNAL( closeAllRequested() ) );

	setActions( QList<QAction*>() << menu->menuAction() );
	*/
}

void pTabbedWorkspaceRightCorner::agTabShape_triggered( QAction* a )
{
	emit requestChangeTabShape( (QTabBar::Shape)a->data().toInt() );
}

void pTabbedWorkspaceRightCorner::agTabMode_triggered( QAction* a )
{
	emit requestChangeTabMode( (pTabbedWorkspace::TabMode)a->data().toInt() );
}

void pTabbedWorkspaceRightCorner::agDocumentMode_triggered( QAction* a )
{
	emit requestChangeDocumentMode( (pTabbedWorkspace::DocumentMode)a->data().toInt() );
}

void pTabbedWorkspaceRightCorner::tabShapeChanged( QTabBar::Shape s )
{
	QList<QAction*> l = agTabShape->actions();
	foreach ( QAction* a, l )
	{
		if ( a->data().toInt() == s )
		{
			if ( !a->isChecked() )
				a->setChecked( true );
			return;
		}
	}
}

void pTabbedWorkspaceRightCorner::tabModeChanged( pTabbedWorkspace::TabMode m )
{
	QList<QAction*> l = agTabMode->actions();
	foreach ( QAction* a, l )
	{
		if ( a->data().toInt() == m )
		{
			if ( !a->isChecked() )
				a->setChecked( true );
			agDocumentMode->setEnabled( m == pTabbedWorkspace::tmMDI ? true : false );
			return;
		}
	}
}

void pTabbedWorkspaceRightCorner::documentModeChanged( pTabbedWorkspace::DocumentMode m )
{
	QList<QAction*> l = agDocumentMode->actions();
	foreach ( QAction* a, l )
	{
		QFont f( a->font() );
		f.setBold( false );
		if ( a->data().toInt() == m )
			f.setBold( true );
		a->setFont( f );
	}
}
