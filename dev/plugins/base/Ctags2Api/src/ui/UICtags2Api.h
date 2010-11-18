/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UICtags2Api.h
** Date      : 2008-01-14T00:39:52
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
#ifndef UICTAGS2API_H
#define UICTAGS2API_H

#include "ui_UICtags2Api.h"

#include <QHash>
#include <QByteArray>

struct CtagsEntity
{
	CtagsEntity( const QString& s ) { mList = s.split( '\t' ); }
	
	QString getName() const { return mList.value( 0 ).trimmed(); }
	QString getFile() const { return mList.value( 1 ).trimmed(); }
	QString getAddress() const { return mList.value( 2 ).trimmed(); }
	QString getFieldValue( const QString& s ) const
	{
		// field are new format, and old is only 3 part separated by '\t'
		if ( mList.count() == 3 || s.isEmpty() )
			return QString();
		
		for ( int i = 3; i < mList.count(); i++ )
		{
			QString f = mList.at( i );
			// special case kind
			if ( !f.contains( ':' ) && s == "kind" )
				return f.trimmed();
			// special case file
			if ( f == "file:" )
				return getFile();
			// generic way
			QStringList l = f.split( ':' );
			if ( l.at( 0 ) == s )
				return l.value( 1 ).trimmed().replace( "\\t", "\t" ).replace( "\\r", "\r" ).replace( "\\n", "\n" ).replace( "\\\\", "\\" );
		}
		return QString();
	}
	QString getKindValue() const { return getFieldValue( "kind" ); }
	QString getKindDefaultField() const
	{
		// get kind
		const QString s = getKindValue();
		// if empty return null string
		if ( s.isEmpty() )
			return QString();
		// get value
		if ( s == "c" )
			return "class";
		else if ( s == "d" )
			return QString();
		else if ( s == "e" )
			return "enum";
		else if ( s == "f" )
			return "function";
		else if ( s == "F" )
			return "file";
		else if ( s == "g" )
			return QString();
		else if ( s == "m" )
		{
			if ( !getFieldValue( "class" ).isEmpty() )
				return "class";
			else if ( !getFieldValue( "struct" ).isEmpty() )
				return "struct";
			return QString();
		}
		else if ( s == "p" )
			return QString();
		else if ( s == "s" )
			return "struct";
		else if ( s == "t" )
			return "typeref";
		else if ( s == "u" )
			return "union";
		else if ( s == "v" )
			return QString();
		return QString();
	}
	QString getKindDefaultValue() const { return getFieldValue( getKindDefaultField() ); }
	
	QStringList mList;
};

class UICtags2Api : public QDialog, public Ui::UICtags2Api
{
	Q_OBJECT

public:
	UICtags2Api( QWidget* = 0 );
	~UICtags2Api();

	QList<QByteArray> getFileContent( const QString& );

protected:
	QHash<QString, QList<QByteArray> > mFileCache;

protected slots:
	void on_tbCtagsBinary_clicked();
	void on_cbGenerateFrom_currentIndexChanged( int );
	void on_tbBrowse_clicked();
	void on_tbSrcPathBrowse_clicked();
	bool processCtagsBuffer( const QByteArray& );
	bool processCtags( const QString& );
	bool processCtags2Api( const QString& );
	void accept();

};

#endif // UICTAGS2API_H
