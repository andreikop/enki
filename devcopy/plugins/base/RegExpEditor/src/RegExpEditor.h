// TODO make it standalone application

#ifndef REGEXPEDITOR_H
#define REGEXPEDITOR_H

#include <pluginsmanager/BasePlugin.h>

class UIRegExpEditor;

class RegExpEditor : public BasePlugin
{
    Q_OBJECT
    Q_INTERFACES( BasePlugin )
    
protected:    
    void fillPluginInfos();
    virtual bool install();
    virtual bool uninstall();

    QPointer<UIRegExpEditor> mEditor;

protected slots:
    void action_triggered();
};

#endif // REGEXPEDITOR_H