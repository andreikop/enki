# ***************************
# base.py - Unit test helpers
# ***************************
import unittest
import logging
import os
import sys
import shutil
import tempfile
import subprocess
import codecs
import imp
import warnings

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QKeySequence
from PyQt5.QtTest import QTest

# Import to avoid ``ImportError: QtWebEngineWidgets must be imported before a
# QCoreApplication instance is created``.
import PyQt5.QtWebEngineWidgets  # noqa: F401


papp = QApplication(sys.argv)

import qutepart
from enki.widgets.dockwidget import DockWidget
import enki.core.defines
enki.core.defines.CONFIG_DIR = tempfile.gettempdir()
from enki.core.core import core

logging.basicConfig(level=logging.ERROR)
logging.getLogger('qutepart').removeHandler(qutepart.consoleHandler)


class DummyProfiler:
    """Dummy profiler is used to run core without profiling"""

    def stepDone(self, description):
        pass

    def printInfo(self):
        pass


def _processPendingEvents():
    """Process pending application events."""

    # Create an event loop to run in. Otherwise, we need to use the
    # QApplication main loop, which may already be running and therefore
    # unusable.
    qe = QEventLoop()

    # Create a single-shot timer. Could use QTimer.singleShot(),
    # but can't cancel this / disconnect it.
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(qe.quit)
    timer.start(1)

    # Wait for an emitted signal.
    qe.exec_()

    # Clean up: don't allow the timer to call qe.quit after this
    # function exits, which would produce "interesting" behavior.
    timer.stop()
    # Stopping the timer may not cancel timeout signals in the
    # event queue. Disconnect the signal to be sure that loop
    # will never receive a timeout after the function exits.
    timer.timeout.disconnect(qe.quit)


def inMainLoop(func, *args):
    """Decorator executes test method in the QApplication main loop.
    QAction shortcuts doesn't work, if main loop is not running.
    Do not use for tests, which doesn't use main loop, because it slows down execution.
    """
    def wrapper(*args):
        def execWithArgs():
            try:
                core.mainWindow().show()
                QTest.qWaitForWindowExposed(core.mainWindow())
                app = QApplication.instance()
                app.setActiveWindow(core.mainWindow())
                assert app.focusWidget() is not None
                func(*args)
                # When done processing these events, exit the event loop. To do so,
            finally:
                try:
                    app.processEvents()
                except:
                    pass
                app.quit()

        QTimer.singleShot(0, execWithArgs)

        # Catch any exceptions which the EventLoop would otherwise catch
        # and not re-raise.
        exceptions = []

        def excepthook(type_, value, tracebackObj):
            exceptions.append((value, tracebackObj))
            QApplication.instance().exit()
        oldExcHook = sys.excepthook
        sys.excepthook = excepthook

        try:
            # Run the requested function in the application's main loop.
            QApplication.instance().exec_()
            # If an exception occurred in the event loop, re-raise it.
            if exceptions:
                value, tracebackObj = exceptions[0]
                raise value.with_traceback(tracebackObj)
        finally:
            # Restore the old exception hook
            sys.excepthook = oldExcHook

    wrapper.__name__ = func.__name__  # for unittest test runner
    return wrapper


