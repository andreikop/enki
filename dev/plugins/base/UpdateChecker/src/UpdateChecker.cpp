/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UpdateChecker.cpp
** Date      : 2008-01-14T00:39:52
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
#include "UpdateChecker.h"
#include "UIUpdateChecker.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <widgets/pMenuBar.h>

#include <QTimer>

void UpdateChecker::fillPluginInfos()
{
	mPluginInfos.Caption = tr( "Update Checker" );
	mPluginInfos.Description = tr( "This plugin allow to activate the update checker." );
	mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>";
	mPluginInfos.Type = BasePlugin::iBase;
	mPluginInfos.Name = PLUGIN_NAME;
	mPluginInfos.Version = "1.0.0";
	mPluginInfos.FirstStartEnabled = true;
	mPluginInfos.Pixmap = pIconManager::pixmap( "UpdateChecker.png", ":/icons" );
}

bool UpdateChecker::install()
{
	// create action
	QAction* a = MonkeyCore::menuBar()->action( "mHelp/aUpdateChecker",  tr( "Check for update..." ), QIcon( ":/icons/UpdateChecker.png" ), QString::null, infos().Description );
	connect( a, SIGNAL( triggered() ), this, SLOT( checkForUpdate_triggered() ) );
	QTimer::singleShot( 15000, this, SLOT( checkForUpdate() ) );
	return true;
}

bool UpdateChecker::uninstall()
{
	// delete action
	delete MonkeyCore::menuBar()->action( "mHelp/aUpdateChecker" );
	// return default value
	return true;
}

void UpdateChecker::checkForUpdate()
{
	checkForUpdate_triggered( false );
}

void UpdateChecker::checkForUpdate_triggered( bool show )
{
	UIUpdateChecker* dlg = new UIUpdateChecker( this, MonkeyCore::mainWindow() );
	
	if ( show )
	{
		dlg->open();
	}
}

Q_EXPORT_PLUGIN2( BaseUpdateChecker, UpdateChecker )