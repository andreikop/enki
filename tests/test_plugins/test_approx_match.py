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
import copy

# Local application imports
# -------------------------
# Insert path to base before importing.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base

# Base will insert path to enki, so its modules that we want to test can now be imported.
from enki.plugins.preview.approx_match import findApproxTextInTarget as f
from enki.plugins.preview.approx_match import refineSearchResult as lcs

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

    # This is a typical multiple match case. It should therefore return a -1.
    def test_9(self):
        index = f(searchAnchor = 2,
                  # Place searchAnchor between ``abc`` and ``d``.
                  searchText = 'abcd',
                  targetText = 'xxabcdabcdabcdxxx')
        self.assertEqual(index, -1)

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

# Failing test casess
# -------------------
    # Scenario:
    #
    #   A click before the second ``head`` will bring the target anchor to
    #   the start of target text.
    #
    # Bug:
    #
    #   Since in search text, the chars inside ``<>`` denote a hyperlink,
    #   they will get deleted in target text. Clicking right before the
    #   second ``head`` should bring the target anchor to anywhere between
    #   ``head`` and ``tail``.
    #
    # Explanation:
    #
    #   This synthesis test case demonstrate the importance of ``searchRange``
    #   in ``approx_match.py``. A ``searchRange`` of 30 is applied before
    #   TRE is used. TRE returns with the string
    #   ``searchPattern = ' <http://---------------------head>`_ tail'`` and
    #   ``targetSubstring = 'head tail'``. Since ``searchPattern`` is not
    #   complete, the LCS algorithm cannot find the correct index.
    #
    # Note:
    #
    #   This problem cannot get bypassed simply by setting a larger
    #   ``searchRange``, as shown by the next test case.
    @unittest.expectedFailure
    def test_10(self):
        index = f(searchAnchor = 35,
                  # Place searchAnchor between ```head <http://---------------------'
                  # and 'head>`_ tail``.
                  searchText = '`head <http://---------------------head>`_ tail',
                  targetText = 'head tail')
                  # The expected targetText index is between ``head`` and ``tail``.
        self.assertIn(index, (4, 5))

    # Scenario:
    #
    #   This scenario is the same as the previous test case.
    #
    # Bug:
    #
    #   What should happen is same as the previous test case.
    #
    # Explanation:
    #
    #   The LCS algorithm input strings are:
    #   ``searchPattern = '`head <http://head>`_ tail'``,
    #   ``targetSubstring = 'head tail'``. Their longest common substring is
    #   ``'head tail'``. The next table demonstrate the mapping of the string
    #   produced by the LCS algorithm back to search pattern and target substring::
    #
    #     searchPattern  : `head <http://head>`_ tail
    #     anchor         :               ^
    #     targetSubstring:               head    tail
    #
    #     LCSString      :               head    tail
    #
    #   The LCS algorithm uses a backward matching method. Thus the word
    #   `head` in the LCS string result is matched to the second `head` word
    #   in the search pattern. Thus when matching the LCS string back to the
    #   target string, it is matched to the wrong place and generates an
    #   index of 0 instead of 4 or 5.
    #
    # Note:
    #
    #   One may debate that the backward searching approach should be
    #   replaced by a forward search in this case, but the lack of context
    #   cannot justify which searching direction can generate better result.
    #   The next test case demonstrates this.
    @unittest.expectedFailure
    def test_11(self):
        index = f(searchAnchor = 14,
                  # Place searchAnchor between ```head <http://`` and ``head>`_ tail``.
                  searchText = '`head <http://head>`_ tail',
                  targetText = 'head tail')
                  # The expected targetText index is between ``head`` and ``tail``.
        self.assertIn(index, (4, 5))

    # Scenario:
    #
    #   A click between the second 'b' and second 'c' will bring the target
    #   anchor to the start of targetText.
    #
    # Bug:
    #
    #   A lack of context causes ambiguity. We cannot determine how the
    #   matching is performed and thus cannot decide which matching is the
    #   optimal one. If the targetText is matched to the first 'abcd' in the
    #   searchText, then if searchAnchor is at index 6 it should map to
    #   index 4 in target string. If targetText is matched to the last
    #   'abcd' in the searchText, then the searchAnchor should map to index
    #   0 in target string. If targetText is matched to the middle 'abcd',
    #   then it should map to index 2.
    #
    # Explaination:
    #
    #   We use backward LCS matching, so the output should be 2, not 0, not 4.
    #
    # TODO:
    #
    #   Since in the conversion, forward conversion is more natural than
    #   backward conversion. The LCS mapping algorithm should provide a
    #   search direction parameter.
    @unittest.expectedFailure
    def test_12(self):
        index = f(searchAnchor = 6,
                  # Place searchAnchor between ``abcdab`` and ``cdabcd``.
                  searchText = 'abcdabcdabcd',
                  targetText = 'abcd')
                  # The expected targetText index is between ``abc`` and ``d``.
        self.assertEqual(index, 2)


