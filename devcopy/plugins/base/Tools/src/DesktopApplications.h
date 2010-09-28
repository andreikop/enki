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
#ifndef DESKTOPAPPLICATIONS_H
#define DESKTOPAPPLICATIONS_H

#include <QObject>
#include <QStringList>
#include <QMap>
#include <QMetaType>

class DesktopFolder;

struct DesktopApplication
{
    DesktopApplication( DesktopFolder* _parent = 0 )
    {
        parent = _parent;
    }
    
    bool operator==( const DesktopApplication& other ) const
    {
        return parent == other.parent
            && name == other.name
            && icon == other.icon
            && genericName == other.genericName
            && comment == other.comment
            && categories == other.categories;
    }
    
    DesktopFolder* parent;
    QString name;
    QString icon;
    QString genericName;
    QString comment;
    QStringList categories;
};

class DesktopFolder
{
public:
    DesktopFolder( DesktopFolder* _parent = 0 )
    {
        parent = _parent;
    }
    
    DesktopFolder* parent;
    QString path;
    QString icon;
    QMap<QString, DesktopApplication> applications;
    QMap<QString, DesktopFolder> folders;
};

class DesktopApplications : public QObject
{
    Q_OBJECT

public:
    DesktopApplications( QObject* parent = 0 );

    DesktopFolder* startMenu() const;
    int applicationCount() const;
    QStringList startMenuPaths() const;
    bool categoriesAvailable() const;
    void scan();

protected:
    mutable DesktopFolder mStartMenu;

    int applicationCount( DesktopFolder* folder ) const;
};

Q_DECLARE_METATYPE( DesktopApplication* );
Q_DECLARE_METATYPE( DesktopFolder* );

#endif // DESKTOPAPPLICATIONS_H
