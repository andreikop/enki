"""
locator --- Locator dialog and functionality
============================================

Implements widget, which appears, when you press Ctrl+L and it's functionality

Contains definition of AbstractCommand and AbstractCompleter interfaces
"""



from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QModelIndex, QSize, Qt
from PyQt4.QtGui import QApplication, QDialog, QFontMetrics, QPalette, QSizePolicy, QStyle, \
                        QStyle, QStyleOptionFrameV2, \
                        QTextCursor, QTextEdit, QTextOption, QTreeView, QVBoxLayout

import os

from pyparsing import Optional, Or, ParseException, StringEnd, White

from mks.core.core import core
from mks.lib.htmldelegate import HTMLDelegate

class AbstractCommand:
    """Base class for Locator commands.
    
    Inherit it to create own commands. Than add your command with Locator.addCommandClass()
    """
    
    @staticmethod
    def signature():
        """Command signature. Shown in the Help. Example:
        
        '[f] PATH [LINE]'
        """
        raise NotImplemented()
    
    @staticmethod
    def description():
        """Command description. Shown in the Help. Example:
        
        'Open file. Globs are supported'
        """
        raise NotImplemented()

    @staticmethod
    def pattern():
        """pyparsing pattern, which recognizes and constructs commands.
        
        See TODO LINK workspace_commands as example
        """
        raise NotImplemented()
    
    def completer(self, text, pos):
        """TODO LINK Completer instance for partially typed command.
        
        Return None, if your command doesn't have completer, or if completion is not available now
        """
        return None

    @staticmethod
    def isAvailable():
        """Check if command is available now.
        
        i.e. SaveAs command is not available, if not files are opened
        """
        return True
    
    def constructCommand(self, completableText):
        """After user clicked item on the TreeView, Locator
        
        1) gets item full text with AbstractCompleter.getFullText() method
        2) constructs a command with this text using currentCommand.constructCommand()
        3) sets command to the LineEdit
        4) tries to execute the command
        """
        return None

    def isReadyToExecute(self):
        """Check if command is ready to execute.
        
        It is ready, when it is complete (contains all mandatory arguments) and arguments are valid
        """
        return True

    def execute(self):
        """Execute the command
        """
        raise NotImplemented()


class AbstractCompleter:
    """Completer for Locator.
    
    Provides:
    * inline completion
    * command(s) description
    * status and any other information from command
    * list of possible completions
    """
    
    def rowCount(self):
        """Row count for TreeView
        """
        raise NotImplemented()
    
    def columnCount(self):
        """Column count for tree view. Default is 1
        """
        return 1
    
    def text(self, row, column):
        """Text for TreeView item
        """
        raise NotImplemented()
    
    def icon(self, row, column):
        """Icon for TreeView item. Default is None
        """
        return None
    
    def inline(self):
        """Inline completion.
        
        Shown after cursor. Appedned to the typed text, if Tab is pressed
        """
        return None
    
    def getFullText(self, row):
        """Row had been clicked by mouse. Get inline completion, which will be inserted after cursor
        """
        return None


class _HelpCompleter(AbstractCompleter):
    """AbstractCompleter implementation, which shows help about all or one command
    """
    def __init__(self, commands):
        self._commands = commands
    
    def rowCount(self):
        """AbstractCompleter method implementation
        
        Return count of available commands
        """
        return len(self._commands)
    
    def columnCount(self):
        """AbstractCompleter method implementation
        """
        return 2
    
    def text(self, row, column):
        """AbstractCompleter method implementation
        
        Return command description
        """
        if column == 0:
            return self._commands[row].signature()
        else:
            return self._commands[row].description()


class _CompleterModel(QAbstractItemModel):
    """QAbstractItemModel implementation.
    
    Adapter between complex and not intuitive QAbstractItemModel interface 
    and simple AbstractCompleter interface.
    Provides data for TreeView with completions and information
    """

    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.completer = None

    def index(self, row, column, parent):
        """QAbstractItemModel method implementation
        """
        return self.createIndex(row, column)
    
    def parent(self, index):
        """QAbstractItemModel method implementation
        """
        return QModelIndex()
    
    def rowCount(self, index):
        """QAbstractItemModel method implementation
        """
        if index.isValid():
            return 0
        if self.completer is None:
            return 0
        
        return self.completer.rowCount()
    
    def columnCount(self, index):
        """QAbstractItemModel method implementation
        """
        if self.completer is None:
            return 0
        return self.completer.columnCount()
    
    def data(self, index, role):
        """QAbstractItemModel method implementation
        """
        if self.completer is None:
            return None
        if role == Qt.DisplayRole:
            return self.completer.text(index.row(), index.column())
        elif role == Qt.DecorationRole:
            return self.completer.icon(index.row(), index.column())
        return None
    
    def setCompleter(self, completer):
        """Set completer, which will be used as data source
        """
        self.completer = completer
        self.modelReset.emit()


