#ifndef VARIABLESEDITOR_H
#define VARIABLESEDITOR_H

#include <objects/MonkeyExport.h>

#include "ui_VariablesEditor.h"

class XUPProjectItem
class XUPItem

class Q_MONKEY_EXPORT VariablesEditor : public QFrame, Ui.VariablesEditor
    Q_OBJECT

public:
    VariablesEditor( parent = 0 )
    virtual ~VariablesEditor()

    inline QStringList& fileVariables()
        return mFileVariables

    inline QStringList& pathVariables()
        return mPathVariables

    inline QStringList& managedVariables()
        return mManagedVariables

    inline QStringList& variablesToRemove()
        return mVariablesToRemove

    inline QMap<QString, values()
        return mValues


    void init( XUPProjectItem* project )
    void finalize()

protected:
    QAction* aOthersValuesAddValue
    QAction* aOthersValuesAddFile
    QAction* aOthersValuesAddPath
    QAction* aOthersValuesEditValue
    QAction* aOthersValuesEditFile
    QAction* aOthersValuesEditPath

    XUPProjectItem* mProject
    QStringList mFileVariables
    QStringList mPathVariables
    QStringList mManagedVariables
    QStringList mVariablesToRemove
    QMap<QString, mValues

    XUPItem* getUniqueVariableItem(  QString& variableName, create )
    void updateValuesEditorVariables()
    void updateValuesEditorValues(  variable = QString.null )

protected slots:
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


#endif # VARIABLESEDITOR_H
