'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Compiler Plugins
** FileName  : GccParser.cpp
** Date      : 2008-01-14T00:53:26
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
'''!
    \file GccParser.cpp
    \date 2008-01-14T00:53:21
    \author Andrei Kopats
    \brief Implementation for GccParser plugin class
'''

#include "GccParser.h"
#include "Parser.h"

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "GccParser" )
    mPluginInfos.Description = tr( "Plugin for parsing output of GNU Copiler Collection" )
    mPluginInfos.Author = "Kopats Andrei aka hlamer <hlamer@tut.by>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "0.1.0"
#ifdef Q_CC_GNU
    mPluginInfos.FirstStartEnabled = True
#else:
    mPluginInfos.FirstStartEnabled = False
#endif


'''!
    Install plugin to the system
    \return Status of process
    \retval True Successfully enabled
    \retval False Some error ocurred
'''
def install(self):
    MonkeyCore.consoleManager().addParser( Parser( self ) )
    return True


'''!
    Uninstall plugin to the system
    \return Status of process
    \retval True Successfully enabled
    \retval False Some error ocurred
'''
def uninstall(self):
    MonkeyCore.consoleManager().removeParser( PLUGIN_NAME )
    return True


Q_EXPORT_PLUGIN2( BaseGccParser, GccParser )