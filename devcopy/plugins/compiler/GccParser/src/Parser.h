'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Compiler Plugins
** FileName  : Parser.h
** Date      : 2008-01-14T00:53:27
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author,
**             fill free to replace/append with your informations.
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
    \file Parser.h
    \date 2008-01-14T00:53:21
    \author Andrei Kopats
    \brief Set of regular expressions for parsing output of gcc and g++ compiler
'''

#ifndef PARSER_H
#define PARSER_H

#include <consolemanager/pConsoleManager.h>
#include <../../../monkey/src/consolemanager/CommandParser.h>

'''!
    \brief Set of regular expressions for parsing output of gcc and g++ compiler

    Allows to find errors and warnings in the output of compiler
'''
class Parser : public CommandParser
    Q_OBJECT
public:
    '''!
        Class constructor. Contatning regular expressions for known errors

        NOTE DO NOT NEED TO ADD SUPPORT OF ALL POSSIBLE ERRORS OF COMPILER
        Checking of every regular expression requires some time. More expressions - more time

        NOTE Try to avoid using expressions as '.*blabla', QRegExp should
        check all string for detect, it's according to regexp. It's requiring HUGE time
        Try always use something as  'blabla...'. For such regular expressions need to
        test just few symbols for understand, string not according to pattern
    '''
    Parser(QObject* parent):
            CommandParser (parent, PLUGIN_NAME)
        Pattern ps[] =
                #Error in the file/line
                QRegExp("^([\\w\\./]+\\.\\w+: In [\\w\\s]+ '.+':\\n)?"
                "(([^\\n]+[\\\\/])?([\\w.]+)):(\\d+):(\\d+:)?"
                "\\serror:\\s([^\\n]+)\\n",
                Qt.CaseSensitive,
                QRegExp.RegExp2), #reg exp
                "%2", #file name
                "%6", #column
                "%5", #row
                pConsoleManager.stError, #type
                "%4:%5: %7", #text
                "%0", #full text
            },
                # middle part of error
                # src/views/TreeViewModel.h:9: note:   because the following virtual functions are pure within 'TreeViewModel':
                QRegExp("^([\\w\\\\/\\.\\:\\d\\-]+):(\\d+): note:  ([^\\n]+)",
                Qt.CaseSensitive,
                QRegExp.RegExp2), #reg exp
                "%1", #file name
                "0", #column
                "%2", #row
                pConsoleManager.stError, #type
                "%3", #text
                "%0", #full text
            },
                #Warning in the file/line
                QRegExp("^([\\w\\./]+\\.\\w+: In [\\w\\s]+ '.+':\\n)?"
                "(([^\\n]+[\\\\/])?([\\w.]+)):(\\d+):(\\d+:)?"
                "\\swarning:\\s([^\\n]+)\\n",
                Qt.CaseSensitive,
                QRegExp.RegExp2), #reg exp
                "%2", #file name
                "%6", #column
                "%5", #row
                pConsoleManager.stWarning, #type
                "%4:%5: %7", #text
                "%0" #full text
            },
                #Building file
                QRegExp("^[gc][\\+c][\\+c] [^\\n]+ ([\\w\\\\/\\.]+\\.\\w+)()[\\r\\n]",
                Qt.CaseSensitive,
                QRegExp.RegExp2), #reg exp
                "%1", #file name
                "0", #column
                "0", #row
                pConsoleManager.stCompiling, #type
                "Compiling %1...", #text
                "%0" #full text
            },
                #Linking file
                QRegExp("^[gc][\\+c][\\+c]\\w+\\-o\\s+([^\\s]+)[^\\n]+[\\r\\n]", Qt.CaseSensitive, QRegExp.RegExp2), #reg exp
                "0", #file name
                "0", #column
                "0", #row
                pConsoleManager.stCompiling, #type
                "Linking %1...", #text
                "%0" #full text
            },
                #Undedined reference
                QRegExp("^([\\w\\./]+\\.o: (In function `[^']+':)\\n)?([\\w\\./]'''([\\w\\.]+)):(\\d+): (undefined reference to `[^']+')[\\r\\n]",
                Qt.CaseSensitive,
                QRegExp.RegExp2), #reg exp
                "%3", #file name
                "0", #column
                "%5", #row
                pConsoleManager.stError, #type
                "%4:%5: %6", #text
                "%3" #full text
            },
                #Missing library
                QRegExp("^/[\\w:/]+ld: cannot find -l(\\w+)[\\r\\n]", Qt.CaseSensitive, QRegExp.RegExp2), #reg exp
                "", #file name
                "", #column
                "", #row
                pConsoleManager.stError, #type
                "%1 library not finded", #text
                "%0" #full text
            },
            {  #FIXME It's moc's error
                #Class declaration lacks Q_OBJECT macro.
                QRegExp("^(\\w+\\.\\w){1,3}:(\\d+): Error: Class declarations lacks Q_OBJECT macro\\.[\\r\\n]", Qt.CaseSensitive, QRegExp.RegExp2), #reg exp
                "%1", #file name
                "", #column
                "%2", #row
                pConsoleManager.stError, #type
                "%0", #text
                "%0" #full text
            },
#ifdef Q_OS_MAC
            {  # MAC specific. Undefined symbol for architecture
                QRegExp("^(Undefined symbols for architecture \\w+:)\\n\\s+(\"[^\"]+\")[^\\n]+\\n[^\\n]+\\n", Qt.CaseSensitive, QRegExp.RegExp2), #reg exp
                "", #file name
                "", #column
                "", #row
                pConsoleManager.stError, #type
                "%1 %2", #text
                "%0" #full text
            },
            {  # MAC specific. Undefined symbol for architecture
                QRegExp("^(Undefined symbols:)\\n(  \"[\\w:\\(\\)\\, \\*]+\"), from:\\n\\s+[\\w\\:\\(\\)\\, \\*\\.]+", Qt.CaseSensitive, QRegExp.RegExp2), #reg exp
                "", #file name
                "", #column
                "", #row
                pConsoleManager.stError, #type
                "%1 %2", #text
                "%0" #full text
            },
#endif
            {QRegExp(), "", "", "", pConsoleManager.stUnknown,"",""} #self item must be last

        for ( i = 0; not ps[i].regExp.isEmpty(); i++)
            addPattern(ps[i])





#endif
