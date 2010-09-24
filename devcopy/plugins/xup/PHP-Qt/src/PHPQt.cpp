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
#include "PHPQt.h"
#include "PHPQtProjectItem.h"
##include "UISettingsPHPQt.h"
#include "../XUP/src/gui/UIXUPEditor.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>

#include <QDir>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "PHP-Qt Project" )
    mPluginInfos.Description = tr( "PHP-Qt Project support for XUPManager" )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iXUP
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "0.1.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = False



def install(self):
    # register phpqt item
    mItem = PHPQtProjectItem
    mItem.registerProjectType()
    return True


def uninstall(self):
    # unregister qmake item, auto delete the item
    mItem.unRegisterProjectType()
    delete mItem
    return True


def editProject(self, project ):
    if  not project :
        return False


    return UIXUPEditor( project, MonkeyCore.mainWindow() ).exec() == QDialog.Accepted


Q_EXPORT_PLUGIN2( ProjectPHPQt, PHPQt )