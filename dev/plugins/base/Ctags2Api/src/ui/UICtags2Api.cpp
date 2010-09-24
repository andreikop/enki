/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UICtags2Api.cpp
** Date      : 2008-01-14T00:39:51
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
#include "UICtags2Api.h"

#include <pMonkeyStudio.h>

#include <QPushButton>
#include <QRegExp>
#include <QFile>
#include <QBuffer>
#include <QTextCodec>
#include <QProcess>

using namespace pMonkeyStudio;

int bracesDiff( const QByteArray& s )
{
	int diff = 0;
	int mode = 0; // 0 <=> default, 1 <=> comment, 2 <=> string
	for ( int i = 0; i < s.count(); i++ )
	{
		if ( mode == 0 ) // default
		{
			if ( s[i] == '(' )
				diff++;
			else if ( s[i] == ')' )
				diff--;
			else if ( s[i] == '"' )
				mode = 2;
			else if ( i > 0 && s[i -1] == '/' && s[i] == '/' )
				return diff;
			else if ( i > 0 && s[i -1] == '/' && s[i] == '*' )
				mode = 1;
		}
		else if ( mode == 1 ) //  comment
		{
			if ( i > 0 && s[i -1] == '*' && s[i] == '/' )
				mode = 0;
		}
		else if ( mode == 2 ) // string
		{
			if ( s[i] == '"' )
				mode = 0;
		}
	}
	return diff;
}

UICtags2Api::UICtags2Api( QWidget* w )
	: QDialog( w )
{
	setupUi( this );
	cbGenerateFrom->setCurrentIndex( 0 );
	pbLoading->setVisible( false );
	dbbButtons->button( QDialogButtonBox::Ok )->setIcon( QPixmap( ":/icons/icons/ok.png" ) );
	dbbButtons->button( QDialogButtonBox::Close )->setIcon( QPixmap( ":/icons/icons/cancel.png" ) );
}

UICtags2Api::~UICtags2Api()
{
	// clear cached files
	mFileCache.clear();
}

QList<QByteArray> UICtags2Api::getFileContent( const QString& s )
{
	QString fn = QDir::toNativeSeparators( s );
	if ( mFileCache.contains( fn ) )
		return mFileCache[fn];
	// create caching file
	QFile f( fn );
	if ( !f.open( QFile::ReadOnly | QFile::Text ) )
		return QList<QByteArray>();
	// read lines
	while ( !f.atEnd() )
		mFileCache[fn] << f.readLine();
	// return content
	return mFileCache[fn];
}

void UICtags2Api::on_tbCtagsBinary_clicked()
{
	QString s = getOpenFileName( tr( "Select the ctags binary file" ), leCtagsBinary->text(), QString::null, this );
	if ( !s.isNull() )
		leCtagsBinary->setText( s );
}

void UICtags2Api::on_cbGenerateFrom_currentIndexChanged( int i )
{
	leSrcPath->setEnabled( i == 1 );
	tbSrcPathBrowse->setEnabled( i == 1 );
}

void UICtags2Api::on_tbBrowse_clicked()
{
	QString c, s;
	switch( cbGenerateFrom->currentIndex() )
	{
		case 0: // include
			s = getExistingDirectory( tr( "Select the include path to scan" ), leLabel->text(), this );
			break;
		case 1: // ctags
			s = getOpenFileName( tr( "Select the tags file to convert" ), leLabel->text(), tr( "Ctags File (tags *.tags)" ), this );
			break;
	}
	if ( !s.isNull() )
		leLabel->setText( s );
}

void UICtags2Api::on_tbSrcPathBrowse_clicked()
{
	QString s = getExistingDirectory( tr( "Select the directory from witch you generated this tags file" ), leSrcPath->text(), this );
	if ( !s.isNull() )
		leSrcPath->setText( s );
}

