"""
editor --- AbstractTextEditor implementation
============================================

Uses QScintilla  internally
"""

import shutil

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import qApp, QColor, QFont, QFrame, QIcon, QKeyEvent, QKeySequence, QPrintDialog, QVBoxLayout

from PyQt4.Qsci import *  # pylint: disable=W0401,W0614

from mks.core.core import core
from mks.core.abstractdocument import AbstractTextEditor

from lexer import Lexer

class _QsciScintilla(QsciScintilla):
    """QsciScintilla wrapper class. It is created to:
    
    * Catch Shift+Tab. When pressed - Qt moves focus, but it is not desired behaviour. This class catches the event
    * Catch Enter presesing and emits a signal after newline had been inserted
    * Fix EOL mode when pasting text
    """
    
    newLineInserted = pyqtSignal()
    
    def __init__(self, editor):
        self._editor = editor
        QsciScintilla.__init__(self, editor)
    
    def keyPressEvent(self, event):
        """Key pressing handler
        """
        if event.key() == Qt.Key_Backtab:  # convert the event to Shift+Tab pressing without backtab behaviour
            event.accept()
            newev = QKeyEvent(event.type(), Qt.Key_Tab, Qt.ShiftModifier)
            super(_QsciScintilla, self).keyPressEvent(newev)
        elif event.matches(QKeySequence.InsertParagraphSeparator):
            lineCount = self.lines()
            self.beginUndoAction()
            super(_QsciScintilla, self).keyPressEvent(event)
            if self.lines() > lineCount:  # bad hack, which checks, if autocompletion window is active
                self.newLineInserted.emit()
            self.endUndoAction()
        else:
            super(_QsciScintilla, self).keyPressEvent(event)
    
    def paste(self):
        """paste() method reimplementation. Converts EOL after text had been pasted
        """
        QsciScintilla.paste(self)
        self.convertEols(self.eolMode())

    def setSelection(self, startLine, startCol, endLine, endCol):
        """Wrapper for QScintilla.setSelection.
        QScintilla copies selected text to the selection clipboard. But, it is not desired behaviour.
        This method restores selection clipboard.
        """
        clipboard = qApp.clipboard()
        contents = clipboard.text(clipboard.Selection)
        QsciScintilla.setSelection(self, startLine, startCol, endLine, endCol)
        clipboard.setText(contents, clipboard.Selection)

    def pasteLine(self):
        """Paste lines from the clipboard.
        
        Lines are always pasted to new lines of document.
        If something is selected - not only selection, but whole lines, which contain selection,
        will be removed
        
        New method, extends QScintilla functionality
        """
        text = qApp.clipboard().text()
        
        self.beginUndoAction()

        if self.hasSelectedText():
            startLine, startCol, endLine, endCol = self.getSelection()
            if endCol == 0:
                endLine -= 1
            endLineLength = len(self.text(endLine))
            self.setSelection(startLine, 0, endLine, endLineLength)
            self.removeSelectedText()
        else:
            line, col = self.getCursorPosition()
            endLineLength = len(self.text(line))
            self.setCursorPosition(line, endLineLength)
            if not self.text(line).endswith('\n'):
                text = '\n' + text
        
        if not text.endswith('\n'):
            text += '\n'

        self.insert(text)
        
        self.endUndoAction()
    
    def ensureLineVisible(self, line):
        """QScintilla method reimplementation. Saves margins
        """
        self.SendScintilla(self.SCI_ENSUREVISIBLEENFORCEPOLICY, line)


