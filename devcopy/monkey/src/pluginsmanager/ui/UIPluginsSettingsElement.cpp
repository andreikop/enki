#include "UIPluginsSettingsElement.h"
#include "UIPluginsSettingsAbout.h"
#include "pluginsmanager/BasePlugin.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <QDesktopWidget>

UIPluginsSettingsElement.UIPluginsSettingsElement( BasePlugin* plugin, p )
        : QWidget( p )
    Q_ASSERT( plugin )
    mPlugin = plugin
    infos = mPlugin.infos()

    # setup dialog
    setupUi( self )
    cbEnabled.setChecked( mPlugin.isEnabled() )

    if  not mPlugin.infos().Pixmap.isNull() :
        lIcon.setPixmap( mPlugin.infos().Pixmap.scaledToWidth( lIcon.maximumWidth(), Qt.SmoothTransformation ) )


    lIcon.setEnabled( cbEnabled.isChecked() )
    lTitle.setText( infos.Caption )
    lDescription.setText( infos.Description )
    pbSettings.setVisible( mPlugin.infos().HaveSettingsWidget )
    cbNeverEnable.setChecked( mPlugin.neverEnable() )


def plugin(self):
    return mPlugin


def on_cbEnabled_toggled(self, checked ):
    if  checked :
        cbNeverEnable.setChecked( False )
    lIcon.setEnabled( checked )
    mPlugin.setEnabled( checked )
    MonkeyCore.settings().setValue( QString( "Plugins/%1" ).arg( mPlugin.infos().Name ), checked )


def on_pbSettings_clicked(self):
    widget = mPlugin.settingsWidget()

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
    widget.setWindowIcon( mPlugin.infos().Pixmap )
    widget.setWindowTitle( tr( "Settings - %1" ).arg( mPlugin.infos().Caption ) )
    widget.adjustSize()

    rect = widget.frameGeometry()
    drect = qApp.desktop().availableGeometry( qApp.activeWindow() )
    rect.moveCenter( drect.center() )

    widget.move( rect.topLeft() )
    widget.show()


def on_pbAbout_clicked(self):
    UIPluginsSettingsAbout psa( mPlugin, window() )
    psa.adjustSize()
    psa.exec()


def on_cbNeverEnable_toggled(self, checked ):
    if  checked :
        cbEnabled.setChecked( False )
    mPlugin.setNeverEnable( checked )

