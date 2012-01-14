"""
termwidget --- Terminal emulator widget
=======================================

Shows intput and output text. Allows to enter commands. Supports history.

This widget only provides GUI, but does not implement any system terminal or other functionality
"""

import cgi

from PyQt4.QtCore import pyqtSignal, QEvent
from PyQt4.QtGui import QColor, QKeySequence, QLineEdit, QPalette, \
                        QSizePolicy, QTextCursor, QTextEdit, \
                        QVBoxLayout, QWidget

from mks.core.core import core

class TermWidget(QWidget):
    """Widget wich represents terminal. It only displays text and allows to enter text.
    All highlevel logic should be implemented by client classes
    
    Text editor class must be set when initializing TermWidget. See Workspace.setTextEditorClass()  # TODO link
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self._browser = QTextEdit(self)
        self._browser.setReadOnly(True)
        self._browser.document().setDefaultStyleSheet(self._browser.document().defaultStyleSheet() + 
                                                      "span {white-space:pre;}")

        self._edit = core.workspace().textEditorClass()(self, None, terminalWidget=True)
        self._edit.widget().installEventFilter(self)
        self._edit.newLineInserted.connect(self._onEditNewLine)
        self.setFocusProxy(self._edit)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._browser)
        layout.addWidget(self._edit)
        
        self._history = ['']  # current empty line
        self._historyIndex = 0
        
        self._edit.setFocus()

    def eventFilter(self, obj, event):
        """Catches _edit key pressings. Processes some of them
        """
        if event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.MoveToNextLine):
                if self._edit.cursorPosition()[0] == self._edit.lineCount():
                    self._onHistoryNext()
                    return True
            elif event.matches(QKeySequence.MoveToPreviousLine):
                if self._edit.cursorPosition()[0] == 1:
                    self._onHistoryPrev()
                    return True
            elif event.matches(QKeySequence.MoveToNextPage) or \
                 event.matches(QKeySequence.MoveToPreviousPage):
                self._browser().keyPressEvent(event)
                return True
        
        return QWidget.eventFilter(self, obj, event)

    def _appendToBrowser(self, style, text):
        """Convert text to HTML for inserting it to browser. Insert the HTML
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
    
    def setLanguage(self, language):
        """Set highlighting language for input widget
        """
        self._edit.setHighlightingLanguage(language)

    def execCurrentCommand(self):
        """Save current command in the history. Append it to the log. Clear edit line
        Reimplement in the child classes to actually execute command
        """
        text = self._edit.text()
        text = text[:text.rindex('\n')]
        self._appendToBrowser('in', text + '\n')

        if len(self._history) < 2 or\
           self._history[-2] != text:  # don't insert duplicating items
            self._history.insert(-1, text)

        self._historyIndex = len(self._history) - 1
        
        self._history[-1] = ''
        self._edit.setText('')
        
        if not text.endswith('\n'):
            text += '\n'

        self.childExecCommand(text)
    
    def childExecCommand(self, text):
        """Reimplement in the child classes to execute enterred commands
        """
        pass

    def appendOutput(self, text):
        """Appent text to output widget
        """
        self._appendToBrowser('out', text)

    def appendError(self, text):
        """Appent error text to output widget. Text is drawn with red background
        """
        self._appendToBrowser('err', text)

    def isCommandComplete(self, text):
        """Executed by _ExpandableTextEdit when Enter is pressed.
        Implement this function in the child classes.
        """
        return True
    
    def _onEditNewLine(self):
        """Handler of Enter pressing in the edit
        """
        text = self._edit.text()
        if self.isCommandComplete(text):
            self.execCurrentCommand()

    def _onHistoryNext(self):
        """Down pressed, show next item from the history
        """
        if (self._historyIndex + 1) < len(self._history):
            self._historyIndex += 1
            self._edit.setText(self._history[self._historyIndex])
            self._edit.goTo(absPos=len(self._edit.text()))

    def _onHistoryPrev(self):
        """Up pressed, show previous item from the history
        """
        if self._historyIndex > 0:
            if self._historyIndex == (len(self._history) - 1):
                self._history[-1] = self._edit.text()
            self._historyIndex -= 1
            self._edit.setText(self._history[self._historyIndex])
            self._edit.goTo(absPos=len(self._edit.text()))
