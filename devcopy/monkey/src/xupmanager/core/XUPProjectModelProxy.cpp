#include "XUPProjectModelProxy.h"
#include "XUPProjectModel.h"
#include "XUPItem.h"

XUPProjectModelProxy::XUPProjectModelProxy( QObject* parent, bool showDisabled )
    : QSortFilterProxyModel( parent )
{
    mShowDisabled = showDisabled;
    mSourceModel = 0;
}

void XUPProjectModelProxy::setSourceModel( QAbstractItemModel* sourceModel )
{
    mSourceModel = qobject_cast<XUPProjectModel*>( sourceModel );
    QSortFilterProxyModel::setSourceModel( mSourceModel );
}

Qt::ItemFlags XUPProjectModelProxy::flags( const QModelIndex& index ) const
{
    if ( !mSourceModel || !index.isValid() )
    {
        return 0;
    }
    
    QModelIndex idx = mapToSource( index );
    XUPItem* item = mSourceModel->itemFromIndex( idx );
    
    bool enabled = false;
    
    if ( item->type() == XUPItem::Project || item->type() == XUPItem::Scope )
    {
        enabled = true;
    }
    else if ( item->type() == XUPItem::Function && item->attribute( "name" ).toLower() != "include" )
    {
        enabled = true;
    }
    
    return enabled ? Qt::ItemIsEnabled | Qt::ItemIsSelectable : Qt::ItemFlags();
}

bool XUPProjectModelProxy::filterAcceptsRow( int sourceRow, const QModelIndex& sourceParent ) const
{
    const QModelIndex sourceIndex = mSourceModel->index( sourceRow, 0, sourceParent );
    XUPItem* item = mSourceModel->itemFromIndex( sourceIndex );
    
    bool isEnabled = false;
    
    if ( item->type() == XUPItem::Project || item->type() == XUPItem::Scope )
    {
        isEnabled = true;
    }
    else if ( item->type() == XUPItem::Function && item->attribute( "name" ).toLower() != "include" )
    {
        isEnabled = true;
    }
    
    return isEnabled ? true : mShowDisabled;
}

bool XUPProjectModelProxy::isShowDisabled() const
{
    return mShowDisabled;
}

void XUPProjectModelProxy::setShowDisabled( bool showDisabled )
{
    if ( mShowDisabled != showDisabled )
    {
        mShowDisabled = showDisabled;
        reset();
    }
}
