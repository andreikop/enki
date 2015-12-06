#!/usr/bin/env python3

import unittest

import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".."))

# Import this to set the SIP API correctly. It is otherwise not used in these
# tests.
from enki.core.locator import splitLine


class Test(unittest.TestCase):
    def test_1(self):
        """ Parse words
        """
        self.assertEqual(splitLine(''), [])
        self.assertEqual(splitLine(' '), [])
        self.assertEqual(splitLine('  '), [])
        self.assertEqual(splitLine('asdf'), ['asdf'])
        self.assertEqual(splitLine('  asdf'), ['asdf'])
        self.assertEqual(splitLine('  asdf  '), ['asdf'])
        self.assertEqual(splitLine('asdf x yz'), ['asdf', 'x', 'yz'])
        self.assertEqual(splitLine(' asdf x  yz    '), ['asdf', 'x', 'yz'])
        self.assertEqual(splitLine('\\'), ['\\'])
        self.assertEqual(splitLine('\\ '), [' '])
        self.assertEqual(splitLine('\\\\'), ['\\'])
        self.assertEqual(splitLine('\\x'), ['x'])


if __name__ == '__main__':
    unittest.main()
