#!/usr/bin/env python

import unittest

import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".."))

# Import this to set the SIP API correctly. It is otherwise not used in these
# tests.
import base
from enki.core.locator import splitLine


class Test(unittest.TestCase):
    def test_1(self):
        """ Parse words
        """
        self.assertEqual(splitLine(''), [])
        self.assertEqual(splitLine(' '), [])
        self.assertEqual(splitLine('  '), [])
        self.assertEqual(splitLine('asdf'), [('asdf', 4)])
        self.assertEqual(splitLine('  asdf'), [('asdf', 6)])
        self.assertEqual(splitLine('  asdf  '), [('asdf', 6)])
        self.assertEqual(splitLine('asdf x yz'), [('asdf', 4), ('x', 6), ('yz', 9)])
        self.assertEqual(splitLine(' asdf x  yz    '), [('asdf', 5), ('x', 7), ('yz', 11)])
        self.assertEqual(splitLine('\\'), [('\\', 1)])
        self.assertEqual(splitLine('\\ '), [(' ', 2)])
        self.assertEqual(splitLine('\\\\'), [('\\', 2)])
        self.assertEqual(splitLine('\\x'), [('x', 2)])



if __name__ == '__main__':
    unittest.main()
