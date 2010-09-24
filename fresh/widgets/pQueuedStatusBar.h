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
	\file pQueuedStatusBar.h
	\date 2008-05-01T00:00:00
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A statusbar that handle a pQueuedMessageWidget
*/
#ifndef PQUEUEDSTATUSBAR_H
#define PQUEUEDSTATUSBAR_H

#include "objects/MonkeyExport.h"
#include "pQueuedMessageWidget.h"

#include <QStatusBar>

/*!
	\brief A statusbar that handle a pQueuedMessageWidget
	\details This status bar can show to the user non blocking queued messages
*/
class Q_MONKEY_EXPORT pQueuedStatusBar : public QStatusBar
{
	Q_OBJECT
	
public:
	pQueuedStatusBar( QWidget* parent = 0 );

protected:
	QPalette mDefaultPalette;
	pQueuedMessageWidget* mQueuedWidget;

public slots:
	int appendMessage( const pQueuedMessage& message );
	int appendMessage( const QString& message, int milliseconds = 0, const QPixmap& pixmap = QPixmap(), const QBrush& background = QBrush( QColor( 255, 0, 0, 20 ) ), const QBrush& foreground = QBrush() );
	void removeMessage( const pQueuedMessage& message );
	void removeMessage( int id );

protected slots:
	void messageShown( const pQueuedMessage& message );
	void messageCleared();
};

#endif // PQUEUEDSTATUSBAR_H
