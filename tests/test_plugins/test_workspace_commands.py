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

from enki.core.core import core


class Test(base.TestCase):
    def _execCommand(self, text):
        def openDialogFunc():
            self.keyClicks('L', Qt.ControlModifier)

        def inDialogFunc(dialog):
            self.keyClicks(text)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(openDialogFunc, inDialogFunc)


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

        self._execCommand(fullPath)

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_3(self):
        """Open file, type only 'f path' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand('f ' + fullPath)

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_4(self):
        """Save file, create dirs"""
        document = core.workspace().createEmptyNotSavedDocument()
        document.qutepart.text = 'filetext'

        fullPath = os.path.join(self.TEST_FILE_DIR, 'dir1/dir2/thefile.txt')

        self._execCommand('s ' + fullPath)

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


if __name__ == '__main__':
    unittest.main()
