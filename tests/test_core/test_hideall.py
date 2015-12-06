#!/usr/bin/env python3

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtCore import Qt

from enki.core.core import core
from enki.widgets.dockwidget import DockWidget


class Test(base.TestCase):
    @base.inMainLoop
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
        self.keyClick(Qt.Key_Escape, Qt.ShiftModifier, core.mainWindow())
        self.assertTrue(all(states()))  # all hidden

        # restore
        self.keyClick(Qt.Key_Escape, Qt.ShiftModifier, core.mainWindow())
        self.assertTrue(originalStates, states())


if __name__ == '__main__':
    unittest.main()
