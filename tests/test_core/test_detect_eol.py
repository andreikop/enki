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
        # Autodetect \n
        doc = self.createFile('file1.rb', 'asdf\nfdsa')
        self.assertEqual(doc.qutepart.eol, '\n')

    def test_2(self):
        # Autodetect \r
        doc = self.createFile('file1.rb', 'asdf\rfdsa')
        self.assertEqual(doc.qutepart.eol, '\r')

    def test_3(self):
        # Autodetect \r\n
        doc = self.createFile('file1.rb', 'asdf\r\nfdsa')
        self.assertEqual(doc.qutepart.eol, '\r\n')

    def test_4(self):
        # Mix, use default
        doc = self.createFile('file1.rb', 'asdf\r\nfdsa\rxxx')
        self.assertEqual(doc.qutepart.eol, '\n')

    def test_5(self):
        # No autodetect, use default
        core.config()["Qutepart"]["EOL"]["AutoDetect"] = False
        doc = self.createFile('file1.rb', 'asdf\r\nfdsa')
        self.assertEqual(doc.qutepart.eol, '\n')


if __name__ == '__main__':
    unittest.main()
