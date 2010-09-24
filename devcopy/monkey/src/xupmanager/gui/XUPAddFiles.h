#ifndef XUPADDFILES_H
#define XUPADDFILES_H

#include "ui_XUPAddFiles.h"

class XUPProjectModelProxy
class XUPProjectModel
class XUPItem

class XUPAddFiles : public QWidget, Ui.XUPAddFiles
    Q_OBJECT

public:
    XUPAddFiles( parent = 0 )
    virtual ~XUPAddFiles()

    void setModel( XUPProjectModel* model )
    XUPProjectModel* model()

    void setAddToProjectChoice( bool choice )
    bool addToProjectChoice()

    void setAddToProject( bool add )
    bool addToProject()

    void setCurrentScope( XUPItem* item )
    XUPItem* currentScope()

    void setImportExternalFiles( bool import )
    bool importExternalFiles()

    void setImportExternalFilesPath(  QString& path )
    QString importExternalFilesPath()

    void setScopeChoiceEnabled( bool enabled )
    void setImportExternalFilesPathEnabled( bool enabled )

protected:
    XUPProjectModelProxy* mProxy
    XUPProjectModel* mModel

protected slots:
    void on_tcbScopes_currentChanged(  QModelIndex& index )

signals:
    void currentScopeChanged( XUPItem* scope )


#endif # XUPADDFILES_H
