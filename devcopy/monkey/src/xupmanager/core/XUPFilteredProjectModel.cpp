#include "XUPFilteredProjectModel.h"
#include "XUPProjectItem.h"

#include <QDebug>

def debug(self, root, mode ):
    if  mode == 0 :
        static prof = 0
        prep = QString().fill( ' ', prof )
        qWarning("%s", root.displayText().prepend( prep ).toLocal8Bit().constData() )
        it = mItemsMapping.constFind( root )
        Q_ASSERT( it != mItemsMapping.constEnd() )
        Q_ASSERT( it.value() )
        for item in it.value().mMappedChildren:
            prof += 4
            debug( item )
            prof -= 4


    else:
        for item in mItemsMapping.keys():
            qWarning() << "Mapped" << item.displayText()
            foreach ( XUPItem* it, mItemsMapping.constFind( item ).value().mMappedChildren )
                qWarning() << "\tChild" << it.displayText()





def xupItemLessThan(self, left, right ):
    return left.operator<( *right )


def qSortItems(self, items ):
    qSort( items.begin(), items.end(), xupItemLessThan )


XUPFilteredProjectModel.XUPFilteredProjectModel( QObject* parent, sourceModel )
        : QAbstractItemModel( parent )
    mSourceModel = 0
    setSourceModel( sourceModel )


XUPFilteredProjectModel.~XUPFilteredProjectModel()


def index(self, row, column, parentProxy ):
    item = mapToSource( parentProxy )
    it = mItemsMapping.constFind( item )

    if  it == mItemsMapping.constEnd() :
        if  row == 0 and column == 0 and mSourceModel :
            it = mItemsMapping.constFind( mSourceModel.mRootProject )

            if  it != mItemsMapping.constEnd() :
                index = createIndex( row, column, *it )
                it.value().mProxyIndex = index
                return index



    else:
        item = it.value().mMappedChildren.value( row )
        if  item :
            it = mItemsMapping.constFind( item )
            if  it != mItemsMapping.constEnd() :
                index = createIndex( row, column, *it )
                it.value().mProxyIndex = index
                return index




    return QModelIndex()


def parent(self, proxyIndex ):
    item = mapToSource( proxyIndex )
    it = mItemsMapping.constFind( item )

    if  it != mItemsMapping.constEnd() :
        parentItem = it.value().mParent
        it = mItemsMapping.constFind( parentItem )

        if  it != mItemsMapping.constEnd() :
            return it.value().mProxyIndex



    return QModelIndex()


def rowCount(self, proxyParent ):
    if  mSourceModel :
        item = mapToSource( proxyParent )
        it = mItemsMapping.constFind( item )

        if  it != mItemsMapping.constEnd() :
            return it.value().mMappedChildren.count()


        return 1


    return 0


def columnCount(self, proxyParent ):
    Q_UNUSED( proxyParent )
    return mSourceModel ? 1 : 0


def headerData(self, section, orientation, role ):
    return mSourceModel ? mSourceModel.headerData( section, orientation, role ) : QVariant()


def data(self, proxyIndex, role ):
    if  not proxyIndex.isValid() :
        return QVariant()


    item = mapToSource( proxyIndex )

    Q_ASSERT( item )

    return item.index().data( role )


def flags(self, proxyIndex ):
    if  not proxyIndex.isValid() :
        return 0


    return Qt.ItemIsEnabled | Qt.ItemIsSelectable


# MAPPING

def indexToIterator(self, proxyIndex ):
    Q_ASSERT( proxyIndex.isValid() )
     p = proxyIndex.internalPointer()
    Q_ASSERT( p )
    it = static_cast< Mapping*>( p ).mIterator
    Q_ASSERT( it != mItemsMapping.constEnd() )
    Q_ASSERT( it.value() )
    return it


def mapToSource(self, proxyIndex ):
    if  proxyIndex.isValid() :
        it = indexToIterator( proxyIndex )
        if  it != mItemsMapping.constEnd() :
            return it.key()

    return 0


def mapFromSource(self, sourceItem ):
    it = mItemsMapping.constFind( sourceItem )
    if  it != mItemsMapping.constEnd() :
        return it.value().mProxyIndex
    return QModelIndex()


def createMapping(self, item, parent ):
    it = mItemsMapping.constFind( item )
    if ( it != mItemsMapping.constEnd() ) # was mapped already
        return it

    m = Mapping
    it = XUPItemMappingIterator( mItemsMapping.insert( item, m ) )
    m.mParent = parent
    m.mIterator = it

    if  item != mSourceModel.mRootProject :
        Q_ASSERT( parent )
        parentIt = createMapping( parent )
        Q_ASSERT( parentIt != mItemsMapping.constEnd() )
        parentIt.value().mMappedChildren << item

    else:
        m.mParent = 0


    Q_ASSERT( it != mItemsMapping.constEnd() )
    Q_ASSERT( it.value() )

    return it


def removeMapping(self, item ):
    if  m = mItemsMapping.take( item ) :
        for ( i = 0; i < m.mMappedChildren.size(); ++i )
            removeMapping( m.mMappedChildren.at( i ) )


        if  item != mSourceModel.mRootProject :
            parentIt = mItemsMapping.constFind( m.mParent )

            if  parentIt != mItemsMapping.constEnd() :
                parentIt.value().mMappedChildren.removeAll( item )



        delete m



def clearMapping(self):
    qDeleteAll( mItemsMapping )
    mItemsMapping.clear()


