"""
locator --- Locator dialog and functionality
============================================

Implements widget, which appears, when you press Ctrl+L and it's functionality

Contains definition of AbstractCommand and AbstractCompleter interfaces
"""

import os

from PyQt5.QtCore import pyqtSignal, QAbstractItemModel, QEvent, QModelIndex, QObject, Qt, QTimer
from PyQt5.QtWidgets import QDialog, QLineEdit, QTreeView, QVBoxLayout
from PyQt5.QtGui import QFontMetrics

from threading import Thread, Event
from queue import Queue

from enki.core.core import core
from enki.lib.htmldelegate import HTMLDelegate


class InvalidCmdArgs(UserWarning):
    pass


class AbstractCommand(QObject):
    """Base class for Locator commands.

    Inherit it to create own commands. Than add your command with Locator.addCommandClass()

    Public attributes:

    * ``command`` - Command text (first word), i.e. ``f`` for Open and ``s`` for Save
    * ``signature`` - Command signature. Shown in the Help. Example:  ``[f] PATH [LINE]``
    * ``description`` - Command description. Shown in the Help. Example: ``Open file. Globs are supported``
    * ``isDefaultCommand`` - If True, command is executed if no other command matches. Must be ``True`` for only 1 command. Currently it is FuzzyOpen
    * ``isDefaultPathCommand`` - If True, command is executed if no other command matches and text looks like a path. Must be ``True`` for only 1 command. Currently it is Open
    * ``isDefaultNumericCommand`` - If True, command is executed if no other command matches and text looks like a number. Must be ``True`` for only 1 command. Currently it is GotoLine
    """
    command = NotImplemented
    signature = NotImplemented
    description = NotImplemented
    isDefaultCommand = False
    isDefaultPathCommand = False
    isDefaultNumericCommand = False

    updateCompleter = pyqtSignal()
    """ Signal is emitted by the command after completer has changed.

    Locator will call ``completer()`` method again after this signal.
    Use this signal only for commands for which completer is changed dynamically,
    i.e. FuzzyOpen loads project files asyncronously.
    For the majority of commands it is enough to implement ``completer()`` method.
    """

    def __init__(self):
        """Construct a command insance.

        Do not forget to call ``AbstractCommand`` constructor.
        """
        QObject.__init__(self)

    def terminate(self):
        """Terminate the command if necessary.

        Default implementation does nothing
        """
        pass

    @staticmethod
    def isAvailable():
        """Check if command is available now.

        i.e. SaveAs command is not available, if no files are opened
        """
        return True

    def setArgs(self):
        """Set command arguments.

        This method can be called multiple times
        while the user edits the command.
        Raise ``InvalidCmdArgs`` if the arguments are invalid.
        """
        raise NotImplemented()

    def completer(self):
        """ ::class:`enki.core.locator.AbstractCompleter` instance for partially typed command.

        Return ``None``, if your command doesn't have completer, or if completion is not available now.
        """
        return None

    def onCompleterLoaded(self, completer):
        """ This method is called after ``completer.load()`` method has finished.
        Completer instance created in ``completer()`` is passed as parameter.

        The command can use loaded data from the completer now.
        """
        pass

    def onItemClicked(self, fullText):
        """Item in the completion tree has been clicked.

        Update internal state. After this call Locator will execute the command
        if isReadyToExecute or update line edit text with lineEditText() otherwise.
        """
        pass

    def lineEditText(self):
        """Get text for Locator dialog line edit.

        This method is called after internal command state has been
        updated with onItemClicked()
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

    If ``mustBeLoaded`` class attribute is True, ``load()`` method will be called in a thread.
    """
    mustBeLoaded = False

    def load(self, stopEvent):
        """Load necessary data in a thread.
        This method must often check ``stopEvent`` ``threading.Event``
        and return if it is set.
        """
        pass

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

    def isSelectable(self, row, column):
        """Check if item is selectable with arrow keys
        """
        return True

    def inline(self):
        """Inline completion.

        Shown after cursor. Appedned to the typed text, if Tab is pressed
        """
        return None

    def getFullText(self, row):
        """Row had been clicked by mouse. Get inline completion, which will be inserted after cursor
        """
        return None

    def autoSelectItem(self):
        """Item, which shall be auto-selected when completer is applied.

        If not None, shall be ``(row, column)``

        Default implementation returns None
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


class StatusCompleter(AbstractCompleter):
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

    def rowCount(self, index=QModelIndex()):
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

    def flags(self, index):
        flags = QAbstractItemModel.flags(self, index)
        if not self.completer.isSelectable(index.row(), index.column()):
            flags = flags & ~Qt.ItemIsEnabled

        return flags

    def setCompleter(self, completer):
        """Set completer, which will be used as data source
        """
        self.completer = completer
        self.modelReset.emit()


class _CompletableLineEdit(QLineEdit):
    """Locator line edit.

    Based on QLineEdit, because needs HTML support

    Supports inline completion, emits signals when user wants to execute command
    """

    """Text changed or cursor moved. Update completion
    """
    updateCurrentCommand = pyqtSignal()

    """Enter pressed. Execute command, if complete
    """
    enterPressed = pyqtSignal()

    def __init__(self, *args):
        QLineEdit.__init__(self, *args)
        self._inlineCompletionIsSet = False  # to differentiate inline completion and selection

        # Timer is used to delay completion update until user has finished typing
        self._updateCurrentCommandTimer = QTimer(self)
        self._updateCurrentCommandTimer.setInterval(100)
        self._updateCurrentCommandTimer.setSingleShot(True)
        self._updateCurrentCommandTimer.timeout.connect(self.updateCurrentCommand)

    def terminate(self):
        self._updateCurrentCommandTimer.stop()

    def event(self, event):
        """QObject.event implementation. Catches Tab events
        """
        if event.type() == event.KeyPress and \
           event.key() == Qt.Key_Tab:
            if self.selectedText():
                self.setCursorPosition(self.selectionStart() + len(self.selectedText()))
                self.updateCurrentCommand.emit()
            return True
        else:
            return QLineEdit.event(self, event)

    def _applyInlineCompetion(self):
        self.setCursorPosition(self.selectionStart() + len(self.selectedText()))
        self._inlineCompletionIsSet = False

    def keyPressEvent(self, event):
        """QWidget.keyPressEvent implementation. Catches Return, Up, Down, Ctrl+Backspace
        """
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            if self._inlineCompletionIsSet:
                self._applyInlineCompetion()
            self.updateCurrentCommand.emit()
            self.enterPressed.emit()
        elif event.key() in (Qt.Key_Right, Qt.Key_End):
            if self.selectedText():
                self._applyInlineCompetion()
            else:
                QLineEdit.keyPressEvent(self, event)
            self.updateCurrentCommand.emit()
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
            self._updateCurrentCommandTimer.start()
        else:
            oldTextBeforeCompletion = self.text()[:self.cursorPosition()]
            inlineCompletion = self._inlineCompletion()

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
            self._updateCurrentCommandTimer.start()

    def _deleteToSlash(self):
        """Delete back until /. Called on Ctrl+Backspace pressing
        """
        text = self.text()
        cursorPos = self.cursorPosition()
        slashPos = text.rfind('/', 0, cursorPos - 1)
        self.setSelection(slashPos + 1, cursorPos - slashPos)
        self.terminate()
        self._inlineCompletionIsSet = False

    def _clearInlineCompletion(self):
        """Clear inline completion, if exists
        """
        if self._inlineCompletionIsSet:
            self.terminate()
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
        if self._updateCurrentCommandTimer.isActive():
            return  # ignore this inline completion because the text has changed

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


class _CompleterLoaderThread(Thread):
    """Thread constructs Completer
    Sometimes it requires a lot of time, i.e. when expanding "/usr/lib/*"
    hlamer: I tried to use QThread + pyqtSignal, but got tired with crashes and deadlocks
    """
    daemon = True

    def __init__(self, locator):
        """Works in the GUI thread
        """
        Thread.__init__(self)

        self._locator = locator

        self._taskQueue = Queue()  # completer or None as exit signal
        self._resultQueue = Queue()

        self._checkResultQueueTimer = QTimer()
        self._checkResultQueueTimer.setInterval(50)
        self._checkResultQueueTimer.timeout.connect(self._checkResultQueue)
        self._checkResultQueueTimer.start()

        self._stopEvent = Event()
        Thread.start(self)

    def _checkResultQueue(self):
        """Check if thread constructed a completer and put it to the queue
        Works in the GUI thread
        """
        if not self._resultQueue.empty():
            command, completer = self._resultQueue.get()
            self._locator.onCompleterLoaded(command, completer)

    def loadCompleter(self, command, completer):
        """Start constructing completer
        Works in the GUI thread
        """
        # Stop previous
        self._stopEvent.set()
        self._taskQueue.join()

        # Drop previous result
        while not self._resultQueue.empty():
            self._resultQueue.get()

        # Start new
        self._stopEvent.clear()
        task = (command, completer)
        if not self.is_alive():
            assert 0
        self._taskQueue.put(task)

    def terminate(self):
        """Set termination flag
        Works in the GUI thread
        """
        if self.is_alive():
            self._stopEvent.set()
            self._taskQueue.put(None)
            self._checkResultQueueTimer.stop()
            self.join()

    def _getNextTask(self):
        # discard old commands
        while self._taskQueue.qsize() > 1:
            self._taskQueue.get()
            self._taskQueue.task_done()

        # Get the last command
        return self._taskQueue.get()

    def run(self):
        """Thread function
        Works in NEW thread
        """
        while True:
            task = self._getNextTask()
            try:
                if task is None:  # exit command
                    break

                command, completer = task
                completer.load(self._stopEvent)
                if self._taskQueue.empty():
                    self._resultQueue.put((command, completer))
            finally:
                self._taskQueue.task_done()


def splitLine(text):
    """ Split text onto words
    Return list of (word, endIndex)
    """
    words = []  # list of tuples (text, endIndex)

    it = enumerate(text)

    def findNonSpace():
        index, char = next(it)
        while char.isspace():
            index, char = next(it)

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
                        index, char = next(it)
                    except StopIteration:
                        word += '\\'
                        raise
                    else:
                        word += char
                else:
                    word += char
                index, char = next(it)

        except StopIteration:
            pass

        return word

    while True:
        try:
            nonSpaceChar, index = findNonSpace()
        except StopIteration:
            break

        words.append(getWord(nonSpaceChar, index))

    return words


class Locator(QObject):

    def __init__(self):
        QObject.__init__(self)
        self._commandClasses = []

        self._action = core.actionManager().addAction("mNavigation/aLocator", "Locator", shortcut='Ctrl+L')
        self._action.triggered.connect(self._onAction)
        self._separator = core.actionManager().menu("mNavigation").addSeparator()

    def terminate(self):
        core.actionManager().removeAction(self._action)
        core.actionManager().menu("mNavigation").removeAction(self._separator)

    def _onAction(self):
        """Locator action triggered. Show themselves and make focused
        """
        _LocatorDialog(core.mainWindow(), self._availableCommands()).exec_()

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


class _LocatorDialog(QDialog):
    """Locator widget and implementation
    """

    def __init__(self, parent, commandClasses):
        QDialog.__init__(self, parent)
        self._terminated = False
        self._commandClasses = commandClasses

        self._createUi()

        self._loadingTimer = QTimer(self)
        self._loadingTimer.setSingleShot(True)
        self._loadingTimer.setInterval(200)
        self._loadingTimer.timeout.connect(self._applyLoadingCompleter)

        self._completerLoaderThread = _CompleterLoaderThread(self)

        self.finished.connect(self._terminate)

        self._command = None
        self._updateCurrentCommand()

    def _createUi(self):
        self.setWindowTitle(core.project().path().replace(os.sep, '/') or 'Locator')

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(1)

        biggerFont = self.font()
        biggerFont.setPointSizeF(biggerFont.pointSizeF() * 2)
        self.setFont(biggerFont)

        self._edit = _CompletableLineEdit(self)
        self._edit.updateCurrentCommand.connect(self._updateCurrentCommand)
        self._edit.enterPressed.connect(self._onEnterPressed)
        self._edit.installEventFilter(self)  # catch Up, Down
        self.layout().addWidget(self._edit)
        self.setFocusProxy(self._edit)

        self._table = QTreeView(self)
        self._table.setFont(biggerFont)
        self._model = _CompleterModel()
        self._table.setModel(self._model)
        self._table.setItemDelegate(HTMLDelegate(self._table))
        self._table.setRootIsDecorated(False)
        self._table.setHeaderHidden(True)
        self._table.clicked.connect(self._onItemClicked)
        self._table.setAlternatingRowColors(True)
        self._table.installEventFilter(self)  # catch focus and give to the edit
        self.layout().addWidget(self._table)

        width = QFontMetrics(self.font()).width('x' * 64)  # width of 64 'x' letters
        self.resize(width, width * 0.62)

    def _terminate(self):
        if not self._terminated:
            if self._command is not None:
                self._command.terminate()
                self._command = None

            self._edit.terminate()

            self._completerLoaderThread.terminate()
            core.workspace().focusCurrentDocument()
            self._terminated = True

    def _updateCurrentCommand(self):
        """Try to parse line edit text and set current command
        """
        if self._terminated:
            return

        newCommand = self._parseCurrentCommand()

        if newCommand is not self._command:
            if self._command is not None:
                self._command.updateCompleter.disconnect(self._updateCompletion)
                self._command.terminate()

            self._command = newCommand
            if self._command is not None:
                self._command.updateCompleter.connect(self._updateCompletion)

        self._updateCompletion()

    def _updateCompletion(self):
        """User edited text or moved cursor. Update inline and TreeView completion
        """
        if self._command is not None:
            completer = self._command.completer()

            if completer is not None and completer.mustBeLoaded:
                self._loadingTimer.start()
                self._completerLoaderThread.loadCompleter(self._command, completer)
            else:
                self._applyCompleter(self._command, completer)
        else:
            self._applyCompleter(None, _HelpCompleter(self._commandClasses))

    def _applyLoadingCompleter(self):
        """Set 'Loading...' message
        """
        self._applyCompleter(None, StatusCompleter('<i>Loading...</i>'))

    def onCompleterLoaded(self, command, completer):
        """The method called from _CompleterLoaderThread when the completer is ready
        This code works in the GUI thread
        """
        self._applyCompleter(command, completer)

    def _applyCompleter(self, command, completer):
        """Apply completer. Called by _updateCompletion or by thread function when Completer is constructed
        """
        self._loadingTimer.stop()

        if command is not None:
            command.onCompleterLoaded(completer)

        if completer is None:
            completer = _HelpCompleter([command])

        if self._edit.cursorPosition() == len(self._edit.text()):  # if cursor at the end of text
            self._edit.setInlineCompletion(completer.inline())

        self._model.setCompleter(completer)
        if completer.columnCount() > 1:
            self._table.resizeColumnToContents(0)
            self._table.setColumnWidth(0, self._table.columnWidth(0) + 20)  # 20 px spacing between columns

        selItem = completer.autoSelectItem()
        if selItem:
            index = self._model.createIndex(selItem[0],
                                            selItem[1])
            self._table.setCurrentIndex(index)

    def _onItemClicked(self, index):
        """Item in the TreeView has been clicked.
        Open file, if user selected it
        """
        if self._command is not None:
            fullText = self._model.completer.getFullText(index.row())
            if fullText is not None:
                self._command.onItemClicked(fullText)
                if self._tryExecCurrentCommand():
                    self.accept()
                    return
                else:
                    self._edit.setText(self._command.lineEditText())
                    self._updateCurrentCommand()

        self._edit.setFocus()

    def _onEnterPressed(self):
        """User pressed Enter or clicked item. Execute command, if possible
        """
        if self._table.currentIndex().isValid():
            self._onItemClicked(self._table.currentIndex())
        else:
            self._tryExecCurrentCommand()

    def _tryExecCurrentCommand(self):
        if self._command is not None and self._command.isReadyToExecute():
            self._command.execute()
            self.accept()
            return True
        else:
            return False

    def _chooseCommand(self, words):
        for cmd in self._commandClasses:
            if cmd.command == words[0]:
                return cmd, words[1:]

        isPath = words and (words[0].startswith('/') or
                            words[0].startswith('./') or
                            words[0].startswith('../') or
                            words[0].startswith('~/') or
                            words[0][1:3] == ':\\' or
                            words[0][1:3] == ':/'
                            )
        isNumber = len(words) == 1 and all([c.isdigit() for c in words[0]])

        def matches(cmd):
            if isPath:
                return cmd.isDefaultPathCommand
            elif isNumber:
                return cmd.isDefaultNumericCommand
            else:
                return cmd.isDefaultCommand

        for cmd in self._commandClasses:
            if matches(cmd):
                return cmd, words

    def _parseCurrentCommand(self):
        """ Parse text and try to get (command, completable word index)
        Return None if failed to parse
        """
        # Split line
        text = self._edit.commandText()
        words = splitLine(text)
        if not words:
            return None

        # Find command
        cmdClass, args = self._chooseCommand(words)

        if isinstance(self._command, cmdClass):
            command = self._command
        else:
            command = cmdClass()

        # Try to make command object
        try:
            command.setArgs(args)
        except InvalidCmdArgs:
            return None
        else:
            return command

    def eventFilter(self, obj, event):
        if obj is self._edit:
            if event.type() == QEvent.KeyPress and \
               event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown):
                return self._table.event(event)
        elif obj is self._table:
            if event.type() == QEvent.FocusIn:
                self._edit.setFocus()
                return True

        return False
