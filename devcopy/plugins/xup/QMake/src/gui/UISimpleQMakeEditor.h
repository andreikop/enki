#ifndef UISIMPLEQMAKEEDITOR_H
#define UISIMPLEQMAKEEDITOR_H

#include "ui_UISimpleQMakeEditor.h"
#include "QtVersionManager.h"

#include <QMap>

class XUPProjectItem
class XUPItem

class UISimpleQMakeEditor : public QDialog, Ui.UISimpleQMakeEditor
    Q_OBJECT
    
public:
    UISimpleQMakeEditor( XUPProjectItem* project, parent = 0 )
    virtual ~UISimpleQMakeEditor()

protected:
    XUPProjectItem* mProject
    QStringList mConfigGui
    QStringList mFileVariables
    QStringList mPathVariables
    QtVersion mQtVersion
    QMap<QString, mValues
    QMap<QString, mProjectFilesItems
    QStringList mManagedVariables
    
    QStringList mVariablesToRemove
    
    QAction* aOthersValuesAddValue
    QAction* aOthersValuesAddFile
    QAction* aOthersValuesAddPath
    QAction* aOthersValuesEditValue
    QAction* aOthersValuesEditFile
    QAction* aOthersValuesEditPath
    
    void updateProjectFiles()
    void updateValuesEditorVariables()
    void updateValuesEditorValues(  variable = QString.null )
    void init( XUPProjectItem* project )
    XUPItem* getUniqueVariableItem(  QString& variableName, create )

protected slots:
    void projectTypeChanged()
    void on_tbProjectTarget_clicked()
    void modules_itemSelectionChanged()
    void on_tbAddFile_clicked()
    void on_tbEditFile_clicked()
    void on_tbRemoveFile_clicked()
    
    # variables
    void on_lwOthersVariables_currentItemChanged( QListWidgetItem* current, previous )
    void on_tbOthersVariablesAdd_clicked()
    void on_tbOthersVariablesEdit_clicked()
    void on_tbOthersVariablesRemove_clicked()
    
    # values
    void on_lwOthersValues_currentItemChanged( QListWidgetItem* current, previous )
    void on_tbOthersValuesAdd_clicked()
    void on_tbOthersValuesAdd_triggered( QAction* action )
    void on_tbOthersValuesEdit_clicked()
    void on_tbOthersValuesEdit_triggered( QAction* action )
    void on_tbOthersValuesRemove_clicked()
    void on_tbOthersValuesClear_clicked()
    
    void accept()


#endif # UISIMPLEQMAKEEDITOR_H
