'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Builder Plugins
** FileName  : GNUMake.cpp
** Date      : 2008-01-14T00:52:24
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
#include "GNUMake.h"

#include <QTabWidget>

GNUMake.GNUMake()


def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "GNUMake" )
    mPluginInfos.Description = tr( "Plugin for execute GNU Make in console and parse it's output" )
    mPluginInfos.Author = "Kopats Andrei aka hlamer <hlamer@tut.by>, Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBuilder
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "0.5.0"
    mPluginInfos.FirstStartEnabled = False
    mPluginInfos.HaveSettingsWidget = True


GNUMake.~GNUMake()
{ # TODO move to uninstall
    # uninstall parsers
    for s in availableParsers():
    MonkeyCore.consoleManager().removeParser( s )


def install(self):
    return True


def uninstall(self):
    return True


def settingsWidget(self):
    tw = QTabWidget
    tw.setAttribute( Qt.WA_DeleteOnClose )
    tw.addTab( builderSettingsWidget(), tr( "Build Command" ) )
    tw.addTab( cliToolSettingsWidget(), tr( "User Commands" ) )
    return tw


def defaultCommands(self):
    return pCommandList()


def availableParsers(self):
    QStringList list
    list << "GNU Make" << "GCC"
    return list


def getParser(self, name ):
    Q_UNUSED( name );    ''' FIXME '''
    return 0


def defaultBuildCommand(self):
#ifdef Q_OS_WIN
     mMake = "mingw32-make"
#else:
     mMake = "make"
#endif
    return pCommand( "Build", mMake, "-w", False, availableParsers(), "$cpp$", True )


Q_EXPORT_PLUGIN2( BuilderGNUMake, GNUMake )