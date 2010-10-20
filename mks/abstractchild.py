"""Basic class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant
"""
import os.path

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class pAbstractChild(QMdiSubWindow):
    """Basic class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant
    """
    
    """TODO
    enum DocumentMode { mNone:, mNa, mInsert, mOverwrite, mReadOnly } mDocument
    enum LayoutMode { lNone:, lNormal, lVertical, lHorizontal } mLayout
    """
    
    def xxx(self):
        return 'xxx'
    
    def __init__( self, parentObject, filePath):
        """Create editor and open file.
        IO Exceptions not catched, so, must be catched on upper level
        """
        QMdiSubWindow.__init__( self, parentObject )
        
        # default for window icon is application icon. This line avoids using it in the opened files list
        self.setWindowIcon(QIcon())
        
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
        # File opening should be implemented in the child classes
    
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
    
    def _setFilePath( self, filePath ):
        """set the file path of the document
        """
        if not filePath:
            self.setWindowFilePath( '' )
            self.setWindowTitle( '' )
        else:
            self.setWindowFilePath( filePath )
            self.setWindowTitle( os.path.basename(unicode(filePath)) + "[*]" )
    
    def filePath(self):
        """return the document file path"""
        return unicode(self.windowFilePath())
    
    '''TODO
    def fileName(self):
        """return the filename of the document"""
        wfp = self.windowFilePath()
        if wfp.isEmpty():
            return None
        else:
            return QFileInfo( wfp ).fileName()
    def path(self):
        """return the absolute path of the document"""
        wfp = self.windowFilePath()
        if wfp.isEmpty():
            return None
        else:
            return QFileInfo( wfp ).absolutePath()

    def QString fileBuffer(self):
        """return the current buffer (text) of filename"""
        return None
    
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
    '''TODO
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
    '''
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
    '''TODO
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
    
    def closeFile(self):
        pass
    
    def reload(self):
        pass
    
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
    # when.emit the child layout mode has changed
    layoutModeChanged = pyqtSignal()
    # when.emit the child document mode has changed
    documentModeChanged = pyqtSignal()
    # when.emit cursor position changed
    cursorPositionChanged = pyqtSignal(int, int) # (line, column)
    '''
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
    '''TODO
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
    '''