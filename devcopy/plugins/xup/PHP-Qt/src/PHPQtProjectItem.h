#ifndef PHPQTPROJECTITEM_H
#define PHPQTPROJECTITEM_H

#include <xupmanager/core/XUPProjectItem.h>

class PHPQtProjectItem : public XUPProjectItem
{
    Q_OBJECT

public:
    enum ProjectType { PHPQtProject = 2 };

    virtual int projectType() const;
    virtual void registerProjectType() const;
    virtual XUPProjectItem* newProject() const;

    virtual InterpreterPlugin* interpreter( const QString& plugin = QString() ) const;
    virtual void installCommands();
};

#endif // PHPQTPROJECTITEM_H
