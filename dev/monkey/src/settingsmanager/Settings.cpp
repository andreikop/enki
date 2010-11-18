/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : Settings.cpp
** Date      : 2008-01-14T00:37:11
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
#include "Settings.h"
#include "main.h"
#include "coremanager/MonkeyCore.h"
#include "pMonkeyStudio.h"

#include <widgets/pQueuedMessageToolBar.h>
#include <qscilexer.h>

#include <QApplication>
#include <QStringList>
#include <QDir>

Settings::Settings( QObject* o )
	: pSettings( o )
{
}

QString Settings::storageToString( Settings::StoragePath type ) const
{
	switch ( type ) {
		case SP_PLUGINS:
			return QString( "plugins" );
			break;
		case SP_APIS:
			return QString( "apis" );
			break;
		case SP_TEMPLATES:
			return QString( "templates" );
			break;
		case SP_TRANSLATIONS:
			return QString( "translations" );
			break;
		case SP_SCRIPTS:
			return QString( "scripts" );
			break;
	}

	return QString::null;
}

QStringList Settings::storagePaths( Settings::StoragePath type ) const
{
	QStringList result = value( QString( "Paths/%1" ).arg( storageToString( type ) ) ).toStringList();

	if ( !result.isEmpty() ) {
		return result;
	}

	// Compatibility layer with old mks version (before 1.8.3.3)
	Settings* settings = const_cast<Settings*>( this );

	if ( type == SP_TEMPLATES && contains( "Templates/DefaultDirectories" ) ) {
		settings->setStoragePaths( type, value( "Templates/DefaultDirectories" ).toStringList() );
		settings->remove( "Templates/DefaultDirectories" );
	}
	else if ( type == SP_TRANSLATIONS && contains( "Translations/Path" ) ) {
		settings->setStoragePaths( type, value( "Translations/Path" ).toStringList() );
		settings->remove( "Translations/Path" );
	}
	else if ( type == SP_PLUGINS && contains( "Plugins/Path" ) ) {
		settings->setStoragePaths( type, value( "Plugins/Path" ).toStringList() );
		settings->remove( "Plugins/Path" );
	}

	result = value( QString( "Paths/%1" ).arg( storageToString( type ) ) ).toStringList();

	if ( !result.isEmpty() ) {
		return result;
	}

	// End compatibility layer

	const QString appPath = qApp->applicationDirPath();
	bool appIsInstalled = false;
	QString basePath;

#ifdef Q_OS_WIN
	appIsInstalled = QFile::exists( QString( "%1/templates" ).arg( appPath ) );
	basePath = appPath;
#elif defined Q_OS_MAC
	appIsInstalled = QFile::exists( QString( "%1/../Resources/templates" ).arg( appPath ) );
	basePath = QString( "%1/../Resources" ).arg( appPath );
#else
	appIsInstalled = QFile::exists( PACKAGE_PREFIX ) && QFile::exists( PACKAGE_DATAS );
	basePath = PACKAGE_DATAS;
#endif

	if ( !appIsInstalled ) {
		return storagePathsOutOfBox( type, appPath );
	}

	if ( type == Settings::SP_PLUGINS ) {
#ifdef Q_OS_WIN
		basePath = appPath;
#elif defined Q_OS_MAC
		basePath = QString( "%1/.." ).arg( appPath );
#else
		return QStringList( PACKAGE_PLUGINS );
#endif
		return QStringList( QDir::cleanPath( QString( "%1/%2" ).arg( basePath ).arg( storageToString( type ) ) ) );
	}

	return QStringList( QDir::cleanPath( QString( "%1/%2" ).arg( basePath ).arg( storageToString( type ) ) ) );
}

void Settings::setStoragePaths( Settings::StoragePath type, const QStringList& paths )
{
	setValue( QString( "Paths/%1" ).arg( storageToString( type ) ), paths );
}

QString Settings::homeFilePath( const QString& filePath ) const
{
	QString path = QFileInfo( fileName() ).absolutePath();
	QDir dir( path );

	return QDir::cleanPath( dir.filePath( filePath ) );
}

QString Settings::homePath( Settings::StoragePath type ) const
{
	const QString folder = storageToString( type ).append( "-%1" ).arg( PACKAGE_VERSION_STR );
	const QString path = QFileInfo( fileName() ).absolutePath().append( QString( "/%1" ).arg( folder ) );
	QDir dir( path );

	if ( !dir.exists() && !dir.mkpath( path ) ) {
		return QString::null;
	}

	return path;
}

QStringList Settings::storagePathsOutOfBox( Settings::StoragePath type, const QString& appPath ) const
{
	QString basePath = appPath;

#ifdef Q_OS_MAC
	basePath.append( "/../../../../datas" );
#else
	basePath.append( "/../datas" );
#endif

	if ( type == Settings::SP_PLUGINS ) {
#ifdef Q_OS_WIN
		basePath = appPath;
#elif defined Q_OS_MAC
		basePath = QString( "%1/.." ).arg( appPath );
#else
		basePath = appPath;
#endif
		return QStringList( QDir::cleanPath( QString( "%1/%2" ).arg( basePath ).arg( storageToString( type ) ) ) );
	}

	return QStringList( QDir::cleanPath( QString( "%1/%2" ).arg( basePath ).arg( storageToString( type ) ) ) );
}

