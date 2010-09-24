#ifndef XUPPROJECTMODEL_H
#define XUPPROJECTMODEL_H

#include <objects/MonkeyExport.h>

#include <QAbstractItemModel>

class XUPProjectItem
class XUPItem
class QFileSystemWatcher

class Q_MONKEY_EXPORT XUPProjectModel : public QAbstractItemModel
    Q_OBJECT
    friend class XUPFilteredProjectModel
    friend class XUPProjectManager
    friend class XUPItem

public:
    enum CustomRole
        TypeRole = Qt.UserRole


    XUPProjectModel( parent = 0 )
    virtual ~XUPProjectModel()

    # QAbstractItemModel reimplementation
    virtual QModelIndex index( int row, column, parent = QModelIndex() )
    virtual QModelIndex parent(  QModelIndex& index )
    virtual int rowCount(  parent = QModelIndex() )
    virtual int columnCount(  parent = QModelIndex() )
    virtual QVariant headerData( int section, orientation, role = Qt.DisplayRole )
    virtual QVariant data(  QModelIndex& index, role = Qt.DisplayRole )
    virtual Qt.ItemFlags flags(  QModelIndex& index )

    #
    QModelIndex indexFromItem( XUPItem* item )
    XUPItem* itemFromIndex(  QModelIndex& index )
    XUPProjectItem* rootProject()

    # error handler
    void setLastError(  QString& error )
    QString lastError()

    # file watcher
    void registerWithFileWatcher( QFileSystemWatcher* watcher, project )
    void registerWithFileWatcher( QFileSystemWatcher* watcher )
    void unregisterWithFileWatcher( QFileSystemWatcher* watcher, project )
    void unregisterWithFileWatcher( QFileSystemWatcher* watcher )

    # XUP Project members
    virtual bool open(  QString& fileName, codec )
    virtual void close()

protected:
    XUPProjectItem* mRootProject
    QString mLastError


Q_DECLARE_METATYPE( XUPProjectModel* )

#endif # XUPPROJECTMODEL_H
