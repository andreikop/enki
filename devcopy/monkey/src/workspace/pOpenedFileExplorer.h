#ifndef POPENEDFILEEXPLORER_H
#define POPENEDFILEEXPLORER_H

#include <objects/MonkeyExport.h>

#include "ui_pOpenedFileExplorer.h"
#include "pOpenedFileModel.h"

class pWorkspace
class pAbstractChild
class pOpenedFileAction

class Q_MONKEY_EXPORT pOpenedFileExplorer : public pDockWidget, Ui.pOpenedFileExplorer
    Q_OBJECT
    friend class pOpenedFileAction

public:
    pOpenedFileExplorer( pWorkspace* workspace )
    
    pOpenedFileModel* model()
    QAction* comboBoxAction()
    
    pOpenedFileModel.SortMode sortMode()
    void setSortMode( pOpenedFileModel.SortMode mode )

protected:
    pWorkspace* mWorkspace
    pOpenedFileModel* mModel
    QMenu* mSortMenu
    pOpenedFileAction* aComboBox

protected slots:
    void syncViewsIndex(  QModelIndex& index, syncOnly = False )
    void sortTriggered( QAction* action )
    void documentChanged( pAbstractChild* document )
    void currentDocumentChanged( pAbstractChild* document )
    void sortModeChanged( pOpenedFileModel.SortMode mode )
    void documentsSorted()
    void selectionModel_selectionChanged(  QItemSelection& selected, deselected )
    void on_tvFiles_customContextMenuRequested(  QPoint& pos )


#endif # POPENEDFILEEXPLORER_H
