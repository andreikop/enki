"""Navigator dock widget and functionality
"""

import os.path
import collections
import queue

from PyQt5.QtCore import pyqtSignal, QObject, QThread, QTimer
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtGui import QIcon
from PyQt5 import uic


from enki.core.core import core
from enki.core.uisettings import TextOption, CheckableOption
import enki.lib.get_console_output as gco

from . import ctags
from .dock import NavigatorDock


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
    "PHP": ("PHP/PHP", "PHP (HTML)"),
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
for ctagsLang, qutepartLangs in _CTAGS_TO_QUTEPART_LANG_MAP.items():
    for qutepartLang in qutepartLangs:
        _QUTEPART_TO_CTAGS_LANG_MAP[qutepartLang] = ctagsLang


class ProcessorThread(QThread):
    """Thread processes text with ctags and returns tags
    """
    tagsReady = pyqtSignal(list)
    error = pyqtSignal(str)

    _Task = collections.namedtuple("Task", ["ctagsLang", "text", "sortAlphabetically"])

    def __init__(self):
        QThread.__init__(self)
        self._queue = queue.Queue()
        self.start(QThread.LowPriority)

    def process(self, ctagsLang, text, sortAlphabetically):
        """Parse text and emit tags
        """
        self._queue.put(self._Task(ctagsLang, text, sortAlphabetically))

    def stopAsync(self):
        self._queue.put(None)

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            # wait task
            task = self._queue.get()
            # take the last task
            while self._queue.qsize():
                task = self._queue.get()

            if task is None:  # None is a quit command
                break

            try:
                tags = ctags.processText(task.ctagsLang, task.text, task.sortAlphabetically)
            except ctags.FailedException as ex:
                self.error.emit(ex.args[0])
            else:
                if not self._queue.qsize():  # Do not emit results, if having new task
                    self.tagsReady.emit(tags)


class SettingsWidget(QWidget):
    """Settings widget. Insertted as a page to UISettings
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        self.pbCtagsPath.clicked.connect(self._onPbCtagsPathClicked)
        self.leCtagsPath.textChanged.connect(self._updateExecuteError)

    def _onPbCtagsPathClicked(self):
        path, _ = QFileDialog.getOpenFileName(core.mainWindow(), 'Ctags path')
        if path:
            self.leCtagsPath.setText(path)

    def _updateExecuteError(self, path):
        """ Check if pylint is installed.

        Return None if OK or textual error
        """
        try:
            stdout, stderr = gco.get_console_output([path, '--version'])
        except OSError as ex:
            self.lExecuteError.setText('Failed to execute ctags: {}'.format(ex))
        else:
            if 'Exuberant Ctags' in stdout:
                self.lExecuteError.setText('ctags is found!')
            elif 'GNU Emacs' in stdout:
                self.lExecuteError.setText(
                    'You are trying to use etags from the Emacs package, but it is not supported. Use Exuberant Ctags.')


class Plugin(QObject):
    """Main class. Interface for the core.
    """

    def __init__(self):
        QObject.__init__(self)
        self._dock = None
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)

        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)
        core.uiSettingsManager().dialogAccepted.connect(self._scheduleDocumentProcessing)

        # If we update Tree on every key pressing, freezes are sensible (GUI thread draws tree too slowly
        # This timer is used for drawing Preview 1000 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(1000)
        self._typingTimer.setSingleShot(True)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self._thread = ProcessorThread()

    def del_(self):
        """Uninstall the plugin
        """
        if self._dock is not None:
            self._thread.tagsReady.disconnect(self._dock.setTags)
            self._thread.error.disconnect(self._dock.onError)
            self._dock.remove()
        self._typingTimer.stop()
        self._thread.stopAsync()
        self._thread.wait()

    def _createDock(self):
        self._dock = NavigatorDock()
        self._dock.setVisible(False)
        self._dock.shown.connect(self._onDockShown)
        self._dock.closed.connect(self._onDockClosed)

        self._thread.tagsReady.connect(self._dock.setTags)
        self._thread.error.connect(self._dock.onError)

    def _isEnabled(self):
        return core.config()['Navigator']['Enabled']

    def _isSupported(self, document):
        return document is not None and \
            document.qutepart.language() in _QUTEPART_TO_CTAGS_LANG_MAP

    def _onDockClosed(self):
        """Dock has been closed by a user. Change Enabled option
        """
        if core.config()['Navigator']['Enabled']:
            core.config()['Navigator']['Enabled'] = False
            core.config().flush()
            self._dock.setTags([])

    def _onDockShown(self):
        """Dock has been shown by a user. Change Enabled option
        """
        if not core.config()['Navigator']['Enabled']:
            core.config()['Navigator']['Enabled'] = True
            core.config().flush()
            self._scheduleDocumentProcessing()

    def _onDocumentChanged(self, old, new):
        if self._isSupported(new):
            if self._dock is None:
                self._createDock()
            self._dock.install()
            if self._isEnabled():
                self._dock.show()
                self._scheduleDocumentProcessing()
        else:
            self._clear()
            if self._dock is not None:
                self._dock.remove()

    def _onTextChanged(self):
        if self._isEnabled():
            self._typingTimer.stop()
            self._typingTimer.start()

    def _clear(self):
        if self._dock is not None:
            self._dock.setTags([])

    def _scheduleDocumentProcessing(self):
        """Start document processing with the thread.
        """
        self._typingTimer.stop()

        document = core.workspace().currentDocument()
        if document is not None and \
           document.qutepart.language() in _QUTEPART_TO_CTAGS_LANG_MAP:
            ctagsLang = _QUTEPART_TO_CTAGS_LANG_MAP[document.qutepart.language()]
            self._thread.process(ctagsLang, document.qutepart.text,
                                 core.config()['Navigator']['SortAlphabetically'])

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        widget = SettingsWidget(dialog)

        dialog.appendPage("Navigator", widget, QIcon(':/enkiicons/goto.png'))

        # Options
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Navigator/CtagsPath", widget.leCtagsPath))
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "Navigator/SortAlphabetically",
                                            widget.cbSortTagsAlphabetically))
