#ifndef XUPPROJECTMODELPROXY_H
#define XUPPROJECTMODELPROXY_H

#include <QSortFilterProxyModel>

class XUPProjectModel;

class XUPProjectModelProxy : public QSortFilterProxyModel
{
public:
	XUPProjectModelProxy( QObject* parent = 0, bool showDisabled = true );
	
	virtual void setSourceModel( QAbstractItemModel* sourceModel );
	virtual Qt::ItemFlags flags( const QModelIndex& index ) const;
	
	bool isShowDisabled() const;

public slots:
	void setShowDisabled( bool showDisabled );

protected:
	XUPProjectModel* mSourceModel;
	bool mShowDisabled;
	
	virtual bool filterAcceptsRow( int sourceRow, const QModelIndex& sourceParent ) const;
};

#endif // XUPPROJECTMODELPROXY_H
