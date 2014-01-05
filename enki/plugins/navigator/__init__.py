"""Navigator dock widget and functionality
"""

import os.path
import threading

from PyQt4.QtCore import pyqtSignal, QObject, Qt, QThread, QTimer, QVariant, QAbstractItemModel, QModelIndex
from PyQt4.QtGui import QApplication, QBrush, QColor, QFileDialog, QLabel, QIcon, QTreeView, QWidget
from PyQt4 import uic

from enki.widgets.dockwidget import DockWidget

from enki.core.core import core
from enki.core.uisettings import TextOption

import ctags

# source map. 1 ctags language is mapped to multiply Qutepart languages
# NOTE this map must be updated after new languages has been added to ctags or Qutepart
#  Initially filled on Qutepart 1.1.0 and Ctags 5.9~svn20110310
_CTAGS_TO_QUTEPART_LANG_MAP = {
    "Asm": ("AVR Assembler", "GNU Assembler", "MIPS Assembler",
            "Asm6502", "Intel x86 (NASM)", "Motorola 68k (VASM/Devpac)", "PicAsm"),
    "Asp": ("ASP",),
    "Awk": ("AWK",),
    "Basic": ("FreeBASIC", "KBasic", "MonoBasic", "PureBasic", "TI Basic"),
    "C": ("C",),
    "C#": ("C#",),
    "C++": ("C++",),
    "DosBatch": ("MS-DOS Batch",),
    "Eiffel": ("Eiffel",),
    "Erlang": ("Erlang",),
    "Flex": ("Lex/Flex",),
    "Fortran": ("Fortran",),
    "Go": ("Go",),
    "HTML": ("Django HTML Template", "HTML", "Ruby/Rails/RHTML"),
    "Java": ("Java",),
    "JavaScript": ("JavaScript",),
    "Lisp": ("Common Lisp",),
    "Lua": ("Lua",),
    "Make": ("Makefile",),
    "Matlab": ("Matlab",),
    "ObjectiveC": ("Objective-C", "Objective-C++"),
    "OCaml": ("Objective Caml",),
    "Pascal": ("Pascal",),
    "Perl": ("Perl",),
    "PHP": "PHP/PHP",
    "Python": ("Python",),
    "REXX": ("REXX",),
    "Ruby": ("Ruby",),
    "Scheme": ("Scheme",),
    "Sh": ("Zsh", "Bash"),
    "SML": ("SML",),
    "SQL": ("SQL", "SQL (MySQL)", "SQL (PostgreSQL)"),
    "Tcl": ("Tcl/Tk",),
    "Tex": ("LaTeX", "Texinfo"),
    "Vera": ("Vera",),
    "Verilog": ("Verilog",),
    "VHDL": ("VHDL",),
    "YACC": ("Yacc/Bison",)
}

# build reverse map
_QUTEPART_TO_CTAGS_LANG_MAP = {}
for ctagsLang, qutepartLangs in _CTAGS_TO_QUTEPART_LANG_MAP.iteritems():
    for qutepartLang in qutepartLangs:
        _QUTEPART_TO_CTAGS_LANG_MAP[qutepartLang] = ctagsLang




