#!/usr/bin/env python3
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
import os
import os.path
import sys

# Local application imports
# -------------------------
# Do this before PyQt imports so that base will set up sip API correctly.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

# Third-party library imports
# ---------------------------
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
from PyQt5.QtTest import QTest


# Tests
# =====
# waitForSignal
# -------------
class BackgroundThread(QThread):
    """ This is a helper class used for multi-threaded testing.

    It waits timeoutMs before emitting the done signal.

    """
    done = pyqtSignal()

    def __init__(self, timeoutMs):
        QThread.__init__(self)
        self.timeoutMs = timeoutMs

    def run(self):
        QTest.qWait(self.timeoutMs)
        self.done.emit()


class TestSignal(QObject):
    """ This is a dummy class which contains a single testSignal."""
    # Create a test signal with one argument.
    testSignal = pyqtSignal(int)
    # Create a test signal with several arguments.
    testSignalArgs = pyqtSignal(str, int, float)


# Unit tests.
@unittest.skipIf('TRAVIS_OS_NAME' in os.environ, 'Fails on Travis')
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

    # Test that signals with arguments work.
    def test_5(self):
        ts = TestSignal()
        self.assertTrue(base.waitForSignal(lambda: ts.testSignal.emit(1),
                                           ts.testSignal, 100))

    # Check the arguements emitted by the requested signal.
    def test_7(self):
        ts = TestSignal()
        self.assertFalse(base.waitForSignal(lambda: ts.testSignal.emit(1),
                                            ts.testSignal, 100, (2,)))

    # Check the arguements emitted by the requested signal.
    def test_8(self):
        ts = TestSignal()
        self.assertTrue(base.waitForSignal(lambda: ts.testSignal.emit(1),
                                           ts.testSignal, 100, (1,)))

    # Check several arguements emitted by the requested signal.
    def test_9(self):
        ts = TestSignal()
        self.assertFalse(base.waitForSignal(lambda: ts.testSignalArgs.emit('hello', 3, 3.14),
                                            ts.testSignalArgs, 100, (2,)))

    # Check several arguements emitted by the requested signal.
    def test_10(self):
        ts = TestSignal()
        self.assertFalse(base.waitForSignal(lambda: ts.testSignalArgs.emit('hello', 3, 3.14),
                                            ts.testSignalArgs, 100, ('Hello', 3, 3.14)))

    # Check several arguements emitted by the requested signal.
    def test_11(self):
        ts = TestSignal()
        self.assertTrue(base.waitForSignal(lambda: ts.testSignalArgs.emit('hello', 3, 3.14),
                                           ts.testSignalArgs, 100, ('hello', 3, 3.14)))

    # Make sure exceptions in sender() are raised properly.
    def test_11(self):
        ts = TestSignal()
        with self.assertRaises(AssertionError):
            base.waitForSignal(lambda: self.fail(), ts.testSignal, 100)


# inMainLoop
# ----------
class TestInMainLoop(base.TestCase):
    # A helper function to raise an exception in the main loop.

    @base.inMainLoop
    def _failInMainLoop(self):
        self.fail()

    # Make sure exceptions inMainLoop get propagated.
    def test_1(self):
        with self.assertRaises(AssertionError):
            self._failInMainLoop()

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
