#!/usr/bin/env python

import unittest
import os.path
import sys
import time

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from enki.core.core import core

class Test(base.TestCase):
    CREATE_NOT_SAVED_DOCUMENT = False
    
    def test_1(self):
        # By name
        doc = self.createFile('file1.rb', 'asdf')
        self.assertEqual(doc.qutepart.language(), 'Ruby')

    def test_2(self):
        # By first line
        doc = self.createFile('file2', '#!/bin/sh\necho')
        self.assertEqual(doc.qutepart.language(), 'Bash')

    def test_3(self):
        # After saved
        doc = self.createFile('file3', '')
        self.assertEqual(doc.qutepart.language(), None)
        doc.qutepart.text = '#!/bin/sh\necho'
        doc.saveFile()
        self.assertEqual(doc.qutepart.language(), 'Bash')

    def test_4(self):
        # Do not highlight huge files
        doc = self.createFile('file4.rb', 'x\n' * (101 * 1000))
        self.assertEqual(doc.qutepart.language(), None)

    def test_5(self):
        # Do not disable highlighting for files, which became huge
        longText = 'x\n' * (55 * 1000)
        doc = self.createFile('file4.rb', longText)
        self.assertEqual(doc.qutepart.language(), 'Ruby')
        doc.qutepart.text = longText * 2
        doc.saveFile()
        self.assertEqual(doc.qutepart.language(), 'Ruby')


if __name__ == '__main__':
    unittest.main()
