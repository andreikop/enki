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
#ifndef PCONSOLECOMMAND_H
#define PCONSOLECOMMAND_H

#include "objects/MonkeyExport.h"

#include <QStringList>
#include <QMetaType>

class Q_MONKEY_EXPORT pConsoleCommand
{
public:
	pConsoleCommand( const QStringList& commands = QStringList() );
	virtual ~pConsoleCommand();

	pConsoleCommand( const pConsoleCommand& other );
	pConsoleCommand& operator=( const pConsoleCommand& other );
	bool operator==( const pConsoleCommand& other ) const;
	bool operator!=( const pConsoleCommand& other ) const;

	QStringList commands() const;
	QStringList parseCommand( const QString& command ) const;
	QStringList autoCompleteList( const QString& command ) const;

	virtual bool isComplete( const QString& command ) const;
	virtual QString usage( const QString& command ) const;
	virtual QString interpret( const QString& command, int* result ) const;

protected:
	QStringList mCommands;
};

typedef QList<pConsoleCommand*> pConsoleCommandList;

Q_DECLARE_METATYPE( pConsoleCommand );
Q_DECLARE_METATYPE( pConsoleCommandList );

#endif // PCONSOLECOMMAND_H
