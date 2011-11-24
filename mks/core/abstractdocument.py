"""
abstractdocument --- Base classes for workspace documents
=========================================================

This class is inherited by textual editor, and must be inherited by other workspace widgets.

:class:`mks.core.workspace.AbstractDocument`  - base class of workspace documents
"""

import os.path

from PyQt4.QtCore import pyqtSignal, QFileSystemWatcher  # pylint: disable=E0611
from PyQt4.QtGui import QFileDialog, \
                        QIcon, \
                        QInputDialog, \
                        QMessageBox, \
                        QWidget

from mks.core.core import core

class AbstractDocument(QWidget):
    """
    Base class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant, ...
    Inherit this class, if you want to create new document type
    
    This class may requre redesign, if we need to add support for non-textual or non-unicode editor.
    DO redesign instead of doing dirty hacks
    """
    
    modifiedChanged = pyqtSignal(bool)
    """
    modifiedChanged(modified)
    
    **Signal** emitted, when modified state changed (file edited, or saved)
    Bool parameter contains new value
    """  # pylint: disable=W0105
    
    #Signal emitted, when document icon or toolTip has changed 
    #(i.e. document has been modified externally)
    documentDataChanged = pyqtSignal()
    
    def __init__( self, parentObject, filePath, createNew=False):
        """Create editor and open file.
        If file is None or createNew is True, empty not saved file is created
        IO Exceptions are not catched, therefore, must be catched on upper level
        """
        QWidget.__init__( self, parentObject)
        self._neverSaved = filePath is None or createNew
        self._filePath = filePath
        self._externallyRemoved = False
        self._externallyModified = False
        # File opening should be implemented in the document classes
        
        self._fileWatcher = None
        
        # create file watcher
        if not self._neverSaved:
            self._createFileWatcher()
        
        if filePath and self._neverSaved:
            core.messageManager().appendMessage('New file "%s" is going to be created' % filePath, 5000)
    
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
        self.documentDataChanged.emit()

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

    def _setModified(self, value):
        """Clear modified state for the file. Called by AbstractDocument
        
        To be implemented by child class
        """
        pass

    def isModified(self):
        """Returns True, if file is modified
        
        To be implemented by child class
        """
        pass

    def isExternallyModified(self):
        """Check if document's file has been modified externally.
        
        This method does not do any file system access, but only returns cached info
        """
        return self._externallyModified
    
    def isExternallyRemoved(self):
        """Check if document's file has been deleted externally.
        
        This method does not do any file system access, but only returns cached info
        """
        return self._externallyRemoved
    
    def isNeverSaved(self):
        """Check if document has been created, but never has been saved on disk
        """
        return self._neverSaved
        
    def filePath(self):
        """return the document file path"""
        return self._filePath
    
    def fileName(self):
        """return the document file name"""
        if self._filePath:
            return os.path.basename(self._filePath)
        else:
            return 'untitled'
            
    def saveFile(self):
        """Save the file to file system
        
        Shows QFileDialog if necessary
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
                self._filePath = path
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
            openedFile.write(self.text().encode('utf8'))
        finally:
            openedFile.close()
            if self._fileWatcher is None:  # file just get its name
                self._createFileWatcher()            
            else:
                self._fileWatcher.addPath(self.filePath())
        
        # Update states
        self._neverSaved = False
        self._externallyRemoved = False
        self._externallyModified = False
        self._setModified(False)
        
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


class AbstractTextEditor(AbstractDocument):
    """Base class for text editors. Currently, only QScintilla is supported, but, we may replace it in the future
    """
    
    cursorPositionChanged = pyqtSignal(int, int) # (line, column)
    """
    modifiedChanged(line, column)
    
    **Signal** emitted, when cursor position has been changed
    """  # pylint: disable=W0105
    def __init__(self, parentObject, filePath, createNew=False):
        AbstractDocument.__init__(self, parentObject, filePath, createNew)
        self._highlightingLanguage = None
    
    def text(self):
        """Contents of the editor.
        
        To be implemented by child class
        """
        pass
    
    def setText(self, text):
        """Set contents in the editor.
        Usually this method is called only internally by openFile()
        
        To be implemented by child class
        """
        pass

    def eolMode(self):
        """Return document's EOL mode. Possible values are:
        
        * ``\\n``  - UNIX EOL
        * ``\\r\\n`` - Windows EOL
        * ``None`` - not defined for the editor type
        
        To be implemented by child class
        """
        return None
    
    def setEolMode(self, mode):
        """Set editor EOL mode.
        See eolMode() for a alowed mode values
        
        To be implemented by child class
        """
        pass
    
    def indentWidth(self):
        """Get width of tabulation symbol and count of spaces to insert, when Tab pressed
        
        To be implemented by child class
        """
        pass
    
    def setIndentWidth(self, width):
        """Set width of tabulation symbol and count of spaces to insert, when Tab pressed
        
        To be implemented by child class
        """
        pass
    
    def indentUseTabs(self):
        """Get indentation uses tabs flag.
        If true - \t inserted by Tab button, if false - spaces
        
        To be implemented by child class
        """
        pass
    
    def setIndentUseTabs(self, use):
        """Set indentation uses tabs flag.
        If true - \t inserted by Tab button, if false - spaces
        
        To be implemented by child class
        """
        pass

    def highlightingLanguage(self):
        """Get programming language of the file.
        
        See list of supported programming languages in the settings
        """
        return self._highlightingLanguage

    def setHighlightingLanguage(self, language):
        """Set programming language of the file.
        
        Called Only by :class:`mks.plugins.associations.Associations` to select syntax highlighting language.
        
        To be implemented by child class
        Implementation must call AbstractDocument method
        """
        self._highlightingLanguage = language

    def cursorPosition(self):
        """Return cursor position as 2 values: line and column, if available
        
        To be implemented by child class
        """
        pass

    def invokeGoTo(self):
        """Show GUI dialog, go to line, if user accepted it
        """
        line, col = self.qscintilla.getCursorPosition()  # pylint: disable=W0612
        gotoLine, accepted = QInputDialog.getInteger(self, self.tr( "Go To Line..." ),
                                                      self.tr( "Enter the line you want to go:" ), 
                                                      line +1, 1, self.qscintilla.lines(), 1)
        
        if accepted:
            self.goTo(gotoLine - 1, 0)
    
    def goTo(self, line, column, selectionLength = -1 ):
        """Go to specified line and column.
        If selectionLength is not -1, select selectionLength characters
        
        To be implemented by child class
        """
        pass
    
    def line(self, index):
        """Get line of the text by its index. Lines are indexed from 0.
        
        None, if index is invalid
        
        To be implemented by child class
        """
        pass


#    TODO restore or delete old code
#    fileOpened = pyqtSignal()
#    fileClosed = pyqtSignal()
#    # when.emit a file is reloaded
#    fileReloaded = pyqtSignal()

#    def isPrintAvailable(self):
#    #    """return if print is available
#    #    """
#    #    pass

#    def textCodec(self)
#    { return mCodec ? mCodec.name() : pMonkeyStudio.defaultCodec();
#    
#    def encoding(self)
#    { return mCodec ? mCodec : QTextCodec.codecForName( pMonkeyStudio.defaultCodec().toLocal8Bit().constData() );

#    def backupFileAs(self fileName ):
#    #    pass
#    
#    def printFile(self):
#    #    pass
#    
#    def quickPrintFile(self):
#    #    pass

