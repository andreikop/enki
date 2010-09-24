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
	\file pKeySequenceInput.h
	\date 2008-01-14T00:27:45
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A special QLineEdit that allow to defin QShortcut
*/
#ifndef PKEYSEQUENCEINPUT_H
#define PKEYSEQUENCEINPUT_H

#include "objects/MonkeyExport.h"

#include <QLineEdit>

/*!
	\brief A special QLineEdit that allow to defin QShortcut
	\details When the user press some combinaison keyx, the result is
	\details wrotten in the QLineEdit
*/
class Q_MONKEY_EXPORT pKeySequenceInput : public QLineEdit
{
	Q_OBJECT

public:
	pKeySequenceInput( QWidget* parent = 0 );

	QString checkKeyEvent( QKeyEvent* event );

protected:
	void keyPressEvent( QKeyEvent* event );
	void keyReleaseEvent( QKeyEvent* event );
};

#endif // PKEYSEQUENCEINPUT_H
