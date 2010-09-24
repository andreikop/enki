#ifndef UISIMPLEQMAKEEDITOR_H
#define UISIMPLEQMAKEEDITOR_H

#include "ui_UIXUPEditor.h"

#include <QMap>

class XUPProjectItem;
class XUPItem;

class UIXUPEditor : public QDialog, public Ui::UIXUPEditor
{
	Q_OBJECT
	
public:
	UIXUPEditor( XUPProjectItem* project, QWidget* parent = 0 );
	virtual ~UIXUPEditor();
	
	void setVariableEditorVisible( bool visible );
	bool isVariableEditorVisible() const;

protected:
	XUPProjectItem* mProject;
	QMap<QString, QTreeWidgetItem*> mProjectFilesItems;
	
	void updateMainFileComboBox( const QString& selectFile );
	void updateProjectFiles();
	
	void init( XUPProjectItem* project );

protected slots:
	// dynamic folder
	void on_tbDynamicFolder_clicked();
	
	// files
	void on_tbAddFile_clicked();
	void on_tbEditFile_clicked();
	void on_tbRemoveFile_clicked();
	
	void accept();
};

#endif // UISIMPLEQMAKEEDITOR_H
