'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pAbbreviationsManager.h
** Date      : 2008-01-14T00:36:49
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
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
#ifndef PABBREVIATIONSMANAGER_H
#define PABBREVIATIONSMANAGER_H

#include <objects/MonkeyExport.h>

#include <QObject>
#include <QString>
#include <QList>

class pEditor
class MkSShellInterpreter

struct Q_MONKEY_EXPORT pAbbreviation
    pAbbreviation()    pAbbreviation(  QString& m, d, l, s )
            : Macro( m ), Description( d ), Language( l ), Snippet( s )
    QString Macro
    QString Description
    QString Language
    QString Snippet

    pAbbreviation& operator=(  pAbbreviation& other )
        if  *self != other :
            Macro = other.Macro
            Description = other.Description
            Language = other.Language
            Snippet = other.Snippet


        return *self


    bool operator==(  pAbbreviation& other )
        return Macro == other.Macro and Description == other.Description and
               Language == other.Language and Snippet == other.Snippet


    bool operator!=(  pAbbreviation& other )
        return not operator==( other )



typedef QList<pAbbreviation> pAbbreviationList

class Q_MONKEY_EXPORT pAbbreviationsManager : public QObject
    Q_OBJECT
    friend class MonkeyCore

public:
    pAbbreviationsManager( parent = 0 )

    void clear()
    void add(  pAbbreviation& abbreviation )
    void add(  pAbbreviationList& abbreviations )
    void set(  pAbbreviationList& abbreviations )
    void remove(  pAbbreviation& abbreviation )
    void remove(  pAbbreviationList& abbreviations )
    void remove(  QString& macro, language )
     pAbbreviationList& abbreviations()
    pAbbreviation abbreviation(  QString& macro, language )
    void expandMacro( pEditor* editor )
    void generateScript()

protected:
    pAbbreviationList mAbbreviations

    void initialize()
    static QString commandInterpreter(  QString& command, arguments, result, interpreter, data )


#endif # PABBREVIATIONSMANAGER_H
