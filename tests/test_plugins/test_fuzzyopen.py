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


PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'enki'))


class Test(base.TestCase):
    def _execCommand(self, text):
        def inDialogFunc(dialog):
            self.keyClicks(text)
            print dialog._edit.text()
            self.keyClick(Qt.Key_Enter)

        self.openDialog(self._openDialog, inDialogFunc)

    def _openDialog(self):
        self.keyClicks('L', Qt.ControlModifier)

    def _waitFiles(self):
        for _ in range(20):
            QTest.qWait(5000 / 20)
            if core.project().files() is not None:
                break
        else:
            self.fail("Project not scanned")

    @base.inMainLoop
    def test_01(self):
        """ Open core.py (first choice) """
        core.project().open(PROJ_ROOT)  # not scanned yet

        def inDialogFunc(dialog):
            self.keyClicks('cowo')
            self._waitFiles()
            self.keyClick(Qt.Key_Enter)

        self.openDialog(self._openDialog, inDialogFunc)

        path = os.path.join(PROJ_ROOT, 'core', 'workspace.py')
        self.assertEqual(core.workspace().currentDocument().filePath(), path)

    @base.inMainLoop
    def test_02(self):
        """ Open mainwindow.py (second choice) """
        core.project().open(PROJ_ROOT)  # not scanned yet

        def inDialogFunc(dialog):
            self.keyClicks('cowo')
            self._waitFiles()
            self.keyClick(Qt.Key_Down)
            self.keyClick(Qt.Key_Enter)

        self.openDialog(self._openDialog, inDialogFunc)

        path = os.path.join(PROJ_ROOT, 'core', 'mainwindow.py')
        self.assertEqual(core.workspace().currentDocument().filePath(), path)


if __name__ == '__main__':
    unittest.main()
