"""
_openedfilesmodel --- Model and treeview manages list of opened files
=====================================================================

Module displays list of opened files, implements files sorting, drag-n-drop in the list, switches current file
Used only internally by Workspace
"""

import os.path
import copy

from PyQt4.QtCore import QAbstractItemModel, \
                         QFileInfo, \
                         QMimeData, \
                         QModelIndex, \
                         QObject, \
                         Qt, \
                         QVariant
from PyQt4.QtGui import QAction, QActionGroup, \
                        QIcon, \
                        QMenu

from PyQt4 import uic

import PyQt4.fresh

from mks.monkeycore import core, DATA_FILES_PATH



class _OpenedFileModel(QAbstractItemModel):
    """Model, herited from QAbstractItemModel, used for show list of opened files
    in the tree view (_OpenedFileExplorer)
    It switches current file, does file sorting
    """
    
    OpeningOrder = "OpeningOrder"
    FileName = "FileName"
    URL = "URL"
    Suffixes = "Suffixes"
    Custom = "Custom"
    
    def __init__(self, parentObject):
        QAbstractItemModel.__init__(self, parentObject )
        self.mSortMode = core.config()["Workspace"]["FileSortMode"]
        workspace = parentObject.parent()
        workspace.documentOpened.connect(self.documentOpened)
        workspace.documentClosed.connect(self.documentClosed)
    
    def columnCount(self, parent ):
        return 1

    def rowCount(self, parent ):
        if parent.isValid():
            return 0
        else:
            return len(core.workspace()._sortedDocuments)
    
    def hasChildren(self, parent ):
        if parent.isValid():
           return False
        else:
            return (len(core.workspace()._sortedDocuments) > 0)

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
        
        if   role == Qt.DecorationRole: return document.modelIcon()
        elif role == Qt.DisplayRole:    return document.fileName()
        elif role == Qt.ToolTipRole:    return document.modelToolTip()
        else:                           return QVariant()
    
    def flags(self, index ):
        if  index.isValid() :
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
    
    def index(self, row, column, parent ):
        if  parent.isValid() or column > 0 or column < 0 or row < 0 or row >= len(core.workspace()._sortedDocuments) :
            return QModelIndex()

        return self.createIndex( row, column, core.workspace()._sortedDocuments[row] )
    
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
        
        if  row >= len(core.workspace()._sortedDocuments):
            row-= 1

        elif  fromRow < row :
            row-= 1

        newDocuments = copy.copy(core.workspace()._sortedDocuments)
        
        item = newDocuments.pop(fromRow)
        
        #if row > fromRow:
        #    row -= 1
        
        newDocuments.insert(row, item)
        
        self.rebuildMapping( core.workspace()._sortedDocuments, newDocuments )
        
        if  self.mSortMode != _OpenedFileModel.Custom :
            self.setSortMode( _OpenedFileModel.Custom )
        
        QObject.parent(self).tvFiles.setCurrentIndex(self.documentIndex(item))
        
        return True
    
    def document(self, index ):
        if  not index.isValid() :
            return 0

        return index.internalPointer()
    
    def documentIndex(self, document ):
        row = core.workspace()._sortedDocuments.index( document )
        
        if  row != -1 :
            return self.createIndex( row, 0, document )

        return QModelIndex()
    
    def sortMode(self):
        return self.mSortMode

    def setSortMode(self, mode ):
        if  self.mSortMode != mode :
            self.mSortMode = mode
            if mode != self.Custom:
                core.config().reload()
                core.config()["Workspace"]["FileSortMode"] = mode
                core.config().flush()
            self.sortDocuments()

    def sortDocuments(self):
        newDocuments = copy.copy(core.workspace()._sortedDocuments)
        
        if self.mSortMode == self.OpeningOrder:
            newDocuments.sort(lambda a, b: cmp(core.workspace()._sortedDocuments.index(a), core.workspace()._sortedDocuments.index(b)))
        elif self.mSortMode == self.FileName:
            newDocuments.sort(lambda a, b: cmp(a.fileName(), b.fileName()))
        elif self.mSortMode == self.URL:
            newDocuments.sort(lambda a, b: cmp(a.filePath(), b.filePath()))
        elif self.mSortMode == self.Suffixes:
            def sorter(a, b):
                aInfos = QFileInfo ( a.filePath() )  # FIXME get rid of QFileInfo
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
        self.rebuildMapping( core.workspace()._sortedDocuments, newDocuments )
        # scroll the view
        selected = QObject.parent(self).tvFiles.selectionModel().selectedIndexes()
        if selected:
            QObject.parent(self).tvFiles.scrollTo( selected[0] )

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

        core.workspace()._sortedDocuments = newList
        
        # build mapping
        for pIndex in pOldIndexes:
            row = pIndex.row()
            document = documentsMapping[ row ]
            index = core.workspace()._sortedDocuments.index( document )
            mapping[ row ] = index
        
        for pIindex in pOldIndexes:
            row = pIndex.row()
            index = mapping[ row ]
            
            if  pIndex.isValid():
                pIndexes.append(self.createIndex( index, pIndex.column(), core.workspace()._sortedDocuments[index] ))
            else:
                pIndexes.append(QModelIndex())
        
        self.changePersistentIndexList( pOldIndexes, pIndexes )
        self.layoutChanged.emit()

    def documentOpened(self, document ):
        assert( not document in core.workspace()._sortedDocuments )
        core.workspace()._sortedDocuments.append( document )
        self.sortDocuments()
        document.modifiedChanged.connect(self._onDocumentDataChanged)
        document._documentDataChanged.connect(self._onDocumentDataChanged)

    def _onDocumentDataChanged(self):
        document = self.sender()
        index = self.documentIndex( document )
        self.dataChanged.emit( index, index )
    
    def documentClosed(self, document ):
        index = core.workspace()._sortedDocuments.index( document )
        
        if  index == -1 :
            return
        
        # scroll the view
        QObject.parent(self)._startModifyModel()
        self.beginRemoveRows( QModelIndex(), index, index )
        core.workspace()._sortedDocuments.remove( document )
        self.endRemoveRows()
        QObject.parent(self)._finishModifyModel()


