#!/usr/bin/env python3
import unittest


# Import just to check that dependencies are installed
import markdown
import docutils
import regex

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    # Look for all tests. Using test_* instead of test_*.py finds modules (test_syntax and test_indenter).
    suite = unittest.TestLoader().discover('.', pattern="test_*")

    QTimer.singleShot(0, lambda: unittest.TextTestRunner(verbosity=2).run(suite))
    QApplication.instance().exec_()
