#!/usr/bin/env python3
# .. -*- coding: utf-8 -*-
#
# **********************************************************************
# test_preview_utils.py - Unit tests for utilities in the Preview module
# **********************************************************************
#
# Imports
# =======
# Library imports
# ---------------
import unittest
import os
import os.path
import sys
import stat

# Local application imports
# -------------------------
# Do this before PyQt imports so that base will set up sip API correctly.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

# Third-party library ihmports
# ---------------------------
from unittest.mock import patch

# Local application imports
# -------------------------
from enki.plugins.preview import commonPrefix
from enki.plugins.preview.preview import copyTemplateFile
from enki.plugins.preview import _getSphinxVersion


@unittest.skip('Crashes')
@unittest.skipIf('TRAVIS_OS_NAME' in os.environ, "Fails on Travis?")
class TestWithDummy(base.TestCase):

    def setUp(self):
        base.TestCase.setUp(self)
        self.createFile('dummy.txt', '')

    # Cases testing copyTemplateFile
    # ------------------------------
    # Basic checks
    # TODO: Do we need to modularize these test cases? It seems we have many
    # tunable parameters, yet all testcases look alike.
    def test_copyTemplateFile1(self):
        # copyTemplateFile has function header:
        # ``copyTemplateFile(errors, source, templateFileName, dest, newName=None)``
        # Basic test would be copy one ``file`` from one valid source directory
        # to a valid ``dest`` directory with no ``newName`` or ``error``.
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        copyTemplateFile(errors, source, 'dummy.txt', dest)
        self.assertEqual(errors, [])
        self.assertTrue(os.path.isfile(os.path.join(source, 'dummy.txt')))
        self.assertTrue(os.path.isfile(os.path.join(dest, 'dummy.txt')))

    def test_copyTemplateFile2(self):
        # Test invalid source directory.
        source = os.path.join(self.TEST_FILE_DIR, 'invalid')
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        copyTemplateFile(errors, source, 'missing.file', dest)
        self.assertNotEqual([x for x in errors[0] if x.startswith("[Errno 2] No such file or directory")], ())

    def test_copyTemplateFile2a(self):
        # Test empty source directory.
        source = None
        dest = os.path.join(self.TEST_FILE_DIR, 'sub')
        os.makedirs(dest)
        errors = []
        with self.assertRaisesRegex(OSError,
                                    "Input or output directory cannot be None"):
            copyTemplateFile(errors, source, 'missing.file', dest)

    def test_copyTemplateFile3(self):
        # Test invalid destination directory.
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        errors = []
        copyTemplateFile(errors, source, 'dummy.txt', dest)
        self.assertNotEqual([x for x in errors[0] if x.startswith("[Errno 2] No such file or directory")], ())

    def test_copyTemplateFile3a(self):
        # Test empty destination directory.
        source = self.TEST_FILE_DIR
        dest = None
        errors = []
        with self.assertRaisesRegex(OSError,
                                    "Input or output directory cannot be None"):
            copyTemplateFile(errors, source, 'dummy.txt', dest)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_copyTemplateFile4(self):
        # Make target directory read only, causing access error (*nix only since
        # NTFS does not have Write-only property)
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        # Make the source file write only
        mode = os.stat(os.path.join(source, 'dummy.txt'))[0]
        os.chmod(os.path.join(source, 'dummy.txt'), stat.S_IWRITE)
        copyTemplateFile(errors, source, 'dummy.txt', dest)
        # Restore source file's attribute
        os.chmod(os.path.join(source, 'dummy.txt'), mode)
        self.assertNotEqual([x for x in errors[0] if "Permission denied" in x], ())

    def test_copyTemplateFile5(self):
        # Test the fifth argument of copyTemplateFile: newName, that will alter
        # copied file's name.
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        copyTemplateFile(errors, source, 'dummy.txt', dest, 'newFile.name')
        self.assertEqual(errors, [])
        self.assertTrue(os.path.isfile(os.path.join(source, 'dummy.txt')))
        self.assertTrue(os.path.isfile(os.path.join(dest, 'newFile.name')))


