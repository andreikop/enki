#!/usr/bin/env python3

"""Tests for workspace_actions plugin functionality
"""

import unittest
import os.path
import os
import sys


sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base  # configures sys.path ans sip

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from enki.core.core import core


PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'enki'))


class Test(base.TestCase):

    def _execCommand(self, text):
        self._openDialog()

        self.keyClicks(text)
        QTest.qWait(150)
        self.keyClick(Qt.Key_Enter)

    def _openDialog(self):
        self.keyClicks('L', Qt.ControlModifier)
        return self.waitDialog()

    def test_01(self):
        """Go to line"""
        document = self.createFile('asdf.txt', 'a\n' * 10)
        self._execCommand('l 5')
        self.assertEqual(document.qutepart.cursorPosition[0], 4)

    def test_02(self):
        """Open file, type only path"""
        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand(fullPath.replace('\\', '\\\\'))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    def test_03(self):
        """Open file, type 'f path' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'thefile.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand('o ' + fullPath.replace('\\', '\\\\'))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    def test_04(self):
        """Save file, create dirs"""
        document = core.workspace().createEmptyNotSavedDocument()
        document.qutepart.text = 'filetext'

        fullPath = os.path.join(self.TEST_FILE_DIR, 'dir1/dir2/thefile.txt')

        self._execCommand('s ' + fullPath.replace('\\', '\\\\'))

        with open(fullPath) as file_:
            data = file_.read()

        self.assertEqual(data, 'filetext\n')

    def test_05(self):
        """Save file, relative path"""
        text = 'a\n' * 10
        document = self.createFile('asdf.txt', text)

        relPath = 'dir1/dir2/newfile.txt'

        self._execCommand('s ' + relPath)

        with open(relPath) as file_:
            data = file_.read()

        self.assertEqual(data, text)

    def test_06(self):
        """Open file, type 'f path with spaces' """
        document = core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'the file.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        self._execCommand('o ' + fullPath.replace('\\', '\\\\').replace(' ', '\\ '))

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    def test_07(self):
        """ Check inline completion for file with spaces"""
        core.workspace().createEmptyNotSavedDocument()

        fullPath = os.path.join(self.TEST_FILE_DIR, 'the file.txt')

        with open(fullPath, 'w') as file_:
            file_.write('thedata')

        dialog = self._openDialog()
        cmdPath = (self.TEST_FILE_DIR + '/the').replace('\\', '\\\\').replace(' ', '\\ ')
        self.keyClicks('o ' + cmdPath)
        QTest.qWait(200)
        self.assertTrue(dialog._edit.text().endswith('file.txt'))
        self.keyClick(Qt.Key_Enter)

        self.assertEqual(core.workspace().currentDocument().filePath(), fullPath)

    def test_08(self):
        """ Open project """
        core.project().open(os.path.dirname(self.TEST_FILE_DIR))

        self.assertNotEqual(core.project().path(), self.TEST_FILE_DIR)

        self._openDialog()

        self.keyClicks('p ' + self.TEST_FILE_DIR.replace('\\', '\\\\'))
        self.keyClick(Qt.Key_Enter)

        self.assertEqual(core.project().path(), self.TEST_FILE_DIR)

    def test_09(self):
        """ Open .. """
        core.project().open(PROJ_ROOT)

        self._openDialog()
        self.keyClicks('p ..')
        self.keyClick(Qt.Key_Enter)
        self.assertEqual(core.project().path(), os.path.dirname(PROJ_ROOT))

    def test_10(self):
        """ Open ./ """
        core.project().open(PROJ_ROOT)

        self._openDialog()
        self.keyClicks('p ./core')
        self.keyClick(Qt.Key_Enter)
        self.assertEqual(core.project().path(), os.path.join(PROJ_ROOT, 'core'))


if __name__ == '__main__':
    base.main()
