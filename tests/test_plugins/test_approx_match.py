#!/usr/bin/env python
# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of Enki.
#
#    Enki is free software: you can redistribute it and/or modify it under the
#    terms of the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option) any later
#    version.
#
#    Enki is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with
#    Enki.  If not, see <http://www.gnu.org/licenses/>.
#
# ***********************************
# test_approx_match.py - Unit testing
# ***********************************

# Imports
# =======
# Library imports
# ---------------
import unittest
import os.path
import sys

# Local application imports
# -------------------------
# Insert path to base before importing.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base
# Base will insert path to enki, so its modules that we want to test can now be
# imported.
from enki.plugins.preview.approx_match import findApproxTextInTarget as f
from enki.plugins.preview.approx_match import findApproxText as g
from enki.plugins.preview.approx_match import refineSearchResult as lcs
#
# Tests for findApproxText
# ==========================
class TestFindApproxText(unittest.TestCase):
    # Check that searchText strings aren't treated as regular expressions
    def test_1(self):
        mo, begin, end = g(searchText='.',
                           targetText='===.===')
        self.assertTrue(mo)
        self.assertEqual(begin, 3)
        self.assertEqual(end, 4)
#
# Tests for findApproxTextInTarget
# ================================
# Find a location in a source file based on a given location in the resulting html.
class TestApproxMatch(unittest.TestCase):
    # Show that we can match identical text.
    def test_1(self):
        index = f(searchAnchor = 2,
                  # Place searchAnchor between ``te`` and ``st``.
                  searchText = 'test',
                  targetText = 'test')
                  # The expected index is between ``te`` and ``st``.
        self.assertEqual(index, 2)

    # Show that we can match with a initial Python comment.
    def test_2(self):
        index = f(searchAnchor = 4,
                  # Place searchAnchor between ``# te`` and ``st``.
                  searchText = '# test',
                  targetText = 'test')
                  # The expected targetText index is between ``te`` and ``st``.
        self.assertEqual(index, 2)

    # Show that we can match with a initial C/C++ comment.
    def test_3(self):
        index = f(searchAnchor = 5,
                  # Place searchAnchor between ``// te`` and ``st``.
                  searchText = '// test',
                  targetText = 'test')
                  # The expected targetText index is between ``te`` and ``st``.
        self.assertEqual(index, 2)

    # Show that we can match at the end of a line.
    def test_4(self):
        index = f(searchAnchor = 4,
                  # Place searchAnchor between ``test`` and ``\ntest``.
                  searchText = 'test\ntest',
                  targetText = 'test\ntest')
                  # The expected targetText index is between ``test`` and ``\ntest``.
        self.assertEqual(index, 4)

    # Show that we can match at the end of a line with a Python comment.
    def test_5(self):
        index = f(searchAnchor = 6,
                  # Place searchAnchor between ``# test`` and ``\n# test``.
                  searchText = '# test\n# test',
                  targetText = 'test\ntest')
                  # The expected targetText index is between ``test`` and ``\ntest``.
        self.assertEqual(index, 4)

    # Test a specific failing case found during development.
    def test_6(self):
        index = f(searchAnchor = 73-34,
                  searchText = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                  targetText = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')
        self.assertEqual(index, 66-34)

    # Test LCS ability to match specific characters mixed with non-matching
    # characters.
    def test_7(self):
        index = f(searchAnchor = 9,
                  # Place searchAnchor between ``bqwc?xyza`` and ``ad``.
                  searchText = 'bqwc?xyzaad',
                  targetText = 'bwxyzcd')
                  # The expected targetText index is between ``bwxyz`` and ``d``.
        self.assertIn(index, (5, 6))

    # A swap of searchText and targetText from the previous test.
    def test_8(self):
        index = f(searchAnchor = 6,
                  # Place searchAnchor between ``bwxyzc`` and ``d``.
                  searchText = 'bwxyzcd',
                  targetText = 'bqwc?xyzaad')
                  # The expected targetText index is between ``bqwc?xyz`` and ``d``.
        self.assertIn(index, (8, 9, 10))

    # This is a typical multiple match case. It should therefore match any of the three abcd strings.
    def test_9(self):
        index = f(searchAnchor = 2,
                  # Place searchAnchor between ``abc`` and ``d``.
                  searchText = 'abcd',
                  targetText = 'xxabcdabcdabcdxxx')
        self.assertEqual(index, 4)

    # If the anchor is placed after the search string, test to see if a
    # correct target index can be found.
    def test_13(self):
        index = f(searchAnchor = 8,
                  # Place searchAnchor between ``\n\n\n\ntest`` and ``\n\n\n\n``.
                  searchText = '\n\n\n\ntest\n\n\n\n',
                  targetText = ' test    ')
                  # The expected targetText index is between ' test' and '    '.
                  #
                  # .. Note: ReST doesn't like whitespace after a literal block
                  #    start string. Instead of working around it, I've just
                  #    escaped it with a backslash.
        self.assertEqual(index, 5)

    # This test case is similar to previous one. But the correct targetText
    # index is 4 -- an invalid index into the targetText string, but a
    # correct search result (at the end of the targetText string).
    def test_14(self):
        index = f(searchAnchor = 8,
                  # Place searchAnchor between ``\n\n\n\ntest`` and ``\n\n\n\n``.
                  searchText = '\n\n\n\ntest\n\n\n\n',
                  targetText = 'test')
                  # The expected targetText index is between ``test`` and \``
                  # (an empty string).
        self.assertEqual(index, 4)

    # With this test case, all boundary conditions have been tested.
    def test_15(self):
        index = f(searchAnchor = 4,
                  # Place searchAnchor between ``test`` and \`` (an empty string).
                  searchText = 'test',
                  targetText = '\n\n\n\ntest\n\n\n\n')
                  # The expected targetText index is between ``\n\n\n\ntest`` and
                  # ``\n\n\n\n``.
        self.assertEqual(index, 8)

#
# Failing test casess
# -------------------
    # Scenario:
    #
    #   A click before the second ``head`` will bring the target anchor to
    #   the start of target text.
    #
    # Problem:
    #
    #   Since in search text, the chars inside ``<>`` denote a hyperlink,
    #   they will get deleted in target text. Clicking right before the
    #   second ``head`` should bring the target anchor to anywhere between
    #   ``head`` and ``tail``.
    #
    # Explanation:
    #
    #   The LCS algorithm find letters as close to the beginning of the string
    #   as possible. The X marks characters it chooses::
    #
    #     `head <http://head>`_ tail
    #              X      X       XX
    #
    #   It's found ``tail`` in parts of the hyperlink, so it places the target
    #   anchor between the found t and a at index 6.
    @unittest.expectedFailure
    def test_11(self):
        index = f(searchAnchor = 14,
                  # Place searchAnchor between ```head <http://`` and ``head>`_ tail``.
                  searchText = '`head <http://head>`_ tail',
                  targetText = 'head tail')
                  # The expected targetText index is between ``head t`` and ``ail``.
        self.assertEqual(index, 5)

    # Scenario:
    #
    #   A click between the second 'b' and second 'c' will bring the target
    #   anchor to the start of targetText.
    #
    # Problem:
    #
    #   More intuitive behavior would be placing the target anchor between
    #   ``ab`` and ``cd``.
    #
    # Explanation:
    #
    #   LCS again finds characters as close as possible to the beginning of the
    #   string. Again, X marks matched characters::
    #
    #     abcdabcdabcd
    #     XXXX
    #
    #   Therefore, the requested anchor is past the found characters, so LCS
    #   places the found target anchor at the end of the string at index 4.
    @unittest.expectedFailure
    def test_12(self):
        index = f(searchAnchor = 6,
                  # Place searchAnchor between ``abcdab`` and ``cdabcd``.
                  searchText = 'abcdabcdabcd',
                  targetText = 'abcd')
                  # The expected targetText index is between ``ab`` and ``cd``.
        self.assertEqual(index, 2)


# Tests for refineSearchResult
# ============================
class TestRefineSearchResult(unittest.TestCase):
    # Boundary conditions: empty search and target strings.
    def test_1(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = '',
                     targetText = '')[1]
        self.assertEqual(string, '')

    # Boundary conditions: empty target string.
    def test_2(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = 'abc',
                     targetText = '')[1]
        self.assertEqual(string, '')

    # Identical string match.
    def test_3(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = 'abc',
                     targetText = 'abc')[1]
        self.assertEqual(string, 'abc')

    # No match.
    def test_4(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = 'Fox',
                     targetText = 'Bear')[1]
        self.assertEqual(string, '')

    # Unicode test.
    def test_5(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = 'Fußball',
                     targetText = 'Football')[1]
        self.assertEqual(string, 'Fball')

    # Unicode test.
    def test_6(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = 'Niederösterreich',
                     targetText = 'Oberösterreich')[1]
        self.assertEqual(string, 'erösterreich')

    # Control charater test.
    def test_7(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = 'abc\ndef',
                     targetText = 'gh\nijkl')[1]
        self.assertEqual(string, '\n')

    # Real test cases. test_8 contains a long common substring.
    def test_8(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                     targetText = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')[1]
        self.assertEqual(string, 'The d user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')

    # This test contains mostly short common subseqence fragments. This will
    # cause long editing distance.
    def test_9(self):
        string = lcs(searchAnchor = 0,
                     returnLcsString = True,
                     searchText = 'age = None# `exclude_patterns# <http://sphinx-doc.org/config.html#confval-exclude_patterns>`_: List of# patterns, re',
                     targetText = 'for a list of supported languages.##language = None exclude_patterns: List of patterns, re')[1]
        self.assertEqual(string, 'a  o upte ngg.lnaexclude_patterns: List of patterns, re')

    # Bug during testing.
    def test_13(self):
        index = lcs(searchAnchor = 30,
                    returnLcsString = True,
                    # Place searchAnchor between ``| '`` and ``Text after block 1,2, and 3``.
                    searchText = '------------+-------------+\n' +
                                 '| Text after block 1,2, and 3   ',
                    targetText = """a 2

Bael 2
Coco 3 Cherry 3
Text after block 1,2, and 3""")[0]
                    # The expected targetText index is at the beginning of the
                    # line ``Text after block 1,2, and 3``.
        self.assertEqual(index, 28)

# Cases from comments in refineSearchResult
# -----------------------------------------
    # Case 1.
    def test_14(self):
        index = lcs(searchAnchor = 1,
                    returnLcsString = True,
                    # Place searchAnchor between ``a`` and ``b``.
                    searchText = 'ab',
                    targetText = 'a--b')[0]
                    # The expected targetText index is between ``a`` and ``b``.
        self.assertIn(index, (1, 2, 3))

    # Case 2a.
    def test_15(self):
        index = lcs(searchAnchor = 10,
                    returnLcsString = True,
                    # Place searchAnchor between ``Chapter 1:`` and
                    # ``Once upon a time``.
                    searchText = 'Chapter 1:Once upon a time',
                    targetText = ':---------Once upon a time')[0]
                    # The expected targetText index is between ``:---------``
                    # and ``Once upon a time``.
        self.assertEqual(index, 10)

    # Case 2b.
    def test_16(self):
        index = lcs(searchAnchor = 16,
                    returnLcsString = True,
                    # Place searchAnchor between ``Once upon a time`` and
                    # ``, there lived``.
                    searchText = 'Once upon a time, there lived',
                    targetText = 'Once upon a time------------,')[0]
                    # The expected targetText index is between
                    # ``Once upon a time`` and ``------------,``.
        self.assertEqual(index, 16)

    # Test LCS ability when the characters at the searchAnchor don't exist in
    # the targetText.
    def test_11(self):
        index = lcs(searchAnchor = 9,
                # Place searchAnchor between ``bqwc?xyza`` and ``ad``.
                searchText = 'bqwc?xyzaad',
                targetText = 'bwxyzcd')[0]
                # The expected targetText index is between ``bwxyzc`` and ``d``.
        self.assertIn(index, (5, 6))

    # A swap of searchText and targetText from the previous test.
    def test_12(self):
        index = lcs(searchAnchor = 6,
                # Place searchAnchor between ``bwxyzc`` and ``d``.
                searchText = 'bwxyzcd',
                targetText = 'bqwc?xyzaad')[0]
                # The expected targetText index is between ``bqwc?xyza`` and ``d``.
        self.assertIn(index, (8, 9, 10))
#
# Main
# ====
if __name__ == '__main__':
    unittest.main()
