# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of Enki.
#
#    Enki is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    Enki is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with Enki.  If not, see <http://www.gnu.org/licenses/>.
#
# *******************************************
# test_ApproxMatch.py - Unit testing
# *******************************************

import unittest
import os.path
import sys


# Insert path to base before importing.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base
# Base will insert path to enki, so its modules that we want to test can now be imported.
from enki.plugins.preview.ApproxMatch import find_approx_text_in_target as f

# Find a location in a source file based on a given location in the resulting html.
class TestApproxMatch(base.TestCase):
    # Show that we can match identical text
    def test_1(self):
        index = f(search_anchor = 2,
                  search_text = 'test',
                  target_text = 'test')
        self.assertEqual(index, 2)

    # Show that we can match with a initial Python comment
    def test_2(self):
        index = f(search_anchor = 4,
                  search_text = '# test',
                  target_text = 'test')
        self.assertEqual(index, 2)

    # Show that we can match with a initial C/C++ comment
    def test_3(self):
        index = f(search_anchor = 5,
                  search_text = '// test',
                  target_text = 'test')
        self.assertEqual(index, 2)

    # Show that we can match at the end of a line
    def test_4(self):
        index = f(search_anchor = 4,
                  search_text = 'test\ntest',
                  target_text = 'test\ntest')
        self.assertEqual(index, 4)

    # Show that we can match at the end of a line with a Python comment
    def test_5(self):
        index = f(search_anchor = 6,
                  search_text = '# test\n# test',
                  target_text = 'test\ntest')
        self.assertEqual(index, 4)

    def test_6(self):
        index = f(search_anchor = 73-34,
                  search_text = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                  target_text = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')
        self.assertEqual(index, 66-34)

if __name__ == '__main__':
    unittest.main()
