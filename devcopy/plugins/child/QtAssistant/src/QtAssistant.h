#ifndef QTASSISTANT_H
#define QTASSISTANT_H

#include <pluginsmanager/ChildPlugin.h>

#include <QPointer>

class QtAssistant : public ChildPlugin
    Q_OBJECT
    Q_INTERFACES( BasePlugin ChildPlugin )

public:
    virtual QWidget* settingsWidget()
    virtual pAbstractChild* createDocument(  QString& fileName )

protected:
    QPointer<class QtAssistantDock> mDock

    virtual void fillPluginInfos()

    virtual bool install()
    virtual bool uninstall()

protected slots:
    void helpShown()


#endif # QTASSISTANT_H
