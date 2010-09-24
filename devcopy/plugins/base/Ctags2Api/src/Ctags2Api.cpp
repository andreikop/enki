'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : Ctags2Api.cpp
** Date      : 2008-01-14T00:39:52
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
#include "Ctags2Api.h"
#include "UICtags2Api.h"

#include <coremanager/MonkeyCore.h>
#include <widgets/pMenuBar.h>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "Api File Generator" )
    mPluginInfos.Description = tr( "This plugin allow to generate api file using ctags." )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = False
    mPluginInfos.Pixmap = pIconManager.pixmap( "Ctags2Api.png", ":/icons" )



def install(self):
    # create action
    a = MonkeyCore.menuBar().action( "mEdit/aCtags2Api",  tr( "Api File Generator" ), QIcon( ":/icons/Ctags2Api.png" ), tr( "Ctrl+Alt+G" ), infos().Description )
    a.triggered.connect(self.UICtags2Api_show)
    return True


def uninstall(self):
    # delete action
    delete MonkeyCore.menuBar().action( "mEdit/aCtags2Api" )
    return True


def UICtags2Api_show(self):
    # create dialog
    UICtags2Api w
    # restore settings
    w.leCtagsBinary.setText( settingsValue( "CtagsBinary", w.leCtagsBinary.text() ).toString() )
    w.cbRemovePrivate.setChecked( settingsValue( "RemovePrivate", w.cbRemovePrivate.isChecked() ).toBool() )
    w.cbWindowsMode.setChecked( settingsValue( "WindowsMode", w.cbWindowsMode.isChecked() ).toBool() )
    w.cbLetter.setCurrentIndex( w.cbLetter.findText( settingsValue( "Letter", w.cbLetter.currentText() ).toString() ) )
    w.exec()
    # save ctags file and options
    setSettingsValue( "CtagsBinary", w.leCtagsBinary.text() )
    setSettingsValue( "RemovePrivate", w.cbRemovePrivate.isChecked() )
    setSettingsValue( "WindowsMode", w.cbWindowsMode.isChecked() )
    setSettingsValue( "Letter", w.cbLetter.currentText() )


Q_EXPORT_PLUGIN2( BaseCtags2Api, Ctags2Api )