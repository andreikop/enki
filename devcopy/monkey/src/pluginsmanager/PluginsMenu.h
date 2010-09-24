#ifndef PLUGINSMENU_H
#define PLUGINSMENU_H

#include <QMenu>

#include "BasePlugin.h"

class PluginsManager

class PluginsMenu : public QObject
    Q_OBJECT

public:
    PluginsMenu( PluginsManager* manager )
    virtual ~PluginsMenu()

    QMenu* menu()
    void setMenu( QMenu* menu )

    void addPlugin( BasePlugin* plugin )

protected:
    PluginsManager* mManager
    QMenu* mMenu
    QAction* mManageDialogAction
    QMap<BasePlugin.Type, mTypeMenus
    QMap<BasePlugin*, mMenus

    void initPluginMenusActions( BasePlugin* plugin, type )

protected slots:
    void actionEnable_triggered( bool checked )
    void actionNeverEnable_triggered( bool checked )
    void actionConfigure_triggered()
    void actionAbout_triggered()


#endif # PLUGINSMENU_H
