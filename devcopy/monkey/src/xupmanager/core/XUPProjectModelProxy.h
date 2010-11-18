#ifndef XUPPROJECTMODELPROXY_H
#define XUPPROJECTMODELPROXY_H

#include <QSortFilterProxyModel>

class XUPProjectModel

class XUPProjectModelProxy : public QSortFilterProxyModel
public:
    XUPProjectModelProxy( parent = 0, showDisabled = True )
    
    virtual void setSourceModel( QAbstractItemModel* sourceModel )
    virtual Qt.ItemFlags flags(  QModelIndex& index )
    
    bool isShowDisabled()

public slots:
    void setShowDisabled( bool showDisabled )

protected:
    XUPProjectModel* mSourceModel
    bool mShowDisabled
    
    virtual bool filterAcceptsRow( int sourceRow, sourceParent )


#endif # XUPPROJECTMODELPROXY_H
