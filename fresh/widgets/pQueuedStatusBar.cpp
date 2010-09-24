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
#include "pQueuedStatusBar.h"

/*!
	\details Create a new pQueuedStatusBar object
	\param parent The parent widget
*/
pQueuedStatusBar::pQueuedStatusBar( QWidget* parent )
	: QStatusBar( parent )
{
	mDefaultPalette = palette();
	// create pQueuedMessageWidget
	mQueuedWidget = new pQueuedMessageWidget( this );
	addWidget( mQueuedWidget, 100 );
	// connections
	connect( mQueuedWidget, SIGNAL( messageShown( const pQueuedMessage& ) ), this, SLOT( messageShown( const pQueuedMessage& ) ) );
	connect( mQueuedWidget, SIGNAL( cleared() ), this, SLOT( messageCleared() ) );
}

/*!
	\details Append a new message and return it's id
	\param message The message structure to show
*/
int pQueuedStatusBar::appendMessage( const pQueuedMessage& message )
{ return mQueuedWidget->append( message ); }

/*!
	\details Append a new message and return it's id
	\param message The message to show
	\param milliseconds The timeout before the message is auto closed, 0 for no timeout
	\param pixmap The pixmap to associate with the message
	\param background The background of the message
	\param foreground The foreground of the message
*/
int pQueuedStatusBar::appendMessage( const QString& message, int milliseconds, const QPixmap& pixmap, const QBrush& background, const QBrush& foreground )
{ return mQueuedWidget->append( message, milliseconds, pixmap, background, foreground ); }

/*!
	\details Remove a message from the queued list
	\param message The message structure to remove
*/
void pQueuedStatusBar::removeMessage( const pQueuedMessage& message )
{ mQueuedWidget->remove( message ); }

/*!
	\details Remove a message from the queued list
	\param id The message id to remove
*/
void pQueuedStatusBar::removeMessage( int id )
{ mQueuedWidget->remove( id ); }

void pQueuedStatusBar::messageShown( const pQueuedMessage& message )
{
	setAutoFillBackground( true );
	QPalette pal = mDefaultPalette;
	pal.setBrush( backgroundRole(), message.Background );
	setPalette( pal );
}

void pQueuedStatusBar::messageCleared()
{
	setAutoFillBackground( false );
	setPalette( mDefaultPalette );
}
