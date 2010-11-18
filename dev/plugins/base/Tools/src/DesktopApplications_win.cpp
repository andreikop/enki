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
#include "DesktopApplications.h"

#include <pMonkeyStudio.h>

#define _WIN32_IE 0x0400
#include <shlobj.h>

#include <QSet>

QStringList DesktopApplications::startMenuPaths() const
{
	QSet<QString> paths;
	wchar_t path[MAX_PATH];
	
	// get common start menu files
	if ( SHGetSpecialFolderPathW( NULL, path, CSIDL_COMMON_STARTMENU, false ) ) {
		paths << QString::fromWCharArray( path ).replace( "\\", "/" );
	}
	
	// get start menu files
	if ( SHGetSpecialFolderPathW( NULL, path, CSIDL_STARTMENU, false ) ) {
		paths << QString::fromWCharArray( path ).replace( "\\", "/" );
	}
	
	// return values
	return paths.toList();
}

bool DesktopApplications::categoriesAvailable() const
{
	return false;
}

void DesktopApplications::scan()
{
	foreach ( const QString& menuPath, startMenuPaths() )
	{
		foreach ( const QFileInfo& applicationFile, pMonkeyStudio::getFiles( QDir( menuPath ) ) )
		{
			// get folder object
			DesktopFolder* df = &mStartMenu;
			// get relative menuPath
			const QString applicationPath = applicationFile.absolutePath().remove( menuPath ).remove( 0, 1 );
			// get last folder object
			QString path;
			
			foreach ( const QString& part, applicationPath.split( "/", QString::SkipEmptyParts ) ) {
				path += part +"/";
				
				if ( df->folders.contains( part ) ) {
					df = &df->folders[ part ];
				}
				else {
					df->folders[ part ] = DesktopFolder( df );
					df = &df->folders[ part ];
					df->path = menuPath +"/" +path;
					
					if ( df->path.endsWith( "/" ) ) {
						df->path.chop( 1 );
					}
				}
			}
			
			// add application
			if ( !df->applications.contains( applicationFile.absoluteFilePath() ) )
			{
				DesktopApplication da( df );
				da.name = applicationFile.completeBaseName();
				da.icon = QString();
				da.genericName = QString();
				da.comment = QString();
				df->applications[ applicationFile.absoluteFilePath() ] = da;
			}
		}
	}
}
