"""
locator --- Locator dialog and functionality
============================================

Implements widget, which appears, when you press Ctrl+L and it's functionality

Contains definition of AbstractCommand and AbstractCompleter interfaces
"""



from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QModelIndex, QSize, Qt, QTimer
from PyQt4.QtGui import QApplication, QDialog, QFontMetrics, QMessageBox, QPalette, QSizePolicy, \
                        QStyle, QStyleOptionFrameV2, \
                        QTextCursor, QLineEdit, QTextOption, QTreeView, QVBoxLayout

import os
import threading
import Queue

from enki.core.core import core
from enki.lib.htmldelegate import HTMLDelegate


class InvalidCmdArgs(UserWarning):
    pass


class AbstractCommand:
    """Base class for Locator commands.

    Inherit it to create own commands. Than add your command with Locator.addCommandClass()

    Public attributes:

    * ``command`` - Command text (first word), i.e. ``f`` for Open and ``s`` for Save
    * ``signature`` - Command signature. Shown in the Help. Example:  ``[f] PATH [LINE]``
    * ``description`` - Command description. Shown in the Help. Example: ``Open file. Globs are supported``
    * ``isDefaultCommand`` - If True, command is executed if no other command matches. Must be ``True`` for only 1 command. Currently it is Open
    """
    command = NotImplemented
    signature = NotImplemented
    description = NotImplemented
    isDefaultCommand = False

    def __init__(self, args):
        """ Construct a command insance from arguments

        Raises InvalidCmdArgs if arguments are invalid
        """
        raise NotImplemented()

    @staticmethod
    def isAvailable():
        """Check if command is available now.

        i.e. SaveAs command is not available, if not files are opened
        """
        return True

    def completer(self, argIndex):
        """ ::class:`enki.core.locator.AbstractCompleter` instance for partially typed command.

        Return None, if your command doesn't have completer, or if completion is not available now
        argIndex is an index of command argument, for which completion is required
        """
        return None

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
            return self._commands[row].signature
        else:
            return self._commands[row].description


class _StatusCompleter(AbstractCompleter):
    """AbstractCompleter implementation, which shows status message
    """
    def __init__(self, text):
        self._text = text

    def rowCount(self):
        """AbstractCompleter method implementation

        Return count of available commands
        """
        return 1

    def text(self, row, column):
        """AbstractCompleter method implementation

        Return command description
        """
        return self._text


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


