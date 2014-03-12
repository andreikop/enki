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

import unittest
import os.path
import sys


# Insert path to base before importing.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base
# Base will insert path to enki, so its modules that we want to test can now be imported.
from enki.plugins.preview.approx_match import findApproxTextInTarget as f

# Find a location in a source file based on a given location in the resulting html.
class TestApproxMatch(base.TestCase):
    # Show that we can match identical text
    def test_1(self):
        index = f(searchAnchor = 2,
                  searchText = 'test',
                  targetText = 'test')
        self.assertEqual(index, 2)

    # Show that we can match with a initial Python comment
    def test_2(self):
        index = f(searchAnchor = 4,
                  searchText = '# test',
                  targetText = 'test')
        self.assertEqual(index, 2)

    # Show that we can match with a initial C/C++ comment
    def test_3(self):
        index = f(searchAnchor = 5,
                  searchText = '// test',
                  targetText = 'test')
        self.assertEqual(index, 2)

    # Show that we can match at the end of a line
    def test_4(self):
        index = f(searchAnchor = 4,
                  searchText = 'test\ntest',
                  targetText = 'test\ntest')
        self.assertEqual(index, 4)

    # Show that we can match at the end of a line with a Python comment
    def test_5(self):
        index = f(searchAnchor = 6,
                  searchText = '# test\n# test',
                  targetText = 'test\ntest')
        self.assertEqual(index, 4)

    def test_6(self):
        index = f(searchAnchor = 73-34,
                  searchText = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                  targetText = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')
        self.assertEqual(index, 66-34)

    def test_7(self):
        index = f(searchAnchor = 9,
                  searchText = 'bqwc?xyzaad',
                  targetText = 'bwxyzcd')
        self.assertEqual(index, 6)

    def test_8(self):
        index = f(searchAnchor = 6,
                  searchText = 'bwxyzcd',
                  targetText = 'bqwc?xyzaad')
        self.assertIn(index, (9,10))

    def test_9(self):
        index = f(searchAnchor = 2,
                  searchText = 'abcd',
                  targetText = 'xxabcdabcdabcdxxx')
        # This is a typical multiple match case. will return a -1
        ##self.assertIn(index, (4,8,12))
        self.assertEqual(index, -1)

    # failed test case:
    def test_10(self):
        index = f(searchAnchor = 35,
                  searchText = '`head <http://---------------------head>`_ tail',
                  targetText = 'head tail')
        # Scenario: 
        #
        #   Click before the second `head` will bring target anchor to the start of target text.
        #
        # Bug: 
        #
        #   Since in search text, the chars inside bracket denote a hyperlink, they will get deleted in target text. 
        #   Click right before the second `head` should bring target anchor to anywhere between `head` and `tail`.
        #
        # Explaination:
        #
        #   This synthesis test case demonstrate the importance of `searchRange` in `approx_match.py`. A `searchRange` of 30 is 
        #   applied before TRE is used. TRE returned with ``searchPattern = ' <http://---------------------head>`_ tail'`` and 
        #   ``targetSubstring = 'head tail'``. Since `searchPattern` is not complete, LCS algorithm cannot find a correct index.
        #
        # Note:
        #
        #   This problem cannot get bypassed simply by setting a larger ``searchRange``. Please refer to the next test case.
        ## self.assertIn(index, (4, 5))

    @unittest.expectedFailure
    def test_11(self):
        index = f(searchAnchor = 14,
                  searchText = '`head <http://head>`_ tail',
                  targetText = 'head tail')
        # Scenario:
        #
        #   This scenario is the same as the previous one.
        #
        # Bug:
        #
        #   What should happen is same as the previous scenario.
        #
        # Explaination:
        #
        #   LCS algorithm input strings are: ``searchPattern = '`head <http://head>`_ tail'``, ``targetSubstring = 'head tail'``. Their longest common substring is ``'head tail'``. The next table demonstrate the mapping of LCS string back to search pattern and target substring::
        #     
        #     searchPattern  : `head <http://head>`_ tail
        #     anchor         :               ^
        #     targetSubstring:               head    tail
        #
        #     LCSString      :               head    tail
        #
        #   LCS algorithm uses backward matching method. Thus word `head` in LCS string is matched to the second `head` word in search pattern. Thus when match LCS string back to target string, it is matched to the wrong place and generated an index of 0 instead of 4 or 5. 
        #
        # Note:
        #
        #   One may debate that backward searching should be replaced by forward searching in this case, but the lack of context cannot justify which searching direction can generate better result. The next test case will demonstrate this:
        self.assertIn(index, (4, 5))

    @unittest.expectedFailure
    def test_12(self):
        index = f(searchAnchor = 6,
                  searchText = 'abcdabcdabcd',
                  targetText = 'abcd')
        # Scenario:
        #
        #   Click between the second 'b' and second 'c' will bring target anchor to the start of targetText.
        #
        # Bug:
        #
        #   Lack of context will cause ambiguity. We cannot determine how the matching is performed and thus cannot decide which matching is the optimal one. If the targetText is matched to the first 'abcd' in the searchText, then if searchAnchor is at index 6 it should map to index 4 in target string. If targetText is matched to the last 'abcd' in the searchText, then the searchAnchor should map to index in target string. If targetText is matched to the middle 'abcd', then it should map to index 2.
        #
        # Explaination:
        #
        #   We use backward LCS matching, so the output should be 2, not 0, not 4.
        #
        # TODO:
        #
        #   Since in the conversion, forward conversion is more natural than backward conversion. LCS mapping algorithm should provide search direction parameter.
        self.assertEqual(index, 2)


    def test_13(self):
        index = f(searchAnchor = 8,
                  searchText = '\n\n\n\ntest\n\n\n\n',
                  targetText = ' test    ')
        # This test case is designed to test such a scenario:
        # 
        # Anchor is placed after the lcs string, the mapping process is tested so that a correct target index can be found.
        self.assertEqual(index, 5)
        
    def test_14(self):
        index = f(searchAnchor = 8,
                  searchText = '\n\n\n\ntest\n\n\n\n',
                  targetText = 'test')
        # This test case is similar to previous one. But the anchor position in the target text is 4 while targetText[4] is invalid.
        # 
        # A reverse case is tested in the next test case
        self.assertEqual(index, 4)
        
    def test_15(self):
        index = f(searchAnchor = 4,
                  searchText = 'test',
                  targetText = '\n\n\n\ntest\n\n\n\n')
        # With this test case, all boundary conditions have been tested.
        self.assertEqual(index, 8)
        
        
from enki.plugins.preview.approx_match import refineSearchResult as lcs
import copy
# Given two strings, find their `longest common subsequence <http://en.wikipedia.org/wiki/Longest_common_subsequence_problem>`_. Notice this is different from `longest common substring <http://en.wikipedia.org/wiki/Longest_common_substring_problem>`_.
class TestLCS(base.TestCase):
    # first test boundary conditions
    def test_1(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = '',
                     targetSubstring = '')[2]
        self.assertEqual(string, '')

    def test_2(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'abc',
                     targetSubstring = '')[2]
        self.assertEqual(string, '')

    # identical string match
    def test_3(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'abc',
                     targetSubstring = 'abc')[2]
        self.assertEqual(string, 'abc')

    # no match
    def test_4(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'Fox',
                     targetSubstring = 'Bear')[2]
        self.assertEqual(string, '')

    # unicode test
    def test_5(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'Fußball',
                     targetSubstring = 'Football')[2]
        self.assertEqual(string, 'Fball')

    def test_6(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'Niederösterreich',
                     targetSubstring = 'Oberösterreich')[2]
        self.assertEqual(string, 'erösterreich')

    # control charater test
    def test_7(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'abc\ndef',
                     targetSubstring = 'gh\nijkl')[2]
        self.assertEqual(string, '\n')

    # real test cases. test8 contains long common substring
    def test_8(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                     targetSubstring = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')[2]
        self.assertEqual(string, 'The d user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')

    # This test contains mostly short common subseqence fragments. This will cause long editing distance
    def test_9(self):
        string = lcs(searchAnchor = 0,
                     searchPattern = 'age = None# `exclude_patterns# <http://sphinx-doc.org/config.html#confval-exclude_patterns>`_: List of# patterns, re',
                     targetSubstring = 'for a list of supported languages.##language = None exclude_patterns: List of patterns, re')[2]
        self.assertEqual(string, 'a  o upte ngg.lnaexclude_patterns: List of patterns, re')

#    # test_10 test the performance when comparing two files. this will take about 1min
#    def test_10(self):
#        print os.getcwd()
#        with open("D:\\enki\\tests\\test_plugins\\test_ApproxMatch.py", 'r') as file:
#            searchPattern = file.read()
#        targetSubstring = copy.deepcopy(searchPattern)
#        string = lcs(0, searchPattern, targetSubstring)[2]
#        self.assertEqual(string, searchPattern)


if __name__ == '__main__':
    unittest.main()
