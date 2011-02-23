"""
workspace --- Open documents and manage it
==========================================

Terminology:

Workspace - main working area, where documents are placed.

Document - widget on workspace. Here is examples of documents:

* Textual editor
* QtDesigner
* QtAssistant

Document classes are herited from :class:`AbstractDocument`

:class:`mks.workspace.Workspace` - module API

:class:`mks.workspace.AbstractDocument`  - base class of workspace documents

Module also contains widget, which shows list of opened documents and AbstractItemModel for manage this list.
"""
import os.path
import copy
import sys

from PyQt4 import uic

from PyQt4.QtGui import QTreeView, QWidget, QStackedWidget, QFileDialog, \
                        QFrame, QKeySequence, QVBoxLayout, QApplication, \
                        QIcon, QMenu, \
                        QMessageBox, QAction, QActionGroup
from PyQt4.QtCore import QByteArray, Qt, QObject, QAbstractItemModel, QMimeData, \
                         QEvent, QFileInfo, QModelIndex, QVariant, pyqtSignal

import PyQt4.fresh

import mks.monkeystudio

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
        self.mSortMode = mks.monkeycore.config()["Workspace"]["FileSortMode"]
        workspace = parentObject.parent()
        workspace.documentOpened.connect(self.documentOpened)
        workspace.documentClosed.connect(self.documentClosed)
    
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
                    return QIcon( ":/mksicons/save.png" )
                else:
                    return QIcon( ":/mksicons/transparent.png" )
            else:
                return document.windowIcon()
        elif role == Qt.DisplayRole:
                return document.fileName()
        elif role == Qt.ToolTipRole:
            return document.filePath()
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
            if mode != self.Custom:
                mks.monkeycore.config()["Workspace"]["FileSortMode"] = mode
            self.sortDocuments()

    def sortDocuments(self):
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

    def documentOpened(self, document ):
        assert( not document in mks.monkeycore.workspace()._sortedDocuments )
        mks.monkeycore.workspace()._sortedDocuments.append( document )
        self.sortDocuments()
        document.modifiedChanged.connect(self.documentModifiedChanged)

    def documentModifiedChanged(self, modified ):
        document = self.sender()
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
        uic.loadUi(os.path.join(mks.monkeycore.dataFilesPath(), 'ui/pOpenedFileExplorer.ui'), self )
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

        mks.monkeycore.workspace().documentChanged.connect(self.documentChanged)
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


