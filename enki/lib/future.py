# ****************************
# future.py - Futures for PyQt
# ****************************
# The idea: create a simple class that encapsulates a thread or thread pool and
# uses it to run a function asynchronously. For example, to run a function
# ``f(a, b)``, then invoke a callback g_ on the return value provided by
# f_:
#
# .. code:: Python
#    :number-lines:
#
#    ac = AsyncController('QThread', parent)
#    def g(future):
#      result = future.result
#      # ...code to process result, the returned tuple resulting from calling
#      # f...
#    ac.start(g, f, a, b)
#
# This is *almost* like:
#
# .. code:: Python
#    :number-lines:
#
#    result = f(a, b)
#    g(result)
#
# except that f_ is run in a separate thread and g_ isn't invoked until
# f_ completes.
#
# .. contents::
#
# Implementation
# ==============
# The AsyncController_ class first wraps a function to be executed along
# with the neceesary state in a Future_. Next, it schedules this Future_
# to be executed in another thread, then passes results from that invocation
# back to the thread in which the start_ method was called.
#
# To do
# =====
# - Make job cancellation change state after the current job completes,
#   instead of waiting until the cancelled job would have been run. This would
#   be easy using a custom event in a QThread_. Doing so in a QThreadPool is
#   probably harder, since we can't guarantee exclusive access to a Future.
#
# Imports
# =======
# Library imports
# ---------------
import sys
import time
import traceback
import gc
#
# Third-party imports
# -------------------
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import (QThread, pyqtSignal, QObject, QTimer, QRunnable,
                          QThreadPool, QEventLoop)
import sip
#
# Local imports
# -------------
# None.
#
# _AsyncAbstractController
# ========================
# This class provides a simpe user interface to start up a thread or thread
# pool, then submit jobs to it. This class **must** be shut down properly
# before application exit; see the cleanup_ section for details. It is an
# abstract class, relying on subclasses to implement the thread or thread pool.
#
# Implementation note: while using Python's `abc module
# <https://docs.python.org/3/library/abc.html>`_ would be nice, it can't be
# used here: I get the following error::
#
#    File "C:\Python27\lib\abc.py", line 87, in __new__
#      cls = super(ABCMeta, mcls).__new__(mcls, name, bases, namespace)
#  TypeError: Error when calling the metaclass bases
#      metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the meta
#  classes of all its bases
class _AsyncAbstractController(QObject):
    # Create a worker thread or thread pool.
    def __init__(self,
      # The _`parent` of this object, if it exists. Providing a parent guarantees
      # that this class instance will be properly finalized when the parent is
      # deleted. If parent is ``None``, then the terminate_ method **MUST** be
      # called before the program exits. See the cleanup_ section for more
      # information.
      parent=None):

        super().__init__(parent)
        self._isAlive = True

        # _`defaultPriority` defines the priority of the thread used to execute
        # f_, which must be a value taken from `QThread.Priority
        # <http://qt-project.org/doc/qt-5/qthread.html#Priority-enum>`_.
        # This default may be overriden in the kwargs_ parameter of start_.
        #
        # Implementation note: I would prefer to use
        # ``QThread.currentThread().priority()``, but this returns
        # ``QThread.InheritPriority`` during unit tests, which causes future
        # calls to ``setPriority`` to fail.
        self.defaultPriority = QThread.NormalPriority

        # Ask the parent_ for a signal before it's destroyed, so we can do
        # cleanup.
        if parent:
            parent.destroyed.connect(self.onParentDestroyed)


    # The _`start` method runs ``future.result = f(*args, **kwargs)`` in a
    # separate thread. When it completes, invoke ``g(future)``, if g_ is
    # provided. It returns a Future_ instance, which can be used to interact
    # with f_.
    def start(self,
      # The result function _`g` which takes one parameter, ``future``,
      # which will be executed in the thread *t* from which this method was
      # called, or ``None`` if no function should be invoked after f_
      # completes. **Important**: g_ will **not** be invoked if the thread
      # *t* does not provide an event loop -- such as a thread taken from
      # the thread pool. See qThreadOrThreadPool_ for more information.
      g,

      # The function _`f` which will be executed in a separate thread.
      # Any exceptions raised in f_ will be caught, then re-raised in
      # ``g(future)`` when accessing ``future.result``. **Very important**: The
      # parameters to f_ must be immutable, or must not change while f_ is
      # executing. The same is true of the value returned by f_.
      f,

      # _`args` defines the arguments used to invoke f_.
      *args,

      # _`kwargs` gives a dict of keyword arguments passed to f_. If the
      # keyword argument  ``_futurePriority`` is provided, this will determine
      # the priority of the thread used to execute f_. If no priority is
      # given, defaultPriority_ is used.
      **kwargs):

        assert self._isAlive
        # Wrap f_ and associated data in a Future_.
        future = self._wrap(g, f, *args, **kwargs)
        # Run it in another thread.
        self._start(future)
        return future

    # _`_start`: Given a Future_ instance, run it in another thread.
    def _start(self, future):
        raise RuntimeError('Abstact method')

    # Wrap f_ and g_ in a Future_ and return it.
    def _wrap(self, g, f, *args, **kwargs):
        # Wrap f_ and associated data in a Future_.
        return Future(g, f, args, kwargs, self.defaultPriority)
