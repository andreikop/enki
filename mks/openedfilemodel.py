from PyQt4.QtCore import *

import mks.iconmanager

"""TODO rewrite with lambda functions. Would be much better
struct OpeningOrderSorter
    OpeningOrderSorter(  QList<pAbstractChild*>& documents )
        originalDocuments = documents


    bool operator()( pAbstractChild* left, right )
        return originalDocuments.indexOf( left ) < originalDocuments.indexOf( right )


    QList<pAbstractChild*> originalDocuments


struct FileNameSorter
    bool operator()( pAbstractChild* left, right )
        return left.fileName().toLower() < right.fileName().toLower()



struct URLSorter
    bool operator()( pAbstractChild* left, right )
        return left.filePath().toLower() < right.filePath().toLower()



struct SuffixesSorter
    bool operator()( pAbstractChild* left, right )
         QFileInfo leftInfos( left.filePath() )
         leftBaseName = leftInfos.baseName().toLower()
         leftSuffix = leftInfos.completeSuffix().toLower()
         QFileInfo rightInfos( right.filePath() )
         rightBaseName = rightInfos.baseName().toLower()
         rightSuffix = rightInfos.completeSuffix().toLower()

        if  leftSuffix == rightSuffix :
            return leftBaseName < rightBaseName


        return leftSuffix < rightSuffix
"""

