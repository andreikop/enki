/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : ProjectHeaders.cpp
** Date      : 2008-01-14T00:40:14
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
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
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
**
****************************************************************************/
#include "ProjectHeaders.h"
#include "UIProjectHeaders.h"

#include <pMonkeyStudio.h>
#include <widgets/pMenuBar.h>

using namespace pMonkeyStudio;

void ProjectHeaders::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "Project Headers" );
    mPluginInfos.Description = tr( "Plugin for managing the license headers of your sources" );
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>";
    mPluginInfos.Type = BasePlugin::iBase;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "0.5.0";
    mPluginInfos.FirstStartEnabled = false;
    mPluginInfos.Pixmap = QPixmap( ":/icons/licensing.png" );
}

bool ProjectHeaders::install()
{
    // add dock to dock toolbar entry
    QAction* a = MonkeyCore::menuBar()->action( "mEdit/aProjectHeaders", tr( "Project Licensing..." ), infos().Pixmap );
    connect( a, SIGNAL( triggered() ), this, SLOT( processLicensing() ) );
    return true;
}

bool ProjectHeaders::uninstall()
{
    delete MonkeyCore::menuBar()->action( "mEdit/aProjectHeaders");
    // return default value
    return true;
}

void ProjectHeaders::processLicensing()
{ UIProjectHeaders( QApplication::activeWindow(), this ).exec(); }

Q_EXPORT_PLUGIN2( BaseProjectHeaders, ProjectHeaders )