# .. -*- coding: utf-8 -*-
#
# ****************************
# future.py - Futures for PyQt
# ****************************
# The idea: create a simple class that encapsulates a thread or thread pool and
# uses it to run a function asynchronously. For example, to run a function
# ``f(a, b)``, then invoke a callback ``g`` with the return value provided by
# ``f`` stored in a class::
#
#   app = QApplication(sys.argv)
#   ac = AsyncController('QThread', app)
#   def g(future):
#     result = future.result
#     ...code to process result, the returned tuple resulting from calling ``f``...
#   ac.start(g, f, a, b)
#
# This is *almost* like::
#
#   result = f(a, b)
#   g(result)
#
# except that ``f`` is run in a separate thread and ``g`` isn't invoked until
# ``f`` completes.
#
# .. contents::
#
# Implementation
# ==============
# The ``AsyncController`` class first wraps a function to be executed along
# with the neceesary state in a ``Future`` class. Next, it schedules this
# class to be executed by the ``_AsyncWorker`` in a thread it creates or in the
# ``_AsyncPoolWorker`` pool it uses, then passes results from that invocation
# back to the thread in which the ``asyncController.start()`` method was called.
#
# Priority
# --------
# The priority of the thread used to execute ``f`` is
# ``AsyncController.defaultPriority``, unless this value is overriden by
# supplying the keyword argument ``futurePriority =``
# `QThread.Priority <http://qt-project.org/doc/qt-4.8/qthread.html#Priority-enum>`_
# when invoking ``start``.
#
# To do
# =====
# - Make job cancellation change state after the current job completes,
#   instead of waiting until the cancelled job would have been run.
# - Provide a "shut down and discard all" option?
# - Allow management of user-supplied QThreads/QThreadPools? If so, for a
#   QThread, should this class finalize (quit/wait) or not? That is, should
#   this class "own" the QThread?
#
# Imports
# =======
# Library imports
# ---------------
import sys, time
#
# Third-party imports
# -------------------
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QThread, pyqtSignal, QObject, QTimer, QRunnable, \
  QThreadPool, pyqtSlot
#
# Local imports
# -------------
# None.
#
# AsyncAbstractController
# =======================
# This class provides a simpe user interface to start up a thread or thread
# pool, then submit jobs to it. This class **must** be shut down properly
# before application exit; see the cleanup_ section for details. It is an
# abstract class, relying on subclasses to implement the thread or thrad pool.
#
# Implementation note: which using Python's `abc module
# <https://docs.python.org/2/library/abc.html>`_ would be nice, it can't be used
# here: I get the following error::
#
#    File "C:\Python27\lib\abc.py", line 87, in __new__
#      cls = super(ABCMeta, mcls).__new__(mcls, name, bases, namespace)
#  TypeError: Error when calling the metaclass bases
#      metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the meta
#  classes of all its bases
class AsyncAbstractController(QObject):
    # Create a worker thread or thread pool.
    def __init__(self,
      # .. |parent| replace:: The parent of this object, if it exists. Selecting an object as
      #    a parent guarantees that this class instance will be properly
      #    finalized when the parent is deleted. If parent is None, then the
      #    ``terminate()`` method **MUST** be called before the program exits.
      #    See the cleanup_ section below for more information.
      #
      # |parent|
      parent=None):

        super(AsyncAbstractController, self).__init__(parent)
        self.isAlive = True

        # I would prefer to use QThread.currentThread().priority(), but this
        # returns QThread.InheritPriority during unit tests, which causes future
        # calls to setPriority to fail.
        self.defaultPriority = QThread.NormalPriority

        # Ask the parent and QApplication for a signal before they're
        # destroyed, so we can do cleanup.
        if parent:
            parent.destroyed.connect(self.onParentDestroyed)
        QApplication.instance().destroyed.connect(self.onParentDestroyed)


    # Run ``future.result = f(*args, **kwargs)`` in a separate thread. When it
    # completes, invoke ``g(future)``, if ``g`` is provided. Returns a ``Future``
    # instance, which can be used to interact with ``f``.
    #
    def start(self,
      # .. |g| replace:: A result function which take one parameter, ``future``,
      #    which will be executed in the thread *t* from which this method was
      #    called, or None if no function should be invoked after ``f``
      #    completes. **Important**: ``g`` will **not** be invoked if the thread
      #    *t* does not provide an event loop -- such as a thread taken from
      #    the thread pool. See the AsycController constructor's
      #    ``qThreadOrThreadPool`` parameter for more information.
      #
      # |g|
      g,

      # .. |f| replace:: A function which will be executed in a separate thread.
      #    Any exceptions raised in ``f`` will be caught, then re-raised in
      #    ``g(future)`` when accessing ``future.result``.
      #    **Very important**: The parameters to ``f`` must be immutable, or must
      #    not change while ``f`` is executing. The same is true of the value
      #    returned by ``f``.
      #
      # |f|
      f,

      # .. |args| replace:: Arguments used to invoke ``f``.
      #
      # |args|
      *args,

      # .. |kwargs| replace:: A dict of keyword arguments passed to ``f``. If
      #    the keyword argument ``_futurePriority`` is provided, this will
      #    determine the priority of the thread used to execute ``f``. If no
      #    priority is given, AsyncController.defaultPriority is used; set this
      #    if desired.
      #
      # |kwargs|
      **kwargs):

        # Wrap ``f`` and associated data in a Future.
        future = self._wrap(g, f, *args, **kwargs)
        # Run it in another thread.
        self._start(future)
        return future

    # .. |_start| replace:: Given a Future instance, run it in another thread.
    #
    # |_start|
    def _start(self, future):
        raise RuntimeError('Abstact method')

    # Wrap ``f`` and ``g`` in a Future and return it. This and the following
    # method are used to do testing.
    def _wrap(self, g, f, *args, **kwargs):
        # Wrap ``f`` and associated data in a class.
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
#      with AsyncController(qThreadOrThreadPool):
#           ac.start(g, f, ...)
#           ...do more work...
#
# #. Let Qt invoke cleanup by providing it a parent, thus including it in the
#    object tree. The sample code at the top of thie file takes this approach.
#    As a backup to this approach, this class will also destroy itself when
#    the QApplication is destroyed.
#
# #. Finalize this instance if the Python destructor is invoked. Python does
#    not guarantee that this will **ever** be invoked. Don't rely on it.
#
# #. Manually call ``asyncController.terminate()`` when necessary. This is soooo
#    easy to forget.
#
# Context manager
# ^^^^^^^^^^^^^^^
    # Provide a `context manager <https://docs.python.org/2/library/stdtypes.html#typecontextmanager>`_
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
    # This is run shortly before this class's C++ destructor is invoked. It
    # emulates a C++ destructor by freeing resources before the C++ class is
    # destroyed.
    @pyqtSlot()
    def onParentDestroyed(self):
        self.terminate()
