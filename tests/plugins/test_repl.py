#!/usr/bin/env python

import unittest
import os.path
import sys
import time

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtTest import QTest

from enki.core.core import core


class Test(base.TestCase):

    def _browserText(self, replName):
        term = self.findDock(replName + ' &Interpreter').widget()
        return term._browser.toPlainText()

    @base.requiresCmdlineUtility('scheme')
    @base.inMainLoop
    def test_1(self):
        # Scheme
        self.createFile('test.scm', '')
        self.keyClick('Ctrl+E')
        self.sleepProcessEvents(2)

    @base.requiresCmdlineUtility('sml -h')
    @base.inMainLoop
    def test_2(self):
        # SML
        self.createFile('test.sml', '1234 * 567;')
        self.keyClick('Ctrl+E')
        self.sleepProcessEvents(0.1)

        self.assertTrue('699678' in self._browserText('Standard ML'))

    @base.requiresCmdlineUtility('python -h')
    @base.inMainLoop
    def test_3(self):
        # Python
        self.createFile('test.py', 'print 1234 * 567\n')
        self.keyClick('Ctrl+E')
        self.sleepProcessEvents(0.1)

        self.assertTrue('699678' in self._browserText('Python'))




if __name__ == '__main__':
    unittest.main()
