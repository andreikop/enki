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
#include "PHP.h"

#include <QTabWidget>

PHP.PHP ()
    # install parsers
    for s in availableParsers():
        MonkeyCore.consoleManager().addParser( getParser( s ) )



def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "PHP" )
    mPluginInfos.Description = tr( "This plugin provide PHP interpreter and php parser." )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iInterpreter
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "0.1.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = True
    mPluginInfos.Pixmap = pIconManager.pixmap( "php.png", ":/icons" )


PHP.~PHP()
{#TODO move to uninstall
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
    tw.addTab( interpreterSettingsWidget(), tr( "Interpret Command" ) )
    tw.addTab( cliToolSettingsWidget(), tr( "User Commands" ) )
    return tw


def defaultCommands(self):
    return pCommandList()


def availableParsers(self):
    return QStringList()


def defaultInterpretCommand(self):
     mPHP = "php"
    return pCommand( "Interpret", mPHP, QString.null, False, availableParsers(), "$cpp$" )


Q_EXPORT_PLUGIN2( InterpreterPHP, PHP )
