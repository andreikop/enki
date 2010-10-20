"""Opened File Explorer is list widget with list of opened files.
It implements switching current file, files sorting
"""
import os.path
import copy

from PyQt4 import uic

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import PyQt4.fresh

import mks.monkeycore

'''TODO rewrite with lambda functions. Would be much better

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
'''

class _OpenedFileModel(QAbstractItemModel):
    """Model, herited from QAbstractItemModel, used for show list of opened files
    in the tree view.
    It switches current file, does file sorting
    """
    
    OpeningOrder = "OpeningOrder"
    FileName = "FileName"
    URL = "URL"
    Suffixes = "Suffixes"
    Custom = "Custom"
    
    def __init__(self, parentObject):
        QAbstractItemModel.__init__(self, parentObject )
        self.mSortMode = _OpenedFileModel.OpeningOrder
        self.mSortDocumentsTimer = QTimer( self )
        self.mSortDocumentsTimeout = 150
        self.mTransparentIcon = mks.monkeystudio.getIcon( "transparent.png" )
        self.mModifiedIcon = mks.monkeystudio.getIcon( "save.png" )
        
        self.mSortDocumentsTimer.timeout.connect(self.sortDocuments_timeout)
        mks.monkeycore.workspace().documentOpened.connect(self.documentOpened)
        mks.monkeycore.workspace().documentModifiedChanged.connect(self.documentModifiedChanged)
        mks.monkeycore.workspace().documentClosed.connect(self.documentClosed)
        self.mDocuments = []
    
    def columnCount(self, parent ):
        return 1

    def rowCount(self, parent ):
        if parent.isValid():
            return 0
        else:
            return len(self.mDocuments)
    
    def hasChildren(self, parent ):
        if parent.isValid():
           return False
        else:
            return (len(self.mDocuments) > 0)

    def headerData(self, section, orientation, role ):
        if  section == 0 and \
            orientation == Qt.Horizontal and \
            role == Qt.DecorationRole:
                return self.tr( "Opened Files" )
        else:
            return QVariant()

    def data(self, index, role ):
        if  not index.isValid() :
            return QVariant()
        
        document = self.document( index )
        assert(document)
        
        if role == Qt.DecorationRole:
            icon = document.windowIcon()
            """ TODO
            if  not self.mDocumentsIcons.value( document ).isNull() :
                icon = self.mDocumentsIcons[ document ]
            elif  document.isModified() :
                icon = self.mModifiedIcon
            """
            
            if  icon.isNull() :
                icon = self.mTransparentIcon
            return icon
        elif role == Qt.DisplayRole:
                return document.filePath()
        elif role == Qt.ToolTipRole:
            """TODO
            customToolTip = self.mDocumentsToolTips.value( document )
            toolTip = document.filePath()
            return customToolTip.isEmpty() ? toolTip : customToolTip
            break
            """
            return document.filePath()
        else:
            return QVariant()
    
    def flags(self, index ):
        if  index.isValid() :
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
    
    def index(self, row, column, parent ):
        if  parent.isValid() or column > 0 or column < 0 or row < 0 or row >= len(self.mDocuments) :
            return QModelIndex()

        return self.createIndex( row, column, self.mDocuments[row] )
    
    def parent(self, index ):
        return QModelIndex()
    
    def mimeTypes(self):
        return ["application/x-modelindexrow"]

    def mimeData(self, indexes ):
        if len(indexes) != 1:
            return 0
        
        data = QMimeData()
        data.setData( self.mimeTypes()[0], QByteArray.number( indexes[0].row() ) )
        return data

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(self, data, action, row, column, parent ):
        if  parent.isValid() or \
            ( row == -1 and column == -1 ) or \
            action != Qt.MoveAction or \
            not data or \
            not data.hasFormat( self.mimeTypes()[0] ) :
                return False
        
        fromRow = data.data( self.mimeTypes()[0] ).toInt()[0]
        
        if  row >= len(self.mDocuments):
            row-= 1

        elif  fromRow < row :
            row-= 1

        newDocuments = copy.copy(self.mDocuments)
        
        item = newDocuments.pop(fromRow)
        
        if row > fromRow:
            row -= 1
        
        newDocuments.insert(row, item)
        
        self.rebuildMapping( self.mDocuments, newDocuments )
        
        if  self.mSortMode != _OpenedFileModel.Custom :
            self.setSortMode( _OpenedFileModel.Custom )

        return True
    
    def document(self, index ):
        if  not index.isValid() :
            return 0

        return index.internalPointer()
    
    def documentIndex(self, document ):
        row = self.mDocuments.index( document )
        
        if  row != -1 :
            return self.createIndex( row, 0, document )

        return QModelIndex()
    
    def sortMode(self):
        return self.mSortMode

    def setSortMode(self, mode ):
        if  self.mSortMode != mode :
            self.mSortMode = mode
            self.sortModeChanged.emit( self.mSortMode )
            self.sortDocuments()

    def setDocumentIcon(self, document, icon ):
        self.mDocumentsIcons[ document ] = icon
        index = self.index( document )
        dataChanged.emit( index, index )

    def setDocumentToolTip(self, document, toolTip ):
        self.mDocumentsToolTips[ document ] = toolTip
        index = self.index( document )
        dataChanged.emit( index, index )


    def sortDocuments(self):
        self.mSortDocumentsTimer.start( self.mSortDocumentsTimeout )

    def insertDocument(self, document, index ):
        assert( not document in self.mDocuments )
        self.beginInsertRows( QModelIndex(), index, index )
        self.mDocuments.insert( index, document )
        self.endInsertRows()
        self.sortDocuments()

    def rebuildMapping(self, oldList, newList ):
        self.layoutAboutToBeChanged.emit()
        pOldIndexes = self.persistentIndexList()
        pIndexes = []
        documentsMapping = {}
        mapping = {}
        
        # build old mapping
        for index in pOldIndexes:
            row = index.row()
            documentsMapping[ row ] = oldList[row]
            mapping[ row ] = row

        self.mDocuments = newList
        
        # build mapping
        for pIndex in pOldIndexes:
            row = pIndex.row()
            document = documentsMapping[ row ]
            index = self.mDocuments.index( document )
            mapping[ row ] = index
        
        for pIindex in pOldIndexes:
            row = pIndex.row()
            index = mapping[ row ]
            
            if  pIndex.isValid():
                pIndexes.append(self.createIndex( index, pIndex.column(), self.mDocuments[index] ))
            else:
                pIndexes.append(QModelIndex())
        
        self.changePersistentIndexList( pOldIndexes, pIndexes )
        self.layoutChanged.emit()


    def sortDocuments_timeout(self):
        """TODO
        self.mSortDocumentsTimer.stop()
        
        newDocuments = copy.copy(self.mDocuments)
        
        switch ( self.mSortMode )
            case _OpenedFileModel.OpeningOrder:
                OpeningOrderSorter functor( mWorkspace.documents() )
                qSort( newDocuments.begin(), newDocuments.end(), functor )
                break

            case _OpenedFileModel.FileName:
                FileNameSorter functor
                qSort( newDocuments.begin(), newDocuments.end(), functor )
                break

            case _OpenedFileModel.URL:
                URLSorter functor
                qSort( newDocuments.begin(), newDocuments.end(), functor )
                break

            case _OpenedFileModel.Suffixes:
                SuffixesSorter functor
                qSort( newDocuments.begin(), newDocuments.end(), functor )
                break

            case _OpenedFileModel.Custom:
                break

        
        self.rebuildMapping( self.mDocuments, newDocuments )
        documentsSorted.emit()
        """
        pass
    
    def documentOpened(self, document ):
        if document in self.mDocuments:
           self.sortDocuments()
        else:
            if document is None or document in self.mDocuments:
                return
            
            index = len(self.mDocuments)
            self.insertDocument( document, index )
    
    def documentModifiedChanged(self, document, modified ):
        index = self.documentIndex( document )
        self.dataChanged.emit( index, index )


    def documentClosed(self, document ):
        index = self.mDocuments.index( document )
        
        if  index == -1 :
            return

        self.beginRemoveRows( QModelIndex(), index, index )
        self.mDocuments.removeOne( document )
        self.mDocumentsIcons.remove( document )
        self.mDocumentsToolTips.remove( document )
        self.endRemoveRows()
        self.sortDocuments()