def _cmdlineUtilityExists(cmdlineArgs):
    try:
        subprocess.call(cmdlineArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False

    return True


def requiresCmdlineUtility(command):
    """A decorator: a test requires a command.
       The command will be split if contains spaces.
    """
    cmdlineArgs = command.split()
    if not _cmdlineUtilityExists(cmdlineArgs):
        return unittest.skip('{} command not found. Cannot run the test without it'.format(cmdlineArgs[0]))
    else:
        return lambda func: func


def requiresModule(module):
    """This decorator checks that the given python module, which is
       required for a unit test, is present. If not, it skips the test."""
    try:
        imp.find_module(module)
    except ImportError:
        return unittest.skip("This test requires python-{}".format(module))
    return lambda func: func


class TestCase(unittest.TestCase):
    TEST_FILE_DIR = os.path.join(tempfile.gettempdir(), 'enki-tests')

    EXISTING_FILE = os.path.join(TEST_FILE_DIR, 'existing_file.txt')
    EXISTING_FILE_TEXT = 'hi\n'

    def _cleanUpFs(self):
        jsonTmp = os.path.join(tempfile.gettempdir(), 'enki.json')
        try:
            os.unlink(jsonTmp)
        except OSError as e:
            pass

        try:
            shutil.rmtree(self.TEST_FILE_DIR)
        except OSError as e:
            pass

    def waitUntilPassed(self, timeout, func):
        """Try to execute a function until it doesn't fail"""
        for _ in range(20):
            QTest.qWait(timeout / 20.)
            try:
                func()
            except:
                continue
            else:
                break
        else:
            func()

    def setUp(self):
        self._finished = False
        self._cleanUpFs()

        # Ignore warnings from PyQt5 ui loader
        warnings.simplefilter("ignore", ResourceWarning)
        warnings.simplefilter("ignore", DeprecationWarning)

        try:
            os.mkdir(self.TEST_FILE_DIR)
        except OSError as e:
            pass

        with open(self.EXISTING_FILE, 'w') as f:
            f.write(self.EXISTING_FILE_TEXT)

        os.chdir(self.TEST_FILE_DIR)

        core.init(DummyProfiler(), {'session_name': '',
                                    'auto-session-name': ''})

    def tearDown(self):
        self._finished = True

        def blockingFunc():
            try:
                core.workspace().forceCloseAllDocuments()
                core.term()
            finally:
                try:
                    QApplication.instance().processEvents()
                except:
                    pass
                QApplication.instance().quit()

        QTimer.singleShot(0, blockingFunc)
        QApplication.exec_()

        self._cleanUpFs()

    def keyClick(self, key, modifiers=Qt.NoModifier, widget=None):
        """Alias for ``QTest.keyClick``.

        If widget is none - focused widget will be keyclicked

        key may be QKeySequence or string
        """
        if widget is None:
            widget = QApplication.instance().focusWidget()

        if widget is None:
            widget = core.mainWindow()

        assert widget is not None

        if isinstance(key, str):
            assert modifiers == Qt.NoModifier, 'Do not set modifiers, if using text key'
            code = QKeySequence(key)[0]
            key = Qt.Key(code & 0x01ffffff)
            modifiers = Qt.KeyboardModifiers(code & 0xfe000000)

        QTest.keyClick(widget, key, modifiers)

    def keyClicks(self, text, modifiers=Qt.NoModifier, widget=None):
        """Alias for ``QTest.keyClicks``.

        If widget is none - focused widget will be keyclicked"""
        if widget is None:
            widget = QApplication.instance().focusWidget()

        if widget is None:
            widget = core.mainWindow()

        assert widget is not None

        QTest.keyClicks(widget, text, modifiers)

    def createFile(self, name, text):
        """Create file in TEST_FILE_DIR.

        File is opened
        """
        path = os.path.join(self.TEST_FILE_DIR, name)
        with codecs.open(path, 'wb', encoding='utf8') as file_:
            file_.write(text)

        return core.workspace().openFile(path)

    def _findDialog(self):
        for widget in QApplication.instance().topLevelWidgets():
            if widget.isVisible() and isinstance(widget, QDialog):
                return widget
        else:
            return None

    def openDialog(self, openDialogFunc, runInDialogFunc):
        """Open dialog by executing ``openDialogFunc`` and run ``runInDialogFunc``.
        Dialog is passed as a parameter to ``runInDialogFunc``
        """
        DELAY = 20
        ATTEMPTS = 50

        def isDialogsChild(dialog, widget):
            if widget is None:
                return False

            return widget is dialog or \
                isDialogsChild(dialog, widget.parentWidget())

        def timerCallback(attempt):
            if self._finished:
                return

            dialog = self._findDialog()

            if dialog is not None and \
               isDialogsChild(dialog, QApplication.instance().focusWidget()):
                runInDialogFunc(dialog)
            else:
                if attempt < ATTEMPTS:
                    QTimer.singleShot(20, lambda: timerCallback(attempt + 1))
                else:
                    self.fail("Dialog not found")

        QTimer.singleShot(20, lambda: timerCallback(1))
        openDialogFunc()

    def openSettings(self, runInDialogFunc):
        """Open Enki settings dialog and run ``runInDialogFunc``.
        Dialog is passed as a parameter to ``runInDialogFunc``
        """
        # Note that the settings dialog calls ``dialog.open()``, not
        # ``dialog.exec_()``. So, open it:
        core.actionManager().action("mSettings/aSettings").trigger()
        # Then run exec_, with runInDialogFunc executing in exec_'s loop.
        dialog = self._findDialog()
        return self.openDialog(dialog.exec_,
                               runInDialogFunc)

    def retryUntilPassed(self, timeoutMs, function):
        """ Try to execute a function until it doesn't generate any exception
        but not more than for timeoutSec
        Raise exception, if timeout passed
        """
        for _ in range(20):
            QTest.qWait(timeoutMs / 20.)
            try:
                function()
            except:
                continue
            else:
                return
        else:
            function()

    def findDock(self, windowTitle):
        """Return a reference to the dock object whose name is windowTitle.
        """
        for dock in core.mainWindow().findChildren(DockWidget):
            # The preview dock's name will have the title of the web page it's
            # it's displaying appended to the title (when a Sphinx document is
            # loaded). Therefore, check for startswith instead of equality.
            if dock.windowTitle().startswith(windowTitle):
                return dock
        else:
            self.fail('Dock {} not found'.format(windowTitle))

    def findVisibleDock(self, windowTitle):
        """Return a reference to the dock object which is both visible and
        has "windowTitle" as its name.
        """
        # Per Andrei's explaination, Enki dock has the following 4 states:
        #
        # #. doesn't exist, not available. Search results dock is created only
        #    when search in directory is used first time;
        # #. exists, available, but not visible. Close "Opened Files" dock. It
        #    still exists and can be opened again by Alt+O;
        # #. exists, available, visible;
        # #. exists, not available, not visible. Navigator is only shown for
        #    languages which are supported by ctags. If current file is not
        #    supported, Navigator is not available. But may exist because had
        #    been created for another file.
        #
        # Dock can exist for another file even if it might not be visible. In
        # our test case, there will always be one preview dock exisiting for
        # *dummy.html* file. Thus instead of checking ``findChildren``, we use
        # ``_addedDockWidigets`` that will only check available docks.
        for dock in core.mainWindow()._addedDockWidgets:
            if dock.windowTitle().startswith(windowTitle):
                return dock
        else:
            self.fail('Dock {} not found'.format(windowTitle))

    def assertEmits(self, sender, senderSignal, timeoutMs=1,
                    expectedSignalParams=None):
        """ A unit testing convenience routine.

        Assert that calling the sender function emits the senderSignal within timeoutMs.
        The default timeoutMs of 1 works for all senders that
        run in the current thread, since the timeout will be
        scheduled after all current thread signals are emitted
        at a timeout of 0 ms.

        """
        self.assertTrue(waitForSignal(sender, senderSignal,
                                      timeoutMs, expectedSignalParams))


def waitForSignal(sender, senderSignal, timeoutMs, expectedSignalParams=None):
    """ Wait up to timeoutMs after calling sender() for senderSignal
    to be emitted.

    It returns True if the senderSignal was emitted; otherwise,
    it returns False. If expectedSignalParams is not None, it
    is compared against the parameters emitted by the senderSignal.
    This function was inspired by http://stackoverflow.com/questions/2629055/qtestlib-qnetworkrequest-not-executed/2630114#2630114.

    """
    # Create a single-shot timer. Could use QTimer.singleShot(),
    # but can't cancel this / disconnect it.
    timer = QTimer()
    timer.setSingleShot(True)

    # Create an event loop to run in. Otherwise, we need to use the
    # QApplication main loop, which may already be running and therefore
    # unusable.
    qe = QEventLoop()

    # Create a slot which receives a senderSignal with any number
    # of arguments. Check the arguments against their expected
    # values, if requested, storing the result in senderSignalArgsWrong[0].
    # (I can't use senderSignalArgsWrong = True/False, since
    # non-local variables cannot be assigned in another scope).
    senderSignalArgsWrong = []

    def senderSignalSlot(*args):
        # If the senderSignal args should be checked and they
        # don't match, then they're wrong. In all other cases,
        # they're right.
        senderSignalArgsWrong.append(
            (expectedSignalParams is not None) and
            (expectedSignalParams != args))
        # We received the requested signal, so exit the event loop.
        qe.exit()

    # Connect both signals to a slot which quits the event loop.
    senderSignal.connect(senderSignalSlot)
    timer.timeout.connect(qe.quit)

    # Start the sender and the timer and at the beginning of the event loop.
    # Just calling sender() may cause signals emitted in sender
    # not to reach their connected slots.
    QTimer.singleShot(0, sender)
    timer.start(timeoutMs)

    # Catch any exceptions which the EventLoop would otherwise catch
    # and not re-raise.
    exceptions = []

    def excepthook(type_, value, tracebackObj):
        exceptions.append((value, tracebackObj))
    oldExcHook = sys.excepthook
    sys.excepthook = excepthook

    # Wait for an emitted signal.
    qe.exec_()
    # If an exception occurred in the event loop, re-raise it.
    if exceptions:
        value, tracebackObj = exceptions[0]
        raise value.with_traceback(tracebackObj)
    # Clean up: don't allow the timer to call app.quit after this
    # function exits, which would produce "interesting" behavior.
    ret = timer.isActive()
    timer.stop()
    # Stopping the timer may not cancel timeout signals in the
    # event queue. Disconnect the signal to be sure that loop
    # will never receive a timeout after the function exits.
    # Likewise, disconnect the senderSignal for the same reason.
    senderSignal.disconnect(senderSignalSlot)
    timer.timeout.disconnect(qe.quit)
    # Restore the old exception hook
    sys.excepthook = oldExcHook

    return ret and senderSignalArgsWrong and (not senderSignalArgsWrong[0])

# The function above is rather awkward to use. This provides the same
# functionality, but as a context manager instead. All statements inside the
# ``with`` statement are run, then a timer started; if a signal is emitted
# before the timer expires, the test succeeds.


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
                 printExcTraceback=True,
                 # Number of times this signal must be emitted
                 numEmittedExpected=1):

        self.signal = signal
        self.timeoutMs = timeoutMs
        self.expectedSignalParams = expectedSignalParams
        self.assertIfNotRaised = assertIfNotRaised
        self.printExcTraceback = printExcTraceback
        self.numEmittedExpected = numEmittedExpected

        # Stores the result of comparing self.expectedSignalParams with the
        # actual params.
        self.areSenderSignalArgsWrong = False
        # The number of times this signal was emitted.
        self.numEmitted = 0

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
        self.numEmitted += 1
        if self._gotSignal():
            # We received the requested signal, so exit the event loop or never
            # enter it (exit won't exit an event loop that hasn't been run). When
            # this is nested inside other WaitForSignal clauses, signals may be
            # received in another QEventLoop, even before this object's QEventLoop
            # starts.
            self.qe.exit()

    # True of the signal was emitted the expected number of times.
    def _gotSignal(self):
        return self.numEmitted == self.numEmittedExpected

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
        if not self._gotSignal():
            self.qe.exec_()
        # Restore the old exception hook
        sys.excepthook = oldExcHook
        # Clean up: don't allow the timer to call qe.quit after this
        # function exits, which would produce "interesting" behavior.
        timerIsActive = self.timer.isActive()
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
            raise value.with_traceback(tracebackObj)

        # Check that the signal occurred.
        self.sawSignal = timerIsActive and not self.areSenderSignalArgsWrong
        if self.assertIfNotRaised:
            self.assertTrue(self.sawSignal)

        # Don't mask exceptions.
        return False
