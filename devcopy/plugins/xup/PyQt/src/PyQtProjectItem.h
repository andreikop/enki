#ifndef PYQTPROJECTITEM_H
#define PYQTPROJECTITEM_H

#include <xupmanager/core/XUPProjectItem.h>

class PyQtProjectItem : public XUPProjectItem
    Q_OBJECT

public:
    enum ProjectType { PyQtProject = 3

    virtual int projectType()
    virtual void registerProjectType()
    virtual XUPProjectItem* newProject()

    virtual InterpreterPlugin* interpreter(  plugin = QString() )
    virtual void installCommands()


#endif # PYQTPROJECTITEM_H
