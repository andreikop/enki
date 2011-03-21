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
import sys

from PyQt4 import uic

from PyQt4.QtGui import QApplication, \
                        QDialog, QDialogButtonBox, \
                        QFileDialog, QFrame, \
                        QIcon, QKeySequence,  \
                        QListWidgetItem, \
                        QMessageBox, \
                        QStackedWidget, QTreeView, \
                        QVBoxLayout, QWidget
from PyQt4.QtCore import pyqtSignal, \
                         QByteArray, \
                         QEvent, QFileSystemWatcher,\
                         Qt, \
                         QTimer

import PyQt4.fresh

from mks.monkeycore import core, DATA_FILES_PATH
import mks._openedfilesmodel

"""
CONTENT_CHANGED_TIME_OUT = 3000
DEFAULT_CONTEXT = "Default"
"""

class AbstractDocument(QWidget):
    """Base class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant, ...
    Inherit this class, if you want to create new document type
    
    This class may requre redesign, if we need to add support for non-textual or non-unicode editor.
    DO redesign instead of do dirty hacks
    """
    
    modifiedChanged = pyqtSignal(bool)
    """
    modifiedChanged(modified)
    
    **Signal** emitted, when modified state changed (file edited, or saved)
    Bool parameter contains new value
    """
    
    #Signal emitted, when document icon or toolTip has changed 
    #(i.e. document has been modified externally)
    _documentDataChanged = pyqtSignal()
    
    
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
        self._externallyRemoved = False
        self._externallyModified = False
        
        """TODO
        mCodec:
        setAttribute( Qt.WA_DeleteOnClose )
        mDocument = mNone
        mLayout = lNone
        """
        # File opening should be implemented in the document classes
    
    def _readFile(self, filePath):
        """Read the file contents.
        Shows QMessageBox for UnicodeDecodeError, but raises IOError, if failed to read file
        """
        with open(filePath, 'r') as f:  # Exception is ok, raise it up
            self._filePath = os.path.abspath(filePath)  # TODO remember fd?
            data = f.read()                
        
        try:
            text = unicode(data, 'utf8')  # FIXME replace 'utf8' with encoding
        except UnicodeDecodeError, ex:
            QMessageBox.critical(None,
                                 self.tr("Can not decode file"),
                                 filePath + '\n' +
                                 unicode(str(ex), 'utf8') + 
                                 '\nProbably invalid encoding was set. ' +
                                 'You may corrupt your file, if saved it')
            text = unicode(data, 'utf8', 'ignore')  # FIXME replace 'utf8' with encoding            
        return text

    def _isExternallyRemoved(self):
        """Check if document's file has been deleted externally.
        This method DOES NOT do any file system access, but only returns cached info
        """
        return self._externallyRemoved
        
    def _setExternallyRemoved(self, flag):
        """Set externallyDeleted flag, update model
        """
        self._externallyRemoved = flag
        self._documentDataChanged.emit()
    
    def _isExternallyModified(self):
        """Check if document's file has been modified externally.
        This method DOES NOT do any file system access, but only returns cached info
        """
        return self._externallyModified
    
    def _setExternallyModified(self, flag):
        """Set externallyModified flag, update model
        """
        self._externallyModified = flag
        self._documentDataChanged.emit()
    
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
        """Returns True, if file is modified
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
        """Save the file to file system
        """
        if  not self.isModified() and \
            not self._isExternallyModified() and \
            not self._isExternallyRemoved():
                return True
        
        dirPath = os.path.dirname(self.filePath())
        if  not os.path.exists(dirPath):
            try:
                os.mkdir(dirPath)
            except OSError:
                core.messageManager().appendMessage( \
                        self.tr( "Cannot create directory '%s'. Error '%s'" % (dirPath, error))) # todo fix
                return False
        
        try:
            f = open(self.filePath(), 'w')
        except IOError, ex:
            QMessageBox.critical(None,
                                 self.tr("Can not write to file"),
                                 unicode(str(ex), 'utf8'))
            return False
        
        try:
            f.write(unicode(self.text()).encode('utf8'))  # FIXME codec hardcoded
        finally:
            f.close()
        
        self._externallyRemoved = False
        self._externallyModified = False
    
    def text(self):
        """Contents of the editor.
        """
        pass
    
    def setText(self, text):
        """Set contents in the editor.
        Usually this method is called only internally by openFile()
        """
        pass
    
    '''TODO
    def backupFileAs(self fileName ):
        pass
    
    def closeFile(self):
        pass
    '''
    def reload(self):
        """Reload the file from the disk
        
        If child class reimplemented this method, it MUST call method of the parent class
        for update internal bookkeeping"""

        text = self._readFile(self.filePath())
        self.setText(text)
        #self.fileReloaded.emit()
        self._externallyModified = False
        self._externallyRemoved = False
    
    '''
    def printFile(self):
        pass
    
    def quickPrintFile(self):
        pass
    '''
    
    def modelToolTip(self):
        """Tool tip for the opened files model
        """
        toolTip = self.filePath()
        
        if self.isModified():
            toolTip += "<br/><font color='blue'>%s</font>" % self.tr("Locally Modified")
        if  self._isExternallyModified():
            toolTip += "<br/><font color='red'>%s</font>" % self.tr("Externally Modified")
        if  self._isExternallyRemoved():
            toolTip += "<br/><font color='red'>%s</font>" % self.tr( "Externally Deleted" )
        return toolTip
    
    def modelIcon(self):
        """Icon for the opened files model
        """
        if   self._isExternallyRemoved()  and self._isExternallyModified():  icon = "modified-externally-deleted.png"
        elif self._isExternallyRemoved():                                    icon = "deleted.png"
        elif self._isExternallyModified() and self.isModified():             icon = "modified-externally-modified.png"
        elif self._isExternallyModified():                                   icon = "modified-externally.png"
        elif self.isModified():                                              icon = "save.png"
        else:                                                                icon = "transparent.png"
        return QIcon(":/mksicons/" + icon)
    '''
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

class _UISaveFiles(QDialog):
    """Save files dialog.
    Shows checkable list of not saved files.
    """
    def __init__(self, workspace, documents):
        super(type(self), self).__init__(workspace)
        self.cancelled = False
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/SaveFiles.ui'), self)
        self.buttonBox.clicked.connect(self._onButtonClicked)
        
        self._itemToDocument = {}
        for document in documents:
            item = QListWidgetItem( document.fileName(), self.listWidget )
            item.setToolTip( document.filePath() )
            item.setCheckState( Qt.Checked )
            self._itemToDocument[item] = document                
    
    def _onButtonClicked(self, button):
        """Button click handler.
        Saves files, if necessary, accepts or rejects dialog
        """
        stButtton = self.buttonBox.standardButton(button)
        if stButtton == QDialogButtonBox.Save:
            for i in range(self.listWidget.count()):
                if  self.listWidget.item( i ).checkState() != Qt.Unchecked:
                    self._itemToDocument[self.listWidget.item(i)].saveFile()
            self.accept()
        elif stButtton == QDialogButtonBox.Cancel:
            self.reject()
        elif stButtton == QDialogButtonBox.Discard:
            self.accept()
        else:
            assert 0

class Workspace(QStackedWidget):
    """
    Class manages set of opened documents, allows to open new file
    
    Instance accessible as: ::
    
        core.workspace()
    
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
        List accessed and modified by mks._openedfilesmodel.OpenedFileModel class
        """
        self._sortedDocuments = []
        self._oldCurrentDocument = None
        self._textEditorClass = None
        
        # create opened files explorer
        self._openedFileExplorer = mks._openedfilesmodel.OpenedFileExplorer(self)
        lefttb = mainWindow.dockToolBar( Qt.LeftToolBarArea )
        lefttb.addDockWidget( self._openedFileExplorer,
                              self._openedFileExplorer.windowTitle(),
                              self._openedFileExplorer.windowIcon())
        
        # create file watcher
        self._fileWatcher = QFileSystemWatcher(self)
        self._fileWatcher.fileChanged.connect(self._onWatcherFileChanged)
        
        # document area
        self.layout().setContentsMargins(0, 0, 0, 0)  # FIXME doesn't work
        self.layout().setSpacing(0)
        self.layout().setMargin(0)
        
        self.currentChanged.connect(self._onStackedLayoutIndexChanged)
        
        """TODO
        self.mContentChangedTimer = QTimer( self )
        
        # load settings
        self.loadSettings()

        # connections
        mViewModesGroup.triggered.connect(self.viewModes_triggered)
        parent.urlsDropped.connect(self.internal_urlsDropped)
        MonkeyCore.projectsManager().currentProjectChanged.connect(self.internal_currentProjectChanged)
        self.mContentChangedTimer.timeout.connect(self.contentChangedTimer_timeout)
    """
        self.currentDocumentChanged.connect(self._updateMainWindowTitle)
        mainWindow.menuBar().action( "mFile/aOpen" ).triggered.connect(self._fileOpen_triggered)
        mainWindow.menuBar().action( "mFile/mReload/aCurrent" ).triggered.connect(self._onFileReloadTriggered)
        mainWindow.menuBar().action( "mFile/mReload/aAll" ).triggered.connect(self._onFileReloadAllTriggered)
        mainWindow.menuBar().action( "mFile/mClose/aCurrent" ).triggered.connect(self._closeCurrentDocument)
    
        mainWindow.menuBar().action( "mFile/mSave/aCurrent" ).triggered.connect(self._fileSaveCurrent_triggered)
        mainWindow.menuBar().action( "mFile/mSave/aAll" ).triggered.connect(self._fileSaveAll_triggered)
        
        mainWindow.menuBar().action( "mView/aNext" ).triggered.connect(self._activateNextDocument)
        mainWindow.menuBar().action( "mView/aPrevious" ).triggered.connect(self._activatePreviousDocument)
        
        mainWindow.menuBar().action( "mView/aFocusCurrentDocument" ).triggered.connect(self.focusCurrentDocument)
        editConfigFile = lambda : self.openFile(core.config().filename)
        mainWindow.menuBar().action( "mEdit/aConfigFile" ).triggered.connect(editConfigFile)
    
    def _mainWindow(self):
        return self.parentWidget().parentWidget()
    
    def documentForPath(self, filePath):
        """Find document by it's file path.
        Raises ValueError, if document hasn't been found
        """
        for document in self.openedDocuments():
            if document.filePath() == filePath:
                return document
        else:
            raise ValueError("Document not found for" + filePath)
    
    def _onWatcherFileChanged(self, filePath):
        """QFileSystemWatcher sent signal, that file has been changed or deleted
        """
        document = self.documentForPath(filePath)
        
        if os.path.exists(filePath):
            document._setExternallyModified(True)
        else:
            document._setExternallyRemoved(True)
        
    def _updateMainWindowTitle(self):
        """Update window title after document or it's modified state has been changed
        """
        document = self.currentDocument()
        if document:
            name = document.fileName()
            if document.isModified():
                name+= '*'
        else:
            name = self._mainWindow().defaultTitle()
        self._mainWindow().setWindowTitle(name)

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
            core.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled(document.isModified())
            core.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled( document.isModified() )
        else:  # no document
            core.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled(False)
        
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
        core.menuBar().action( "mFile/mSave/aAll" ).setEnabled( document is not None)
        core.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled( document is not None)
        core.menuBar().action( "mView/aFocusCurrentDocument" ).setEnabled( document is not None)
        '''
        core.menuBar().action( "mFile/mClose/aAll" ).setEnabled( document )
        '''
        core.menuBar().action( "mFile/mReload/aCurrent" ).setEnabled( document is not None )
        '''
        core.menuBar().action( "mFile/aSaveAsBackup" ).setEnabled( document )
        core.menuBar().action( "mFile/aQuickPrint" ).setEnabled( print_ )
        core.menuBar().action( "mFile/aPrint" ).setEnabled( print_ )
        
        # update edit menu
        core.menuBar().action( "mEdit/aExpandAbbreviation" ).setEnabled( document )
        core.menuBar().setMenuEnabled( core.menuBar().menu( "mEdit/mAllCommands" ), editor )
        '''
        
        # update view menu
        moreThanOneDocument = self.count() > 1
        core.menuBar().action( "mView/aNext" ).setEnabled( moreThanOneDocument )
        core.menuBar().action( "mView/aPrevious" ).setEnabled( moreThanOneDocument )
        
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
        
        if showDialog and document.isModified():
            if _UISaveFiles(self, [document]).exec_() == QDialog.Rejected:
                return
        
        self._fileWatcher.removePath(document.filePath())
        
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
        document.modifiedChanged.connect(core.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled)
        document.modifiedChanged.connect(self._updateMainWindowTitle)
        
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
        document.modifiedChanged.disconnect(core.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled)
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
        document = core.pluginsManager().documentForFileName( filePath )
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
        
        self._fileWatcher.addPath(document.filePath())
        
        self._handleDocument( document )
        
        if not os.access(filePath, os.W_OK):
            core.messageManager().appendMessage( \
                        self.tr( "File '%s' is not writable" % filePath), 4000) # todo fix
        
        return document
    
    def _closeCurrentDocument(self):
        document = self.currentWidget()
        assert(document is not None)
        self.closeDocument( document )
    
    def openedDocuments(self):
        """Get list of opened documents (:class:AbstractDocument instances)
        """
        return self._sortedDocuments
    
    def closeAllDocuments(self):
        """Close all documents
        If there are not saved documents, dialog will be shown.
        Returns True, if all files had been closed, and False, if save dialog rejected
        """
        if any([d.isModified() for d in self.openedDocuments()]):
            if (_UISaveFiles( self, self.openedDocuments()).exec_() != QDialog.Rejected):
                for document in self.openedDocuments():
                    self.closeDocument(document, False)
            else:
                return False; #not close IDE
        return True
        
    
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
    
    """
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
            core.messageManager().appendMessage(self.tr( "Can't create file '%1'" ).arg( QFileInfo( fileName ).fileName() ) )
            return 0

        # reset file
        file.resize( 0 )
        file.close()

        if  result.value( "addtoproject", e ).toBool() :
            # add files to scope
            core.projectsManager().addFilesToScope( result[ "scope" ].value(XUPItem), [fileName] )
        
        # open file
        return self.openFile( fileName, result[ "encoding" ].toString() )

    def document_contentChanged(self):
        self.mContentChangedTimer.start( CONTENT_CHANGED_TIME_OUT )
        document = self.sender() # signal sender
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
                entries[ document.filePath() ] = document.text()

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
                    core.projectsManager().openProject( url.toLocalFile(), c() )


    def internal_currentProjectChanged(self, currentProject, previousProject ):
        # uninstall old commands
        if  previousProject :
            previousProject.uninstallCommands()
            disconnect( previousProject, L( installCommandRequested(  pCommand&, & ) ), s, T( internal_projectInstallCommandRequested(  pCommand&, & ) ) )
            disconnect( previousProject, L( uninstallCommandRequested(  pCommand&, & ) ), s, T( internal_projectUninstallCommandRequested(  pCommand&, & ) ) )
    
        # get pluginsmanager
        pm = core.pluginsManager()
        
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
        self._mainWindow().menu_CustomAction_aboutToShow()


    def internal_projectInstallCommandRequested(self, cmd, mnu ):
        # create action
        action = core.menuBar().action( QString( "%1/%2" ).arg( mnu ).arg( cmd.text() ) , d.text() )
        action.setStatusTip( cmd.text() )

        # set action custom data contain the command to execute
        action.setData( QVariant.fromValue( cmd ) )
        
        # connect to signal
        action.triggered().connect(s.internal_projectCustomActionTriggered())
        
        # update menu visibility
        self._mainWindow().menu_CustomAction_aboutToShow()


    def internal_projectUninstallCommandRequested(self, cmd, mnu ):
        menu = core.menuBar().menu( mnu )
        
        for action in u.actions():
            if  action.menu() :
                internal_projectUninstallCommandRequested( cmd, QString( "%1/%2" ).arg( mnu ).arg( action.menu().objectName() ) )
            elif  not action.isSeparator() and action.data().value(pCommand) == cmd :
                delete action

        # update menu visibility
        self._mainWindow().menu_CustomAction_aboutToShow()

    def internal_projectCustomActionTriggered(self):
        action = self.sender()

        if  action :
            cm = core.consoleManager()
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
                #TODO core.recentsManager().addRecentFile( file )
    
    '''TODO
    def fileSessionSave_triggered(self):
        files = []
        projects = []

        # files
        for window in self.mdiArea.subWindowList():
            document = window
            files.append(document.filePath())

        core.settings().setValue( "Session/Files", files )
        
        # projects
        for project in core.projectsManager().topLevelProjects():
            projects.append(project.fileName())

        core.settings().setValue( "Session/Projects", projectss )

    def fileSessionRestore_triggered(self):
        # restore files
        for file in core.settings().value("Session/Files", [] ).toStringList():
            if not self.openFile( file, mks.monkeystudio.defaultCodec() ): # remove it from recents files
                core.recentsManager().removeRecentFile( file )
        
        # restore projects
        for project in core.settings().value( "Session/Projects", [] ).toStringList():
            if not core.projectsManager().openProject( project, mks.monkeystudio.defaultCodec() ): # remove it from recents projects
                core.recentsManager().removeRecentProject( project )
    
    '''
    
    def _saveDocument(self, document):
        self._fileWatcher.removePath(document.filePath())
        document.saveFile()
        self._fileWatcher.addPath(document.filePath())
    
    def _fileSaveCurrent_triggered(self):
        return self._saveDocument(self.currentDocument())
    
    def _fileSaveAll_triggered(self):
        for document in self.openedDocuments():
            self._saveDocument(document)
    
    def _reloadDocument(self, document):
        if  document.isModified():
            template = unicode(self.tr( "The file <b>%s</b> has been modified by you.\n"
                                        "Do you want to reload and discard changes?" ))
            text = template % document.fileName()
            ret = QMessageBox.question(self, self.tr( "Reload file..." ), text,
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret != QMessageBox.Yes:
                return

        # open file
        try:
            QApplication.setOverrideCursor( Qt.WaitCursor )
            document.reload()
        except IOError, ex:
            #TODO replace with messageManager ?
            QMessageBox.critical(None,
                                 self.tr("File not reloaded"),
                                 unicode(str(ex), 'utf8'))
            return None
        finally:
            QApplication.restoreOverrideCursor()
        
    def _onFileReloadTriggered(self):
        document = self.currentDocument()
        if  document is not None:
            self._reloadDocument(document)
    
    def _onFileReloadAllTriggered(self):
        for document in self.openedDocuments():
            if not document._isExternallyRemoved():
                self._reloadDocument(document)
            
    
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
    
    # edit menu
    def editSettings_triggered(self):
        UISettings.instance( self ).exec_()

    def editTranslations_triggered(self):
        locale = TranslationDialog.getLocale( core.translationsManager(), self )

        if  not locale.isEmpty() :
            core.settings().setValue( "Translations/Locale", locale )
            core.settings().setValue( "Translations/Accepted", True )
            core.translationsManager().setCurrentLocale( locale )
            core.translationsManager().reloadTranslations()


    def editExpandAbbreviation_triggered(self):
        document = self.currentDocument()

        if  document :
            core.abbreviationsManager().expandMacro( document.editor() )



    def editPrepareAPIs_triggered(self):
        mks.monkeystudio.prepareAPIs()

    # help menu
    def helpAboutApplication_triggered(self):
        dlg = UIAbout( self )
        dlg.open()
    '''
