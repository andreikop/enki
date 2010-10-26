"""
Workspace class implements spacked widget with opened textual documents, 
Qt Designers, Qt Assistants and other widgets, creates and manages opened 
file list, opens and closes files...
Instance accessible as mks.monkeycore.workspace()
First time created by mainWindow()
"""
import os.path
import copy
import sys

from PyQt4 import uic

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import PyQt4.fresh

import mks.monkeycore
import mks.monkeystudio
import mks.child
#import mks.abstractchild

"""
CONTENT_CHANGED_TIME_OUT = 3000
DEFAULT_CONTEXT = "Default"
"""

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
        self.mSortMode = _OpenedFileModel.OpeningOrder
        self.mSortDocumentsTimer = QTimer( self )
        self.mSortDocumentsTimeout = 150
        
        self.mSortDocumentsTimer.timeout.connect(self.sortDocuments_timeout)
        parentObject.parent().documentOpened.connect(self.documentOpened)
        parentObject.parent().documentModifiedChanged.connect(self.documentModifiedChanged)
        parentObject.parent().documentClosed.connect(self.documentClosed)
        
        self.mSortMode = self.Suffixes # FIXME
    
    def columnCount(self, parent ):
        return 1

    def rowCount(self, parent ):
        if parent.isValid():
            return 0
        else:
            return len(mks.monkeycore.workspace()._sortedDocuments)
    
    def hasChildren(self, parent ):
        if parent.isValid():
           return False
        else:
            return (len(mks.monkeycore.workspace()._sortedDocuments) > 0)

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
        if  parent.isValid() or column > 0 or column < 0 or row < 0 or row >= len(mks.monkeycore.workspace()._sortedDocuments) :
            return QModelIndex()

        return self.createIndex( row, column, mks.monkeycore.workspace()._sortedDocuments[row] )
    
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
        
        if  row >= len(mks.monkeycore.workspace()._sortedDocuments):
            row-= 1

        elif  fromRow < row :
            row-= 1

        newDocuments = copy.copy(mks.monkeycore.workspace()._sortedDocuments)
        
        item = newDocuments.pop(fromRow)
        
        #if row > fromRow:
        #    row -= 1
        
        newDocuments.insert(row, item)
        
        self.rebuildMapping( mks.monkeycore.workspace()._sortedDocuments, newDocuments )
        
        if  self.mSortMode != _OpenedFileModel.Custom :
            self.setSortMode( _OpenedFileModel.Custom )
        
        QObject.parent(self).tvFiles.setCurrentIndex(self.documentIndex(item))
        
        return True
    
    def document(self, index ):
        if  not index.isValid() :
            return 0

        return index.internalPointer()
    
    def documentIndex(self, document ):
        row = mks.monkeycore.workspace()._sortedDocuments.index( document )
        
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
        assert( not document in mks.monkeycore.workspace()._sortedDocuments )
        self.beginInsertRows( QModelIndex(), index, index )
        mks.monkeycore.workspace()._sortedDocuments.insert( index, document )
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

        mks.monkeycore.workspace()._sortedDocuments = newList
        
        # build mapping
        for pIndex in pOldIndexes:
            row = pIndex.row()
            document = documentsMapping[ row ]
            index = mks.monkeycore.workspace()._sortedDocuments.index( document )
            mapping[ row ] = index
        
        for pIindex in pOldIndexes:
            row = pIndex.row()
            index = mapping[ row ]
            
            if  pIndex.isValid():
                pIndexes.append(self.createIndex( index, pIndex.column(), mks.monkeycore.workspace()._sortedDocuments[index] ))
            else:
                pIndexes.append(QModelIndex())
        
        self.changePersistentIndexList( pOldIndexes, pIndexes )
        self.layoutChanged.emit()


    def sortDocuments_timeout(self):
        self.mSortDocumentsTimer.stop()
        
        newDocuments = copy.copy(mks.monkeycore.workspace()._sortedDocuments)
        
        if self.mSortMode == self.OpeningOrder:
            newDocuments.sort(lambda a, b: cmp(mks.monkeycore.workspace()._sortedDocuments.index(a), mks.monkeycore.workspace()._sortedDocuments.index(b)))
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
        self.rebuildMapping( mks.monkeycore.workspace()._sortedDocuments, newDocuments )
                    # scroll the view
        QObject.parent(self).tvFiles.scrollTo( QObject.parent(self).tvFiles.selectionModel().selectedIndexes()[0] )

    def documentOpened(self, document ):
        if document in mks.monkeycore.workspace()._sortedDocuments:
           self.sortDocuments()
        else:
            if document is None or document in mks.monkeycore.workspace()._sortedDocuments:
                return
            
            index = len(mks.monkeycore.workspace()._sortedDocuments)
            self.insertDocument( document, index )

    def documentModifiedChanged(self, document, modified ):
        index = self.documentIndex( document )
        self.dataChanged.emit( index, index )

    def documentClosed(self, document ):
        index = mks.monkeycore.workspace()._sortedDocuments.index( document )
        
        if  index == -1 :
            return
        
        # scroll the view
        QObject.parent(self)._startModifyModel()
        self.beginRemoveRows( QModelIndex(), index, index )
        mks.monkeycore.workspace()._sortedDocuments.remove( document )
        self.endRemoveRows()
        QObject.parent(self)._finishModifyModel()


