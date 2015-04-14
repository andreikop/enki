#!/usr/bin/env python

import unittest

import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".."))

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



if __name__ == '__main__':
    unittest.main()
