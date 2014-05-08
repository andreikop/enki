#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QAction
from PyQt4.QtTest import QTest

import enki.core.workspace
from enki.core.core import core



class Test(base.TestCase):
    def test_1(self):
        # Do not open same file twice
        doc = self.createFile('file1.rb', 'asdf\nfdsa')
        doc2 = core.workspace().openFile(doc.filePath())
        self.assertTrue(doc is doc2)



class OpenFail(base.TestCase):
    def _runTest(self, filePath, expectedTitle):
        def inDialog(dialog):
            self.assertEqual(dialog.windowTitle(), expectedTitle)
            self.keyClick('Enter')

        self.openDialog(lambda: core.workspace().openFile(filePath),
                        inDialog)

    def test_1(self):
        # Fail on not existing file
        self._runTest('not existing file', "Failed to stat the file")

    def test_2(self):
        # Not a file
        self._runTest('.', "Can not open a directory")

    def test_3(self):
        # Too big
        self.createFile('x', 'the text')

        oldMaxSize = enki.core.workspace._MAX_SUPPORTED_FILE_SIZE
        enki.core.workspace._MAX_SUPPORTED_FILE_SIZE = 3

        try:
            self._runTest('x', "Too big file")
        finally:
            enki.core.workspace._MAX_SUPPORTED_FILE_SIZE = oldMaxSize

    def test_4(self):
        # no access
        document = self.createFile('x', 'the text')
        core.workspace().closeDocument(document)

        os.chmod('x', 0)

        self._runTest('x', "Don't have the access")


class Loop(base.TestCase):
    #@base.inMainLoop
    def test_1(self):
        def func():
            a = QAction(core.workspace())
            core.actionManager().addAction('mFile/aAction', a)
            core.actionManager().removeAction('mFile/aAction')
            a.setParent(None)
            QTimer.singleShot(0, func)

        func()
        QTest.qWait(20 * 1000)

    def test_2(self):
        a = self.createFile('x', 'y')
        b = self.createFile('w', 'z')

        def func():
            core.workspace().setCurrentDocument(a)
            core.workspace().setCurrentDocument(b)
            QTimer.singleShot(0, func)

        func()
        QTest.qWait(20 * 1000)


if __name__ == '__main__':
    unittest.main()
