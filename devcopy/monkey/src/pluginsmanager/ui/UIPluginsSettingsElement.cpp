#include "UIPluginsSettingsElement.h"
#include "UIPluginsSettingsAbout.h"
#include "pluginsmanager/BasePlugin.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <QDesktopWidget>

UIPluginsSettingsElement::UIPluginsSettingsElement( BasePlugin* plugin, QWidget* p )
    : QWidget( p )
{
    Q_ASSERT( plugin );
    mPlugin = plugin;
    BasePlugin::PluginInfos infos = mPlugin->infos();
    
    // setup dialog
    setupUi( this );
    cbEnabled->setChecked( mPlugin->isEnabled() );
    
    if ( !mPlugin->infos().Pixmap.isNull() )
    {
        lIcon->setPixmap( mPlugin->infos().Pixmap.scaledToWidth( lIcon->maximumWidth(), Qt::SmoothTransformation ) );
    }
    
    lIcon->setEnabled( cbEnabled->isChecked() );
    lTitle->setText( infos.Caption );
    lDescription->setText( infos.Description );
    pbSettings->setVisible( mPlugin->infos().HaveSettingsWidget );
    cbNeverEnable->setChecked( mPlugin->neverEnable() );
}

BasePlugin* UIPluginsSettingsElement::plugin() const
{ return mPlugin; }

void UIPluginsSettingsElement::on_cbEnabled_toggled( bool checked )
{
    if ( checked )
        cbNeverEnable->setChecked( false );
    lIcon->setEnabled( checked );
    mPlugin->setEnabled( checked );
    MonkeyCore::settings()->setValue( QString( "Plugins/%1" ).arg( mPlugin->infos().Name ), checked );
}

void UIPluginsSettingsElement::on_pbSettings_clicked()
{
    QWidget* widget = mPlugin->settingsWidget();
    
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
    widget->setWindowIcon( mPlugin->infos().Pixmap );
    widget->setWindowTitle( tr( "Settings - %1" ).arg( mPlugin->infos().Caption ) );
    widget->adjustSize();
    
    QRect rect = widget->frameGeometry();
    QRect drect = qApp->desktop()->availableGeometry( qApp->activeWindow() );
    rect.moveCenter( drect.center() );
    
    widget->move( rect.topLeft() );
    widget->show();
}

void UIPluginsSettingsElement::on_pbAbout_clicked()
{
    UIPluginsSettingsAbout psa( mPlugin, window() );
    psa.adjustSize();
    psa.exec();
}

void UIPluginsSettingsElement::on_cbNeverEnable_toggled( bool checked )
{
    if ( checked )
        cbEnabled->setChecked( false );
    mPlugin->setNeverEnable( checked );
}
