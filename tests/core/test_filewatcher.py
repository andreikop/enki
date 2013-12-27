#!/usr/bin/env python

import unittest
import os.path
import sys
import time

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

class Test(base.TestCase):
    CREATE_NOT_SAVED_DOCUMENT = False

    def setUp(self):
        base.TestCase.setUp(self)
        self._doc1 = self.createFile('file1.txt', 'asdf')
        self._doc2 = self.createFile('file2.txt', 'fdsa')

    def _sleep_and_check(self, sleep,
                        doc1_modified, doc1_removed,
                        doc2_modified, doc2_removed):
        self.sleepProcessEvents(sleep)
        self.assertEqual(self._doc1._externallyModified, doc1_modified)
        self.assertEqual(self._doc1._externallyRemoved, doc1_removed)
        self.assertEqual(self._doc2._externallyModified, doc2_modified)
        self.assertEqual(self._doc2._externallyRemoved, doc2_removed)

    @base.inMainLoop
    def test_1(self):
        # Modify file, than restore, than modify again
        with open(self._doc1.filePath(), 'w') as file_:
            file_.write('new text')
        self._sleep_and_check(0.1, True, False, False, False)

        with open(self._doc1.filePath(), 'w') as file_:
            file_.write('asdf')
        self._sleep_and_check(1, False, False, False, False)

        # modify again
        with open(self._doc1.filePath(), 'w') as file_:
            file_.write('new text')
        self._sleep_and_check(0.1, True, False, False, False)

    @base.inMainLoop
    def test_2(self):
        # Modify file, than restore, than modify again
        os.unlink(self._doc2.filePath())
        self._sleep_and_check(0.1, False, False, False, True)

        # restore
        with open(self._doc2.filePath(), 'w') as file_:
            file_.write('fdsa')
        self._sleep_and_check(1, False, False, False, False)

        # delete
        os.unlink(self._doc2.filePath())
        self._sleep_and_check(0.1, False, False, False, True)

        # restore, but with different contents
        with open(self._doc2.filePath(), 'w') as file_:
            file_.write('fdsaA')
        self._sleep_and_check(1, False, False, True, False)

    @base.inMainLoop
    def test_3(self):
        # valid state after normal save
        self._doc2.qutepart.text = 'new text'
        self._doc2.saveFile()
        self._sleep_and_check(0.1, False, False, False, False)

        with open(self._doc2.filePath(), 'w') as file_:
            file_.write('another new text')
        self._sleep_and_check(0.1, False, False, True, False)

        self._doc2.saveFile()
        self._sleep_and_check(0, False, False, False, False)

    @base.inMainLoop
    def test_4(self):
        # save instead of removed
        os.unlink(self._doc1.filePath())
        self._sleep_and_check(0.1, False, True, False, False)

        self._doc1.saveFile()
        self._sleep_and_check(0, False, False, False, False)

        os.unlink(self._doc1.filePath())
        self._sleep_and_check(0.1, False, True, False, False)

        self._doc1.saveFile()
        self._sleep_and_check(0, False, False, False, False)

if __name__ == '__main__':
    unittest.main()
