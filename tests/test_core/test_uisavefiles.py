#!/usr/bin/env python

import unittest
import os.path
import sys
import time

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtTest import QTest

from enki.core.core import core

class Test(base.TestCase):

    def _verifyText(self, fileName, text):
        with open(os.path.join(self.TEST_FILE_DIR, fileName)) as file_:
            actualText = file_.read()

        self.assertEqual(text, actualText)

    def test_1(self):
        # Close all, no modified files
        self.createFile('file1.rb', 'asdf\nfdsa')
        self.createFile('file2.rb', 'asdf\nfdsa')

        self.keyClick('Ctrl+Shift+W')

        self.assertIsNone(core.workspace().currentDocument())

    @base.inMainLoop
    def test_2(self):
        # Close all, do not save
        self.createFile('file1.rb', 'asdf\nfdsa')
        self.createFile('file2.rb', 'fdsa')

        self.keyClick('Ctrl+Enter')
        self.keyClicks('new text')

        self.openDialog(lambda: self.keyClick('Ctrl+Shift+W'),
                        lambda dialog: self.keyClick('w'))

        self.assertIsNone(core.workspace().currentDocument())
        self._verifyText('file2.rb', 'fdsa')

    @base.inMainLoop
    def test_3(self):
        # Close all, cancel close
        self.createFile('file1.rb', 'asdf\nfdsa')
        self.createFile('file2.rb', 'fdsa')

        self.keyClick('Ctrl+Enter')
        self.keyClicks('new text')

        self.openDialog(lambda: self.keyClick('Ctrl+Shift+W'),
                        lambda dialog: self.keyClick('c'))

        self.assertIsNotNone(core.workspace().currentDocument())

    @base.inMainLoop
    def test_4(self):
        # Close all, save
        self.createFile('file1.rb', 'asdf\nfdsa')
        self.createFile('file2.rb', 'fdsa')

        self.keyClick('Ctrl+Enter')
        self.keyClicks('new text+')

        self.openDialog(lambda: self.keyClick('Ctrl+Shift+W'),
                        lambda dialog: self.keyClick('s'))

        self.assertIsNone(core.workspace().currentDocument())

        self._verifyText('file2.rb', 'new text+fdsa\n')

    @base.inMainLoop
    def test_5(self):
        # Close all, reject save dialog
        self.createFile('file1.rb', 'asdf\nfdsa')
        self.createFile('file2.rb', 'fdsa')

        self.keyClick('Ctrl+N')  # file without name
        self.keyClicks('new text')  # but modified

        def inUiSaveFilesDialog(dialog):
            # open and reject save dialog for file without name
            def inSaveFileDialog(saveDialog):
                QTest.qWait(4000)
                self.keyClick('Esc')

            self.openDialog(lambda: self.keyClick('s'),
                            inSaveFileDialog)

        self.openDialog(lambda: self.keyClick('Ctrl+Shift+W'),
                        inUiSaveFilesDialog)

        self.assertIsNotNone(core.workspace().currentDocument())


if __name__ == '__main__':
    unittest.main()
