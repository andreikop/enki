import unittest
import logging
import os
import sys
import threading
import shutil

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QApplication, QDialog
from PyQt4.QtTest import QTest

import qutepart

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import enki.core.defines
enki.core.defines.CONFIG_DIR = '/tmp'
from enki.core.core import core

logging.basicConfig(level=logging.ERROR)
logging.getLogger('qutepart').removeHandler(qutepart.consoleHandler)


def in_main_loop(func, *args):
    """Decorator executes test method in the QApplication main loop.
    QAction shortcuts doesn't work, if main loop is not running.
    Do not use for tests, which doesn't use main loop, because it slows down execution.
    """
    def wrapper(*args):
        self = args[0]
        
        def execWithArgs():
            core.mainWindow().show()
            QTest.qWaitForWindowShown(core.mainWindow())
            while self.app.hasPendingEvents():
                self.app.processEvents()
            
            try:
                func(*args)
            finally:
                while self.app.hasPendingEvents():
                    self.app.processEvents()
                self.app.quit()
        
        QTimer.singleShot(0, execWithArgs)
        
        self.app.exec_()
    
    wrapper.__name__ = func.__name__  # for unittest test runner
    return wrapper


class TestCase(unittest.TestCase):
    CREATE_NOT_SAVED_DOCUMENT = True
    NOT_SAVED_DOCUMENT_TEXT = None
    
    app = QApplication( sys.argv )
    
    TEST_FILES_DIR = '/tmp/enki-tests/'
    
    EXISTING_FILE = TEST_FILES_DIR + 'existing_file.txt'
    EXISTING_FILE_TEXT = 'hi\n'
    
    def _cleanUpFs(self):
        if os.path.isfile('/tmp/enki.json'):
            os.unlink('/tmp/enki.json')
        
        if os.path.isdir(self.TEST_FILES_DIR):
            shutil.rmtree(self.TEST_FILES_DIR)
        
    
    def setUp(self):
        self._cleanUpFs()
        os.mkdir(self.TEST_FILES_DIR)
        with open(self.EXISTING_FILE, 'w') as f:
            f.write(self.EXISTING_FILE_TEXT)
        
        core.init(None)
        
        if self.CREATE_NOT_SAVED_DOCUMENT:
            core.workspace().createEmptyNotSavedDocument()
            if self.NOT_SAVED_DOCUMENT_TEXT is not None:
                core.workspace().currentDocument().qutepart.text = self.NOT_SAVED_DOCUMENT_TEXT
    
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
        """Create file in TEST_FILES_DIR.
        
        File is opened
        """
        path = self.TEST_FILES_DIR + name
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
    
    def findDock(self, windowTitle):
        for dock in core.mainWindow().findChildren(DockWidget):
            if dock.windowTitle() == windowTitle:
                return dock
        else:
            self.fail('Dock {} not found'.format(windowTitle))
