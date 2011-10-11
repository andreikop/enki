"""
abstractdocument --- Base class for workspace documents
=======================================================

This class is inherited by textual editor, and must be inherited by other workspace widgets.

:class:`mks.core.workspace.AbstractDocument`  - base class of workspace documents
"""

import os.path

from PyQt4.QtCore import pyqtSignal, \
                         QFileSystemWatcher
from PyQt4.QtGui import QFileDialog, \
                        QIcon, \
                        QInputDialog, \
                        QMessageBox, \
                        QWidget

from mks.core.core import core

class AbstractDocument(QWidget):
    """Base class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant, ...
    Inherit this class, if you want to create new document type
    
    This class may requre redesign, if we need to add support for non-textual or non-unicode editor.
    DO redesign instead of doing dirty hacks
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
    
    # emit when cursor position changed
    cursorPositionChanged = pyqtSignal(int, int) # (line, column)
    
    def __init__( self, parentObject, filePath):
        """Create editor and open file.
        If file is '', empty not saved file is created
        IO Exceptions not catched, so, must be catched on upper level
        """
        QWidget.__init__( self, parentObject )
        
        self._filePath = filePath
        self._externallyRemoved = False
        self._externallyModified = False
        # File opening should be implemented in the document classes
        
        self._fileWatcher = None
        
        # create file watcher
        if filePath:
            self._createFileWatcher()
    
    def _createFileWatcher(self):
        """Create own filewatcher. Called from the constructor, or after name has been defined for new created file
        """
        self._fileWatcher = QFileSystemWatcher([self.filePath()], self)
        self._fileWatcher.fileChanged.connect(self._onWatcherFileChanged)
    
    def _onWatcherFileChanged(self):
        """QFileSystemWatcher sent signal, that file has been changed or deleted
        """
        if os.path.exists(self.filePath()):
            self._externallyModified = True
        else:
            self._externallyRemoved = True
        self._documentDataChanged.emit()

    def _readFile(self, filePath):
        """Read the file contents.
        Shows QMessageBox for UnicodeDecodeError, but raises IOError, if failed to read file
        """
        with open(filePath, 'r') as openedFile:  # Exception is ok, raise it up
            self._filePath = os.path.abspath(filePath)
            data = openedFile.read()                
        
        try:
            text = unicode(data, 'utf8')
        except UnicodeDecodeError, ex:
            QMessageBox.critical(None,
                                 self.tr("Can not decode file"),
                                 filePath + '\n' +
                                 unicode(str(ex), 'utf8') + 
                                 '\nProbably invalid encoding was set. ' +
                                 'You may corrupt your file, if saved it')
            text = unicode(data, 'utf8', 'replace')
        return text

    def isExternallyRemoved(self):
        """Check if document's file has been deleted externally.
        This method DOES NOT do any file system access, but only returns cached info
        """
        return self._externallyRemoved
    
    def isExternallyModified(self):
        """Check if document's file has been modified externally.
        This method DOES NOT do any file system access, but only returns cached info
        """
        return self._externallyModified
    
    def isNeverSaved(self):
        """Check if document has been created, but never has been saved on disk
        """
        return self._filePath is None
    
    def eolMode(self):
        """Return document's EOL mode. Possible values are:
        
        * ``\\n``  - UNIX EOL
        * ``\\r\\n`` - Windows EOL
        * ``None`` - not defined for the editor type
        
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
    
    def filePath(self):
        """return the document file path"""
        return self._filePath
    
    def fileName(self):
        """return the document file name"""
        if self._filePath:
            return os.path.basename(self._filePath)
        else:
            return 'untitled'
        
    def cursorPosition(self):
        """return cursor position as 2 values: line and column, if available
        """
        pass
    
    def isModified(self):
        """Returns True, if file is modified
        """
        pass
        
    def invokeGoTo(self):
        """Show GUI dialog, go to line, if user accepted it
        """
        line, col = self.qscintilla.getCursorPosition()
        gotoLine, accepted = QInputDialog.getInteger(self, self.tr( "Go To Line..." ),
                                                      self.tr( "Enter the line you want to go:" ), 
                                                      line +1, 1, self.qscintilla.lines(), 1)
        
        if accepted:
            self.goTo(gotoLine - 1, 0)
    
    def goTo(self, line, column, selectionLength = -1 ):
        """Go to specified line and column.
        If selectionLength is not -1, select selectionLength characters
        """
        pass
    
    def saveFile(self):
        """Save the file to file system
        """
        if  not self.isModified() and \
            not self.isNeverSaved() and \
            not self.isExternallyModified() and \
            not self.isExternallyRemoved():
            return
        
        # Get path
        if not self._filePath:
            path = QFileDialog.getSaveFileName (self, self.tr('Save file as...'))
            if path:
                core.workspace().documentClosed.emit(self)
                self._filePath = unicode(path, 'utf8')
                core.workspace().documentOpened.emit(self)
            else:
                return
        
        # Create directory
        dirPath = os.path.dirname(self.filePath())
        if  not os.path.exists(dirPath):
            try:
                os.mkdir(dirPath)
            except OSError, ex:
                error = unicode(str(ex), 'utf8')
                QMessageBox.critical(None,
                                     self.tr("Can not save file"),
                                     self.tr( "Cannot create directory '%s'. Error '%s'" % (dirPath, error)))
                return
        
        # Write file
        if self._fileWatcher is not None:
            self._fileWatcher.removePath(self.filePath())
        
        try:
            openedFile = open(self.filePath(), 'w')
        except IOError as ex:
            QMessageBox.critical(None,
                                 self.tr("Can not write to file"),
                                 unicode(str(ex), 'utf8'))
            return
        
        try:
            openedFile.write(unicode(self.text()).encode('utf8'))
        finally:
            openedFile.close()
            if self._fileWatcher is None:  # file just get its name
                self._createFileWatcher()            
            else:
                self._fileWatcher.addPath(self.filePath())
        
        # Update states
        self._externallyRemoved = False
        self._externallyModified = False
        self._setModified(False)
        
    
    def text(self):
        """Contents of the editor.
        """
        pass
    
    def setText(self, text):
        """Set contents in the editor.
        Usually this method is called only internally by openFile()
        """
        pass
    
    def reload(self):
        """Reload the file from the disk
        
        If child class reimplemented this method, it MUST call method of the parent class
        for update internal bookkeeping"""

        text = self._readFile(self.filePath())
        self.setText(text)
        #self.fileReloaded.emit()
        self._externallyModified = False
        self._externallyRemoved = False
        
    def modelToolTip(self):
        """Tool tip for the opened files model
        """
        toolTip = self.filePath()
        
        if self.isModified():
            toolTip += "<br/><font color='blue'>%s</font>" % self.tr("Locally Modified")
        if  self._externallyModified:
            toolTip += "<br/><font color='red'>%s</font>" % self.tr("Externally Modified")
        if  self._externallyRemoved:
            toolTip += "<br/><font color='red'>%s</font>" % self.tr( "Externally Deleted" )
        return toolTip
    
    def modelIcon(self):
        """Icon for the opened files model
        """
        if self.isNeverSaved():  # never has been saved
            icon = "save.png"
        elif   self._externallyRemoved  and self._externallyModified:
            icon = "modified-externally-deleted.png"
        elif self._externallyRemoved:
            icon = "deleted.png"
        elif self._externallyModified and self.isModified():
            icon = "modified-externally-modified.png"
        elif self._externallyModified:
            icon = "modified-externally.png"
        elif self.isModified():
            icon = "save.png"
        else:
            icon = "transparent.png"
        return QIcon(":/mksicons/" + icon)
    
    def _setModified(self, value):
        """Clear modified state for the file. Called by AbstractDocument, must be implemented by the children
        """
        pass
    
    def highlightingLanguage(self):
        """Get programming language of the file.
        """
        return self._highlightingLanguage

    def setHighlightingLanguage(self, language):
        """Set programming language of the file.
        Called Only by FIXME link assotiations module to select syntax highlighting language.
        
        To be implemented by child classes
        Implementation must call AbstractDocument class method
        """
        self._highlightingLanguage = language
    
''' TODO restore or delete old code
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

    # when.emit search/replace is available
    #searchReplaceAvailableChanged = pyqtSignal(bool)
    # when.emit requesting search in editor
    #requestSearchReplace = pyqtSignal()
    # when.emit a document require to update workspace
    #updateWorkspaceRequested()
    
    enum DocumentMode { mNone:, mNa, mInsert, mOverwrite, mReadOnly } mDocument
    enum LayoutMode { lNone:, lNormal, lVertical, lHorizontal } mLayout
    
    mDocument = mNone
    mLayout = lNone

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

    def path(self):
        """return the absolute path of the document"""
        wfp = self.windowFilePath()
        if wfp.isEmpty():
            return None
        else:
            return QFileInfo( wfp ).absolutePath()

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

    def backupFileAs(self fileName ):
        pass
    
    def closeFile(self):
        pass

    def invokeSearch(self):
        pass

    def printFile(self):
        pass
    
    def quickPrintFile(self):
        pass
'''
