#include "XUPProjectModelProxy.h"
#include "XUPProjectModel.h"
#include "XUPItem.h"

XUPProjectModelProxy.XUPProjectModelProxy( QObject* parent, showDisabled )
        : QSortFilterProxyModel( parent )
    mShowDisabled = showDisabled
    mSourceModel = 0


def setSourceModel(self, sourceModel ):
    mSourceModel = qobject_cast<XUPProjectModel*>( sourceModel )
    QSortFilterProxyModel.setSourceModel( mSourceModel )


def flags(self, index ):
    if  not mSourceModel or not index.isValid() :
        return 0


    idx = mapToSource( index )
    item = mSourceModel.itemFromIndex( idx )

    enabled = False

    if  item.type() == XUPItem.Project or item.type() == XUPItem.Scope :
        enabled = True

    elif  item.type() == XUPItem.Function and item.attribute( "name" ).toLower() != "include" :
        enabled = True


    return enabled ? Qt.ItemIsEnabled | Qt.ItemIsSelectable : Qt.ItemFlags()


def filterAcceptsRow(self, sourceRow, sourceParent ):
     sourceIndex = mSourceModel.index( sourceRow, 0, sourceParent )
    item = mSourceModel.itemFromIndex( sourceIndex )

    isEnabled = False

    if  item.type() == XUPItem.Project or item.type() == XUPItem.Scope :
        isEnabled = True

    elif  item.type() == XUPItem.Function and item.attribute( "name" ).toLower() != "include" :
        isEnabled = True


    return isEnabled ? True : mShowDisabled


def isShowDisabled(self):
    return mShowDisabled


def setShowDisabled(self, showDisabled ):
    if  mShowDisabled != showDisabled :
        mShowDisabled = showDisabled
        reset()