def setSourceModel(self, model ):
    if  mSourceModel :
        dismSourceModel.rowsInserted.connect(self.internal_rowsInserted)
        dismSourceModel.rowsAboutToBeRemoved.connect(self.internal_rowsAboutToBeRemoved)
        dismSourceModel.dataChanged.connect(self.internal_dataChanged)


    mSourceModel = 0

    clearMapping()
    reset()

    if  model :
        mSourceModel = model

        mSourceModel.rowsInserted.connect(self.internal_rowsInserted)
        mSourceModel.rowsAboutToBeRemoved.connect(self.internal_rowsAboutToBeRemoved)
        mSourceModel.dataChanged.connect(self.internal_dataChanged)

        # header
        beginInsertColumns( QModelIndex(), 0, 0 )
        endInsertColumns()

        # tree items
        layoutAboutToBeChanged.emit()
        populateProject( mSourceModel.mRootProject )
        layoutChanged.emit()



def sourceModel(self):
    return mSourceModel


def getFilteredVariables(self, root ):
    XUPItemList variables
    rootProject = mSourceModel.mRootProject
     filteredVariables = rootProject.projectInfos().filteredVariables( rootProject.projectType() )

    for ( i = 0; i < root.childCount(); i++ )
        child = root.child( i )

        switch ( child.type() )
        case XUPItem.Project:
            populateProject( child.project() )
            break
        case XUPItem.Comment:
            break
        case XUPItem.EmptyLine:
            break
        case XUPItem.Variable:
            if  filteredVariables.contains( child.attribute( "name" ) ) :
                variables << child

            variables << getFilteredVariables( child )
            break
        case XUPItem.DynamicFolder:
            variables << child
            break
        case XUPItem.Value:
            break
        case XUPItem.Function:
            variables << getFilteredVariables( child )
            break
        case XUPItem.Scope:
            variables << getFilteredVariables( child )
            break
        default:
            break



    return variables


def getValues(self, root ):
    XUPItemList values
    for ( i = 0; i < root.childCount(); i++ )
        child = root.child( i )
        switch ( child.type() )
        case XUPItem.Value:
        case XUPItem.File:
        case XUPItem.Path:
            values << child
            break
        case XUPItem.Folder:
            values << getValues( child )
        default:
            break


    return values


def populateVariable(self, variable ):
    project = variable.project()
    projectIterator = mItemsMapping.constFind( project )

    if  projectIterator == mItemsMapping.constEnd() :
        return


    tmpValuesItem = getValues( variable )
    tmp = projectIterator.value().findVariable( variable.attribute( "name" ) )

    if  tmp :
        variable = tmp


    variableIterator = createMapping( variable, project )

    for value in tmpValuesItem:
         content = value.attribute( "content" )
        if  not content.isEmpty() and not variableIterator.value().findValue( content ) :
            createMapping( value, variable )



    variableValues = variableIterator.value().mMappedChildren
    qSortItems( variableValues )


def populateProject(self, project ):
    projectIterator = createMapping( project, project.parentProject() )

    variables = getFilteredVariables( project )

    for variable in variables:
        populateVariable( variable )


    projectVariables = projectIterator.value().mMappedChildren
    qSortItems( projectVariables )


def internal_rowsInserted(self, parent, start, end ):
    layoutAboutToBeChanged.emit()

    project = mSourceModel.mRootProject
     filteredVariables = project.projectInfos().filteredVariables( project.projectType() )

    for ( i = start; i < end +1; i++ )
        childIndex = mSourceModel.index( i, 0, parent )
        item = static_cast<XUPItem*>( childIndex.internalPointer() )

        switch ( item.type() )
        case XUPItem.Project:
            populateProject( item.project() )
            break
        case XUPItem.Variable:
            if  item.type() == XUPItem.Variable and filteredVariables.contains( item.attribute( "name" ) ) :
                populateVariable( item )

            break
        case XUPItem.DynamicFolder:
            populateVariable( item )
            break
        case XUPItem.Value:
        case XUPItem.File:
        case XUPItem.Path:
            if ( ( item.parent().type() == XUPItem.Variable and filteredVariables.contains( item.parent().attribute( "name" ) ) ) or
                    item.parent().type() == XUPItem.DynamicFolder )
                populateVariable( item.parent() )

            break
        case XUPItem.Scope:
        case XUPItem.Function:
            break
        default:
            break



    layoutChanged.emit()


def recursiveRemoveItems(self, item ):
    itemIt = mItemsMapping.constFind( item )

    if  itemIt == mItemsMapping.constEnd() :
        for ( i = item.childCount() -1; i > -1; i-- )
            recursiveRemoveItems( item.child( i ) )


    else:
        parentItem = itemIt.value().mParent
        parentIt = mItemsMapping.constFind( parentItem )

        if  parentIt != mItemsMapping.constEnd() :
            parentProxy = mapFromSource( parentItem )
            indexProxy = mapFromSource( item )
            indexRow = indexProxy.row()

            beginRemoveRows( parentProxy, indexRow, indexRow )
            removeMapping( item )
            endRemoveRows()




def internal_rowsAboutToBeRemoved(self, parent, start, end ):
    for ( i = start; i < end +1; i++ )
        item = static_cast<XUPItem*>( mSourceModel.index( start, 0, parent ).internalPointer() )
        recursiveRemoveItems( item )



def internal_dataChanged(self, topLeft, bottomRight ):
    Q_UNUSED( bottomRight )

    layoutAboutToBeChanged.emit()

    project = static_cast<XUPItem*>( topLeft.internalPointer() ).project()
    populateProject( project )

    layoutChanged.emit()

