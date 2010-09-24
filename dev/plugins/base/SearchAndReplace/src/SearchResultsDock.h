#ifndef SEARCHRESULTSDOCK_H
#define SEARCHRESULTSDOCK_H

#include <widgets/pDockWidget.h>

#include <QModelIndex>

class SearchThread;
class SearchResultsModel;
class QHBoxLayout;
class QTreeView;

class SearchResultsDock : public pDockWidget
{
	Q_OBJECT
	
public:
	SearchResultsDock( SearchThread* searchThread, QWidget* parent = 0 );
	
	SearchResultsModel* model() const;

protected:
	SearchThread* mSearchThread;
	QHBoxLayout* mLayout;
	SearchResultsModel* mModel;
	QTreeView* mView;

protected slots:
	void view_activated( const QModelIndex& index );
};

#endif // SEARCHRESULTSDOCK_H
