#include "Tools.h"
#include "ToolsManager.h"
#include "ui/UIToolsEdit.h"
#include "ui/UIDesktopTools.h"

#include <coremanager/MonkeyCore.h>
#include <shellmanager/MkSShellInterpreter.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <widgets/pMenuBar.h>

#include <QFileInfo>

void Tools::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "Tools" );
    mPluginInfos.Description = tr( "A plugin that allow you to define some external tools in the menu bar" );
    mPluginInfos.Author = "Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>";
    mPluginInfos.Type = BasePlugin::iBase;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "0.5.0";
    mPluginInfos.FirstStartEnabled = false;
    mPluginInfos.HaveSettingsWidget = false;
    mPluginInfos.Pixmap = pIconManager::pixmap( "Tools.png", ":/icons" );
}

bool Tools::install()
{
    mToolsManager = new ToolsManager( this );
    pMenuBar* mb = MonkeyCore::menuBar();
    
    QMenu* menu = mb->menu( "mTools", tr( "Tools" ) );
    mb->beginGroup( "mTools" );
        mb->action( "aEditUser", tr( "&Edit User Tools..." ), QIcon( ":/tools/icons/tools/edit.png" ), QString::null, tr( "Edit tools..." ) );
        mb->action( "aEditDesktop", tr( "Edit &Desktop Tools..." ), QIcon( ":/tools/icons/tools/desktop.png" ), QString::null, tr( "Edit desktop tools..." ) );
        mb->action( "aSeparator1" );
        mb->menu( "mUserTools", tr( "&User Tools" ), QIcon( ":/tools/icons/tools/user.png" ) );
        mb->menu( "mDesktopTools", tr( "Desktop &Tools" ), QIcon( ":/tools/icons/tools/desktop.png" ) );
        mb->action( "aSeparator2" );
    mb->endGroup();
    
    mb->insertMenu( mb->menu( "mPlugins" )->menuAction(), menu );
    mb->action( "mTools/aEditUser" )->setData( ToolsManager::UserEntry );
    mb->action( "mTools/aEditDesktop" )->setData( ToolsManager::DesktopEntry );
    
    // actions connection
    connect( mb->action( "mTools/aEditUser" ), SIGNAL( triggered() ), mToolsManager, SLOT( editTools_triggered() ) );
    connect( mb->action( "mTools/aEditDesktop" ), SIGNAL( triggered() ), mToolsManager, SLOT( editTools_triggered() ) );
    connect( mb->menu( "mTools/mUserTools" ), SIGNAL( triggered( QAction* ) ), mToolsManager, SLOT( toolsMenu_triggered( QAction* ) ) );
    connect( mb->menu( "mTools/mDesktopTools" ), SIGNAL( triggered( QAction* ) ), mToolsManager, SLOT( toolsMenu_triggered( QAction* ) ) );
    
    // load script
    const QString filePath = mToolsManager->scriptFilePath();
    
    if ( !MonkeyCore::interpreter()->loadScript( filePath ) )
    {
        MonkeyCore::messageManager()->appendMessage( tr( "An error occur while loading script: '%1'" ).arg( QFileInfo( filePath ).fileName() ) );
    }
    
    return true;
}

bool Tools::uninstall()
{
    pMenuBar* mb = MonkeyCore::menuBar();
    
    // actions disconnection
    disconnect( mb->action( "mTools/aEditUser" ), SIGNAL( triggered() ), mToolsManager, SLOT( editTools_triggered() ) );
    disconnect( mb->action( "mTools/aEditDesktop" ), SIGNAL( triggered() ), mToolsManager, SLOT( editTools_triggered() ) );
    disconnect( mb->menu( "mTools/mUserTools" ), SIGNAL( triggered( QAction* ) ), mToolsManager, SLOT( toolsMenu_triggered( QAction* ) ) );
    disconnect( mb->menu( "mTools/mDesktopTools" ), SIGNAL( triggered( QAction* ) ), mToolsManager, SLOT( toolsMenu_triggered( QAction* ) ) );
    
    mb->deleteMenu( "mTools" );
    delete mToolsManager;
    
    return true;
}

Q_EXPORT_PLUGIN2( BaseTools, Tools )