class AbstractDocument(QWidget):
    """Base class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant, ...
    Inherit this class, if you want to create new document type
    """
    
    modifiedChanged = pyqtSignal(bool)
    """
    modifiedChanged(modified)
    
    **Signal** emitted, when modified state changed (file edited, or saved)
    Bool parameter contains new value
    """
    
    """TODO
    enum DocumentMode { mNone:, mNa, mInsert, mOverwrite, mReadOnly } mDocument
    enum LayoutMode { lNone:, lNormal, lVertical, lHorizontal } mLayout
    """
    
    def __init__( self, parentObject, filePath):
        """Create editor and open file.
        IO Exceptions not catched, so, must be catched on upper level
        """
        QWidget.__init__( self, parentObject )
        
        self._filePath = None # To be filled by child classes
        
        # default for window icon is application icon. This line avoids using it in the opened files list
        self.setWindowIcon(QIcon())
        self.setWindowTitle("[*]")  # avoid warning
        
        """TODO
        mCodec:
        setAttribute( Qt.WA_DeleteOnClose )
        mDocument = mNone
        mLayout = lNone
        """
        # File opening should be implemented in the document classes
    
    def eolMode(self):
        """Return document's EOL mode. Possible values are:
            r"\n"  - UNIX EOL
            r"\r\n" - Windows EOL
            None - not defined for the editor type
        """
        return None
    
    def setEolMode(self, mode):
        """Set editor EOL mode.
        See eolMode() for a alowed mode values
        """
        pass
    
    def indentWidth(self):
        """Get width of tabulation symbol and count of spaces to insert, when Tab pressed
        """
        pass
    
    def setIndentWidth(self, width):
        """Set width of tabulation symbol and count of spaces to insert, when Tab pressed
        """
        pass
    
    def indentUseTabs(self):
        """Get indentation uses tabs flag.
        If true - \t inserted by Tab button, if false - spaces
        """
        pass
    
    def setIndentUseTabs(self, use):
        """Set indentation uses tabs flag.
        If true - \t inserted by Tab button, if false - spaces
        """
        pass
    
    '''TODO
    def sizeHint(self):
        """eturn defaultsize for document
        """
        return QSize( 640, 480 )

    def documentMode(self):
        """return document document mode
        """
        return self.mDocument

    def layoutMode(self):
        """return the document layout mode"""
        return self.mLayout
    
    def language(self):
        """return document language
        """
        return QString.null;
    '''
        
    def filePath(self):
        """return the document file path"""
        return self._filePath
    
    def fileName(self):
        """return the document file name"""
        return os.path.basename(self._filePath)
    
    '''TODO
    def path(self):
        """return the absolute path of the document"""
        wfp = self.windowFilePath()
        if wfp.isEmpty():
            return None
        else:
            return QFileInfo( wfp ).absolutePath()
    '''
    
    def fileBuffer(self):
        """return the current buffer (text) of opened file"""
        return None
    
    def cursorPosition(self):
        """return cursor position as 2 values: line and column, if available
        """
        pass
    
    '''
    def editor(self):
        """the current visible editor
        """
        pass
    '''
    def isModified(self):
        """Returns true, if file is modified
        """
        pass
    
    '''TODO
    def isPrintAvailable(self):
        """return if print is available
        """
        pass

    def setDocumentMode(self, documentMode ):
        """set the document document mode"""
        if  self.mDocument == documentMode :
            return
        self.mDocument = documentMode
        self.documentModeChanged.emit( self.mDocument )

    def setLayoutMode(self layoutMode )
        """set the document layout mode
        """
        
        if  self.mLayout == layoutMode :
            return
        self.mLayout = layoutMode
        self.layoutModeChanged.emit( self.mLayout )

    
    def textCodec(self)
    { return mCodec ? mCodec.name() : pMonkeyStudio.defaultCodec();
    
    def encoding(self)
    { return mCodec ? mCodec : QTextCodec.codecForName( pMonkeyStudio.defaultCodec().toLocal8Bit().constData() );
    '''
    
    def goTo(self, line, column, selectionLength = -1 ):
        pass
    
    '''
    def invokeSearch(self):
        pass
    '''
    def saveFile(self):
        """Save changes, made in the file
        """
        pass
    '''TODO
    def backupFileAs(self fileName ):
        pass
    
    def closeFile(self):
        pass
    '''
    def reload(self):
        pass
    '''
    def printFile(self):
        pass
    
    def quickPrintFile(self):
        pass
    fileOpened = pyqtSignal()
    fileClosed = pyqtSignal()
    # when.emit a file is reloaded
    fileReloaded = pyqtSignal()
    # when.emit the content changed
    contentChanged = pyqtSignal()
    # when.emit the document layout mode has changed
    layoutModeChanged = pyqtSignal()
    # when.emit the document document mode has changed
    documentModeChanged = pyqtSignal()
    '''
    # emit when cursor position changed
    cursorPositionChanged = pyqtSignal(int, int) # (line, column)
    
    '''TODO
    # when.emit search/replace is available
    #searchReplaceAvailableChanged = pyqtSignal(bool)
    # when.emit requesting search in editor
    #requestSearchReplace = pyqtSignal()
    # when.emit a document require to update workspace
    #updateWorkspaceRequested()
    '''

