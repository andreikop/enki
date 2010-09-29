'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : ProjectHeaders.cpp
** Date      : 2008-01-14T00:40:14
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
#include "ProjectHeaders.h"
#include "UIProjectHeaders.h"

#include <pMonkeyStudio.h>
#include <widgets/pMenuBar.h>

using namespace pMonkeyStudio

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "Project Headers" )
    mPluginInfos.Description = tr( "Plugin for managing the license headers of your sources" )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "0.5.0"
    mPluginInfos.FirstStartEnabled = False
    mPluginInfos.Pixmap = QPixmap( ":/icons/licensing.png" )


def install(self):
    # add dock to dock toolbar entry
    a = MonkeyCore.menuBar().action( "mEdit/aProjectHeaders", tr( "Project Licensing..." ), infos().Pixmap )
    a.triggered.connect(self.processLicensing)
    return True


def uninstall(self):
    delete MonkeyCore.menuBar().action( "mEdit/aProjectHeaders")
    # return default value
    return True


def processLicensing(self):
{ UIProjectHeaders( QApplication.activeWindow(), self ).exec();

Q_EXPORT_PLUGIN2( BaseProjectHeaders, ProjectHeaders )