#!/usr/bin/env python3

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from enki.core.core import core
from enki.plugins.lint.settings_widget import _getFlake8Version


class Test(base.TestCase):

    @base.requiresCmdlineUtility('flake8 --version')
    def test_1(self):
        """ File is checked after opened """
        doc = self.createFile('te:st .py', 'asdf\n\n')
        self.waitUntilPassed(2000, lambda: self.assertEqual(doc.qutepart.lintMarks,
                                                            {0: ('e', "F821 undefined name 'asdf'"),
                                                             1: ('w', 'W391 blank line at end of file')}))
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), "F821 undefined name 'asdf'")

        doc.qutepart.cursorPosition = ((1, 0))
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), 'W391 blank line at end of file')

        doc.qutepart.cursorPosition = ((0, 1))
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), "F821 undefined name 'asdf'")

        doc.qutepart.text = 'def main()\n    return 7'
        self.assertEqual(doc.qutepart.lintMarks, {})
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), "")

        doc.saveFile()

        self.waitUntilPassed(2000, lambda: self.assertEqual(doc.qutepart.lintMarks,
                                                            {0: ('e', 'E901 SyntaxError: invalid syntax'),
                                                             1: ('w', 'E113 unexpected indentation')}))

    @base.requiresCmdlineUtility('flake8 --version')
    def test_2(self):
        """ _getFlake8Version """
        version = _getFlake8Version('flake8')
        self.assertIsInstance(version, list)
        self.assertEqual(len(version), 3)

    def _setSettings(self, enabled=None, path=None, checkedRb=None):
        def continueFunc(dialog):
            page = dialog._pageForItem["Lint/Python"]

            if enabled is not None:
                page.gbEnabled.setChecked(enabled)

            if checkedRb is not None:
                getattr(page, checkedRb).setChecked(True)

            if path is not None:
                page.leFlake8Path.setText(path)

            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

    def test_3(self):
        """ Settings widget """
        self._setSettings(enabled=False, path='newlint', checkedRb='rbErrors')

        self.assertEqual(core.config().get('Lint/Python/Enabled'), False)
        self.assertEqual(core.config().get('Lint/Python/Show'), 'errors')
        self.assertEqual(core.config().get('Lint/Python/Path'), 'newlint')

        self._setSettings(checkedRb='rbErrorsAndWarnings')
        self.assertEqual(core.config().get('Lint/Python/Show'), 'errorsAndWarnings')

        self._setSettings(checkedRb='rbAll')
        self.assertEqual(core.config().get('Lint/Python/Show'), 'all')

        self._setSettings(enabled=True)
        self.assertEqual(core.config().get('Lint/Python/Enabled'), True)

    def test_4(self):
        """ Settings are applied """
        doc = self.createFile('test.py', 'asdf\n\n')
        self.waitUntilPassed(2000, lambda: self.assertEqual(doc.qutepart.lintMarks,
                                                            {0: ('e', "F821 undefined name 'asdf'"),
                                                             1: ('w', 'W391 blank line at end of file')}))

        core.config().set('Lint/Python/IgnoredMessages', 'F821 W391')
        doc.qutepart.text += ' '
        doc.saveFile()

        self.waitUntilPassed(2000, lambda: self.assertEqual(doc.qutepart.lintMarks,
                                                            {1: ('w', 'W293 blank line contains whitespace')}))


if __name__ == '__main__':
    unittest.main()
