"""
mitscheme --- MIT Scheme integration. Interactive Scheme console
================================================================

File contains module functionality
"""

import os.path

from PyQt4.QtCore import pyqtSignal, QEvent, QObject, Qt, QTimer
from PyQt4.QtGui import QFileDialog, QIcon, QMessageBox, QWidget

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
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        self.pbInterpreterPath.clicked.connect(self._onPbInterpreterPathClicked)
    
    def _onPbInterpreterPathClicked(self):
        path = QFileDialog.getOpenFileName(core.mainWindow(), 'Interpreter path')
        if path:
            self.leInterpreterPath.setText(path)


class ReplDock(DockWidget):
    """Dock widget with terminal emulator
    """
    def __init__(self, widget, replName, title, icon):
        DockWidget.__init__(self, core.mainWindow(), title, icon, "Alt+M")

        self.setAllowedAreas( Qt.BottomDockWidgetArea)
        
        self._action = core.actionManager().addAction("mView/a%s" % replName, self.showAction())

        self.setWidget(widget)
        self.setFocusProxy(widget)
        widget.installEventFilter(self)
    
    def del_(self):
        core.actionManager().removeAction(self._action)
    
    def eventFilter(self, obj, event):
        """Event filter for the widget. Catches Esc pressings. It is necessary, because QScintilla eats it
        """
        if (event.type() == QEvent.KeyPress or event.type() == QEvent.ShortcutOverride) and \
           event.key() == Qt.Key_Escape and \
           event.modifiers() == Qt.NoModifier:
            self.hide()
            return True
        return DockWidget.eventFilter(self, obj, event)

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
    """Terminal emulator widget
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
                break;
            
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
        
        self._term.appendOutput("Execute any command to run the interpreter\n")

    def __del__(self):
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

    def start(self):
        """Start scheme process
        """
        if self._processIsRunning:
            return

        try:
            self._buffPopen.start()
        except OSError, ex:
            fullName = self._fullName.replace(' ', '&nbsp;')
            text = '<p>Interpreter path: %s</p>' % self._interpreterPath
            text += '<p>Error: %s</p>' % unicode(str(ex), 'utf8')
            text += '<p>Make sure interpreter is installed and go to '\
                    '<b>Settings -> Settings -> Modes -> %s</b> to correct the path</p>' % fullName
            text = '<html>%s</html' % text
            QMessageBox.critical (core.mainWindow(),
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

    def execCommand(self, text):
        """Execute text
        """
        if not self._processIsRunning:
            try:
                self.start()
            except UserWarning:
                return

        self._processOutput() # write old output to the log, and only then write fresh input
        self._buffPopen.write(text)
    
    def _processOutput(self):
        """Append output from Popen to widget, if available
        """
        output = self._buffPopen.readOutput()
        if output:
            self._term.appendOutput(output)
        if self._processIsRunning and not self._buffPopen.isAlive():
            self.stop()

class MitScheme(_AbstractInterpreter):
    """MIT scheme interpreter
    """
    def _createTermWidget(self):
        return MitSchemeTermWidget(self)
    
    def loadFile(self, filePath):
        """Load file using MIT Scheme load function
        """
        if not self._processIsRunning:
            try:
                self.start()
            except UserWarning:
                return
        self._buffPopen.write('(load "%s")' % filePath)

