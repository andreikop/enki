'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Andrei Kopats aka hlamer <hlamer@tut.by>
** Project   : Monkey Studio IDE
** FileName  : CommandParser.h
** Date      : 2008-01-14T00:36:50
** License   : GPL
** Home Page : http:#www.monkeystudio.org
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
'''!
    \file CommandParser.h
    \date 2008-01-14T00:36:50
    \author Andrei Kopats
    \brief Header for CommandParser class
'''

#ifndef COMMANDPARSER_H
#define COMMANDPARSER_H

#include "AbstractCommandParser.h"

'''!
    Class implements parsing based on patterns.
    It is used by the majority of parsers used in MkS (all parsers on 28-10-2009)
    See \ref CommandParser.Pattern
'''
class Q_MONKEY_EXPORT CommandParser : public AbstractCommandParser
    Q_OBJECT

public:
    #not  Install 'parser' command of MkS scripting interface
    static void installParserCommand()

    '''!
        Structure contains regular expression for searching some phrase
        in a console output of programm, also information, it should be
        used.

        FileName, col, row, Text, fields should contain text, which
        includes %d patterns (where d is any number)
        %d patterns will be replaced with submatching of regular expression, when
        parsing result are generated.
    '''
    struct Pattern
        QRegExp regExp
        QString FileName
        QString col
        QString row
        pConsoleManagerStep.Type Type
        QString Text
        QString FullText


protected:

    QString mName
    QList <Pattern> mPatterns

    QString replaceWithMatch( QRegExp&, QString)
    static QString parserCommandImplementation(  QString& command, arguments, status, MkSShellInterpreter* interpreter, data )

public:
    CommandParser(QObject* parent, name)
    QString name()
        return mName

    void addPattern( Pattern& pattern)
    void removePattern( QString& regExp)
    int processParsing(QString* text)


#endif # COMMANDPARSER_H
