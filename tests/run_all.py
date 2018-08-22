#!/usr/bin/env python3
import unittest
import sys

# Import just to check that dependencies are installed
import markdown  # noqa: F401

if __name__ == "__main__":
    # Look for all tests. Using test_* instead of test_*.py finds modules (test_syntax and test_indenter).
    suite = unittest.TestLoader().discover('.', pattern="test_*")
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Indicate success or failure via the exit code: success = 0, failure = 1.
    sys.exit(not result.wasSuccessful())
