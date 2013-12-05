#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtTest import QTest

from enki.core.core import core
import enki.plugins.searchreplace

_TEXT = """middle_underscore
abc ab4d a@cd8 a@

% variables (begin with capital letter or underscore, contain numbers, letters and @)
_leadingUnderscore AbdD@ B45@c

% this is a string 
"a string sits between \" double quotes" atom "more string"

% and finally some real code, so we can see what it looks like...
-module(codetest).			% everything is in a module
-export([fac/1]).		% name and number of arguments - need this to be called outside of the module

fac(N) when N > 0  -> N * fac(N-1);
fac(N) when N == 0 -> 1.
"""

_TEXT_MULTILINE_SEARCH = """a
b

a
b
"""

_TEXT_WHOLE_WORD = """spam
foobarbaz
foo bar baz"""


def _findSearchController():
    for plugin in core.loadedPlugins():
        if isinstance(plugin, enki.plugins.searchreplace.Plugin):
            return plugin._controller


class InFile(base.TestCase):
    NOT_SAVED_DOCUMENT_TEXT = _TEXT
    
    @base.in_main_loop
    def test_type_and_search(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        qpart = core.workspace().currentDocument().qutepart
        
        self.keyClicks("string")
        
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
   
    @base.in_main_loop
    def test_search_next(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        qpart = core.workspace().currentDocument().qutepart
        
        self.keyClicks("string")
        
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
        
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (7, 9))
        self.assertEqual(qpart.selectedText, "string")
   
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (7, 57))
        self.assertEqual(qpart.selectedText, "string")
   
        # wrap
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
   
    @base.in_main_loop
    def test_search_previous(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        qpart = core.workspace().currentDocument().qutepart
        
        self.keyClicks("string")
        
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
        
        self.keyClick(Qt.Key_F3, Qt.ShiftModifier)
        self.assertEqual(qpart.cursorPosition, (7, 57))
        self.assertEqual(qpart.selectedText, "string")
   
        self.keyClick(Qt.Key_F3, Qt.ShiftModifier)
        self.assertEqual(qpart.cursorPosition, (7, 9))
        self.assertEqual(qpart.selectedText, "string")
   
        # wrap
        self.keyClick(Qt.Key_F3, Qt.ShiftModifier)
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")

    @base.in_main_loop
    def test_select_and_search(self):
        qpart = core.workspace().currentDocument().qutepart
        
        # select first 'string'
        qpart.selectedPosition = ((6, 12), (6, 18))
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (7, 9))
        self.assertEqual(qpart.selectedText, "string")
   
    @base.in_main_loop
    def test_select_and_search_multiline(self):
        qpart = core.workspace().currentDocument().qutepart
        
        qpart.text = _TEXT_MULTILINE_SEARCH
        
        # select first 'string'
        qpart.selectedPosition = ((0, 0), (1, 1))
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        self.keyClick(Qt.Key_F3)
        
        self.assertEqual(qpart.selectedPosition, ((3, 0), (4, 1)))
        self.assertEqual(qpart.selectedText, "a\nb")

    @base.in_main_loop
    def test_whole_word(self):
        qpart = core.workspace().currentDocument().qutepart
        
        qpart.text = _TEXT_WHOLE_WORD
        
        # select first 'string'
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        self.keyClicks("bar")
        self.assertEqual(qpart.cursorPosition[0], 1)
        
        # 2 items found
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition[0], 2)
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition[0], 1)
        
        # only 1 item found
        QTest.mouseClick(_findSearchController()._widget.cbWholeWord, Qt.LeftButton)
        self.assertEqual(qpart.cursorPosition[0], 2)
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition[0], 2)  # not moved, only line 2

        # only 1 item found in reg exp mode
        qpart.cursorPosition = (0, 0)
        QTest.mouseClick(_findSearchController()._widget.cbRegularExpression, Qt.LeftButton)
        self.assertEqual(qpart.cursorPosition[0], 2)
        self.keyClick(Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition[0], 2)  # not moved, only line 2

    @base.in_main_loop
    def test_highlight_found_items(self):
        qpart = core.workspace().currentDocument().qutepart
        
        qpart.text = "one two two three three three"
        
        def highlightedWordsCount():
            return len(qpart.extraSelections()) - 1  # 1 for cursor
        
        # select first 'string'
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        self.assertEqual(highlightedWordsCount(), 0)
        
        # search results are highlighted
        self.keyClicks("one")
        self.assertEqual(highlightedWordsCount(), 1)
        for i in range(3):
            self.keyClick(Qt.Key_Backspace)
        self.keyClicks("three")
        self.assertEqual(highlightedWordsCount(), 3)
        
        # widget search highlighting updated on text chagne
        qpart.text = qpart.text + ' '
        self.assertEqual(highlightedWordsCount(), 3)
        
        # Escape hides search widget and items
        self.keyClick(Qt.Key_Escape)
        self.assertEqual(highlightedWordsCount(), 0)
        
        # 'two' is highlighted during word search
        qpart.cursorPosition = (0, 5)
        self.keyClick(Qt.Key_Period, Qt.ControlModifier)
        self.assertEqual(highlightedWordsCount(), 2)
        
        # word search highlighting cleared on text chagne
        qpart.text = qpart.text + ' '
        self.assertEqual(highlightedWordsCount(), 0)


class ReplaceInDirectory(base.TestCase):
    @base.in_main_loop
    def test_1(self):
        # replace 'foo' with 'UUH' in opened and not opened file
        opened_file = self.createFile('opened_file.txt', 'the text contains foo bar\nand\nfew\nmore lines')
        opened_file.qutepart.cursorPosition = (3, 2)
        
        not_opened_file_path = self.TEST_FILE_DIR + 'not_opened_file.txt'
        with open(not_opened_file_path, 'w') as file_:
            file_.write('this file also contains foo bar')
            
        self.keyClick(Qt.Key_R, Qt.ShiftModifier | Qt.ControlModifier)
        self.keyClicks('foo')
        self.keyClick(Qt.Key_Tab)
        self.keyClicks('UUHHH')
        self.keyClick(Qt.Key_Enter)
        QTest.qWait(500)  # searching
        self.keyClick(Qt.Key_A, Qt.AltModifier)
        QTest.qWait(500)  # replacing
        
        self.assertEqual(opened_file.qutepart.text, 'the text contains UUHHH bar\nand\nfew\nmore lines')
        self.assertEqual(opened_file.qutepart.cursorPosition, (3, 2))
        with open(not_opened_file_path) as file_:
            self.assertEqual(file_.read(), 'this file also contains UUHHH bar')


class Gui(base.TestCase):
    @base.in_main_loop
    def test_esc_on_widget_closes(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        widget = _findSearchController()._widget
        self.assertFalse(widget.isHidden())
        
        QTest.keyClick(widget, Qt.Key_Escape)
        self.assertTrue(widget.isHidden())
    
    @base.in_main_loop
    def test_esc_on_editor_closes(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        widget = _findSearchController()._widget
        self.assertFalse(widget.isHidden())
        
        QTest.keyClick(core.mainWindow(), Qt.Key_Return, Qt.ControlModifier)  # focus to editor
        QTest.keyClick(core.workspace().currentDocument(), Qt.Key_Escape)
        self.assertTrue(widget.isHidden())
    

if __name__ == '__main__':
    unittest.main()
