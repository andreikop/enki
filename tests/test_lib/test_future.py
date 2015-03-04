#!/usr/bin/env python
#
# .. -*- coding: utf-8 -*-
#
# *****************************************
# future_test.py - Unit tests for future.py
# *****************************************
# To run the tests, invoke ``py.test future_test.py``. Helpful command-line
# options:
#
# -s
#    Don't capture stdout, instead dump to screen. See `capturing
#    <http://pytest.org/latest/capture.html>`_.
#
# -k name
#    Run only tests matching name. See `specifying tests
#    <http://pytest.org/latest/usage.html#specifying-tests-selecting-tests>`_.
#
# Imports
# =======
import time
import sys
import os.path
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base

# Library imports
# ---------------
from Queue import Queue
import unittest
#
# Third-party imports
# -------------------
from PyQt4.QtCore import pyqtSignal, QObject, QTimer, QEventLoop, QThread
#
# Local imports
# -------------
from enki.lib.future import AsyncController, Future
#
# Test helpers
# ============
class WaitForSignal(unittest.TestCase):
    def __init__(self,
      # The signal to wait for.
      signal,
      # The maximum time to wait for the signal to be emitted, in ms.
      timeoutMs,
      # True to self.assertif the signal wasn't emitted.
      assertIfNotRaised=True,
      # Expected parameters which this signal must supply.
      expectedSignalParams=None,
      # True to print exceptions raised in the event loop
      printExcTraceback=True):

        self.signal = signal
        self.timeoutMs = timeoutMs
        self.expectedSignalParams = expectedSignalParams
        self.assertIfNotRaised = assertIfNotRaised
        self.printExcTraceback = printExcTraceback

        # Stores the result of comparing self.expectedSignalParams with the
        # actual params.
        self.areSenderSignalArgsWrong = False
        # True if signal was received.
        self.gotSignal = False

    # Create a slot which receives a senderSignal with any number
    # of arguments. Check the arguments against their expected
    # values, if requested, storing the result in senderSignalArgsWrong[0].
    # (I can't use senderSignalArgsWrong = True/False, since
    # non-local variables cannot be assigned in another scope).
    def signalSlot(self, *args):
        # If the senderSignal args should be checked and they
        # don't match, then they're wrong. In all other cases,
        # they're right.
        if self.expectedSignalParams:
            self.areSenderSignalArgsWrong = (self.expectedSignalParams != args)
        # We received the requested signal, so exit the event loop or never
        # enter it (exit won't exit an event loop that hasn't been run). When
        # this is nested inside other WaitForSignal clauses, signals may be
        # received in another QEventLoop, even before this object's QEventLoop
        # starts.
        self.qe.exit()
        self.gotSignal = True

    def __enter__(self):
        # Create an event loop to run in. Otherwise, we need to use the papp
        # (QApplication) main loop, which may already be running and therefore
        # unusable.
        self.qe = QEventLoop()

        # Connect both signals to a slot which quits the event loop.
        self.signal.connect(self.signalSlot)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Create a single-shot timer. Could use QTimer.singleShot(),
        # but can't cancel this / disconnect it.
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.qe.quit)
        self.timer.start(self.timeoutMs)

        # Catch any exceptions which the EventLoop would otherwise catch
        # and not re-raise.
        self.exceptions = None
        def excepthook(type_, value, tracebackObj):
            self.exceptions = (value, tracebackObj)
            if self.printExcTraceback:
                oldExcHook(type_, value, tracebackObj)
            self.qe.exit()
        oldExcHook = sys.excepthook
        sys.excepthook = excepthook

        # Wait for an emitted signal, unless it already occurred.
        if not self.gotSignal:
            self.qe.exec_()
        # Restore the old exception hook
        sys.excepthook = oldExcHook
        # Clean up: don't allow the timer to call app.quit after this
        # function exits, which would produce "interesting" behavior.
        ret = self.timer.isActive()
        self.timer.stop()
        # Stopping the timer may not cancel timeout signals in the
        # event queue. Disconnect the signal to be sure that loop
        # will never receive a timeout after the function exits.
        # Likewise, disconnect the senderSignal for the same reason.
        self.signal.disconnect(self.signalSlot)
        self.timer.timeout.disconnect(self.qe.quit)

        # If an exception occurred in the event loop, re-raise it.
        if self.exceptions:
            value, tracebackObj = self.exceptions
            raise value, None, tracebackObj

        # Check that the signal occurred.
        self.sawSignal = ret and not self.areSenderSignalArgsWrong
        if self.assertIfNotRaised:
            self.assertTrue(self.sawSignal)

        # Don't mask exceptions.
        return False

