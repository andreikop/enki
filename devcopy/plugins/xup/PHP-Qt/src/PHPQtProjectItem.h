#ifndef PHPQTPROJECTITEM_H
#define PHPQTPROJECTITEM_H

#include <xupmanager/core/XUPProjectItem.h>

class PHPQtProjectItem : public XUPProjectItem
    Q_OBJECT

public:
    enum ProjectType { PHPQtProject = 2

    virtual int projectType()
    virtual void registerProjectType()
    virtual XUPProjectItem* newProject()

    virtual InterpreterPlugin* interpreter(  plugin = QString() )
    virtual void installCommands()


#endif # PHPQTPROJECTITEM_H
