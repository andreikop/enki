#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from enki.core.core import core

import enki.core.core
import enki.core.defines


class RestoreOldConfigs(base.TestCase):
    INIT_CORE = False
    @unittest.skip("This test makes all others print lots of junk.")
    def test_1(self):
        # Enki restores configs from old directory ~/.enki to new ~/.config/enki
        old_cfg = enki.core.core._OLD_CONFIG_DIR
        curr_cfg = enki.core.defines.CONFIG_DIR

        enki.core.core._OLD_CONFIG_DIR = self.TEST_FILE_DIR + '/old'
        enki.core.defines.CONFIG_DIR = self.TEST_FILE_DIR + '/new'
        try:
            os.mkdir(enki.core.core._OLD_CONFIG_DIR)
            core.init(base.DummyProfiler())
            self.assertTrue(os.path.isdir(enki.core.defines.CONFIG_DIR))
            self.assertFalse(os.path.isdir(enki.core.core._OLD_CONFIG_DIR))
        finally:
            enki.core.core._OLD_CONFIG_DIR = old_cfg
            enki.core.defines.CONFIG_DIR = curr_cfg

    def xtest_2(self):
        # Enki shows QMessageBox if failed to move config dir
        old_cfg = enki.core.core._OLD_CONFIG_DIR
        curr_cfg = enki.core.defines.CONFIG_DIR

        enki.core.core._OLD_CONFIG_DIR = self.TEST_FILE_DIR + '/old'
        enki.core.defines.CONFIG_DIR = '/new'
        try:
            os.mkdir(enki.core.core._OLD_CONFIG_DIR)

            def inDialog(dialog):
                self.assertTrue(dialog.windowTitle().startswith('Failed to move configs'))
                dialog.accept()

            self.openDialog(lambda: core.init(base.DummyProfiler()), inDialog)
        finally:
            enki.core.core._OLD_CONFIG_DIR = old_cfg
            enki.core.defines.CONFIG_DIR = curr_cfg


if __name__ == '__main__':
    unittest.main()