# A helper class to signal when its method function is executed.
class Emitter(QObject):
    bing = pyqtSignal()

    def __init__(self, expected=None, assertEquals=None):
        QObject.__init__(self)
        self.expected = expected
        self.assertEquals = assertEquals

    def g(self, future):
        self.thread = QThread.currentThread()
        # Retrieve the result, even if it won't be checked, to make sure that no
        # exceptions were raised.
        self.result = future.result
        if self.expected:
            self.assertEquals(self.expected, self.result)
        self.bing.emit()

# Emit a signal afte receiving three unique signals.
class SignalCombiner(QObject):
    allEmitted = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.s = set()

    def onBing(self):
        assert self.sender()
        self.s.add(self.sender())
        if len(self.s) == 3:
            self.allEmitted.emit()

#
# Unit tests
# ==========
class TestAsyncController(unittest.TestCase):
    # Tuples of AsyncController params to test over.
    syncPoolAndThread = ('Sync', 'QThread', 0, 1, 4)
    poolAndThread = ('QThread', 0, 1, 4)
    poolOnly = (0, 1, 4)
    singleThreadOnly = ('QThread', 1)
    multipleThreadsOnly = (4,)

    # Verify that a test function is run.
    def test_1(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                # gotHere must be a list in order to f to change it in a way that is
                # visible outside of f.
                gotHere = [False]
                def f():
                    gotHere[0] = True
                future = ac._wrap(None, f)
                with WaitForSignal(future.signalInvoker.doneSignal, 1000):
                    ac._start(future)
                self.assertTrue(gotHere[0])

    # Verify that the result function is run.
    def test_2(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                em = Emitter(2, self.assertEquals)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, lambda: 2)

    # Verify that a result from f is passed to g.
    def test_3(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                em = Emitter(123, self.assertEquals)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, lambda x: x + 2, 121)

    # Verify that correct arguments are passed to f.
    def test_4(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                def f(a, b, c=2, d=4):
                    self.assertEquals(a, 2)
                    self.assertEquals(b, 3)
                    self.assertEquals(c, 4)
                    self.assertEquals(d, 5)
                em = Emitter()
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, 2, 3, d=5, c=4)

    # Verify that f actually runs in a separate thread.
    def test_5(self):
        for _ in self.poolAndThread:
            with AsyncController(_) as ac:
                def f(currentThread):
                    self.assertNotEquals(currentThread, QThread.currentThread())
                em = Emitter()
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, QThread.currentThread())

    # Verify that f actually runs in separate pooled threads.
    def test_6(self):
        # Don't test with one pooled thread -- this test expects at least two
        # threads.
        with AsyncController(2) as ac:
            q = Queue()
            def f():
                q.get()
                return QThread.currentThread()
            em1 = Emitter()
            em2 = Emitter()
            ac.start(em1.g, f)
            ac.start(em2.g, f)
            with WaitForSignal(em1.bing, 1000), WaitForSignal(em2.bing, 1000):
                q.put(None)
                q.put(None)
            s = set([em1.result, em2.result, QThread.currentThread()])
            self.assertEquals(len(s), 3)

    # Verify that the correct functions and callbacks get executed.
    def test_7(self):
        for _ in ('Sync', 'QThread'):
            with AsyncController(_) as ac:
                em1 = Emitter(15, self.assertEquals)
                em2 = Emitter(16, self.assertEquals)
                em3 = Emitter(17, self.assertEquals)
                ac.start(em1.g, lambda: 15)
                ac.start(em2.g, lambda: 16)
                future3 = ac._wrap(em3.g, lambda: 17)
                with WaitForSignal(em3.bing, 1000):
                    ac._start(future3)

    # Verify that the correct functions and callbacks get executed in a pool.
    def test_8(self):
        for _ in self.poolOnly:
            with AsyncController(_) as ac:
                q1 = Queue()
                q2 = Queue()
                q3 = Queue()
                em1 = Emitter(15, self.assertEquals)
                em2 = Emitter(16, self.assertEquals)
                em3 = Emitter(17, self.assertEquals)
                future1 = ac.start(em1.g, lambda: q1.get())
                future2 = ac.start(em2.g, lambda: q2.get())
                future3 = ac.start(em3.g, lambda: q3.get())
                sc = SignalCombiner()
                em1.bing.connect(sc.onBing)
                em2.bing.connect(sc.onBing)
                em3.bing.connect(sc.onBing)
                with WaitForSignal(sc.allEmitted, 1000):
                    q1.put(15)
                    q2.put(16)
                    q3.put(17)

    # Verify that exceptions get propogated correctly.
    def test_9(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                def f():
                    raise TypeError
                em = Emitter()
                with self.assertRaises(TypeError), WaitForSignal(em.bing, 1000, printExcTraceback=False):
                    ac.start(em.g, f)

    # Verify that if ``f`` is launched in a thread, ``g`` will be run in that
    # same thread.
    def test_10(self):
        with AsyncController('QThread') as ac:
            em1 = Emitter()
            def f1():
                ac.start(em1.g, lambda: QThread.currentThread())
            with WaitForSignal(em1.bing, 1000):
                ac.start(None, f1)
            self.assertEquals(em1.thread, em1.result)

    # Verify that if ``f`` is launched in a thread, ``g`` will be run in that
    # same thread. (For thread pools).
    def test_11(self):
        # Don't test with one pooled thread -- this test expects at least two
        # threads.
        with AsyncController(2) as ac:
            em2 = Emitter()
            def f2():
                future = ac.start(em2.g, lambda x: x, QThread.currentThread())
                # The doneSignal won't be processed without an event loop. A
                # thread pool doesn't create one, so make our own to run ``g``.
                qe = QEventLoop()
                future.signalInvoker.doneSignal.connect(qe.exit)
                qe.exec_()
            with WaitForSignal(em2.bing, 1000):
                ac.start(None, f2)
            self.assertEquals(em2.thread, em2.result)

    # Verify that job status and cancelation works: while a job in in progress,
    # cancel an pending job.
    def test_12(self):
        for _ in self.singleThreadOnly:
            with AsyncController(_) as ac:
                q1a = Queue()
                q1b = Queue()
                def f1():
                    q1b.put(None)
                    q1a.get()
                em1 = Emitter()
                future1 = ac.start(em1.g, f1)
                q1b.get()
                self.assertEquals(future1.state, Future.STATE_RUNNING)

                future2 = ac.start(None, lambda: None)
                time.sleep(0.100)
                self.assertEquals(future2.state, Future.STATE_WAITING)
                with WaitForSignal(em1.bing, 1000):
                    future2.cancel()
                    q1a.put(None)
                self.assertEquals(future1.state, Future.STATE_FINISHED)
                time.sleep(0.1)
                self.assertEquals(future2.state, Future.STATE_CANCELED)

    # Verify that job status and cancelation works: cancel an in-progress job,
    # verifying that it does not emit a signal or invoke a callback when it
    # completes.
    def test_13(self):
        for _ in self.singleThreadOnly:
            with AsyncController(_) as ac:
                q1a = Queue()
                q1b = Queue()
                def f1():
                    q1b.put(None)
                    q1a.get()
                # Cancel future3 while it's running in the other thread.
                em1 = Emitter('should never be called', self.assertEquals)
                em1.bing.connect(self.fail)
                future1 = ac.start(em1.g, f1)
                q1b.get()
                self.assertEquals(future1.state, Future.STATE_RUNNING)
                future1.cancel(True)
                q1a.put(None)
                # If the result is discarded, it should never emit a signal or
                # invoke its callback, even if the task is already running. Wait
                # to make sure neither happened.
                time.sleep(0.1)

                # In addition, the signal from a finished task that is discarded
                # should not invoke the callback, even after the task has
                # finihsed and the sigal emitted.
                em2 = Emitter('should never be called', self.assertEquals)
                em2.bing.connect(self.fail)
                future2 = ac.start(em2.g, lambda: None)
                time.sleep(0.1)
                self.assertEquals(future2.state, Future.STATE_FINISHED)
                future2.cancel(True)

    # Test per-task priority.
    def test_14(self):
        for _ in self.poolAndThread:
            with AsyncController(_) as ac:
                def f(assertEquals, priority):
                    assertEquals(QThread.currentThread().priority(), priority)
                em = Emitter()
                ac.defaultPriority = QThread.LowPriority
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, self.assertEquals, QThread.LowestPriority,
                             _futurePriority=QThread.LowestPriority)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, self.assertEquals, QThread.LowPriority)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, self.assertEquals, QThread.HighestPriority,
                             _futurePriority=QThread.HighestPriority)

    # Test calling canel twice. Should not raise an exception.
    def test_15(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                future = ac._wrap(None, lambda: None)
                future.cancel(True)
                future.cancel(True)

if __name__ == '__main__':
    unittest.main()
