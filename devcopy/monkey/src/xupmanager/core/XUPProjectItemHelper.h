#ifndef XUPPROJECTITEMHELPER_H
#define XUPPROJECTITEMHELPER_H

#include <objects/MonkeyExport.h>

#include "pluginsmanager/BasePlugin.h"
#include "consolemanager/pCommand.h"

#include <QDomDocument>

class XUPItem
class XUPProjectItem

typedef QList<BasePlugin.Type> BasePluginTypeList
typedef QMap<BasePlugin.Type, TypeCommandListMap

struct Q_MONKEY_EXPORT XUPDynamicFolderSettings
    XUPDynamicFolderSettings()
        Active = False


    bool isNull()
        return not Active and AbsolutePath.isEmpty() and FilesPatterns.isEmpty()


    bool Active
    QString AbsolutePath
    QStringList FilesPatterns


namespace XUPProjectItemHelper
static  CommandsScopeName = "Commands"
static  CommandScopeName = "Command"
static  DynamicFolderSettingsName = "DynamicFolder.Settings"
static  DynamicFolderName = "DynamicFolder"

Q_MONKEY_EXPORT XUPItem* projectCommandsScope( XUPProjectItem* project, create )
Q_MONKEY_EXPORT void addCommandProperty( XUPItem* variableItem, value )
Q_MONKEY_EXPORT void setProjectCommands( XUPProjectItem* project, commands )
Q_MONKEY_EXPORT TypeCommandListMap projectCommands( XUPProjectItem* project )
Q_MONKEY_EXPORT void installProjectCommands( XUPProjectItem* project )

Q_MONKEY_EXPORT XUPItem* projectDynamicFolderSettingsItem( XUPProjectItem* project, create )
Q_MONKEY_EXPORT void addDynamicFolderSettingsProperty( XUPItem* dynamicFolderItem, value )
Q_MONKEY_EXPORT XUPDynamicFolderSettings projectDynamicFolderSettings( XUPProjectItem* project )
Q_MONKEY_EXPORT void setProjectDynamicFolderSettings( XUPProjectItem* project, folder )

Q_MONKEY_EXPORT XUPItem* projectDynamicFolderItem( XUPProjectItem* project, create )
Q_MONKEY_EXPORT void addDynamicFolderProperty( XUPItem* dynamicFolderItem, value )
Q_MONKEY_EXPORT void updateDynamicFolder( XUPProjectItem* project, path )

Q_MONKEY_EXPORT QDomDocument stripDynamicFolderFiles(  QDomDocument& document )


#endif # XUPPROJECTITEMHELPER_H
