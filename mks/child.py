from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mks.abstractchild
import mks.editor

class pChild(mks.abstractchild.pAbstractChild):
    
    """TODO rename
    """
    def __init__(self):
        mks.abstractchild.pAbstractChild.__init__(self, )
        self.mEditor = mks.editor.pEditor(self)
        self.mEditor.setAttribute( Qt.WA_MacSmallSize )
        self.mEditor.setFrameStyle( QFrame.NoFrame | QFrame.Plain )

        self.setWidget( self.mEditor )
        self.setFocusProxy( self.mEditor )
        
        """TODO
        # connections
        self.mEditor.cursorPositionChanged.connect(self.cursorPositionChanged)
        self.mEditor.undoAvailable.connect(self.undoAvailableChanged)
        self.mEditor.redoAvailable.connect(self.redoAvailableChanged)
        self.mEditor.copyAvailable.connect(self.copyAvailableChanged)
        self.mEditor.pasteAvailable.connect(self.pasteAvailableChanged)
        self.mEditor.modificationChanged.connect(self.setWindowModified)
        self.mEditor.modificationChanged.connect(self.modifiedChanged)
        self.mEditor.textChanged.connect(self.contentChanged)


    def cursorPositionChanged(self):
        self.cursorPositionChanged.emit( cursorPosition() )

    def language(self):
        # return the editor language
        if  self.mEditor.lexer() :
            return self.mEditor.lexer().language()

        # return nothing
        return ''

    def fileBuffer(self):
        return self.mEditor.text()

    def context(self):
        return "Coding"

    def initializeContext(self, tb ):
        pass

    def cursorPosition(self):
        return self.mEditor.cursorPosition() +QPoint( 0, 1 )

    def editor(self):
        return self.mEditor

    def isModified(self):
        return self.mEditor.isModified()

    def isUndoAvailable(self):
        return self.mEditor.isUndoAvailable()

    def invokeSearch ():
        '''MonkeyCore.searchWidget().showSearchFile ();'''
        pass

    def undo(self):
        self.mEditor.undo()

    def isRedoAvailable(self):
        return self.mEditor.isRedoAvailable()

    def redo(self):
        self.mEditor.redo()

    def cut(self):
        self.mEditor.cut()

    def copy(self):
        self.mEditor.copy()

    def paste(self):
        self.mEditor.paste()

    def goTo(self):
        self.mEditor.invokeGoToLine()

    def goTo(self, pos, selectionLength ):
        column = pos.x()
        line = pos.y()
        
        self.mEditor.setCursorPosition( line, column )
        self.mEditor.setSelection( line, column, line, column +selectionLength )
        self.mEditor.ensureLineVisible( line )
        self.mEditor.setFocus()

    def isCopyAvailable(self):
        return self.mEditor.copyAvailable()

    def isPasteAvailable(self):
        return self.mEditor.canPaste()

    def isGoToAvailable(self):
        return True

    def isPrintAvailable(self):
        return True
    
    def saveFile(self):
        self.mEditor.saveFile( filePath() )

    def backupFileAs(self, s ):
        self.mEditor.saveBackup( s )
    """
    
    def openFile(self, fileName, codec ):
        # if already open file, cancel
        '''if  not filePath().isEmpty() :
            return False
        }'''
        
        # set filename of the owned document
        self.setFilePath( fileName )

        # open file
        locked = self.blockSignals( True )
        opened = self.mEditor.openFile( fileName, codec )
        self.blockSignals( locked )
        
        if  not opened :
            self.setFilePath( '' )
            return False
        """ TODO
        self.mCodec = QTextCodec.codecForName( codec.toUtf8() )
        """
        self.fileOpened.emit()
        return True
    
    """
    def closeFile(self):
        self.mEditor.closeFile()
        self.setFilePath( QString.null )

        self.fileClosed.emit()

    def reload(self):
        self.openFile( self.mEditor.property( "fileName" ).toString(), self.mEditor.property( "codec" ).toString() )
        self.fileReloaded.emit()

    def printFile(self):
        self.mEditor.print_()

    def quickPrintFile(self):
        # print file
        self.mEditor.quickPrint()
    """