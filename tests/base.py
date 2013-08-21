import unittest
import logging
import os
import sys
import threading

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
    
    def setUp(self):
        try:
            os.unlink('/tmp/enki.json')
        except OSError, IOError:
            pass
        
        self.app = QApplication( sys.argv )
        core.init(None)
        
        if self.CREATE_NOT_SAVED_DOCUMENT:
            core.workspace().createEmptyNotSavedDocument()
            if self.NOT_SAVED_DOCUMENT_TEXT is not None:
                core.workspace().currentDocument().qutepart.text = self.NOT_SAVED_DOCUMENT_TEXT
    
    def tearDown(self):
        core.term()

    def _findDialog(self):
        for widget in self.app.topLevelWidgets():
            if widget.isVisible() and isinstance(widget, QDialog):
                return widget
        else:
            return None

    def openSettings(self, continueFunc):
        QTimer.singleShot(0, lambda: continueFunc(self._findDialog()))
        core.actionManager().action("mSettings/aSettings").trigger()
