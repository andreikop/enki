#!/usr/bin/env python3

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QKeySequence


from enki.core.core import core
from enki.core.workspace import _UISaveFiles


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

    def test_3(self):
        # Close all, cancel close
        self.createFile('file1.rb', 'asdf\nfdsa')
        self.createFile('file2.rb', 'fdsa')

        self.keyClick('Ctrl+Enter')
        self.keyClicks('new text')

        self.openDialog(lambda: self.keyClick('Ctrl+Shift+W'),
                        lambda dialog: self.keyClick('c'))

        self.assertIsNotNone(core.workspace().currentDocument())

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

    def test_5(self):
        # Close all, reject save dialog
        self.createFile('file1.rb', 'asdf\nfdsa')
        self.createFile('file2.rb', 'fdsa')

        self.keyClick('Ctrl+N')  # file without name
        self.keyClicks('new text')  # but modified

        @classmethod
        def fakeSaveFile(*args):
            return None, None

        # Native file dialog hangs the test. Mock it
        oldSaveFileName, QFileDialog.getSaveFileName = QFileDialog.getSaveFileName, fakeSaveFile

        try:
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
        finally:
            QFileDialog.getSaveFileName = oldSaveFileName

    def test_6(self):
        """Test _firstLetterShortcut."""
        # To access this function, create a dummy document so we can pull
        # up its containing dialog.
        self.createFile('file1.rb', 'asdf\nfdsa')
        uis = _UISaveFiles(core.workspace(), core.workspace().documents())
        # Label one of the dialog buttons.
        s = uis._firstLetterShortcut(uis.buttonBox.Discard, 'Does &This work')

        self.assertEqual(s.key(), QKeySequence("T"))

if __name__ == '__main__':
    unittest.main()
