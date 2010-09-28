#ifndef TOOLS_H
#define TOOLS_H

#include <pluginsmanager/BasePlugin.h>

#include <QPointer>

class ToolsManager;

class Tools : public BasePlugin
{
    Q_OBJECT
    Q_INTERFACES( BasePlugin )

protected:
    QPointer<ToolsManager> mToolsManager;
    
    virtual void fillPluginInfos();

    virtual bool install();
    virtual bool uninstall();
};

#endif // TOOLS_H
