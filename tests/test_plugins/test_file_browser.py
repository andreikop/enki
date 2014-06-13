#!/usr/bin/env python

import unittest
import os
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from enki.core.core import core


class Test(base.TestCase):
    def test_1(self):
        """ Restore path
        """
        path = os.path.abspath('../..')

        dock = self.findDock('&File Browser')
        dock._onVisibilityChanged(True)
        dock.setCurrentPath(path)

        core.term()
        core.init(base.DummyProfiler())
        dock = self.findDock('&File Browser')
        dock._onVisibilityChanged(True)

        self.assertEqual(dock.currentPath(), path)


if __name__ == '__main__':
    unittest.main()