#
# Python destructor
# ^^^^^^^^^^^^^^^^^
    # In case the above method wasn't called, try to exit gracefully here.
    def __del__(self):
        self.terminate()
#
# Manual
# ^^^^^^
    # Without calling this before the program exits, we get nasty crashes since
    # the Python portion of the class is still alive. At a minimum, we see
    # "QThread: Destroyed while thread is still running" messages.
    #
    # This is NOT thread-safe.
    def terminate(self):
        # Only run this once.
        if self.isAlive:
            self.isAlive = False
            self._terminate()

    # .. |terminate| replace:: Called by ``terminate`` to actually shut down this class.
    #
    # |terminate|
    def _terminate(self):
        raise RuntimeError('Abstact method')


# Concrete AsyncAbstractController subclasses
# ===========================================
# These two subclasses inherit from AsyncAbstractController and prove a thread
# or thread pool for use by the class.
#
# AsyncThreadController
# ---------------------
# Run functions in a QThread, using the ``AsyncAbstractController`` framework.
class AsyncThreadController(AsyncAbstractController):
    def __init__(self,
      # |parent|
      parent=None):

        super(AsyncThreadController, self).__init__(parent)
        # Create a worker and a thread it runs in. This approach was
        # inspired by  example given in the `QThread docs
        # <http://qt-project.org/doc/qt-4.8/qthread.html>`_.
        self._worker = _AsyncWorker()
        self._workerThread = QThread(parent)
        # Attach the worker to the thread's event queue.
        self._worker.moveToThread(self._workerThread)
        # Hook up signals.
        self._worker.startSignal.connect(self._worker.onStart)
        # Everything is ready. Start the worker thread, so it will
        # be ready for functions to run.
        self._workerThread.start()

    # |_start|
    def _start(self, future):
        self._worker.startSignal.emit(future)

    # |terminate|
    def _terminate(self):
        # Shut down the thread the Worker runs in.
        self._workerThread.quit()
        self._workerThread.wait()
        # Finally, detach (and probably garbage collect) the objects
        # used by this class.
        del self._worker
        del self._workerThread
