'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : pAStyle.cpp
** Date      : 2008-01-14T00:39:48
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
#include "pAStyle.h"
#include "UISettingsAStyle.h"
#include "astyle.h"
#include "pFormatterSettings.h"

#include <pMonkeyStudio.h>
#include <coremanager/MonkeyCore.h>
#include <workspace/pWorkspace.h>
#include <workspace/pAbstractChild.h>
#include <qscintillamanager/pEditor.h>
#include <widgets/pMenuBar.h>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "AStyle Formatter" )
    mPluginInfos.Description = tr( "Uses AStyle to reformat your sources. Useful when copying code from the net or if you just want to reformat your sources based on a specific style" )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = False
    mPluginInfos.HaveSettingsWidget = True
    mPluginInfos.Pixmap = pIconManager.pixmap( "astyle.png", ":/icons" )


def settingsWidget(self):
    return UISettingsAStyle


def install(self):
    # create action
    a = MonkeyCore.menuBar().action( "mEdit/aAStyle",  tr( "AStyle Formatter" ), QIcon( ":/icons/astyle.png" ), tr( "Ctrl+Alt+A" ), infos().Description )
    a.triggered.connect(self.applyFormatter)
    return True


def uninstall(self):
    delete MonkeyCore.menuBar().action( "mEdit/aAStyle" )
    return True


def applyFormatter(self):
    if  c = MonkeyCore.workspace().currentDocument() :
        if  e = c.editor() :
            # vars
            s1 = e.text()
            QString s2
            astyle.ASFormatter f

            # load settings
            pFormatterSettings s
            s.applyTo( f )

            # eol
            eolChars = pMonkeyStudio.getEol( e.eolMode() )

            # add eol
            if  s1.length() and not s1.endsWith( '\r' ) and not s1.endsWith( '\n' ) :
                s1 += eolChars

            # iterate lines
            istringstream iter( s1.toStdString() )
            f.init( iter )
            while ( f.hasMoreLines() )
                s2.append( f.nextLine().c_str() )
                if  f.hasMoreLines() :
                    s2.append( eolChars )


            # update text and restore cursor position
            int l, i
            e.getCursorPosition(  &l, &i )
            e.clear()
            e.insert( s2 )
            e.setCursorPosition( l, i )




Q_EXPORT_PLUGIN2( BasepAStyle, pAStyle )