bool UICtags2Api::processCtagsBuffer( const QByteArray& a )
{
	// cancel if no buffer
	if ( a.isEmpty() )
		return false;
	
	// create io buffer
	QBuffer b;
	b.setData( a );
	if ( !b.open( QBuffer::ReadOnly | QFile::Text ) )
		return false;
	
	// set progress bar
	pbLoading->setVisible( true );
	pbLoading->setValue( 0 );
	pbLoading->setMaximum( a.split( '\n' ).count() -1 );
	
	// process buffer
	QList<QByteArray> lb, contents;
	QByteArray curDef, rt;
	QString c;
	int braces = 0, curLineNo = 0;
	
	// check each line
	while ( b.canReadLine() )
	{
		// get line
		const QString l = QTextCodec::codecForLocale()->toUnicode( b.readLine() );
		// if no comment line
		if ( l.split( '\t' ).count() > 3 && l[0] != '!' )
		{
			// create ctags entity
			CtagsEntity e( l );
			// get line in file
			c = e.getAddress();
			curLineNo = c.left( c.length() -2 ).toInt() -1; // -1 because line numbers in tags file start at 1.
			// get correct path
			QString d = QFileInfo( leLabel->text() ).isDir() ? leLabel->text() : QFileInfo( leLabel->text() ).absolutePath();
			if ( cbGenerateFrom->currentIndex() == 1 && !leSrcPath->text().isEmpty() )
				d = leSrcPath->text();
			// cache file
			contents = getFileContent( e.getFile().prepend( "/" ).prepend( d ) );
			// checking entity
			if ( !contents.isEmpty() && ( !cbRemovePrivate->isChecked() || e.getName()[0] != '_' ) && !e.getName().startsWith( "operator " ) )
			{
				// get kind value
				c = e.getKindValue();
				// kind...
				if ( c == "p" || c == "f" )
				{
					curDef = contents[curLineNo];
					braces = bracesDiff( curDef );
					while ( braces > 0 ) // search end of prototype.
					{
						curLineNo++;
						braces = braces +bracesDiff( contents[curLineNo] );
						curDef = curDef +contents[curLineNo];
					}
					// Replace whitespace sequences with a single space character.
					curDef = curDef.simplified();
					// Qt slot
					if ( QString( curDef ).contains( QRegExp( "Q_.*_SLOT" ) ) || QString( curDef ).contains( QRegExp( "QT_.*" ) ) )
					{
						// cancel because internal member
						curDef.clear();
						//qWarning( QString( curDef ).replace( QRegExp( "^Q_PRIVATE_SLOT\\(.*,(.*)\\)" ), "\\1" ).toAscii() );
					}
					// Remove space around the '('.
					curDef.replace( " (", "(" ).replace( "( ", "(" );
					// Remove space around the ')'.
					curDef.replace( " )", ")" );
					// Remove trailing semicolon.
					curDef.replace( ";", "" );
					// Remove implementation if present.
					if ( curDef.contains( "{" ) )
					{
						if ( curDef.contains( "}" ) )
						{
							int startImpl = curDef.indexOf( "{" );
							int endImpl = curDef.indexOf( "}" );
							curDef.remove( startImpl, endImpl -startImpl +1 );
						}
						else
						{
							// Remove trailing brace.
							curDef.remove( curDef.lastIndexOf( "{" ), 1 );
						}
					}
					// get return type.
					rt = curDef.mid( 0, curDef.indexOf( e.getName() ) ).simplified();
					// remove return type.
					curDef = curDef.mid( curDef.indexOf( e.getName() ) ).trimmed();
					// remove final comment
					if ( curDef.contains( "//" ) )
					{
						int cs = curDef.indexOf( "//" );
						int bs = curDef.indexOf( ")" );
						if ( cs > bs )
							curDef = curDef.left( cs ).trimmed();
					}
					// Remove virtual indicator.
					if ( curDef.trimmed().replace( " ", "" ).endsWith( ")=0" ) )
					{
						curDef.remove( curDef.lastIndexOf( "0" ), 1 );
						curDef.remove( curDef.lastIndexOf( "=" ), 1 );
					}
					// Remove trailing space.
					curDef = curDef.trimmed();
					// winmode
					if ( cbWindowsMode->isChecked() )
					{
						if ( curDef.contains( "A(" ) && cbLetter->currentText() == "A" )
							curDef.replace( "A(", "(" );
						else if ( curDef.contains( "W(" ) && cbLetter->currentText() == "W" )
							curDef.replace( "W(", "(" );
					}
				}
				else if ( c == "d" )
				{
					if ( !cbWindowsMode->isChecked() || ( !e.getName().endsWith( "A" ) && !e.getName().endsWith( "W" ) ) )
						curDef = e.getName().toAscii();
				}
				else
					curDef = e.getName().toAscii();
				// prepend context if available
				if ( !e.getFieldValue( "class" ).isEmpty() )
					curDef.prepend( e.getFieldValue( "class" ).append( "::" ).toAscii() );
				else if ( !e.getFieldValue( "struct" ).isEmpty() )
					curDef.prepend( e.getFieldValue( "struct" ).append( "::" ).toAscii() );
				else if ( !e.getFieldValue( "namespace" ).isEmpty() )
					curDef.prepend( e.getFieldValue( "namespace" ).append( "::" ).toAscii() );
				else if ( !e.getFieldValue( "enum" ).isEmpty() )
					curDef.prepend( e.getFieldValue( "enum" ).append( "::" ).toAscii() );
				// check return type
				if ( !rt.isEmpty() )
				{
					// remove Qt export macro
					rt = QString( rt ).replace( QRegExp( "Q_.*_EXPORT" ), "" ).replace( QRegExp( "QT_.*" ), "" ).trimmed().toAscii();
					// append return type
					curDef.append( " (" +rt +")" );
				}
				
				// append to buffer if needed
				if ( !curDef.isEmpty() && !lb.contains( curDef ) )
					lb << curDef;
			}
		}
		
		// clear bytearrays
		curDef.clear();
		rt.clear();
		
		// increase progressbar
		pbLoading->setValue( pbLoading->value() +1 );
		QApplication::processEvents();
	}
	
	// return if buffer is empty
	if ( lb.isEmpty() )
	{
		pbLoading->setVisible( false );
		return false;
	}
	
	// get save filename
	QString s = getSaveFileName( tr( "Save api file" ), QString::null, tr( "Api Files (*.api)" ), this );
	if ( s.isEmpty() )
	{
		pbLoading->setVisible( false );
		return false;
	}
	
	// save file
	QFile f( s );
	if ( f.open( QFile::WriteOnly ) )
	{
		// erase file
		f.resize( 0 );
		// sort list
		qSort( lb );
		// save each line of buffer
		foreach ( QByteArray ba, lb )
			f.write( ba +'\n' );
	}
	else
	{
		pbLoading->setVisible( false );
		return false;
	}
	
	// hide progress bar
	pbLoading->setVisible( false );
	
	// success
	return true;
}