"""
class pOpenedFileAction(QWidgetAction):
    
    def __init__( self, parent, model ):
        QWidgetAction.__init__(self, parent )
        
        self.mOpenedFileExplorer = parent
        self.mModel = model
        self.mCombos = []

    def syncViewIndex( self, index ):
        for combo in self.mCombos:
            aSMLocked = combo.view().selectionModel().blockSignals( True )
            aLocked = combo.blockSignals( True )
            combo.setCurrentIndex( index.row() )
            combo.view().selectionModel().blockSignals( aSMLocked )
            combo.blockSignals( aLocked )

    def createWidget( self, parent ):
        combo = self.mCombos.value( parent )

        if  combo :
            #Q_ASSERT( 0 )
            return combo

        combo = QComboBox( parent )
        combo.setMaxVisibleItems( 25 )
        combo.setSizeAdjustPolicy( QComboBox.AdjustToContents )
        combo.setAttribute( Qt.WA_MacSmallSize )
        combo.setModel( self.mModel )

        combo.activated.connect(self.comboBox_activated)
        combo.destroyed.connect(self.object_destroyed)
        
        self.mCombos[ parent ] = combo

        return combo

    def comboBox_activated( row ):
        index = self.mModel.index( row, 0 )
        self.currentIndexChanged.emit( index )
    
    def object_destroyed( object ):
        self.mCombos.remove( (object).parentWidget() )

    currentIndexChanged = pyqtSignal()
"""

