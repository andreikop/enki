# .. -*- coding: utf-8 -*-
#
# ************************************************************************
# test_importFail.py - Test ImportFail class
# ************************************************************************
# Typically for use in unit tests.
import unittest

from import_fail import ImportFail

# ImportFail tests
# ================
class TestImportFail(unittest.TestCase):
    def test_1(self):
        # Make sure ImportFail causes an exception for a fail_name.
        with self.assertRaises(ImportError):
            with ImportFail('re'):
                import re
        # Make sure the same name now works
        import re

    # Make sure import of other modules work.
    def test_2(self):
        with ImportFail('re'):
            import os


# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()