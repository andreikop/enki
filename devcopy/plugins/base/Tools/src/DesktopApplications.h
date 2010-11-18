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
#ifndef DESKTOPAPPLICATIONS_H
#define DESKTOPAPPLICATIONS_H

#include <QObject>
#include <QStringList>
#include <QMap>
#include <QMetaType>

class DesktopFolder

struct DesktopApplication
    DesktopApplication( _parent = 0 )
        parent = _parent

    
    bool operator==(  DesktopApplication& other )
        return parent == other.parent
            and name == other.name
            and icon == other.icon
            and genericName == other.genericName
            and comment == other.comment
            and categories == other.categories

    
    DesktopFolder* parent
    QString name
    QString icon
    QString genericName
    QString comment
    QStringList categories


class DesktopFolder
public:
    DesktopFolder( _parent = 0 )
        parent = _parent

    
    DesktopFolder* parent
    QString path
    QString icon
    QMap<QString, applications
    QMap<QString, folders


class DesktopApplications : public QObject
    Q_OBJECT

public:
    DesktopApplications( parent = 0 )

    DesktopFolder* startMenu()
    int applicationCount()
    QStringList startMenuPaths()
    bool categoriesAvailable()
    void scan()

protected:
    mutable DesktopFolder mStartMenu

    int applicationCount( DesktopFolder* folder )


Q_DECLARE_METATYPE( DesktopApplication* )
Q_DECLARE_METATYPE( DesktopFolder* )

#endif # DESKTOPAPPLICATIONS_H
