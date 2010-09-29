from PyQt4.QtGui import *
from PyQt4.QtCore import *

import mks.monkeycore
import mks.monkeystudio
import mks.openedfileexplorer
import mks.child
import mks.abstractchild

CONTENT_CHANGED_TIME_OUT = 3000
DEFAULT_CONTEXT = "Default"

class pAbstractChild(QMdiSubWindow):
    """TODO
    enum DocumentMode { mNone:, mNa, mInsert, mOverwrite, mReadOnly } mDocument
    enum LayoutMode { lNone:, lNormal, lVertical, lHorizontal } mLayout
    """
    
    def __init__( self, parent = None):
        QMdiSubWindow.__init__( self, parent )
        """TODO
        mCodec:
        setAttribute( Qt.WA_DeleteOnClose )
        mDocument = mNone
        mLayout = lNone
        
        # clear Close shortcut that conflict with menu one on some platform
        menu = systemMenu()
         QKeySequence closeSequence( QKeySequence.Close )
        
        for action in menu.actions():
            if  action.shortcut() == closeSequence :
                action.setShortcut( QKeySequence() )
        """

    '''TODO
    def sizeHint(self):
        """eturn defaultsize for child
        """
        return QSize( 640, 480 )

    def documentMode(self):
        """return child document mode
        """
        return self.mDocument

    def layoutMode(self):
        """return the child layout mode"""
        return self.mLayout
    
    def language(self):
        """return child language
        """
        return QString.null;
    '''
    def setFilePath( self, filePath ):
        """set the file path of the document
        """
        if not filePath:
            self.setWindowFilePath( '' )
            self.setWindowTitle( '' )
        else:
            self.setWindowFilePath( filePath )
            self.setWindowTitle( self.fileName().append( "[*]" ) )
    
    def filePath(self):
        """return the document file path"""
        return self.windowFilePath()
    
    def fileName(self):
        """return the filename of the document"""
        wfp = self.windowFilePath()
        if wfp.isEmpty():
            return None
        else:
            return QFileInfo( wfp ).fileName()
    '''TODO
    def path(self):
        """return the absolute path of the document"""
        wfp = self.windowFilePath()
        if wfp.isEmpty():
            return None
        else:
            return QFileInfo( wfp ).absolutePath()

    def QString fileBuffer(self):
        """return the current buffer of filename"""
        return None
    
    def context(self):
        """return the child context"""
        pass
        
    def initializeContext(self, toolBar ):
        """the context initialization"""
        pass
    
    def cursorPosition(self):
        """return cursor position if available
        """
        pass
    
    def editor(self):
        """the current visible editor
        """
        pass
    '''
    def isModified(self):
        """return the current file modified flag
        """
        pass
    
    '''TODO
    def isUndoAvailable(self):
        """return the current file undo flag
        """
        pass
    
    def isRedoAvailable(self):
        """return the current file redo flag
        """
        pass

    def isCopyAvailable(self):
        """return the current file copy available
        """
        pass
        
    def isPasteAvailable(self):
        """return the current file paste available
        """
        pass

    def isGoToAvailable(self):
        """return is goto is available
        """
        pass

    def isPrintAvailable(self):
        """return if print is available
        """
        pass

    def setDocumentMode(self, documentMode ):
        """set the child document mode"""
        if  self.mDocument == documentMode :
            return
        self.mDocument = documentMode
        self.documentModeChanged.emit( self.mDocument )

    def setLayoutMode(self layoutMode )
        """set the child layout mode
        """
        
        if  self.mLayout == layoutMode :
            return
        self.mLayout = layoutMode
        self.layoutModeChanged.emit( self.mLayout )

    
    def textCodec(self)
    { return mCodec ? mCodec.name() : pMonkeyStudio.defaultCodec();
    
    def codec(self)
    { return mCodec ? mCodec : QTextCodec.codecForName( pMonkeyStudio.defaultCodec().toLocal8Bit().constData() );
    
    def undo(self):
        pass
    
    def redo(self):
        pass
        
    def cut(self):
        pass
    
    def copy(self):
        pass
    
    def paste(self):
        pass
    
    def goTo(self):
        pass
    
    def goTo(self, position, selectionLength = -1 ):
        pass
    
    def invokeSearch(self):
        pass
    
    def saveFile(self):
        pass
    
    def backupFileAs(self fileName ):
        pass
    
    def openFile(self fileName, codec ):
        pass
    
    def closeFile(self):
        pass
    
    def reload(self):
        pass
    
    def printFile(self):
        pass
    
    def quickPrintFile(self):
        pass
        
    '''
    fileOpened = pyqtSignal()
    fileClosed = pyqtSignal()
    # when.emit a file is reloaded
    fileReloaded = pyqtSignal()
    # when.emit the content changed
    contentChanged = pyqtSignal()
    # when.emit the child layout mode has changed
    layoutModeChanged = pyqtSignal()
    # when.emit the child document mode has changed
    documentModeChanged = pyqtSignal()
    # when.emit cursor position changed
    cursorPositionChanged = pyqtSignal(QPoint)
    # when.emit a file is modified
    modifiedChanged = pyqtSignal(bool)
    # when.emit undo has changed
    undoAvailableChanged = pyqtSignal(bool)
    # when.emit undo has changed
    redoAvailableChanged = pyqtSignal(bool)
    # when.emit a file paste available change
    pasteAvailableChanged = pyqtSignal(bool)
    # when.emit a file copy available change
    copyAvailableChanged = pyqtSignal(bool)
    # when.emit search/replace is available
    #searchReplaceAvailableChanged = pyqtSignal(bool)
    # when.emit goto is available
    #goToAvailableChanged = pyqtSignal(bool)
    # when.emit requesting search in editor
    #requestSearchReplace = pyqtSignal()
    # when.emit request go to line
    #requestGoTo = pyqtSignal()
    # when.emit a child require to update workspace
    #updateWorkspaceRequested()


