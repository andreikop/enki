#!/usr/bin/env python3

"""Tests for workspace_actions plugin functionality
"""

import unittest
import os.path
import os
import sys
import stat

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base  # configures sys.path ans sip

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from enki.core.core import core


class Rename(base.TestCase):

    def test_action_enabled(self):
        action = core.actionManager().action("mFile/mFileSystem/aRename")
        core.workspace().closeAllDocuments()

        self.assertFalse(action.isEnabled())

        document = core.workspace().createEmptyNotSavedDocument()
        self.assertFalse(action.isEnabled())

        document.setFilePath(self.TEST_FILE_DIR + 'file')
        self.assertTrue(action.isEnabled())

        core.workspace().closeAllDocuments()
        self.assertFalse(action.isEnabled())

    def test_success(self):
        OLD_PATH = self.TEST_FILE_DIR + '/oldname'
        NEW_PATH = self.TEST_FILE_DIR + '/newname'

        document = core.workspace().createEmptyNotSavedDocument()
        action = core.actionManager().action("mFile/mFileSystem/aRename")

        document.setFilePath(OLD_PATH)
        document.qutepart.text = 'hi'

        # can not rename, if not saved
        def runInDialog(dialog):
            self.assertTrue(dialog.windowTitle(), 'Rename file')
            self.keyClick(Qt.Key_Return)

        self.openDialog(action.trigger, runInDialog)

        document.saveFile()

        # can rename
        def runInDialog(dialog):
            QTest.keyClicks(QApplication.instance().focusWidget(), NEW_PATH)
            self.keyClick(Qt.Key_Return)

        self.openDialog(action.trigger, runInDialog)

        self.assertTrue(os.path.isfile(NEW_PATH))
        with open(NEW_PATH) as f:
            text = f.read()
            self.assertEqual(text, 'hi\n')

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_os_fail(self):
        NEW_PATH = '/root/newname'

        document = core.workspace().openFile(self.EXISTING_FILE)
        action = core.actionManager().action("mFile/mFileSystem/aRename")

        # can rename
        def runInDialog(dialog):
            QTest.keyClicks(QApplication.instance().focusWidget(), NEW_PATH)

            def nextRunInDialog(nextDialog):
                self.assertEqual(nextDialog.windowTitle(), 'Failed to rename file')
                self.keyClick(Qt.Key_Return)

            self.openDialog(lambda: self.keyClick(Qt.Key_Return),
                            nextRunInDialog)

        self.openDialog(action.trigger, runInDialog)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_same_path(self):
        FILE_PATH = '/etc/passwd'

        document = core.workspace().openFile(FILE_PATH)
        action = core.actionManager().action("mFile/mFileSystem/aRename")

        def runInDialog(dialog):
            QTest.keyClicks(QApplication.instance().focusWidget(), FILE_PATH)
            # will not generate error messagebox, because same path is used
            self.keyClick(Qt.Key_Return)

        self.openDialog(action.trigger, runInDialog)
        # will freeze, if error happened

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_dev_null(self):
        action = core.actionManager().action("mFile/mFileSystem/aRename")

        document = core.workspace().openFile(self.EXISTING_FILE)

        self.assertTrue(os.path.isfile(self.EXISTING_FILE))

        def runInDialog(dialog):
            QTest.keyClicks(QApplication.instance().focusWidget(), '/dev/null')
            self.keyClick(Qt.Key_Return)

        self.openDialog(action.trigger, runInDialog)

        self.assertFalse(os.path.isfile(self.EXISTING_FILE))
        self.assertIsNone(core.workspace().currentDocument())

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_dev_null_os_fail(self):
        action = core.actionManager().action("mFile/mFileSystem/aRename")

        core.workspace().closeAllDocuments()
        document = core.workspace().openFile('/etc/passwd')

        def runInDialog(dialog):
            QTest.keyClicks(QApplication.instance().focusWidget(), '/dev/null')

            def runInNextDialog(nextDialog):
                self.assertTrue(nextDialog.windowTitle(), 'Not this time')
                self.keyClick(Qt.Key_Return)

            self.openDialog(lambda: self.keyClick(Qt.Key_Return),
                            runInNextDialog)

        self.openDialog(action.trigger, runInDialog)


class ToggleExecutable(base.TestCase):

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_action_enabled(self):
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")
        core.workspace().closeAllDocuments()

        self.assertFalse(action.isEnabled())

        document = core.workspace().createEmptyNotSavedDocument()
        self.assertFalse(action.isEnabled())

        document = core.workspace().openFile(self.EXISTING_FILE)
        self.assertTrue(action.isEnabled())

        core.workspace().closeAllDocuments()
        self.assertFalse(action.isEnabled())

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_action_text(self):
        document = core.workspace().openFile(self.EXISTING_FILE)
        menu = core.actionManager().action("mFile/mFileSystem").menu()
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")

        menu.aboutToShow.emit()
        self.assertEqual(action.text(), 'Make executable')

        st = os.stat(self.EXISTING_FILE)
        os.chmod(self.EXISTING_FILE, st.st_mode | stat.S_IEXEC)

        menu.aboutToShow.emit()
        self.assertEqual(action.text(), 'Make Not executable')

        os.chmod(self.EXISTING_FILE, st.st_mode)
        menu.aboutToShow.emit()
        self.assertEqual(action.text(), 'Make executable')

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_modify_flags(self):
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")

        document = core.workspace().openFile(self.EXISTING_FILE)

        self.assertFalse(os.access(self.EXISTING_FILE, os.X_OK))
        action.trigger()
        self.assertTrue(os.access(self.EXISTING_FILE, os.X_OK))
        action.trigger()
        self.assertFalse(os.access(self.EXISTING_FILE, os.X_OK))

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_os_fail(self):
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")

        FILE_PATH = '/etc/passwd'

        document = core.workspace().openFile(FILE_PATH)

        self.assertFalse(os.access(FILE_PATH, os.X_OK))

        def runInDialog(dialog):
            self.assertEqual(dialog.windowTitle(), 'Failed to change executable mode')
            self.keyClick(Qt.Key_Return)

        self.openDialog(action.trigger, runInDialog)


if __name__ == '__main__':
    base.main()
