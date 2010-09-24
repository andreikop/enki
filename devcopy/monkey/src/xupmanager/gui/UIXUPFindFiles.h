#ifndef UIXUPFINDFILES_H
#define UIXUPFINDFILES_H

#include <objects/MonkeyExport.h>

#include "ui_UIXUPFindFiles.h"

#include <QFileInfo>

class Q_MONKEY_EXPORT UIXUPFindFiles : public QDialog, Ui.UIXUPFindFiles
    Q_OBJECT

public:
    UIXUPFindFiles(  QString& findFile, parent = 0 )
    virtual ~UIXUPFindFiles()

    void setFiles(  QFileInfoList& files, rootPath = QString.null )
    QString selectedFile()

protected slots:
    void on_lwFiles_itemSelectionChanged()
    void on_lwFiles_itemActivated( QListWidgetItem* item )
    void accept()


#endif # UIXUPFINDFILES_H
