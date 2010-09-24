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

#include <QDir>

const QFileInfoList getMacApplicationsFolders( QDir dir )
{
	QFileInfoList applications;
	
	foreach ( const QFileInfo& file, dir.entryInfoList( QDir::Dirs | QDir::NoDotAndDotDot ) ) {
		if ( file.isBundle() ) {
			applications << file;
		}
		else if ( file.isDir() ) {
			dir.cd( file.filePath() );
			applications << getMacApplicationsFolders( dir );
			dir.cdUp();
		}
	}
	
	return applications;
}

QStringList DesktopApplications::startMenuPaths() const
{
	return QStringList( "/Applications" );
}

bool DesktopApplications::categoriesAvailable() const
{
	return false;
}

void DesktopApplications::scan()
{
	foreach ( const QString& menuPath, startMenuPaths() ) {
		foreach ( const QFileInfo& file, getMacApplicationsFolders( QDir( menuPath ) ) ) {
			// get folder object
			DesktopFolder* df = &mStartMenu;
			// get relative path
			const QString applicationPath = file.absolutePath().remove( menuPath ).remove( 0, 1 );
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
			if ( !df->applications.contains( file.absoluteFilePath() ) ) {
				DesktopApplication da = DesktopApplication( df );
				da.name = file.completeBaseName();
				da.icon = QString();
				da.genericName = QString();
				da.comment = QString();
				df->applications[ file.absoluteFilePath() ] = da;
			}
		}
	}
}
