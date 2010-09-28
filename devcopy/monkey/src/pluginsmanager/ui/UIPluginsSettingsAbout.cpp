#include "UIPluginsSettingsAbout.h"
#include "pluginsmanager/BasePlugin.h"

UIPluginsSettingsAbout::UIPluginsSettingsAbout( BasePlugin* plugin, QWidget* p )
    : QDialog( p )
{
    Q_ASSERT( plugin );
    BasePlugin::PluginInfos infos = plugin->infos();
    
    // setup dialog
    setupUi( this );
    setWindowTitle( windowTitle().arg( infos.Caption ) );
    lDescriptionInfos->setText( infos.Description );
    lVersionInfos->setText( infos.Version );
    lAuthorInfos->setText( infos.Author );
    lLicenseInfos->setText( infos.License.isEmpty() ? tr( "GNU General Public License" ) : infos.License );
    lTypesInfos->setText( BasePlugin::completeTypeToString( infos.Type ) );
    lLanguagesInfos->setText( infos.Languages.isEmpty() ? tr( "All" ) : infos.Languages.join( ", " ) );
}
