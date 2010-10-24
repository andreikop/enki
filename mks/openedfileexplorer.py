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
        
        self.mSortDocumentsTimer.timeout.connect(self.sortDocuments_timeout)
        mks.monkeycore.workspace().documentOpened.connect(self.documentOpened)
        mks.monkeycore.workspace().documentModifiedChanged.connect(self.documentModifiedChanged)
        mks.monkeycore.workspace().documentClosed.connect(self.documentClosed)
        self.mDocuments = []
        
        self.mSortMode = self.Suffixes # FIXME
    
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
            if document.windowIcon().isNull():
                if document.isModified():
                    return mks.monkeystudio.getIcon( "file/save.png" )
                else:
                    return mks.monkeystudio.getIcon( "file/transparent.png" )
            else:
                return document.windowIcon()
        elif role == Qt.DisplayRole:
                return document.fileName()
        elif role == Qt.ToolTipRole:
            return document.toolTip()
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
        
        #if row > fromRow:
        #    row -= 1
        
        newDocuments.insert(row, item)
        
        self.rebuildMapping( self.mDocuments, newDocuments )
        
        if  self.mSortMode != _OpenedFileModel.Custom :
            self.setSortMode( _OpenedFileModel.Custom )
        
        QObject.parent(self).tvFiles.setCurrentIndex(self.documentIndex(item))
        
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
            self.sortDocuments()

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
        self.mSortDocumentsTimer.stop()
        
        newDocuments = copy.copy(self.mDocuments)
        
        if self.mSortMode == self.OpeningOrder:
            newDocuments.sort(lambda a, b: cmp(self.mDocuments.index(a), self.mDocuments.index(b)))
        elif self.mSortMode == self.FileName:
            newDocuments.sort(lambda a, b: cmp(a.fileName(), b.fileName()))
        elif self.mSortMode == self.URL:
            newDocuments.sort(lambda a, b: cmp(a.filePath(), b.filePath()))
        elif self.mSortMode == self.Suffixes:
            def sorter(a, b):
                aInfos = QFileInfo ( a.filePath() )
                aBaseName = aInfos.baseName().toLower()
                aSuffix = aInfos.completeSuffix().toLower()
                bInfos = QFileInfo ( b.filePath() )
                bBaseName = bInfos.baseName().toLower()
                bSuffix = bInfos.completeSuffix().toLower()
                return cmp(aSuffix, bSuffix)

            newDocuments.sort(sorter)
        elif self.mSortMode == self.Custom:
            pass
        else:
            assert(0)
        self.rebuildMapping( self.mDocuments, newDocuments )
                    # scroll the view
        QObject.parent(self).tvFiles.scrollTo( QObject.parent(self).tvFiles.selectionModel().selectedIndexes()[0] )

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
        self.mDocuments.remove( document )
        self.endRemoveRows()

"""TODO
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
        '''
        tb = qobject_cast<QToolButton*>( titleBar().addAction( aSortMenu, 0 ) )
        tb.setPopupMode( QToolButton.InstantPopup )
        titleBar().addSeparator( 1 )
        '''
        self.tvFiles.viewport().setAcceptDrops( True )

        mks.monkeycore.workspace().documentChanged.connect(self.documentChanged)
        """
        mks.monkeycore.workspace().currentDocumentChanged.connect(self.currentDocumentChanged)
        self.tvFiles.selectionModel().selectionChanged.connect(self.selectionModel_selectionChanged)
        """TODO
        self.aComboBox.currentIndexChanged.connect(self.syncViewsIndex)

    def comboBoxAction(self):
        return self.aComboBox
"""
    def sortTriggered(self, action ):
        mode = action.data().toString()
        self.mModel.setSortMode( mode )
    
    def currentDocumentChanged(self, document ):
        if document is not None:
            index = self.mModel.documentIndex( document )
            
            vLocked = self.tvFiles.selectionModel().blockSignals( True )
            self.tvFiles.setCurrentIndex( index )
            self.tvFiles.selectionModel().blockSignals( vLocked )
            # scroll the view
            self.tvFiles.scrollTo( index )
        pass
    
    def selectionModel_selectionChanged(self, selected, deselected ):
        if not selected.indexes():  # empty list, last file closed
            return
        
        index = selected.indexes()[0]
        # backup/restore current focused widget as setting active mdi window will steal it
        focusWidget = self.window().focusWidget()

        # set current document
        document = self.mModel.mDocuments[index.row()]
        mks.monkeycore.workspace().setCurrentDocument( document )
        
        # restore focus widget
        if  focusWidget :
            focusWidget.setFocus()
    
    def on_tvFiles_customContextMenuRequested(self, pos ):
        menu = QMenu()
        
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ) )
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ) )
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/aReload" ) )
        menu.addSeparator()
        
        # sort menu
        sortMenu = QMenu( self )
        group = QActionGroup( sortMenu )

        group.addAction( self.tr( "Opening order" ) )
        group.addAction( self.tr( "File name" ) )
        group.addAction( self.tr( "URL" ) )
        group.addAction( self.tr( "Suffixes" ) )
        group.addAction( self.tr( "Custom" ) )
        group.triggered.connect(self.sortTriggered)
        sortMenu.addActions( group.actions() )
        
        for i, sortMode in enumerate(["OpeningOrder", "FileName", "URL", "Suffixes", "Custom"]):
            action = group.actions()[i]
            action.setData( sortMode )
            action.setCheckable( True )
            if sortMode == self.mModel.sortMode:
                action.setChecked( True )
        
        aSortMenu = QAction( self.tr( "Sorting" ), self )
        aSortMenu.setMenu( sortMenu )
        aSortMenu.setIcon( mks.monkeystudio.getIcon( "file/sort.png" ))
        aSortMenu.setToolTip( aSortMenu.text() )
        
        menu.addAction( sortMenu.menuAction() )
        menu.exec_( self.tvFiles.mapToGlobal( pos ) )
