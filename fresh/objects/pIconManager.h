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
/*!
	\file pIconManager.h
	\date 2008-11-01
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A cache class for icons and pixmaps
*/
#ifndef PICONMANAGER_H
#define PICONMANAGER_H

#include "MonkeyExport.h"

#include <QPixmapCache>
#include <QCache>
#include <QIcon>
#include <QPair>
#include <QMap>

/*!
	\details A typedef for icons caching
*/
typedef QCache<QString, QIcon> QIconCache;

typedef QPair<QString, QString> FileNamePair;
typedef QMap<FileNamePair, QString> FileNameCache;

/*!
	\brief A cache class for icons and pixmaps
	\details This class allow to cache and share QPixmap & QIcon.
	\details Icons and pixmaps can easily be loaded on demand by using coresponding members.
*/
class Q_MONKEY_EXPORT pIconManager
{
public:
	// return the filepath of the icon named fileName in prefix folder ( check is done recursively )
	static QString filePath( const QString& fileName, const QString& prefix = QLatin1String( ":/" ) );
	// return the QPixmap of the pixmap named fileName in prefix folder ( check is done recursively )
	static QPixmap pixmap( const QString& fileName, const QString& prefix = QLatin1String( ":/" ) );
	// return the QIcon of the icon named fileName in prefix folder ( check is done recursively )
	static QIcon icon( const QString& fileName, const QString& prefix = QLatin1String( ":/" ) );

protected:
	static QIconCache mIconCache;
	static FileNameCache mFileNameCache;
};

#endif // PICONMANAGER_H
