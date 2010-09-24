#include "pConsoleManagerStepModel.h"

#include <QDebug>

pConsoleManagerStepModel.pConsoleManagerStepModel( QObject* parent )
        : QAbstractItemModel( parent )
    mWarnings = 0
    mErrors = 0


pConsoleManagerStepModel.~pConsoleManagerStepModel()


def columnCount(self, parent ):
    return parent.isValid() ? 0 : 1


def data(self, index, role ):
    if  not index.isValid() :
        return QVariant()


     step = static_cast<pConsoleManagerStep*>( index.internalPointer() )
    return step.roleValue( role )


def index(self, row, column, parent ):
    if  parent.isValid() or row < 0 or row >= rowCount( parent ) or column < 0 or column >= columnCount( parent ) :
        return QModelIndex()


    return createIndex( row, column, &mSteps[ row ] )


def parent(self, index ):
    Q_UNUSED( index )
    return QModelIndex()


def rowCount(self, parent ):
    return parent.isValid() ? 0 : mSteps.count()


def hasChildren(self, parent ):
    return parent.isValid() ? False : not mSteps.isEmpty()


def index(self, step ):
     row = mSteps.indexOf( step )
    return row == -1 ? QModelIndex() : createIndex( row, 0, &mSteps[ row ] )


def step(self, index ):
    return mSteps.value( index.row() )


def nextWarning(self, fromIndex ):
     row = fromIndex.isValid() ? fromIndex.row() +1 : 0

    if  row >= rowCount() :
        return QModelIndex()


    for ( i = row; i < rowCount(); i++ )
        step = mSteps[ i ]

        if  step.type() == pConsoleManagerStep.Warning :
            return createIndex( i, 0, &step )



    return QModelIndex()


def nextError(self, fromIndex ):
     row = fromIndex.isValid() ? fromIndex.row() +1 : 0

    if  row >= rowCount() :
        return QModelIndex()


    for ( i = row; i < rowCount(); i++ )
        step = mSteps[ i ]

        if  step.type() == pConsoleManagerStep.Error :
            return createIndex( i, 0, &step )



    return QModelIndex()


def clear(self):
     count = rowCount()

    if  count == 0 :
        return


    beginRemoveRows( QModelIndex(), 0, count -1 )
    mSteps.clear()
    mWarnings = 0
    mErrors = 0
    endRemoveRows()


def appendStep(self, step ):
    # get last type
     type = mSteps.isEmpty() ? pConsoleManagerStep.Unknown : mSteps.last().type()
     count = rowCount()

    # update warnings/errors
    switch ( step.type() )
    case pConsoleManagerStep.Warning:
        mWarnings++
        break
    case pConsoleManagerStep.Error:
        mErrors++
        break
    default:
        break


    # add step
    switch ( type )
    case pConsoleManagerStep.Compiling:
        switch ( step.type() )
        case pConsoleManagerStep.Warning:
        case pConsoleManagerStep.Error:
            # add to last -1
            beginInsertRows( QModelIndex(), count -1, count -1 )
            mSteps.insert( count -1, step )
            endInsertRows()
            break

        # replace last
        default:
            mSteps[ count -1 ] = step
             index = self.index( step )
            dataChanged.emit( index, index )
            break



        break

    default:
        beginInsertRows( QModelIndex(), count, count )
        mSteps << step
        endInsertRows()
        break



    # if step is finish, set error, text if needed
    if  step.type() == pConsoleManagerStep.Finish :
        _step = &mSteps.last()

        if  step.roleValue( Qt.DisplayRole ).toString().isEmpty() :
            _step.setRoleValue( pConsoleManagerStep.TypeRole, mErrors ? pConsoleManagerStep.Bad : pConsoleManagerStep.Good )
            _step.setRoleValue( Qt.DisplayRole, tr( "Command terminated, error(s): %1, warning(s): %2" ).arg( mErrors ).arg( mWarnings ) )

        else # own text present
            _step.setRoleValue( pConsoleManagerStep.TypeRole, pConsoleManagerStep.Bad )


         index = self.index( *_step )
        dataChanged.emit( index, index )



def appendSteps(self, steps ):
    # do a hacky loop for now as self member is not yet used
    for step in steps:
        appendStep( step )


