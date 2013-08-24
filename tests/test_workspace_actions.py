#!/usr/bin/env python

"""Tests for workspace_actions plugin functionality
"""

import unittest
import os.path
import os
import stat

import base  # configures sys.path ans sip

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from enki.core.core import core


class Rename(base.TestCase):
    def test_action_enabled(self):
        action = core.actionManager().action("mFile/mFileSystem/aRename")
        core.workspace().closeAllDocuments()
        
        self.assertFalse(action.isEnabled())
        
        document = core.workspace().createEmptyNotSavedDocument()
        self.assertFalse(action.isEnabled())
        
        document.setFilePath(self.TEST_FILES_DIR + 'file')
        self.assertTrue(action.isEnabled())
        
        core.workspace().closeAllDocuments()
        self.assertFalse(action.isEnabled())
    
    @base.in_main_loop
    def test_success(self):
        OLD_PATH = self.TEST_FILES_DIR + 'oldname'
        NEW_PATH = self.TEST_FILES_DIR + 'newname'
        
        document = core.workspace().currentDocument()
        action = core.actionManager().action("mFile/mFileSystem/aRename")
        
        document.setFilePath(OLD_PATH)
        document.qutepart.text = 'hi'
        
        # can not rename, if not saved
        def runInDialog(dialog):
            self.assertTrue(dialog.windowTitle(), 'Rename file')
            QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        
        self.openDialog(action.trigger, runInDialog)
        
        document.saveFile()
        
        # can rename
        def runInDialog(dialog):
            QTest.keyClicks(self.app.focusWidget(), NEW_PATH)
            QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        
        self.openDialog(action.trigger, runInDialog)

        self.assertTrue(os.path.isfile(NEW_PATH))
        with open(NEW_PATH) as f:
            text = f.read()
            self.assertEqual(text, 'hi\n')

    def test_os_fail(self):
        OLD_PATH = self.TEST_FILES_DIR + 'oldname'
        NEW_PATH = '/root/newname'

        document = core.workspace().currentDocument()
        action = core.actionManager().action("mFile/mFileSystem/aRename")
        
        document.setFilePath(OLD_PATH)
        document.qutepart.text = 'hi'
        document.saveFile()
        
        # can rename
        def runInDialog(dialog):
            QTest.keyClicks(self.app.focusWidget(), NEW_PATH)
            
            def nextRunInDialog(nextDialog):
                self.assertEqual(nextDialog.windowTitle(), 'Failed to rename file')
                QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
            
            self.openDialog(lambda: QTest.keyClick(self.app.focusWidget(), Qt.Key_Return),
                            nextRunInDialog)
        
        self.openDialog(action.trigger, runInDialog)


class ToggleExecutable(base.TestCase):
    def test_action_enabled(self):
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")
        core.workspace().closeAllDocuments()
        
        self.assertFalse(action.isEnabled())
        
        document = core.workspace().createEmptyNotSavedDocument()
        self.assertFalse(action.isEnabled())
        
        document.setFilePath(self.TEST_FILES_DIR + 'file')
        document.saveFile()
        self.assertTrue(action.isEnabled())
        
        core.workspace().closeAllDocuments()
        self.assertFalse(action.isEnabled())
    
    def test_action_text(self):
        document = core.workspace().currentDocument()
        menu = core.actionManager().action("mFile/mFileSystem").menu()
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")
        
        FILE_PATH = self.TEST_FILES_DIR + 'file'
        
        document.setFilePath(FILE_PATH)
        document.saveFile()
        
        menu.aboutToShow.emit()
        self.assertEqual(action.text(), 'Make executable')
        
        st = os.stat(FILE_PATH)
        os.chmod(FILE_PATH, st.st_mode | stat.S_IEXEC)

        menu.aboutToShow.emit()
        self.assertEqual(action.text(), 'Make Not executable')

        os.chmod(FILE_PATH, st.st_mode)
        menu.aboutToShow.emit()
        self.assertEqual(action.text(), 'Make executable')
    
    def test_modify_flags(self):
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")
        
        FILE_PATH = self.TEST_FILES_DIR + 'file'
        
        document = core.workspace().currentDocument()
        document.setFilePath(FILE_PATH)
        document.saveFile()

        self.assertFalse(os.access(FILE_PATH, os.X_OK))
        action.trigger()
        self.assertTrue(os.access(FILE_PATH, os.X_OK))
        action.trigger()
        self.assertFalse(os.access(FILE_PATH, os.X_OK))

    @base.in_main_loop
    def test_os_fail(self):
        action = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")
        
        FILE_PATH = '/etc/passwd'
        
        document = core.workspace().currentDocument()
        document.setFilePath(FILE_PATH)

        self.assertFalse(os.access(FILE_PATH, os.X_OK))
        
        def runInDialog(dialog):
            self.assertEqual(dialog.windowTitle(), 'Failed to change executable mode')
            QTest.keyClick(self.app.focusWidget(), Qt.Key_Return)
        
        self.openDialog(action.trigger, runInDialog)


if __name__ == '__main__':
    unittest.main()
