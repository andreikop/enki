#!/usr/bin/env python

import unittest

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


class InFile(base.TestCase):
    NOT_SAVED_DOCUMENT_TEXT = _TEXT
    
    @base.in_main_loop
    def test_type_and_search(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        qpart = core.workspace().currentDocument().qutepart
        
        QTest.keyClicks(self.app.focusWidget(), "string")
        
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
   
    @base.in_main_loop
    def test_search_next(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        qpart = core.workspace().currentDocument().qutepart
        
        QTest.keyClicks(self.app.focusWidget(), "string")
        
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
        
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (7, 9))
        self.assertEqual(qpart.selectedText, "string")
   
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (7, 57))
        self.assertEqual(qpart.selectedText, "string")
   
        # wrap
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
   
    @base.in_main_loop
    def test_search_previous(self):
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        qpart = core.workspace().currentDocument().qutepart
        
        QTest.keyClicks(self.app.focusWidget(), "string")
        
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")
        
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3, Qt.ShiftModifier)
        self.assertEqual(qpart.cursorPosition, (7, 57))
        self.assertEqual(qpart.selectedText, "string")
   
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3, Qt.ShiftModifier)
        self.assertEqual(qpart.cursorPosition, (7, 9))
        self.assertEqual(qpart.selectedText, "string")
   
        # wrap
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3, Qt.ShiftModifier)
        self.assertEqual(qpart.cursorPosition, (6, 18))
        self.assertEqual(qpart.selectedText, "string")

    @base.in_main_loop
    def test_select_and_search(self):
        qpart = core.workspace().currentDocument().qutepart
        
        # select first 'string'
        qpart.selectedPosition = ((6, 12), (6, 18))
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3)
        self.assertEqual(qpart.cursorPosition, (7, 9))
        self.assertEqual(qpart.selectedText, "string")
   
    @base.in_main_loop
    def test_select_and_search_multiline(self):
        qpart = core.workspace().currentDocument().qutepart
        
        qpart.text = _TEXT_MULTILINE_SEARCH
        
        # select first 'string'
        qpart.selectedPosition = ((0, 0), (1, 1))
        QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
        
        QTest.keyClick(self.app.focusWidget(), Qt.Key_F3)
        
        self.assertEqual(qpart.selectedPosition, ((3, 0), (4, 1)))
        self.assertEqual(qpart.selectedText, "a\nb")
   

class Gui(base.TestCase):
     @staticmethod
     def _findSearchController():
          for plugin in core.loadedPlugins():
               if isinstance(plugin, enki.plugins.searchreplace.Plugin):
                    return plugin._controller
     
     @base.in_main_loop
     def test_esc_on_widget_closes(self):
          QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
          widget = self._findSearchController()._widget
          self.assertFalse(widget.isHidden())
          
          QTest.keyClick(widget, Qt.Key_Escape)
          self.assertTrue(widget.isHidden())

     @base.in_main_loop
     def test_esc_on_editor_closes(self):
          QTest.keyClick(core.mainWindow(), Qt.Key_F, Qt.ControlModifier)
          widget = self._findSearchController()._widget
          self.assertFalse(widget.isHidden())
          
          QTest.keyClick(core.mainWindow(), Qt.Key_Return, Qt.ControlModifier)  # focus to editor
          QTest.keyClick(core.workspace().currentDocument(), Qt.Key_Escape)
          self.assertTrue(widget.isHidden())


if __name__ == '__main__':
    unittest.main()