class Editor(AbstractTextEditor):
    """Text editor widget.
    
    Uses QScintilla internally
    """
    
    _MARKER_BOOKMARK = -1  # QScintilla marker type
    
    _EOL_CONVERTOR_TO_QSCI = {r'\n'     : QsciScintilla.EolUnix,
                              r'\r\n'   : QsciScintilla.EolWindows,
                              r'\r'     : QsciScintilla.EolMac}
    
    _WRAP_MODE_TO_QSCI = {"WrapWord"      : QsciScintilla.WrapWord,
                          "WrapCharacter" : QsciScintilla.WrapCharacter}
    
    _WRAP_FLAG_TO_QSCI = {"None"           : QsciScintilla.WrapFlagNone,
                          "ByText"         : QsciScintilla.WrapFlagByText,
                          "ByBorder"       : QsciScintilla.WrapFlagByBorder}

    _EDGE_MODE_TO_QSCI = {"Line"        : QsciScintilla.EdgeLine,
                          "Background"  : QsciScintilla.EdgeBackground} 
    
    _WHITE_MODE_TO_QSCI = {"Invisible"           : QsciScintilla.WsInvisible,
                           "Visible"             : QsciScintilla.WsVisible,
                           "VisibleAfterIndent"  : QsciScintilla.WsVisibleAfterIndent}
        
    _AUTOCOMPLETION_MODE_TO_QSCI = {"APIs"      : QsciScintilla.AcsAPIs,
                                    "Document"  : QsciScintilla.AcsDocument,
                                    "All"       : QsciScintilla.AcsAll}
    
    _BRACE_MATCHING_TO_QSCI = {"Strict"    : QsciScintilla.StrictBraceMatch,
                               "Sloppy"    : QsciScintilla.SloppyBraceMatch}
    
    _CALL_TIPS_STYLE_TO_QSCI = {"NoContext"                : QsciScintilla.CallTipsNoContext,
                                "NoAutoCompletionContext"  : QsciScintilla.CallTipsNoAutoCompletionContext,
                                "Context"                  : QsciScintilla.CallTipsContext}
    
    #
    # Own methods
    #
    
    def __init__(self, parentObject, filePath, createNew=False, terminalWidget=False):
        super(Editor, self).__init__(parentObject, filePath, createNew)
        
        self._terminalWidget = terminalWidget
        self._eolMode = None
        
        # Configure editor
        self.qscintilla = _QsciScintilla(self)
        self.qscintilla.newLineInserted.connect(self.newLineInserted)
        
        pixmap = QIcon(":/mksicons/bookmark.png").pixmap(16, 16)
        self._MARKER_BOOKMARK = self.qscintilla.markerDefine(pixmap, -1)
        
        self._initQsciShortcuts()
        
        self.qscintilla.setUtf8(True)
        
        self.qscintilla.setAttribute(Qt.WA_MacSmallSize)
        self.qscintilla.setFrameStyle(QFrame.NoFrame | QFrame.Plain)
        
        self.qscintilla.SendScintilla(self.qscintilla.SCI_SETVISIBLEPOLICY,
                                      self.qscintilla.CARET_SLOP | self.qscintilla.CARET_STRICT,
                                      3)
        
        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.qscintilla)
        
        self.setFocusProxy(self.qscintilla)
        # connections
        self.qscintilla.cursorPositionChanged.connect(self.cursorPositionChanged)
        self.qscintilla.modificationChanged.connect(self.modifiedChanged)
        
        self.applySettings()
        self.lexer = Lexer(self)
        
        if not self._neverSaved:
            originalText = self._readFile(filePath)
            self.setText(originalText)
        else:
            originalText = ''
        
        myConfig = core.config()["Editor"]
        
        # make backup if needed
        if  myConfig["CreateBackupUponOpen"]:
            if self.filePath() and not createNew:
                shutil.copy(self.filePath(), self.filePath() + '.bak')

        # convert tabs if needed
        if  myConfig["Indentation"]["ConvertUponOpen"]:
            self._convertIndentation()
        
        #autodetect eol, need
        self._configureEolMode(originalText)
        
        self.modifiedChanged.emit(self.isModified())
        self.cursorPositionChanged.emit(*self.cursorPosition())

    def _initQsciShortcuts(self):
        """Clear default QScintilla shortcuts, and restore only ones, which are needed for MkS.
        
        Other shortcuts are disabled, or are configured with mks.plugins.editorshortcuts and defined here
        """
        qsci = self.qscintilla
        
        leaveDefaults = set([\
            "Move down one line", "Move up one line", "Move left one character", "Move right one character",
            "Extend selection down one line", "Extend selection up one line", 
                "Extend selection left one character", "Extend selection right one character",
            "Move left one word", "Move right one word",
                "Extend selection left one word", "Extend selection right one word",
            "Move down one page", "Move up one page",
                "Extend selection down one page", "Extend selection up one page",
            "Move to first visible character in line", "Move to end of line",
                "Extend selection to first visible character in line", "Extend selection to end of line",
            "Move to start of text", "Move to end of text",
                "Extend selection to start of text", "Extend selection to end of text",
            "Indent one level", "Move back one indentation level",
            "Insert new line",
            "Cancel",
            "Delete current character", "Delete previous character",
            "Delete word to right", "Delete word to left",
            "Select all text"
            ])

        for command in qsci.standardCommands().commands():
            if not command.description() in leaveDefaults:
                command.setKey(0)
                command.setAlternateKey(0)
        
        for key in range(ord('A'), ord('Z')):
            for modifier in [qsci.SCMOD_CTRL | qsci.SCMOD_ALT,
                             qsci.SCMOD_CTRL | qsci.SCMOD_SHIFT,
                             qsci.SCMOD_ALT | qsci.SCMOD_SHIFT,
                             qsci.SCMOD_CTRL | qsci.SCMOD_ALT | qsci.SCMOD_SHIFT]:
                qsci.SendScintilla(qsci.SCI_ASSIGNCMDKEY,
                                   key + (modifier << 16),
                                   qsci.SCI_NULL)

    def applySettings(self):  # pylint: disable=R0912,R0915
        """Apply own settings form the config
        """
        myConfig = core.config()["Editor"]

        if myConfig["ShowLineNumbers"] and not self._terminalWidget:
            self.qscintilla.linesChanged.connect(self._onLinesChanged)
            self._onLinesChanged()
        else:
            try:
                self.qscintilla.linesChanged.disconnect(self._onLinesChanged)
            except TypeError:  # not connected
                pass
            self.qscintilla.setMarginWidth(0, 0)
        
        if myConfig["EnableCodeFolding"] and not self._terminalWidget:
            self.qscintilla.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        else:
            self.qscintilla.setFolding(QsciScintilla.NoFoldStyle)
        
        self.qscintilla.setSelectionBackgroundColor(QColor(myConfig["SelectionBackgroundColor"]))
        self.qscintilla.setSelectionForegroundColor(QColor(myConfig["SelectionForegroundColor"]))
        if myConfig["DefaultDocumentColours"]:
            # set scintilla default colors
            self.qscintilla.setColor(QColor(myConfig["DefaultDocumentPen"]))
            self.qscintilla.setPaper(QColor(myConfig["DefaultDocumentPaper"]))

        self.qscintilla.setFont(QFont(myConfig["DefaultFont"], myConfig["DefaultFontSize"]))
        # Auto Completion
        if myConfig["AutoCompletion"]["Enabled"] and not self._terminalWidget:
            self.qscintilla.setAutoCompletionSource(\
                                            self._AUTOCOMPLETION_MODE_TO_QSCI[myConfig["AutoCompletion"]["Source"]])
            self.qscintilla.setAutoCompletionThreshold(myConfig["AutoCompletion"]["Threshold"])
            self.qscintilla.setAutoCompletionCaseSensitivity(myConfig["AutoCompletion"]["CaseSensitivity"])
            self.qscintilla.setAutoCompletionReplaceWord(myConfig["AutoCompletion"]["ReplaceWord"])
            self.qscintilla.setAutoCompletionShowSingle(myConfig["AutoCompletion"]["ShowSingle"])
        else:
            self.qscintilla.setAutoCompletionSource(QsciScintilla.AcsNone)
        
        # CallTips
        if myConfig["CallTips"]["Enabled"]:
            self.qscintilla.setCallTipsStyle(self._CALL_TIPS_STYLE_TO_QSCI[myConfig["CallTips"]["Style"]])
            self.qscintilla.setCallTipsVisible(myConfig["CallTips"]["VisibleCount"])
            self.qscintilla.setCallTipsBackgroundColor(QColor(myConfig["CallTips"]["BackgroundColor"]))
            self.qscintilla.setCallTipsForegroundColor(QColor(myConfig["CallTips"]["ForegroundColor"]))
            self.qscintilla.setCallTipsHighlightColor(QColor(myConfig["CallTips"]["HighlightColor"]))
        else:
            self.qscintilla.setCallTipsStyle(QsciScintilla.CallTipsNone)

        # Indentation
        self.qscintilla.setAutoIndent(myConfig["Indentation"]["AutoIndent"])
        self.qscintilla.setBackspaceUnindents(myConfig["Indentation"]["BackspaceUnindents"])
        self.qscintilla.setIndentationGuides(myConfig["Indentation"]["Guides"])
        self.qscintilla.setIndentationGuidesBackgroundColor(QColor(myConfig["Indentation"]["GuidesBackgroundColor"]))
        self.qscintilla.setIndentationGuidesForegroundColor(QColor(myConfig["Indentation"]["GuidesForegroundColor"]))
        self.qscintilla.setIndentationsUseTabs(myConfig["Indentation"]["UseTabs"])
        self.qscintilla.setIndentationWidth(myConfig["Indentation"]["Width"])
        self.qscintilla.setTabWidth(myConfig["Indentation"]["Width"])
        self.qscintilla.setTabIndents(myConfig["Indentation"]["TabIndents"])

        # Brace Matching
        if myConfig["BraceMatching"]["Enabled"]:
            self.qscintilla.setBraceMatching(self._BRACE_MATCHING_TO_QSCI[myConfig["BraceMatching"]["Mode"]])
            self.qscintilla.setMatchedBraceBackgroundColor(QColor(myConfig["BraceMatching"]["MatchedBackgroundColor"]))
            self.qscintilla.setMatchedBraceForegroundColor(QColor(myConfig["BraceMatching"]["MatchedForegroundColor"]))
            self.qscintilla.setUnmatchedBraceBackgroundColor(\
                                                        QColor(myConfig["BraceMatching"]["UnmatchedBackgroundColor"]))
            self.qscintilla.setUnmatchedBraceForegroundColor(\
                                                        QColor(myConfig["BraceMatching"]["UnmatchedForegroundColor"]))
        else:
            self.qscintilla.setBraceMatching(QsciScintilla.NoBraceMatch)
        
        # Edge Mode
        if myConfig["Edge"]["Enabled"]:
            self.qscintilla.setEdgeMode(self._EDGE_MODE_TO_QSCI[myConfig["Edge"]["Mode"]])
            self.qscintilla.setEdgeColor(QColor(myConfig["Edge"]["Color"]))
            self.qscintilla.setEdgeColumn(myConfig["Edge"]["Column"])
        else:
            self.qscintilla.setEdgeMode(QsciScintilla.EdgeNone)

        # Caret
        self.qscintilla.setCaretLineVisible(myConfig["Caret"]["LineVisible"])
        self.qscintilla.setCaretLineBackgroundColor(QColor(myConfig["Caret"]["LineBackgroundColor"]))
        self.qscintilla.setCaretForegroundColor(QColor(myConfig["Caret"]["ForegroundColor"]))
        self.qscintilla.setCaretWidth(myConfig["Caret"]["Width"])
        
        # Special Characters
        self.qscintilla.setWhitespaceVisibility(self._WHITE_MODE_TO_QSCI[myConfig["WhitespaceVisibility"]])
        
        if myConfig["Wrap"]["Enabled"]:
            self.qscintilla.setWrapMode(self._WRAP_MODE_TO_QSCI[myConfig["Wrap"]["Mode"]])
            self.qscintilla.setWrapVisualFlags(self._WRAP_FLAG_TO_QSCI[myConfig["Wrap"]["EndVisualFlag"]],
                                               self._WRAP_FLAG_TO_QSCI[myConfig["Wrap"]["StartVisualFlag"]],
                                               myConfig["Wrap"]["LineIndentWidth"])
        else:
            self.qscintilla.setWrapMode(QsciScintilla.WrapNone)

    def _convertIndentation(self):
        """Try to fix indentation mode of the file, if there are mix of different indentation modes
        (tabs and spaces)
        """
        # get original text
        originalText = self.qscintilla.text()
        # all modifications must believe as only one action
        self.qscintilla.beginUndoAction()
        # get indent width
        indentWidth = self.qscintilla.indentationWidth()
        
        if indentWidth == 0:
            indentWidth = self.qscintilla.tabWidth()
        
        # iterate each line
        for i in range(self.qscintilla.lines()):
            # get current line indent width
            lineIndent = self.qscintilla.indentation(i)
            # remove indentation
            self.qscintilla.setIndentation(i, 0)
            # restore it with possible troncate indentation
            self.qscintilla.setIndentation(i, lineIndent)
        
        # end global undo action
        self.qscintilla.endUndoAction()
        # compare original and newer text
        if  originalText == self.qscintilla.text():
            # clear undo buffer
            self.qscintilla.SendScintilla(QsciScintilla.SCI_EMPTYUNDOBUFFER)
            # set unmodified
            self._setModified(False)
        else:
            core.mainWindow().appendMessage('Indentation converted. You can Undo the changes', 5000)

    def _onLinesChanged(self):
        """Handler of change of lines count in the qscintilla
        """
        digitsCount = len(str(self.qscintilla.lines()))
        if digitsCount:
            digitsCount += 1
        self.qscintilla.setMarginWidth(0, '0' * digitsCount)

    #
    # AbstractDocument interface
    #
    
    def _setModified(self, modified):
        """Update modified state for the file. Called by AbstractTextEditor, must be implemented by the children
        """
        self.qscintilla.setModified(modified)

    def isModified(self):
        """Check is file has been modified
        """
        return self.qscintilla.isModified()
    
    #
    # AbstractTextEditor interface
    #
    
    def eolMode(self):
        """Line end mode of the file
        """
        return self._eolMode

    def setEolMode(self, mode):
        """Set line end mode of the file
        """
        self.qscintilla.setEolMode(self._EOL_CONVERTOR_TO_QSCI[mode])
        self.qscintilla.convertEols(self._EOL_CONVERTOR_TO_QSCI[mode])
        self._eolMode = mode

    def indentWidth(self):
        """Indentation width in symbol places (spaces)
        """
        return self.qscintilla.indentationWidth()
    
    def _applyIndentWidth(self, width):
        """Set indentation width in symbol places (spaces)
        """
        return self.qscintilla.setIndentationWidth(width)
    
    def indentUseTabs(self):
        """Indentation uses Tabs instead of Spaces
        """
        return self.qscintilla.indentationsUseTabs()
    
    def _applyIndentUseTabs(self, use):
        """Set iindentation mode (Tabs or spaces)
        """
        return self.qscintilla.setIndentationsUseTabs(use)
    
    def _applyHighlightingLanguage(self, language):
        """Set programming language of the file.
        Called Only by :mod:`mks.plugins.associations` to select syntax highlighting language.
        """
        self.lexer.applyLanguage(language)

    def text(self):
        """Contents of the editor
        """
        text = self.qscintilla.text()
        lines = text.splitlines()
        if text.endswith('\r') or text.endswith('\n'):
               lines.append('')
        return '\n'.join(lines)
    
    def setText(self, text):
        """Set text in the QScintilla, clear modified flag, update line numbers bar
        """
        self.qscintilla.setText(text)
        self.qscintilla.linesChanged.emit()
        self._setModified(False)

    def selectedText(self):
        """Get selected text
        """
        return self.qscintilla.selectedText()
        
    def selection(self):
        """Get coordinates of selected area as ((startLine, startCol), (endLine, endCol))
        """
        startLine, startCol, endLine, endCol = self.qscintilla.getSelection()
        if startLine == -1:
            cursorPos = self.cursorPosition()
            return (cursorPos, cursorPos)

        return ((startLine, startCol), (endLine, endCol))

    def absSelection(self):
        """Get coordinates of selected area as (startAbsPos, endAbsPos)
        """
        start, end = self.selection()
        return (self._toAbsPosition(*start), self._toAbsPosition(*end))

    def cursorPosition(self):
        """Get cursor position as tuple (line, col)
        """
        line, col = self.qscintilla.getCursorPosition()
        return line, col
    
    def _setCursorPosition(self, line, col):
        """Implementation of AbstractTextEditor.setCursorPosition
        """
        self.qscintilla.setCursorPosition(line, col)
        self.qscintilla.ensureLineVisible(line)

    def replaceSelectedText(self, text):
        """Replace selected text with text
        """
        self.qscintilla.beginUndoAction()
        self.qscintilla.removeSelectedText()
        self.qscintilla.insert(text)
        self.qscintilla.endUndoAction()
    
    def _replace(self, startAbsPos, endAbsPos, text):
        """Replace text at position with text
        """
        startLine, startCol = self._toLineCol(startAbsPos)
        endLine, endCol = self._toLineCol(endAbsPos)
        self.qscintilla.setSelection(startLine, startCol,
                                     endLine, endCol)
        self.replaceSelectedText(text)
    
    def beginUndoAction(self):
        """Start doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        
        DO NOT FORGET to call **endUndoAction()** after you have finished
        """
        self.qscintilla.beginUndoAction()

    def endUndoAction(self):
        """Finish doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        """
        self.qscintilla.endUndoAction()

    def _goTo(self, line, column, selectionLine = None, selectionCol = None):
        """Go to specified line and column. Select text if necessary
        """
        if selectionLine is None:
            self.qscintilla.setCursorPosition(line, column)
        else:
            self.qscintilla.setSelection(selectionLine, selectionCol,
                                         line, column)
        self.qscintilla.ensureLineVisible(line)
    
    def lineCount(self):
        """Get line count
        """
        return self.qscintilla.lines()

    def printFile(self):
        """Print file
        """
        printer = QsciPrinter()
        
        # set wrapmode
        printer.setWrapMode(QsciScintilla.WrapWord)

        dialog = QPrintDialog (printer)
        
        if dialog.exec_() == dialog.Accepted:
            if  dialog.printRange() == dialog.Selection:
                f, unused, t, unused1 = self.qscintilla.getSelection()
            else:
                f = -1
                t = -1

            printer.printRange(self.qscintilla, f, t)

    #
    # Public methods for editorshortcuts
    #
    
    def toggleBookmark(self):
        """Set or clear bookmark on the line
        """
        if self._terminalWidget:
            return

        row = self.qscintilla.getCursorPosition()[0]
        if self.qscintilla.markersAtLine(row) & 1 << self._MARKER_BOOKMARK:
            self.qscintilla.markerDelete(row, self._MARKER_BOOKMARK)
        else:
            self.qscintilla.markerAdd(row, self._MARKER_BOOKMARK)
        
    def nextBookmark(self):
        """Move to the next bookmark
        """
        row = self.qscintilla.getCursorPosition()[0]
        self.qscintilla.setCursorPosition(
                    self.qscintilla.markerFindNext(row + 1, 1 << self._MARKER_BOOKMARK), 0)
        
    def prevBookmark(self):
        """Move to the previous bookmark
        """
        row = self.qscintilla.getCursorPosition()[0]
        self.qscintilla.setCursorPosition(
                    self.qscintilla.markerFindPrevious(row - 1, 1 << self._MARKER_BOOKMARK), 0)

    def _moveLines(self, disposition):
        """Move selected lines down
        """
        clipboard = qApp.clipboard()
        selectionBuffer = clipboard.text(clipboard.Selection)
        copyBuffer = clipboard.text(clipboard.Clipboard)
        start, end = self.selection()
        startLine, startCol = start
        endLine, endCol = end
        
        if startLine == endLine and startCol == endCol:  # empty selection, select 1 line
            endCol = len(self.line(endLine))
        
        startCol = 0  # always cut whole line
        if endCol > 0:
            if (endLine + 1) < self.lineCount():
                # expand to line end (with \n)
                endCol = 0
                endLine += 1
            else:
                # expand to line end WITHOUT \n
                endCol = len(self.line(endLine))

        if startLine != endLine or startCol != endCol:  # if have text to move
            if disposition < 0:  # move up
                canMove = startLine + disposition >= 0
            else:  # move down
                endAbsPos = self._toAbsPosition(endLine, endCol)
                canMove = endAbsPos + 1 < len(self.text())
            
            if canMove:
                self.beginUndoAction()
                self.qscintilla.setSelection(startLine, startCol, endLine, endCol)
                self.qscintilla.cut()
                
                # add missing line to end before pasting, if necessary
                if self.lineCount() <= startLine + disposition:
                    lineBefore = startLine + disposition - 1
                    self.setCursorPosition(line=lineBefore,
                                           column = len(self.line(lineBefore)))
                    self.qscintilla.insert('\n')
                    newlineAddedWhenCut = True
                else:
                    newlineAddedWhenCut = False

                self.setCursorPosition(line=startLine + disposition, column = 0)
                text = qApp.clipboard().text()
                if not text.endswith('\n'):  # if copied line without \n, add it
                    text += '\n'
                
                if newlineAddedWhenCut:
                    text = text[:-1]
                
                self.qscintilla.insert(text)
                self.qscintilla.setSelection(startLine + disposition, startCol, endLine + disposition, endCol)
                self.endUndoAction()
                clipboard.setText(selectionBuffer, clipboard.Selection)
                clipboard.setText(copyBuffer, clipboard.Clipboard)

    def moveLinesDown(self):
        """Move selected lines down
        """
        return self._moveLines(1)

    def moveLinesUp(self):
        """Move selected lines up
        """
        return self._moveLines(-1)