#
# Cleanup
# -------
# **Very important**: Before application exit, cleanup tasks in this class
# **MUST** be performed. Otherwise, the code will print error messages and
# probably crash. Options are:
#
# #. Use a context manager::
#
#      with _AsyncController(qThreadOrThreadPool):
#           ac.start(g, f, ...)
#
# #. Let Qt invoke cleanup by providing it a parent, thus including it in the
#    object tree. The sample code at the top of this file takes this approach.
#    As a backup to this approach, this class will also destroy itself when
#    the `QApplication <http://doc.qt.io/qt-5/qapplication.html>`_ is
#    destroyed.
#
# #. Finalize this instance if the Python finalizer is invoked. Python does
#    not guarantee that this will **ever** be invoked. Don't rely on it.
#
# #. Manually call terminate_ when necessary. This is soooo easy to forget.
#
# Context manager
# ^^^^^^^^^^^^^^^
    # Provide a `context manager <https://docs.python.org/3/library/stdtypes.html#typecontextmanager>`_
    # for Pythonic construction and cleanup.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()
        # Pass any exceptions through.
        return False
#
# Qt destructor
# ^^^^^^^^^^^^^
    # This is run when the parent of this object is destroyed. We're next, so
    # perform our termination actions.
    def onParentDestroyed(self):
        self.terminate()
#
# Python finalizer
# ^^^^^^^^^^^^^^^^
    # This might be run by Python. Or it might not. Don't rely on it.
    def __del__(self):
        self.terminate()
#
# Manual
# ^^^^^^
    # Without calling _`terminate` before the program exits, we get nasty
    # crashes since the Python portion of the class is still alive. At a
    # minimum, we see "QThread: Destroyed while thread is still running"
    # messages.
    #
    # This is NOT thread-safe.
    def terminate(self):
        # Only run this once.
        if self._isAlive:
            self._isAlive = False
            self._terminate()

            # Waiting for the thread or thread pool to shut down may have
            # placed completed jobs in this thread's queue. Process them now to
            # avoid any surprises (terminated `_AsyncAbstractController`_
            # instances still invoke callbacks, making it seem that the
            # terminate didn't fully terminate. It did, but still leaves g_
            # callbacks to be run in the event queue.)
            el = QEventLoop(self.parent())
            QTimer.singleShot(0, el.exit)
            el.exec_()

            # Delete the `QObject <http://doc.qt.io/qt-5/qobject.html>`_
            # underlying this class, which disconnects all signals.
            sip.delete(self)

    # _`_terminate` is called by terminate_ to actually shut down this class.
    def _terminate(self):
        raise RuntimeError('Abstact method')
#
# Concrete `_AsyncAbstractController`_ subclasses
# ===============================================
# These two subclasses inherit from `_AsyncAbstractController`_ and provide a
# thread or thread pool for use by the class.
#
# AsyncThreadController
# ---------------------
# Run functions in a QThread, using the `_AsyncAbstractController`_ framework.
class AsyncThreadController(_AsyncAbstractController):
    def __init__(self,
      # See parent_.
      parent=None):

        super().__init__(parent)
        # Create a worker and a thread it runs in. This approach was
        # inspired by the example given in the QThread_ docs.
        self._worker = _AsyncWorker()
        self._workerThread = QThread(self)
        # Attach the worker to the thread's event queue.
        self._worker.moveToThread(self._workerThread)
        # Hook up signals.
        self._worker.startSignal.connect(self._worker.onStart)
        # Everything is ready. Start the worker thread, so it will
        # be ready for functions to run.
        self._workerThread.start()

    # See `_start`_.
    def _start(self, future):
        self._worker.startSignal.emit(future)

    # See `_terminate`_.
    def _terminate(self):
        # Shut down the thread the worker runs in.
        self._workerThread.quit()
        self._workerThread.wait()
        # Delete the worker, since it doesn't have a parent and therefore
        # won't be deleted by the Qt object tree.
        sip.delete(self._worker)
        del self._worker
