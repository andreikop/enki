"""Navigator dock widget and functionality
"""

import tempfile
import subprocess
import shutil
import os.path
import threading

from PyQt4.QtCore import pyqtSignal, QObject, Qt, QThread, QTimer, QVariant, QAbstractItemModel, QModelIndex
from PyQt4.QtGui import QIcon, QTreeView

from enki.widgets.dockwidget import DockWidget

from enki.core.core import core


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
    "Flex": "Lex/Flex",
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
    "OCaml": "Objective Caml",
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
    "Tcl": "Tcl/Tk",
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


class Tag:
    def __init__(self, name, lineNumber, parent):
        self.name = name
        self.lineNumber = lineNumber
        self.parent = parent
        self.children = []
    
    def format(self, indentLevel=0):
        indent = '\t' * indentLevel
        formattedChildren = [child.format(indentLevel + 1) \
                                for child in self.children]
        result = '{}{} {}'.format(indent, self.lineNumber, self.name)
        if formattedChildren:
            result += '\n'
            result += '\n'.join(formattedChildren)
        
        return result


def parseTags(text):
    def parseTag(line):
        items = line.split('\t')
        name = items[0]
        if len(items) == 5:
            type_ = items[-2]
            lineText = items[-1]
            scopeText = None
        else:
            type_ = items[-3]
            lineText = items[-2]
            scopeText = items[-1]
        
        lineNumber = int(lineText.split(':')[-1])
        
        scope = scopeText.split(':')[-1].split('.')[-1] if scopeText else None
        return name, lineNumber, type_, scope
    
    def findScope(tag, scopeName):
        """Check tag and its parents, it theirs name is scopeName.
        Return tag or None
        """
        if tag is None:
            return None
        if tag.name == scopeName:
            return tag
        elif tag.parent is not None:
            return findScope(tag.parent, scopeName)
        else:
            return None
    
    ignoredTypes = ('variable')
    
    tags = []
    lastTag = None
    for line in text.splitlines():
        name, lineNumber, type_, scope = parseTag(line)
        if type_ not in ignoredTypes:
            parent = findScope(lastTag, scope)
            tag = Tag(name, lineNumber, parent)
            if parent is not None:
                parent.children.append(tag)
            else:
                tags.append(tag)
            lastTag = tag
    
    return tags


def processText(fileName, text):
    tmpDir = tempfile.mkdtemp()
    try:
        path = os.path.join(tmpDir, fileName)
        with open(path, 'w') as file_:
            file_.write(text)
        popen = subprocess.Popen(['ctags', '-f', '-', '-u', '--fields=nKs', path], stdout=subprocess.PIPE)
        stdout, stderr = popen.communicate()
    finally:
        shutil.rmtree(tmpDir)
    
    return parseTags(stdout)


class TagModel(QAbstractItemModel):
    def __init__(self, *args):
        QAbstractItemModel.__init__(self, *args)
        self.beginResetModel()
        self._tags = []
        self.endResetModel()
    
    def setTags(self, tags):
        self._tags = tags
        self.layoutChanged.emit()
    
    def index(self, row, column, parent):
        if not parent.isValid():  # top level
            return self.createIndex(row, column, self._tags[row])
        else:  # nested
            parentTag = parent.internalPointer()
            return self.createIndex(row, column, parentTag.children[row])
    
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        tag = index.internalPointer()
        if tag.parent is not None:
            parent = tag.parent
            if parent.parent:
                row = parent.parent.children.index(parent)
            else:
                row = self._tags.index(parent)
            
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
        
        tag = index.internalPointer()
        if role == Qt.DisplayRole:
            return '{} {}'.format(tag.name, tag.lineNumber)
        else:
            return QVariant()


class ProcessorThread(QThread):
    """Thread processes text with ctags and returns tags
    """
    tagsReady = pyqtSignal(list)

    def __init__(self):
        QThread.__init__(self)
        self._fileName = None
        self._text = None
        self._haveData = False
        self._lock = threading.Lock()

    def process(self, fileName, text):
        """Parse text and emit tags
        """
        with self._lock:
            self._fileName = fileName
            self._haveData = True
            self._text = text
            if not self.isRunning():
                self.start(QThread.LowPriority)

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            with self._lock:
                fileName = self._fileName
                text = self._text
                self._haveData = False
            
            tags = processText(fileName, text)
            
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
        self._model.layoutChanged.connect(self._tree.expandAll)
        
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

    def closeEvent(self, event):
        """Widget is closed.
        Probably should update enabled state
        """
        self.closed.emit()
        self.setTags([])


class Plugin(QObject):
    """Main class. Interface for the core.
    """
    def __init__(self):
        QObject.__init__(self)
        self._dock = NavigatorDock()
        self._dock.closed.connect(self._onDockClosed)
        
        self._dock.showAction().triggered.connect(self._onDockShown)
        core.mainWindow().stateRestored.connect(self._onMainWindowStateRestored)

        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)
        
        # If we update Tree on every key pressing, freezes are sensible (GUI thread draws tree too slowly
        # This timer is used for drawing Preview 1000 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(1000)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self._thread = ProcessorThread()
        self._thread.tagsReady.connect(self._dock.setTags)

    def del_(self):
        """Uninstall the plugin
        """
        self._dock.remove()
        self._typingTimer.stop()
        self._thread.wait()
    
    def _isEnabled(self):
        return core.config()['Ctags']['Enabled']
    
    def _isSupported(self, document):
        return document is not None and \
               document.qutepart.language() in _QUTEPART_TO_CTAGS_LANG_MAP
    
    def _onDockClosed(self):
        """Dock has been closed by a user. Change Enabled option
        """
        core.config()['Ctags']['Enabled'] = False
        core.config().flush()
    
    def _onDockShown(self):
        """Dock has been shown by a user. Change Enabled option
        """
        core.config()['Ctags']['Enabled'] = True
        core.config().flush()
        self._scheduleDocumentProcessing()
    
    def _onMainWindowStateRestored(self):
        """When main window state is restored - dock is made visible, even if should not. Qt bug?
        Hide dock, if can't view current document
        """
        if not (self._isEnabled() and \
                self._isSupported(core.workspace().currentDocument())):
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
           document.fileName() is not None:
            self._thread.process(document.fileName(), document.qutepart.text)