@unittest.skip('Crashes')
class Test(base.TestCase):
    #  Tests for getSphinxVersion
    # -------------------------

    def test_getSphinxVersion1(self):
        """Check that _getSphinxVersion raises an exception if the binary isn't
        present."""
        with self.assertRaises(OSError):
            _getSphinxVersion('this_executable_does_not_exist')

    # For mocking, mock an item where it is used, not where it came from. See
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch and
    # http://www.toptal.com/python/an-introduction-to-mocking-in-python.
    @patch('enki.plugins.preview.get_console_output')
    def test_getSphinxVersion2(self, mock_gca):
        """Check that _getSphinxVersion raises an exception if the Sphinx
        version info isn't present."""
        mock_gca.return_value = ("stderr",
                                 "stdout - no version info here, sorry!")
        with self.assertRaises(ValueError):
            _getSphinxVersion('anything_since_replaced_by_mock')

    @patch('enki.plugins.preview.get_console_output')
    def test_getSphinxVersion3(self, mock_gca):
        """Check that _getSphinxVersion complies to sphinx version 1.1.3"""
        mock_gca.return_value = ("stderr",
                                 """Sphinx v1.1.3
Usage: C:\\Python27\\Scripts\\sphinx-build [options] sourcedir outdir [filenames...
]
""")
        self.assertEqual(_getSphinxVersion('anything_since_replaced_by_mock'),
                         [1, 1, 3])

    @patch('enki.plugins.preview.get_console_output')
    def test_getSphinxVersion4(self, mock_gca):
        """Check that _getSphinxVersion complies to sphinx version 1.2.3"""
        mock_gca.return_value = ("stderr",
                                 """Sphinx (sphinx-build) 1.2.3
""")
        self.assertEqual(_getSphinxVersion('anything_since_replaced_by_mock'),
                         [1, 2, 3])

    @patch('enki.plugins.preview.get_console_output')
    def test_getSphinxVersion5(self, mock_gca):
        """Check that _getSphinxVersion complies to sphinx version 1.3.1"""
        mock_gca.return_value = ("stdout",
                                 """Sphinx (sphinx-build) 1.3.1
""")
        self.assertEqual(_getSphinxVersion('anything_since_replaced_by_mock'),
                         [1, 3, 1])

    # Cases testing commonPrefix
    # --------------------------
    # Basic checks
    def test_commonPrefix1(self):
        self.assertEqual(commonPrefix('a', 'a'), 'a')

    def test_commonPrefix2(self):
        self.assertEqual(commonPrefix('a', 'b'), '')

    def test_commonPrefix3(self):
        self.assertEqual(commonPrefix('', 'a'), '')

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    # Test using various path separators.
    def test_commonPrefix5(self):
        self.assertEqual(commonPrefix('a\\b', 'a\\b'), os.path.join('a', 'b'))

    def test_commonPrefix6(self):
        self.assertEqual(commonPrefix('a/b', 'a/b'), os.path.join('a', 'b'))

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix7(self):
        self.assertEqual(commonPrefix('a/b', 'a\\b'), os.path.join('a', 'b'))

    # Check for the bug in os.path.commonprefix.
    def test_commonPrefix8(self):
        self.assertEqual(commonPrefix(os.path.join('a', 'bc'), os.path.join('a', 'b')), 'a')

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix9(self):
        self.assertEqual(commonPrefix('a\\b\\..', 'a\\b'), 'a')

    def test_commonPrefix9a(self):
        self.assertEqual(commonPrefix('a/b/..', 'a/b'), 'a')

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix10(self):
        self.assertEqual(commonPrefix('a\\.\\b', 'a\\b'), os.path.join('a', 'b'))

    def test_commonPrefix10a(self):
        self.assertEqual(commonPrefix('a/./b', 'a/b'), os.path.join('a', 'b'))

    def test_commonPrefix11(self):
        """Check that leading ../current_subdir will be removed after path
           clearnup."""
        # Get the name of the current directory
        d = os.path.basename(os.getcwd())
        self.assertEqual(commonPrefix('../' + d + '/a/b', 'a/b'), os.path.join('a', 'b'))

    def test_commonPrefix11a(self):
        # if any input directory is abs path, return abs commonprefix
        d1 = os.path.join(os.getcwd(), 'a1')
        self.assertEqual(commonPrefix(d1, 'a2'), os.path.normcase(os.getcwd()))

    # Test for paths with spaces (Windows version)
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix12(self):
        # Cases like this only applies to Windows. Since Unix separator
        # is not '\\' but '/'. Unix will treat '\\' as part of file name.
        self.assertEqual(commonPrefix('a a\\b b\\c c', 'a a\\b b'), os.path.join('a a', 'b b'))

    # Test for paths with spaces (Platform independent version)
    def test_commonPrefix12a(self):
        # Cases like this only applies to Windows. Since Unix separator
        # is not '\\' but '/'. Unix will treat '\\' as part of file name.
        self.assertEqual(commonPrefix(os.path.join('a a', 'b b', 'c c'),
                                      os.path.join('a a', 'b b')), os.path.join('a a', 'b b'))

    # Test for paths with different cases (Windows only)
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix13(self):
        self.assertEqual(commonPrefix('aa\\bb', 'Aa\\bB'), os.path.join('aa', 'bb'))

    def test_commonPrefix14(self):
        # Empty input list should generate empty result
        self.assertEqual(commonPrefix(), '')

    def test_commonPrefix15(self):
        # if current working directory is 'a/b', for ".." and "", what part is
        # the commonprefix? It should be an absolute path "a"
        self.assertEqual(commonPrefix('..', ''), os.path.normcase(os.path.dirname(os.getcwd())))

    def test_commonPrefix16(self):
        # commonPrefix use the assumption that all relativepaths are based on
        # current working directory. If the resulting common prefix does not
        # have current workign directory as one of its parent directories, then
        # the absolute path will be used.
        self.assertEqual(commonPrefix(os.path.join('..', 'AVeryLongFileName'),
                                      os.path.join('..', 'AVeryLongFileName')),
                         os.path.normcase(os.path.abspath(os.path.join('..', 'AVeryLongFileName'))))

    # TODO: need symbolic link test case.
#
# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main(verbosity=2)
