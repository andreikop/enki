"""
repl --- MIT Scheme and Standard ML REPL
========================================

File contains plugin functionality implementation
"""

import os
import os.path

from PyQt5.QtCore import pyqtSignal, QObject, Qt, QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt5.QtGui import QFont
from PyQt5 import uic

from enki.core.core import core

from enki.widgets.dockwidget import DockWidget

import enki.lib.buffpopen
import enki.widgets.termwidget

#
# Integration with the core
#


class SettingsWidget(QWidget):
    """Settings widget. Insertted as a page to UISettings
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        self.pbInterpreterPath.clicked.connect(self._onPbInterpreterPathClicked)

    def _onPbInterpreterPathClicked(self):
        path, _ = QFileDialog.getOpenFileName(core.mainWindow(), 'Interpreter path')
        if path:
            self.leInterpreterPath.setText(path)


class ReplDock(DockWidget):
    """Dock widget with terminal emulator
    """

    def __init__(self, widget, title, icon):
        DockWidget.__init__(self, core.mainWindow(), title, icon, "Alt+I")
        self.setObjectName(title)

        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.setWidget(widget)
        self.setFocusProxy(widget)


#
# Plugin functionality
#
class _AbstractReplTermWidget(enki.widgets.termwidget.TermWidget):
    """Base class for REPL terminal widgets
    """

    def __init__(self, interpreter, *args):
        enki.widgets.termwidget.TermWidget.__init__(self, *args)
        self._interpreter = interpreter

    def childExecCommand(self, text):
        """Execute command. Called by parent class
        """
        self._interpreter.execCommand(text)


class MitSchemeTermWidget(_AbstractReplTermWidget):
    """Scheme terminal emulator widget
    """

    def isCommandComplete(self, text):
        """Parse the command and check, if it is complete and should be executed
        """
        # TODO support comments
        # Stage 1: remove strings
        index = 0
        foundStrings = []
        while True:
            try:
                index = text.index('"', index)
            except ValueError:
                break

            try:
                endIndex = text.index('"', index + 1)
            except ValueError:
                return False

            foundStrings.append((index, endIndex))
            index = endIndex + 1

        for foundString in foundStrings[::-1]:  # from the last found string
            text = text[:foundString[0]] + text[foundString[1] + 1:]  # remove found string

        # Stage 2: calculate braces
        # Let's MIT scheme check if braces are placed correctly. We just check count
        if text.count('(') != text.count(')'):
            return False

        return True


class SmlTermWidget(_AbstractReplTermWidget):
    """Standard ML terminal emulator widget
    """

    def isCommandComplete(self, text):
        """TODO support comments and strings
        """
        return text.rstrip().endswith(';')


class PythonTermWidget(_AbstractReplTermWidget):
    """Python terminal emulator widget
    """

    def isCommandComplete(self, text):
        """TODO support comments and strings
        """
        return True


class _AbstractInterpreter(QObject):
    """MIT scheme shell. Implements REPL. Graphical frontend for original terminal version.
    """

    processIsRunningChanged = pyqtSignal(bool)
    """
    processStopped(isRunning)

    **Signal** emitted, when MIT Scheme process starts and stops
    """  # pylint: disable=W0105

    def __init__(self, language, fullName, interpreterPath):
        QObject.__init__(self)
        self._fullName = fullName
        self._term = self._createTermWidget()
        self._term.setLanguage(language)
        self._interpreterPath = interpreterPath

        self._processOutputTimer = QTimer()  # I use Qt timer, because we must append data to GUI in the GUI thread
        self._processOutputTimer.timeout.connect(self._processOutput)
        self._processOutputTimer.setInterval(100)

        self._buffPopen = enki.lib.buffpopen.BufferedPopen(interpreterPath)
        self._processIsRunning = False

        self._term.appendHint("Execute any command to run the interpreter\n")

    def term(self):
        self.stop()

    def loadFile(self, filePath):
        """Load (interpret) the file
        """
        raise NotImplementedError()

    def _createTermWidget(self):
        """Create terminal emulator widget instance
        """
        raise NotImplementedError()

    def widget(self):
        """Terminal emulator widget
        """
        return self._term

    def start(self, args=[]):
        """Start scheme process
        """
        if self._processIsRunning:
            return

        try:
            self._buffPopen.start(args)
        except OSError as ex:
            fullName = self._fullName.replace(' ', '&nbsp;')
            text = '<p>Interpreter path: %s</p>' % self._interpreterPath
            text += '<p>Error: %s</p>' % str(ex)
            text += '<p>Make sure interpreter is installed and go to '\
                    '<b>Settings -> Settings -> Modes -> %s</b> to correct the path</p>' % fullName
            text = '<html>%s</html' % text
            QMessageBox.critical(core.mainWindow(),
                                 "Failed to run the interpreter",
                                 text)
            raise UserWarning("Failed to run the interpreter")

        self._processOutputTimer.start()
        self._processIsRunning = True
        self.processIsRunningChanged.emit(self._processIsRunning)

    def stop(self):
        """Stop scheme process
        """
        if not self._processIsRunning:
            return

        self._buffPopen.stop()
        self._processOutputTimer.stop()
        self._processIsRunning = False
        self._term.appendError("Interpreter process exited. Execute any command to run it again\n")
        self.processIsRunningChanged.emit(self._processIsRunning)
        self._term.terminate()

    def execCommand(self, text):
        """Execute text
        """
        if not text.endswith('\n'):
            text += '\n'

        if not self._processIsRunning:
            try:
                self.start()
            except UserWarning:
                return

        self._processOutput()  # write old output to the log, and only then write fresh input
        self._buffPopen.write(text)

    def _processOutput(self):
        """Append output from Popen to widget, if available
        """
        output = self._buffPopen.readOutput()
        if output:
            self._term.appendOutput(output)
        if self._processIsRunning and not self._buffPopen.isAlive():
            self.stop()

    @staticmethod
    def _termWidgetFont():
        return QFont(core.config()["Qutepart"]["Font"]["Family"],
                     core.config()["Qutepart"]["Font"]["Size"])


class MitSchemeInterpreter(_AbstractInterpreter):
    """MIT scheme interpreter
    """

    def _createTermWidget(self):
        return MitSchemeTermWidget(self, self._termWidgetFont())

    def loadFile(self, filePath):
        """Load file using MIT Scheme load function
        """
        if not self._processIsRunning:
            try:
                self.start()
            except UserWarning:
                return
        self._buffPopen.write('(load "%s")\n' % filePath)


class SmlInterpreter(_AbstractInterpreter):
    """SML interpreter
    """

    def __init__(self, *args):
        super(SmlInterpreter, self).__init__(*args)
        self._term.appendHint("Commands are ended with ';'\n")

    def _createTermWidget(self):
        return SmlTermWidget(self, self._termWidgetFont())

    def loadFile(self, filePath):
        """Load file with 'use foo.sml;'
        """
        if not self._processIsRunning:
            try:
                self.start()
            except UserWarning:
                return
        self._buffPopen.write('use "%s";\n' % filePath)


class PythonInterpreter(_AbstractInterpreter):
    """Python interpreter
    """

    def _createTermWidget(self):
        return PythonTermWidget(self, self._termWidgetFont())

    def loadFile(self, filePath):
        """Load file interactively using `python -i`
        """
        self.stop()
        self._term.clear()

        self._term.appendHint('{} {}\n'.format(self._interpreterPath, filePath))

        try:
            self.start([filePath])
        except UserWarning:
            return
