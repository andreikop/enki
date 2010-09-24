#include "SearchAndReplaceSettings.h"

SearchAndReplaceSettings.SearchAndReplaceSettings( SearchAndReplace* plugin, parent )
        : QWidget( parent )
    Q_ASSERT( plugin )
    mPlugin = plugin

    setupUi( self )

    loadSettings( mPlugin.settings() )


SearchAndReplaceSettings.~SearchAndReplaceSettings()


def loadSettings(self, settings ):
    cbReplaceSearchText.setChecked( settings.replaceSearchText )
    cbOnlyWhenNotVisible.setChecked( settings.onlyWhenNotVisible )
    cbOnlyWhenNotRegExp.setChecked( settings.onlyWhenNotRegExp )
    cbOnlyWhenNotEmpty.setChecked( settings.onlyWhenNotEmpty )


def restoreDefault(self):
    loadSettings( SearchAndReplace.Settings() )


def reject(self):
    close()


def accept(self):
    SearchAndReplace.Settings settings

    settings.replaceSearchText = cbReplaceSearchText.isChecked()
    settings.onlyWhenNotVisible = cbOnlyWhenNotVisible.isChecked()
    settings.onlyWhenNotRegExp = cbOnlyWhenNotRegExp.isChecked()
    settings.onlyWhenNotEmpty = cbOnlyWhenNotEmpty.isChecked()

    mPlugin.setSettings( settings )

    close()


def on_dbbButtons_clicked(self, button ):
    switch ( dbbButtons.standardButton( button ) )
    case QDialogButtonBox.Help:
        #help()
        break
    case QDialogButtonBox.RestoreDefaults:
        restoreDefault()
        break
    case QDialogButtonBox.Ok:
        accept()
        break
    case QDialogButtonBox.Cancel:
        reject()
        break
    default:
        break