# Tests for refineSearchResult
# ============================
class TestRefineSearchResult(unittest.TestCase):
    # Boundary conditions: empty search and target strings.
    def test_1(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = '',
                     targetSubstring = '')[1]
        self.assertEqual(string, '')

    # Boundary conditions: empty target string.
    def test_2(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'abc',
                     targetSubstring = '')[1]
        self.assertEqual(string, '')

    # Identical string match.
    def test_3(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'abc',
                     targetSubstring = 'abc')[1]
        self.assertEqual(string, 'abc')

    # No match.
    def test_4(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'Fox',
                     targetSubstring = 'Bear')[1]
        self.assertEqual(string, '')

    # Unicode test.
    def test_5(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'Fußball',
                     targetSubstring = 'Football')[1]
        self.assertEqual(string, 'Fball')

    # Unicode test.
    def test_6(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'Niederösterreich',
                     targetSubstring = 'Oberösterreich')[1]
        self.assertEqual(string, 'erösterreich')

    # Control charater test.
    def test_7(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'abc\ndef',
                     targetSubstring = 'gh\nijkl')[1]
        self.assertEqual(string, '\n')

    # Real test cases. test_8 contains a long common substring.
    def test_8(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                     targetSubstring = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')[1]
        self.assertEqual(string, 'The d user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')

    # This test contains mostly short common subseqence fragments. This will
    # cause long editing distance.
    def test_9(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'age = None# `exclude_patterns# <http://sphinx-doc.org/config.html#confval-exclude_patterns>`_: List of# patterns, re',
                     targetSubstring = 'for a list of supported languages.##language = None exclude_patterns: List of patterns, re')[1]
        self.assertEqual(string, 'a  o upte ngg.lnaexclude_patterns: List of patterns, re')

    # Test LCS ability when the characters at the searchAnchor don't exist in
    # the targetSubstring.
    def test_11(self):
        index = lcs(searchAnchor = 9,
                # Place searchAnchor between ``bqwc?xyza`` and ``ad``.
                searchPattern = 'bqwc?xyzaad',
                targetSubstring = 'bwxyzcd')[0]
                # The expected targetText index is between ``bwxyzc`` and ``d``.
        self.assertIn(index, (5, 6))

    # A swap of searchText and targetText from the previous test.
    def test_12(self):
        index = lcs(searchAnchor = 6,
                # Place searchAnchor between ``bwxyzc`` and ``d``.
                searchPattern = 'bwxyzcd',
                targetSubstring = 'bqwc?xyzaad')[0]
                # The expected targetText index is between ``bqwc?xyza`` and ``d``.
        self.assertIn(index, (8, 9, 10))

    # test_10 tests the performance when comparing two files. It takes about
    # 1 minute to run.
    @unittest.skip('Long-running performance test')
    def test_10(self):
        print os.getcwd()
        with open("D:\\enki\\tests\\test_plugins\\test_ApproxMatch.py", 'r') as file:
            searchPattern = file.read()
        targetSubstring = copy.deepcopy(searchPattern)
        string = lcs(0, searchPattern, targetSubstring)[1]
        self.assertEqual(string, searchPattern)


# Main
# ====
if __name__ == '__main__':
    unittest.main()
