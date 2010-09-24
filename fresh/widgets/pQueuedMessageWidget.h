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
	\file pQueuedMessageWidget.h
	\date 2008-05-01T00:00:00
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A QMessageBox like Widget, that can show queued message.
*/
#ifndef PQUEUEDMESSAGEWIDGET_H
#define PQUEUEDMESSAGEWIDGET_H

#include "objects/MonkeyExport.h"

#include <QWidget>
#include <QHash>
#include <QDialogButtonBox>
#include <QPointer>
#include <QVariant>

class QLabel;
class QDialogButtonBox;

/*!
	\brief The is the \c message structure used by the pQueuedMessageWidget class.
	\details It allow to configure the message to show.
	\details Each variable is directly accessible and mostly optionnal except \c Message.
	\details A default \c Ok button is added if \c Buttons is empty.
*/
struct Q_MONKEY_EXPORT pQueuedMessage
{
	pQueuedMessage()
	{
		MilliSeconds = 0;
		Object = 0;
		Slot = 0;
	}
	
	bool operator==( const pQueuedMessage& o ) const
	{
		return Message == o.Message && MilliSeconds == o.MilliSeconds &&
			( Pixmap.cacheKey() == o.Pixmap.cacheKey() || ( Pixmap.isNull() && o.Pixmap.isNull() ) ) &&
			Background == o.Background && Foreground == o.Foreground && Buttons == o.Buttons &&
			Object == o.Object && Slot == o.Slot && UserData == o.UserData;
	}
	
	/*! \details The message to show */
	QString Message;
	/*! \details The millisecond time to wait before the message is auto closed. Use 0 for unilimited time */
	int MilliSeconds;
	/*! \details The pixmap to show before the message */
	QPixmap Pixmap;
	/*! \details The brush to use as background */
	QBrush Background;
	/*! \details The brush to use as foreground */
	QBrush Foreground;
	/*! \details A hash representing a StandardButton role, and it's optionnal text overridding the default StandardButton text */
	QHash<QDialogButtonBox::StandardButton, QString> Buttons; // StandardButton, Button Text ( empty for standard )
	/*! \details The object that is used to invoke \c Slot */
	QPointer<QObject> Object;
	/*!
		\details If \c Object is not null, it will invoke this \c Slot, the slot must take 2 parameters :
		\details QDialogButtonBox::StandardButton : The StandardButton clicked and
		\details pQueuedMessage : The message from where the button was clicked
	*/
	const char* Slot;
	/*! \details A place to stock custom user data */
	QVariant UserData;
};

/*!
	\brief A QMessageBox like Widget, that can show queued message.
	\details The messages are queued until they are closed by user or elapsed time is timeout
*/
class Q_MONKEY_EXPORT pQueuedMessageWidget : public QWidget
{
	Q_OBJECT
	
public:
	pQueuedMessageWidget( QWidget* parent = 0 );
	
	int messagesCount() const;
	pQueuedMessage currentMessage() const;

protected:
	QHash<int,pQueuedMessage> mMessages;
	static int pQueuedMessageUniqueId;
	QLabel* lPixmap;
	QLabel* lMessage;
	QDialogButtonBox* dbbButtons;

public slots:
	int append( const pQueuedMessage& message );
	int append( const QString& message, int milliseconds = 0, const QPixmap& pixmap = QPixmap(), const QBrush& background = QBrush( QColor( 255, 0, 0, 20 ) ), const QBrush& foreground = QBrush() );
	void remove( const pQueuedMessage& message );
	void remove( int id );
	void clear();

protected slots:
	void clicked( QAbstractButton* button );
	void showMessage();
	void closeMessage();

signals:
	void messageShown( const pQueuedMessage& message );
	void messageClosed( const pQueuedMessage& message );
	void cleared();
	void finished();
};

#endif // PQUEUEDMESSAGEWIDGET_H
