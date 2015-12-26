#!/usr/bin/env python3

import unittest
import os.path
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from enki.core.core import core


def _startEditCurrentFilePath():
    tree = core.workspace().openedFileExplorer.tvFiles
    model = core.workspace().openedFileExplorer.model
    document = core.workspace().currentDocument()
    tree.edit(model.documentIndex(document))


class Rename(base.TestCase):
    def test_flags(self):
        workspace = core.workspace()
        tree = core.workspace().openedFileExplorer.tvFiles
        model = core.workspace().openedFileExplorer.model
        core.workspace().createEmptyNotSavedDocument()

        def editable():
            index = model.documentIndex(workspace.currentDocument())
            return bool(int(model.flags(index)) & Qt.ItemIsEditable)

        self.assertFalse(editable())  # empty not saved document

        workspace.openFile(self.EXISTING_FILE)
        self.assertTrue(editable())  # normal document

        self.keyClicks('adsf', widget=workspace.currentDocument().qutepart)
        self.assertFalse(editable())  # modified document

    @base.inMainLoop
    def test_success(self):
        core.workspace().openFile(self.EXISTING_FILE)

        NEW_PATH = self.TEST_FILE_DIR + '/newname'
        _startEditCurrentFilePath()

        self.keyClicks(NEW_PATH)
        self.keyClick(Qt.Key_Return)
        QTest.qWait(100)  # Test fails without a sleep. Threads inside Qt???

        self.assertTrue(os.path.isfile(NEW_PATH))
        with open(NEW_PATH) as f:
            text = f.read()
            self.assertEqual(text, self.EXISTING_FILE_TEXT)

    @base.inMainLoop
    def test_os_fail(self):
        core.workspace().openFile(self.EXISTING_FILE)

        # The path shall be invalid on both Unix and Windows
        NEW_PATH = '/root/newname:::'

        _startEditCurrentFilePath()
        self.keyClicks(NEW_PATH)

        def runInDialog(dialog):
            self.assertEqual(dialog.windowTitle(), 'Failed to rename file')
            self.keyClick(Qt.Key_Return)

        self.openDialog(lambda: self.keyClick(Qt.Key_Return),
                        runInDialog)

    @base.inMainLoop
    def test_same_path(self):
        core.workspace().openFile(self.EXISTING_FILE)

        _startEditCurrentFilePath()
        self.keyClicks(self.EXISTING_FILE)
        self.keyClick(Qt.Key_Return)

        self.assertEqual(QApplication.instance().activeWindow(), core.mainWindow())  # not messagebox with error

    @base.inMainLoop
    def test_dev_null(self):
        core.workspace().openFile(self.EXISTING_FILE)
        NEW_PATH = '/dev/null'

        _startEditCurrentFilePath()

        self.keyClicks(NEW_PATH)
        self.keyClick(Qt.Key_Return)
        QTest.qWait(100)  # Test fails without a sleep. Threads inside Qt???

        self.assertFalse(os.path.isfile(self.EXISTING_FILE))
        self.assertIsNone(core.workspace().currentDocument())

    # This test reports a permission denied dailog box failure in Windows, but then crashes. Not sure how to work around this.
    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    @base.inMainLoop
    def test_dev_null_os_fail(self):
        # On Windows, a file in use cannot be deleted. Create one.
        with tempfile.NamedTemporaryFile() as tempFile:
            # In Linux, pick and undeleteable file (don't run this as root!)
            if sys.platform.startswith("linux"):
                existingNotDeletableFile = '/etc/passwd'
            else:
                existingNotDeletableFile = tempFile.name

            core.workspace().openFile(existingNotDeletableFile)

            NEW_PATH = '/dev/null'

            _startEditCurrentFilePath()

            self.keyClicks(NEW_PATH)

        def runInDialog(dialog):
            self.assertTrue(dialog.windowTitle(), 'Not this time')
            self.keyClick(Qt.Key_Return)

        self.openDialog(lambda: self.keyClick(Qt.Key_Return),
                        runInDialog)


if __name__ == '__main__':
        unittest.main()
