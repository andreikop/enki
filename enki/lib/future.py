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
# To do
# =====
# - Make job cancellation change state after the current job completes,
#   instead of waiting until the cancelled job would have been run.
# - Provide a "shut down and discard all" option?
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
    QThreadPool
#
# Local imports
# -------------
# None.
#
# Implementation
# ==============
# The ``AsyncController`` class first wraps a function to be executed along
# with the neceesary state in a ``Future`` class. Next, it schedules this
# class to be executed by the ``_AsyncWorker`` in a thread it creates or in the
# ``_AsyncPoolWorker`` pool it uses, then passes results from that invocation
# back to the thread in which the ``asyncController.start()`` method was called.
#
# AsyncController
# ---------------
# This class provides a simpe user interface to start up a thread or thread
# pool, then submit jobs to it. This class **must** be shut down properly
# before application exit; see the cleanup_ section for details.
class AsyncController(QObject):
    # Create a worker thread or thread pool.
    def __init__(self,
      # * 'QThread' to create a single QThread with an event loop, enabling it
      #   to both emit and receive signals -- meaning that ``g`` may be run
      #   in this created thread.
      # * A number *n* to create a pool of *n* simple threads, where each thread
      #   lacks an event loop, so that it can emit but not receive signals.
      #   This means that ``g`` may **not** be run in a thread, without
      #   manually adding a event loop. If *n* < 1, the global thread pool
      #   is used.
      qThreadOrThreadPool,

      # The parent of this object, if it exists. Selecting an object as
      # a parent guarantees that this class instance will be properly
      # finalized when the parent is deleted. If parent is None, then the
      # ``del_()`` method **MUST** be called before the program exits.
      # See the cleanup_ section below for more information.
      parent=None):

        QObject.__init__(self, parent)
        self.isAlive = True

        # Ask the parent and QApplication for a signal before they're
        # destroyed, so we can do cleanup.
        if parent:
            parent.destroyed.connect(self.onParentDestroyed)
        QApplication.instance().destroyed.connect(self.onParentDestroyed)

        # Create either a thread pool or a thread.
        self._usePool = qThreadOrThreadPool != 'QThread'
        if self._usePool:
            if qThreadOrThreadPool < 1:
                self._threadPool = QThreadPool.globalInstance()
            else:
                self._threadPool = QThreadPool()
                self._threadPool.setMaxThreadCount(qThreadOrThreadPool)
        else:
            # Create a worker and a thread it runs in. This approach was
            # inspired by  example given in the `QThread docs
            # <http://qt-project.org/doc/qt-4.8/qthread.html>`_.

            self._worker = _AsyncWorker()
            self._workerThread = QThread()
            # Attach the worker to the thread's event queue.
            self._worker.moveToThread(self._workerThread)
            # Hook up signals.
            self._worker.startSignal.connect(self._worker.onStart)
            # Everything is ready. Start the worker thread, so it will
            # be ready for functions to run.
            self._workerThread.start()

    # Run ``future.result = f(*args, **kwargs)`` in a separate thread. When it
    # completes, invoke ``g(future)``, if ``g`` is provided. Returns a ``Future``
    # instance, which can be used to interact with ``f``.
    #
    def start(self,
      # A result function which take one parameter, ``future``, which will be
      # executed in the thread *t* from which this method was called, or None if
      # no function should be invoked after ``f`` completes. **Important**: ``g``
      # will **not** be invoked if the thread *t* does not provide an event
      # loop -- such as a thread taken from the thread pool. See the
      # constructor's ``qThreadOrThreadPool`` parameter for more information.
      g,

      # A function which will be executed in a separate thread. Note that:
      #
      # - Any exceptions raised in ``f`` will be caught, then re-raised in
      #   ``g(future)`` when accessing ``future.result``.
      # - **Very important**: The parameters to ``f`` must be immutable, or must
      #   not change while ``f`` is executing. The same is true of the value
      #   returned by ``f``.
      f,

      # Arguments used to invoke ``f``.
      *args,

      # Keyword arguments used to invoke ``f``.
      **kwargs):

        # Wrap ``f`` and associated data in a Future.
        future = self._wrap(g, f, *args, **kwargs)
        # Run it in another thread.
        self._start(future)
        return future

    # Wrap ``f`` and ``g`` in a Future and return it. This and the following
    # method are used to do testing.
    def _wrap(self, g, f, *args, **kwargs):
        # Wrap ``f`` and associated data in a class.
        return Future(g, f, args, kwargs)

    # Given a Future instance, run it in another thread.
    def _start(self, future):
        # Asynchronously invoke ``f``.
        if self._usePool:
            apw = _AsyncPoolWorker(future)
            self._threadPool.start(apw)
        else:
            self._worker.startSignal.emit(future)
