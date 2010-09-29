'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : ChildPlugin.h
** Date      : 2008-01-14T00:37:00
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#ifndef CHILDPLUGIN_H
#define CHILDPLUGIN_H

#include <objects/MonkeyExport.h>

#include "BasePlugin.h"

#include <QHash>
#include <QStringList>
#include <QDir>

class pAbstractChild

class Q_MONKEY_EXPORT ChildPlugin : public BasePlugin
public:
    # the suffixes self project can manage
    virtual QHash<QString, suffixes()
    { return mSuffixes;
    
    # tell if self plugin can open self file
    virtual bool canOpen(  QString& fileName )
        for suffixes in mSuffixes.values():
            if  QDir.match( suffixes, fileName ) :
                return True


        
        return False

    
    # try opening self file
    virtual pAbstractChild* createDocument(  QString& fileName ) = 0
    
protected:
    QHash<QString, mSuffixes


Q_DECLARE_INTERFACE( ChildPlugin, "org.monkeystudio.MonkeyStudio.ChildPlugin/1.0" )

#endif # CHILDPLUGIN_H