#
# AsyncPoolController
# -------------------
# Run functions in a QThread, using the ``AsyncAbstractController`` framework.
class AsyncPoolController(AsyncAbstractController):
    def __init__(self,
      # A number *n* to create a pool of *n* simple threads, where each thread
      # lacks an event loop, so that it can emit but not receive signals.
      # This means that ``g`` may **not** be run in a thread of this pool,
      # without manually adding a event loop. If *n* < 1, the global thread pool
      # is used.
      maxThreadCount,

      # |parent|
      parent=None):

        super(AsyncPoolController, self).__init__(parent)
        if maxThreadCount < 1:
            self.threadPool = QThreadPool.globalInstance()
        else:
            self.threadPool = QThreadPool()
            self.threadPool.setMaxThreadCount(maxThreadCount)

    # |_start|
    def _start(self, future):
        # Asynchronously invoke ``f``.
        apw = _AsyncPoolWorker(future)
        self.threadPool.start(apw)

    # |terminate|
    def _terminate(self):
        self.threadPool.waitForDone()
        del self.threadPool
#
# SyncController
# --------------
# For testing purposes, this controller simply runs all jobs given it in the
# current thread, using the ``AsyncAbstractController`` framework.
class SyncController(AsyncAbstractController):
    # |_start|
    def _start(self, future):
        future._invoke()

    # |terminate|
    def _terminate(self):
        pass
#
# AsyncController
# ---------------
# This "class" provides a unified interface to both the thread and thread pool
# implementations.
def AsyncController(
  # * 'QThread' to create a single QThread with an event loop, enabling it
  #   to both emit and receive signals -- meaning that ``g`` may be run
  #   in this created thread.
  # * A number *n* to create a pool of *n* simple threads, where each thread
  #   lacks an event loop, so that it can emit but not receive signals.
  #   This means that ``g`` may **not** be run in a thread, without
  #   manually adding a event loop. If *n* < 1, the global thread pool
  #   is used.
  # * 'Sync' to execute tasks in the current thread, rather than a separate
  #   thread. Primarily provided to test and debug purposes.
  qThreadOrThreadPool, parent=None):

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
      # See AsyncController_'s ``qThreadOrThreadPool`` argument.
      qThreadOrThreadPool,
      parent=None):

        self.ac = AsyncController(qThreadOrThreadPool, parent)
        # Create a valid ``_future`` object, so that the first calls to
        # ``start`` can still operate on a valid instance of ``_future``.
        self._future = self.ac.start(None, lambda: None)

    def start(self, *args, **kwargs):
        self._future.cancel()
        self._future = self.ac.start(*args, **kwargs)
        return self._future

    def terminate(self):
        self.ac.terminate()
#
# Future
# ======
# The Future class holds all the information necessary to invoke ``f``
# and return its results to ``g``.
class Future(object):
    # The possible states for an instance of this class.
    STATE_WAITING, STATE_RUNNING, STATE_FINISHED, STATE_CANCELED = range(4)

    def __init__(self,
      # |g|
      g,

      # |f|
      f,

      # |args|
      args,

      # |kwargs|
      kwargs,

      # The thread priority to use if none is given in ``kwargs`` above.
      defaultPriority):

        # Look for the ``_futurePriority`` keyword argument and remove it if
        # found.
        self._futurePriority = kwargs.pop('_futurePriority', defaultPriority)

        self._g = g
        self._f = f
        self._args = args
        self._kwargs = kwargs

        # State maintained by Future.
        self._state = self.STATE_WAITING
        self.signalInvoker = SignalInvoker()
        self._requestCancel = False
        self._result = None
        self._exc_info = None
        self._exc_raised = False

        # Set up to invoke ``g`` in the current thread, if ``g`` was
        # provided.
        self.signalInvoker.doneSignal.connect(self.signalInvoker.onDoneSignal)

    # Invoke ``f`` and emit its returned value.
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

            # Report the results.
            self._state = self.STATE_FINISHED
            self.signalInvoker.doneSignal.emit(self)

    # This method may be called from any thread; it requests that the execution
    # of ``f`` be canceled. If ``f`` is already running, then it will not be
    # interrupted, nor will it be canceled.
    def cancel(self):
        self._requestCancel = True

    # Return the result produced by invoking ``f``, or raise any exception which
    # occurred in ``f``.
    @property
    def result(self):
        if self._exc_info:
            # Note that the exception was raised.
            self._exc_raised = True
            # Raise an exception which provides a trackback all the way into the
            # line in ``f`` that caused the exception. Just re-raising the
            # exception doesn't preserve the full traceback. Likewise, ``raise
            # self._exc_info`` provides only a limited tracebacak.
            #
            # The mapping: One form of `raise
            # <https://docs.python.org/2/reference/simple_stmts.html#raise>`_
            # expects ``instance, None, traceback``. `sys.exc_info()
            # <https://docs.python.org/2/library/sys.html#sys.exc_info>`_
            # produces ``type, value, traceback`` where type is the exception
            # type of the exception being handled, value is a class instance,
            # and traceback is the desired trackback to report.
            raise self._exc_info[1], None, self._exc_info[2]
        else:
            return self._result

    # Make ``state`` a read-only property. It reflects the status of the
    # callable it wraps.
    @property
    def state(self):
        return self._state

