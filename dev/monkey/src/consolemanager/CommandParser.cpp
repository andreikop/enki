/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Andrei Kopats aka hlamer <hlamer@tut.by>
** Project   : Monkey Studio IDE
** FileName  : CommandParser.cpp
** Date      : 2008-01-14T00:36:50
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
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
	\brief Implementation of CommandParser class
*/

#include <QDebug>

#include "shellmanager/MkSShellInterpreter.h"
#include "coremanager/MonkeyCore.h"
#include "CommandParser.h"

/*!
	Change value of this macro, if you need to debug parsing or parsers, 
	and also check, how much time parsing takes
	A lot of debug info will be printed
*/
#define PARSERS_DEBUG 0

#if PARSERS_DEBUG
	#include <QTime>
#endif

//! Implementation for 'parser' MkS scripting interface command
QString CommandParser::parserCommandImplementation( const QString& command, const QStringList& arguments, int* status, class MkSShellInterpreter* interpreter, void* data )
{
	Q_UNUSED( interpreter );
	Q_UNUSED( data );
	CommandParser::Pattern pattern;
	
	if (9 != arguments.size())
	{
		if ( status )
		{
			*status = MkSShellInterpreter::InvalidCommand;
		}
		
		return QString("Command '%1' has 9 arguments").arg(command);
	}
	
	if (arguments[0] == "add")
	{
		pattern.regExp = QRegExp(arguments[2], Qt::CaseSensitive, QRegExp::RegExp2);
		pattern.FileName = arguments[3];
		pattern.col = arguments[4];
		pattern.row = arguments[5];
		
		if (arguments[6] == "error")
			pattern.Type = pConsoleManagerStep::Error;
		else if (arguments[6] == "warning")
			pattern.Type = pConsoleManagerStep::Warning;
		else if (arguments[6] == "compiling")
			pattern.Type = pConsoleManagerStep::Compiling;
		else if (arguments[6] == "finish")
			pattern.Type = pConsoleManagerStep::Finish;
		else if (arguments[6] == "good")
			pattern.Type = pConsoleManagerStep::Good;
		else if (arguments[6] == "bad")
			pattern.Type = pConsoleManagerStep::Bad;
		else if (arguments[6] == "invalid")
			pattern.Type = pConsoleManagerStep::Invalid;
		else
		{
			if ( status )
			{
				*status = MkSShellInterpreter::InvalidCommand;
			}
			
			return QString("Invalid type '%1'").arg(arguments[6]);
		}
		
		pattern.Text = arguments[7];
		pattern.FullText = arguments[8];
		
		AbstractCommandParser* parser = MonkeyCore::consoleManager()->getParser(arguments[1]);
		if (parser) // Already exists, add pattern
		{
			if (static_cast<CommandParser*>(parser))
			{
				static_cast<CommandParser*>(parser)->addPattern(pattern);
			}
			else
			{
				if ( status )
				{
					*status = MkSShellInterpreter::InvalidCommand;
				}
				
				return QString("Parser '%1' has invalid type").arg(arguments[1]);
			}
		}
		else // Create parser and add pattern
		{
			CommandParser* comParser = new CommandParser(MonkeyCore::consoleManager(), arguments[1]);
			comParser->addPattern(pattern);
			MonkeyCore::consoleManager()->addParser(comParser);
		}
	}
	else // Command is not "add"
	{
		if ( status )
		{
			*status = MkSShellInterpreter::InvalidCommand;
		}
		
		return QString("Invalid command %1").arg(arguments[0]);
	}
	
	if ( status )
	{
		*status = MkSShellInterpreter::NoError;
	}
	
	return QString::null;
}

void CommandParser::installParserCommand()
{
	QString help = tr( "This command allows to add and remove console output parsing patterns. Usage:\n"
						"\tparser add <name> <regular expression> <file name> <column> <row> <pattern type> <pattern text> <full text>\n"
						"\tparser remove <name> <regular expression>\n" );
	
	MkSShellInterpreter::instance()->addCommandImplementation( "parser", parserCommandImplementation, help, 0 );
}

