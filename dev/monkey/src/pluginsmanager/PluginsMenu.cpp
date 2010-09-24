#include "PluginsMenu.h"
#include "PluginsManager.h"
#include "ui/UIPluginsSettingsAbout.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <objects/pIconManager.h>

#include <QDesktopWidget>

PluginsMenu::PluginsMenu( PluginsManager* manager )
	: QObject( manager )
{
	Q_ASSERT( manager );
	
	mManager = manager;
	mMenu = 0;
	mManageDialogAction = 0;
}

PluginsMenu::~PluginsMenu()
{
}

QMenu* PluginsMenu::menu() const
{
	return mMenu;
}

void PluginsMenu::setMenu( QMenu* menu )
{
	mMenu = menu;
	
	mManageDialogAction = mMenu->addAction( pIconManager::icon( "settings.png", ":/edit" ), tr( "&Manage using dialog..." ) );
	mManageDialogAction->setObjectName( "aManageDialogAction" );
	mManageDialogAction->setToolTip( tr( "Manage plugins using a dialog..." ) );
	
	mMenu->addSeparator();
	
	connect( mManageDialogAction, SIGNAL( triggered() ), mManager, SLOT( manageRequested() ) );
}

void PluginsMenu::initPluginMenusActions( BasePlugin* plugin, BasePlugin::Type type )
{
	QMenu* menu = mMenus[ plugin ];
	
	if ( !menu )
	{
		QMenu* tmenu = mTypeMenus[ type ];
		
		if ( !tmenu )
		{
			tmenu = mMenu->addMenu( BasePlugin::typeToString( type ) );
			mTypeMenus[ type ] = tmenu;
		}
		
		menu = tmenu->addMenu( plugin->infos().Pixmap, plugin->infos().Caption );
		mMenus[ plugin ] = menu;
		
		menu->addAction( plugin->stateAction() );
		connect( plugin->stateAction(), SIGNAL( triggered( bool ) ), this, SLOT( actionEnable_triggered( bool ) ) );
		
		if ( plugin->infos().HaveSettingsWidget )
		{
			QAction* action = menu->addAction( tr( "Configure..." ) );
			action->setData( QVariant::fromValue( plugin ) );
			connect( action, SIGNAL( triggered() ), this, SLOT( actionConfigure_triggered() ) );
		}
		
		menu->addSeparator();
		
		QAction* actionNeverEnable = menu->addAction( tr( "No auto enable" ) );
		actionNeverEnable->setCheckable( true );
		actionNeverEnable->setChecked( plugin->neverEnable() );
		actionNeverEnable->setData( QVariant::fromValue( plugin ) );
		connect( actionNeverEnable, SIGNAL( triggered( bool ) ), this, SLOT( actionNeverEnable_triggered( bool ) ) );
		
		QAction* actionAbout = menu->addAction( tr( "About..." ) );
		actionAbout->setData( QVariant::fromValue( plugin ) );
		connect( actionAbout, SIGNAL( triggered() ), this, SLOT( actionAbout_triggered() ) );
	}
	else
	{
		QMenu* tmenu = mTypeMenus[ type ];
		
		if ( !tmenu )
		{
			tmenu = mMenu->addMenu( BasePlugin::typeToString( type ) );
			mTypeMenus[ type ] = tmenu;
		}
		
		tmenu->addMenu( menu );
	}
}

void PluginsMenu::addPlugin( BasePlugin* plugin )
{
	BasePlugin::Types type = plugin->infos().Type;
	
	initPluginMenusActions( plugin, BasePlugin::iAll );
	
	if ( type & BasePlugin::iBase )
	{
		initPluginMenusActions( plugin, BasePlugin::iBase );
	}
	else if ( type & BasePlugin::iChild )
	{
		initPluginMenusActions( plugin, BasePlugin::iChild );
	}
	else if ( type & BasePlugin::iCLITool )
	{
		initPluginMenusActions( plugin, BasePlugin::iCLITool );
	}
	else if ( type & BasePlugin::iBuilder )
	{
		initPluginMenusActions( plugin, BasePlugin::iBuilder );
	}
	else if ( type & BasePlugin::iDebugger )
	{
		initPluginMenusActions( plugin, BasePlugin::iDebugger );
	}
	else if ( type & BasePlugin::iInterpreter )
	{
		initPluginMenusActions( plugin, BasePlugin::iInterpreter );
	}
	else if ( type & BasePlugin::iXUP )
	{
		initPluginMenusActions( plugin, BasePlugin::iXUP );
	}
}

void PluginsMenu::actionEnable_triggered( bool checked )
{
	QAction* action = qobject_cast<QAction*>( sender() );
	BasePlugin* plugin = action->data().value<BasePlugin*>();
	
	action->setChecked( !checked );
	plugin->setEnabled( checked );
	
	MonkeyCore::settings()->setValue( QString( "Plugins/%1" ).arg( plugin->infos().Name ), checked );
}

void PluginsMenu::actionNeverEnable_triggered( bool checked )
{
	QAction* action = qobject_cast<QAction*>( sender() );
	BasePlugin* plugin = action->data().value<BasePlugin*>();
	
	plugin->setNeverEnable( checked );
}

void PluginsMenu::actionConfigure_triggered()
{
	QAction* action = qobject_cast<QAction*>( sender() );
	BasePlugin* plugin = action->data().value<BasePlugin*>();
	QWidget* widget = plugin->settingsWidget();
	
#ifdef Q_OS_MAC
#if QT_VERSION >= 0x040500
	widget->setParent( qApp->activeWindow(), Qt::Dialog | Qt::CustomizeWindowHint | Qt::WindowCloseButtonHint );
#else
	widget->setParent( qApp->activeWindow(), Qt::Dialog | Qt::CustomizeWindowHint | Qt::WindowSystemMenuHint );
#endif
#else
	widget->setParent( qApp->activeWindow(), Qt::Dialog );
#endif
	widget->setWindowModality( Qt::ApplicationModal );
	widget->setAttribute( Qt::WA_DeleteOnClose );
	widget->setWindowIcon( plugin->infos().Pixmap );
	widget->setWindowTitle( tr( "Settings - %1" ).arg( plugin->infos().Caption ) );
	widget->adjustSize();
	
	QRect rect = widget->frameGeometry();
	QRect drect = qApp->desktop()->availableGeometry( qApp->activeWindow() );
	rect.moveCenter( drect.center() );
	
	widget->move( rect.topLeft() );
	widget->show();
}

void PluginsMenu::actionAbout_triggered()
{
	QAction* action = qobject_cast<QAction*>( sender() );
	BasePlugin* plugin = action->data().value<BasePlugin*>();
	UIPluginsSettingsAbout about( plugin, qApp->activeWindow() );
	about.adjustSize();
	
	about.exec();
}
