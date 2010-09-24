/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pAbbreviationsManager.h
** Date      : 2008-01-14T00:36:49
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
#ifndef PABBREVIATIONSMANAGER_H
#define PABBREVIATIONSMANAGER_H

#include <objects/MonkeyExport.h>

#include <QObject>
#include <QString>
#include <QList>

class pEditor;
class MkSShellInterpreter;

struct Q_MONKEY_EXPORT pAbbreviation
{
	pAbbreviation() {}
	pAbbreviation( const QString& m, const QString& d, const QString& l, const QString& s )
		: Macro( m ), Description( d ), Language( l ), Snippet( s ) {}

	QString Macro;
	QString Description;
	QString Language;
	QString Snippet;
	
	pAbbreviation& operator=( const pAbbreviation& other )
	{
		if ( *this != other )
		{
			Macro = other.Macro;
			Description = other.Description;
			Language = other.Language;
			Snippet = other.Snippet;
		}
		
		return *this;
	}

	bool operator==( const pAbbreviation& other ) const
	{
		return Macro == other.Macro && Description == other.Description &&
			Language == other.Language && Snippet == other.Snippet;
	}
	
	bool operator!=( const pAbbreviation& other ) const
	{
		return !operator==( other );
	}
};

typedef QList<pAbbreviation> pAbbreviationList;

class Q_MONKEY_EXPORT pAbbreviationsManager : public QObject
{
	Q_OBJECT
	friend class MonkeyCore;
	
public:
	pAbbreviationsManager( QObject* parent = 0 );
	
	void clear();
	void add( const pAbbreviation& abbreviation );
	void add( const pAbbreviationList& abbreviations );
	void set( const pAbbreviationList& abbreviations );
	void remove( const pAbbreviation& abbreviation );
	void remove( const pAbbreviationList& abbreviations );
	void remove( const QString& macro, const QString& language );
	const pAbbreviationList& abbreviations() const;
	pAbbreviation abbreviation( const QString& macro, const QString& language ) const;
	void expandMacro( pEditor* editor );
	void generateScript();

protected:
	pAbbreviationList mAbbreviations;
	
	void initialize();
	static QString commandInterpreter( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data );
};

#endif // PABBREVIATIONSMANAGER_H
