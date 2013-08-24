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

sys.path.insert(0, os.path.abspath('..'))

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
    
    def _cleanUpFs(self):
        if os.path.isfile('/tmp/enki.json'):
            os.unlink('/tmp/enki.json')
        
        if os.path.isdir(self.TEST_FILES_DIR):
            shutil.rmtree(self.TEST_FILES_DIR)
        
    
    def setUp(self):
        self._cleanUpFs()
        os.mkdir(self.TEST_FILES_DIR)
        
        core.init(None)
        
        if self.CREATE_NOT_SAVED_DOCUMENT:
            core.workspace().createEmptyNotSavedDocument()
            if self.NOT_SAVED_DOCUMENT_TEXT is not None:
                core.workspace().currentDocument().qutepart.text = self.NOT_SAVED_DOCUMENT_TEXT
    
    def tearDown(self):
        core.workspace().closeAllDocuments()
        core.term()
        self._cleanUpFs()

    def _findDialog(self):
        for widget in self.app.topLevelWidgets():
            if widget.isVisible() and isinstance(widget, QDialog):
                QTest.qWaitForWindowShown(widget)
                return widget
        else:
            self.fail("Dialog not found")

    def openDialog(self, openDialogFunc, runInDialogFunc):
        """Open dialog by executing ``openDialogFunc`` and run ``runInDialogFunc``.
        Dialog is passed as a parameter to ``runInDialogFunc``
        """
        QTimer.singleShot(0, lambda: runInDialogFunc(self._findDialog()))
        openDialogFunc()

    def openSettings(self, runInDialogFunc):
        """Open Enki settings dialog and run ``runInDialogFunc``.
        Dialog is passed as a parameter to ``runInDialogFunc``
        """
        return self.openDialog(core.actionManager().action("mSettings/aSettings").trigger,
                               runInDialogFunc)