class TagModel(QAbstractItemModel):
    def __init__(self, *args):
        QAbstractItemModel.__init__(self, *args)
        self._tags = []

        self._currentTagIndex = QModelIndex()

        defBaseColor = QApplication.instance().palette().base().color()
        # yellow or maroon
        brightBg = QColor('#ffff80') if defBaseColor.lightnessF() > 0.5 else QColor('#800000')
        self._currentTagBrush = QVariant(QBrush(brightBg))

        core.workspace().cursorPositionChanged.connect(self._onCursorPositionChanged)
        self._updateCurrentTagTimer = QTimer()
        self._updateCurrentTagTimer.setInterval(300)
        self._updateCurrentTagTimer.timeout.connect(self._updateCurrentTagAndEmitSignal)

    def setTags(self, tags):
        self.beginResetModel()
        self._tags = tags
        self._updateCurrentTag(False)
        self.endResetModel()

    def _onCursorPositionChanged(self):
        """If position is updated on every key pressing - cursor movement might be slow
        Update position, when movement finished
        """
        self._updateCurrentTagTimer.stop()
        self._updateCurrentTagTimer.start()

    def _updateCurrentTagAndEmitSignal(self):
        self._updateCurrentTag(True)

    def _updateCurrentTag(self, emitChanged):
        old = self._currentTagIndex
        if core.workspace().currentDocument() is not None:
            lineNumber = core.workspace().currentDocument().qutepart.cursorPosition[0]
            self._currentTagIndex = self._indexForLineNumber(lineNumber)
        else:
            self._currentTagIndex = QModelIndex()

        if emitChanged:
            if old != self._currentTagIndex and \
               old.isValid():
               self.dataChanged.emit(old, old)
            if self._currentTagIndex.isValid():
                self.dataChanged.emit(self._currentTagIndex, self._currentTagIndex)

    def index(self, row, column, parent):
        if row < 0 or column != 0:
            return QModelIndex()

        if not parent.isValid():  # top level
            if row < len(self._tags):
                return self.createIndex(row, column, self._tags[row])
            else:
                return QModelIndex()
        else:  # nested
            parentTag = parent.internalPointer()
            if row < len(parentTag.children):
                return self.createIndex(row, column, parentTag.children[row])
            else:
                return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        tag = index.internalPointer()
        if tag.parent is not None:
            parent = tag.parent
            if parent.parent:
                try:
                    row = parent.parent.children.index(parent)
                except ValueError:
                    return QModelIndex()
            else:
                try:
                    row = self._tags.index(parent)
                except ValueError:
                    return QModelIndex()

            return self.createIndex(row, 0, parent)
        else:
            return QModelIndex()

    def rowCount(self, index):
        if index.isValid():
            tag = index.internalPointer()
            return len(tag.children)
        else:
            return len(self._tags)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            tag = index.internalPointer()
            return tag.name
        elif role == Qt.BackgroundRole:
            return self._currentTagBrush if index == self._currentTagIndex else QVariant()
        else:
            return QVariant()

    def onActivated(self, index):
        tag = index.internalPointer()

        document = core.workspace().currentDocument()
        if document is not None:
            core.workspace().cursorPositionChanged.disconnect(self._onCursorPositionChanged)
            document.qutepart.cursorPosition = (tag.lineNumber, 0)
            core.workspace().cursorPositionChanged.connect(self._onCursorPositionChanged)
            self._updateCurrentTagAndEmitSignal()

            document.qutepart.centerCursor()
            document.qutepart.setFocus()

    def tagPathForIndex(self, index):
        def tagPath(tag):
            if tag is None:
                return []
            else:
                return tagPath(tag.parent) + [tag.name]

        tag = index.internalPointer()
        return '.'.join(tagPath(tag))

    def indexForTagPath(self, tagPath):
        def findTag(tagList, name):
            for tag in tagList:
                if tag.name == name:
                    return tag
            else:
                return None

        def findPath(currentTag, childTags, parts):
            if not parts:
                return currentTag

            part = parts[0]
            tag = findTag(childTags, part)
            if tag is not None:
                return findPath(tag, tag.children, parts[1:])
            else:
                return currentTag

        parts = tagPath.split('.')
        tag = findPath(None, self._tags, parts)
        if tag is not None:
            row = tag.parent.children.index(tag) if tag.parent else self._tags.index(tag)
            return self.createIndex(row, 0, tag)
        else:
            return QModelIndex()

    def _indexForLineNumber(self, number):

        def recursiveTagGenerator(tags):
            for childRow, childTag in enumerate(tags):
                yield childRow, childTag
                for gcRow, grandChild in recursiveTagGenerator(childTag.children):
                    yield gcRow, grandChild

        prevRow, prevTag = None, None
        for row, tag in recursiveTagGenerator(self._tags):
            if tag.lineNumber == number:
                return self.createIndex(row, 0, tag)
            elif tag.lineNumber > number and \
                 prevTag is not None and \
                 prevTag.lineNumber <= number:
                return self.createIndex(prevRow, 0, prevTag)
            else:
                prevRow, prevTag = row, tag
        else:
            if prevTag is not None and \
               prevTag.lineNumber <= number: # the last tag is current
                return self.createIndex(prevRow, 0, prevTag)

        return QModelIndex()


class ProcessorThread(QThread):
    """Thread processes text with ctags and returns tags
    """
    tagsReady = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self._ctagsLang = None
        self._text = None
        self._haveData = False
        self._lock = threading.Lock()

    def process(self, ctagsLang, text):
        """Parse text and emit tags
        """
        with self._lock:
            self._ctagsLang = ctagsLang
            self._haveData = True
            self._text = text
            if not self.isRunning():
                self.start(QThread.LowPriority)

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            with self._lock:
                ctagsLang = self._ctagsLang
                text = self._text
                self._haveData = False

            result = ctags.processText(ctagsLang, text)

            if isinstance(result, basestring):
                self.error.emit(result)
                break
            else:
                tags = result

                with self._lock:
                    if not self._haveData:
                        self.tagsReady.emit(tags)
                        break
                    # else - next iteration