bool UICtags2Api::processCtags( const QString& s )
{
	// create process
	QProcess p;
	p.setWorkingDirectory( s );
	// start process
	p.start( QString( "%1 -f \"%2\" -R -u -n --c-types=pcdgstue ." ).arg( leCtagsBinary->text() ).arg( QDir::tempPath().append( "/temp.tags" ) ), QIODevice::ReadOnly | QIODevice::Text );
	// wait process end
	if ( !p.waitForFinished( -1 ) )
		return false;
	// process temp file
	return processCtags2Api( QDir::tempPath().append( "/temp.tags" ) );
}

bool UICtags2Api::processCtags2Api( const QString& s )
{
	QFile f( s );
	if ( !f.open( QFile::ReadOnly ) )
		return false;
	return processCtagsBuffer( f.readAll() );
}

void UICtags2Api::accept()
{
	// deactivated window
	setEnabled( false );
	
	// process convertion
	bool b = false;
	switch( cbGenerateFrom->currentIndex() )
	{
		case 0: // src folder
			b = processCtags( leLabel->text() );
			break;
		case 1: // ctags file
			b = processCtags2Api( leLabel->text() );
			break;
	}
	
	// reactivate window
	setEnabled( true );
	
	// if ok close dialog
	if ( b )
		QDialog::accept();
}
