#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from enki.core.core import core
from enki.plugins.lint.settings_widget import _getPylintVersion

nullFile = '/dev/null' if os.name == 'posix' else 'nul'
err = os.system('pylint --version > {} 2>&1'.format(nullFile))
havePylint = (0 == err)

class Test(base.TestCase):
    @unittest.skipUnless(havePylint, 'Pylint not found')
    def test_1(self):
        """ File is checked after opened """
        doc = self.createFile('test.py', 'asdf\n\n')
        self.waitUntilPassed(2000, lambda: self.assertEqual(doc.qutepart.lintMarks, {0: ('e', "Undefined variable 'asdf'")}))
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), "Undefined variable 'asdf'")

        doc.qutepart.cursorPosition = ((1, 0))
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), "")

        doc.qutepart.cursorPosition = ((0, 1))
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), "Undefined variable 'asdf'")

        doc.qutepart.text = 'def main()\n    return 7'
        self.assertEqual(doc.qutepart.lintMarks, {})
        self.assertEqual(core.mainWindow().statusBar().currentMessage(), "")

        doc.saveFile()

        self.waitUntilPassed(2000, lambda: self.assertEqual(doc.qutepart.lintMarks, {0: ('e', 'invalid syntax')}))

    @unittest.skipUnless(havePylint, 'Pylint not found')
    def test_2(self):
        """ _getPylintVersion """
        version = _getPylintVersion('pylint')
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
                page.lePylintPath.setText(path)

            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

    def test_3(self):
        """ Settings """
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


if __name__ == '__main__':
    unittest.main()
