#ifndef MKSSHELL_H
#define MKSSHELL_H

#include <pluginsmanager/BasePlugin.h>

class MkSShellDock;

class MkSShell : public BasePlugin
{
    Q_OBJECT
    Q_INTERFACES( BasePlugin )
    
protected:    
    void fillPluginInfos();
    virtual bool install();
    virtual bool uninstall();

    QPointer<MkSShellDock> mDock;
};

#endif // MKSSHELL_H