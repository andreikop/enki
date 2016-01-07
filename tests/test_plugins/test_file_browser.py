#!/usr/bin/env python3

import unittest
import os
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from enki.core.core import core


class Test(base.TestCase):

    def test_1(self):
        """ Init with current document path
        """
        path = os.path.abspath('../..')

        dock = self.findDock('&File Browser')
        dock._onVisibilityChanged(True)
        dock.setCurrentPath(path)

        core.term()
        core.init(base.DummyProfiler(), {'session_name': ''})
        dock = self.findDock('&File Browser')
        dock._onVisibilityChanged(True)

        # We can't simply do ``dock.currentPath() == path`` because of
        # Windows fun: ``u'C:/Users/bjones/AppData/Local' != 'c:\\users\\bjones\\appdata\\local'``.
        # We can't use ``os.path.samefile()`` because that's available only on
        # Unix for Python 2.7. So, use normpath and normcase per
        # http://stackoverflow.com/questions/21158667/comparing-two-paths-in-python.
        self.assertEqual(normpathcase(dock.currentPath()), normpathcase(self.TEST_FILE_DIR))


def normpathcase(path):
    """A helper function to normalize the path and case of a given path a.
    """
    return os.path.normpath(os.path.normcase(path))


if __name__ == '__main__':
    base.main()