class _CompletableLineEdit(QLineEdit):
    """Locator line edit.

    Based on QLineEdit, because needs HTML support

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
        QLineEdit.__init__(self, *args)
        self._inlineCompletionIsSet = False  # for differentiate inline completion and selection

    def event(self, event):
        """QObject.event implementation. Catches Tab events
        """
        if event.type() == event.KeyPress and \
           event.key() == Qt.Key_Tab:
            if self.selectedText():
                self.setCursorPosition(self.selectionStart() + len(self.selectedText()))
                self.updateCompletion.emit()
            return True
        else:
            return QLineEdit.event(self, event)

    def keyPressEvent(self, event):
        """QWidget.keyPressEvent implementation. Catches Return, Up, Down, Ctrl+Backspace
        """
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            if self._inlineCompletionIsSet:
                self.setCursorPosition(self.selectionStart() + len(self.selectedText()))
            self.enterPressed.emit()
        elif event.key() == Qt.Key_Up:
            self.historyPrevious.emit()
        elif event.key() == Qt.Key_Down:
            self.historyNext.emit()
        elif event.key() in (Qt.Key_Right, Qt.Key_End):
            if self.selectedText():
                self.setCursorPosition(self.selectionStart() + len(self.selectedText()))
            else:
                QLineEdit.keyPressEvent(self, event)
        elif event.key() == Qt.Key_Backspace and \
             event.modifiers() == Qt.ControlModifier:
            # Ctrl+Backspace. Usualy deletes word, but, for this edit should delete path level
            self._clearInlineCompletion()
            pos = self.cursorPosition()
            textBefore = self.text()[:pos - 1]  # -1 to ignore / at the end
            slashIndex = textBefore.rfind('/')
            spaceIndex = textBefore.rfind(' ')
            if slashIndex != -1 and slashIndex > spaceIndex:
                self._deleteToSlash()
            else:
                QLineEdit.keyPressEvent(self, event)
        else:
            oldTextBeforeCompletion = self.text()[:self.cursorPosition()]
            inlineCompletion = self._inlineCompletion()
            textAfterCompletion = self.text()[:self.cursorPosition() + len(inlineCompletion)]

            self._clearInlineCompletion()

            QLineEdit.keyPressEvent(self, event)

            # Inline completion will be recalculated later in the thread.
            # But, this code helps to avoid flickering in case when user typed first letter of inline completion
            textBeforeCompletion = self.text()[:self.cursorPosition()]
            if inlineCompletion and \
               len(oldTextBeforeCompletion) + 1 == len(textBeforeCompletion) and \
               textBeforeCompletion.startswith(oldTextBeforeCompletion) and \
               textBeforeCompletion[-1] == inlineCompletion[0]:
                self.setInlineCompletion(inlineCompletion[1:])  # set rest of the inline completion

        self.updateCompletion.emit()

    def _deleteToSlash(self):
        """Delete back until /. Called on Ctrl+Backspace pressing
        """
        text = self.text()
        cursorPos = self.cursorPosition()
        slashPos = text.rfind('/', 0, cursorPos - 1)
        self.setSelection(slashPos + 1, cursorPos - slashPos)
        self.del_()
        self._inlineCompletionIsSet = False

    def _clearInlineCompletion(self):
        """Clear inline completion, if exists
        """
        if self._inlineCompletionIsSet:
            self.del_()
            self._inlineCompletionIsSet = False

    def _inlineCompletion(self):
        """Get current inline completion text
        """
        if self._inlineCompletionIsSet:
            return self.selectedText()
        else:
            return ''

    def setInlineCompletion(self, text):
        """Set inline completion
        """
        if text:
            visibleText = text.replace(' ', '\\ ')
            self.insert(visibleText)
            self.setSelection(self.cursorPosition(), -len(visibleText))
            self._inlineCompletionIsSet = True
        else:
            self._clearInlineCompletion()

    def commandText(self):
        """Get text, which doesn't include inline completion
        Text is stripped
        """
        text = self.text()
        if self._inlineCompletionIsSet:
            selectionStart = self.selectionStart()
            selectionEnd = selectionStart + len(self.selectedText())
            text = text[:selectionStart] + text[selectionEnd:]
        return text


class _CompleterConstructorThread(threading.Thread):
    """Thread constructs Completer
    Sometimes it requires a lot of time, i.e. when expanding "/usr/lib/*"
    hlamer: I tried to use QThread + pyqtSignal, but got tired with crashes and deadlocks
    """

    def __init__(self, locator):
        """Works in the GUI thread
        """
        threading.Thread.__init__(self)

        self._locator = locator
        self._queue = Queue.Queue()
        self._checkQueueTimer = QTimer()
        self._checkQueueTimer.setInterval(50)
        self._checkQueueTimer.timeout.connect(self._checkQueue)

    def _checkQueue(self):
        """Check if thread constructed a completer and put it to the queue
        Works in the GUI thread
        """
        if not self._queue.empty():
            command, completer = self._queue.get()
            self._locator._applyCompleter(command, completer)

    def start(self, command, argIndex):
        """Start constructing completer
        Works in the GUI thread
        """
        self._terminated = False
        self._command = command
        self._argIndex = argIndex
        self._checkQueueTimer.start()
        threading.Thread.start(self)

    def terminate(self):
        """Set termination flag
        Works in the GUI thread
        """
        self._checkQueueTimer.stop()
        self.join()

    def run(self):
        """Thread function
        Works in NEW thread
        """
        completer = self._command.completer(self._argIndex)
        self._queue.put([self._command, completer])


def splitLine(text):
    """ Split text onto words
    Return list of (word, endIndex)
    """
    words = []  # list of tuples (text, endIndex)

    it = enumerate(text)

    def findNonSpace():
        index, char = it.next()
        while char.isspace():
            index, char = it.next()

        return index, char

    def getWord(index, char):
        word = ''
        try:
            while True:
                if char.isspace():
                    index -= 1
                    break
                elif char == '\\':
                    try:
                        index, char = it.next()
                    except StopIteration:
                        word += '\\'
                        raise
                    else:
                        word += char
                else:
                    word += char
                index, char = it.next()

        except StopIteration:
            pass

        return word, index + 1

    while True:
        try:
            nonSpaceChar, index = findNonSpace()
        except StopIteration:
            break

        words.append(getWord(nonSpaceChar, index))

    return words



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

        width = QFontMetrics(self.font()).width('x' * 64)  # width of 64 'x' letters
        self.resize(width, width * 0.62)

        self._action = core.actionManager().addAction("mNavigation/aLocator", "Locator", shortcut='Ctrl+L')
        self._action.triggered.connect(self._onAction)
        self._separator = core.actionManager().menu("mNavigation").addSeparator()

        # without it action works only when main window is focused, and user can't move focus, when tree is focused
        self.addAction(self._action)

        self._loadingTimer = QTimer(self)
        self._loadingTimer.setSingleShot(True)
        self._loadingTimer.setInterval(200)
        self._loadingTimer.timeout.connect(self._applyLoadingCompleter)

        self._completerConstructorThread = None


    def del_(self):
        """Explicitly called destructor
        """
        core.actionManager().removeAction(self._action)
        core.actionManager().menu("mNavigation").removeAction(self._separator)

        if self._completerConstructorThread is not None:
            self._completerConstructorThread.terminate()

    def _onAction(self):
        """Locator action triggered. Show themselves and make focused
        """
        self._edit.setFocus()
        if not self.isVisible():
            self.exec_()

    def _onItemClicked(self, index):
        """Item in the TreeView has been clicked.
        Open file, if user selected it
        """
        command, completableWordIndex = self._parseCurrentCommand()
        if command is not None:
            newText = self._model.completer.getFullText(index.row())
            if newText is not None:
                newCommandText = command.constructCommand(newText)
                if newCommandText is not None:
                    self._edit.setText(newCommandText)
                    self._edit.setFocus()
                    self._onEnterPressed()
                    self._updateCompletion()

    def _updateCompletion(self):
        """User edited text or moved cursor. Update inline and TreeView completion
        """
        text = self._edit.commandText()
        atEnd = self._edit.cursorPosition() == len(text)
        completer = None

        command, completableWordIndex = self._parseCurrentCommand()
        if command is not None and atEnd:
            if self._completerConstructorThread is not None:
                self._completerConstructorThread.terminate()
            self._completerConstructorThread = _CompleterConstructorThread(self)

            self._loadingTimer.start()
            self._completerConstructorThread.start(command,
                                                   completableWordIndex)
        else:
            self._applyCompleter(None, _HelpCompleter(self._availableCommands()))

    def _applyLoadingCompleter(self):
        """Set 'Loading...' message
        """
        self._applyCompleter(None, _StatusCompleter('<i>Loading...</i>'))

    def _applyCompleter(self, command, completer):
        """Apply completer. Called by _updateCompletion or by thread function when Completer is constructed
        """
        self._loadingTimer.stop()

        if completer is None:
            completer = _HelpCompleter([command])

        inline = completer.inline()
        self._edit.setInlineCompletion(inline)

        self._model.setCompleter(completer)
        if completer.columnCount() > 1:
            self._table.resizeColumnToContents(0)
            self._table.setColumnWidth(0, self._table.columnWidth(0) + 20)  # 20 px spacing between columns

    def _onEnterPressed(self):
        """User pressed Enter or clicked item. Execute command, if possible
        """
        text = self._edit.commandText()
        command, completableWordIndex = self._parseCurrentCommand()
        if command is not None and command.isReadyToExecute():
            command.execute()
            self._history[-1] = text
            if len(self._history) > 1 and \
               self._history[-1].strip() == self._history[-2].strip():
                   self._history = self._history[:-1]  # if the last command repeats, remove duplicate
            self._history.append('')  # new edited command
            self._historyIndex = len(self._history) - 1
            self._edit.clear()
            if core.workspace().currentDocument() is not None:
                core.workspace().currentDocument().setFocus()
            self.hide()

    def _onHistoryPrevious(self):
        """User pressed Up. Roll history
        """
        if self._historyIndex == len(self._history) - 1:  # save edited command
            self._history[self._historyIndex] = self._edit.commandText()

        if self._historyIndex > 0:
            self._historyIndex -= 1
            self._edit.setText(self._history[self._historyIndex])

    def _onHistoryNext(self):
        """User pressed Down. Roll history
        """
        if self._historyIndex < len(self._history) - 1:
            self._historyIndex += 1
            self._edit.setText(self._history[self._historyIndex])

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

    def _parseCurrentCommand(self):
        """ Parse text and try to get (command, completable word index)
        Return None, None if failed to parse
        """
        if not self._commandClasses:
            return None, None

        #
        # Split line
        #
        text = self._edit.commandText()
        wordsWithIndexes = splitLine(text)
        if not wordsWithIndexes:
            return None, None

        #
        # Find command
        #
        for cmdClass in self._commandClasses:
            if cmdClass.command == wordsWithIndexes[0][0]:
                effectiveCmdClass = cmdClass
                argWordsWithIndexes = wordsWithIndexes[1:]
                break
        else:
            for cmdClass in self._commandClasses:
                if cmdClass.isDefaultCommand:
                    effectiveCmdClass = cmdClass
                    argWordsWithIndexes = wordsWithIndexes
                    break


        #
        # Try to make command object
        #
        args = [item[0] for item in argWordsWithIndexes]
        endIndexes = [item[1] for item in argWordsWithIndexes]

        try:
            cmd = effectiveCmdClass(args)
        except InvalidCmdArgs:
            return None, None

        #
        # Check if some word is completable
        #
        cursorPos = self._edit.cursorPosition()
        if cursorPos in endIndexes:
            completableWordIndex = endIndexes.index(cursorPos)
        else:
            completableWordIndex = None

        return cmd, completableWordIndex


    def exec_(self):
        """QDialog.exec() implementation. Updates completion before showing widget
        """
        try:
            curDir = os.path.abspath(os.path.curdir)
        except OSError:  # deleted
            curDir = '?'

        self.setWindowTitle(curDir)

        self._edit.setText('')
        self._updateCompletion()
        QDialog.exec_(self)