#
# AsyncPoolController
# -------------------
# Run functions in a `QThread <http://doc.qt.io/qt-5/qthread.html>`_, using the
# `_AsyncAbstractController`_ framework.
class AsyncPoolController(_AsyncAbstractController):
    def __init__(self,
      # A number *n* to create a pool of *n* simple threads, where each thread
      # lacks an event loop, so that it can emit but not receive signals.
      # This means that g_ may **not** be run in a thread of this pool,
      # without manually adding a event loop. If *n* < 1, the global thread
      # pool is used.
      maxThreadCount,

      # See parent_.
      parent=None):

        super().__init__(parent)
        if maxThreadCount < 1:
            self.threadPool = QThreadPool.globalInstance()
        else:
            self.threadPool = QThreadPool(self)
            self.threadPool.setMaxThreadCount(maxThreadCount)

    # See `_start`_.
    def _start(self, future):
        # Asynchronously invoke f_.
        apw = _AsyncPoolWorker(future)
        self.threadPool.start(apw)

    # See `_terminate`_.
    def _terminate(self):
        self.threadPool.waitForDone()
        del self.threadPool
#
# SyncController
# --------------
# For testing purposes, this controller simply runs all jobs given it in the
# current thread, using the `_AsyncAbstractController`_ framework.
class SyncController(_AsyncAbstractController):
    # See `_start`_.
    def _start(self, future):
        future._invoke()

    # See `_terminate`_.
    def _terminate(self):
        pass
#
# AsyncController
# ---------------
# This "class" provides a unified interface to both the thread and thread pool
# implementations.
def AsyncController(
  # The _`qThreadOrThreadPool` argument can take on several values:
  #
  # * 'QThread' to create a single QThread with an event loop, enabling it
  #   to both emit and receive signals -- meaning that g_ may be run
  #   in this created thread.
  # * A number *n* to create a pool of *n* simple threads, where each thread
  #   lacks an event loop, so that it can emit but not receive signals.
  #   This means that g_ may **not** be run in a thread, without
  #   manually adding a event loop. If *n* < 1, the global thread pool
  #   is used.
  # * 'Sync' to execute tasks in the current thread, rather than a separate
  #   thread. Primarily provided for test and debug purposes.
  qThreadOrThreadPool,

  # See parent_.
  parent=None):

    if qThreadOrThreadPool == 'Sync':
        return SyncController(parent)
    elif qThreadOrThreadPool == 'QThread':
        return AsyncThreadController(parent)
    else:
        return AsyncPoolController(qThreadOrThreadPool, parent)

# RunLatest
# ---------
# This class runs the latest (most recent) job submitted, discarding any jobs
# that have been submitted but not run.
class RunLatest(object):
    def __init__(self,
      # See qThreadOrThreadPool_.
      qThreadOrThreadPool,

      # If ``True``, discard the results of a currently-executing job when a new
      # job is submitted. If ``False``, report the results of the
      # currently-executing job when a new job is submitted.
      discardPending=False,

      # See parent_.
      parent=None):

        self.ac = AsyncController(qThreadOrThreadPool, parent)
        # Create a valid ``_future`` object, so that the first calls to
        # ``start`` can still operate on a valid instance of ``_future``.
        self.future = self.ac.start(None, lambda: None)
        self.discardPending = discardPending

    # See `_start`_.
    def start(self, *args, **kwargs):
        self.future.cancel(self.discardPending)
        self.future = self.ac.start(*args, **kwargs)
        return self.future

    def terminate(self):
        self.ac.terminate()
