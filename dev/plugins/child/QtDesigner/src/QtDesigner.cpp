/****************************************************************************
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
****************************************************************************/
#include "QtDesigner.h"
#include "QtDesignerManager.h"
#include "QtDesignerChild.h"

void QtDesigner::fillPluginInfos()
{
	mPluginInfos.Caption = tr( "Qt Designer" );
	mPluginInfos.Description = tr( "This plugin embeds Qt Designer" );
	mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>, Luc Bruant aka fullmetalcoder <fullmetalcoder@hotmail.fr>";
	mPluginInfos.Type = BasePlugin::iChild;
	mPluginInfos.Name = PLUGIN_NAME;
	mPluginInfos.Version = "1.0.0";
	mPluginInfos.FirstStartEnabled = true;
	mPluginInfos.Pixmap = pIconManager::pixmap( "designer.png", ":/icons" );
}

bool QtDesigner::install()
{
	// set usable suffixes
	mSuffixes[ tr( "Qt Forms" ) ] = QStringList( "*.ui" );
	// create designer
	mDesignerManager = new QtDesignerManager( this );
	return true;
}

bool QtDesigner::uninstall()
{
	// clear suffixes
	mSuffixes.clear();
	// clear designer instance
	delete mDesignerManager;
	return true;
}

pAbstractChild* QtDesigner::createDocument( const QString& fileName )
{
	if ( canOpen( fileName ) )
	{
		return new QtDesignerChild( mDesignerManager );
	}
	
	return 0;
}

Q_EXPORT_PLUGIN2( BaseQtDesigner, QtDesigner )
