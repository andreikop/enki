#!/usr/bin/env python3

import unittest

import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".."))

# Import this to set the SIP API correctly. It is otherwise not used in these
# tests.
import base

from enki.core.core import core


PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'enki'))


class Test(base.TestCase):

    def test_1(self):
        """ Parse words
        """
        proj = core.project()

        self.assertEqual(proj.files(), None)

        proj.open(PROJ_ROOT)
        self.assertEqual(proj.path(), PROJ_ROOT)
        self.assertEqual(proj.files(), None)

        proj.startLoadingFiles()
        proj.startLoadingFiles()
        proj.cancelLoadingFiles()
        proj.cancelLoadingFiles()
        self.assertEqual(proj.files(), None)

        proj.startLoadingFiles()
        self.waitUntilPassed(5000, lambda: self.assertIsNotNone(proj.files()))

        corepy = [path for path in proj.files() if path.endswith('core.py')]
        self.assertEqual(len(corepy), 1)

        newPath = os.path.dirname(PROJ_ROOT)
        proj.open(newPath)
        self.assertEqual(proj.path(), newPath)
        self.assertEqual(proj.files(), None)


if __name__ == '__main__':
    unittest.main()