#
# Future
# ======
# The Future class holds all the information necessary to invoke f_
# and return its results to g_.
class Future(object):
    # The possible states for an instance of this class.
    (STATE_WAITING, STATE_RUNNING, STATE_FINISHED,
     STATE_CANCELED) = list(range(4))

    def __init__(self,
      # g_
      g,

      # f_
      f,

      # args_
      args,

      # kwargs_
      kwargs,

      # The thread priority to use if none is given in kwargs_ above.
      defaultPriority):

        # Look for the ``_futurePriority`` keyword argument and remove it if
        # found. See also defaultPriority_ and kwargs_.
        self._futurePriority = kwargs.pop('_futurePriority', defaultPriority)

        # State used to invoke f_ and g_.
        self._g = g
        self._f = f
        self._args = args
        self._kwargs = kwargs

        # State maintained by Future.
        self._state = self.STATE_WAITING
        self._signalInvoker = _SignalInvoker()
        self._requestCancel = False
        self._result = None
        self._exc_info = None
        self._exc_raised = False
        self._discardResult = False

        # Set up to invoke g_ in the current thread, if g_ was
        # provided.
        self._signalInvoker.doneSignal.connect(self._signalInvoker.onDoneSignal)

    # Invoke f_ and emit its returned value.
    def _invoke(self):
        if self._requestCancel:
            # Skip canceled callables.
            self._state = self.STATE_CANCELED
        else:
            # Run the function, catching any exceptions.
            self._state = self.STATE_RUNNING
            QThread.currentThread().setPriority(self._futurePriority)
            try:
                self._result = self._f(*self._args, **self._kwargs)
            except:
                # Save not just the exception, but also the traceback to provide
                # better debugging info when this is re-raised in the calling
                # thread.
                self._exc_info = sys.exc_info()


            self._state = self.STATE_FINISHED

        # Emit the doneSignal to invoke g_ optionally and to destroy
        # ``_signalInvoker``, even in the case of a canceled job.
        self._signalInvoker.doneSignal.emit(self)

    # The _`cancel` method may be called from any thread; it requests that the
    # execution of f_ be canceled. If f_ is already running, then it will not
    # be interrupted.
    def cancel(self,
      # If _`discardResult` is ``True``, then the results returned from
      # evaluating f_ will be discarded, instead of invoking g_ [#]_. Any
      # exceptions which occurred in f_ will still be raised.
      #
      # .. [#]  Note that this is only guaranteed to work when cancel_ is
      #         invoked from the thread which started the job.
      discardResult=False):

        self._requestCancel = True
        self._discardResult = discardResult

    # Return the result produced by invoking f_, or raise any exception which
    # occurred in f_.
    @property
    def result(self):
        if self._exc_info:
            # Note that the exception was raised.
            self._exc_raised = True

            # Raise an exception which provides a traceback all the way into
            # the line in f_ that caused the exception. Just re-raising the
            # exception doesn't preserve the full traceback. Likewise, ``raise
            # self._exc_info`` provides only a limited tracebacak.
            #
            # Quoting from `sys.exc_info() <https://docs.python.org/3/library/sys.html#sys.exc_info>`_,
            # "*value* gets the exception instance (an instance of the
            # exception type)."
            type_, value, traceback = self._exc_info
            # Re-`raise <https://docs.python.org/3/reference/simple_stmts.html#raise>`_
            # the caught exception.
            raise value.with_traceback(traceback)
        else:
            return self._result

    # Make ``state`` a read-only property. It reflects the status of the
    # callable it wraps.
    @property
    def state(self):
        return self._state
#
# _SignalInvoker
# --------------
# A helper class to hold a signal and invoke g_. This can't be easily
# incorporated into Future_ for several reasons:
#
# #. If Future_ is a subclass of QObject_, then its lifetime must be carefully
#    managed to insure that it is deleted before the QApplication_. This is
#    difficult, since every invocation of start_ produces a new object which
#    must be tracked.
# #. If the signal is declared in Future_, then the it must accept an
#    ``object`` instead of a Future_, since Future_ isn't defined yet.
#    Awkward, but not a show-stopper.
class _SignalInvoker(QObject):
    # Emitted to invoke g_.
    doneSignal = pyqtSignal(Future)

    # A method to invoke g_.
    def onDoneSignal(self, future):
        try:
            # Invoke g_ if it was provided and should be invoked.
            if (future._g and not future._discardResult and
                future.state == future.STATE_FINISHED):
                future._g(future)
            # If an exception occurred while executing f_ and that exception
            # wasn't raised, do so now.
            if future._exc_info and not future._exc_raised:
                future.result
        finally:
            # Make sure to manually delete this object, because it has no
            # parent, meaning the Qt object tree won't automaticlly delete it.
            self.deleteLater()
