#!/usr/bin/env python

"""Tests for workspace_actions plugin functionality
"""

import unittest
import os.path
import os
import sys
import stat

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base  # configures sys.path ans sip

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from enki.core.core import core


class Test(base.TestCase):
    @base.inMainLoop
    def xtest_1(self):
        """Go to line"""
        document = self.createFile('asdf.txt', 'a\n' * 10)

        def openDialogFunc():
            self.keyClicks('L', Qt.ControlModifier)

        def inDialogFunc(dialog):
            self.keyClicks('5')
            self.keyClick(Qt.Key_Enter)

        self.openDialog(openDialogFunc, inDialogFunc)

        self.assertEqual(document.qutepart.cursorPosition[0], 4)

    @base.inMainLoop
    def xtest_2(self):
        """Open file, type only path"""
        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        def openDialogFunc():
            self.keyClicks('L', Qt.ControlModifier)

        def inDialogFunc(dialog):
            self.keyClicks(fullPath)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(openDialogFunc, inDialogFunc)

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_3(self):
        """Open file, type only 'f path' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        def openDialogFunc():
            self.keyClicks('L', Qt.ControlModifier)

        def inDialogFunc(dialog):
            self.keyClicks('f ' + fullPath)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(openDialogFunc, inDialogFunc)

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    @base.inMainLoop
    def test_4(self):
        """Save file, create dirs"""
        document = core.workspace().createEmptyNotSavedDocument()
        document.qutepart.text = 'filetext'

        fullPath = os.path.join(self.TEST_FILE_DIR, 'dir1/dir2/thefile.txt')

        def openDialogFunc():
            self.keyClicks('L', Qt.ControlModifier)

        def inDialogFunc(dialog):
            self.keyClicks('s ' + fullPath)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(openDialogFunc, inDialogFunc)

        with open(fullPath) as file_:
            data = file_.read()

        self.assertEqual(data, 'filetext\n')

    @base.inMainLoop
    def test_5(self):
        """Save file, relative path"""
        text = 'a\n' * 10
        document = self.createFile('asdf.txt', text)

        relPath = 'dir1/dir2/newfile.txt'

        def openDialogFunc():
            self.keyClicks('L', Qt.ControlModifier)

        def inDialogFunc(dialog):
            self.keyClicks('s ' + relPath)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(openDialogFunc, inDialogFunc)

        with open(relPath) as file_:
            data = file_.read()

        self.assertEqual(data, text)


if __name__ == '__main__':
    unittest.main()
