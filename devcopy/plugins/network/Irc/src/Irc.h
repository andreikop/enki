


#ifndef IRC_H
#define IRC_H

#include <pluginsmanager/BasePlugin.h>
#include "IrcDock.h"



class Irc : public BasePlugin
    Q_OBJECT
    Q_INTERFACES( BasePlugin )

protected:
    void fillPluginInfos()
    virtual bool install()
    virtual bool uninstall()

    IrcDock *mIrcDock


#endif