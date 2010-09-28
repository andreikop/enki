#ifndef POPENEDFILEEXPLORER_H
#define POPENEDFILEEXPLORER_H

#include <objects/MonkeyExport.h>

#include "ui_pOpenedFileExplorer.h"
#include "pOpenedFileModel.h"

class pWorkspace;
class pAbstractChild;
class pOpenedFileAction;

class Q_MONKEY_EXPORT pOpenedFileExplorer : public pDockWidget, public Ui::pOpenedFileExplorer
{
    Q_OBJECT
    friend class pOpenedFileAction;

public:
    pOpenedFileExplorer( pWorkspace* workspace );
    
    pOpenedFileModel* model() const;
    QAction* comboBoxAction() const;
    
    pOpenedFileModel::SortMode sortMode() const;
    void setSortMode( pOpenedFileModel::SortMode mode );

protected:
    pWorkspace* mWorkspace;
    pOpenedFileModel* mModel;
    QMenu* mSortMenu;
    pOpenedFileAction* aComboBox;

protected slots:
    void syncViewsIndex( const QModelIndex& index, bool syncOnly = false );
    void sortTriggered( QAction* action );
    void documentChanged( pAbstractChild* document );
    void currentDocumentChanged( pAbstractChild* document );
    void sortModeChanged( pOpenedFileModel::SortMode mode );
    void documentsSorted();
    void selectionModel_selectionChanged( const QItemSelection& selected, const QItemSelection& deselected );
    void on_tvFiles_customContextMenuRequested( const QPoint& pos );
};

#endif // POPENEDFILEEXPLORER_H