#
# Cleanup
# ^^^^^^^
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
# #. Manually call ``asyncController.del_()`` when necessary. This is soooo
#    easy to forget.
#
#
# Context manager
# """""""""""""""
    # Provide a `context manager <https://docs.python.org/2/library/stdtypes.html#typecontextmanager>`_
    # for Pythonic construction and cleanup.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.del_()
        # Pass any exceptions through.
        return False
#
# Qt destructor
# """""""""""""
    # This is run shortly before this class's C++ destructor is invoked. It
    # emulates a C++ destructor by freeing resources before the C++ class is
    # destroyed.
    def onParentDestroyed(self):
        self.del_()
#
# Destructor
# """"""""""
    # In case the above method wasn't called, try to exit gracefully here.
    def __del__(self):
        self.del_()
#
# Manual
# """"""
    # Without calling this before the program exits, we get nasty crashes since
    # the Python portion of the class is still alive. At a minimum, we see
    # "QThread: Destroyed while thread is still running" messages.
    #
    # This is NOT thread-safe.
    def del_(self):
        # Only run this once.
        if self.isAlive:
            #print('shutdown')
            self.isAlive = False
            if self._usePool:
                self._threadPool.waitForDone()
                del self._threadPool
            else:
                # Now, shut down the thread the Worker runs in.
                self._workerThread.quit()
                self._workerThread.wait()
                # Finally, detach (and probably garbage collect) the objects
                # used by this class.
                del self._worker
                del self._workerThread
#
# Future
# ------
# The Future class holds all the information necessary to invoke ``f``
# and return its results to ``g``.
class Future(object):
    # The possible states for an instance of this class.
    STATE_WAITING, STATE_RUNNING, STATE_FINISHED, STATE_CANCELED = range(4)

    def __init__(self,
      # A function to invoke in the calling thread with the return value
      # produced by  ``f``  If this is None, it will not be invoked.
      g,
      # A function which will be invoked in the worker thread / pool.
      f,
      # A list of arguments passed to ``f``.
      args,
      # A dict of keyword arguments passed to ``f``.
      kwargs):

        self._g = g
        self._f = f
        self._args = args
        self._kwargs = kwargs

        # State maintained by Future.
        self._state = self.STATE_WAITING
        self.signalInvoker = SignalInvoker()
        self._requestCancel = False
        self._emitDoneSignal = True
        self._result = None
        self._exc_info = None

        if self._g:
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
            try:
                self._result = self._f(*self._args, **self._kwargs)
            except:
                # Save not just the exception, but also the traceback to provide
                # better debugging info when this is re-raised in the calling
                # thread.
                self._exc_info = sys.exc_info()

            # Report the results.
            self._state = self.STATE_FINISHED
            if self._emitDoneSignal:
                self.signalInvoker.doneSignal.emit(self)

    # This method may be called from any thread; it requests that the execution
    # of ``f`` be canceled. If ``f`` is already running, then it will not be
    # interrupted. However, if ``discardResult`` is True, then the results
    # returned from evaluating ``f`` will be discarded and the signal that is
    # emitted when ``f`` finishes will not be.
    def cancel(self, discardResult=False):
        self._requestCancel = True
        self._emitDoneSignal = not discardResult

    # Return the result produced by invoking ``f``, or raise any exception which
    # occurred in ``f``.
    @property
    def result(self):
        if self._exc_info:
            # Raise an exception which provides a trackback all the way into the
            # line in ``f`` that caused the exception. Just re-raising the
            # exception doesn't preserve the full traceback. Likewise, ``raise
            # self._exc_info`` provides only a limited tracebacak.
            #
            # The mapping: One form of `raise <https://docs.python.org/2/reference/simple_stmts.html#raise>`_
            # expects ``instance, None, traceback``. `sys.exc_info() <https://docs.python.org/2/library/sys.html#sys.exc_info>`_
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
    def onDoneSignal(self, future):
        future._g(future)
#
# Thread / thread pool worker classes
# -----------------------------------
# Neither the ``_AsyncWorker`` class nor the ``AsyncPoolWorker`` class should
# be instianted by a user of this module; instead, these are used by
# ``AsyncController`` to run a function in a separate thread.
class _AsyncPoolWorker(QRunnable):
    def __init__(self,
      # The Future instance which contains the callable to invoke.
      future):

        QRunnable.__init__(self)
        self._future = future

    # This is invoked by a thread from the thread pool.
    def run(self):
        self._future._invoke()

class _AsyncWorker(QObject):
    # This signal contains the information necessary to run a callable.
    startSignal = pyqtSignal(Future)

    # The start signal is connected to this slot. It runs ``f`` in the worker
    # thread.
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
        print('Done ' + str(future.result) )

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