class pWorkspace(QFrame):
    
    NoTabs = "NoTabs"
    TopTabs = "TopTabs"
    BottomTabs = "BottomTabs"
    LeftTabs = "LeftTabs"
    RightTabs = "RightTabs"
    
    # a file has been opened
    documentOpened = pyqtSignal(mks.abstractchild.pAbstractChild)
    # a file have changed
    documentChanged = pyqtSignal(mks.abstractchild.pAbstractChild)
    # a file modified state changed
    documentModifiedChanged = pyqtSignal(mks.abstractchild.pAbstractChild, bool)
    # document about to close
    documentAboutToClose = pyqtSignal(mks.abstractchild.pAbstractChild)
    # a file has been closed
    documentClosed = pyqtSignal(mks.abstractchild.pAbstractChild)
    # a file has been reloaded
    documentReloaded = pyqtSignal(mks.abstractchild.pAbstractChild)
    # current file changed
    currentDocumentChanged = pyqtSignal(mks.abstractchild.pAbstractChild)
    
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        
        """TODO
        self.mViewMode = self.NoTabs
        
        mb = mks.mks.monkeycore.menuBar()

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
        self.mOpenedFileExplorer = mks.openedfileexplorer.pOpenedFileExplorer( self )
        
        # layout
        self.mLayout = QVBoxLayout( self )
        self.mLayout.setMargin( 0 )
        self.mLayout.setSpacing( 0 )

        # multitoolbar
        hline = QFrame( self )
        hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )
        
        # document area
        self.mdiArea = QMdiArea( self )
        self.mdiArea.setActivationOrder( QMdiArea.CreationOrder )
        self.mdiArea.setDocumentMode( True )

        # add widgets to layout
        """TODO
        self.mLayout.addWidget( mks.mks.monkeycore.multiToolBar() )
        """
        
        self.mLayout.addWidget( hline )
        self.mLayout.addWidget( self.mdiArea )
        
        """TODO
        # creaet file watcher
        self.mFileWatcher = QFileSystemWatcher( self )
        """
        self.mContentChangedTimer = QTimer( self )
        
        """TODO
        # load settings
        self.loadSettings()

        # connections
        mViewModesGroup.triggered.connect(self.viewModes_triggered)
        mMdiArea.subWindowActivated.connect(self.mdiArea_subWindowActivated)
        parent.urlsDropped.connect(self.internal_urlsDropped)
        MonkeyCore.projectsManager().currentProjectChanged.connect(self.internal_currentProjectChanged)
        """
        self.mContentChangedTimer.timeout.connect(self.contentChangedTimer_timeout)
        """TODO
        MonkeyCore.multiToolBar().notifyChanges.connect(self.multitoolbar_notifyChanges)
        """

    """TODO
    def eventFilter( self, object, event ):
        # get document
        if  object.isWidgetType() :
            document = object

            if  document and event.type() == QEvent.Close :
                event.ignore()
                self.closeDocument( document )
                return True
    
        return QFrame.eventFilter( object, event )
    """
    """
    def updateGuiState( document ):
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
        
        moreThanOneDocument = self.mdiArea.subWindowList().count() > 1

        # context toolbar
        mtb = mks.mks.monkeycore.multiToolBar()

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

        # update file menu
        mks.mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled( modified )
        mks.mks.monkeycore.menuBar().action( "mFile/mSave/aAll" ).setEnabled( document )
        mks.mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled( document )
        mks.mks.monkeycore.menuBar().action( "mFile/mClose/aAll" ).setEnabled( document )
        mks.mks.monkeycore.menuBar().action( "mFile/aReload" ).setEnabled( document )
        mks.mks.monkeycore.menuBar().action( "mFile/aSaveAsBackup" ).setEnabled( document )
        mks.mks.monkeycore.menuBar().action( "mFile/aQuickPrint" ).setEnabled( print_ )
        mks.mks.monkeycore.menuBar().action( "mFile/aPrint" ).setEnabled( print_ )

        # update edit menu
        mks.mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled( undo )
        mks.mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled( redo )
        mks.mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled( copy )
        mks.mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled( copy )
        mks.mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled( paste )

        mks.mks.monkeycore.menuBar().action( "mEdit/aGoTo" ).setEnabled( go )
        mks.mks.monkeycore.menuBar().action( "mEdit/aExpandAbbreviation" ).setEnabled( document )
        mks.mks.monkeycore.menuBar().setMenuEnabled( mks.mks.monkeycore.menuBar().menu( "mEdit/mAllCommands" ), editor )
        mks.mks.monkeycore.menuBar().setMenuEnabled( mks.mks.monkeycore.menuBar().menu( "mEdit/mBookmarks" ), editor )

        # update view menu
        mks.mks.monkeycore.menuBar().action( "mView/aNext" ).setEnabled( moreThanOneDocument )
        mks.mks.monkeycore.menuBar().action( "mView/aPrevious" ).setEnabled( moreThanOneDocument )

        # update status bar
        mks.mks.monkeycore.statusBar().setModified( modified )
        if editor:
            mks.mks.monkeycore.statusBar().setEOLMode( editor.eolMode() )
            mks.mks.monkeycore.statusBar().setIndentMode( editor.indentationsUseTabs())
            mks.mks.monkeycore.statusBar().setCursorPosition( document.cursorPosition())
        
            mks.mks.monkeycore.statusBar().setEOLMode( editor.eolMode())
            mks.mks.monkeycore.statusBar().setIndentMode( editor.indentationsUseTabs())
            mks.mks.monkeycore.statusBar().setCursorPosition( document.cursorPosition())
        
        # internal update
        if  document :
            QDir.setCurrent( document.path() )
    """
    """
    def defaultContext(self):
        return DEFAULT_CONTEXT
    """
    
    """
    def loadSettings(self):
        # restore tabs settings
        tabBar().setTabsHaveCloseButton( tabsHaveCloseButton() )
        tabBar().setTabsHaveShortcut( tabsHaveShortcut() )
        tabBar().setTabsElided( tabsElided() )
        tabBar().setTabsColor( tabsTextColor() )
        tabBar().setCurrentTabColor( currentTabTextColor() )
        self.mOpenedFileExplorer.setSortMode( mks.monkeystudio.openedFileSortingMode() )
        self.setDocumentMode( mks.monkeystudio.documentMode() )
        mtb = mks.mks.monkeycore.multiToolBar()

        for context in mtb.contexts():
            tb = mtb.toolBar( context )
            self.initMultiToolBar( tb )
        
        self.multitoolbar_notifyChanges()
    """
    
    """TODO
    def initMultiToolBar( self, tb ):
        if  mks.monkeystudio.showQuickFileAccess() :
            tb.insertAction( tb.actions().value( 0 ), mks.mks.monkeycore.workspace().dockWidget().comboBoxAction() )
        else:
            tb.removeAction( mks.mks.monkeycore.workspace().dockWidget().comboBoxAction() )
    """
    def dockWidget(self):
        return self.mOpenedFileExplorer
    """TODO
    def fileWatcher(self):
        return self.mFileWatcher
    
    """
    
    def document( index ):
        window = self.mdiArea.subWindowList().value( index )
        return window

    def indexOfDocument( self, document ):
        return self.mdiArea.subWindowList().indexOf( document )

    def documents(self):
        return self.mdiArea.subWindowList()
    
    def setCurrentDocument( self, document ):
        if  self.currentDocument() != document :
            self.mdiArea.setActiveSubWindow( document )
    
    def currentDocument(self):
        return self.mdiArea.currentSubWindow()

    def goToLine(  self, fileName,  pos,  codec, selectionLength ):
        for window in self.mdiArea.subWindowList():
            if  mks.monkeystudio.isSameFile( window.filePath(), fileName ) :
                self.setCurrentDocument( window )
                document.goTo( pos, selectionLength )
                return

        document = self.openFile( fileName, codec )

        if  document :
            document.goTo( pos, selectionLength )

    def closeDocument( self, document, showDialog ):
        if  showDialog and UISaveFiles.saveDocument( self.window(), document, False ) == UISaveFiles.bCancelClose :
            return
        
        # stop watching files
        file = document.filePath()

        if  QFileInfo( file ).isFile() and self.mFileWatcher.files().contains( file ) :
            self.mFileWatcher.removePath( file )

        # close document
        documentAboutToClose.emit(document)
        document.closeFile()
        
        if  document.testAttribute( Qt.WA_DeleteOnClose ) :
            document.deleteLater()
        else:
            self.unhandleDocument( document )

    def documentMode(self):
        return self.mViewMode
    

    def handleDocument( self, document ):
        # init document connections
        document.fileOpened.connect(self.document_fileOpened)
        document.contentChanged.connect(self.document_contentChanged)
        document.modifiedChanged.connect(self.document_modifiedChanged)
        document.fileClosed.connect(self.document_fileClosed)
        document.fileReloaded.connect(self.document_fileReloaded)
        # update file menu
        document.modifiedChanged.connect(mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled)
        # update edit menu
        document.undoAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aUndo" ).setEnabled)
        document.redoAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aRedo" ).setEnabled)
        document.copyAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aCut" ).setEnabled)
        document.copyAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aCopy" ).setEnabled)
        document.pasteAvailableChanged.connect(mks.monkeycore.menuBar().action( "mEdit/aPaste" ).setEnabled)
        """TODO
        # update status bar
        document.cursorPositionChanged.connect(mks.monkeycore.statusBar().setCursorPosition)
        document.modifiedChanged.connect(mks.monkeycore.statusBar().setModified)
        """
        # add to workspace
        document.installEventFilter( self )
        
        self.mdiArea.blockSignals( True )
        self.mdiArea.addSubWindow( document )
        self.mdiArea.blockSignals( False )

    """TODO
    def unhandleDocument( self, document ):
        maximized = document.isMaximized()
        # init document connections
        disconnect( document, SIGNAL( fileOpened() ), this, SLOT( document_fileOpened() ) )
        disconnect( document, SIGNAL( contentChanged() ), this, SLOT( document_contentChanged() ) )
        disconnect( document, SIGNAL( modifiedChanged( bool ) ), this, SLOT( document_modifiedChanged( bool ) ) )
        disconnect( document, SIGNAL( fileClosed() ), this, SLOT( document_fileClosed() ) )
        disconnect( document, SIGNAL( fileReloaded() ), this, SLOT( document_fileReloaded() ) )
        # update file menu
        disconnect( document, SIGNAL( modifiedChanged( bool ) ), mks.mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ), SLOT( setEnabled( bool ) ) )
        # update edit menu
        disconnect( document, SIGNAL( undoAvailableChanged( bool ) ), mks.mks.monkeycore.menuBar().action( "mEdit/aUndo" ), SLOT( setEnabled( bool ) ) )
        disconnect( document, SIGNAL( redoAvailableChanged( bool ) ), mks.mks.monkeycore.menuBar().action( "mEdit/aRedo" ), SLOT( setEnabled( bool ) ) )
        disconnect( document, SIGNAL( copyAvailableChanged( bool ) ), mks.mks.monkeycore.menuBar().action( "mEdit/aCut" ), SLOT( setEnabled( bool ) ) )
        disconnect( document, SIGNAL( copyAvailableChanged( bool ) ), mks.mks.monkeycore.menuBar().action( "mEdit/aCopy" ), SLOT( setEnabled( bool ) ) )
        disconnect( document, SIGNAL( pasteAvailableChanged( bool ) ), mks.mks.monkeycore.menuBar().action( "mEdit/aPaste" ), SLOT( setEnabled( bool ) ) )
        # update status bar
        disconnect( document, SIGNAL( cursorPositionChanged(  QPoint& ) ), mks.mks.monkeycore.statusBar(), SLOT( setCursorPosition(  QPoint& ) ) )
        disconnect( document, SIGNAL( modifiedChanged( bool ) ), mks.mks.monkeycore.statusBar(), SLOT( setModified( bool ) ) )
        # remove from workspace
        document.removeEventFilter( self )
        self.mdiArea.removeSubWindow( document )
        document.hide()

        # maximize current window if needed
        if  maximized :
            if  self.currentDocument() :
                self.currentDocument().showMaximized()
    """
    def openFile(self, fileName, codec = ''):
        # if it not exists
        if  not QFile.exists( fileName ) or not QFileInfo( fileName ).isFile() :
            return 0
        
        # check if file is already opened
        for window in self.mdiArea.subWindowList():
            document = window

            if  mks.monkeystudio.isSameFile( document.filePath(), fileName ) :
                self.setCurrentDocument( document )
                return document
        
        """TODO
        # get a document interface that can handle the file
        document = mks.mks.monkeycore.pluginsManager().documentForFileName( fileName )
        """
        document = None
        
        # open it with pChild instance if no document
        if  not document :
            document = mks.child.pChild()
        
        # make connection if worksapce don t contains self document
        if not document in self.mdiArea.subWindowList():
            self.handleDocument( document )
        
        # open file
        if  not document.openFile( fileName, codec ) :
            mks.mks.monkeycore.messageManager().appendMessage(self.tr( "An error occur while opening self file: '%1'" ).arg( QFileInfo( fileName ).fileName() ) )
            self.closeDocument( document )
            return 0

        document.showMaximized()
        self.mdiArea.setActiveSubWindow( document )

        # update gui state
        #updateGuiState( document )

        # return child instance
        return document
    """
    def closeFile(self, filePath ):
        for window in a.subWindowList():
            if  mks.monkeystudio.isSameFile( window.filePath(), h ) :
                self.closeDocument( window )
                return

    def closeCurrentDocument(self):
        document = self.currentDocument()

        if  document :
            self.closeDocument( document )
    
    def closeAllDocuments(self):
        # try save documents
        button = UISaveFiles.saveDocuments( window(), s(), e )

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

    def activateNextDocument(self):
        if self.mViewMode == self.NoTabs :
            document = self.currentDocument()
            curIndex = self.mOpenedFileExplorer.model().index( document )
            index = self.mOpenedFileExplorer.model().index( document )
            
            x = curIndex.sibling( curIndex.row() +1, x.column() )

            if  not index.isValid() :
                x = curIndex.sibling( 0, x.column() )

            t = self.mOpenedFileExplorer.model().document( index )
            
            self.setCurrentDocument( document )
        else:
            self.mdiArea.activateNextSubWindow()


    def activatePreviousDocument(self):
        if self.mViewMode == self.NoTabs :
            document = self.currentDocument()
            curIndex = self.mOpenedFileExplorer.model().index( document )
            index = self.mOpenedFileExplorer.model().index( document )

            x = curIndex.sibling( curIndex.row() -1, x.column() )

            if  not index.isValid() :
                x = curIndex.sibling( self.mOpenedFileExplorer.model().rowCount() -1, x.column() )

            t = self.mOpenedFileExplorer.model().document( index )
            self.setCurrentDocument( document )
        else:
            self.mdiArea.activatePreviousSubWindow()
    
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
            mks.mks.monkeycore.messageManager().appendMessage(self.tr( "Can't create file '%1'" ).arg( QFileInfo( fileName ).fileName() ) )
            return 0

        # reset file
        file.resize( 0 )
        file.close()

        if  result.value( "addtoproject", e ).toBool() :
            # add files to scope
            mks.mks.monkeycore.projectsManager().addFilesToScope( result[ "scope" ].value(XUPItem), [fileName] )
        
        # open file
        return self.openFile( fileName, result[ "codec" ].toString() )

    """
    def document_fileOpened(self):
        document = self.sender() # signal sender
        """TODO
        if  QFileInfo( document.filePath() ).isFile() and not self.mFileWatcher.files().contains( document.filePath() ) :
            self.mFileWatcher.addPath( document.filePath() )
        """
        self.documentOpened.emit( document )
    

    def document_contentChanged(self):
        self.mContentChangedTimer.start( CONTENT_CHANGED_TIME_OUT )
        document = self.sender() # signal sender

        # externally deleted files make the filewatcher to no longer watch them
        path = document.filePath()
        
        self.documentChanged.emit( document )


    def document_modifiedChanged(self, modified ):
        document = self.sender()
        self.documentModifiedChanged.emit( document, modified )


    def document_fileClosed(self):
        document = self.sender()
        mtb = mks.mks.monkeycore.multiToolBar()

        mtb.removeContext( document.context(), e )
        self.documentClosed.emit( document )


    def document_fileReloaded(self):
        document = self.sender()
        self.documentReloaded.emit( document )

    def contentChangedTimer_timeout(self):
        self.mContentChangedTimer.stop()
        mks.monkeycore.fileManager().computeModifiedBuffers()
    """TODO

    def multitoolbar_notifyChanges(self):
        mtb = mks.mks.monkeycore.multiToolBar()
        tb = mtb.currentToolBar()
        show = tb and not tb.actions().isEmpty()

        mtb.setVisible( show )

    def viewModes_triggered(self, action ):
        self.setDocumentMode( action.data().toInt() )

    def self.mdiArea_subWindowActivated(self, document ):

        # update gui state
        self.updateGuiState( document )

        # emit file changed
        self.currentDocumentChanged.emit( document )


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
                    mks.mks.monkeycore.projectsManager().openProject( url.toLocalFile(), c() )


    def internal_currentProjectChanged(self, currentProject, previousProject ):
        # uninstall old commands
        if  previousProject :
            previousProject.uninstallCommands()
            disconnect( previousProject, L( installCommandRequested(  pCommand&, & ) ), s, T( internal_projectInstallCommandRequested(  pCommand&, & ) ) )
            disconnect( previousProject, L( uninstallCommandRequested(  pCommand&, & ) ), s, T( internal_projectUninstallCommandRequested(  pCommand&, & ) ) )
    
        # get pluginsmanager
        pm = mks.mks.monkeycore.pluginsManager()
        
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
        mks.mks.monkeycore.mainWindow().menu_CustomAction_aboutToShow()


    def internal_projectInstallCommandRequested(self, cmd, mnu ):
        # create action
        action = mks.mks.monkeycore.menuBar().action( QString( "%1/%2" ).arg( mnu ).arg( cmd.text() ) , d.text() )
        action.setStatusTip( cmd.text() )

        # set action custom data contain the command to execute
        action.setData( QVariant.fromValue( cmd ) )
        
        # connect to signal
        action.triggered().connect(s.internal_projectCustomActionTriggered())
        
        # update menu visibility
        mks.mks.monkeycore.mainWindow().menu_CustomAction_aboutToShow()


    def internal_projectUninstallCommandRequested(self, cmd, mnu ):
        menu = mks.mks.monkeycore.menuBar().menu( mnu )
        
        for action in u.actions():
            if  action.menu() :
                internal_projectUninstallCommandRequested( cmd, QString( "%1/%2" ).arg( mnu ).arg( action.menu().objectName() ) )
            elif  not action.isSeparator() and action.data().value(pCommand) == cmd :
                delete action

        # update menu visibility
        mks.mks.monkeycore.mainWindow().menu_CustomAction_aboutToShow()

    def internal_projectCustomActionTriggered(self):
        action = self.sender()

        if  action :
            cm = mks.mks.monkeycore.consoleManager()
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
    
    def fileOpen_triggered(self):
        #mFilters = mks.monkeystudio.availableFilesFilters() # get available filters
        mFilters = ''
        
        # show filedialog to user
        """TODO
        result = MkSFileDialog.getOpenFileNames( window(), tr( "Choose the file(s) to open" ), QDir.currentPath(), mFilters, True, False )
        
        # open open file dialog
        fileNames = result[ "filenames" ].toStringList()
        """
        fileNames = QFileDialog.getOpenFileNames( self.window(), self.tr( "Choose the file(s) to open" ), QDir.currentPath(), mFilters)
        
        # return 0 if user cancel
        if  fileNames.isEmpty() :
            return
        
        """
        # for each entry, file
        for file in fileNames:
            if  self.openFile( file, result[ "codec" ].toString() ) :
                # append file to recents
                mks.mks.monkeycore.recentsManager().addRecentFile( file )

            else:
                # remove it from recents files
                mks.mks.monkeycore.recentsManager().removeRecentFile( file )
        """
        for file in fileNames:
            self.openFile( file )
    
    """TODO
    def fileSessionSave_triggered(self):
        files = []
        projects = []

        # files
        for window in self.mdiArea.subWindowList():
            document = window
            files.append(document.filePath())

        mks.mks.monkeycore.settings().setValue( "Session/Files", files )
        
        # projects
        for project in mks.mks.monkeycore.projectsManager().topLevelProjects():
            projects.append(project.fileName())

        mks.mks.monkeycore.settings().setValue( "Session/Projects", projectss )

    def fileSessionRestore_triggered(self):
        # restore files
        for file in mks.mks.monkeycore.settings().value("Session/Files", [] ).toStringList():
            if not self.openFile( file, mks.monkeystudio.defaultCodec() ): # remove it from recents files
                mks.mks.monkeycore.recentsManager().removeRecentFile( file )
        
        # restore projects
        for project in mks.mks.monkeycore.settings().value( "Session/Projects", [] ).toStringList():
            if not mks.mks.monkeycore.projectsManager().openProject( project, mks.monkeystudio.defaultCodec() ): # remove it from recents projects
                mks.mks.monkeycore.recentsManager().removeRecentProject( project )

    def fileSaveCurrent_triggered(self):
        document = self.currentDocument()

        if  document :
            fn = document.filePath()
            self.mFileWatcher.removePath( fn )
            document.saveFile()
            self.mFileWatcher.addPath( fn )

    def fileSaveAll_triggered(self):
        for window in a.subWindowList():
            document = window
            fn = document.filePath()
            self.mFileWatcher.removePath( fn )
            document.saveFile()
            self.mFileWatcher.addPath( fn )


    def fileCloseCurrent_triggered(self):
       self.closeCurrentDocument()


    def fileCloseAll_triggered(self):
        self.closeAllDocuments()


    def fileReload_triggered(self):
        document = self.currentDocument()

        if  document :
            button = QMessageBox.Yes

            if  document.isModified() :
                n = QMessageBox.question( self, self.tr( "Confirmation needed..." ), self.tr( "The file has been modified, anyway ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No )

            if button == QMessageBox.Yes :
                ''' fileName = document.filePath()
                 codec = document.textCodec()

                self.closeDocument( document )
                self.openFile( fileName, c );'''
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
        locale = TranslationDialog.getLocale( mks.mks.monkeycore.translationsManager(), self )

        if  not locale.isEmpty() :
            mks.mks.monkeycore.settings().setValue( "Translations/Locale", locale )
            mks.mks.monkeycore.settings().setValue( "Translations/Accepted", True )
            mks.mks.monkeycore.translationsManager().setCurrentLocale( locale )
            mks.mks.monkeycore.translationsManager().reloadTranslations()


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
            mks.mks.monkeycore.abbreviationsManager().expandMacro( document.editor() )



    def editPrepareAPIs_triggered(self):
        mks.monkeystudio.prepareAPIs()

    # help menu
    def helpAboutApplication_triggered(self):
        dlg = UIAbout( self )
        dlg.open()
    """

    def helpAboutQt_triggered(self):
        # FIXME move to main window
        qApp.aboutQt()
