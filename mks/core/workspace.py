"""
workspace --- Open documents and manage it
==========================================

Terminology:

Workspace - main working area, where documents are placed.

Document - widget on workspace. Here is examples of documents:

* Textual editor
* QtDesigner (probably in the future)
* QtAssistant (probably in the future)

Document classes are herited from :class:`mks.core.abstractdocument.AbstractDocument`

:class:`mks.core.workspace.Workspace`
"""

import os.path
import sys

from PyQt4.QtGui import QApplication, \
                        QDialog, QDialogButtonBox, \
                        QFileDialog, \
                        QListWidgetItem, \
                        QMessageBox, \
                        QStackedWidget
from PyQt4.QtCore import pyqtSignal, QEvent, Qt  # pylint: disable=E0611

from mks.core.core import core, DATA_FILES_PATH
import mks.core.openedfilemodel
from mks.core.abstractdocument import AbstractDocument


class _UISaveFiles(QDialog):
    """Save files dialog.
    Shows checkable list of not saved files.
    """
    def __init__(self, workspace, documents):
        super(_UISaveFiles, self).__init__(workspace)
        self.cancelled = False
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/SaveFiles.ui'), self)
        self.buttonBox.clicked.connect(self._onButtonClicked)
        
        self._itemToDocument = {}
        for document in documents:
            name = document.fileName()
            if name is None:
                name = 'untitled'
            item = QListWidgetItem( name, self.listWidget )
            if document.filePath() is not None:
                item.setToolTip( document.filePath() )
            item.setCheckState( Qt.Checked )
            self._itemToDocument[item] = document
        self.buttonBox.button(self.buttonBox.Cancel).setText(self.tr('Cancel Close'))
        self.buttonBox.button(self.buttonBox.Save).setText(self.tr('Save checked'))
        
        self.buttonBox.button(QDialogButtonBox.Cancel).setFocus()

    
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
    
    instance is accessible as: ::
    
        from mks.core.core import core
        core.workspace()
    
    """
        
    documentOpened = pyqtSignal(AbstractDocument)
    """
    documentOpened(:class:`mks.core.abstractdocument.AbstractDocument`)
    
    **Signal** emitted, when document has been created, i.e. textual file opened, 
    or some other document added to workspace
    """  # pylint: disable=W0105
    
    documentClosed = pyqtSignal(AbstractDocument)
    """
    documentClosed(:class:`mks.core.abstractdocument.AbstractDocument`)
    
    **Signal** emitted, when document was closed
    """  # pylint: disable=W0105
    
    currentDocumentChanged = pyqtSignal(AbstractDocument,
                                        AbstractDocument)
    """
    currentDocumentChanged(:class:`mks.core.abstractdocument.AbstractDocument` old, 
    :class:`mks.core.abstractdocument.AbstractDocument` current)
    
    **Signal** emitted, when current document changed, i.e. user selected another document, 
    new document opened, current closed
    """  # pylint: disable=W0105
    
    modifiedChanged = pyqtSignal(AbstractDocument, bool)
    """
    modifiedChanged(document, modified)
    
    **Signal** emitted, when modified state of a document had been changed (file edited, or saved)
    Bool parameter contains new value
    Convenience signal, which retransmits original signal, sent by the document
    """  # pylint: disable=W0105

    cursorPositionChanged = pyqtSignal(AbstractDocument, int, int)
    """
    cursorPositionChanged(document, line, column)
    
    **Signal** emitted, when cursor position has been changed
    Convenience signal, which retransmits original signal, sent by the document
    """  # pylint: disable=W0105
    
    textChanged = pyqtSignal(AbstractDocument)
    """
    textChanged(document)
    
    **Signal** emitted, when text has been chagned
    Convenience signal, which retransmits original signal, sent by the document
    """  # pylint: disable=W0105
    
    languageChanged = pyqtSignal(AbstractDocument, unicode, unicode)
    """
    languageChanged(document, old, new)
    
    **Signal** emitted, when highlighting (programming) language of a file has been changed
    Convenience signal, which retransmits original signal, sent by the document
    """  # pylint: disable=W0105
    
    indentWidthChanged = pyqtSignal(AbstractDocument, int)
    """
    indentWidthChanged(document, width)
    
    **Signal** emitted, when indentation with has been changed
    Convenience signal, which retransmits original signal, sent by the document
    """  # pylint: disable=W0105

    indentUseTabsChanged = pyqtSignal(AbstractDocument, bool)
    """
    indentUseTabsChanged(document, use)
    
    **Signal** emitted, when indentation mode has been changed
    Convenience signal, which retransmits original signal, sent by the document
    """  # pylint: disable=W0105

    def __init__(self, mainWindow):
        """ list of opened documents as it is displayed in the Opened Files Explorer. 
        List accessed and modified by mks.core.openedfilemodel.OpenedFileModel class
        """
        QStackedWidget.__init__(self, mainWindow)
        mainWindow.setFocusProxy(self)
        
        self.setStyleSheet("QStackedWidget { padding-bottom: 5; }");
        self.sortedDocuments = []  # not protected, because available for OpenedFileModel
        self._oldCurrentDocument = None
        self._textEditorClass = None
        
        # create opened files explorer
        # openedFileExplorer is not protected, because it is available for OpenedFileModel
        self.openedFileExplorer = mks.core.openedfilemodel.OpenedFileExplorer(self)
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.openedFileExplorer)
        
        self.currentChanged.connect(self._onStackedLayoutIndexChanged)
        
        self.currentDocumentChanged.connect(self._updateMainWindowTitle)
        self.currentDocumentChanged.connect(self._onCurrentDocumentChanged)
    
    def del_(self):
        """Terminate workspace. Called by the core to clear actions
        """
        self.openedFileExplorer.del_()
    
    def _mainWindow(self):
        """Get mainWindow instance
        """
        return self.parentWidget().parentWidget()

    def _updateMainWindowTitle(self):
        """Update window title after document or it's modified state has been changed
        """
        document = self.currentDocument()
        if document:
            name = document.fileName()
            if name is None:
                name = 'untitled'
            if document.isModified():
                name += '*'
            if document.filePath() is not None:
                path = os.path.dirname(document.filePath())
            else:
                path = os.path.abspath(os.curdir)
            
            name += ' - '
            name += path
        else:
            name = self._mainWindow().defaultTitle()
        self._mainWindow().setWindowTitle(name)

    def setTextEditorClass(self, newEditorClass):
        """Set text editor, which is used for open textual documents.
        New editor would be used for newly opened textual documents.
        
        newEditorClass is class, herited from :class:`mks.core.abstractdocument.AbstractDocument`
        """
        self._textEditorClass = newEditorClass
    
    def textEditorClass(self):
        """Get text editor, which is used for open textual documents.
        Text editor is class, herited from :class:`mks.core.abstractdocument.AbstractDocument`
        """
        return self._textEditorClass
    
    def eventFilter( self, obj, event ):
        """NOT AN API function
        
        Handler for QObject events of children
        """
        if  obj.isWidgetType() :
            document = obj
            if  event.type() == QEvent.Close:
                event.ignore()
                self.closeDocument( document )
                return True
        
        return super(Workspace, self).eventFilter(obj, event)
    
    def _onStackedLayoutIndexChanged(self, index):
        """Handler of change of current document in the stacked layout.
        Only calls _onCurrentDocumentChanged(document)
        """
        document = self.widget(index)
        self._onCurrentDocumentChanged(document)
        
        if document is None and self.count():  # just lost focus, no real change
            return
        if document == self._oldCurrentDocument:  # just recieved focus, no real change
            return
        
        if document is not None:
            self.setFocusProxy(document)

        self.currentDocumentChanged.emit(self._oldCurrentDocument, document)
        self._oldCurrentDocument = document

    def _onCurrentDocumentChanged( self, document):
        """Change current directory, if current file changed
        """
        if  document and document.filePath() is not None and \
            os.path.exists(os.path.dirname(document.filePath())):
            try:
                os.chdir( os.path.dirname(document.filePath()) )
            except OSError, ex:  # directory might be deleted
                print >> sys.stderr, 'Failed to change directory:', str(ex)

    def currentDocument(self):
        """Returns currently active (focused) document. None, if no documents are opened
        """
        return self.currentWidget()
    
    def setCurrentDocument( self, document ):
        """Select active (focused and visible) document form list of opened documents
        """
        self.setCurrentWidget( document )
    
    def _activeDocumentByIndex(self, index):
        """Activate document by it's index in the list of documents
        """
        document = self.documents()[index]
        self.setCurrentDocument(document)
        document.setFocus()
        
    def activateNextDocument(self):
        """Activate next document in the list
        """
        documents = self.documents()
        
        curIndex = documents.index(self.currentDocument())
        nextIndex = (curIndex + 1) % len(documents)
        self._activeDocumentByIndex(nextIndex)
        
    
    def activatePreviousDocument(self):
        """Activate previous document in the list
        """
        documents = self.documents()
        
        curIndex = documents.index(self.currentDocument())
        prevIndex = (curIndex - 1 + len(documents)) % len(documents)
        
        self._activeDocumentByIndex(prevIndex)

    def focusCurrentDocument(self):
        """Set focus (cursor) to current document.
        
        Used if user has finished work with some dialog, and, probably, want's to edit text
        """
        document = self.currentDocument()
        if  document :
            document.setFocus()

    def goTo(self, filePath, absPos=None, line=None, column=None, selectionLength=None):
        """Open file, activate it, and go to specified position. Select text after position, if necessary.
        
        selectionLength specifies, how much characters should be selected
        """
        document = self.openFile(filePath)  # search for already opened or open new

        if  document is not None and \
            (absPos is not None or \
             line is not None or \
             column is not None or \
             selectionLength is not None):
                document.goTo(absPos=absPos, line=line, column=column, selectionLength=selectionLength, grabFocus=True)
    
    def _handleDocument( self, document ):
        """Add document to the workspace. Connect signals
        """
        # update file menu
        document.modifiedChanged.connect(self._updateMainWindowTitle)

        # Create lambda functions, which retransmit conveniense signals, and connect it to document signals
        document.modifiedChanged.connect(lambda modified: self.modifiedChanged.emit(document, modified))
        document.cursorPositionChanged.connect(lambda row, col: self.cursorPositionChanged.emit(document, row, col))
        document.textChanged.connect(lambda: self.textChanged.emit(document))
        document.languageChanged.connect(lambda old, new: self.languageChanged.emit(document, old, new))
        document.indentWidthChanged.connect(lambda width: self.indentWidthChanged.emit(document, width))
        document.indentUseTabsChanged.connect(lambda useTabs: self.indentUseTabsChanged.emit(document, useTabs))    

        # add to workspace
        document.installEventFilter( self )

        self.documentOpened.emit( document )

        self.addWidget( document )
        self.setCurrentWidget( document )
    
    def _unhandleDocument( self, document ):
        """Remove document from the workspace. Disconnect signals
        """
        # remove from workspace
        document.removeEventFilter( self )
        self.removeWidget(document)
        
    def openFile(self, filePath):
        """Open named file using suitable plugin, or textual editor, if other suitable editor not found.
        
        Returns document, if opened, None otherwise
        
        Opens modal dialog, if failed to open the file
        """
        # Close 'untitled'
        if len(self.documents()) == 1 and \
           self.documents()[0].fileName() is None and \
           not self.documents()[0].filePath() and \
           not self.documents()[0].text() and \
           not self.documents()[0].isModified():
            self.closeDocument(self.documents()[0])        

        # check if file is already opened
        for document in self.sortedDocuments:
            if os.path.isfile(filePath) and \
               document.filePath() is not None and \
               os.path.isfile(document.filePath()) and \
               os.path.samefile( document.filePath(), filePath ) :
                self.setCurrentDocument( document )
                return document

        documentType = None  # TODO detect document type, choose editor
        
        # select editor for the file
        if not documentType :
            documentType = self._textEditorClass
        
        if not documentType:
            QMessageBox.critical(None,
                                 self.tr("Failed to open file"),
                                 self.tr("Don't have any editor for open %s. Is any text editor plugin enabled?" % 
                                         filePath))
            return None
        
        # open file
        try:
            QApplication.setOverrideCursor( Qt.WaitCursor )
            document = documentType(self, filePath)
        except IOError as ex:
            QMessageBox.critical(None,
                                 self.tr("Failed to open file"),
                                 unicode(str(ex), 'utf8'))
            return None
        finally:
            QApplication.restoreOverrideCursor()

        self._handleDocument( document )
        
        if not os.access(filePath, os.W_OK):
            core.mainWindow().appendMessage( \
                        self.tr( "File '%s' is not writable" % filePath), 4000) # todo fix
        
        return document
    
    def createEmptyNotSavedDocument(self, filePath=None):
        """Create empty not saved document.
        Used on startup, if no file was specified, and after File->New file has been triggered
        """
        document = self._textEditorClass(self, filePath, True)
        self._handleDocument( document )
        document.setFocus()
        return document
    
    def documents(self):
        """Get list of opened documents (:class:`mks.core.abstractdocument.AbstractDocument` instances)
        """
        return self.sortedDocuments
    
    def _doCloseDocument(self, document):
        """Closes document, even if it is modified
        """
        if len(self.sortedDocuments) > 1:  # not the last document
            if document == self.sortedDocuments[-1]:  # the last document
                self.activatePreviousDocument()
            else:  # not the last
                self.activateNextDocument()
        
        self.documentClosed.emit( document )
        # close document
        self._unhandleDocument( document )
        document.del_()        

    def closeDocument( self, document):
        """Close opened file, remove document from workspace and delete the widget
        """
        if document.isModified():
            if _UISaveFiles(self, [document]).exec_() == QDialog.Rejected:
                return
        
        self._doCloseDocument(document)

    def askToCloseAll(self):
        """If have unsaved documents, ask user to save it and close all
        Will save documents, checked by user
        Returns True, if user hasn't pressed Cancel Close
        """
        modifiedDocuments = [d for d in self.documents() if d.isModified()]
        if modifiedDocuments:
            if (_UISaveFiles( self, modifiedDocuments).exec_() == QDialog.Rejected):
                return False # do not close
        
        return True
    
    def closeAllDocuments(self):
        """Close all documents
        
        If there are not saved documents, dialog will be shown.
        
        Handler of File->Close->All
        
        Returns True, if all files had been closed, and False, if save dialog rejected
        
        If hideMainWindow is True, main window will be hidden, if user hadn't pressed "Cancel Close"
        """
        if not self.askToCloseAll():
            return
        
        self.forceCloseAllDocuments()
    
    def forceCloseAllDocuments(self):
        """Close all documents without asking user to save
        """
        for document in self.documents()[::-1]:
            self._doCloseDocument(document)

#    def onEditExpandAbbreviation(self):
#        document = self.currentDocument()

#        if  document :
#            core.abbreviationsManager().expandMacro( document.editor() )
