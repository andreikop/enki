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


class TestCase(unittest.TestCase):
    CREATE_EMPTY_DOCUMENT = True
    
    def setUp(self):
        try:
            os.unlink('/tmp/enki.json')
        except OSError, IOError:
            pass
        
        self.app = QApplication( sys.argv )
        core.init(None)
        
        if self.CREATE_EMPTY_DOCUMENT:
            core.workspace().createEmptyNotSavedDocument()
    
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
    
