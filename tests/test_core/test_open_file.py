#!/usr/bin/env python3

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base

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

        # On Windows (possibly Unix -- not tested), the file x below cannot be
        # erased after the chmod, making future tests using x fail. So, be sure
        # to chmod it back to the old permissions after the test runs. Note that,
        # per the `stat docs <https://docs.python.org/2/library/os.html#os.stat>`_,
        # stat returns lots of info; the only thing we care about is the file
        # permissions in st_mode, which `chmod
        # <https://docs.python.org/2/library/os.html#os.chmod>`_ uses.
        s = os.stat('x').st_mode
        try:
            os.chmod('x', 0)
            self._runTest('x', "Don't have the access")
        finally:
            os.chmod('x', s)


if __name__ == '__main__':
    unittest.main()