class _CompletableLineEdit(QTextEdit):
    """Locator line edit.
    
    Based on QTextEdit, because needs HTML support
    
    Supports inline completion, emits signals when user wants to roll history or execute command
    """
    
    """Text changed or cursor moved. Update completion
    """
    updateCompletion = pyqtSignal()
    
    """Enter pressed. Execute command, if complete
    """
    enterPressed = pyqtSignal()
    
    """Up pressed, roll history
    """
    historyPrevious = pyqtSignal()
    """Down pressed, roll history
    """
    historyNext = pyqtSignal()
    
    def __init__(self, *args):
        QTextEdit.__init__(self, *args)
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(self.sizeHint().height())
        self._inlineCompletion = None

    def sizeHint(self):
        """QWidget.sizeHint implementation. Returns height of 1 line of text
        """
        fm = QFontMetrics(self.font())
        h = fm.height() + 4
        w = fm.width('x' * 64)
        opt = QStyleOptionFrameV2()
        opt.initFrom(self);
        return self.style().sizeFromContents(QStyle.CT_LineEdit,
                                             opt,
                                             QSize(w, h).expandedTo(QApplication.globalStrut()),
                                             self)

    def event(self, event):
        """QObject.event implementation. Catches Tab events
        """
        if event.type() == event.KeyPress and \
           event.key() == Qt.Key_Tab:
            if self._inlineCompletion is not None:
                color = self.palette().color(QPalette.Base).name()
                self.insertHtml('<font style="background-color: %s">%s</font>' % (color, self._inlineCompletion))
                self._clearInlineCompletion()
                self.updateCompletion.emit()
            return True
        else:
            return QTextEdit.event(self, event)
    
    def keyPressEvent(self, event):
        """QWidget.keyPressEvent implementation. Catches Return, Up, Down, Ctrl+Backspace
        """
        self._clearInlineCompletion()
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.enterPressed.emit()
        elif event.key() == Qt.Key_Up:
            self.historyPrevious.emit()
        elif event.key() == Qt.Key_Down:
            self.historyNext.emit()
        elif event.key() == Qt.Key_Backspace and \
             event.modifiers() == Qt.ControlModifier:
            # Ctrl+Backspace. Usualy deletes word, but, for this edit should delete path level
            pos = self.textCursor().position()
            textBefore = self.toPlainText()[:pos - 1]  # -1 to ignore / at the end
            slashIndex = textBefore.rfind('/')
            spaceIndex = textBefore.rfind(' ')
            if slashIndex != -1 and slashIndex > spaceIndex:
                self._deleteToSlash()
            else:
                QTextEdit.keyPressEvent(self, event)
        else:
            QTextEdit.keyPressEvent(self, event)
        self.updateCompletion.emit()
    
    def _deleteToSlash(self):
        """Delete back until /. Called on Ctrl+Backspace pressing
        """
        text = self.toPlainText()
        cursor = self.textCursor()
        cursorPos = cursor.position()
        slashPos = text.rfind('/', 0, cursorPos - 1)
        cursor.movePosition(cursor.Left, cursor.KeepAnchor, cursorPos - slashPos - 1)
        cursor.removeSelectedText()
    
    def mousePressEvent(self, event):
        """Mouse event handler.
        Removed inline completion before processing event
        """
        self._clearInlineCompletion()
        QTextEdit.mousePressEvent(self, event)
        if self.textCursor().atEnd():
            self.updateCompletion.emit()

    def _clearInlineCompletion(self):
        """Remove inline completion
        """
        if self._inlineCompletion is not None:
            cursor = self.textCursor()
            for c in self._inlineCompletion:
                cursor.deleteChar()
            self._inlineCompletion = None
    
    def setInlineCompletion(self, text):
        """Set inline completion
        """
        self._inlineCompletion = text
        cursor = self.textCursor()
        pos = cursor.position()
        color = self.palette().color(QPalette.Highlight).name()
        cursor.insertHtml('<font style="background-color: %s">%s</font>' % (color, text))
        cursor.setPosition(pos)
        self.setTextCursor(cursor)
    
    def setPlainText(self, text):
        """QTextEdit.setPlainText implementation.
        Clears inline completion before setting new text
        """
        self.setInlineCompletion('')
        QTextEdit.setPlainText(self, text)
        self.moveCursor(QTextCursor.End)
    
    def insertPlainText(self, text):
        """QTextEdit.insertPlainText implementation.
        Clears inline completion before inserting new text
        """
        self._clearInlineCompletion()
        QTextEdit.insertPlainText(self, text)


