import unittest
import logging
import os
import sys
import threading
import shutil
import time
import tempfile
import subprocess

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4.QtCore import Qt, QTimer, QEventLoop, pyqtSlot
from PyQt4.QtGui import QApplication, QDialog, QKeySequence
from PyQt4.QtTest import QTest


import qutepart

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

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
    """Process pending application events.
    Timeout is used, because on Windows hasPendingEvents() always returns True
    """
    t = time.time()
    while app.hasPendingEvents() and (time.time() - t < 0.1):
        app.processEvents()

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
        # Exceptions get silenced inside execWithArgs. Use
        # eList to store then re-raise them. Note that a list
        # must be used, since this is passed to a function and
        # any changes to a non-mutable object will be lost when
        # the function exits.
        eList = []

        def execWithArgs(eListLocal):
            core.mainWindow().show()
            QTest.qWaitForWindowShown(core.mainWindow())
            _processPendingEvents(self.app)

            try:
                func(*args)
            except Exception as e:
                # Save the exception so we can re-raise it; exceptions here
                # get caught and reported (I think by PyQt).
                eListLocal.append(e)
                if PRINT_EXEC_TRACKBACK:
                    raise
            finally:
                _processPendingEvents(self.app)
                self.app.quit()

        QTimer.singleShot(0, lambda: execWithArgs(eList))

        self.app.exec_()
        # Re-raise any exceptions (such as unit test failed assertions)
        # that happened while executing func. Unfortunately, this
        # reports a traceback from here, instead of from the except
        # clause above. I don't know how to easily fix this.
        if eList:
            raise eList[0]

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


class NotifyApplication(QApplication):
    """ This class can assert if any events are emitted.
    
    Its purpose is to check that, after a PyQt class is closed, there are no timer/other callback leaks.
    
    """
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self.assertOnEvents = False
        
    def notify(self, receiver, event):
        """ Pass the event on, printing diagnostics if enabled. """
        
        if self.assertOnEvents:
            print('Post-termination event: receiver = %s, event = %s' % (receiver, event))
        return QApplication.notify(self, receiver, event)
        
papp = NotifyApplication(sys.argv)
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
        
        # Find orphaned objects
        # ---------------------
        # Look for any objects that are still generating signals after
        # core.term().
        #
        # 1. Process all termination-related events.
        _processPendingEvents(self.app)
        # 2. Now, print a diagnostic on any events that are still occurring.
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
            key = Qt.Key(code & 0x00ffffff)
            modifiers = Qt.KeyboardModifiers(code & 0xff000000)

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
        with open(path, 'w') as file_:
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
            
    def assertEmits(self, sender, senderSignal, timeoutMs=1):
        """ A unit testing convenience routine.
        
        Assert that calling the sender function emits the senderSignal within timeoutMs.
        The default timeoutMs of 1 works for all senders that
        run in the current thread, since the timeout will be
        scheduled after all current thread signals are emitted
        at a timeout of 0 ms.
        
        """
        self.assertTrue(waitForSignal(sender, senderSignal, timeoutMs))
            
def waitForSignal(sender, senderSignal, timeoutMs):
    """ Wait up to timeoutMs after calling sender for senderSignal to be emitted.
    
    It returns True if the senderSignal was emitted; otherwise, it returns False.
    This function was inspired by http://stackoverflow.com/questions/2629055/qtestlib-qnetworkrequest-not-executed/2630114#2630114.
    
    """
    # Create a single-shot timer. Could use QTimer.singleShot(),
    # but can't cancel this / disconnect it.
    timer = QTimer()
    timer.setSingleShot(True)
    # Create an event loop to wait for either the senderSignal
    # or the timer's timeout signal.
    loop = QEventLoop()

    # Create a slot which receives a senderSignal with any number of arguments.
    def senderSignalSlot(*args):
        loop.quit()

    # Connect both signals to a slot which quits the event loop.
    senderSignal.connect(senderSignalSlot)
    timer.timeout.connect(loop.quit)
    
    # Exceptions in sender(), which is run in loop.exec_(), are
    # caught. Catch then re-raise them; see inMainLoop for
    # a full explanation.
    def senderWithExceptions(sender, eListLocal):
        try:
            sender()
        except Exception as e:
            eListLocal.append(e)
            if PRINT_EXEC_TRACKBACK:
                raise

    # Start the sender and the timer and at the beginning of the event loop.
    # Just calling sender() may cause signals emitted in sender
    # not to reach their connected slots.
    eList = []
    QTimer.singleShot(0, lambda: senderWithExceptions(sender, eList))
    timer.start(timeoutMs)
    
    # Wait for an emitted signal. Make sure to do cleanup even on an exception.
    try:
        loop.exec_()
        if eList:
            raise eList[0]
    finally:
        # Clean up: don't allow the timer to call loop after this
        # function exits, which would produce "interesting" behavior.
        ret = timer.isActive()
        timer.stop()
        # Stopping the timer may not cancel timeout signals in the
        # event queue. Disconnect the signal to be sure that loop
        # will never receive a timeout after the function exits.
        # Likewise, disconnect the senderSignal for the same reason.
        senderSignal.disconnect(senderSignalSlot)
        timer.timeout.disconnect(loop.quit)
        
    return ret
