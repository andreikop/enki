/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIPluginsSettings.cpp
** Date      : 2008-01-14T00:37:00
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
#include "UIPluginsSettings.h"
#include "UIPluginsSettingsElement.h"
#include "coremanager/MonkeyCore.h"
#include "pluginsmanager/PluginsManager.h"

UIPluginsSettings::UIPluginsSettings( QWidget* p )
	: QDialog( p, Qt::Dialog )
{
	// setup dialog
	setupUi( this );
	setWindowModality( Qt::ApplicationModal );
	setAttribute( Qt::WA_DeleteOnClose );
	
	// fill list with plugins type
	for ( int i = BasePlugin::iAll; i < BasePlugin::iLast; i++ )
	{
		const QString s = BasePlugin::typeToString( (BasePlugin::Type)i );
		if ( !s.isEmpty() && cbPluginType->findData( i ) == -1 )
			cbPluginType->addItem( s, i );
	}
	
	// update plugins list
	updateList();
}

void UIPluginsSettings::updateList()
{
	// clear list
	lwPlugins->clear();
	
	// create items and editor foreach plugin
	foreach ( BasePlugin* bp, MonkeyCore::pluginsManager()->plugins() )
	{
		UIPluginsSettingsElement* pse = new UIPluginsSettingsElement( bp, this );
		QListWidgetItem* item = new QListWidgetItem( lwPlugins );
		item->setSizeHint( pse->sizeHint() );
		lwPlugins->setItemWidget( item, pse );
	}
}

void UIPluginsSettings::on_cbPluginType_currentIndexChanged( int id )
{
	// clear selection
	lwPlugins->clearSelection();
	lwPlugins->setCurrentItem( 0 );
	// get current type
	BasePlugin::Type mType = (BasePlugin::Type)cbPluginType->itemData( id ).toInt();
	// show/hide item according to type
	for ( int i = 0; i < lwPlugins->count(); i++ )
	{
		QListWidgetItem* item = lwPlugins->item( i );
		UIPluginsSettingsElement* pse = qobject_cast<UIPluginsSettingsElement*>( lwPlugins->itemWidget( item ) );
		item->setHidden( mType != BasePlugin::iAll && !pse->plugin()->infos().Type.testFlag( mType ) );
	}
}
