"""
abstractdocument --- Base class for workspace documents
=======================================================

This class is inherited by textual editor, and must be inherited by other workspace widgets.

:class:`mks.workspace.AbstractDocument`  - base class of workspace documents
"""

import os.path

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QIcon, \
						QMessageBox, \
						QWidget


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
        IO Exceptions not catched, so, must be catched on upper level
        """
        QWidget.__init__( self, parentObject )
        
        self._filePath = None # To be filled by child classes
        self._externallyRemoved = False
        self._externallyModified = False    
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
    
    def filePath(self):
        """return the document file path"""
        return self._filePath
    
    def fileName(self):
        """return the document file name"""
        return os.path.basename(self._filePath)
        
    def cursorPosition(self):
        """return cursor position as 2 values: line and column, if available
        """
        pass
    
    def isModified(self):
        """Returns True, if file is modified
        """
        pass
        
    
    def goTo(self, line, column, selectionLength = -1 ):
        pass
    
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
