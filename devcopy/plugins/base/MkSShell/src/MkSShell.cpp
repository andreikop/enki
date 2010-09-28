#include "MkSShell.h"

#include <widgets/pDockWidget.h>
#include <widgets/pDockToolBar.h>
#include <shellmanager/MkSShellConsole.h>
#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <widgets/pActionsManager.h>

class MkSShellDock : public pDockWidget
{
public:
    MkSShellDock( QWidget* parent = 0 )
        : pDockWidget( parent )
    {
        setWidget( new MkSShellConsole( this ) );
    }
};

void MkSShell::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "MkS Shell" );
    mPluginInfos.Description = tr( "This plugin allow you to manually use the MkS Shell interpreter" );
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>";
    mPluginInfos.Type = BasePlugin::iBase;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "1.0.0";
    mPluginInfos.FirstStartEnabled = false;
    mPluginInfos.Pixmap = pIconManager::pixmap( "konsole.png", ":/icons" );
}

bool MkSShell::install()
{
    mDock = new MkSShellDock( MonkeyCore::mainWindow() );
    // add dock to dock toolbar entry
    MonkeyCore::mainWindow()->dockToolBar( Qt::TopToolBarArea )->addDock( mDock, infos().Caption, QIcon( infos().Pixmap ) );
    // create menu action for the dock
    pActionsManager::setDefaultShortcut( mDock->toggleViewAction(), QKeySequence( "F6" ) );
    return true;
}

bool MkSShell::uninstall()
{
    mDock->deleteLater();
    return true;
}

Q_EXPORT_PLUGIN2( BaseMkSShell, MkSShell )