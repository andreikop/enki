"""
mitscheme --- MIT Scheme integration. Interactive Scheme console
================================================================

File contains module functionality
"""

import os.path

from PyQt4.QtCore import pyqtSignal, QEvent, QObject, Qt, QTimer
from PyQt4.QtGui import QFileDialog, QIcon, QMessageBox, QWidget
from PyQt4 import uic

from mks.core.core import core

from mks.fresh.dockwidget.pDockWidget import pDockWidget

import mks.lib.buffpopen
import mks.lib.termwidget

#
# Integration with the core
#

class MitSchemeSettings(QWidget):
    """Settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'MitSchemeSettings.ui'), self)
        self.pbInterpreterPath.clicked.connect(self._onPbInterpreterPathClicked)
    
    def _onPbInterpreterPathClicked(self):
        path = QFileDialog.getOpenFileName(core.mainWindow(), 'MIT Scheme interpreter path')
        if path:
            self.leInterpreterPath.setText(path)


class MitSchemeDock(pDockWidget):
    """Dock widget with terminal emulator
    """
    def __init__(self, widget):
        pDockWidget.__init__(self, "&MIT Scheme", core.mainWindow())
        self.setObjectName("MitSchemeDock")
        self.setWindowIcon(QIcon(':/mksicons/languages/scheme.png'))
        self.setAllowedAreas( Qt.BottomDockWidgetArea)
        
        self.showAction().setShortcut("Alt+M")
        core.actionManager().addAction("mView/aMitScheme", self.showAction())

        self.setWidget(widget)
        self.setFocusProxy(widget)
        widget.installEventFilter(self)
    
    def del_(self):
        core.actionManager().removeAction("mView/aMitScheme")
    
    def eventFilter(self, obj, event):
        """Event filter for the widget. Catches Esc pressings. It is necessary, because QScintilla eats it
        """
        if (event.type() == QEvent.KeyPress or event.type() == QEvent.ShortcutOverride) and \
           event.key() == Qt.Key_Escape and \
           event.modifiers() == Qt.NoModifier:
            self.hide()
            return True
        return pDockWidget.eventFilter(self, obj, event)

#
# Plugin functionality
#

class MitSchemeTermWidget(mks.lib.termwidget.TermWidget):
    """Terminal emulator widget
    """
    def __init__(self, mitScheme, *args):
        mks.lib.termwidget.TermWidget.__init__(self, *args)
        self._mitScheme = mitScheme

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

    def childExecCommand(self, text):
        """Execute command. Called by parent class
        """
        self._mitScheme.execCommand(text)

class MitScheme(QObject):
    """MIT scheme shell. Implements REPL. Graphical frontend for original terminal version.
    """
    
    processIsRunningChanged = pyqtSignal(bool)
    """
    processStopped(isRunning)
    
    **Signal** emitted, when MIT Scheme process starts and stops
    """  # pylint: disable=W0105

    def __init__(self, interpreterPath):
        QObject.__init__(self)
        self._term = MitSchemeTermWidget(self)
        self._term.setLanguage('Scheme')
        self._interpreterPath = interpreterPath
        
        self._processOutputTimer = QTimer()  # I use Qt timer, because we must append data to GUI in the GUI thread
        self._processOutputTimer.timeout.connect(self._processOutput)
        self._processOutputTimer.setInterval(100)

        self._buffPopen = mks.lib.buffpopen.BufferedPopen(interpreterPath)
        self._schemeIsRunning = False
        
        self._term.appendOutput("Execute any command to run the scheme interpreter\n")

    def __del__(self):
        self.stop()
    
    def widget(self):
        """MIT Scheme emulator
        """
        return self._term

    def start(self):
        """Start scheme process
        """
        if self._schemeIsRunning:
            return

        try:
            self._buffPopen.start()
        except OSError, ex:
            text = '<p>Interpreter path: %s</p>' % self._interpreterPath
            text += '<p>Error: %s</p>' % unicode(str(ex), 'utf8')
            text += '<p>Make sure MIT Scheme is installed and go to '\
                    '<b>Settings -> Settings -> Modes -> MIT&nbsp;Scheme</b> to correct the path</p>'
            text = '<html>%s</html' % text
            QMessageBox.critical (core.mainWindow(),
                                  "Failed to run MIT Scheme", 
                                  text)
            raise UserWarning("Failed to run the interpreter")

        self._processOutputTimer.start()
        self._schemeIsRunning = True
        self.processIsRunningChanged.emit(self._schemeIsRunning)

    def stop(self):
        """Stop scheme process
        """
        if not self._schemeIsRunning:
            return

        self._buffPopen.stop()
        self._processOutputTimer.stop()
        self._schemeIsRunning = False
        self._term.appendError("Interpreter process exited. Execute any command to run it again\n")
        self.processIsRunningChanged.emit(self._schemeIsRunning)

    def execCommand(self, text):
        """Execute text
        """
        if not self._schemeIsRunning:
            try:
                self.start()
            except UserWarning:
                return

        self._processOutput() # write old output to the log, and only then write fresh input
        self._buffPopen.write(text)
    
    def loadFile(self, filePath):
        """Load file using MIT Scheme load function
        """
        if not self._schemeIsRunning:
            try:
                self.start()
            except UserWarning:
                return
        self._buffPopen.write('(load "%s")' % filePath)
    
    def _processOutput(self):
        """Append output from Popen to widget, if available
        """
        output = self._buffPopen.readOutput()
        if output:
            self._term.appendOutput(output)
        if self._schemeIsRunning and not self._buffPopen.isAlive():
            self.stop()
