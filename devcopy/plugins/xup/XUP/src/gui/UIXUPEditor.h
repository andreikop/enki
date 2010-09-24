#ifndef UISIMPLEQMAKEEDITOR_H
#define UISIMPLEQMAKEEDITOR_H

#include "ui_UIXUPEditor.h"

#include <QMap>

class XUPProjectItem
class XUPItem

class UIXUPEditor : public QDialog, Ui.UIXUPEditor
    Q_OBJECT

public:
    UIXUPEditor( XUPProjectItem* project, parent = 0 )
    virtual ~UIXUPEditor()

    void setVariableEditorVisible( bool visible )
    bool isVariableEditorVisible()

protected:
    XUPProjectItem* mProject
    QMap<QString, mProjectFilesItems

    void updateMainFileComboBox(  QString& selectFile )
    void updateProjectFiles()

    void init( XUPProjectItem* project )

protected slots:
    # dynamic folder
    void on_tbDynamicFolder_clicked()

    # files
    void on_tbAddFile_clicked()
    void on_tbEditFile_clicked()
    void on_tbRemoveFile_clicked()

    void accept()


#endif # UISIMPLEQMAKEEDITOR_H
