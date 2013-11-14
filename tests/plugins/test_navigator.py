#!/usr/bin/env python

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtCore import Qt, QModelIndex, QTimer
from PyQt4.QtTest import QTest
from PyQt4.QtGui import QColor, QFont, QPlainTextEdit, QTextOption

from enki.core.core import core


RUBY_SOURCE = '''class Person
  attr_reader :name, :age
  def initialize(name, age)
    @name, @age = name, age
  end
  def <=>(person) # the comparison operator for sorting
    age <=> person.age
  end
  def to_s
    "#{name} (#{age})"
  end
end

def hello_world
    return 7
end
'''


class Settings(base.TestCase):
    def test_1(self):
        # Ctags path are configurable
        def continueFunc(dialog):
            page = dialog._pageForItem["Navigator"]
            
            page.leCtagsPath.setText('new ctags path')
            
            QTest.keyClick(dialog, Qt.Key_Enter)
        
        self.openSettings(continueFunc)
        
        self.assertEqual(core.config()['Navigator']['CtagsPath'], 'new ctags path')


class Test(base.TestCase):
    @base.in_main_loop
    def test_1(self):
        # Tags are parsed and shown
        self.createFile('source.rb', RUBY_SOURCE)
        dock = self.findDock('&Navigator')
        model = dock._model
        self.assertEqual(model.rowCount(QModelIndex()), 0)
        
        self.sleepProcessEvents(0.1)
        self.assertEqual(model.rowCount(QModelIndex()), 2)
    
    def test_2(self):
        # Tags are updated on timer
        document = self.createFile('source.rb', RUBY_SOURCE)
        dock = self.findDock('&Navigator')
        model = dock._model
        self.assertEqual(model.rowCount(QModelIndex()), 0)
        
        self.sleepProcessEvents(0.1)
        self.assertEqual(model.rowCount(QModelIndex()), 2)
        
        document.qutepart.text = RUBY_SOURCE + '\n' + RUBY_SOURCE
        self.assertEqual(model.rowCount(QModelIndex()), 2)
        self.sleepProcessEvents(1.1)
        self.assertEqual(model.rowCount(QModelIndex()), 4)
    
    def test_3(self):
        # Dock is visible when file is supported, and hidden otherwise
        ruby = self.createFile('source.rb', RUBY_SOURCE)
        txt = self.createFile('file.txt', "asdf")

        dock = self.findDock('&Navigator')
        
        core.workspace().setCurrentDocument(ruby)
        self.assertFalse(dock.isHidden())
        
        core.workspace().setCurrentDocument(txt)
        self.assertTrue(dock.isHidden())
        
        core.workspace().setCurrentDocument(ruby)
        self.assertFalse(dock.isHidden())
    
    @base.in_main_loop
    def test_4(self):
        # dock remembers its Enabled/Disabled state
        ruby = self.createFile('source.rb', RUBY_SOURCE)
        txt = self.createFile('file.txt', "asdf")

        dock = self.findDock('&Navigator')
        
        core.workspace().setCurrentDocument(ruby)
        self.sleepProcessEvents(0.1)
        
        self.assertTrue(dock.isVisible())
    
        self.keyClicks('N', Qt.AltModifier)
        self.keyClick(Qt.Key_Escape)
        self.assertFalse(dock.isVisible())
        self.assertFalse(core.config()['Navigator']['Enabled'])
        
        core.workspace().setCurrentDocument(txt)
        core.workspace().setCurrentDocument(ruby)
        self.assertFalse(dock.isVisible())
        
        self.keyClicks('N', Qt.AltModifier)
        self.assertTrue(dock.isVisible())
        self.assertTrue(core.config()['Navigator']['Enabled'])

        core.workspace().setCurrentDocument(txt)
        core.workspace().setCurrentDocument(ruby)
        self.assertTrue(dock.isVisible())
    
    def test_5(self):
        # error message shown if ctags not found
        core.config()['Navigator']['CtagsPath'] = 'notexisiting'
        
        ruby = self.createFile('source.rb', RUBY_SOURCE)
        
        dock = self.findDock('&Navigator')
        
        self.sleepProcessEvents(0.5)
        self.assertTrue(dock._tree.isHidden())
        self.assertFalse(dock._errorLabel.isHidden())
        
        core.config()['Navigator']['CtagsPath'] = 'ctags'
        ruby.qutepart.text = RUBY_SOURCE + '\n'
        self.sleepProcessEvents(1.1)
        self.assertFalse(dock._tree.isHidden())
        self.assertTrue(dock._errorLabel.isHidden())


if __name__ == '__main__':
    unittest.main()
