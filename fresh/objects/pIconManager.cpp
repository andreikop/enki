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
#include "pIconManager.h"

#include <QApplication>
#include <QDir>

QIconCache pIconManager::mIconCache( 200 );
FileNameCache pIconManager::mFileNameCache;

QString findFile( QDir& dir, const QString& fileName )
{
	foreach ( const QFileInfo& fi, dir.entryInfoList( QStringList( fileName ), QDir::Files | QDir::CaseSensitive ) )
	{
		if ( fi.fileName() == fileName )
		{
			return fi.canonicalFilePath();
		}
	}
	
	foreach ( const QFileInfo& fi, dir.entryInfoList( QDir::AllDirs ) )
	{
		dir.setPath( fi.canonicalFilePath() );
		QString fn = findFile( dir, fileName );
		if ( !fn.isNull() )
			return fn;
	}
	
	return QString::null;
}

QString pIconManager::filePath( const QString& fileName, const QString& prefix )
{
	QString path = prefix;
	if ( path.isEmpty() )
		path = QLatin1String( ":/" );
	
	const FileNamePair pair = qMakePair( fileName, path );
	QString fn = mFileNameCache.value( pair );
	
	if ( !fn.isEmpty() )
	{
		return fn;
	}
	
	QDir dir( path );
	fn = findFile( dir, fileName );
	mFileNameCache[ pair ] = fn;
	return fn;
}

QPixmap pIconManager::pixmap( const QString& fileName, const QString& prefix )
{
	QPixmap pixmap;
	const QString fn = filePath( fileName, prefix );
	if ( !QPixmapCache::find( fn, pixmap ) )
	{
		if ( pixmap.load( fn ) )
		{
			QPixmapCache::insert( fn, pixmap );
		}
	}
	return pixmap;
}

QIcon pIconManager::icon( const QString& fileName, const QString& prefix )
{
	QIcon* icon = 0;
	const QString fn = filePath( fileName, prefix );
	if ( mIconCache.contains( fn ) )
	{
		icon = mIconCache[ fn ];
	}
	else
	{
		icon = new QIcon( pixmap( fileName, prefix ) );
		if ( icon->isNull() )
		{
			delete icon;
			icon = 0;
		}
		else
		{
			mIconCache.insert( fn, icon );
		}
	}
	return icon ? QIcon( *icon ) : QIcon();
}