class _OpenedFileExplorer(PyQt4.fresh.pDockWidget):
    """Opened File Explorer is list widget with list of opened files.
    It implements switching current file, files sorting. Uses _OpenedFileModel internally.
    Class instance created by Workspace.
    """
    def __init__(self, workspace):
        PyQt4.fresh.pDockWidget.__init__(self, workspace)
        
        self.mModel = _OpenedFileModel(self)
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
        workspace.currentDocumentChanged.connect(self.currentDocumentChanged)
        
        self.tvFiles.selectionModel().selectionChanged.connect(self.selectionModel_selectionChanged)  # disconnected by _startModifyModel()
    
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
    
    def currentDocumentChanged(self, document ):
        if document is not None:
            index = self.mModel.documentIndex( document )
            
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
        document = mks.monkeycore.workspace()._sortedDocuments[index.row()]
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
            if sortMode == self.mModel.sortMode():
                action.setChecked( True )
        
        aSortMenu = QAction( self.tr( "Sorting" ), self )
        aSortMenu.setMenu( sortMenu )
        aSortMenu.setIcon( mks.monkeystudio.getIcon( "file/sort.png" ))
        aSortMenu.setToolTip( aSortMenu.text() )
        
        menu.addAction( sortMenu.menuAction() )
        menu.exec_( self.tvFiles.mapToGlobal( pos ) )



