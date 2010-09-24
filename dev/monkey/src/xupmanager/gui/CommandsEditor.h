#ifndef COMMANDSEDITOR_H
#define COMMANDSEDITOR_H

#include <objects/MonkeyExport.h>

#include "ui_CommandsEditor.h"
#include "xupmanager/core/XUPProjectItemHelper.h"

class Q_MONKEY_EXPORT CommandsEditor : public QFrame, public Ui::CommandsEditor
{
	Q_OBJECT

public:
	CommandsEditor( QWidget* parent = 0 );
	virtual ~CommandsEditor();
	
	void finalize();
	
	void setCommandTypes( const BasePluginTypeList& types );
	BasePluginTypeList commandTypes() const;
	
	void setCommands( const TypeCommandListMap& commands );
	TypeCommandListMap commands() const;
	
	void setCurrentType( BasePlugin::Type type );
	BasePlugin::Type currentType() const;
	
	void setParsers( const QStringList& parsers );
	QStringList parsers() const;

protected:
	BasePluginTypeList mCommandTypes;
	QStringList mParsers;
	TypeCommandListMap mCommands;
	BasePlugin::Type mLastCommandType;

protected slots:
	void updateGui();
	void on_cbCommandTypes_currentIndexChanged( int index );
	void on_tbCommandAdd_clicked();
	void on_tbCommandRemove_clicked();
	void on_tbCommandUp_clicked();
	void on_tbCommandDown_clicked();
	void on_lwCommands_itemSelectionChanged();
	void on_lwCommands_currentItemChanged( QListWidgetItem* current, QListWidgetItem* previous );
};

#endif // COMMANDSEDITOR_H
