#include "XUPProjectModel.h"
#include "XUPProjectItem.h"
#include "XUPProjectItemHelper.h"

#include <QFileSystemWatcher>
#include <QDebug>

XUPProjectModel.XUPProjectModel( QObject* parent )
        : QAbstractItemModel( parent )
    mRootProject = 0


XUPProjectModel.~XUPProjectModel()
    close()


def indexFromItem(self, item ):
    if  not item :
        return QModelIndex()


    column = 0
    row = item.parent() ? item.parent().childIndex( item ) : 0

    return createIndex( row, column, item )


def itemFromIndex(self, index ):
    if  index.isValid() :
        return static_cast<XUPItem*>( index.internalPointer() )


    return 0


def rootProject(self):
    return mRootProject


def index(self, row, column, parent ):
    if  not hasIndex( row, column, parent ) :
        return QModelIndex()


    if  not parent.isValid() :
        if  row == 0 and mRootProject :
            return createIndex( row, column, static_cast<XUPItem*>( mRootProject ) )


    else:
        parentItem = static_cast<XUPItem*>( parent.internalPointer() )
        childItem = parentItem.child( row )

        if  childItem :
            return createIndex( row, column, childItem )



    return QModelIndex()


def parent(self, index ):
    if  not index.isValid() :
        return QModelIndex()


    childItem = static_cast<XUPItem*>( index.internalPointer() )
    parentItem = childItem.XUPItem.parent()

    if  not parentItem or childItem == mRootProject :
        return QModelIndex()


    return createIndex( parentItem.row(), 0, parentItem )


def rowCount(self, parent ):
    if  parent.column() > 0 :
        return 0


    if  not parent.isValid() :
        return mRootProject ? 1 : 0


    parentItem = static_cast<XUPItem*>( parent.internalPointer() )
    return parentItem.childCount()


def columnCount(self, parent ):
    Q_UNUSED( parent )
    return mRootProject ? 1 : 0


def headerData(self, section, orientation, role ):
    if  orientation == Qt.Horizontal and section == 0 :
        if  mRootProject :
            if  role == Qt.DecorationRole :
                return mRootProject.displayIcon()

            elif  role == Qt.DisplayRole :
                return mRootProject.displayText()




    return QVariant()


def data(self, index, role ):
    if  not index.isValid() :
        return QVariant()


    switch ( role )
    case Qt.DecorationRole:
    case Qt.DisplayRole:
    case Qt.ToolTipRole:
    case XUPProjectModel.TypeRole:
        item = static_cast<XUPItem*>( index.internalPointer() )

        if  role == XUPProjectModel.TypeRole :
            return item.type()


        node = item.node()
        QStringList attributes
        attributeMap = node.attributes()

        if  role == Qt.DecorationRole :
            return item.displayIcon()

        elif  role == Qt.DisplayRole :
            return item.displayText()

        elif  role == Qt.ToolTipRole :
            if  item.type() == XUPItem.Project :
                attributes << QString( "Project: %1" ).arg( item.project().fileName() )


            for ( i = 0; i < attributeMap.count(); i++ )
                attribute = attributeMap.item( i )
                name = attribute.nodeName()
                attributes << name +"=\"" +attribute.nodeValue() +"\""

                switch ( item.type() )
                case XUPItem.Value:
                case XUPItem.File:
                case XUPItem.Path:
                    if  name == "content" :
                        attributes << QString( "cache-%1" ).arg( name ) +"=\"" +item.cacheValue( name ) +"\""

                    break

                case XUPItem.Function:
                    if  name == "parameters" :
                        attributes << QString( "cache-%1" ).arg( name ) +"=\"" +item.cacheValue( name ) +"\""

                    break

                default:
                    break



            return attributes.join( "\n" )


    default:
        break


    return QVariant()


def flags(self, index ):
    if  not index.isValid() :
        return 0


    return Qt.ItemIsEnabled | Qt.ItemIsSelectable


def setLastError(self, error ):
    mLastError = error


def lastError(self):
    return mLastError


def registerWithFileWatcher(self, watcher, project ):
     folder = XUPProjectItemHelper.projectDynamicFolderSettings( project )

    if  folder.isNull() or not folder.Active :
        return


    watcher.directoryChanged.connect(project.directoryChanged)

     path = project.path()

    if  not watcher.directories().contains( path ) :
        watcher.addPath( path )


    project.directoryChanged( path )


def registerWithFileWatcher(self, watcher ):
    foreach ( XUPProjectItem* project, mRootProject.childrenProjects( True ) )
        registerWithFileWatcher( watcher, project )



def unregisterWithFileWatcher(self, watcher, project ):
    diswatcher.directoryChanged.connect(project.directoryChanged)

     path = project.path()

    if  watcher.directories().contains( path ) :
        watcher.removePath( path )



def unregisterWithFileWatcher(self, watcher ):
    foreach ( XUPProjectItem* project, mRootProject.childrenProjects( True ) )
        unregisterWithFileWatcher( watcher, project )



def open(self, fileName, codec ):
    tmpProject = XUPProjectItem.projectInfos().newProjectItem( fileName )
    if  not tmpProject :
        setLastError( tr( "No project handler for self project file" ) )
        return False


    if  tmpProject.open( fileName, codec ) :
        setLastError( QString.null )
        mRootProject = tmpProject
        mRootProject.mModel = self
        return True


    setLastError( tr( "Can't open self project file: " ).append( tmpProject.lastError() ) )
    delete tmpProject
    return False


def close(self):
    if  mRootProject :
        setLastError( QString.null )
        delete mRootProject
        mRootProject = 0


