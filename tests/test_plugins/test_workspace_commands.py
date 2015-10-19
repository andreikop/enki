#!/usr/bin/env python

"""Tests for workspace_actions plugin functionality
"""

import unittest
import os.path
import os
import sys


sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base  # configures sys.path ans sip

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from enki.core.core import core


class Test(base.TestCase):
    def _execCommand(self, text):
        def inDialogFunc(dialog):
            self.keyClicks(text)
            QTest.qWait(150)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(self._openDialog, inDialogFunc)

    def _openDialog(self):
        self.keyClicks('L', Qt.ControlModifier)

    @base.inMainLoop
    def test_01(self):
        """Go to line"""
        document = self.createFile('asdf.txt', 'a\n' * 10)
        self._execCommand('l 5')
        self.assertEqual(document.qutepart.cursorPosition[0], 4)

    @base.inMainLoop
    def test_02(self):
        """Open file, type only path"""
        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand(fullPath.replace('\\', '\\\\'))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_03(self):
        """Open file, type 'f path' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand('o ' + fullPath.replace('\\', '\\\\'))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_04(self):
        """Save file, create dirs"""
        document = core.workspace().createEmptyNotSavedDocument()
        document.qutepart.text = 'filetext'

        fullPath = os.path.join(self.TEST_FILE_DIR, 'dir1/dir2/thefile.txt')

        self._execCommand('s ' + fullPath.replace('\\', '\\\\'))

        with open(fullPath) as file_:
            data = file_.read()

        self.assertEqual(data, 'filetext\n')

    @base.inMainLoop
    def test_05(self):
        """Save file, relative path"""
        text = 'a\n' * 10
        document = self.createFile('asdf.txt', text)

        relPath = 'dir1/dir2/newfile.txt'

        self._execCommand('s ' + relPath)

        with open(relPath) as file_:
            data = file_.read()

        self.assertEqual(data, text)

    @base.inMainLoop
    def test_06(self):
        """Open file, type 'f path with spaces' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'the file.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand('o ' + fullPath.replace('\\', '\\\\').replace(' ', '\\ '))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_07(self):
        """ Check inline completion for file with spaces"""
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'the file.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        def inDialogFunc(dialog):
            cmdPath = (self.TEST_FILE_DIR + '/the').replace('\\', '\\\\').replace(' ', '\\ ')
            self.keyClicks('o ' + cmdPath)
            QTest.qWait(200)
            self.assertTrue(dialog._edit.text().endswith('file.txt'))
            self.keyClick(Qt.Key_Enter)

        self.openDialog(self._openDialog, inDialogFunc)

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_08(self):
        """ Open project """
        core.project().open(os.path.dirname(self.TEST_FILE_DIR))

        self.assertNotEqual(core.project().path(), self.TEST_FILE_DIR)

        def inDialogFunc(dialog):
            self.keyClicks('p ' + self.TEST_FILE_DIR)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(self._openDialog, inDialogFunc)

        self.assertEqual(core.project().path(), self.TEST_FILE_DIR)



if __name__ == '__main__':
    unittest.main()
