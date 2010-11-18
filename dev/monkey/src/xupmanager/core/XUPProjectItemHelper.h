#ifndef XUPPROJECTITEMHELPER_H
#define XUPPROJECTITEMHELPER_H

#include <objects/MonkeyExport.h>

#include "pluginsmanager/BasePlugin.h"
#include "consolemanager/pCommand.h"

#include <QDomDocument>

class XUPItem;
class XUPProjectItem;

typedef QList<BasePlugin::Type> BasePluginTypeList;
typedef QMap<BasePlugin::Type, pCommandList> TypeCommandListMap;

struct Q_MONKEY_EXPORT XUPDynamicFolderSettings
{
	XUPDynamicFolderSettings()
	{
		Active = false;
	}
	
	bool isNull() const
	{
		return !Active && AbsolutePath.isEmpty() && FilesPatterns.isEmpty();
	}
	
	bool Active;
	QString AbsolutePath;
	QStringList FilesPatterns;
};

namespace XUPProjectItemHelper
{
	static const QString CommandsScopeName = "Commands";
	static const QString CommandScopeName = "Command";
	static const QString DynamicFolderSettingsName = "DynamicFolder.Settings";
	static const QString DynamicFolderName = "DynamicFolder";
	
	Q_MONKEY_EXPORT XUPItem* projectCommandsScope( XUPProjectItem* project, bool create );
	Q_MONKEY_EXPORT void addCommandProperty( XUPItem* variableItem, const QString& value );
	Q_MONKEY_EXPORT void setProjectCommands( XUPProjectItem* project, const TypeCommandListMap& commands );
	Q_MONKEY_EXPORT TypeCommandListMap projectCommands( XUPProjectItem* project );
	Q_MONKEY_EXPORT void installProjectCommands( XUPProjectItem* project );
	
	Q_MONKEY_EXPORT XUPItem* projectDynamicFolderSettingsItem( XUPProjectItem* project, bool create );
	Q_MONKEY_EXPORT void addDynamicFolderSettingsProperty( XUPItem* dynamicFolderItem, const QString& value );
	Q_MONKEY_EXPORT XUPDynamicFolderSettings projectDynamicFolderSettings( XUPProjectItem* project );
	Q_MONKEY_EXPORT void setProjectDynamicFolderSettings( XUPProjectItem* project, const XUPDynamicFolderSettings& folder );
	
	Q_MONKEY_EXPORT XUPItem* projectDynamicFolderItem( XUPProjectItem* project, bool create );
	Q_MONKEY_EXPORT void addDynamicFolderProperty( XUPItem* dynamicFolderItem, const QString& value );
	Q_MONKEY_EXPORT void updateDynamicFolder( XUPProjectItem* project, const QString& path );
	
	Q_MONKEY_EXPORT QDomDocument stripDynamicFolderFiles( const QDomDocument& document );
};

#endif // XUPPROJECTITEMHELPER_H
