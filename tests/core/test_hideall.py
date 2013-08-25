#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from enki.core.core import core
from enki.widgets.dockwidget import DockWidget


class Test(base.TestCase):
    @base.in_main_loop
    def test_1(self):
        
        docks = core.mainWindow().findChildren(DockWidget)
        
        for index, dock in enumerate(docks):
            if index % 2:
                dock.hide()
            else:
                dock.show()
        
        def states():
            return [dock.isHidden() for dock in docks]
        
        originalStates = states()
        
        # hide
        QTest.keyClick(core.mainWindow(), Qt.Key_Escape, Qt.ShiftModifier)
        self.assertTrue(all(states()))  # all hidden
        
        # restore
        QTest.keyClick(core.mainWindow(), Qt.Key_Escape, Qt.ShiftModifier)
        self.assertTrue(originalStates, states())


if __name__ == '__main__':
    unittest.main()
