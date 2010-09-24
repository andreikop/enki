#ifndef XUPFILTEREDPROJECTMODEL_H
#define XUPFILTEREDPROJECTMODEL_H

#include <objects/MonkeyExport.h>

#include "XUPProjectModel.h"
#include "XUPItem.h"

#include <QMap>

typedef QMap<XUPItem*, Mapping*> XUPItemMapping
typedef XUPItemMapping.const_iterator XUPItemMappingIterator

struct Q_MONKEY_EXPORT Mapping
    Mapping()
        mParent = 0


    QModelIndex mProxyIndex
    XUPItem* mParent
    QList<XUPItem*> mMappedChildren
    XUPItemMappingIterator mIterator

    XUPItem* findVariable(  QString& name )
        for item in mMappedChildren:
            if ( ( item.type() == XUPItem.Variable or XUPItem.DynamicFolder ) and
                    item.attribute( "name" ) == name )
                return item


        return 0


    XUPItem* findValue(  QString& content )
        for item in mMappedChildren:
            switch ( item.type() )
            case XUPItem.Value:
            case XUPItem.File:
            case XUPItem.Path:
                if  item.attribute( "content" ) == content :
                    return item

                break
            default:
                break


        return 0



class Q_MONKEY_EXPORT XUPFilteredProjectModel : public QAbstractItemModel
    Q_OBJECT

public:
    XUPFilteredProjectModel( parent = 0, sourceModel = 0 )
    virtual ~XUPFilteredProjectModel()

    # QAbstractItemModel reimplementation
    virtual QModelIndex index( int row, column, parent = QModelIndex() )
    virtual QModelIndex parent(  QModelIndex& index )
    virtual int rowCount(  parent = QModelIndex() )
    virtual int columnCount(  parent = QModelIndex() )
    virtual QVariant headerData( int section, orientation, role = Qt.DisplayRole )
    virtual QVariant data(  QModelIndex& index, role = Qt.DisplayRole )
    virtual Qt.ItemFlags flags(  QModelIndex& index )

    XUPItemMappingIterator indexToIterator(  QModelIndex& proxyIndex )
    XUPItem* mapToSource(  QModelIndex& proxyIndex )
    QModelIndex mapFromSource( XUPItem* sourceItem )

    void setSourceModel( XUPProjectModel* model )
    XUPProjectModel* sourceModel()

    XUPItemList getFilteredVariables(  XUPItem* root )
    XUPItemList getValues(  XUPItem* root )

    void populateVariable( XUPItem* variable )
    void populateProject( XUPProjectItem* item )

    void debug( XUPItem* root, mode = 0 )

protected:
    XUPProjectModel* mSourceModel
    mutable XUPItemMapping mItemsMapping

    XUPItemMappingIterator createMapping( XUPItem* item, parent = 0 )
    void removeMapping( XUPItem* item )
    void clearMapping()
    void recursiveRemoveItems( XUPItem* item )

protected slots:
    void internal_rowsInserted(  QModelIndex& parent, start, end )
    void internal_rowsAboutToBeRemoved(  QModelIndex& parent, start, end )
    void internal_dataChanged(  QModelIndex& topLeft, bottomRight )


#endif # XUPFILTEREDPROJECTMODEL_H