CommandParser::CommandParser(QObject* parent, const QString& name):
	AbstractCommandParser(parent),
	mName(name)
{
}

void CommandParser::addPattern(const Pattern& pattern)
{
	foreach(const Pattern& p, mPatterns) {
		if (p.regExp.pattern() == pattern.regExp.pattern()) {
			qWarning() << "Duplicating regular expression " << p.regExp << "for" << name();
		}
	}
	
	mPatterns.append(pattern);
	
#if 0
	qDebug() << "Added pattern " << pattern.regExp.pattern() << 
									pattern.FileName << 
									pattern.col << 
									pattern.row << 
									pattern.Type << 
									pattern.Text << 
									pattern.FullText;
#endif
}

void CommandParser::removePattern(const QString& regExp)
{
	for (int i = 0; i < mPatterns.size(); i++)
	{
		if (mPatterns[i].regExp.pattern() == regExp)
		{
			mPatterns.removeAt(i);
			i--;
		}
	}
}

/*!
	see \ref AbstractCommandParser::processParsing
*/
int CommandParser::processParsing(QString* buf)
{
#if PARSERS_DEBUG
	static int allTime;
	static int total;
	QTime time1;
	time1.start();
#endif
	foreach ( const Pattern& p, mPatterns)
	{
		int pos = p.regExp.indexIn(*buf);
#if PARSERS_DEBUG
		qDebug () << "parser " << name();
		qDebug () << "parsing  " << *buf << "with" << p.regExp.pattern();
#endif
		if (pos != -1)
		{
			pConsoleManagerStep::Data data;
			data[ pConsoleManagerStep::TypeRole ] = p.Type;
			data[ pConsoleManagerStep::FileNameRole ] = replaceWithMatch(p.regExp,p.FileName);
			data[ pConsoleManagerStep::PositionRole ] = QPoint( replaceWithMatch(p.regExp,p.col).toInt(), replaceWithMatch(p.regExp,p.row).toInt()) -QPoint( 0, 1 );
			data[ Qt::DisplayRole ] = replaceWithMatch(p.regExp,p.Text);
			data[ Qt::ToolTipRole ] = replaceWithMatch(p.regExp,p.FullText);
			
			// emit signal
			emit newStepAvailable( pConsoleManagerStep( data ) );
			
#if PARSERS_DEBUG
			qDebug() << "Emited new step";
#endif
			
			int linesCount = p.regExp.cap().count ('\n');
			
			if (! p.regExp.cap().endsWith('\n'))
				linesCount++;
			
#if PARSERS_DEBUG
			qDebug () << "Capture :" << p.regExp.cap();
			qDebug () << "CaptureS :" << p.regExp.capturedTexts ();
			qDebug () << "Returning " << linesCount;
#endif
			return linesCount;
		}
#if PARSERS_DEBUG
			qDebug () << "Not matching";
#endif
	}
#if PARSERS_DEBUG
	allTime += time1.elapsed ();
	qDebug () << "All time" <<allTime;
	qDebug () << "Total count" <<total++;
	
	qDebug () << "Returning false";
#endif
	return 0;
}

/*!
	Function replaces sequences "%d" (where d is number) with matches 
	from regular expression. 

	%0 mean wall match, %n - nth submatch.
	Function is using for generating results of parsing
	\param rex Already matched regular expression (searching of a pattern 
		should be called before this function)
	\param s String, which contains %d (where d is number) patterns.
		Patterns will be replaced with according submatch of string
	\return Resulting string
*/
QString CommandParser::replaceWithMatch(const QRegExp& rex, QString s)
{
	int pos = 0; 
	int i = 0;
	while ( (i = s.indexOf("%", pos)) != -1)
	{
		pos = i;
		if ( ! s[i+1].isDigit () )
			continue;
		QString cap = rex.cap(s[i+1].digitValue ());
		if (cap.endsWith ("\n"))
			cap.chop(1);
		if (cap.endsWith ("\r"))
			cap.chop(1);
		s.replace (i,2,cap);
		pos += cap.size ();
	}
	return s;
}
