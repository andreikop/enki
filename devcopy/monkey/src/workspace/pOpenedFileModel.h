#ifndef POPENEDFILEMODEL_H
#define POPENEDFILEMODEL_H

#include <objects/MonkeyExport.h>

#include <QAbstractItemModel>
#include <QIcon>

class pWorkspace
class pAbstractChild

class Q_MONKEY_EXPORT pOpenedFileModel : public QAbstractItemModel
    Q_OBJECT
    
public:
    enum SortMode
        OpeningOrder,
        FileName,
        URL,
        Suffixes,
        Custom

    
    pOpenedFileModel( pWorkspace* workspace )
    virtual ~pOpenedFileModel()
    
    virtual int columnCount(  parent = QModelIndex() )
    virtual int rowCount(  parent = QModelIndex() )
    virtual bool hasChildren(  parent = QModelIndex() )
    virtual QVariant headerData( int section, orientation, role = Qt.DisplayRole )
    virtual QVariant data(  QModelIndex& index, role = Qt.DisplayRole )
    virtual Qt.ItemFlags flags(  QModelIndex& index )
    virtual QModelIndex index( int row, column, parent = QModelIndex() )
    virtual QModelIndex parent(  QModelIndex& index )
    virtual QStringList mimeTypes()
    virtual QMimeData* mimeData(  QModelIndexList& indexes )
    virtual bool dropMimeData(  QMimeData* data, action, row, column, parent )
    virtual Qt.DropActions supportedDropActions()
    
    pAbstractChild* document(  QModelIndex& index )
    QModelIndex index( pAbstractChild* document )
    
    pOpenedFileModel.SortMode sortMode()
    void setSortMode( pOpenedFileModel.SortMode mode )
    
    void setDocumentIcon( pAbstractChild* document, icon )
    void setDocumentToolTip( pAbstractChild* document, toolTip )

protected:
    pWorkspace* mWorkspace
    pOpenedFileModel.SortMode mSortMode
    QTimer* mSortDocumentsTimer
    int mSortDocumentsTimeout
    QList<pAbstractChild*> mDocuments
    QMap<pAbstractChild*, mDocumentsIcons
    QMap<pAbstractChild*, mDocumentsToolTips
    QIcon mTransparentIcon
    QIcon mModifiedIcon
    
    void rebuildMapping(  QList<pAbstractChild*>& oldList, newList )
    void sortDocuments()
    void insertDocument( pAbstractChild* document, index )

protected slots:
    void sortDocuments_timeout()
    void documentOpened( pAbstractChild* document )
    void documentModifiedChanged( pAbstractChild* document, modified )
    void documentClosed( pAbstractChild* document )

signals:
    void sortModeChanged( pOpenedFileModel.SortMode mode )
    void documentsSorted()


#endif # POPENEDFILEMODEL_H
