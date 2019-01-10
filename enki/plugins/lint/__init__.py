"""Lint plugin shows linter messages for different languages
"""


import re
import os.path
import collections
import queue

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon

from enki.core.core import core
from enki.core.uisettings import ChoiseOption, TextOption, CheckableOption, NumericOption
from enki.lib.get_console_output import get_console_output

from qutepart import Qutepart


class ProcessorThread(QThread):
    """Thread processes text with ctags and returns tags
    """
    resultsReady = pyqtSignal(object, object)  # Document, results dict

    _Task = collections.namedtuple("Task", ["document", "language", "filePath"])

    _PARSER_REG_EXP = re.compile(r'^(.+):(\d+):(\d+): ([A-Z]\d\d\d .+)$')

    def __init__(self):
        QThread.__init__(self)
        self._queue = queue.Queue()
        self.start(QThread.LowPriority)

    def process(self, document):
        """Parse text and emit results
        """
        self._queue.put(self._Task(document,
                                   document.qutepart.language(),
                                   document.filePath()))

    def stopAsync(self):
        self._queue.put(None)

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            # wait task
            task = self._queue.get()
            # take the last task

            # get the last task
            while not self._queue.empty():
                task = self._queue.get()

            if task is None:  # None is a quit command
                break

            results = self._processSync(task.language, task.filePath)

            if results is not None:
                self.resultsReady.emit(task.document, results)

    """ Note that most of the PEP8 "errors" listed in
    http://pep8.readthedocs.org/en/latest/intro.html#error-codes aren't syntax errors.
    So, mark most of these as warnings instead.
    Later in the code, E9 errors are actually marked as errors.
    See https://github.com/andreikop/enki/issues/349.
    """
    _MSG_ID_CONVERTOR = {  #
        'E': Qutepart.LINT_WARNING,
        'W': Qutepart.LINT_WARNING,
        'F': Qutepart.LINT_WARNING,
        'C': Qutepart.LINT_NOTE,
        'N': Qutepart.LINT_NOTE,
    }

    _PEP8_ERRORS = ('E112', 'E113', 'E901', 'E902')
    _PYFLAKES_ERRORS = ('F821', 'F822', 'F823', 'F831', 'E999')

    def _msgType(self, msgId):
        # Per comments on _MSG_ID_CONVERTOR, mark PEP8/pyflake errors as errors. All
        # other errors are shown as warnings.
        if(msgId in self._PEP8_ERRORS or
           msgId in self._PYFLAKES_ERRORS):
            return Qutepart.LINT_ERROR
        else:
            return self._MSG_ID_CONVERTOR[msgId[0]]

    def _processSync(self, language, filePath):
        conf = core.config()['Lint']['Python']
        ignored = ','.join(conf['IgnoredMessages'].split())
        try:
            stdout = get_console_output([conf['Path'],
                                         '--max-line-length={}'.format(conf['MaxLineLength']),
                                         '--ignore={}'.format(ignored),
                                         filePath])[0]
        except OSError:
            return

        result = {}

        for line in stdout.splitlines():
            match = self._PARSER_REG_EXP.match(line)
            if match:
                filePath = match.group(1)
                lineNumber = match.group(2)
                rest = match.group(4)

                msgId, msgText = rest.lstrip().split(' ', 1)

                lineIndex = int(lineNumber) - 1
                msgType = self._msgType(msgId)

                if msgType is not None:  # not ignored
                    if lineIndex not in result:
                        result[lineIndex] = (msgType, rest)

        return result


