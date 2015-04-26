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
            self.keyClick(Qt.Key_Enter)

        self.openDialog(self._openDialog, inDialogFunc)

    def _openDialog(self):
        self.keyClicks('L', Qt.ControlModifier)

    @base.inMainLoop
    def test_1(self):
        """Go to line"""
        document = self.createFile('asdf.txt', 'a\n' * 10)
        self._execCommand('l 5')
        self.assertEqual(document.qutepart.cursorPosition[0], 4)

    @base.inMainLoop
    def test_2(self):
        """Open file, type only path"""
        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand(fullPath.replace('\\', '\\\\'))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_3(self):
        """Open file, type 'f path' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand('f ' + fullPath.replace('\\', '\\\\'))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_4(self):
        """Save file, create dirs"""
        document = core.workspace().createEmptyNotSavedDocument()
        document.qutepart.text = 'filetext'

        fullPath = os.path.join(self.TEST_FILE_DIR, 'dir1/dir2/thefile.txt')

        self._execCommand('s ' + fullPath.replace('\\', '\\\\'))

        with open(fullPath) as file_:
            data = file_.read()

        self.assertEqual(data, 'filetext\n')

    @base.inMainLoop
    def test_5(self):
        """Save file, relative path"""
        text = 'a\n' * 10
        document = self.createFile('asdf.txt', text)

        relPath = 'dir1/dir2/newfile.txt'

        self._execCommand('s ' + relPath)

        with open(relPath) as file_:
            data = file_.read()

        self.assertEqual(data, text)

    @base.inMainLoop
    def test_6(self):
        """Open file, type 'f path with spaces' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'the file.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand('f ' + fullPath.replace('\\', '\\\\').replace(' ', '\\ '))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_7(self):
        """ Check inline completion for file with spaces"""
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'the file.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        def inDialogFunc(dialog):
            self.keyClicks('f ' + self.TEST_FILE_DIR + '/the')
            QTest.qWait(200)
            self.assertEqual(core.locator()._edit.text(),
                             'f ' + fullPath.replace('\\', '\\\\').replace(' ', '\\ '))
            self.keyClick(Qt.Key_Escape)

        self.openDialog(self._openDialog, inDialogFunc)



if __name__ == '__main__':
    unittest.main()
