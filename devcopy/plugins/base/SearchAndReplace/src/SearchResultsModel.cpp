#include "SearchResultsModel.h"
#include "SearchThread.h"

SearchResultsModel.SearchResultsModel( SearchThread* searchThread, parent )
        : QAbstractItemModel( parent )
    Q_ASSERT( searchThread )
    mRowCount = 0
    mSearchThread = searchThread

    # connections
    mSearchThread.reset.connect(self.thread_reset)
    mSearchThread.resultsAvailable.connect(self.thread_resultsAvailable)


def columnCount(self, parent ):
    Q_UNUSED( parent )
    return 1


def data(self, index, role ):
    if  not index.isValid() :
        return QVariant()


    result = self.result( index )

    Q_ASSERT( result )

    switch ( role )
    case Qt.DisplayRole:
        QString text

        # index is a root parent
        if  mParentsList.value( index.row() ) == result :
             count = rowCount( index )
            text = mSearchDir.relativeFilePath( result.fileName )
            text.append( QString( " (%1)" ).arg( count ) )

        # index is a root parent child
        else:
            text = tr( "Line: %1, Column: %2: %3" ).arg( result.position.y() +1 ).arg( result.position.x() ).arg( result.capture )


        return text

    case Qt.ToolTipRole:
        return data( index, Qt.DisplayRole )

    case Qt.CheckStateRole:
        if  flags( index ) & Qt.ItemIsUserCheckable :
            return result.checkState


        break



    return QVariant()


def index(self, row, column, parent ):
    if  row >= rowCount( parent ) or column >= columnCount( parent ) :
        return QModelIndex()


    result = self.result( parent )

    # parent is a root parent
    if  result and mParentsList.value( parent.row() ) == result :
        result = mResults.at( parent.row() ).at( row )
        return createIndex( row, column, result )


    Q_ASSERT( not parent.isValid() )

    # parent is invalid
    return createIndex( row, column, mParentsList[ row ] )


def parent(self, index ):
    if  not index.isValid() :
        return QModelIndex()


    result = self.result( index )

    # index is a root parent
    if  result and mParentsList.value( index.row() ) == result :
        return QModelIndex()


    Q_ASSERT( index.isValid() )

    result = mParents[ result.fileName ]
     row = mParentsList.indexOf( result )

    # index is a root parent child
    return createIndex( row, index.column(), result )


def rowCount(self, parent ):
    # root parents
    if  not parent.isValid() :
        return mRowCount


    return parent.parent().isValid() ? 0 : mResults.at( parent.row() ).count()


def flags(self, index ):
    flags = QAbstractItemModel.flags( index )
    properties = mSearchThread.properties()

    if  properties.mode & SearchAndReplace.ModeFlagReplace :
        flags |= Qt.ItemIsUserCheckable


    result = self.result( index )

    if  result :
        if  not result.enabled :
            flags &= ~Qt.ItemIsEnabled
            flags &= ~Qt.ItemIsSelectable



    return flags


def hasChildren(self, parent ):
    # root parents
    if  not parent.isValid() :
        return mRowCount != 0


    return parent.parent().isValid() ? False : not mResults.at( parent.row() ).isEmpty()