# A helper class to hold a signal and invoke ``g``. This can't be easily
# incorporated into ``Future`` for several reasons:
#
# #. A Future needs to remember the thread in which to run the result function
#    ``g``. If it contains a signal, then it moveToThread should be called to
#    first move it to the worker thread, then back to the thread from which it
#    was invoked before emitting ``g``. This is awkward and I can't get it to
#    work. What seems better: use SignalInvoker as an anchor, connecting it to
#    the thread used to invoke ``g``, and leaving it there.
# #. Any class inheriting from QObject, crossing threads, and without a parent
#    gets destroyed by Qt. This is exactly the case Future needs to use if it
#    contains a signal. See emit_refs.py for sample code that demonstrates this
#    crash and workarounds.
# #. If the signal is declared in ``Future``, then the it must accept an
#    ``object`` instead of a ``Future``, sine ``Future`` isn't defined yet.
#    Awkward, but not a show-stopper.
class SignalInvoker(QObject):
    # Emitted to invoke ``g``.
    doneSignal = pyqtSignal(Future)

    # A method to invoke ``future.g``.
    @pyqtSlot(Future)
    def onDoneSignal(self, future):
        # Invoke ``g`` if it was provided.
        if future._g:
            future._g(future)
        # If an exception occurred while executing ``f`` and that exception
        # wasn't raised, do so now.
        if future._exc_info and not future._exc_raised:
            future.result
#
# Thread / thread pool worker classes
# -----------------------------------
# Neither the ``_AsyncWorker`` class nor the ``AsyncPoolWorker`` class should
# be instianted by a user of this module; instead, these are used by
# ``AsyncXxxController`` to run a function in a separate thread.
class _AsyncPoolWorker(QRunnable):
    def __init__(self,
      # The Future instance which contains the callable to invoke.
      future):

        super(_AsyncPoolWorker, self).__init__()
        self._future = future

    # This is invoked by a thread from the thread pool.
    def run(self):
        self._future._invoke()

class _AsyncWorker(QObject):
    # This signal contains the information necessary to run a callable.
    startSignal = pyqtSignal(Future)

    # The start signal is connected to this slot. It runs ``f`` in the worker
    # thread.
    @pyqtSlot(Future)
    def onStart(self,
      # The Future instance which contains the callable to invoke.
      future):

        future._invoke()
#
# Demo code
# =========
# Print the time and status of a set of tasks, to see how the threads operate.
class TimePrinter(object):
    def __init__(self,
      # A sequence of tasks to monitor.
      tasks,
      # QApplication instance, used as a parent for a Qtimer
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

    # Print the time.
    @pyqtSlot()
    def printTime(self):
        sys.stdout.write('{} seconds: task states are '.format(self.time_sec))
        for task in self.tasks:
            sys.stdout.write('{}'.format(task.state))
        sys.stdout.write('.\n')
        self.time_sec += self.interval_sec
        self.tasks[3].cancel()

def main():
    # Create an application.
    app = QApplication(sys.argv)

    # Define a function ``foo`` to run aysnchronously, calling ``foo_done`` when
    # it completes.
    def foo(a, b):
        print('Foo ' + str(a) + str(b) + ' in thread ' + str(QThread.currentThread()))
        if a == 3:
            # As a test, raise an exception. See if a useful traceback is
            # printed.
            asdf
        time.sleep(0.3)
        return a + 0.1
    def foo_done(future):
        print('Done ' + str(future.result))

    # Run foo using a single thread ('QThread') or a pool of threads (0). Give
    # it ``app`` as the parent so that when Qt destroys ``app``, it will also
    # destroy this class.
    ac = AsyncController(0, app) # ac = AsyncController('QThread', app)
    task1 = ac.start(foo_done, foo, 1, b=' 2')
    task2 = ac.start(foo_done, foo, 3, b=' 4')
    task3 = ac.start(foo_done, foo, 5, b=' 6')
    task4 = ac.start(foo_done, foo, 7, b=' 8')

    # Print the time and thread status.
    tp = TimePrinter((task1, task2, task3, task4), app)

    # Exit the program shortly after the event loop starts up.
    QTimer.singleShot(800, app.exit)

    # Run the main event loop.
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
