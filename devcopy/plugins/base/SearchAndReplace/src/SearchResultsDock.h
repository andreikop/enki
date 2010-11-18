#ifndef SEARCHRESULTSDOCK_H
#define SEARCHRESULTSDOCK_H

#include <widgets/pDockWidget.h>

#include <QModelIndex>

class SearchThread
class SearchResultsModel
class QHBoxLayout
class QTreeView

class SearchResultsDock : public pDockWidget
    Q_OBJECT
    
public:
    SearchResultsDock( SearchThread* searchThread, parent = 0 )
    
    SearchResultsModel* model()

protected:
    SearchThread* mSearchThread
    QHBoxLayout* mLayout
    SearchResultsModel* mModel
    QTreeView* mView

protected slots:
    void view_activated(  QModelIndex& index )


#endif # SEARCHRESULTSDOCK_H