class pOpenedFileModel(QAbstractItemModel):

    def __init__(self, workspace ):
        QAbstractItemModel.__init__(self, workspace )
        self.mWorkspace = workspace
        """TODO
        self.mSortMode = pOpenedFileModel.OpeningOrder
        """
        self.mSortDocumentsTimer = QTimer( self )
        self.mSortDocumentsTimeout = 150
        self.mTransparentIcon = mks.iconmanager.icon( "transparent.png" )
        self.mModifiedIcon = mks.iconmanager.icon( "save.png" )
        mSortDocumentsTimer = QTimer()
        mSortDocumentsTimer.timeout.connect(self.sortDocuments_timeout)
        workspace.documentOpened.connect(self.documentOpened)
        workspace.documentModifiedChanged.connect(self.documentModifiedChanged)
        workspace.documentClosed.connect(self.documentClosed)

    def columnCount(self, parent ):
        return 1
    
    def rowCount(self, parent ):
        if parent.isValid():
            return mDocuments.contains()
        else:
            return 0
        
    def hasChildren(self, parent ):
        if parent.isValid():
            return mDocuments.isEmpty()
        else:
            return False

    def headerData(self, section, orientation, role ):
        if  section == 0 and orientation == Qt.Horizontal :
            if role == Qt.DecorationRole:
                pass
            elif role == Qt.DisplayRole:
                return tr( "Opened Files" )
            else:
                pass
        
        return QVariant()

    def data(self, index, role ):
        if  not index.isValid() :
            return QVariant()

        document = self.document( index )

        if  not document :
            """TODO
            qWarning() << Q_FUNC_INFO << index << mDocuments
            """
            return QVariant()


        if role == Qt.DecorationRole:
            icon = document.windowIcon()

            if  not mDocumentsIcons.value( document ).isNull() :
                icon = mDocumentsIcons[ document ]
            elif  document.isModified() :
                icon = mModifiedIcon
            
            if  icon.isNull() :
                icon = mTransparentIcon
            return icon
        elif role == Qt.DisplayRole:
            return document.fileName()
        elif role == Qt.ToolTipRole:
            customToolTip = mDocumentsToolTips.value( document )
            toolTip = document.filePath()
            if customToolTip.isEmpty():
                return toolTip
            else:
                return customToolTip
        
        return QVariant()
    
    def flags(self, index ):
        if  index.isValid() :
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

    def index(self, row, column, parent ):
        if  parent.isValid() or column > 0 or column < 0 or row < 0 or row >= mDocuments.count() :
            return QModelIndex()

        return createIndex( row, column, mDocuments.at( row ) )

    def parent(self, index ):
        return QModelIndex()
    
    def mimeTypes(self):
        return QStringList( "application/x-modelindexrow" )

    def mimeData(self, indexes ):
        if  indexes.count() != 1 :
            return 0
        
        data = QMimeData()
        data.setData( mimeTypes().first(), QByteArray.number( indexes.first().row() ) )
        return data

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(self, data, action, row, column, parent ):
        if  parent.isValid() or ( row == -1 and column == -1 ) or action != Qt.MoveAction or not data or not data.hasFormat( mimeTypes().first() ) :
            return False

        fromRow = data.data( mimeTypes().first() ).toInt()

        if  row >= mDocuments.count() :
            row = row -1
        elif  fromRow < row :
            row = row - 1

        newDocuments = mDocuments

        newDocuments.move( fromRow, row )
        rebuildMapping( mDocuments, newDocuments )

        if  mSortMode != pOpenedFileModel.Custom :
            setSortMode( pOpenedFileModel.Custom )
        
        return True

    def document(self, index ):
        if  not index.isValid() :
            return 0

        return index.internalPointer()

    def index(self, document ):
        row = mDocuments.indexOf( document )

        if  row != -1 :
            return createIndex( row, 0, document )

        return QModelIndex()

    def sortMode(self):
        return mSortMode

    def setSortMode(self, mode ):
        if  mSortMode != mode :
            mSortMode = mode
            sortModeChanged.emit( mSortMode )
            sortDocuments()

    def setDocumentIcon(self, document, icon ):
        mDocumentsIcons[ document ] = icon
        index = self.index( document )
        dataChanged.emit( index, index )

    def setDocumentToolTip(self, document, toolTip ):
        mDocumentsToolTips[ document ] = toolTip
        index = self.index( document )
        dataChanged.emit( index, index )

    def sortDocuments(self):
        mSortDocumentsTimer.start( mSortDocumentsTimeout )

    def insertDocument(self, document, index ):
        Q_ASSERT( not mDocuments.contains( document ) )
        beginInsertRows( QModelIndex(), index, index )
        mDocuments.insert( index, document )
        endInsertRows()
        sortDocuments()
    
    def rebuildMapping(self, oldList, newList ):
        layoutAboutToBeChanged.emit()
        pOldIndexes = persistentIndexList()
        pIndexes = QModelIndexList ()
        
        documentsMapping = {}
        mapping = {}

        # build old mapping
        for i in range(pOldIndexes.count()): 
            index = pOldIndexes.at( i )
            row = index.row()
            documentsMapping[ row ] = oldList.at( row )
            mapping[ row ] = row
        
        mDocuments = newList

        # build mapping
        for i in range(pOldIndexes.count()):
            pIndex = pOldIndexes.at( i )
            row = pIndex.row()
            document = documentsMapping[ row ]
            index = mDocuments.indexOf( document )
            mapping[ row ] = index

        for i in range(pOldIndexes.count()):
            pIndex = pOldIndexes.at( i )
            row = pIndex.row()
            index = mapping[ row ]

            if  pOldIndexes.at( i ).isValid() :
                pIndexes.append(createIndex( index, pIndex.column(), mDocuments.at( index ) ))
            else:
                pIndexes.append(QModelIndex())
        
        changePersistentIndexList( pOldIndexes, pIndexes )
        layoutChanged.emit()

    def sortDocuments_timeout(self):
        """TODO
        mSortDocumentsTimer.stop()

        QList<pAbstractChild*> newDocuments = mDocuments

        switch ( mSortMode )
        case pOpenedFileModel.OpeningOrder:
            OpeningOrderSorter functor( mWorkspace.documents() )
            qSort( newDocuments.begin(), newDocuments.end(), functor )
            break

        case pOpenedFileModel.FileName:
            FileNameSorter functor
            qSort( newDocuments.begin(), newDocuments.end(), functor )
            break

        case pOpenedFileModel.URL:
            URLSorter functor
            qSort( newDocuments.begin(), newDocuments.end(), functor )
            break

        case pOpenedFileModel.Suffixes:
            SuffixesSorter functor
            qSort( newDocuments.begin(), newDocuments.end(), functor )
            break

        case pOpenedFileModel.Custom:
            break


        rebuildMapping( mDocuments, newDocuments )
        documentsSorted.emit()
        """
    
    def documentOpened(self, document ):
        if  mDocuments.contains( document ) :
            sortDocuments()
        else:
            if  not document or mDocuments.contains( document ) :
                return


            index = mDocuments.count()
            insertDocument( document, index )
    
    def documentModifiedChanged(self, document, modified ):
        index = self.index( document )
        dataChanged.emit( index, index )


    def documentClosed(self, document ):
        index = mDocuments.indexOf( document )

        if  index == -1 :
            return


        beginRemoveRows( QModelIndex(), index, index )
        mDocuments.removeOne( document )
        mDocumentsIcons.remove( document )
        mDocumentsToolTips.remove( document )
        endRemoveRows()
        sortDocuments()
