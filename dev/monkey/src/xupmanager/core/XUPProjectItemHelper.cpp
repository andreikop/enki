#include "XUPProjectItemHelper.h"
#include "XUPProjectItem.h"
#include "pMonkeyStudio.h"

#include <QDir>
#include <QDebug>

XUPItem* XUPProjectItemHelper::projectCommandsScope( XUPProjectItem* project, bool create )
{
	XUPItem* settingsScope = project->projectSettingsScope( create );
	
	if ( !settingsScope )
	{
		return 0;
	}
	
	foreach ( XUPItem* child, settingsScope->childrenList() )
	{
		if ( child->type() == XUPItem::Scope && child->attribute( "name" ) == CommandsScopeName )
		{
			return child;
		}
	}
	
	if ( !create )
	{
		return 0;
	}
	
	XUPItem* commandsScope = settingsScope->addChild( XUPItem::Scope );
	commandsScope->setAttribute( "name", CommandsScopeName );
	commandsScope->setAttribute( "nested", "false" );
	return commandsScope;
}

void XUPProjectItemHelper::addCommandProperty( XUPItem* variableItem, const QString& value )
{
	XUPItem* valueItem = variableItem->addChild( XUPItem::Value );
	valueItem->setAttribute( "content", value );
}

void XUPProjectItemHelper::setProjectCommands( XUPProjectItem* project, const TypeCommandListMap& commands )
{
	bool emptyCommands = true;
	
	foreach ( const BasePlugin::Type& type, commands.keys() )
	{
		if ( commands[ type ].isEmpty() )
		{
			continue;
		}
		
		emptyCommands = false;
		break;
	}
	
	XUPItem* commandsScope = projectCommandsScope( project, !emptyCommands );
	
	if ( !commandsScope )
	{
		return;
	}
	
	// delete scope if no commands
	if ( emptyCommands )
	{
		commandsScope->parent()->removeChild( commandsScope );
		return;
	}
	
	// clear existing commands
	foreach ( XUPItem* child, commandsScope->childrenList() )
	{
		commandsScope->removeChild( child );
	}
	
	// create new ones
	foreach ( const BasePlugin::Type& type, commands.keys() )
	{
		foreach ( const pCommand& command, commands[ type ] )
		{
			XUPItem* variable = commandsScope->addChild( XUPItem::Variable );
			variable->setAttribute( "name", CommandScopeName );
			variable->setAttribute( "operator", "=" );
			variable->setAttribute( "multiline", "true" );
			
			addCommandProperty( variable, QString::number( type ) );
			addCommandProperty( variable, command.text() );
			addCommandProperty( variable, command.command() );
			addCommandProperty( variable, command.arguments() );
			addCommandProperty( variable, command.workingDirectory() );
			addCommandProperty( variable, command.parsers().join( ";" ) );
			addCommandProperty( variable, command.skipOnError() ? "1" : "0" );
			addCommandProperty( variable, command.tryAllParsers() ? "1" : "0" );
		}
	}
}

TypeCommandListMap XUPProjectItemHelper::projectCommands( XUPProjectItem* project )
{
	TypeCommandListMap commands;
	XUPItem* commandsScope = projectCommandsScope( project, false );
	
	if ( commandsScope )
	{
		foreach ( XUPItem* commandVariable, commandsScope->childrenList() )
		{
			QVariantList values;
			
			foreach ( XUPItem* commandValue, commandVariable->childrenList() )
			{
				values << commandValue->attribute( "content" );
			}
			
			if ( values.count() != 8 )
			{
				qWarning() << "Skip reading incomplete command";
				Q_ASSERT( 0 );
				continue;
			}
			
			pCommand command;
			
			command.setText( values.at( 1 ).toString() );
			command.setCommand( values.at( 2 ).toString() );
			command.setArguments( values.at( 3 ).toString() );
			command.setWorkingDirectory( values.at( 4 ).toString() );
			command.setParsers( values.at( 5 ).toString().split( ";", QString::SkipEmptyParts ) );
			command.setSkipOnError( values.at( 6 ).toBool() );
			command.setTryAllParsers( values.at( 7 ).toBool() );
			
			commands[ (BasePlugin::Type)values.at( 0 ).toInt() ] << command;
		}
	}
	
	return commands;
}

void XUPProjectItemHelper::installProjectCommands( XUPProjectItem* project )
{
	const TypeCommandListMap commands = projectCommands( project );
	
	foreach ( const BasePlugin::Type& type, commands.keys() )
	{
		foreach ( pCommand command, commands[ type ] )
		{
			switch ( type )
			{
				case BasePlugin::iBuilder:
					project->addCommand( command, "mBuilder" );
					break;
				case BasePlugin::iDebugger:
					project->addCommand( command, "mDebugger" );
					break;
				case BasePlugin::iInterpreter:
					project->addCommand( command, "mInterpreter" );
					break;
				default:
					Q_ASSERT( 0 );
					break;
			}
		}
	}
}

