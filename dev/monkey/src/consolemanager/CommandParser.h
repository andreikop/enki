/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors   : Andrei Kopats aka hlamer <hlamer@tut.by>
** Project   : Monkey Studio IDE
** FileName  : CommandParser.h
** Date      : 2008-01-14T00:36:50
** License   : GPL
** Home Page : http://www.monkeystudio.org
**
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
**
****************************************************************************/
/*!
	\file CommandParser.h
	\date 2008-01-14T00:36:50
	\author Andrei Kopats
	\brief Header for CommandParser class
*/

#ifndef COMMANDPARSER_H
#define COMMANDPARSER_H

#include "AbstractCommandParser.h"

/*!
	Class implements parsing based on patterns.
	It is used by the majority of parsers used in MkS (all parsers on 28-10-2009)
	See \ref CommandParser::Pattern
*/
class Q_MONKEY_EXPORT CommandParser : public AbstractCommandParser
{
	Q_OBJECT
	
public:
	//! Install 'parser' command of MkS scripting interface
	static void installParserCommand();

	/*!
		Structure contains regular expression for searching some phrase
		in a console output of programm, and also information, how it should be 
		used.
		
		FileName, col, row, Text, FullText fields should contain text, which
		includes %d patterns (where d is any number)
		%d patterns will be replaced with submatching of regular expression, when
		parsing result are generated.
	*/
	struct Pattern
	{
		QRegExp regExp;
		QString FileName;
		QString col;
		QString row;
		pConsoleManagerStep::Type Type;
		QString Text;
		QString FullText;
	};
	
protected:
	
	QString mName;
	QList <Pattern> mPatterns;
	
	QString replaceWithMatch(const QRegExp&, QString);
	static QString parserCommandImplementation( const QString& command, const QStringList& arguments, int* status, class MkSShellInterpreter* interpreter, void* data );
	
public:
	CommandParser(QObject* parent, const QString& name);
	QString name() const
		{	return mName;	};
	void addPattern(const Pattern& pattern);
	void removePattern(const QString& regExp);
	int processParsing(QString* text);
};

#endif // COMMANDPARSER_H
