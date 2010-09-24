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
#include "pTabbedWorkspaceCorner.h"
#include "pTabbedWorkspaceCornerButton.h"
#include "pTabbedWorkspace.h"

#include <QPaintEvent>
#include <QPainter>
#include <QStyle>

#include <QDebug>

pTabbedWorkspaceCorner::pTabbedWorkspaceCorner( pTabbedWorkspace* w )
	: QWidget( w ), mWorkspace( w ), mLayout( new QBoxLayout( QBoxLayout::LeftToRight, this ) )
{
	/*
	QBoxLayout::LeftToRight
	QBoxLayout::RightToLeft
	QBoxLayout::TopToBottom
	QBoxLayout::BottomToTop
	*/

	mLayout->setSpacing( 3 );
	mLayout->setMargin( 0 );
}

pTabbedWorkspaceCorner::~pTabbedWorkspaceCorner()
{
	clearActions();
}

QBoxLayout::Direction pTabbedWorkspaceCorner::direction() const
{
	return mLayout->direction();
}

void pTabbedWorkspaceCorner::clearActions()
{
	qDeleteAll( findChildren<pTabbedWorkspaceCornerButton*>() );
}

void pTabbedWorkspaceCorner::setDirection( QBoxLayout::Direction d )
{
	// change buttons direction
	foreach ( pTabbedWorkspaceCornerButton* tb, findChildren<pTabbedWorkspaceCornerButton*>() )
		tb->setDirection( d );

	// change layout direction
	mLayout->setDirection( d );
}

void pTabbedWorkspaceCorner::addAction( QAction* a )
{
	// create button
	pTabbedWorkspaceCornerButton* tb = new pTabbedWorkspaceCornerButton( this );
	tb->setDefaultAction( a );
	tb->setDirection( direction() );

	// add to layout
	mLayout->addWidget( tb );
}

void pTabbedWorkspaceCorner::setActions( QList<QAction*> l )
{
	// hide to avoid flickering
	hide();

	// delete all buttons
	clearActions();

	// create button associated with actions
	foreach ( QAction* a, l )
		addAction( a );
	
	// show corner
	show();
}
