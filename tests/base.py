# ***************************
# base.py - Unit test helpers
# ***************************
import unittest
import logging
import os
import sys
import threading
import shutil
import time
import tempfile
import subprocess

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
from persistent_qapplication import papp

from PyQt4.QtCore import Qt, QTimer, QEventLoop, pyqtSlot
from PyQt4.QtGui import QApplication, QDialog, QKeySequence
from PyQt4.QtTest import QTest

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


def _processPendingEvents(app):
    """Process pending application events."""

    # Quit the event loop when it becomes idle.
    QTimer.singleShot(0, papp.quit)
    papp.exec_()

# By default, the traceback for excpetions occurring inside
# an exec_ loop will be printed.
PRINT_EXEC_TRACKBACK = True

def inMainLoop(func, *args):
    """Decorator executes test method in the QApplication main loop.
    QAction shortcuts doesn't work, if main loop is not running.
    Do not use for tests, which doesn't use main loop, because it slows down execution.
    """
    def wrapper(*args):
        self = args[0]

        def execWithArgs():
            core.mainWindow().show()
            QTest.qWaitForWindowShown(core.mainWindow())
            func(*args)
            # When done processing these events, exit the event loop.
            QTimer.singleShot(0, self.app.quit)

        QTimer.singleShot(0, execWithArgs)

        # Catch any exceptions which the EventLoop would otherwise catch
        # and not re-raise.
        ex = []
        def excepthook(type_, value, traceback):
            ex.append(value)
            if PRINT_EXEC_TRACKBACK:
                oeh(type_, value, traceback)
            self.app.quit()
        oeh = sys.excepthook
        sys.excepthook = excepthook

        # Run the requested function in the application's main loop.
        self.app.exec_()
        # If an exception occurred in the event loop, re-raise it.
        if ex:
            raise ex[0]
        # Restore the old exception hook
        sys.excepthook = oeh

    wrapper.__name__ = func.__name__  # for unittest test runner
    return wrapper


def _cmdlineUtilityExists(cmdlineArgs):
    try:
        subprocess.call(cmdlineArgs, stdout=subprocess.PIPE)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False

    return True


def requiresCmdlineUtility(command):
    """A decorator: a test requires a command.
    The command will be splitted if contains spaces
    """
    def inner(func):
        def wrapper(*args, **kwargs):
            cmdlineArgs = command.split()
            if not _cmdlineUtilityExists(cmdlineArgs):
                self = args[0]
                self.fail('{} command not found. Can not run the test without it'.format(cmdlineArgs[0]))
            return func(*args, **kwargs)
        return wrapper
    return inner


class TestCase(unittest.TestCase):
    app = papp

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


    def setUp(self):
        self._finished = False
        self._cleanUpFs()
        try:
            os.mkdir(self.TEST_FILE_DIR)
        except OSError as e:
            pass

        with open(self.EXISTING_FILE, 'w') as f:
            f.write(self.EXISTING_FILE_TEXT)

        os.chdir(self.TEST_FILE_DIR)

        core.init(DummyProfiler())

    def tearDown(self):
        self._finished = True

        for document in core.workspace().documents():
            document.qutepart.text = ''  # clear modified flag, avoid Save Files dialog

        core.workspace().closeAllDocuments()
        core.term()
        
        # | **Find orphaned objects**
        # | Look for any objects that are still generating signals after
        # core.term().
        #
        # \1. Process all termination-related events.
        _processPendingEvents(self.app)
        # \2. Now, print a diagnostic on any events that are still occurring.
        self.app.assertOnEvents = True
        _processPendingEvents(self.app)
        self.app.assertOnEvents = False

        self._cleanUpFs()

    def keyClick(self, key, modifiers=Qt.NoModifier, widget=None):
        """Alias for ``QTest.keyClick``.

        If widget is none - focused widget will be keyclicked"""
        if widget is not None:
            widget = self.app.focusWidget()

        if isinstance(key, basestring):
            assert modifiers == Qt.NoModifier, 'Do not set modifiers, if using text key'
            code = QKeySequence(key)[0]
            key = Qt.Key(code & 0x01ffffff)
            modifiers = Qt.KeyboardModifiers(code & 0xfe000000)

        QTest.keyClick(widget, key, modifiers)

    def keyClicks(self, text, modifiers=Qt.NoModifier, widget=None):
        """Alias for ``QTest.keyClicks``.

        If widget is none - focused widget will be keyclicked"""
        if widget is not None:
            QTest.keyClicks(widget, text, modifiers)
        else:
            QTest.keyClicks(self.app.focusWidget(), text, modifiers)

    def createFile(self, name, text):
        """Create file in TEST_FILE_DIR.

        File is opened
        """
        path = os.path.join(self.TEST_FILE_DIR, name)
        with open(path, 'wb') as file_:
            file_.write(text)

        return core.workspace().openFile(path)

    def _findDialog(self):
        for widget in self.app.topLevelWidgets():
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
               isDialogsChild(dialog, self.app.focusWidget()):
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
        return self.openDialog(core.actionManager().action("mSettings/aSettings").trigger,
                               runInDialogFunc)

    def sleepProcessEvents(self, delay):
        end = time.time() + delay
        while time.time() < end:
            self.app.processEvents()
            time.sleep(0.01)

    def findDock(self, windowTitle):
        for dock in core.mainWindow().findChildren(DockWidget):
            if dock.windowTitle() == windowTitle:
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
          (expectedSignalParams != args) )
        # We received the requested signal, so exit the event loop.
        papp.quit()

    # Connect both signals to a slot which quits the event loop.
    senderSignal.connect(senderSignalSlot)
    timer.timeout.connect(papp.quit)

    # Start the sender and the timer and at the beginning of the event loop.
    # Just calling sender() may cause signals emitted in sender
    # not to reach their connected slots.
    QTimer.singleShot(0, sender)
    timer.start(timeoutMs)

    # Catch any exceptions which the EventLoop would otherwise catch
    # and not re-raise.
    ex = []
    def excepthook(type_, value, traceback):
        ex.append(value)
        if PRINT_EXEC_TRACKBACK:
            oeh(type_, value, traceback)
    oeh = sys.excepthook
    sys.excepthook = excepthook

    # Wait for an emitted signal.
    papp.exec_()
    # If an exception occurred in the event loop, re-raise it.
    if ex:
        raise ex[0]
    # Clean up: don't allow the timer to call app.quit after this
    # function exits, which would produce "interesting" behavior.
    ret = timer.isActive()
    timer.stop()
    # Stopping the timer may not cancel timeout signals in the
    # event queue. Disconnect the signal to be sure that loop
    # will never receive a timeout after the function exits.
    # Likewise, disconnect the senderSignal for the same reason.
    senderSignal.disconnect(senderSignalSlot)
    timer.timeout.disconnect(papp.quit)
    # Restore the old exception hook
    sys.excepthook = oeh
    
    return ret and senderSignalArgsWrong and (not senderSignalArgsWrong[0])
