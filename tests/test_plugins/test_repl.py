#!/usr/bin/env python3
# .. -*- coding: utf-8 -*-

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtTest import QTest


class Test(base.TestCase):

    def _browserText(self, replName):
        term = self.findDock(replName + ' &Interpreter').widget()
        return term._browser.toPlainText()

    def _waitForText(self, text, replName):
        for i in range(50):
            if text in self._browserText(replName):
                break
            else:
                QTest.qWait(100)
        else:
            self.fail("Text doesn't contain '{}'".format(text))

    @base.requiresCmdlineUtility('scheme')
    def test_1(self):
        """ Scheme """
        return  # TODO
        self.createFile('test.scm', '(+ 17 10)')
        self.keyClick('Ctrl+E')
        self._waitForText('27', 'MIT Scheme')

    @base.requiresCmdlineUtility('sml -h')
    def test_2(self):
        """ SML """
        self.createFile('test.sml', '1234 * 567;')
        self.keyClick('Ctrl+E')

        self._waitForText('699678', 'Standard ML')

    @base.requiresCmdlineUtility('python -h')
    def test_3(self):
        """ Python """
        self.createFile('test.py', 'print(1234 * 567)\n')
        self.keyClick('Ctrl+E')

        self._waitForText('699678', 'Python')

    @base.requiresCmdlineUtility('python -h')
    def test_4(self):
        """ Python, execute a function """
        self.createFile('test.py', 'def mysum(a, b):\n\n  return a + b\n')
        self.keyClick('Ctrl+E')
        self.keyClick('Alt+I')
        self.keyClicks('mysum(77000, 13)')
        self.keyClick('Enter')

        self._waitForText('77013', 'Python')

    @unittest.skipIf(sys.platform.startswith("win"), "Has Windows encoding problems")
    # Specifically, running this test (and lengthening the qWait delay to allow
    # more time for user interaction) then typing "1" or any other character
    # produces the following output::
    #
    #    python -i C:\Users\bjones\AppData\Local\Temp\enki-tests\test.py
    #    hello
    #    >>> 1
    #    Traceback (most recent call last):
    #      File "C:\Users\bjones\AppData\Local\Temp\enki-tests\test.py", line 3, in <module>
    #        print("\u041f\u0440\u0438\u0432\u0435\u0442")
    #      File "C:\Users\bjones\Downloads\WinPython-64bit-3.4.3.7Qt5\python-3.4.3.amd64\lib\encodings\cp1252.py", line 19, in encode
    #        return codecs.charmap_encode(input,self.errors,encoding_table)[0]
    #    UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-5: character maps to <undefined>
    #    1
    #    >>>
    #
    # This doesn't happen when testing interactively, which suggests that
    # unittest somehow changes the encoding to cp-1252 on Windows. I don't know
    # how to fix this, so this test is skipped.
    @base.requiresCmdlineUtility('python -h')
    def test_5(self):
        """ print unicode """
        self.createFile('test.py', '# -*- coding: utf-8 -*-\nprint("Привет")\n')
        self.keyClick('Ctrl+E')

        self._waitForText('Привет', 'Python')


if __name__ == '__main__':
    unittest.main()