void Settings::setDefaultSettings()
{
	// create default paths
	QStringList pluginsPaths = storagePaths( Settings::SP_PLUGINS );
	QStringList apisPaths = storagePaths( Settings::SP_APIS );
	QStringList templatesPaths = storagePaths( Settings::SP_TEMPLATES );
	QStringList translationsPaths = storagePaths( Settings::SP_TRANSLATIONS );
	QStringList scriptsPaths = storagePaths( Settings::SP_SCRIPTS );
	QString scriptsPath = homePath( Settings::SP_SCRIPTS );

	// save default paths
	setStoragePaths( Settings::SP_PLUGINS, pluginsPaths );
	setStoragePaths( Settings::SP_APIS, apisPaths );
	setStoragePaths( Settings::SP_TEMPLATES, templatesPaths );
	setStoragePaths( Settings::SP_TRANSLATIONS, translationsPaths );
	setStoragePaths( Settings::SP_SCRIPTS, scriptsPaths );

	// apis
	foreach ( const QString& path, apisPaths ) {
		if ( QFile::exists( path +"/cmake.api" ) ) {
			setValue( "SourceAPIs/CMake", QStringList( QDir::cleanPath( path +"/cmake.api" ) ) );
		}

		if ( QFile::exists( path +"/cs.api" ) ) {
			setValue( "SourceAPIs/C#", QStringList( QDir::cleanPath( path +"/cs.api" ) ) );
		}

		if ( QFile::exists( path +"/c.api" ) ) {
			QStringList files;

			files << QDir::cleanPath( path +"/c.api" );
			files << QDir::cleanPath( path +"/cpp.api" );
			files << QDir::cleanPath( path +"/glut.api" );
			files << QDir::cleanPath( path +"/opengl.api" );
			files << QDir::cleanPath( path +"/qt-4.5.x.api" );

			setValue( "SourceAPIs/C++", files );
		}
	}

	// copy scripts to user's home
	foreach ( const QString& path, scriptsPaths ) {
		QFileInfoList files = QDir( path ).entryInfoList( QStringList( "*.mks" ) );

		foreach ( const QFileInfo& file, files ) {
			const QString fn = QDir( scriptsPath ).absoluteFilePath( file.fileName() );

			if ( !QFile::exists( fn ) ) {
				QFile f( file.absoluteFilePath() );

				if ( !f.copy( fn ) ) {
					MonkeyCore::messageManager()->appendMessage( tr( "Can't copy script '%1', %2" ).arg( file.fileName() ).arg( f.errorString() ) );
				}
			}
		}
	}

	// syntax highlighter
	setDefaultLexerProperties( pMonkeyStudio::defaultDocumentFont(), true );
	setDefaultCppSyntaxHighlight();
}

void Settings::setDefaultCppSyntaxHighlight()
{
	const QFont font = pMonkeyStudio::defaultDocumentFont();
	const QStringList parts = QStringList() << font.family() << QString::number( font.pointSize() );

	// configure default styles
	LexerStyleList styles;
	styles << LexerStyle( 0, 0, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 1, 10526880, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 2, 10526880, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 3, 8421631, false, "%1, 1, 0, 0", 16777215 );
	styles << LexerStyle( 4, 15728880, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 5, 160, false, "%1, 1, 0, 0", 16777215 );
	styles << LexerStyle( 6, 255, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 7, 14721024, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 9, 40960, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 10, 16711680, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 11, 0, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 12, 0, true, "%1, 0, 0, 0", 16711680 );
	styles << LexerStyle( 15, 8421631, false, "%1, 1, 0, 0", 16777215 );
	styles << LexerStyle( 16,0 , false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 17, 32896, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 18, 8388608, false, "%1, 0, 0, 0", 16777215 );
	styles << LexerStyle( 19, 0, false, "%1, 0, 0, 0", 16777215 );
	
	// write styles
	beginGroup( "Scintilla/C++" );
	
	foreach ( const LexerStyle& style, styles )
	{
		beginGroup( QString( "style%1" ).arg( style.id ) );
		setValue( "color", style.color );
		setValue( "eolfill", style.eolfill );
		setValue( "font", style.font.arg( parts.join( ", " ) ).split( ',' ) );
		setValue( "paper", style.paper );
		endGroup();
	}
	
	setValue( "properties/foldatelse", QVariant( true ).toString() );
	setValue( "properties/foldcomments", QVariant( true ).toString() );
	setValue( "properties/foldcompact", QVariant( true ).toString() );
	setValue( "properties/foldpreprocessor", QVariant( true ).toString() );
	setValue( "properties/stylepreprocessor", QVariant( true ).toString() );
	setValue( "defaultcolor", 0 );
	setValue( "defaultpaper", 16777215 );
	setValue( "defaultfont", QString( "Verdana, 10, 0, 0, 0" ).split( ',' ) );
	setValue( "autoindentstyle", 1 );
	
	endGroup();
}

void Settings::setDefaultLexerProperties( const QFont& defaultFont, bool write )
{
	foreach ( const QString& language, pMonkeyStudio::availableLanguages() ) {
		QsciLexer* lexer = pMonkeyStudio::lexerForLanguage( language );
		
		for ( int i = 0; i < 128; i++ ) {
			if ( !lexer->description( i ).isEmpty() ) {
                QFont font = lexer->font( i );
				
				font.setFamily( defaultFont.family() );
				font.setPointSize( defaultFont.pointSize() );
				lexer->setFont( font, i );
			}
		}
		
		if ( write ) {
			lexer->writeSettings( *this, pMonkeyStudio::scintillaSettingsPath().toLocal8Bit().constData() );
		}
	}
}
