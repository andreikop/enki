#ifndef UIPLUGINSSETTINGSABOUT_H
#define UIPLUGINSSETTINGSABOUT_H

#include <objects/MonkeyExport.h>

#include "ui_UIPluginsSettingsAbout.h"

class BasePlugin;

class Q_MONKEY_EXPORT UIPluginsSettingsAbout : public QDialog, public Ui::UIPluginsSettingsAbout
{
    Q_OBJECT
    
public:
    UIPluginsSettingsAbout( BasePlugin* plugin, QWidget* parent = 0 );
};

#endif // UIPLUGINSSETTINGSABOUT_H
