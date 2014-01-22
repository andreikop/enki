#!/usr/bin/env python
#
# **************************************
# test_base.py -- Unit tests for base.py
# **************************************
#
#
# Imports
# =======
# Library imports
# ---------------
import unittest
import os.path
import sys

# Third-party library imports
# ---------------------------
import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt, QTimer, QEventLoop, QThread, pyqtSignal
from PyQt4.QtTest import QTest

# Local application imports
# -------------------------
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

# Tests
# =====
# waitForSignal
# -------------
# This is a helper class used for multi-threaded testing. It emits
# the started signal just after this thread starts, then waits
# timeout_ms before emitting the done signal.
class BackgroundThread(QThread):
    started = pyqtSignal()
    done = pyqtSignal()
    
    def __init__(self, timeout_ms):
        QThread.__init__(self)
        self.timeout_ms = timeout_ms
    
    def run(self):
        self.started.emit()
        QTest.qWait(self.timeout_ms)
        self.done.emit()


# Unit tests.
class TestWaitForSignal(unittest.TestCase):
    # Create a timer to send a timeout signal before the timeout.
    def test_1(self):
        t = QTimer()
        t.setInterval(50)
        t.setSingleShot(True)
        t.start()
        self.assertTrue(base.waitForSignal(t.timeout, 100))
        
    # Create a timer to send a timeout signal after the timeout.
    def test_2(self):
        t = QTimer()
        t.setInterval(100)
        t.setSingleShot(True)
        t.start()
        self.assertFalse(base.waitForSignal(t.timeout, 50))
        
    # Test operation from another thread: the other thread emits a signal before the timeout.
    def test_3(self):
        bt = BackgroundThread(50)
        # Run the assertion after the other thread starts.
        bt.started.connect(lambda: self.assertTrue(base.waitForSignal(bt.done, 100)))
        # Start the background thread, then wait for it to finish before leaving this test.
        bt.start()
        bt.wait()
        
    # Test operation from another thread: the other thread emits a signal after the timeout.
    def test_4(self):
        bt = BackgroundThread(100)
        # Run the assertion after the other thread starts.
        bt.started.connect(lambda: self.assertFalse(base.waitForSignal(bt.done, 50)))
        # Start the background thread, then wait for it to finish before leaving this test.
        bt.start()
        bt.wait()
        

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