class NavigatorDock(DockWidget):

    closed = pyqtSignal()

    def __init__(self):
        DockWidget.__init__(self, core.mainWindow(), '&Navigator', QIcon(':/enkiicons/goto.png'), "Alt+N")

        self._tree = QTreeView(self)
        self._tree.setHeaderHidden(True)
        self.setWidget(self._tree)
        self.setFocusProxy(self._tree)

        self._model = TagModel(self._tree)
        self._tree.setModel(self._model)
        self._tree.activated.connect(self._model.onActivated)
        self._tree.clicked.connect(self._model.onActivated)
        self._model.modelAboutToBeReset.connect(self._onModelAboutToBeReset)
        self._model.modelReset.connect(self._onModelReset)
        self._currentTagPath = None

        self._errorLabel = None

        self._installed = False

    def install(self):
        if not self._installed:
            core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self)
            core.actionManager().addAction("mView/aNavigator", self.showAction())
            self._installed = True

    def remove(self):
        if self._installed:
            core.mainWindow().removeDockWidget(self)
            core.actionManager().removeAction("mView/aNavigator")
            self.hide()
            self._installed = False

    def setTags(self, tags):
        self._model.setTags(tags)
        if self.widget() is not self._tree:
            self.setWidget(self._tree)
            self._tree.show()
        if self._errorLabel is not None:
            self._errorLabel.hide()

    def onError(self, error):
        self._tree.hide()
        if self._errorLabel is None:
            self._errorLabel = QLabel(self)
            self._errorLabel.setWordWrap(True)

        self._errorLabel.setText(error)

        if not self.widget() is self._errorLabel:
            self.setWidget(self._errorLabel)
            self._errorLabel.show()
            self._tree.hide()

    def closeEvent(self, event):
        """Widget is closed.
        Probably should update enabled state
        """
        self.closed.emit()
        self.setTags([])

    def _onModelAboutToBeReset(self):
        currIndex = self._tree.currentIndex()
        self._currentTagPath = self._model.tagPathForIndex(currIndex) if currIndex.isValid() else None

    def _onModelReset(self):
        self._tree.expandAll()

        # restore current item
        if self._currentTagPath is not None:
            index = self._model.indexForTagPath(self._currentTagPath)
            if index.isValid():
                self._tree.setCurrentIndex(index)


class SettingsWidget(QWidget):
    """Settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        self.pbCtagsPath.clicked.connect(self._onPbCtagsPathClicked)

    def _onPbCtagsPathClicked(self):
        path = QFileDialog.getOpenFileName(core.mainWindow(), 'Ctags path')
        if path:
            self.leCtagsPath.setText(path)


class Plugin(QObject):
    """Main class. Interface for the core.
    """
    def __init__(self):
        QObject.__init__(self)
        self._dock = NavigatorDock()
        self._dock.hide()
        self._dock.closed.connect(self._onDockClosed)

        self._dock.showAction().triggered.connect(self._onDockShown)
        core.mainWindow().stateRestored.connect(self._onMainWindowStateRestored)

        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)

        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

        # If we update Tree on every key pressing, freezes are sensible (GUI thread draws tree too slowly
        # This timer is used for drawing Preview 1000 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(1000)
        self._typingTimer.setSingleShot(True)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self._thread = ProcessorThread()
        self._thread.tagsReady.connect(self._dock.setTags)
        self._thread.error.connect(self._dock.onError)

    def del_(self):
        """Uninstall the plugin
        """
        self._dock.remove()
        self._typingTimer.stop()
        self._thread.tagsReady.disconnect(self._dock.setTags)
        self._thread.wait()

    def _isEnabled(self):
        return core.config()['Navigator']['Enabled']

    def _isSupported(self, document):
        return document is not None and \
               document.qutepart.language() in _QUTEPART_TO_CTAGS_LANG_MAP

    def _onDockClosed(self):
        """Dock has been closed by a user. Change Enabled option
        """
        core.config()['Navigator']['Enabled'] = False
        core.config().flush()

    def _onDockShown(self):
        """Dock has been shown by a user. Change Enabled option
        """
        core.config()['Navigator']['Enabled'] = True
        core.config().flush()
        self._scheduleDocumentProcessing()

    def _onMainWindowStateRestored(self):
        """When main window state is restored - dock is made visible, even if should not. Qt bug?
        Hide dock, if can't view current document
        """
        if not self._isEnabled() or \
           not self._isSupported(core.workspace().currentDocument()):
            self._dock.hide()

    def _onDocumentChanged(self, old, new):
        if self._isSupported(new):
            self._dock.install()
            if self._isEnabled():
                self._dock.show()
                self._scheduleDocumentProcessing()
        else:
            self._clear()
            self._dock.remove()

    def _onTextChanged(self):
        if self._isEnabled():
            self._typingTimer.stop()
            self._typingTimer.start()

    def _clear(self):
        self._dock.setTags([])

    def _scheduleDocumentProcessing(self):
        """Start document processing with the thread.
        """
        self._typingTimer.stop()

        document = core.workspace().currentDocument()
        if document is not None and \
           document.qutepart.language() in _QUTEPART_TO_CTAGS_LANG_MAP:
            ctagsLang = _QUTEPART_TO_CTAGS_LANG_MAP[document.qutepart.language()]
            self._thread.process(ctagsLang, document.qutepart.text)

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        widget = SettingsWidget(dialog)

        dialog.appendPage(u"Navigator", widget, self._dock.windowIcon())

        # Options
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Navigator/CtagsPath", widget.leCtagsPath))
