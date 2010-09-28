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
#include "pDockClassBrowser.h"
#include "ClassBrowser.h"

#include <qCtagsSenseBrowser.h>
#include <widgets/pDockWidgetTitleBar.h>
#include <coremanager/MonkeyCore.h>
#include <widgets/pActionsManager.h>

pDockClassBrowser::pDockClassBrowser( ClassBrowser* plugin, QWidget* w )
    : pDockWidget( w )
{
    Q_ASSERT( plugin );
    mPlugin = plugin;
    
    // restrict areas
    setAllowedAreas( Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea );
    
    // create browser and set it as central widget
    mBrowser = new qCtagsSenseBrowser( this );
    setWidget( mBrowser );
    
    // set actions manager
    setActionsManager( MonkeyCore::actionsManager() );
    pActionsManager::setPathPartTranslation( "Plugins", tr( "Plugins" ) );
    pActionsManager::setActionsManager( mBrowser->viewBrowserAction(), actionsManager() );
    pActionsManager::setActionPath( mBrowser->viewBrowserAction(), QString( "Plugins/%1" ).arg( mPlugin->infos().Caption ) );
    pActionsManager::setActionsManager( mBrowser->viewSearchResultsAction(), actionsManager() );
    pActionsManager::setActionPath( mBrowser->viewSearchResultsAction(), QString( "Plugins/%1" ).arg( mPlugin->infos().Caption ) );
    
    // set dock actions
    titleBar()->addAction( mBrowser->viewBrowserAction(), 0 );
    titleBar()->addAction( mBrowser->viewSearchResultsAction(), 1 );
    titleBar()->addSeparator( 2 );
}

pDockClassBrowser::~pDockClassBrowser()
{
    delete mBrowser;
}

qCtagsSenseBrowser* pDockClassBrowser::browser() const
{
    return mBrowser;
}
