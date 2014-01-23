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

from PyQt4.QtCore import Qt, QTimer, QEventLoop, QThread, QObject, pyqtSignal
from PyQt4.QtTest import QTest

# Local application imports
# -------------------------
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

# Tests
# =====
# waitForSignal
# -------------
# This is a helper class used for multi-threaded testing. It
# waits timeout_ms before emitting the done signal.
class BackgroundThread(QThread):
    done = pyqtSignal()
    
    def __init__(self, timeout_ms):
        QThread.__init__(self)
        self.timeout_ms = timeout_ms
    
    def run(self):
        QTest.qWait(self.timeout_ms)
        self.done.emit()

# This is a dummy class which contains a single test_signal.
class TestSignal(QObject):
    # Create a test signal with one argument.
    test_signal = pyqtSignal(int)

# Unit tests.
class TestWaitForSignal(unittest.TestCase):
    
    # Create a timer to send a timeout signal before the timeout.
    def test_1(self):
        t = QTimer()
        t.setInterval(50)
        t.setSingleShot(True)
        self.assertTrue(base.waitForSignal(t.start, t.timeout, 100))
        
    # Create a timer to send a timeout signal after the timeout.
    def test_2(self):
        t = QTimer()
        t.setInterval(100)
        t.setSingleShot(True)
        self.assertFalse(base.waitForSignal(t.start, t.timeout, 50))
        
    # Test operation from another thread: the other thread emits a signal before the timeout.
    def test_3(self):
        bt = BackgroundThread(50)
        # Run the assertion after the other thread starts.
        self.assertTrue(base.waitForSignal(bt.start, bt.done, 100))
        # Wait for the background thread to finish before leaving this test.
        bt.wait()
        
    # Test operation from another thread: the other thread emits a signal after the timeout.
    def test_4(self):
        bt = BackgroundThread(100)
        self.assertFalse(base.waitForSignal(bt.start, bt.done, 50))
        # Wait for the background thread to finish before leaving this test.
        bt.wait()
        
    # Test that signals with multiple arguments work.
    def test_5(self):
        ts = TestSignal()
        self.assertTrue(base.waitForSignal(lambda: ts.test_signal.emit(1), ts.test_signal, 100))
        
    # Make sure exceptions in sender() are raised properly.
    def test_6(self):
        ts = TestSignal()
        with self.assertRaises(AssertionError):
            base.PRINT_EXEC_TRACKBACK = False
            base.waitForSignal(lambda: self.fail(), ts.test_signal, 100)
        

# inMainLoop
# ----------
class TestInMainLoop(unittest.TestCase):
    # Make sure exceptions get propagated.
    def test_1(self):
        with self.assertRaises(AssertionError):
            base.PRINT_EXEC_TRACKBACK = False
            base.inMainLoop(self.fail())

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
