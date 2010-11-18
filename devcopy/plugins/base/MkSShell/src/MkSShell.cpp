#include "MkSShell.h"

#include <widgets/pDockWidget.h>
#include <widgets/pDockToolBar.h>
#include <shellmanager/MkSShellConsole.h>
#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <widgets/pActionsManager.h>

class MkSShellDock : public pDockWidget
public:
    MkSShellDock( parent = 0 )
        : pDockWidget( parent )
        setWidget( MkSShellConsole( self ) )



def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "MkS Shell" )
    mPluginInfos.Description = tr( "This plugin allow you to manually use the MkS Shell interpreter" )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = False
    mPluginInfos.Pixmap = pIconManager.pixmap( "konsole.png", ":/icons" )


def install(self):
    mDock = MkSShellDock( MonkeyCore.mainWindow() )
    # add dock to dock toolbar entry
    MonkeyCore.mainWindow().dockToolBar( Qt.TopToolBarArea ).addDock( mDock, infos().Caption, QIcon( infos().Pixmap ) )
    # create menu action for the dock
    pActionsManager.setDefaultShortcut( mDock.toggleViewAction(), QKeySequence( "F6" ) )
    return True


def uninstall(self):
    mDock.deleteLater()
    return True


Q_EXPORT_PLUGIN2( BaseMkSShell, MkSShell )