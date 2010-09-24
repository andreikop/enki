#ifndef QMAKEPROJECTITEM_H
#define QMAKEPROJECTITEM_H

#include <xupmanager/core/XUPProjectItem.h>

class QMakeProjectItem : public XUPProjectItem
    Q_OBJECT

public:
    enum ProjectType { QMakeProject = 1

    QMakeProjectItem()
    virtual ~QMakeProjectItem()

    virtual QString toString()
    inline virtual int projectType()
        return QMakeProjectItem.QMakeProject

    virtual void registerProjectType()
    inline virtual XUPProjectItem* newProject()
        return QMakeProjectItem()

    virtual QString getVariableContent(  QString& variableName )
    virtual bool analyze( XUPItem* item )
    virtual bool open(  QString& fileName, codec )
    virtual bool save()
    virtual QString targetFilePath( allowToAskUser = False, type = XUPProjectItem.DefaultTarget, XUPProjectItem.PlatformType = XUPProjectItem.CurrentPlatform )

    virtual BuilderPlugin* builder(  plugin = QString() )
    virtual DebuggerPlugin* debugger(  plugin = QString() )
    virtual InterpreterPlugin* interpreter(  plugin = QString() )
    virtual void installCommands()

protected:
    bool handleSubdirs( XUPItem* subdirs )


#endif # QMAKEPROJECTITEM_H
