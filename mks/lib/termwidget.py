"""Terminal emulator widget.
Shows intput and output text. Allows to enter commands. Supports history.
"""

import cgi

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QColor, QKeySequence, QLineEdit, QPalette, \
                        QSizePolicy, QTextCursor, QTextEdit, \
                        QVBoxLayout, QWidget

class _ExpandableTextEdit(QTextEdit):
    """Class implements edit line, which expands themselves automatically
    """
    
    historyNext = pyqtSignal()
    historyPrev = pyqtSignal()
    
    def __init__(self, termWidget, *args):
        QTextEdit.__init__(self, *args)
        self._termWidget = termWidget
        self._fittedHeight = 0
        self.textChanged.connect(self._fitToDocument)

    def sizeHint(self):
        """QWidget sizeHint impelemtation
        """
        hint = QTextEdit.sizeHint(self)
        hint.setHeight(self._fittedHeight)
        return hint
    
    def showEvent(self, event):  # TO fight fucking flickering, when settings are applied and widget is recreated
        QWidget.showEvent(self, event)
        self._fitToDocument()

    def _fitToDocument(self):
        """Update widget height to fit all text
        """
        documentSize = self.document().size().toSize()
        self.updateGeometry()
        fittedHeight = documentSize.height() + (self.height() - self.viewport().height())
        if fittedHeight > 10:
            self._fittedHeight = fittedHeight
            self.setMaximumHeight(self._fittedHeight)
            self.updateGeometry()
    
    def keyPressEvent(self, event):
        """Catch keywoard events. Process Enter, Up, Down
        """
        if event.matches(QKeySequence.InsertParagraphSeparator):
            text = self.toPlainText()
            if self._termWidget.isCommandComplete(text):
                self._termWidget.execCurrentCommand()
                return
        elif event.matches(QKeySequence.MoveToNextLine):
            text = self.toPlainText()
            cursorPos = self.textCursor().position()
            textBeforeEnd = text[cursorPos:]
            if len(textBeforeEnd.splitlines()) <= 1:
                self.historyNext.emit()
                return
        elif event.matches(QKeySequence.MoveToPreviousLine):
            text = self.toPlainText()
            cursorPos = self.textCursor().position()
            textBeforeStart = text[:cursorPos]
            lineCount = len(textBeforeStart.splitlines())
            if textBeforeStart.endswith('\n') or textBeforeStart.endswith('\r'):
                lineCount += 1
            if lineCount <= 1:
                self.historyPrev.emit()
                return
        elif event.matches(QKeySequence.MoveToNextPage) or \
             event.matches(QKeySequence.MoveToPreviousPage):
            return self._termWidget.browser().keyPressEvent(event)
        
        QTextEdit.keyPressEvent(self, event)

class TermWidget(QWidget):
    """Widget wich represents terminal. It only displays text and allows to enter text.
    All highlevel logic should be implemented by client classes

    User pressed Enter. Client class should decide, if command must be executed or user may continue edit it
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self._browser = QTextEdit(self)
        self._browser.setReadOnly(True)
        self._browser.document().setDefaultStyleSheet(self._browser.document().defaultStyleSheet() + 
                                                      "span {white-space:pre;}")

        self._edit = _ExpandableTextEdit(self, self)
        self._edit.historyNext.connect(self._onHistoryNext)
        self._edit.historyPrev.connect(self._onHistoryPrev)
        self.setFocusProxy(self._edit)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._browser)
        layout.addWidget(self._edit)
        
        self._history = ['']  # current empty line
        self._historyIndex = 0
        
        self._edit.setFocus()

    def _appendToBrowser(self, style, text):
        """Convert text to HTML for inserting it to browser
        """
        assert style in ('in', 'out', 'err')

        text = cgi.escape(text)
        
        text = text.replace('\n', '<br/>')
        
        if style != 'out':
            defBg = self._browser.palette().color(QPalette.Base)
            h, s, v, a = defBg.getHsvF()
            
            if style == 'in':
                if v > 0.5:  # white background
                    v = v - (v / 8)  # make darker
                else:
                    v = v + ((1 - v) / 4)  # make ligher
            else:  # err
                if v < 0.5:
                    v = v + ((1 - v) / 4)  # make ligher

                if h == -1:  # make red
                    h = 0
                    s = .4
                else:
                    h = h + ((1 - h) * 0.5)  # make more red
            
            bg = QColor.fromHsvF(h, s, v).name()
            text = '<span style="background-color: %s;">%s</span>' % (bg, text)
        else:
            text = '<span>%s</span>' % text  # without span <br/> is ignored!!!
        
        scrollBar = self._browser.verticalScrollBar()
        oldValue = scrollBar.value()
        scrollAtTheEnd = oldValue == scrollBar.maximum()
        
        self._browser.moveCursor(QTextCursor.End)
        self._browser.insertHtml(text)
        
        """TODO When user enters second line to the input, and input is resized, scrollbar changes its positon
        and stops moving. As quick fix of this problem, now we always scroll down when add new text.
        To fix it correctly, srcoll to the bottom, if before intput has been resized, 
        scrollbar was in the bottom, and remove next lien
        """
        scrollAtTheEnd = True
        
        if scrollAtTheEnd:
            scrollBar.setValue(scrollBar.maximum())
        else:
            scrollBar.setValue(oldValue)
            

    def execCurrentCommand(self):
        """Save current command in the history. Append it to the log. Clear edit line
        Reimplement in the child classes to actually execute command
        """
        text = self._edit.toPlainText()
        self._appendToBrowser('in', text + '\n')

        if len(self._history) < 2 or\
           self._history[-2] != text:  # don't insert duplicating items
            self._history.insert(-1, text)

        self._historyIndex = len(self._history) - 1
        
        self._history[-1] = ''
        self._edit.clear()
        
        if not text.endswith('\n'):
            text += '\n'

        self.childExecCommand(text)
    
    def childExecCommand(self, text):
        """Reimplement in the child classes
        """
        pass
    
    def addLineBreakToInput(self):
        self._edit.textCursor().insertText('\n')

    def appendOutput(self, text):
        """Appent text to output widget
        """
        self._appendToBrowser('out', text)

    def appendError(self, text):
        """Appent error text to output widget. Text is drawn with red background
        """
        self._appendToBrowser('err', text)

    def isCommandComplete(self, text):
        """Executed by _ExpandableTextEdit. Reimplement this function in the child classes.
        """
        return True
    
    def browser(self):
        return self._browser

    def _onHistoryNext(self):
        """Down pressed, show next item from the history
        """
        if (self._historyIndex + 1) < len(self._history):
            self._historyIndex += 1
            self._edit.setPlainText(self._history[self._historyIndex])
            self._edit.moveCursor(QTextCursor.End)

    def _onHistoryPrev(self):
        """Up pressed, show previous item from the history
        """
        if self._historyIndex > 0:
            if self._historyIndex == (len(self._history) - 1):
                self._history[-1] = self._edit.toPlainText()
            self._historyIndex -= 1
            self._edit.setPlainText(self._history[self._historyIndex])
            self._edit.moveCursor(QTextCursor.End)
