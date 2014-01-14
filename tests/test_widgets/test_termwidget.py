#!/usr/bin/env python

"""Tests for enki.core.termwidget
Formatting and history is tested here, functionality shall be tested by tests for client code
"""

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base  # configures sys.path and sip


from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QColor
from PyQt4.QtTest import QTest

from enki.widgets.termwidget import TermWidget

class _BaseTest(base.TestCase):

     def setUp(self):
          self.term = TermWidget(self.app.font())

     def tearDown(self):
          del self.term


class Formatting(_BaseTest):
     def setupPalette(self, baseColorName, textColorName):
          palette = self.app.palette()
          palette.setColor(palette.Base, QColor(baseColorName))
          palette.setColor(palette.Text, QColor(textColorName))
          self.app.setPalette(palette)

     def body(self):
          text = self.term._browser.toHtml()
          pStart = text.index('<p')
          pEnd = text.index('>', pStart)
          text = text[pEnd+1:]
          bodyEnd = text.index('</p>')
          return text[:bodyEnd]

     def test_light_cmd(self):
          self.setupPalette('#ffffff', '#000000')
          self.term.execCommand('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#dfdfdf;">foo<br /></span>')

     def test_light_out(self):
          self.setupPalette('#ffffff', '#000000')
          self.term.appendOutput('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#ffffff;">foo</span>')

     def test_light_error(self):
          self.setupPalette('#ffffff', '#000000')
          self.term.appendError('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#ff9999;">foo</span>')

     def test_light_hint(self):
          self.setupPalette('#ffffff', '#000000')
          self.term.appendHint('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#9bff99;">foo</span>')

     def test_dark_cmd(self):
          self.setupPalette('#000000', '#ffffff')
          self.term.execCommand('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#404040;">foo<br /></span>')

     def test_dark_out(self):
          self.setupPalette('#000000', '#ffffff')
          self.term.appendOutput('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#000000;">foo</span>')

     def test_dark_error(self):
          self.setupPalette('#000000', '#ffffff')
          self.term.appendError('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#402626;">foo</span>')

     def test_dark_hint(self):
          self.setupPalette('#000000', '#ffffff')
          self.term.appendHint('foo')
          self.assertEqual(self.body(), '<span style=" background-color:#264026;">foo</span>')


class History(_BaseTest):
     def test_1(self):
          self.term.execCommand('foo')
          self.term.execCommand('bar')
          self.term.execCommand('bar')  # duplicating
          self.term.execCommand('baz')

          def clickAndCheck(key, text):
               QTest.keyClick(self.term._edit, key)
               self.assertEqual(self.term._edit.toPlainText(), text)

          clickAndCheck(Qt.Key_Up, 'baz')
          clickAndCheck(Qt.Key_Up, 'bar')
          clickAndCheck(Qt.Key_Up, 'foo')
          clickAndCheck(Qt.Key_Up, 'foo')  # no more items
          clickAndCheck(Qt.Key_Down, 'bar')
          clickAndCheck(Qt.Key_Down, 'baz')
          clickAndCheck(Qt.Key_Down, '')  # no more history, type new item

class Lang(_BaseTest):
     def test_1(self):
          self.term.setLanguage('Python')
          self.assertEqual(self.term._edit.language(), 'Python')
          self.term.setLanguage('C++')
          self.assertEqual(self.term._edit.language(), 'C++')

if __name__ == '__main__':
    unittest.main()