class Workspace(QStackedWidget):
    """
    Class manages set of opened documents, allows to open new file
    
    Instance accessible as: ::
    
        mks.monkeycore.workspace()
    
    First time created by ::class:mks.mainwindow.MainWindow
    
    NOTE: class contains some methods, which are not public now, but, could be useful for plugins.
    If you found such method - don't use it silently, send bug report for make it public and document
    """
    
    """TODO
    NoTabs = "NoTabs"
    TopTabs = "TopTabs"
    BottomTabs = "BottomTabs"
    LeftTabs = "LeftTabs"
    RightTabs = "RightTabs"
    """
    
    documentOpened = pyqtSignal(AbstractDocument)
    """
    documentOpened(:class:AbstractDocument)
    
    **Signal** emitted, when document has been created, i.e. textual file opened, 
    or some other document added to workspace
    
    TODO rename class?
    """
    
    """
    # a file have changed
    documentChanged = pyqtSignal(AbstractDocument)
    """
    # a file modified state changed
    
    """TODO
    # document about to close
    documentAboutToClose = pyqtSignal(AbstractDocument)
    """
    """A file has been closed. When signal emitted, document pointer is valid,
    document not yet removed from workspace
    """
    
    documentClosed = pyqtSignal(AbstractDocument)
    """
    documentClosed(:class:AbstractDocument)
    
    **Signal** emitted, when document was closed
    """
    
    """TODO
    # a file has been reloaded
    documentReloaded = pyqtSignal(AbstractDocument)
    """
    
    currentDocumentChanged = pyqtSignal(AbstractDocument, AbstractDocument)
    """
    currentDocumentChanged(:class:AbstractDocument old, :class:AbstractDocument current)
    
    **Signal** emitted, when current document changed, i.e. user selected another document, 
    new document opened, current closed
    """
    
    """TODO
    buffersChanged = pyqtSignal(dict) # {file path : file contents}
    """
    
    def __init__(self, mainWindow):
        QStackedWidget.__init__(self, mainWindow)
        
        """ list of opened documents as it is displayed in the Opened Files Explorer. 
        List accessed and modified by _OpenedFileModel class
        """
        self._sortedDocuments = []
        
        self._oldCurrentDocument = None
        
        self._textEditorClass = None
        
        # create opened files explorer
        self.mOpenedFileExplorer = _OpenedFileExplorer(self)
        lefttb = mainWindow.dockToolBar( Qt.LeftToolBarArea )
        lefttb.addDockWidget( self.mOpenedFileExplorer,
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
        
        # document area
        self.layout().setContentsMargins(0, 0, 0, 0)  # FIXME doesn't work
        self.layout().setSpacing(0)
        self.layout().setMargin(0)
        
        self.currentChanged.connect(self._onStackedLayoutIndexChanged)
        
        """TODO
        # creaet file watcher
        self.mFileWatcher = QFileSystemWatcher( self )
        self.mContentChangedTimer = QTimer( self )
        
        # load settings
        self.loadSettings()

        # connections
        mViewModesGroup.triggered.connect(self.viewModes_triggered)
        parent.urlsDropped.connect(self.internal_urlsDropped)
        MonkeyCore.projectsManager().currentProjectChanged.connect(self.internal_currentProjectChanged)
        self.mContentChangedTimer.timeout.connect(self.contentChangedTimer_timeout)
    """
        mainWindow.menuBar().action( "mFile/aOpen" ).triggered.connect(self._fileOpen_triggered)
        mainWindow.menuBar().action( "mFile/aReload" ).triggered.connect(self._fileReload_triggered)
        mainWindow.menuBar().action( "mFile/mClose/aCurrent" ).triggered.connect(self._closeCurrentDocument)
    
        mainWindow.menuBar().action( "mFile/mSave/aCurrent" ).triggered.connect(self._fileSaveCurrent_triggered)
        mainWindow.menuBar().action( "mFile/mSave/aAll" ).triggered.connect(self._fileSaveAll_triggered)
        
        mainWindow.menuBar().action( "mView/aNext" ).triggered.connect(self._activateNextDocument)
        mainWindow.menuBar().action( "mView/aPrevious" ).triggered.connect(self._activatePreviousDocument)
        
        mainWindow.menuBar().action( "mView/aFocusCurrentDocument" ).triggered.connect(self.focusCurrentDocument)
        
    def setTextEditorClass(self, newEditor):
        """Set text editor, which is used for open textual documents.
        New editor would be used for newly opened textual documents.
        
        newEditor is class, herited from :class:AbstractDocument 
        """
        self._textEditorClass = newEditor
    
    def eventFilter( self, object, event ):
        """NOT AN API function
        
        Handler for QObject events of children
        """
        if  object.isWidgetType() :
            document = object
            if  event.type() == QEvent.Close:
                event.ignore()
                self.closeDocument( document )
                return True
        
        return QFrame.eventFilter( self, object, event )
    
    def _onStackedLayoutIndexChanged(self, index):
        """Handler of change of current document in the stacked layout.
        Only calls _onCurrentDocumentChanged(document)
        """
        document = self.widget(index)
        self._onCurrentDocumentChanged(document)
    
    def _onCurrentDocumentChanged( self, document ):
        """Connect/disconnect document signals and update enabled/disabled 
        state of the actions
        """
        
        if document is None and self.count():  # just lost focus, no real change
            return
        if document == self._oldCurrentDocument:  # just recieved focus, no real change
            return
        
        if document is not None:
            self.setFocusProxy(document)
        
        if self._oldCurrentDocument is not None:
            pass
        
        if document is not None:
            mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled(document.isModified())
            mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled( document.isModified() )
        else:  # no document
            mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled(False)

        '''
        # fix fucking flickering due to window activation change on application gain / lost focus.
        if  not document and self.currentDocument() :
            return

        # get document
        editor = None
        if document:
            editor = document.editor()
        
        modified = False
        print_ = False
        
        if document:
            modified = document.isModified()
            print_ = document.isPrintAvailable()
        '''
        
        # update file menu
        mks.monkeycore.menuBar().action( "mFile/mSave/aAll" ).setEnabled( document is not None)
        mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled( document is not None)
        mks.monkeycore.menuBar().action( "mView/aFocusCurrentDocument" ).setEnabled( document is not None)
        '''
        mks.monkeycore.menuBar().action( "mFile/mClose/aAll" ).setEnabled( document )
        '''
        mks.monkeycore.menuBar().action( "mFile/aReload" ).setEnabled( document is not None )
        '''
        mks.monkeycore.menuBar().action( "mFile/aSaveAsBackup" ).setEnabled( document )
        mks.monkeycore.menuBar().action( "mFile/aQuickPrint" ).setEnabled( print_ )
        mks.monkeycore.menuBar().action( "mFile/aPrint" ).setEnabled( print_ )
        
        # update edit menu
        mks.monkeycore.menuBar().action( "mEdit/aExpandAbbreviation" ).setEnabled( document )
        mks.monkeycore.menuBar().setMenuEnabled( mks.monkeycore.menuBar().menu( "mEdit/mAllCommands" ), editor )
        '''
        
        # update view menu
        moreThanOneDocument = self.count() > 1
        mks.monkeycore.menuBar().action( "mView/aNext" ).setEnabled( moreThanOneDocument )
        mks.monkeycore.menuBar().action( "mView/aPrevious" ).setEnabled( moreThanOneDocument )
        
        # internal update
        if  document and document.filePath():
            try:
                os.chdir( os.path.dirname(document.filePath()) )
            except OSError, ex:  # directory might be deleted
                print >> sys.stderr, 'Failed to change directory:', str(ex)
        
        self.currentDocumentChanged.emit(self._oldCurrentDocument, document)
        self._oldCurrentDocument = document
    
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
            
    def fileWatcher(self):
        return self.mFileWatcher    
    '''
    
    def setCurrentDocument( self, document ):
        """Select active (focused and visible) document form list of opened documents
        """
        self.setCurrentWidget( document )
    
    def currentDocument(self):
        """Returns currently active (focused) document.
        """
        return self.currentWidget()
    
    def goToLine(self, filePath, line, column, encoding, selectionLength):
        for document in self.openedDocuments():
            if os.path.realpath(document.filePath()) == \
               os.path.realpath(filePath):
                self.setCurrentDocument(document)
                break
        else:
            document = self.openFile(filePath)  # document = self.openFile( filePath, encoding )

        if  document :
            document.goTo(line, column, selectionLength )
    
    def closeDocument( self, document, showDialog = True):
        """Close opened file, remove document from workspace and delete the widget"""
        
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
        if len(self._sortedDocuments) > 1:  # not the last document
            if document == self._sortedDocuments[-1]:  # the last document
                self._activatePreviousDocument()
            else:  # not the last
                self._activateNextDocument()
        
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
        document.fileClosed.connect(self.document_fileClosed)
        document.fileReloaded.connect(self.document_fileReloaded)
        """
        # update file menu
        document.modifiedChanged.connect(mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled)
        
        # add to workspace
        document.installEventFilter( self )
        
        self.addWidget( document )
        self.setCurrentWidget( document )
    
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

        # remove from workspace
        document.removeEventFilter( self )
        self.removeWidget(document)
        
    def openFile(self, filePath, encoding=''):
        """Open named file using suitable plugin, or textual editor, if other suitable editor not found.
        
        Returns document, if opened, None otherwise
        
        Opens modal dialog, if failed to open the file
        """
        
        # check if file is already opened
        for document in self._sortedDocuments:
            if os.path.isfile(filePath) and \
               os.path.isfile(document.filePath()) and \
               os.path.samefile( document.filePath(), filePath ) :
                    self.setCurrentDocument( document )
                    return document
        
        """TODO
        # get a document interface that can handle the file
        document = mks.monkeycore.pluginsManager().documentForFileName( filePath )
        """
        documentType = None
        
        # open it with textual editor
        if not documentType :
            documentType = self._textEditorClass
        
        if not documentType:
            QMessageBox.critical(None,
                                 self.tr("Failed to open file"),
                                 self.tr("Don't have any editor for open %s. Is any text editor plugin enabled?" % filePath))
            return None
        
        # open file
        try:
            QApplication.setOverrideCursor( Qt.WaitCursor )
            document = documentType(self, filePath)
        except IOError, ex:
            #TODO replace with messageManager ?
            QMessageBox.critical(None,
                                 self.tr("Failed to open file"),
                                 unicode(str(ex), 'utf8'))
            return None
        finally:
            QApplication.restoreOverrideCursor()
        
        self.documentOpened.emit( document )
        
        self._handleDocument( document )
        
        return document
    
    """TODO
    def closeFile(self, filePath ):
        for window in a.subWindowList():
            if  mks.monkeystudio.isSameFile( window.filePath(), h ) :
                self.closeDocument( window )
                return
    """
    
    def _closeCurrentDocument(self):
        document = self.currentWidget()
        assert(document is not None)
        self.closeDocument( document )
    
    def openedDocuments(self):
        """Get list of opened documents (:class:AbstractDocument instances)
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
    
    def _activateNextDocument(self):
        curIndex = self._sortedDocuments.index(self.currentDocument())
        nextIndex = (curIndex + 1) % len(self._sortedDocuments)
        self.setCurrentDocument( self._sortedDocuments[nextIndex] )
    
    def _activatePreviousDocument(self):
        curIndex = self._sortedDocuments.index(self.currentDocument())
        prevIndex = (curIndex - 1 + len(self._sortedDocuments)) % len(self._sortedDocuments)
        self.setCurrentDocument( self._sortedDocuments[prevIndex] )
    
    def focusCurrentDocument(self):
        """Set focus (cursor) to current document.
        Used if user finished work with some dialog, and, probably, want's to edit text
        """
        document = self.currentDocument()

        if  document :
            document.setFocus()
    
    """TODO
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
        return self.openFile( fileName, result[ "encoding" ].toString() )

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
    
    def document_fileClosed(self):
        document = self.sender()
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
    
    def viewModes_triggered(self, action ):
        self.setDocumentMode( action.data().toInt() )
    
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
        fileNames = map(unicode, QFileDialog.getOpenFileNames( self.window(), self.tr( "Choose the file(s) to open" )))
                
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
    '''
    def _fileReload_triggered(self):
        document = self.currentDocument()

        if  document is not None:
            button = QMessageBox.Yes

            if  document.isModified():
                button = QMessageBox.question(self, self.tr( "Reload file..." ), 
                                         self.tr( "The file has been modified, do you want to reload it?" ),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if button == QMessageBox.Yes :
                """ fileName = document.filePath()
                 encoding = document.textCodec()

                self.closeDocument( document )
                self.openFile( fileName, c );"""
                document.reload()
    '''
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

    def editSearch_triggered(self):
        document = self.currentDocument()

        if  document and not document.editor() :
            document.invokeSearch()

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
