"""
editor --- AbstractTextEditor implementation
============================================

Uses Qutepart internally
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextCursor, QVBoxLayout

from enki.core.core import core
from enki.core.abstractdocument import AbstractTextEditor

from qutepart import Qutepart

class Editor(AbstractTextEditor):
    """Text editor widget.
    
    Uses Qutepart internally
    """
    
    def __init__(self, parentObject, filePath, createNew=False, terminalWidget=False):
        super(Editor, self).__init__(parentObject, filePath, createNew)
        
        self._terminalWidget = terminalWidget

        self.qutepart = Qutepart(self)
        
        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.qutepart)
        self.setFocusProxy(self.qutepart)
        
        self.qutepart.document().modificationChanged.connect(self.modifiedChanged)
        self.qutepart.cursorPositionChanged.connect(self._onCursorPositionChanged)
        
        self._eolMode = r'\n'
        
        if not self._neverSaved:
            originalText = self._readFile(filePath)
            self.setText(originalText)
        else:
            originalText = ''

        #autodetect eol, if need
        pass  # TODO self._configureEolMode(originalText)
        
        self.qutepart.detectSyntax(sourceFilePath = filePath)

    #
    # AbstractDocument interface
    #
    
    def _setModified(self, modified):
        """Update modified state for the file. Called by AbstractTextEditor, must be implemented by the children
        """
        self.qutepart.document().setModified(modified)

    def isModified(self):
        """Check is file has been modified
        """
        return self.qutepart.document().isModified()

    #
    # AbstractTextEditor interface
    #
    
    def _onCursorPositionChanged(self):
        """Emit signal with current position
        """
        cursor = self.qutepart.textCursor()
        self.cursorPositionChanged.emit(cursor.blockNumber(), cursor.positionInBlock())

    def eolMode(self):
        """Line end mode of the file
        """
        return self._eolMode

    def setEolMode(self, mode):
        """Set line end mode of the file
        """
        # TODO
        self._eolMode = mode

    def indentWidth(self):
        """Indentation width in symbol places (spaces)
        """
        return 4 # TODO
    
    def _applyIndentWidth(self, width):
        """Set indentation width in symbol places (spaces)
        """
        # TODO 
        pass
    
    def indentUseTabs(self):
        """Indentation uses Tabs instead of Spaces
        """
        return False  # TODO
    
    def _applyIndentUseTabs(self, use):
        """Set iindentation mode (Tabs or spaces)
        """
        pass  # TODO
    
    def _applyLanguage(self, language):
        """Set programming language of the file.
        Called Only by :mod:`enki.plugins.associations` to select syntax highlighting language.
        """
        pass  # TODO

    def text(self):
        """Contents of the editor
        """
        return self.qutepart.toPlainText()

    def setText(self, text):
        """Set text in the Qutepart, clear modified flag, update line numbers bar
        """
        self.qutepart.setPlainText(text)
        self._setModified(False)

    def selectedText(self):
        """Get selected text
        """
        return self.qutepart.textCursor().selectedText()
        
    def selection(self):
        """Get coordinates of selected area as ((startLine, startCol), (endLine, endCol))
        """
        cursor = self.qutepart.textCursor()
        startPos = cursor.selectionStart()
        endPos = cursor.selectionEnd()
        
        return (self._toLineCol(startPos), self._toLineCol(endPos))

    def absSelection(self):
        """Get coordinates of selected area as (startAbsPos, endAbsPos)
        """
        cursor = self.qutepart.textCursor()
        
        return (cursor.selectionStart(), cursor.selectionEnd())

    def cursorPosition(self):
        """Get cursor position as tuple (line, col)
        """
        cursor = self.qutepart.textCursor()
        
        return self._toLineCol(cursor.position())
    
    def _setCursorPosition(self, line, col):
        """Implementation of AbstractTextEditor.setCursorPosition
        """
        absPos = self._toAbsPosition(line, col)
        
        cursor = QTextCursor(self.qutepart.document())
        cursor.setPosition(absPos)
        self.qutepart.setTextCursor(cursor)

    def replaceSelectedText(self, text):
        """Replace selected text with text
        """
        self.qutepart.textCursor().insertText(text)
    
    def _replace(self, startAbsPos, endAbsPos, text):
        """Replace text at position with text
        """
        cursor = QTextCursor(self.qutepart.document())
        cursor.setPosition(startAbsPos)
        cursor.setPosition(endAbsPos, Qt.KeepAnchor)
        cursor.insertText(text)
    
    def beginUndoAction(self):
        """Start doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        
        DO NOT FORGET to call **endUndoAction()** after you have finished
        """
        self.qutepart.textCursor().beginEditBlock()

    def endUndoAction(self):
        """Finish doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        """
        self.qutepart.textCursor().endEditBlock()

    def _goTo(self, line, column, selectionLine = None, selectionCol = None):
        """Go to specified line and column. Select text if necessary
        """
        cursor  = QTextCursor(self.qutepart.document())
        
        if selectionLine is None:
            cursor.setPosition(self._toAbsPosition(line, column))
        else:
            cursor.setPosition(self._toAbsPosition(selectionLine, selectionCol))
            cursor.setPosition(self._toAbsPosition(line, column), QTextCursor.KeepAnchor)
        
        self.qutepart.setTextCursor(cursor)
    
    def lineCount(self):
        """Get line count
        """
        return self.qutepart.blockCount()

    def printFile(self):
        """Print file
        """
        pass  # TODO

    def setExtraSelections(self, selections):
        """Set additional selections.
        Used for highlighting search results
        Selections is list of turples (startAbsolutePosition, length)
        """
        pass  # TODO