class Workspace(QFrame):
    """
    Workspace class implements spacked widget with opened textual documents, 
    Qt Designers, Qt Assistants and other widgets, creates and manages opened 
    file list, opens and closes files...
    Instance accessible as mks.monkeycore.workspace().
    First time created by monkeycore.
    """
    
    """TODO
    NoTabs = "NoTabs"
    TopTabs = "TopTabs"
    BottomTabs = "BottomTabs"
    LeftTabs = "LeftTabs"
    RightTabs = "RightTabs"
    """
    # a file has been opened
    documentOpened = pyqtSignal(mks.abstractchild.pAbstractChild)
    """
    # a file have changed
    documentChanged = pyqtSignal(mks.abstractchild.pAbstractChild)
    """
    # a file modified state changed
    documentModifiedChanged = pyqtSignal(mks.abstractchild.pAbstractChild, bool)
    """TODO
    # document about to close
    documentAboutToClose = pyqtSignal(mks.abstractchild.pAbstractChild)
    """
    """A file has been closed. When signal emitted, document pointer is valid,
    document not yet removed from workspace
    """
    documentClosed = pyqtSignal(mks.abstractchild.pAbstractChild)
    """TODO
    # a file has been reloaded
    documentReloaded = pyqtSignal(mks.abstractchild.pAbstractChild)
    """
    # current file changed
    currentDocumentChanged = pyqtSignal(mks.abstractchild.pAbstractChild)
    """TODO
    buffersChanged = pyqtSignal(dict) # {file path : file contents}
    """
    
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        
        """ list of opened documents as it is displayed in the Opened Files Explorer. 
        List accessed and modified by _OpenedFileModel class
        """
        self._sortedDocuments = []
        
        self._oldCurrentDocument = None
        
        # create opened files explorer
        self.mOpenedFileExplorer = _OpenedFileExplorer(self)
        lefttb = mks.monkeycore.mainWindow().dockToolBar( Qt.LeftToolBarArea )
        lefttb.addDock( self.mOpenedFileExplorer,
                        self.mOpenedFileExplorer.windowTitle(),
                        self.mOpenedFileExplorer.windowIcon())
        
        """TODO
        self.mViewMode = self.NoTabs
        
        mb = mks.monkeycore.menuBar()

        # action group for view modes
        self.mViewModesGroup = QActionGroup( self )
        self.mViewModesGroup.addAction( mb.action( "mWindow/aNoTabs" ) )
        self.mViewModesGroup.addAction( mb.action( "mWindow/aTopTabs" ) )
        self.mViewModesGroup.addAction( mb.action( "mWindow/aBottomTabs" ) )
        self.mViewModesGroup.addAction( mb.action( "mWindow/aLeftTabs" ) )
        self.mViewModesGroup.addAction( mb.action( "mWindow/aRightTabs" ) )
        mb.action( "mWindow/aSeparator1" )

        mb.menu( "mWindow" ).insertActions( mb.action( "mWindow/aCascase" ), self.mViewModesGroup.actions() )
        mb.menu( "mWindow" ).insertAction( mb.action( "mWindow/aCascase" ), mb.action( "mWindow/aSeparator1" ) )

        actions = self.mViewModesGroup.actions()

        for i, mode in enumerate([self.NoTabs, self.TopTabs, self.BottomTabs, self.LeftTabs, self.RightTabs]):
            action = actions[i]
            action.setCheckable( True )
            action.setData( mode )

            if  self.mViewMode == mode :
                action.setChecked( True )

            if mode == self.NoTabs:
                action.setText(self.tr( "No Tabs" ) )
                action.setToolTip(self.tr( "No tabs, use 'Oopened Files List' to have a list of opened documents" ) )
            elif mode == self.TopTabs:
                action.setText(self.tr( "Tabs at &Top" ) )
                action.setToolTip( action.text() )
            elif mode == self.BottomTabs:
                action.setText(self.tr( "Tabs at &Bottom" ) )
                action.setToolTip( action.text() )
            elif mode == self.LeftTabs:
                action.setText(self.tr( "Tabs at &Left" ) )
                action.setToolTip( action.text() )
            elif mode == self.RightTabs:
                action.setText(self.tr( "Tabs at &Right" ) )
                action.setToolTip( action.text() )
        """
        
        # layout
        self.mLayout = QVBoxLayout( self )
        self.mLayout.setMargin( 0 )
        self.mLayout.setSpacing( 0 )
        """TODO
        # multitoolbar
        hline = QFrame( self )
        hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )
        """
        # document area
        self.mdiArea = QMdiArea( self )
        self.mdiArea.setActivationOrder( QMdiArea.CreationOrder )
        self.mdiArea.setDocumentMode( True )
        self.mdiArea.subWindowActivated.connect(self._onCurrentDocumentChanged)
        
        """
        # add widgets to layout
        self.mLayout.addWidget( mks.monkeycore.multiToolBar() )
        
        self.mLayout.addWidget( hline )
        """
        self.mLayout.addWidget( self.mdiArea )
        """TODO
        # creaet file watcher
        self.mFileWatcher = QFileSystemWatcher( self )
        self.mContentChangedTimer = QTimer( self )
        
        # load settings
        self.loadSettings()

        # connections
        mViewModesGroup.triggered.connect(self.viewModes_triggered)
        self.mdiArea.subWindowActivated.connect(self.mdiArea_subWindowActivated)
        parent.urlsDropped.connect(self.internal_urlsDropped)
        MonkeyCore.projectsManager().currentProjectChanged.connect(self.internal_currentProjectChanged)
        self.mContentChangedTimer.timeout.connect(self.contentChangedTimer_timeout)
        MonkeyCore.multiToolBar().notifyChanges.connect(self.multitoolbar_notifyChanges)
    """
        mks.monkeycore.menuBar().action( "mFile/aOpen" ).triggered.connect(self._fileOpen_triggered)
        mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).triggered.connect(self.closeCurrentDocument)
    
        mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).triggered.connect(self._fileSaveCurrent_triggered)
        mks.monkeycore.menuBar().action( "mFile/mSave/aAll" ).triggered.connect(self._fileSaveAll_triggered)
        
        mks.monkeycore.menuBar().action( "mView/aNext" ).triggered.connect(self.activateNextDocument)
        mks.monkeycore.menuBar().action( "mView/aPrevious" ).triggered.connect(self.activatePreviousDocument)
    
    def eventFilter( self, object, event ):
        # get document
        if  object.isWidgetType() :
            document = object
            if  document and event.type() == QEvent.Close :
                event.ignore()
                self.closeDocument( document )
                return True
        
        return QFrame.eventFilter( self, object, event )
    
    def _onCurrentDocumentChanged( self, document ):
        """Connect/disconnect document signals and update enabled/disabled 
        state of the actions
        """
        if self._oldCurrentDocument is not None:
            mks.monkeycore.menuBar().action( "mEdit/aUndo" ).triggered.disconnect(
                            self._oldCurrentDocument.undo)
            mks.monkeycore.menuBar().action( "mEdit/aRedo" ).triggered.disconnect(
                            self._oldCurrentDocument.redo)
            mks.monkeycore.menuBar().action( "mEdit/aCut" ).triggered.disconnect(
                            self._oldCurrentDocument.cut)
            mks.monkeycore.menuBar().action( "mEdit/aCopy" ).triggered.disconnect(
                            self._oldCurrentDocument.copy)
            mks.monkeycore.menuBar().action( "mEdit/aPaste" ).triggered.disconnect(
                            self._oldCurrentDocument.paste)
            self._oldCurrentDocument.modifiedChanged.disconnect(self.document_modifiedChanged)
        
        if document is not None:
            mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled(document.isModified())
            # Undo
            mks.monkeycore.menuBar().action( "mEdit/aUndo" ).triggered.connect(
                            document.undo)
            document.undoAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled)
            mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled(document.isUndoAvailable())
            # Redo
            mks.monkeycore.menuBar().action( "mEdit/aRedo" ).triggered.connect(
                            document.redo)
            mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled(document.isRedoAvailable())
            document.redoAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled)            
            # Cut
            mks.monkeycore.menuBar().action( "mEdit/aCut" ).triggered.connect(
                            document.cut)
            mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled(document.isCopyAvailable())
            document.copyAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled)
            # Copy
            mks.monkeycore.menuBar().action( "mEdit/aCopy" ).triggered.connect(
                            document.copy)
            mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled(document.isCopyAvailable())
            document.copyAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled)
            # Copy
            mks.monkeycore.menuBar().action( "mEdit/aPaste" ).triggered.connect(
                            document.paste)
            mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled(document.isPasteAvailable())
            document.pasteAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled)
            document.modifiedChanged.connect(self.document_modifiedChanged)
            
            mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled( document.isModified() )
            
        else:  # no document
            mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled(False)
            mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled(False)
            mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled(False)
            mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled(False)
            mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled(False)
            mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled(False)

        '''
        # fix fucking flickering due to window activation change on application gain / lost focus.
        if  not document and self.currentDocument() :
            return

        # get child
        editor = None
        if document:
            editor = document.editor()
        
        modified = False
        print_ = False
        undo = False
        redo = False
        copy = False
        paste = False
        go = False
        
        if document:
            modified = document.isModified()
            print_ = document.isPrintAvailable()
            undo = document.isUndoAvailable()
            redo = document.isRedoAvailable()
            copy = document.isCopyAvailable()
            paste = document.isPasteAvailable()
            go = document.isGoToAvailable()
        # context toolbar
        mtb = mks.monkeycore.multiToolBar()
        
        if  document :
            if  not mtb.contexts().contains( document.context() ) :
                tb = mtb.toolBar( document.context() )

                self.initMultiToolBar( tb )
                document.initializeContext( tb )


            mtb.setCurrentContext( document.context() )
        else:
            if  not mtb.contexts().contains( DEFAULT_CONTEXT ) :
                tb = mtb.toolBar( DEFAULT_CONTEXT )

                self.initMultiToolBar( tb )
            
            mtb.setCurrentContext( DEFAULT_CONTEXT )
        
        self.multitoolbar_notifyChanges()
        '''
        
        # update file menu
        mks.monkeycore.menuBar().action( "mFile/mSave/aAll" ).setEnabled( document is not None)
        mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled( document is not None)
        '''
        mks.monkeycore.menuBar().action( "mFile/mClose/aAll" ).setEnabled( document )
        mks.monkeycore.menuBar().action( "mFile/aReload" ).setEnabled( document )
        mks.monkeycore.menuBar().action( "mFile/aSaveAsBackup" ).setEnabled( document )
        mks.monkeycore.menuBar().action( "mFile/aQuickPrint" ).setEnabled( print_ )
        mks.monkeycore.menuBar().action( "mFile/aPrint" ).setEnabled( print_ )
        
        # update edit menu
        mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled( undo )
        mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled( redo )
        mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled( copy )
        mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled( copy )
        mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled( paste )
        mks.monkeycore.menuBar().action( "mEdit/aGoTo" ).setEnabled( go )
        mks.monkeycore.menuBar().action( "mEdit/aExpandAbbreviation" ).setEnabled( document )
        mks.monkeycore.menuBar().setMenuEnabled( mks.monkeycore.menuBar().menu( "mEdit/mAllCommands" ), editor )
        mks.monkeycore.menuBar().setMenuEnabled( mks.monkeycore.menuBar().menu( "mEdit/mBookmarks" ), editor )
        '''
        
        # update view menu
        moreThanOneDocument = len(self.mdiArea.subWindowList()) > 1
        mks.monkeycore.menuBar().action( "mView/aNext" ).setEnabled( moreThanOneDocument )
        mks.monkeycore.menuBar().action( "mView/aPrevious" ).setEnabled( moreThanOneDocument )
        
        '''TODO
        # update status bar
        mks.monkeycore.statusBar().setModified( modified )
        if editor:
            mks.monkeycore.statusBar().setEOLMode( editor.eolMode() )
            mks.monkeycore.statusBar().setIndentMode( editor.indentationsUseTabs())
            mks.monkeycore.statusBar().setCursorPosition( document.cursorPosition())
        
            mks.monkeycore.statusBar().setEOLMode( editor.eolMode())
            mks.monkeycore.statusBar().setIndentMode( editor.indentationsUseTabs())
            mks.monkeycore.statusBar().setCursorPosition( document.cursorPosition())
        # internal update
        if  document :
            QDir.setCurrent( document.path() )
        '''
        self._oldCurrentDocument = document
        
        self.currentDocumentChanged.emit( document )
    
    '''TODO
    def defaultContext(self):
        return DEFAULT_CONTEXT
    
    def loadSettings(self):
        # restore tabs settings
        tabBar().setTabsHaveCloseButton( tabsHaveCloseButton() )
        tabBar().setTabsHaveShortcut( tabsHaveShortcut() )
        tabBar().setTabsElided( tabsElided() )
        tabBar().setTabsColor( tabsTextColor() )
        tabBar().setCurrentTabColor( currentTabTextColor() )
        self.mOpenedFileExplorer.setSortMode( mks.monkeystudio.openedFileSortingMode() )
        self.setDocumentMode( mks.monkeystudio.documentMode() )
        mtb = mks.monkeycore.multiToolBar()

        for context in mtb.contexts():
            tb = mtb.toolBar( context )
            self.initMultiToolBar( tb )
        
        self.multitoolbar_notifyChanges()
    
    def initMultiToolBar( self, tb ):
        if  mks.monkeystudio.showQuickFileAccess() :
            tb.insertAction( tb.actions().value( 0 ), mks.monkeycore.workspace().dockWidget().comboBoxAction() )
        else:
            tb.removeAction( mks.monkeycore.workspace().dockWidget().comboBoxAction() )
    
    def fileWatcher(self):
        return self.mFileWatcher
    
    
    def document( index ):
        window = self.mdiArea.subWindowList().value( index )
        return window

    def indexOfDocument( self, document ):
        return self.mdiArea.subWindowList().indexOf( document )

    def documents(self):
        return self.mdiArea.subWindowList()
    '''
    
    def setCurrentDocument( self, document ):
        #fixme replace with setCurrentFile?
        self.mdiArea.setActiveSubWindow( document )
    
    def currentDocument(self):
        return self.mdiArea.currentSubWindow()
    
    """TODO
    def goToLine(  self, fileName,  pos,  codec, selectionLength ):
        for window in self.mdiArea.subWindowList():
            if  mks.monkeystudio.isSameFile( window.filePath(), fileName ) :
                self.setCurrentDocument( window )
                document.goTo( pos, selectionLength )
                return

        document = self.openFile( fileName, codec )

        if  document :
            document.goTo( pos, selectionLength )
    """
    
    def closeDocument( self, document, showDialog = True):
        """Close opened file, open document from workspace and delete widget"""
        
        """TODO
        if  showDialog and UISaveFiles.saveDocument( self.window(), document, False ) == UISaveFiles.bCancelClose :
            return
        """
        
        """ TODO
        # stop watching files
        file = document.filePath()
        if  QFileInfo( file ).isFile() and self.mFileWatcher.files().contains( file ) :
            self.mFileWatcher.removePath( file )
        """
        self.documentClosed.emit( document )
        # close document
        self._unhandleDocument( document ) #FIXME make sure not always unhandleDocument
        document.deleteLater()
    
    """TODO
    def documentMode(self):
        return self.mViewMode
    """

    def _handleDocument( self, document ):
        """TODO
        # init document connections
        document.fileOpened.connect(self.document_fileOpened)
        document.contentChanged.connect(self.document_contentChanged)
        document.modifiedChanged.connect(self.document_modifiedChanged)
        document.fileClosed.connect(self.document_fileClosed)
        document.fileReloaded.connect(self.document_fileReloaded)
        """
        # update file menu
        document.modifiedChanged.connect(mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled)
        """
        # update edit menu
        document.undoAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled)
        document.redoAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled)
        document.copyAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled)
        document.copyAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled)
        document.pasteAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled)
        
        # update status bar
        document.cursorPositionChanged.connect(mks.monkeycore.statusBar().setCursorPosition)
        document.modifiedChanged.connect(mks.monkeycore.statusBar().setModified)
        """        
        # add to workspace
        document.installEventFilter( self )
        
        self.mdiArea.blockSignals( True )
        self.mdiArea.addSubWindow( document )
        self.mdiArea.blockSignals( False )
    
    def _unhandleDocument( self, document ):
        
        """TODO
        # init document connections
        disconnect( document, SIGNAL( fileOpened() ), this, SLOT( document_fileOpened() ) )
        disconnect( document, SIGNAL( contentChanged() ), this, SLOT( document_contentChanged() ) )
        disconnect( document, SIGNAL( modifiedChanged( bool ) ), this, SLOT( document_modifiedChanged( bool ) ) )
        disconnect( document, SIGNAL( fileClosed() ), this, SLOT( document_fileClosed() ) )
        disconnect( document, SIGNAL( fileReloaded() ), this, SLOT( document_fileReloaded() ) )
        # update file menu
        """
        document.modifiedChanged.disconnect(mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled)
        # update edit menu
        """TODO
        document.undoAvailableChanged.disconnect(mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled)
        document.redoAvailableChanged.disconnect(mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled)
        document.copyAvailableChanged.disconnect(mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled)
        document.copyAvailableChanged.disconnect(mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled)
        document.pasteAvailableChanged.disconnect(mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled)
        # update status bar
        
        disconnect( document, SIGNAL( cursorPositionChanged(  QPoint& ) ), mks.monkeycore.statusBar(), SLOT( setCursorPosition(  QPoint& ) ) )
        disconnect( document, SIGNAL( modifiedChanged( bool ) ), mks.monkeycore.statusBar(), SLOT( setModified( bool ) ) )
        """
        # remove from workspace
        document.removeEventFilter( self )
        self.mdiArea.removeSubWindow( document )
        
        # maximize current window if needed
        if document.isMaximized() :
            if self.mdiArea.currentSubWindow() :
               self.mdiArea.currentSubWindow().showMaximized()
    
    def openFile(self, fileName):
        """Open named file. Shows error messages to the user, if failed to open
        Returns document, if opened, None otherwise
        """
        
        # check if file is already opened
        for document in self._sortedDocuments:
            if os.path.isfile(fileName) and os.path.samefile( document.filePath(), fileName ) :
                self.setCurrentDocument( document )
                return document
        
        """TODO
        # get a document interface that can handle the file
        document = mks.monkeycore.pluginsManager().documentForFileName( fileName )
        """
        documentType = None
        
        # open it with pChild instance if no document
        if not documentType :
            documentType = mks.child.pChild
        
        # open file
        try:
            QApplication.setOverrideCursor( Qt.WaitCursor )
            document = documentType(self, fileName)
        except IOError, ex:
            #TODO mks.monkeycore.messageManager().appendMessage(self.tr( "An error occur while opening self file: '%1'" % str(ex))
            print >> sys.stderr, ex
            return None
        finally:
            QApplication.restoreOverrideCursor()
        
        self.documentOpened.emit( document )
        
        self._handleDocument( document )
        
        document.showMaximized()
        #FIXME remove. Genrates too lot if signals. 
        #self.setCurrentDocument( document )
        
        return document
    
    """TODO
    def closeFile(self, filePath ):
        for window in a.subWindowList():
            if  mks.monkeystudio.isSameFile( window.filePath(), h ) :
                self.closeDocument( window )
                return
    """
    
    def closeCurrentDocument(self):
        #fixme replace with setCurrentFile?
        document = self.mdiArea.currentSubWindow()
        assert(document is not None)
        self.closeDocument( document )
    
    def openedDocuments(self):
        """Get list of opened documents (mks.abstractchild instances)
        """
        return self._sortedDocuments
    
    """TODO
    def closeAllDocuments(self):
        # try save documents
        button = UISaveFiles.saveDocuments( window(), self.openedDocuments(), False )

        # close all object, them
        if  button != UISaveFiles.bCancelClose :
            # stop watching files
            for window in a.subWindowList():
                document = window
                self.closeDocument( document, e )
            return True
        else:
            return False; #not close IDE
        return True
    """
    
    def activateNextDocument(self):
        curIndex = self._sortedDocuments.index(self.currentDocument())
        nextIndex = (curIndex + 1) % len(self._sortedDocuments)
        self.setCurrentDocument( self._sortedDocuments[nextIndex] )
    
    def activatePreviousDocument(self):
        curIndex = self._sortedDocuments.index(self.currentDocument())
        prevIndex = (curIndex - 1 + len(self._sortedDocuments)) % len(self._sortedDocuments)
        self.setCurrentDocument( self._sortedDocuments[prevIndex] )
    
    """TODO
    def focusEditor(self):
        document = self.currentDocument()

        if  document :
            document.setFocus()
    
    def tile(self):
        self.mdiArea.tileSubWindows()

    def cascade(self):
        self.mdiArea.cascadeSubWindows()

    def minimize(self):
        self.setDocumentMode( self.NoTabs )

        for window in a.subWindowList():
            window.showMinimized()

    def restore(self):
        self.setDocumentMode( self.NoTabs )

        for window in a.subWindowList():
            window.showNormal()

    def setDocumentMode(self, mode ):
        if self.mViewMode == mode :
            return

        document = self.mdiArea.currentSubWindow()
        e = mode
        
        if self.mViewMode == self.NoTabs:
            self.mdiArea.setViewMode( QMdiArea.SubWindowView )
        elif self.mViewMode == self.TopTabs:
            self.mdiArea.setTabPosition( QTabWidget.North )
            self.mdiArea.setViewMode( QMdiArea.TabbedView )
        elif self.mViewMode == self.BottomTabs:
            self.mdiArea.setTabPosition( QTabWidget.South )
            self.mdiArea.setViewMode( QMdiArea.TabbedView )
        elif self.mViewMode == self.LeftTabs:
            self.mdiArea.setTabPosition( QTabWidget.West )
            self.mdiArea.setViewMode( QMdiArea.TabbedView )
        elif self.mViewMode == self.RightTabs:
            self.mdiArea.setTabPosition( QTabWidget.East )
            self.mdiArea.setViewMode( QMdiArea.TabbedView )
        
        self.mOpenedFileExplorer.setVisible( e == self.NoTabs )

        if  document and not document.isMaximized() :
            document.showMaximized()
        
        for action in self.mViewModesGroup.actions():
            if  action.data().toInt() == self.mViewMode :
                if  not action.isChecked() :
                    action.setChecked( True )
                return

    def createNewTextEditor(self):
        result = MkSFileDialog.getNewEditorFile( window() )

        # open open file dialog
        fileName = result[ "filename" ].toString()
        
        # return 0 if user cancel
        if  fileName.isEmpty() :
            return 0
        
        # close file if already open
        self.closeFile( fileName )

        # create/reset file
        file = QFile ( fileName )

        if  not file.open( QIODevice.WriteOnly ) :
            mks.monkeycore.messageManager().appendMessage(self.tr( "Can't create file '%1'" ).arg( QFileInfo( fileName ).fileName() ) )
            return 0

        # reset file
        file.resize( 0 )
        file.close()

        if  result.value( "addtoproject", e ).toBool() :
            # add files to scope
            mks.monkeycore.projectsManager().addFilesToScope( result[ "scope" ].value(XUPItem), [fileName] )
        
        # open file
        return self.openFile( fileName, result[ "codec" ].toString() )

    def document_fileOpened(self):
        document = self.sender() # signal sender
        if  QFileInfo( document.filePath() ).isFile() and not self.mFileWatcher.files().contains( document.filePath() ) :
            self.mFileWatcher.addPath( document.filePath() )
        self.documentOpened.emit( document )
    

    def document_contentChanged(self):
        self.mContentChangedTimer.start( CONTENT_CHANGED_TIME_OUT )
        document = self.sender() # signal sender

        # externally deleted files make the filewatcher to no longer watch them
        path = document.filePath()
        
        self.documentChanged.emit( document )

    """
    def document_modifiedChanged(self, modified ):
        document = self.sender()
        self.documentModifiedChanged.emit( document, modified )
    
    """TODO

    def document_fileClosed(self):
        document = self.sender()
        mtb = mks.monkeycore.multiToolBar()
        mtb.removeContext( document.context(), e )
        self.documentClosed.emit( document )


    def document_fileReloaded(self):
        document = self.sender()
        self.documentReloaded.emit( document )

    def contentChangedTimer_timeout(self):
        self.mContentChangedTimer.stop()
        
        entries = {}
        
        for document in self.documents():
            if  document.isModified() :
                entries[ document.filePath() ] = document.fileBuffer()

        self.buffersChanged.emit( entries )
    
    def multitoolbar_notifyChanges(self):
        mtb = mks.monkeycore.multiToolBar()
        tb = mtb.currentToolBar()
        show = tb and not tb.actions().isEmpty()

        mtb.setVisible( show )

    def viewModes_triggered(self, action ):
        self.setDocumentMode( action.data().toInt() )
    
    def mdiArea_subWindowActivated(self, document ):

        # update gui state
        self.updateGuiState( document )

    def internal_urlsDropped(self, urls ):
        # create menu
        menu = QMenu()
        aof = menu.addAction(self.tr( "Open As &File" ) )
        aop = menu.addAction(self.tr( "Open As &Project" ) )
        menu.addSeparator()
        menu.addAction(self.tr( "Cancel" ) )

        # execute menu
        action = menu.exec_( QCursor.pos() )

        # check triggered action
        if action == aof :
            for url in s:
                if  not url.toLocalFile().trimmed().isEmpty() :
                    self.openFile( url.toLocalFile(), c() )
        elif action == aop :
            for url in s:
                if  not url.toLocalFile().trimmed().isEmpty() :
                    mks.monkeycore.projectsManager().openProject( url.toLocalFile(), c() )


    def internal_currentProjectChanged(self, currentProject, previousProject ):
        # uninstall old commands
        if  previousProject :
            previousProject.uninstallCommands()
            disconnect( previousProject, L( installCommandRequested(  pCommand&, & ) ), s, T( internal_projectInstallCommandRequested(  pCommand&, & ) ) )
            disconnect( previousProject, L( uninstallCommandRequested(  pCommand&, & ) ), s, T( internal_projectUninstallCommandRequested(  pCommand&, & ) ) )
    
        # get pluginsmanager
        pm = mks.monkeycore.pluginsManager()
        
        # set debugger and interpreter
        bp = currentProject ? currentProject.builder() : 0
        dp = currentProject ? currentProject.debugger() : 0
        ip = currentProject ? currentProject.interpreter() : 0
        
        pm.setCurrentBuilder( bp and not bp.neverEnable() ? bp : 0 )
        pm.setCurrentDebugger( dp and not dp.neverEnable() ? dp : 0 )
        pm.setCurrentInterpreter( ip and not ip.neverEnable() ? ip : 0 )
        
        # install commands
        if  currentProject :
            connect( currentProject, L( installCommandRequested(  pCommand&, & ) ), s, T( internal_projectInstallCommandRequested(  pCommand&, & ) ) )
            connect( currentProject, L( uninstallCommandRequested(  pCommand&, & ) ), s, T( internal_projectUninstallCommandRequested(  pCommand&, & ) ) )

            currentProject.installCommands()
        
        # update menu visibility
        mks.monkeycore.mainWindow().menu_CustomAction_aboutToShow()


    def internal_projectInstallCommandRequested(self, cmd, mnu ):
        # create action
        action = mks.monkeycore.menuBar().action( QString( "%1/%2" ).arg( mnu ).arg( cmd.text() ) , d.text() )
        action.setStatusTip( cmd.text() )

        # set action custom data contain the command to execute
        action.setData( QVariant.fromValue( cmd ) )
        
        # connect to signal
        action.triggered().connect(s.internal_projectCustomActionTriggered())
        
        # update menu visibility
        mks.monkeycore.mainWindow().menu_CustomAction_aboutToShow()


    def internal_projectUninstallCommandRequested(self, cmd, mnu ):
        menu = mks.monkeycore.menuBar().menu( mnu )
        
        for action in u.actions():
            if  action.menu() :
                internal_projectUninstallCommandRequested( cmd, QString( "%1/%2" ).arg( mnu ).arg( action.menu().objectName() ) )
            elif  not action.isSeparator() and action.data().value(pCommand) == cmd :
                delete action

        # update menu visibility
        mks.monkeycore.mainWindow().menu_CustomAction_aboutToShow()

    def internal_projectCustomActionTriggered(self):
        action = self.sender()

        if  action :
            cm = mks.monkeycore.consoleManager()
            cmd = action.data().value<pCommand>()
            cmdsHash = cmd.userData().value<pCommandMap*>()
            cmds = cmdsHash ? cmdsHash.values() : pCommandList()

            # save project files
            if  mks.monkeystudio.saveFilesOnCustomAction() :
                fileSaveAll_triggered()


            # check that command to execute exists, ask to user if he want to choose another one
            if  cmd.targetExecution().isActive and cmd.project() :
                d = cm.processCommand( cm.getCommand( cmds, d.text() ) )
                fileName = cmd.project().filePath( cmd.command() )
                workDir = cmd.workingDirectory()

                # Try to correct command by asking user
                if  not QFile.exists( fileName ) :
                    project = cmd.project()
                    e = project.targetFilePath( cmd.targetExecution() )

                    if  fileName.isEmpty() :
                        return


                     QFileInfo fileInfo( fileName )

                    # if not exists ask user to select one
                    if  not fileInfo.exists() :
                        QMessageBox.critical( window(), r( "Executable file not found" ), r( "Target '%1' does not exists" ).arg( fileName ) )
                        return


                    if  not fileInfo.isExecutable() :
                        QMessageBox.critical( window(), r( "Can't execute target" ), r( "Target '%1' is not an executable" ).arg( fileName ) )
                        return


                    # file found, it is executable. Correct command
                    cmd.setCommand( fileName )
                    cmd.setWorkingDirectory( fileInfo.absolutePath() )


                cm.addCommand( cmd )

                return


            # generate commands list
            mCmds = cm.recursiveCommandList( cmds, m.getCommand( cmds, d.text() ) )

            # the first one must not be skipped on last error
            if  not mCmds.isEmpty() :
                mCmds.first().setSkipOnError( False )


            # send command to consolemanager
            cm.addCommands( mCmds )


    # file menu
    def fileNew_triggered(self):
        wizard = UITemplatesWizard ( self )
        wizard.setType( "Files" )
        wizard.exec_()
    """
    
    def _fileOpen_triggered(self):
        """Main menu handler"""
        """TODO
        mFilters = mks.monkeystudio.availableFilesFilters() # get available filters

        # show filedialog to user
        result = MkSFileDialog.getOpenFileNames( window(), tr( "Choose the file(s) to open" ), QDir.currentPath(), mFilters, True, False )
        
        # open open file dialog
        fileNames = result[ "filenames" ].toStringList()
        """
        fileNames = QFileDialog.getOpenFileNames( self.window(), self.tr( "Choose the file(s) to open" ))
                
        for file in fileNames:
            if self.openFile(file) is not None:
                pass
                #TODO mks.monkeycore.recentsManager().addRecentFile( file )
    
    '''TODO
    def fileSessionSave_triggered(self):
        files = []
        projects = []

        # files
        for window in self.mdiArea.subWindowList():
            document = window
            files.append(document.filePath())

        mks.monkeycore.settings().setValue( "Session/Files", files )
        
        # projects
        for project in mks.monkeycore.projectsManager().topLevelProjects():
            projects.append(project.fileName())

        mks.monkeycore.settings().setValue( "Session/Projects", projectss )

    def fileSessionRestore_triggered(self):
        # restore files
        for file in mks.monkeycore.settings().value("Session/Files", [] ).toStringList():
            if not self.openFile( file, mks.monkeystudio.defaultCodec() ): # remove it from recents files
                mks.monkeycore.recentsManager().removeRecentFile( file )
        
        # restore projects
        for project in mks.monkeycore.settings().value( "Session/Projects", [] ).toStringList():
            if not mks.monkeycore.projectsManager().openProject( project, mks.monkeystudio.defaultCodec() ): # remove it from recents projects
                mks.monkeycore.recentsManager().removeRecentProject( project )
    
    '''
    
    def _fileSaveCurrent_triggered(self):
        """TODO
        self.mFileWatcher.removePath( self.currentDocument().filePath() )
        """
        self.currentDocument().saveFile()
        """TODO
        self.mFileWatcher.addPath( fn )
        """
    
    def _fileSaveAll_triggered(self):
        # fixme duplicating code with save current
        for document in self.openedDocuments():
            """TODO
            self.mFileWatcher.removePath( document.filePath() )
            """
            document.saveFile()
            """TODO
            self.mFileWatcher.addPath( fn )
            """
    
    '''TODO
    def fileCloseAll_triggered(self):
        self.closeAllDocuments()  # fixme KILL this 

    def fileReload_triggered(self):
        document = self.currentDocument()

        if  document :
            button = QMessageBox.Yes

            if  document.isModified() :
                n = QMessageBox.question( self, self.tr( "Confirmation needed..." ), self.tr( "The file has been modified, anyway ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No )

            if button == QMessageBox.Yes :
                """ fileName = document.filePath()
                 codec = document.textCodec()

                self.closeDocument( document )
                self.openFile( fileName, c );"""
                document.reload()

    def fileSaveAsBackup_triggered(self):
        document = self.currentDocument()

        if  document :
            fileName = mks.monkeystudio.getSaveFileName(self.tr( "Choose a filename to backup your file" ), document.fileName(), '', self )

            if  not fileName.isEmpty() :
                document.backupFileAs( fileName )

    def fileQuickPrint_triggered(self):
        document = self.currentDocument()

        if  document :
            document.quickPrintFile()

    def filePrint_triggered(self):
        document = self.currentDocument()

        if  document :
            document.printFile()
    
    def fileExit_triggered(self):
        window().close()

    # edit menu
    def editSettings_triggered(self):
        UISettings.instance( self ).exec_()

    def editTranslations_triggered(self):
        locale = TranslationDialog.getLocale( mks.monkeycore.translationsManager(), self )

        if  not locale.isEmpty() :
            mks.monkeycore.settings().setValue( "Translations/Locale", locale )
            mks.monkeycore.settings().setValue( "Translations/Accepted", True )
            mks.monkeycore.translationsManager().setCurrentLocale( locale )
            mks.monkeycore.translationsManager().reloadTranslations()

    def editUndo_triggered(self):
        document = self.currentDocument()

        if  document :
            document.undo()

    def editRedo_triggered(self):
        document = self.currentDocument()

        if  document :
            document.redo()

    def editCut_triggered(self):
        document = self.currentDocument()

        if  document :
            document.cut()


    def editCopy_triggered(self):
        document = self.currentDocument()

        if  document :
            document.copy()


    def editPaste_triggered(self):
        document = self.currentDocument()

        if  document :
            document.paste()

    def editSearch_triggered(self):
        document = self.currentDocument()

        if  document and not document.editor() :
            document.invokeSearch()


    def editGoTo_triggered(self):
        document = self.currentDocument()

        if  document :
            document.goTo()


    def editExpandAbbreviation_triggered(self):
        document = self.currentDocument()

        if  document :
            mks.monkeycore.abbreviationsManager().expandMacro( document.editor() )



    def editPrepareAPIs_triggered(self):
        mks.monkeystudio.prepareAPIs()

    # help menu
    def helpAboutApplication_triggered(self):
        dlg = UIAbout( self )
        dlg.open()
    '''
