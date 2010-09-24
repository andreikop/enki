'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : FileBrowserSettings.cpp
** Date      : 2008-01-14T00:39:55
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
    \file FileBrowserSettings.cpp
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, KOPATS
    \brief Settings widget of FileBrowser plugin
'''
#include "FileBrowserSettings.h"
#include "FileBrowser.h"

#include <widgets/pStringListEditor.h>

#include <QVBoxLayout>
#include <QDialogButtonBox>
#include <QPushButton>

'''!
    Creates settings widget
    \param plugin Pointer to FileBrowser plugin
    \param parent Parent widget of settings widget
'''
FileBrowserSettings.FileBrowserSettings( FileBrowser* plugin, parent )
        : QWidget( parent )
    # retain plugin
    mPlugin = plugin

    # list editor
    mEditor = pStringListEditor( self, tr( "Except Suffixes" ) )
    mEditor.setValues( plugin.filters() )

    # apply button
    dbbApply = QDialogButtonBox( self )
    dbbApply.addButton( QDialogButtonBox.Apply )

    # global layout
    vbox = QVBoxLayout( self )
    vbox.addWidget( mEditor )
    vbox.addWidget( dbbApply )

    # connections
    connect( dbbApply.button( QDialogButtonBox.Apply ), SIGNAL( clicked() ), self, SLOT( applySettings() ) )


'''!
    Handler of clicking Apply button. Applying settings
'''
def applySettings(self):
    mPlugin.setFilters( mEditor.values(), True )