class Plugin(QObject):
    """Main class. Interface for the core.
    """

    _LEVEL_FILTER = {'errors': (Qutepart.LINT_ERROR,),
                     'errorsAndWarnings': (Qutepart.LINT_ERROR, Qutepart.LINT_WARNING),
                     'all': (Qutepart.LINT_ERROR, Qutepart.LINT_WARNING, Qutepart.LINT_NOTE)
                     }

    def __init__(self):
        QObject.__init__(self)

        self._installed = False
        self._myMessageIsShown = False
        self._thread = None

        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)
        core.uiSettingsManager().dialogAccepted.connect(self._applySettings)

        self._applySettings()

    def terminate(self):
        """Uninstall the plugin
        """
        if self._thread is not None:
            self._thread.stopAsync()
            self._thread.wait()

        self._uninstall()

        core.uiSettingsManager().aboutToExecute.disconnect(self._onSettingsDialogAboutToExecute)
        core.uiSettingsManager().dialogAccepted.disconnect(self._applySettings)

    def _install(self):
        if self._installed:
            return

        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        core.workspace().cursorPositionChanged.connect(self._onCursorPositionChanged)
        core.workspace().modificationChanged.connect(self._onModificationChanged)
        core.mainWindow().statusBar().messageChanged.connect(self._onStatusBarMessageChanged)

        self._installed = True

    def _uninstall(self):
        if not self._installed:
            return

        core.workspace().documentOpened.disconnect(self._onDocumentOpened)
        core.workspace().currentDocumentChanged.disconnect(self._onCurrentDocumentChanged)
        core.workspace().cursorPositionChanged.disconnect(self._onCursorPositionChanged)
        core.workspace().modificationChanged.disconnect(self._onModificationChanged)
        core.mainWindow().statusBar().messageChanged.disconnect(self._onStatusBarMessageChanged)

        if self._thread is not None:
            self._thread.resultsReady.disconnect(self._onResultsReady)
            self._thread.stopAsync()
            self._thread.wait()
            self._thread = None

        self._clearMessage()

        self._installed = False

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        from .settings_widget import SettingsWidget
        widget = SettingsWidget(dialog)

        icon = QIcon(os.path.join(os.path.dirname(__file__), 'python.png'))
        dialog.appendPage("Lint/Python", widget, icon)

        # Options
        dialog.appendOption(CheckableOption(dialog, core.config(), "Lint/Python/Enabled", widget.gbEnabled))
        dialog.appendOption(ChoiseOption(dialog, core.config(), "Lint/Python/Show",
                                         {widget.rbErrors: "errors",
                                          widget.rbErrorsAndWarnings: "errorsAndWarnings",
                                          widget.rbAll: "all"}))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Lint/Python/Path", widget.leFlake8Path))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Lint/Python/IgnoredMessages", widget.leIgnoredMessages))
        dialog.appendOption(NumericOption(dialog, core.config(),
                                          "Lint/Python/MaxLineLength", widget.spMaxLineLength))

    def _applySettings(self):
        if core.config()['Lint']['Python']['Enabled']:
            self._install()
            if self._isSupported(core.workspace().currentDocument()):
                self._processDocument(core.workspace().currentDocument())
        else:
            self._uninstall()
            for document in core.workspace().documents():
                document.qutepart.lintMarks = {}

    def _processDocument(self, document):
        if self._thread is None:
            self._thread = ProcessorThread()
            self._thread.resultsReady.connect(self._onResultsReady)

        self._thread.process(document)

    def _isSupported(self, document):
        return document is not None and \
            document.filePath() is not None and \
            document.qutepart.language() in ('Python',)

    def _onDocumentOpened(self, document):
        if not core.config()['Lint']['Python']['Enabled']:
            return

        if self._isSupported(document):
            self._processDocument(document)

    def _onCurrentDocumentChanged(self, old, new):
        self._clearMessage()

    def _onCursorPositionChanged(self, document):
        lineNumber = document.qutepart.cursorPosition[0]
        if lineNumber in document.qutepart.lintMarks:
            msgType, msgText = document.qutepart.lintMarks[lineNumber]
            core.mainWindow().statusBar().showMessage(msgText)
            self._myMessageIsShown = True
        else:
            self._clearMessage()

    def _clearMessage(self):
        statusBar = core.mainWindow().statusBar()
        if self._myMessageIsShown:
            statusBar.clearMessage()

    def _onModificationChanged(self, document, modified):
        if not modified:
            if self._isSupported(document):
                self._processDocument(document)

    def _onStatusBarMessageChanged(self):
        self._myMessageIsShown = False

    @pyqtSlot(object, object)
    def _onResultsReady(self, document, results):
        # Check that the document with lint marks is still the current document.
        if core.workspace().currentDocument() is not document:
            return
        errors = 0
        warnings = 0

        visibleMessagesFilter = self._LEVEL_FILTER[core.config().get('Lint/Python/Show')]

        filteredResults = {lineNumber: value
                           for lineNumber, value in results.items()
                           if (value[0] in visibleMessagesFilter)}

        for level, message in filteredResults.values():
            if level == Qutepart.LINT_ERROR:
                errors += 1
            elif level == Qutepart.LINT_WARNING:
                warnings += 1

        document.qutepart.lintMarks = filteredResults
        if document.qutepart.cursorPosition[0] in filteredResults:
            self._onCursorPositionChanged(document)  # show msg on statusbar
        elif errors:
            core.mainWindow().statusBar().showMessage('Lint: {} error(s) found'.format(errors))
            self._myMessageIsShown = True
        elif warnings:
            core.mainWindow().statusBar().showMessage('Lint: {} warning(s) found'.format(warnings))
            self._myMessageIsShown = True
