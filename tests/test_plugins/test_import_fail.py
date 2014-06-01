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
import unittest

# Local imports
# -------------
from import_fail import ImportFail

# ImportFail tests
# ================
class TestImportFail(unittest.TestCase):
    def test_1(self):
        """ Make sure ImportFail causes an exception for a fail_name.
        """
        with self.assertRaises(ImportError):
            with ImportFail('re'):
                import re
        # Make sure the same name now works
        import re

    def test_2(self):
        """ Make sure ImportFail causes an exception for multiple fail_names.
        """
        with self.assertRaises(ImportError):
            with ImportFail('os', 're'):
                import re
        # Make sure the same name now works
        import re

    def test_3(self):
        """Make sure import of other modules works.
        """
        with ImportFail('re'):
            import os


# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