class OpenedFileExplorer(PyQt4.fresh.pDockWidget):
    """Opened File Explorer is list widget with list of opened files.
    It implements switching current file, files sorting
    """
    def __init__(self, parentWidget):
        PyQt4.fresh.pDockWidget.__init__(self, parentWidget)
        
        self.mModel = _OpenedFileModel(self)
        """TODO
        self.aComboBox = pOpenedFileAction( self, self.mModel )
        """
        uic.loadUi('mks/pOpenedFileExplorer.ui', self )
        self.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.tvFiles.setModel( self.mModel )
        self.tvFiles.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.tvFiles.setAttribute( Qt.WA_MacSmallSize )
        
        """TODO
        # sort menu
        self.mSortMenu = QMenu( self )
        group = QActionGroup( self.mSortMenu )

        group.addAction( self.tr( "Opening order" ) )
        group.addAction( self.tr( "File name" ) )
        group.addAction( self.tr( "URL" ) )
        group.addAction( self.tr( "Suffixes" ) )
        group.addAction( self.tr( "Custom" ) )
        self.mSortMenu.addActions( group.actions() )

        for  i in range(_OpenedFileModel.OpeningOrder, _OpenedFileModel.Custom +1):
            action = group.actions()[i]
            action.setData( i )
            action.setCheckable( True )

            if  i == _OpenedFileModel.OpeningOrder :
                action.setChecked( True )

        aSortMenu = QAction( tr( "Sorting" ), self )
        aSortMenu.setMenu( self.mSortMenu )
        aSortMenu.setIcon( mks.monkeystudio.iconsPath() + "file/sort.png" ) )
        aSortMenu.setToolTip( aSortMenu.text() )
        '''
        tb = qobject_cast<QToolButton*>( titleBar().addAction( aSortMenu, 0 ) )
        tb.setPopupMode( QToolButton.InstantPopup )
        titleBar().addSeparator( 1 )
        '''
        self.tvFiles.viewport().setAcceptDrops( True )

        group.triggered.connect(self.sortTriggered)
        mks.monkeycore.workspace().documentChanged.connect(self.documentChanged)
        """
        mks.monkeycore.workspace().currentDocumentChanged.connect(self.currentDocumentChanged)
        """TODO
        self.mModel.sortModeChanged.connect(self.sortModeChanged)
        self.mModel.documentsSorted.connect(self.documentsSorted)
        """
        self.tvFiles.selectionModel().selectionChanged.connect(self.selectionModel_selectionChanged)
        """TODO
        self.aComboBox.currentIndexChanged.connect(self.syncViewsIndex)

    def model(self):
        return self.mModel

    def comboBoxAction(self):
        return self.aComboBox

    def sortMode(self):
        return self.mModel.sortMode()

    def setSortMode(self, mode ):
        self.mModel.setSortMode( mode )
"""
    def syncViewsIndex(self, index, syncOnly=True):
        """TODO
        # sync action combobox
        self.aComboBox.syncViewIndex( index )

        # sync listview
        """
        vLocked = self.tvFiles.blockSignals( True )
        self.tvFiles.setCurrentIndex( index )
        self.tvFiles.blockSignals( vLocked )

        # scroll the view
        self.tvFiles.scrollTo( index )
    
        if  syncOnly :
            return

        # backup/restore current focused widget as setting active mdi window will steal it
        focusWidget = self.window().focusWidget()

        # set current document
        document = mks.monkeycore.workspace().openedDocuments()[index.row()]
        mks.monkeycore.workspace().setCurrentDocument( document )
        
        # restore focus widget
        if  focusWidget :
            focusWidget.setFocus()
    """TODO
    def sortTriggered(self, action ):
        mode = action.data().toInt()
        setSortMode( mode )

    def documentChanged(self, document ):
        pass
"""
    def currentDocumentChanged(self, document ):
        if document is not None:
            index = self.mModel.documentIndex( document )
            self.syncViewsIndex( index, True )
        pass
    
    """TODO
        def sortModeChanged(self, mode ):
            for action in self.mSortMenu.actions():
                if  action.data().toInt() == mode :
                    if  not action.isChecked() :
                        action.setChecked( True )
        
                    return
        
        def documentsSorted(self):
            # scroll the view
            self.tvFiles.scrollTo( self.tvFiles.selectionModel().selectedIndexes().value( 0 ) )
    """
    
    def selectionModel_selectionChanged(self, selected, deselected ):
        index = selected.indexes()[0]
        self.syncViewsIndex( index, False )

"""TODO
    def on_tvFiles_customContextMenuRequested(self, pos ):
        menu = QMenu()
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ) )
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ) )
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/aReload" ) )
        menu.addSeparator()
        menu.addAction( self.mSortMenu.menuAction() )
        menu.exec_( self.tvFiles.mapToGlobal( pos ) )
"""