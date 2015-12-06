#!/usr/bin/env python3
# .. -*- coding: utf-8 -*-
#
# ************************************************************************
# test_importFail.py - Test ImportFail class
# ************************************************************************
#
# Imports
# =======
# Library imports
# ---------------
import sys
import os.path
import unittest
#
# Third-party library imports
# ---------------------------
from unittest.mock import patch, call
#
# Local imports
# -------------
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from import_fail import ImportFail
#
# ImportFail tests
# ================
class TestImportFail(unittest.TestCase):
    def test_1(self):
        """ Make sure ImportFail causes an exception for a fail_name.
        """
        with self.assertRaises(ImportError):
            with ImportFail(['re']):
                import re
        # Make sure the same name now works
        import re

    def test_2(self):
        """ Make sure ImportFail causes an exception for multiple fail_names.
        """
        with self.assertRaises(ImportError):
            with ImportFail(['os', 're']):
                import re
        # Make sure the same name now works
        import re

    def test_3(self):
        """Make sure import of other modules works.
        """
        with ImportFail(['re']):
            import os

    @patch('imp.reload')
    def test_4(self, _reload):
        """Check that reload isn't called if no modules are given."""
        with ImportFail(['re']):
            pass
        self.assertFalse(_reload.called)

    @patch('imp.reload')
    def test_5(self, _reload):
        """Check that reload is called twice."""
        with ImportFail(['re'], ['one', 'two']):
            pass
        _reload.assert_has_calls([call('one'), call('two'), call('one'), call('two')])

    @patch('imp.reload')
    def test_6(self, _reload):
        """Check that reload is called in the correct context."""
        class ImportTester(object):
            def __init__(self):
                # Save a list of success/failure of an import.
                self.import_success = []

            def try_import(self, *args, **kwargs):
                try:
                    import re
                    self.import_success += [True]
                except ImportError:
                    self.import_success += [False]

        it = ImportTester()
        _reload.side_effect = it.try_import
        with ImportFail(['re'], ['one']):
            pass
        self.assertEqual(it.import_success, [False, True])

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