class OpenedFileExplorer(PyQt4.fresh.pDockWidget):
    """Opened File Explorer is list widget with list of opened files.
    It implements switching current file, files sorting. Uses _OpenedFileModel internally.
    Class instance created by Workspace.
    """
    def __init__(self, workspace):
        PyQt4.fresh.pDockWidget.__init__(self, workspace)
        self.mModel = _OpenedFileModel(self)
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/pOpenedFileExplorer.ui'), self )
        self.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.tvFiles.setModel( self.mModel )
        self.tvFiles.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.tvFiles.setAttribute( Qt.WA_MacSmallSize )
        self.setFocusProxy(self.tvFiles)
        
        """TODO
        '''
        tb = qobject_cast<QToolButton*>( titleBar().addAction( aSortMenu, 0 ) )
        tb.setPopupMode( QToolButton.InstantPopup )
        titleBar().addSeparator( 1 )
        '''
        self.tvFiles.viewport().setAcceptDrops( True )

        core.workspace().documentChanged.connect(self.documentChanged)
        """
        workspace.currentDocumentChanged.connect(self.currentDocumentChanged)
        
        self.tvFiles.selectionModel().selectionChanged.connect(self.selectionModel_selectionChanged)  # disconnected by _startModifyModel()
        
        self.showAction().setShortcut("F2")
        workspace.parentWidget().addAction(self.showAction())
    
    def _startModifyModel(self):
        """Blocks signals from model while it modified by code
        """
        self.tvFiles.selectionModel().selectionChanged.disconnect(self.selectionModel_selectionChanged)
    
    def _finishModifyModel(self):
        """Unblocks signals from model
        """
        self.tvFiles.selectionModel().selectionChanged.connect(self.selectionModel_selectionChanged)
    
    def sortTriggered(self, action ):
        mode = action.data().toString()
        self.mModel.setSortMode( mode )
    
    def currentDocumentChanged(self, oldDocument, currentDocument ):
        if currentDocument is not None:
            index = self.mModel.documentIndex( currentDocument )
            
            self._startModifyModel()
            self.tvFiles.setCurrentIndex( index )
            # scroll the view
            self.tvFiles.scrollTo( index )
            self._finishModifyModel()
    
    def selectionModel_selectionChanged(self, selected, deselected ):
        if not selected.indexes():  # empty list, last file closed
            return
        
        index = selected.indexes()[0]
        # backup/restore current focused widget as setting active mdi window will steal it
        focusWidget = self.window().focusWidget()

        # set current document
        document = core.workspace()._sortedDocuments[index.row()]
        core.workspace().setCurrentDocument( document )
        
        # restore focus widget
        if  focusWidget :
            focusWidget.setFocus()
    
    def on_tvFiles_customContextMenuRequested(self, pos ):
        menu = QMenu()
        
        menu.addAction( core.menuBar().action( "mFile/mClose/aCurrent" ) )
        menu.addAction( core.menuBar().action( "mFile/mSave/aCurrent" ) )
        menu.addAction( core.menuBar().action( "mFile/mReload/aCurrent" ) )
        menu.addSeparator()
        
        # sort menu
        sortMenu = QMenu( self )
        group = QActionGroup( sortMenu )

        group.addAction( self.tr( "Opening order" ) )
        group.addAction( self.tr( "File name" ) )
        group.addAction( self.tr( "URL" ) )
        group.addAction( self.tr( "Suffixes" ) )
        group.triggered.connect(self.sortTriggered)
        sortMenu.addActions( group.actions() )
        
        for i, sortMode in enumerate(["OpeningOrder", "FileName", "URL", "Suffixes"]):
            action = group.actions()[i]
            action.setData( sortMode )
            action.setCheckable( True )
            if sortMode == self.mModel.sortMode():
                action.setChecked( True )
        
        aSortMenu = QAction( self.tr( "Sorting" ), self )
        aSortMenu.setMenu( sortMenu )
        aSortMenu.setIcon( QIcon( ":/mksicons/sort.png" ))
        aSortMenu.setToolTip( aSortMenu.text() )
        
        menu.addAction( sortMenu.menuAction() )
        menu.exec_( self.tvFiles.mapToGlobal( pos ) )
