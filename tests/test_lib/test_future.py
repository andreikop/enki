#!/usr/bin/env python3
# .. -*- coding: utf-8 -*-
#
# *****************************************
# future_test.py - Unit tests for future.py
# *****************************************
# Imports
# =======
import time
import sys
import os.path
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                ".."))
from base import WaitForSignal
#
# Library imports
# ---------------
from queue import Queue
import unittest
#
# Third-party imports
# -------------------
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, QEventLoop, QThread
from PyQt5.QtTest import QTest
#
# Local imports
# -------------
from enki.lib.future import AsyncController, Future, RunLatest
#
# Test helpers
# ============
# A helper class to signal when its method function is executed.
class Emitter(QObject):
    bing = pyqtSignal()

    def __init__(self, expected=None, assertEqual=None):
        QObject.__init__(self)
        self.expected = expected
        self.assertEqual = assertEqual

    def g(self, future):
        self.thread = QThread.currentThread()
        # Always bing, even if there's an exception.
        try:
            # Retrieve the result, even if it won't be checked, to make sure
            # that no exceptions were raised.
            self.result = future.result
            if self.expected:
                self.assertEqual(self.expected, self.result)
        except:
            raise
        finally:
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
                # gotHere must be a list in order to f to change it in a way
                # that is visible outside of f.
                gotHere = [False]
                def f():
                    gotHere[0] = True
                future = ac._wrap(None, f)
                with WaitForSignal(future._signalInvoker.doneSignal, 1000):
                    ac._start(future)
                self.assertTrue(gotHere[0])

    # Verify that the result function is run.
    def test_2(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                em = Emitter(2, self.assertEqual)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, lambda: 2)

    # Verify that a result from f is passed to g.
    def test_3(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                em = Emitter(123, self.assertEqual)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, lambda x: x + 2, 121)

    # Verify that correct arguments are passed to f.
    def test_4(self):
        for _ in self.syncPoolAndThread:
            with AsyncController(_) as ac:
                def f(a, b, c=2, d=4):
                    self.assertEqual(a, 2)
                    self.assertEqual(b, 3)
                    self.assertEqual(c, 4)
                    self.assertEqual(d, 5)
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
            self.assertEqual(len(s), 3)

    # Verify that the correct functions and callbacks get executed.
    def test_7(self):
        for _ in ('Sync', 'QThread'):
            with AsyncController(_) as ac:
                em1 = Emitter(15, self.assertEqual)
                em2 = Emitter(16, self.assertEqual)
                em3 = Emitter(17, self.assertEqual)
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
                ac.start(em1.g, lambda: q1.get())
                ac.start(em2.g, lambda: q2.get())
                ac.start(em3.g, lambda: q3.get())
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
        for _ in self.poolAndThread:
            with AsyncController(_) as ac:
                def f():
                    raise TypeError
                em = Emitter()
                # Fun with exceptions: if an exception is raised while handling
                # a signal, it doesn't show up with normal try/catch semantics.
                # Instead, ``sys.excepthook`` must be overridden to see it.
                # ``WaitForSignal`` does this in ``__exit__``, so use it for the
                # convenience. Put another way, removing ``WaitForSignal`` and
                # adding a time.sleep(1.0) produces test failures, since the
                # exceptions raised are not caught by standard Python mechanisms
                # (here, ``self.assertRaises``).
                #
                # **However**, ``WaitForSignal`` doesn't do this in the body of
                # the ``with`` statement, so 'Sync' raises an exception but this
                # is discarded. For simplicity, skip this test case for now.
                with self.assertRaises(TypeError), WaitForSignal(em.bing, 1000,
                  printExcTraceback=False):
                    ac.start(em.g, f)

                # Make sure that the exception is still raised even if g doesn't
                # check for it.
                with self.assertRaises(TypeError), WaitForSignal(em.bing, 1000,
                  printExcTraceback=False):
                    ac.start(lambda result: None, f)

                # Make sure that the exception is still raised even there is no
                # g to check for it.
                with self.assertRaises(TypeError), WaitForSignal(em.bing, 1000,
                  printExcTraceback=False):
                    ac.start(None, f)

    # Verify that if ``f`` is launched in a thread, ``g`` will be run in that
    # same thread.
    def test_10(self):
        with AsyncController('QThread') as ac:
            em1 = Emitter()
            def f1():
                ac.start(em1.g, lambda: QThread.currentThread())
            with WaitForSignal(em1.bing, 1000):
                ac.start(None, f1)
            self.assertEqual(em1.thread, em1.result)

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
                future._signalInvoker.doneSignal.connect(qe.exit)
                qe.exec_()
            with WaitForSignal(em2.bing, 1000):
                ac.start(None, f2)
            self.assertEqual(em2.thread, em2.result)

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
                self.assertEqual(future1.state, Future.STATE_RUNNING)

                future2 = ac.start(None, lambda: None)
                QTest.qWait(100)
                self.assertEquals(future2.state, Future.STATE_WAITING)
                with WaitForSignal(em1.bing, 1000):
                    future2.cancel()
                    q1a.put(None)
                self.assertEquals(future1.state, Future.STATE_FINISHED)
                QTest.qWait(100)
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
                em1 = Emitter('em1 should never be called by {}'.format(_),
                              self.assertEquals)
                em1.bing.connect(self.fail)
                future1 = ac.start(em1.g, f1)
                q1b.get()
                self.assertEqual(future1.state, Future.STATE_RUNNING)
                future1.cancel(True)
                q1a.put(None)
                # If the result is discarded, it should never emit a signal or
                # invoke its callback, even if the task is already running. Wait
                # to make sure neither happened.
                QTest.qWait(100)

                # In addition, the signal from a finished task that is discarded
                # should not invoke the callback, even after the task has
                # finihsed and the sigal emitted.
                em2 = Emitter('em2 should never be called be {}'.format(_),
                              self.assertEquals)
                em2.bing.connect(self.fail)
                future2 = ac.start(em2.g, lambda: None)
                # Don't use qWait here, since it will process messages, which
                # causes em2.g to be invoked.
                time.sleep(0.1)
                self.assertEquals(future2.state, Future.STATE_FINISHED)
                future2.cancel(True)    # Test per-task priority.
                # Wait, in case a pending signal will invoke em2.g.
                QTest.qWait(100)

    def test_14(self):
        for _ in self.poolAndThread:
            with AsyncController(_) as ac:
                def f(assertEqual, priority):
                    assertEqual(QThread.currentThread().priority(), priority)
                em = Emitter()
                ac.defaultPriority = QThread.LowPriority
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, self.assertEqual, QThread.LowestPriority,
                             _futurePriority=QThread.LowestPriority)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, self.assertEqual, QThread.LowPriority)
                with WaitForSignal(em.bing, 1000):
                    ac.start(em.g, f, self.assertEqual, QThread.HighestPriority,
                             _futurePriority=QThread.HighestPriority)

    # Test the RunLatest class: do older jobs get canceled?
    def test_15(self):
        for _ in self.singleThreadOnly:
            rl = RunLatest(_)

            # Start a job, keeping it running.
            q1a = Queue()
            q1b = Queue()
            def f1():
                q1b.put(None)
                q1a.get()
            em1 = Emitter()
            future1 = rl.start(em1.g, f1)
            q1b.get()
            self.assertEquals(future1.state, Future.STATE_RUNNING)

            # Start two more. The first should not run; if it does, it raises
            # an exception.
            def f2():
                raise TypeError
            rl.start(None, f2)
            em3 = Emitter()
            rl.start(em3.g, lambda: None)

            with WaitForSignal(em3.bing, 1000):
                q1a.put(None)

            rl.terminate()

    # Test the RunLatest class: do older completed jobs get canceled?
    def test_16(self):
        for _ in self.singleThreadOnly:
            rl = RunLatest(_, True)

            # Start a job.
            q1a = Queue()
            q1b = Queue()
            def f1():
                q1b.put(None)
                q1a.get()
            em1 = Emitter('em1 should never be called by {}'.format(_),
                              self.assertEquals)
            future1 = rl.start(em1.g, f1)
            q1b.get()
            self.assertEquals(future1.state, Future.STATE_RUNNING)

            # Start another job, canceling the previous job while it's running.
            em2 = Emitter()
            rl.start(em2.g, lambda: None)
            with WaitForSignal(em2.bing, 1000):
                q1a.put(None)

            rl.terminate()

if __name__ == '__main__':
    unittest.main()
