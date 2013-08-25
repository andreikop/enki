#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtCore import Qt, QPoint
from PyQt4.QtTest import QTest

from enki.core.core import core
from enki.widgets.dockwidget import DockWidget


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
        
        def editable():
            index = model.documentIndex(workspace.currentDocument())
            return bool(int(model.flags(index)) & Qt.ItemIsEditable)
        
        self.assertFalse(editable())  # empty not saved document
        
        workspace.openFile('/etc/passwd')
        self.assertTrue(editable())  # normal document
        
        QTest.keyClicks(workspace.currentDocument().qutepart, 'adsf')
        self.assertFalse(editable())  # modified document
    
    @base.in_main_loop
    def test_success(self):
        core.workspace().openFile(self.EXISTING_FILE)
        
        NEW_PATH = self.TEST_FILES_DIR + 'newname'
        _startEditCurrentFilePath()
        
        QTest.keyClicks(self.app.focusWidget(), NEW_PATH)
        QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        QTest.qWait(100)  # Test fails without a sleep. Threads inside Qt???

        self.assertTrue(os.path.isfile(NEW_PATH))
        with open(NEW_PATH) as f:
            text = f.read()
            self.assertEqual(text, self.EXISTING_FILE_TEXT)

    @base.in_main_loop
    def test_os_fail(self):
        core.workspace().openFile(self.EXISTING_FILE)
        
        NEW_PATH = '/root/newname'
        
        _startEditCurrentFilePath()
        QTest.keyClicks(self.app.focusWidget(), NEW_PATH)

        def runInDialog(dialog):
            self.assertEqual(dialog.windowTitle(), 'Failed to rename file')
            QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        
        self.openDialog(lambda: QTest.keyClick(self.app.focusWidget(), Qt.Key_Return),
                        runInDialog)

    @base.in_main_loop
    def test_same_path(self):
        FILE_PATH = '/etc/passwd'
        core.workspace().openFile(FILE_PATH)
        
        _startEditCurrentFilePath()
        QTest.keyClicks(self.app.focusWidget(), FILE_PATH)
        QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        
        self.assertEqual(self.app.activeWindow(), core.mainWindow())  # not messagebox with error

    @base.in_main_loop
    def test_dev_null(self):
        core.workspace().openFile(self.EXISTING_FILE)
        NEW_PATH = '/dev/null'
        
        _startEditCurrentFilePath()
        
        QTest.keyClicks(self.app.focusWidget(), NEW_PATH)
        QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        QTest.qWait(100)  # Test fails without a sleep. Threads inside Qt???

        self.assertFalse(os.path.isfile(self.EXISTING_FILE))
        self.assertIsNone(core.workspace().currentDocument())

    @base.in_main_loop
    def test_dev_null_os_fail(self):
        core.workspace().openFile('/etc/passwd')
        NEW_PATH = '/dev/null'
        
        _startEditCurrentFilePath()
                
        QTest.keyClicks(self.app.focusWidget(), NEW_PATH)
        
        def runInDialog(dialog):
            self.assertTrue(dialog.windowTitle(), 'Not this time')
            QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        
        self.openDialog(lambda: QTest.keyClick(self.app.focusWidget(), Qt.Key_Return),
                        runInDialog)


if __name__ == '__main__':
    unittest.main()
