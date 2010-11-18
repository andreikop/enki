#ifndef XUPPROJECTMANAGER_H
#define XUPPROJECTMANAGER_H

#include <objects/MonkeyExport.h>

#include "ui_XUPProjectManager.h"
#include "xupmanager/core/XUPProjectItem.h"

#include <QMap>

class XUPProjectModel;
class XUPFilteredProjectModel;
class XUPItem;

class Q_MONKEY_EXPORT XUPProjectManager : public pDockWidget, public Ui::XUPProjectManager
{
	Q_OBJECT

public:
	enum ActionType { atNew = 0, atOpen, atClose, atCloseAll, atEdit, atAddFiles, atRemoveFiles };
	
	XUPProjectManager( QWidget* parent = 0 );
	virtual ~XUPProjectManager();
	
	QAction* action( XUPProjectManager::ActionType type );
	XUPProjectModel* currentProjectModel() const;
	XUPProjectItem* currentProject() const;
	XUPItem* currentItem() const;
	XUPProjectItemList topLevelProjects() const;
	
	void addFilesToScope( XUPItem* scope, const QStringList& allFiles, const QString& op = QString::null );

protected:
	QMap<XUPProjectManager::ActionType, QAction*> mActions;
	XUPFilteredProjectModel* mFilteredModel;
	
	QString checkForBestAddOperator( const XUPItemList& variables ) const;

public slots:
	bool openProject( const QString& fileName, const QString& codec );
	void newProject();
	bool openProject();
	void closeProject();
	void closeAllProjects();
	void editProject();
	void addFiles();
	void removeFiles();
	void setCurrentProject( XUPProjectItem* curProject, XUPProjectItem* preProject );

protected slots:
	void setCurrentProjectModel( XUPProjectModel* model );
	void on_cbProjects_currentIndexChanged( int id );
	void tvFiltered_currentChanged( const QModelIndex& current, const QModelIndex& previous );
	void on_tvFiltered_activated( const QModelIndex& index );
	void on_tvFiltered_customContextMenuRequested( const QPoint& pos );

signals:
	void projectCustomContextMenuRequested( const QPoint& pos );
	
	void projectOpened( XUPProjectItem* project );
	void projectAboutToClose( XUPProjectItem* project );
	
	void currentProjectChanged( XUPProjectItem* currentProject, XUPProjectItem* previousProject );
	void currentProjectChanged( XUPProjectItem* currentProject );
	
	void projectDoubleClicked( XUPProjectItem* project );
	void fileDoubleClicked( XUPProjectItem* project, const QString& fileName, const QString& codec );
	void fileDoubleClicked( const QString& fileName, const QString& codec );
};

#endif // XUPPROJECTMANAGER_H
