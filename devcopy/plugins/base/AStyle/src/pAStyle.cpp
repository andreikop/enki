/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : pAStyle.cpp
** Date      : 2008-01-14T00:39:48
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

void pAStyle::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "AStyle Formatter" );
    mPluginInfos.Description = tr( "Uses AStyle to reformat your sources. Useful when copying code from the net or if you just want to reformat your sources based on a specific style" );
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>";
    mPluginInfos.Type = BasePlugin::iBase;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "1.0.0";
    mPluginInfos.FirstStartEnabled = false;
    mPluginInfos.HaveSettingsWidget = true;
    mPluginInfos.Pixmap = pIconManager::pixmap( "astyle.png", ":/icons" );
}

QWidget* pAStyle::settingsWidget()
{ return new UISettingsAStyle; }

bool pAStyle::install()
{
    // create action
    QAction* a = MonkeyCore::menuBar()->action( "mEdit/aAStyle",  tr( "AStyle Formatter" ), QIcon( ":/icons/astyle.png" ), tr( "Ctrl+Alt+A" ), infos().Description );
    connect( a, SIGNAL( triggered() ), this, SLOT( applyFormatter() ) );
    return true;
}

bool pAStyle::uninstall()
{
    delete MonkeyCore::menuBar()->action( "mEdit/aAStyle" );
    return true;
}

void pAStyle::applyFormatter()
{
    if ( pAbstractChild* c = MonkeyCore::workspace()->currentDocument() )
    {
        if ( pEditor* e = c->editor() )
        {
            // vars
            QString s1 = e->text();
            QString s2;
            astyle::ASFormatter f;
            
            // load settings
            pFormatterSettings s;
            s.applyTo( f );
            
            // eol
            QString eolChars = pMonkeyStudio::getEol( e->eolMode() );
            
            // add eol
            if ( s1.length() && !s1.endsWith( '\r' ) && !s1.endsWith( '\n' ) )
                s1 += eolChars;
            
            // iterate lines
            istringstream iter( s1.toStdString() );
            f.init( iter );
            while ( f.hasMoreLines() )
            {
                s2.append( f.nextLine().c_str() );
                if ( f.hasMoreLines() )
                    s2.append( eolChars );
            }
            
            // update text and restore cursor position
            int l, i;
            e->getCursorPosition(  &l, &i );
            e->clear();
            e->insert( s2 );
            e->setCursorPosition( l, i );
        }
    }
}

Q_EXPORT_PLUGIN2( BasepAStyle, pAStyle )