

#include "Irc.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <consolemanager/pConsoleManager.h>
#include <widgets/pDockToolBar.h>

#include <QIcon>
#include <QTabWidget>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "Chat Irc" )
    mPluginInfos.Description = tr( "Plugin Irc for Monkey studio live" )
    mPluginInfos.Author = "Pinon yannick aka Xiantia <private mail>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = False
    mPluginInfos.Pixmap = QPixmap( ":/icons/irc.png" )


def install(self):
    # create docks
    mIrcDock = IrcDock.instance()
    # add docks to main window
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( mIrcDock, infos().Caption, QIcon( infos().Pixmap ) )
    return True


def uninstall(self):
    # delete docks
    delete mIrcDock
    return False


Q_EXPORT_PLUGIN2( BaseIrc, Irc )