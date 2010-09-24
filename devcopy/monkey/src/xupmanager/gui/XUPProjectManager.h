#ifndef XUPPROJECTMANAGER_H
#define XUPPROJECTMANAGER_H

#include <objects/MonkeyExport.h>

#include "ui_XUPProjectManager.h"
#include "xupmanager/core/XUPProjectItem.h"

#include <QMap>

class XUPProjectModel
class XUPFilteredProjectModel
class XUPItem

class Q_MONKEY_EXPORT XUPProjectManager : public pDockWidget, Ui.XUPProjectManager
    Q_OBJECT

public:
    enum ActionType { atNew = 0, atOpen, atClose, atCloseAll, atEdit, atAddFiles, atRemoveFiles

    XUPProjectManager( parent = 0 )
    virtual ~XUPProjectManager()

    QAction* action( XUPProjectManager.ActionType type )
    XUPProjectModel* currentProjectModel()
    XUPProjectItem* currentProject()
    XUPItem* currentItem()
    XUPProjectItemList topLevelProjects()

    void addFilesToScope( XUPItem* scope, allFiles, op = QString.null )

protected:
    QMap<XUPProjectManager.ActionType, mActions
    XUPFilteredProjectModel* mFilteredModel

    QString checkForBestAddOperator(  XUPItemList& variables )

public slots:
    bool openProject(  QString& fileName, codec )
    void newProject()
    bool openProject()
    void closeProject()
    void closeAllProjects()
    void editProject()
    void addFiles()
    void removeFiles()
    void setCurrentProject( XUPProjectItem* curProject, preProject )

protected slots:
    void setCurrentProjectModel( XUPProjectModel* model )
    void on_cbProjects_currentIndexChanged( int id )
    void tvFiltered_currentChanged(  QModelIndex& current, previous )
    void on_tvFiltered_activated(  QModelIndex& index )
    void on_tvFiltered_customContextMenuRequested(  QPoint& pos )

signals:
    void projectCustomContextMenuRequested(  QPoint& pos )

    void projectOpened( XUPProjectItem* project )
    void projectAboutToClose( XUPProjectItem* project )

    void currentProjectChanged( XUPProjectItem* currentProject, previousProject )
    void currentProjectChanged( XUPProjectItem* currentProject )

    void projectDoubleClicked( XUPProjectItem* project )
    void fileDoubleClicked( XUPProjectItem* project, fileName, codec )
    void fileDoubleClicked(  QString& fileName, codec )


#endif # XUPPROJECTMANAGER_H