def setData(self, index, value, role ):
    result = self.result( index )
    ok = False

    switch ( role )
    case Qt.CheckStateRole:
        ok = True
        break

    case SearchResultsModel.EnabledRole:
        result.enabled = value.toBool()
        ok = True
        break



    if  role != Qt.CheckStateRole :
        if  ok :
            dataChanged.emit( index, index )


        return ok


     state = Qt.CheckState( value.toInt() )
     pIndex = index.parent()
     isParent = not pIndex.isValid()
    pResult = self.result( pIndex )

    Q_ASSERT( result )

    if  isParent :
         pRow = mParentsList.indexOf( result )
        checkedCount = 0

        # update all children to same state as parent
        foreach ( SearchResultsModel.Result* r, mResults.at( pRow ) )
            if  r.enabled :
                r.checkState = state
                checkedCount++



         left = index.child( 0, 0 )
         right = index.child( rowCount( index ) -1, columnCount( index ) -1 )
        # update root parent children
        dataChanged.emit( left, right )

        if  state == Qt.Unchecked :
            checkedCount = 0


        if  ( checkedCount == 0 and state == Qt.Checked ) or result.checkState == state :
            ok = False


        if  ok :
            result.checkState = state


    else:
         pRow = mParentsList.indexOf( pResult )
        count = 0
        checkedCount = 0

        foreach ( SearchResultsModel.Result* r, mResults.at( pRow ) )
            count++

            if  r.checkState == Qt.Checked :
                checkedCount++



        if  state == Qt.Checked :
            checkedCount++

        else:
            checkedCount--


        result.checkState = state

        # update parent
        if  checkedCount == 0 :
            pResult.checkState = Qt.Unchecked

        elif  checkedCount == count :
            pResult.checkState = Qt.Checked

        else:
            pResult.checkState = Qt.PartiallyChecked


        # update root parent index
        dataChanged.emit( pIndex, pIndex )


    # update clicked index
    dataChanged.emit( index, index )

    return ok


def index(self, result ):
     QModelIndex index
    row = mParentsList.indexOf( result )

    if  row != -1 :
        return createIndex( row, 0, result )

    elif  result :
        pResult = mParents.value( result.fileName )

        if  pResult :
            row = mParentsList.indexOf( pResult )

            if  row != -1 :
                row = mResults.at( row ).indexOf( result )
                return createIndex( row, 0, result )




    return index


def result(self, index ):
    return index.isValid() ? static_cast<SearchResultsModel.Result*>( index.internalPointer() ) : 0


 QList<SearchResultsModel.ResultList>& SearchResultsModel.results()
    return mResults


def clear(self):
    if  mRowCount == 0 :
        return


    beginRemoveRows( QModelIndex(), 0, mRowCount -1 )

    foreach (  SearchResultsModel.ResultList& results, mResults )
        qDeleteAll( results )


    mResults.clear()
    qDeleteAll( mParents )
    mParents.clear()
    mParentsList.clear()
    mRowCount = 0

    endRemoveRows()


def thread_reset(self):
    clear()


def thread_resultsAvailable(self, fileName, results ):
    if  mRowCount == 0 :
        firstResultsAvailable.emit()


    result = mParents[ fileName ]
    properties = mSearchThread.properties()

    if  mRowCount == 0 :
        mSearchDir.setPath( properties.searchPath )


    if  not result :
        result = SearchResultsModel.Result( fileName )
        result.checkable = properties.mode & SearchAndReplace.ModeFlagReplace
        result.checkState = result.checkable ? Qt.Checked : Qt.Unchecked

        beginInsertRows( QModelIndex(), mRowCount, mRowCount )
        mParents[ fileName ] = result
        mParentsList << result
        mRowCount++
        mResults << results
        endInsertRows()

    else:
         pRow = mParentsList.indexOf( result )
         count = mResults.at( pRow ).count()
         index = createIndex( pRow, 0, result )

        beginInsertRows( index, count, count +results.count() -1 )
        mResults[ pRow ] << results
        endInsertRows()

        dataChanged.emit( index, index )



def thread_resultsHandled(self, fileName, results ):
    pResult = mParents.value( fileName )

    Q_ASSERT( pResult )

     pRow = mParentsList.indexOf( pResult )
    children = mResults[ pRow ]
     pIndex = createIndex( pRow, 0, pResult )

    # remove root parent children
    foreach ( SearchResultsModel.Result* result, results )
         index = children.indexOf( result )
        beginRemoveRows( pIndex, index, index )
        delete children.takeAt( index )
        endRemoveRows()


    # remove root parent
    if  children.isEmpty() :
        beginRemoveRows( QModelIndex(), pRow, pRow )
        mResults.removeAt( pRow )
        mParentsList.removeAt( pRow )
        delete mParents.take( fileName )
        mRowCount--
        endRemoveRows()

    else:
        pResult.checkState = Qt.Unchecked
        dataChanged.emit( pIndex, pIndex )