XUPItem* XUPProjectItemHelper::projectDynamicFolderSettingsItem( XUPProjectItem* project, bool create )
{
	foreach ( XUPItem* child, project->childrenList() )
	{
		if ( child->type() == XUPItem::Variable && child->attribute( "name" ) == DynamicFolderSettingsName )
		{
			return child;
		}
	}
	
	if ( !create )
	{
		return 0;
	}
	
	XUPItem* dynamicFolderSettingsItem = project->addChild( XUPItem::Variable );
	dynamicFolderSettingsItem->setAttribute( "name", DynamicFolderSettingsName );
	dynamicFolderSettingsItem->setAttribute( "operator", "=" );
	dynamicFolderSettingsItem->setAttribute( "multiline", "true" );
	return dynamicFolderSettingsItem;
}

void XUPProjectItemHelper::addDynamicFolderSettingsProperty( XUPItem* dynamicFolderSettingsItem, const QString& value )
{
	XUPItem* valueItem = dynamicFolderSettingsItem->addChild( XUPItem::Value );
	valueItem->setAttribute( "content", value );
}

XUPDynamicFolderSettings XUPProjectItemHelper::projectDynamicFolderSettings( XUPProjectItem* project )
{
	XUPDynamicFolderSettings folder;
	XUPItem* dynamicFolderSettingsItem = projectDynamicFolderSettingsItem( project, false );
	
	if ( dynamicFolderSettingsItem )
	{
		QVariantList values;
		
		foreach ( XUPItem* valueItem, dynamicFolderSettingsItem->childrenList() )
		{
			values << valueItem->attribute( "content" );
		}
		
		if ( values.count() != 3 )
		{
			qWarning() << "Skip reading incomplete dynamic folder settings";
			Q_ASSERT( 0 );
			return folder;
		}
		
		folder.Active = values.at( 0 ).toBool();
		folder.AbsolutePath = project->filePath( values.at( 1 ).toString() );
		folder.FilesPatterns = values.at( 2 ).toString().split( ";", QString::SkipEmptyParts );
		
		if ( folder.AbsolutePath.isEmpty() && folder.Active )
		{
			folder.AbsolutePath = project->path();
		}
	}
	
	return folder;
}

void XUPProjectItemHelper::setProjectDynamicFolderSettings( XUPProjectItem* project, const XUPDynamicFolderSettings& folder )
{
	XUPItem* dynamicFolderSettingsItem = projectDynamicFolderSettingsItem( project, !folder.isNull() );
	
	if ( dynamicFolderSettingsItem )
	{
		// clear existing values
		foreach ( XUPItem* child, dynamicFolderSettingsItem->childrenList() )
		{
			dynamicFolderSettingsItem->removeChild( child );
		}
		
		addDynamicFolderSettingsProperty( dynamicFolderSettingsItem, folder.Active ? "1" : "0" );
		addDynamicFolderSettingsProperty( dynamicFolderSettingsItem, folder.AbsolutePath );
		addDynamicFolderSettingsProperty( dynamicFolderSettingsItem, folder.FilesPatterns.join( ";" ) );
	}
}

XUPItem* XUPProjectItemHelper::projectDynamicFolderItem( XUPProjectItem* project, bool create )
{
	foreach ( XUPItem* child, project->childrenList() )
	{
		if ( child->type() == XUPItem::DynamicFolder && child->attribute( "name" ) == DynamicFolderName )
		{
			return child;
		}
	}
	
	if ( !create )
	{
		return 0;
	}
	
	XUPItem* dynamicFolderItem = project->addChild( XUPItem::DynamicFolder );
	dynamicFolderItem->setAttribute( "name", DynamicFolderName );
	dynamicFolderItem->setAttribute( "operator", "=" );
	dynamicFolderItem->setAttribute( "multiline", "true" );
	return dynamicFolderItem;
}

void XUPProjectItemHelper::addDynamicFolderProperty( XUPItem* dynamicFolderItem, const QString& value )
{
	XUPItem* valueItem = dynamicFolderItem->addChild( XUPItem::File );
	valueItem->setAttribute( "content", value );
}

void XUPProjectItemHelper::updateDynamicFolder( XUPProjectItem* project, const QString& path )
{
	XUPItem* dynamicFolderItem = projectDynamicFolderItem( project, true );
	const XUPDynamicFolderSettings folder = projectDynamicFolderSettings( project );
	const bool samePath = QDir::cleanPath( path ) == QDir::cleanPath( folder.AbsolutePath );
	
	if ( !dynamicFolderItem || !samePath )
	{
		return;
	}
	
	foreach ( XUPItem* child, dynamicFolderItem->childrenList() )
	{
		dynamicFolderItem->removeChild( child );
	}
	
	QDir dir( path );
	QFileInfoList files = pMonkeyStudio::getFiles( dir, folder.FilesPatterns, false );
	
	if ( !folder.Active || files.isEmpty() )
	{
		project->removeChild( dynamicFolderItem );
		return;
	}
	
	foreach ( const QFileInfo& file, files )
	{
		addDynamicFolderProperty( dynamicFolderItem, file.absoluteFilePath() );
	}
}

QDomDocument XUPProjectItemHelper::stripDynamicFolderFiles( const QDomDocument& document )
{
	QDomDocument doc = document.cloneNode().toDocument();
	const QDomNodeList nodesToRemove = doc.elementsByTagName( "dynamicfolder" );
	
	for ( int i = 0; i < nodesToRemove.count(); i++ )
	{
		const QDomNode& node = nodesToRemove.at( i );
		node.parentNode().removeChild( node );
	}
	
	return doc;
}
