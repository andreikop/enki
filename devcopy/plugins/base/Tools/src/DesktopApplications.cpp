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

DesktopApplications::DesktopApplications( QObject* parent )
    : QObject( parent ), mStartMenu( 0 )
{
}

DesktopFolder* DesktopApplications::startMenu() const
{
    return &mStartMenu;
}

int DesktopApplications::applicationCount( DesktopFolder* _folder ) const
{
    Q_ASSERT( _folder );
    
    // recursive count
    int count = 0;
    
    // Applications
    count = _folder->applications.count();
    
    // Folders
    foreach ( const QString& key, _folder->folders.keys() ) {
        count += applicationCount( &_folder->folders[ key ] );
    }
    
    // return result
    return count;
}

int DesktopApplications::applicationCount() const
{
    return applicationCount( &mStartMenu );
}