#
# Thread / thread pool worker classes
# ===================================
# Neither the `_AsyncWorker`_ class nor the `_AsyncPoolWorker`_ class should
# be instianted by a user of this module; instead, these are used by
# ``AsyncXxxController`` to run a function in a separate thread.
#
# _AsyncPoolWorker
# ----------------
class _AsyncPoolWorker(QRunnable):
    def __init__(self,
      # The Future_ instance which contains the callable to invoke.
      future):

        super().__init__()
        self._future = future

    # This is invoked by a thread from the thread pool.
    def run(self):
        self._future._invoke()
#
# _AsyncWorker
# ------------
class _AsyncWorker(QObject):
    # This signal contains the information necessary to run a callable.
    startSignal = pyqtSignal(Future)

    # The start signal is connected to this slot. It runs f_ in the worker
    # thread.
    def onStart(self,
      # The Future_ instance which contains the callable to invoke.
      future):

        future._invoke()
#
# Demo code
# =========
# TimePrinter
# -----------
# Print the time and status of a set of tasks, to see how the threads operate.
class TimePrinter(object):
    def __init__(self,
      # A sequence of tasks to monitor.
      tasks,
      # QApplication_ instance, used as a parent for a `QTimer <http://doc.qt.io/qt-5/qtimer.html>`_.
      app):

        self.tasks = tasks

        # Current time, in seconds.
        self.time_sec = 0.0

        # Time between prints, in seconds.
        self.interval_sec = 0.1

        # Create a timer to continually print the time.
        self.qt = QTimer(app)
        self.qt.timeout.connect(self.printTime)
        self.qt.start(self.interval_sec*1000)

        # Print them now, to show the initial state.
        self.printTime()

    # Print the time.
    def printTime(self):
        sys.stdout.write('{} seconds: task states are '.format(self.time_sec))
        for task in self.tasks:
            sys.stdout.write('{}'.format(task.state))
        sys.stdout.write('.\n')
        self.time_sec += self.interval_sec
#
# checkLeaks
# ----------
# Look for any Qt objets that aren't destroyed.
def checkLeaks():
    gc.collect()

    notDestroyedCount = 0
    for o in gc.get_objects():
        try:
            if not sip.isdeleted(o):
                sip.dump(o)
                notDestroyedCount += 1
        except TypeError:
            pass
    if notDestroyedCount:
        print("\n\n{}\nFound {} objects that weren't deleted.".format('*'*80,
          notDestroyedCount))
#
# main
# ----
def main():
    try:
        demo()
    finally:
        checkLeaks()
#
# demo
# ----
def demo():
    # Create a Qt application.
    app = QApplication(sys.argv)

    # Make sure it's properly destroyed.
    try:

        # Catch exceptions when the Qt event loop runs, so that the program
        # won't immediately exit.
        sys.excepthook = traceback.print_exception

        # Define a function ``foo`` to run aysnchronously, calling ``foo_done`` when
        # it completes.
        def foo(a, b):
            print('Foo {} {} in thread {}'.format(a, b, QThread.currentThread()))
            if a == 3:
                # As a test, raise an exception. See if a useful traceback is
                # printed.
                asdf
            time.sleep(0.3)
            return a + 0.1

        def foo_done(future):
            print('Done {}'.format(future.result))

        # Run ``foo`` using a single thread (``'QThread'``) or a pool of 2 threads
        # (``2``). Give it ``app`` as the parent so that when Qt destroys ``app``,
        # it will also destroy this class.
        ac = AsyncController(2, app)
        #ac = AsyncController('QThread', app)
        task1 = ac.start(foo_done, foo, 1, b=' 2')
        task2 = ac.start(foo_done, foo, 3, b=' 4')
        task3 = ac.start(foo_done, foo, 5, b=' 6')
        task4 = ac.start(foo_done, foo, 7, b=' 8')

        # Print the time and thread status. Note the ``tp =`` is necessary;
        # otherwise, the TimePrinter_ object will be deleted immediately!
        tp = TimePrinter((task1, task2, task3, task4), app)

        # Exit the program shortly after the event loop starts up.
        QTimer.singleShot(1800, app.exit)

        # Cancel one of the tasks.
        QTimer.singleShot(200, task4.cancel)

        # Run the main event loop.
        ret = app.exec_()

    finally:
        ac.terminate()
        sip.delete(app)
        del app

    sys.exit(ret)

if __name__ == '__main__':
    main()
