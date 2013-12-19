import unittest
import logging
import os
import sys
import threading
import shutil
import time
import tempfile

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QApplication, QDialog
from PyQt4.QtTest import QTest


import qutepart

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from enki.widgets.dockwidget import DockWidget
import enki.core.defines
enki.core.defines.CONFIG_DIR = tempfile.gettempdir()
from enki.core.core import core

logging.basicConfig(level=logging.ERROR)
logging.getLogger('qutepart').removeHandler(qutepart.consoleHandler)


class DummyProfiler:
    """Dummy profiler is used to run core without profiling"""
    def stepDone(self, description):
        pass

    def printInfo(self):
        pass


def _processPendingEvents(app):
    """Process pending application events.
    Timeout is used, because on Windows hasPendingEvents() always returns True
    """
    t = time.time()
    while app.hasPendingEvents() and (time.time() - t < 0.1):
        app.processEvents()


def inMainLoop(func, *args):
    """Decorator executes test method in the QApplication main loop.
    QAction shortcuts doesn't work, if main loop is not running.
    Do not use for tests, which doesn't use main loop, because it slows down execution.
    """
    def wrapper(*args):
        self = args[0]
        
        def execWithArgs():
            core.mainWindow().show()
            QTest.qWaitForWindowShown(core.mainWindow())
            _processPendingEvents(self.app)
            
            try:
                func(*args)
            finally:
                _processPendingEvents(self.app)
                self.app.quit()
        
        QTimer.singleShot(0, execWithArgs)
        
        self.app.exec_()
    
    wrapper.__name__ = func.__name__  # for unittest test runner
    return wrapper


class TestCase(unittest.TestCase):
    INIT_CORE = True
    
    app = QApplication( sys.argv )
    
    TEST_FILE_DIR = os.path.join(tempfile.gettempdir(), 'enki-tests')
    
    EXISTING_FILE = os.path.join(TEST_FILE_DIR, 'existing_file.txt')
    EXISTING_FILE_TEXT = 'hi\n'
    
    def _cleanUpFs(self):
        json_tmp = os.path.join(tempfile.gettempdir(), 'enki.json')
        try:
            os.unlink(json_tmp)
        except OSError as e:
            pass
        
        try:
            shutil.rmtree(self.TEST_FILE_DIR)
        except OSError as e:
            pass

    
    def setUp(self):
        self._cleanUpFs()
        try:
            os.mkdir(self.TEST_FILE_DIR)
        except OSError as e:
            pass
        
        with open(self.EXISTING_FILE, 'w') as f:
            f.write(self.EXISTING_FILE_TEXT)
        
        if self.INIT_CORE:
            core.init(DummyProfiler())
    
    def tearDown(self):
        for document in core.workspace().documents():
            document.qutepart.text = ''  # clear modified flag, avoid Save Files dialog
        
        core.workspace().closeAllDocuments()
        core.term()
        self._cleanUpFs()

    def keyClick(self, key, modifiers=Qt.NoModifier, widget=None):
        """Alias for ``QTest.keyClick``.
        
        If widget is none - focused widget will be keyclicked"""
        if widget is not None:
            QTest.keyClick(widget, key, modifiers)
        else:
            QTest.keyClick(self.app.focusWidget(), key, modifiers)
    
    def keyClicks(self, text, modifiers=Qt.NoModifier, widget=None):
        """Alias for ``QTest.keyClicks``.
        
        If widget is none - focused widget will be keyclicked"""
        if widget is not None:
            QTest.keyClicks(widget, text, modifiers)
        else:
            QTest.keyClicks(self.app.focusWidget(), text, modifiers)
    
    def createFile(self, name, text):
        """Create file in TEST_FILE_DIR.
        
        File is opened
        """
        path = os.path.join(self.TEST_FILE_DIR, name)
        with open(path, 'w') as file_:
            file_.write(text)
        
        return core.workspace().openFile(path)
    
    def _findDialog(self):
        for widget in self.app.topLevelWidgets():
            if widget.isVisible() and isinstance(widget, QDialog):
                return widget
        else:
            self.fail("Dialog not found")

    def openDialog(self, openDialogFunc, runInDialogFunc):
        """Open dialog by executing ``openDialogFunc`` and run ``runInDialogFunc``.
        Dialog is passed as a parameter to ``runInDialogFunc``
        """
        QTimer.singleShot(100, lambda: runInDialogFunc(self._findDialog()))
        openDialogFunc()

    def openSettings(self, runInDialogFunc):
        """Open Enki settings dialog and run ``runInDialogFunc``.
        Dialog is passed as a parameter to ``runInDialogFunc``
        """
        return self.openDialog(core.actionManager().action("mSettings/aSettings").trigger,
                               runInDialogFunc)
    
    def sleepProcessEvents(self, delay):
        end = time.time() + delay
        while time.time() < end:
            QApplication.instance().processEvents()
            time.sleep(0.01)
    
    def findDock(self, windowTitle):
        for dock in core.mainWindow().findChildren(DockWidget):
            if dock.windowTitle() == windowTitle:
                return dock
        else:
            self.fail('Dock {} not found'.format(windowTitle))
