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
#ifndef PCONSOLE_H
#define PCONSOLE_H

#include "objects/MonkeyExport.h"
#include "pConsoleCommand.h"

#include <QPlainTextEdit>
#include <QMap>

class Q_MONKEY_EXPORT pConsole : public QPlainTextEdit
{
	Q_OBJECT

public:
	enum ColorType
	{
		ctCommand,
		ctError,
		ctOutput,
		ctCompletion
	};

	pConsole( QWidget* parent = 0 );
	virtual ~pConsole();

	QString prompt() const;
	void setPrompt( const QString& prompt );

	bool isPromptVisible() const;
	void setPromptVisible( bool visible );

	QStringList history() const;
	void setHistory( const QStringList& history );

	QColor color( ColorType type ) const;
	void setColor( ColorType type, const QColor& color );

	void executeCommand( const QString& command, bool writeCommand = true, bool showPrompt = true );

	bool saveScript( const QString& fileName );
	bool loadScript( const QString& fileName );

	void clear();
	void reset();

	pConsoleCommandList availableCommands() const;
	void setAvailableCommands( const pConsoleCommandList& commands );

	void addAvailableCommand( pConsoleCommand* command );
	void removeAvailableCommand( pConsoleCommand* command );

protected:
	QString mPrompt;
	QPoint mPromptPosition;
	QStringList mHistory;
	int mHistoryIndex;
	QString mTypedCommand;
	QMap<ColorType, QColor> mColors;
	QStringList mRecordedScript;
	pConsoleCommandList mAvailableCommands;

	virtual void keyPressEvent( QKeyEvent* event );
	virtual void mousePressEvent( QMouseEvent* event );
	virtual void mouseReleaseEvent( QMouseEvent* event );

	virtual bool isCommandComplete( const QString& command );
	virtual QString interpretCommand( const QString& command, int* result );
	virtual QStringList autocompleteCommand( const QString& command );

	bool replaceCommand( const QString& command );
	QString currentCommand() const;
	void focusCommand();

	void useColor( ColorType type );
	void displayPrompt();
	bool showHistoryItem( int index );

signals:
	void commandExecuted( const QString& command, int result );
};

#endif // PCONSOLE_H
