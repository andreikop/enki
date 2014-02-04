#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from enki.core.core import core

class Test(base.TestCase):
    def test_1(self):
        # Do not open same file twice
        doc = self.createFile('file1.rb', 'asdf\nfdsa')
        doc2 = core.workspace().openFile(doc.filePath())
        self.assertTrue(doc is doc2)

if __name__ == '__main__':
    unittest.main()
