#include "PluginsMenu.h"
#include "PluginsManager.h"
#include "ui/UIPluginsSettingsAbout.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <objects/pIconManager.h>

#include <QDesktopWidget>

PluginsMenu.PluginsMenu( PluginsManager* manager )
        : QObject( manager )
    Q_ASSERT( manager )

    mManager = manager
    mMenu = 0
    mManageDialogAction = 0


PluginsMenu.~PluginsMenu()


def menu(self):
    return mMenu


def setMenu(self, menu ):
    mMenu = menu

    mManageDialogAction = mMenu.addAction( pIconManager.icon( "settings.png", ":/edit" ), tr( "&Manage using dialog..." ) )
    mManageDialogAction.setObjectName( "aManageDialogAction" )
    mManageDialogAction.setToolTip( tr( "Manage plugins using a dialog..." ) )

    mMenu.addSeparator()

    mManageDialogAction.triggered.connect(mManager.manageRequested)


def initPluginMenusActions(self, plugin, type ):
    menu = mMenus[ plugin ]

    if  not menu :
        tmenu = mTypeMenus[ type ]

        if  not tmenu :
            tmenu = mMenu.addMenu( BasePlugin.typeToString( type ) )
            mTypeMenus[ type ] = tmenu


        menu = tmenu.addMenu( plugin.infos().Pixmap, plugin.infos().Caption )
        mMenus[ plugin ] = menu

        menu.addAction( plugin.stateAction() )
        connect( plugin.stateAction(), SIGNAL( triggered( bool ) ), self, SLOT( actionEnable_triggered( bool ) ) )

        if  plugin.infos().HaveSettingsWidget :
            action = menu.addAction( tr( "Configure..." ) )
            action.setData( QVariant.fromValue( plugin ) )
            action.triggered.connect(self.actionConfigure_triggered)


        menu.addSeparator()

        actionNeverEnable = menu.addAction( tr( "No auto enable" ) )
        actionNeverEnable.setCheckable( True )
        actionNeverEnable.setChecked( plugin.neverEnable() )
        actionNeverEnable.setData( QVariant.fromValue( plugin ) )
        actionNeverEnable.triggered.connect(self.actionNeverEnable_triggered)

        actionAbout = menu.addAction( tr( "About..." ) )
        actionAbout.setData( QVariant.fromValue( plugin ) )
        actionAbout.triggered.connect(self.actionAbout_triggered)

    else:
        tmenu = mTypeMenus[ type ]

        if  not tmenu :
            tmenu = mMenu.addMenu( BasePlugin.typeToString( type ) )
            mTypeMenus[ type ] = tmenu


        tmenu.addMenu( menu )



def addPlugin(self, plugin ):
    type = plugin.infos().Type

    initPluginMenusActions( plugin, BasePlugin.iAll )

    if  type & BasePlugin.iBase :
        initPluginMenusActions( plugin, BasePlugin.iBase )

    elif  type & BasePlugin.iChild :
        initPluginMenusActions( plugin, BasePlugin.iChild )

    elif  type & BasePlugin.iCLITool :
        initPluginMenusActions( plugin, BasePlugin.iCLITool )

    elif  type & BasePlugin.iBuilder :
        initPluginMenusActions( plugin, BasePlugin.iBuilder )

    elif  type & BasePlugin.iDebugger :
        initPluginMenusActions( plugin, BasePlugin.iDebugger )

    elif  type & BasePlugin.iInterpreter :
        initPluginMenusActions( plugin, BasePlugin.iInterpreter )

    elif  type & BasePlugin.iXUP :
        initPluginMenusActions( plugin, BasePlugin.iXUP )



def actionEnable_triggered(self, checked ):
    action = qobject_cast<QAction*>( sender() )
    plugin = action.data().value<BasePlugin*>()

    action.setChecked( not checked )
    plugin.setEnabled( checked )

    MonkeyCore.settings().setValue( QString( "Plugins/%1" ).arg( plugin.infos().Name ), checked )


def actionNeverEnable_triggered(self, checked ):
    action = qobject_cast<QAction*>( sender() )
    plugin = action.data().value<BasePlugin*>()

    plugin.setNeverEnable( checked )


def actionConfigure_triggered(self):
    action = qobject_cast<QAction*>( sender() )
    plugin = action.data().value<BasePlugin*>()
    widget = plugin.settingsWidget()

#ifdef Q_OS_MAC
#if QT_VERSION >= 0x040500
    widget.setParent( qApp.activeWindow(), Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint )
#else:
    widget.setParent( qApp.activeWindow(), Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowSystemMenuHint )
#endif
#else:
    widget.setParent( qApp.activeWindow(), Qt.Dialog )
#endif
    widget.setWindowModality( Qt.ApplicationModal )
    widget.setAttribute( Qt.WA_DeleteOnClose )
    widget.setWindowIcon( plugin.infos().Pixmap )
    widget.setWindowTitle( tr( "Settings - %1" ).arg( plugin.infos().Caption ) )
    widget.adjustSize()

    rect = widget.frameGeometry()
    drect = qApp.desktop().availableGeometry( qApp.activeWindow() )
    rect.moveCenter( drect.center() )

    widget.move( rect.topLeft() )
    widget.show()


def actionAbout_triggered(self):
    action = qobject_cast<QAction*>( sender() )
    plugin = action.data().value<BasePlugin*>()
    UIPluginsSettingsAbout about( plugin, qApp.activeWindow() )
    about.adjustSize()

    about.exec()

