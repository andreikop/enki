'''***************************************************************************
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
***************************************************************************'''
#include "DesktopApplications.h"

#include <QDir>

 QFileInfoList getMacApplicationsFolders( QDir dir )
    QFileInfoList applications

    foreach (  QFileInfo& file, dir.entryInfoList( QDir.Dirs | QDir.NoDotAndDotDot ) )
        if  file.isBundle() :
            applications << file

        elif  file.isDir() :
            dir.cd( file.filePath() )
            applications << getMacApplicationsFolders( dir )
            dir.cdUp()



    return applications


def startMenuPaths(self):
    return QStringList( "/Applications" )


def categoriesAvailable(self):
    return False


def scan(self):
    for menuPath in startMenuPaths():
        foreach (  QFileInfo& file, getMacApplicationsFolders( QDir( menuPath ) ) )
            # get folder object
            df = &mStartMenu
            # get relative path
             applicationPath = file.absolutePath().remove( menuPath ).remove( 0, 1 )
            # get last folder object
            QString path

            foreach (  QString& part, applicationPath.split( "/", QString.SkipEmptyParts ) )
                path += part +"/"

                if  df.folders.contains( part ) :
                    df = &df.folders[ part ]

                else:
                    df.folders[ part ] = DesktopFolder( df )
                    df = &df.folders[ part ]
                    df.path = menuPath +"/" +path

                    if  df.path.endsWith( "/" ) :
                        df.path.chop( 1 )




            # add application
            if  not df.applications.contains( file.absoluteFilePath() ) :
                da = DesktopApplication( df )
                da.name = file.completeBaseName()
                da.icon = QString()
                da.genericName = QString()
                da.comment = QString()
                df.applications[ file.absoluteFilePath() ] = da




