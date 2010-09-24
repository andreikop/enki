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
#include "pQueuedMessageWidget.h"

#include <QLabel>
#include <QHBoxLayout>
#include <QTimer>
#include <QShowEvent>
#include <QPushButton>
#include <QStyle>
#include <QMetaMethod>

int pQueuedMessageWidget::pQueuedMessageUniqueId = 0;

/*!
	\details Create a new pQueuedMessageWidget object
	\param parent The parent widget
*/
pQueuedMessageWidget::pQueuedMessageWidget( QWidget* parent )
	: QWidget( parent )
{
	QFont font = this->font();
	font.setPointSize( 9 );
	setFont( font );
	// pixmap
	lPixmap = new QLabel( this );
	lPixmap->setAlignment( Qt::AlignCenter );
	lPixmap->setSizePolicy( QSizePolicy( QSizePolicy::Maximum, QSizePolicy::Preferred ) );
	// message
	lMessage = new QLabel( this );
	lMessage->setAlignment( Qt::AlignVCenter | Qt::AlignLeft );
	lMessage->setSizePolicy( QSizePolicy( QSizePolicy::Expanding, QSizePolicy::Maximum ) );
	lMessage->setWordWrap( true );
	// button
	dbbButtons = new QDialogButtonBox( this );
	dbbButtons->setSizePolicy( QSizePolicy( QSizePolicy::Maximum, QSizePolicy::Preferred ) );
	// layout
	QHBoxLayout* hbl = new QHBoxLayout( this );
	hbl->setMargin( 0 );
	hbl->addWidget( lPixmap, 0, Qt::AlignCenter );
	hbl->addWidget( lMessage );
	hbl->addWidget( dbbButtons, 0, Qt::AlignCenter );
	// connections
	connect( dbbButtons, SIGNAL( clicked( QAbstractButton* ) ), this, SLOT( clicked( QAbstractButton* ) ) );
}

/*!
	\details Return the number of message currently queued
*/
int pQueuedMessageWidget::messagesCount() const
{
	return mMessages.count();
}

pQueuedMessage pQueuedMessageWidget::currentMessage() const
{
	return mMessages.values().value( 0 );
}

/*!
	\details Append a message to the queued and return it's unique \c id
	\param message The message structure to add
*/
int pQueuedMessageWidget::append( const pQueuedMessage& message )
{
	if ( !mMessages.values().contains( message ) )
	{
		mMessages[pQueuedMessageUniqueId] = message;
		if ( mMessages.count() == 1 )
			QTimer::singleShot( 0, this, SLOT( showMessage() ) );
		return pQueuedMessageUniqueId++;
	}
	return mMessages.key( message );
}

/*!
	\details Append a message to the queued and return it's unique \c id
	\param message The message to show
	\param milliseconds The milliseconds to wait before the message is auto closed, use 0 for unlimited time
	\param pixmap The pixmap to use as icon
	\param background The brush background
	\param foreground The brush foreground
*/
int pQueuedMessageWidget::append( const QString& message, int milliseconds, const QPixmap& pixmap, const QBrush& background, const QBrush& foreground )
{
	pQueuedMessage m;
	m.Message = message;
	m.MilliSeconds = milliseconds;
	m.Pixmap = pixmap;
	m.Background = background;
	m.Foreground = foreground;
	return append( m );
}

/*!
	\details Remove a message from the queue
	\param message The message to remove
*/
void pQueuedMessageWidget::remove( const pQueuedMessage& message )
{ mMessages.remove( mMessages.key( message ) ); }

/*!
	\details Remove a message from the queue by it's id
	\param id The message id to remove
*/
void pQueuedMessageWidget::remove( int id )
{ mMessages.remove( id ); }

/*!
	\details Clear the current message
*/
void pQueuedMessageWidget::clear()
{
	lPixmap->clear();
	lMessage->clear();
	dbbButtons->clear();
	emit cleared();
}

void pQueuedMessageWidget::clicked( QAbstractButton* button )
{
	const pQueuedMessage msg = mMessages.begin().value();
	if ( msg.Object && msg.Slot )
		QMetaObject::invokeMethod( msg.Object, msg.Slot, Q_ARG( QDialogButtonBox::StandardButton, dbbButtons->standardButton( button ) ), Q_ARG( pQueuedMessage, msg ) );
	closeMessage();
}

/*!
	\details Show the curernt message.
	\details The widget must be visible as only the gui contents is updated.
*/
void pQueuedMessageWidget::showMessage()
{
	// get message
	pQueuedMessage msg = mMessages.begin().value();
	// set palette
	QPalette pal = style()->standardPalette();
	if ( msg.Foreground != QBrush() )
		pal.setBrush( lMessage->foregroundRole(), msg.Foreground );
	lMessage->setPalette( pal );
	// format widget
	lPixmap->setPixmap( msg.Pixmap );
	lMessage->setText( msg.Message );
	lMessage->setToolTip( msg.Message );
	lMessage->setWhatsThis( msg.Message );
	// set buttons
	if ( msg.Buttons.isEmpty() )
		msg.Buttons[ QDialogButtonBox::Ok ] = QString();
	dbbButtons->clear();
	foreach( QDialogButtonBox::StandardButton button, msg.Buttons.keys() )
	{
		QPushButton* pb = dbbButtons->addButton( button );
		if ( !msg.Buttons[ button ].isEmpty() )
			pb->setText( msg.Buttons[ button ] );
	}
	// auto close if needed
	if ( msg.MilliSeconds > 0 )
		QTimer::singleShot( msg.MilliSeconds, this, SLOT( closeMessage() ) );
	// emit signal
	emit messageShown( msg );
}

/*!
	\details Close the current shown message
*/
void pQueuedMessageWidget::closeMessage()
{
	// emit message
	emit messageClosed( mMessages.begin().value() );
	// remove remove current message from hash
	mMessages.erase( mMessages.begin() );
	// process next if possible, else clear gui
	QTimer::singleShot( 0, this, mMessages.count() > 0 ? SLOT( showMessage() ) : SLOT( clear() ) );
	// emit finished message if needed
	if ( mMessages.count() == 0 )
		emit finished();
}