class Locator(QDialog):
    """Locator widget and implementation
    """
    def __init__(self, *args):
        QDialog.__init__(self, *args)
        
        self._commandClasses = []
        self._history = ['']
        self._historyIndex = 0
        self._incompleteCommand = None
        
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(1)
        
        self._table = QTreeView(self)
        self._model = _CompleterModel()
        self._table.setModel(self._model)
        self._table.setItemDelegate(HTMLDelegate())
        self._table.setRootIsDecorated(False)
        self._table.setHeaderHidden(True)
        self._table.clicked.connect(self._onItemClicked)
        self.layout().addWidget(self._table)
        
        self._edit = _CompletableLineEdit(self)
        self.layout().addWidget(self._edit)
        self._edit.updateCompletion.connect(self._updateCompletion)
        self._edit.enterPressed.connect(self._onEnterPressed)
        self._edit.historyPrevious.connect(self._onHistoryPrevious)
        self._edit.historyNext.connect(self._onHistoryNext)
        self.setFocusProxy(self._edit)

        editSizeHint = self._edit.sizeHint()
        self.resize(editSizeHint.width(), editSizeHint.width() * 0.62)
        
        self._edit.setFocus()
        self._updateCompletion()
        
        self._action = core.actionManager().addAction("mNavigation/aLocator", "Locator", shortcut='Ctrl+L')
        self._action.triggered.connect(self._onAction)
    
    def del_(self):
        """Explicitly called destructor
        """
        core.actionManager().removeAction(self._action)
    
    def _onAction(self):
        """Locator action triggered. Show themselves and make focused
        """
        self.show()
        self._edit.setFocus()

    def _onItemClicked(self, index):
        """Item in the TreeView has been clicked.
        Open file, if user selected it
        """
        command = self._parseCommand(self._edit.toPlainText())
        if command is not None:
            newText = self._model.completer.getFullText(index.row())
            if newText is not None:
                newCommandText = command.constructCommand(newText)
                if newCommandText is not None:
                    self._edit.setPlainText(newCommandText)
                    self._edit.setFocus()
                    self._onEnterPressed()
                    self._updateCompletion()

    def _updateCompletion(self):
        """User edited text or moved cursor. Update inline and TreeView completion
        """
        text = self._edit.toPlainText()
        completer = None
        
        command = self._parseCommand(text)
        if command is not None:
            completer = command.completer(self._edit.toPlainText(), self._edit.textCursor().position())

            if completer is not None:
                inline = completer.inline()
                if inline:
                    self._edit.setInlineCompletion(inline)
            else:
                completer = _HelpCompleter([command])
        else:
            completer = _HelpCompleter(self._availableCommands())

        self._model.setCompleter(completer)
        if completer.columnCount() > 1:
            self._table.resizeColumnToContents(0)
            self._table.setColumnWidth(0, self._table.columnWidth(0) + 20)  # 20 px spacing between columns
    
    def _onEnterPressed(self):
        """User pressed Enter or clicked item. Execute command, if possible
        """
        text = self._edit.toPlainText().strip()
        command = self._parseCommand(text)
        if command is not None and command.isReadyToExecute():
            command.execute()
            self._history[-1] = text
            if len(self._history) > 1 and \
               self._history[-1].strip() == self._history[-2].strip():
                   self._history = self._history[:-1]  # if the last command repeats, remove duplicate
            self._history.append('')  # new edited command
            self._historyIndex = len(self._history) - 1
            self._edit.clear()
            self.hide()
    
    def _onHistoryPrevious(self):
        """User pressed Up. Roll history
        """
        if self._historyIndex == len(self._history) - 1:  # save edited command
            self._history[self._historyIndex] = self._edit.toPlainText()
        
        if self._historyIndex > 0:
            self._historyIndex -= 1
            self._edit.setPlainText(self._history[self._historyIndex])
    
    def _onHistoryNext(self):
        """User pressed Down. Roll history
        """
        if self._historyIndex < len(self._history) - 1:
            self._historyIndex += 1
            self._edit.setPlainText(self._history[self._historyIndex])
    
    def addCommandClass(self, commandClass):
        """Add new command to the locator. Shall be called by plugins, which provide locator commands
        """
        self._commandClasses.append(commandClass)
    
    def removeCommandClass(self, commandClass):
        """Remove command from the locator. Shall be called by plugins when terminating it
        """        
        self._commandClasses.remove(commandClass)
    
    def _availableCommands(self):
        """Get list of available commands
        """
        return [cmd for cmd in self._commandClasses if cmd.isAvailable()]

    def _parseCommand(self, text):
        """Parse text and try to get command
        """
        optWs = Optional(White()).suppress()
        pattern = optWs + Or([cmd.pattern() for cmd in self._availableCommands()]) + optWs + StringEnd()
        try:
            res = pattern.parseString(text)
            return res[0]
        except ParseException:
            return None

    def show(self):
        """QWidget.show implementation. Updates completion before showing widget
        """
        self._updateCompletion()
        QDialog.show(self)
