#!/usr/bin/env python

import unittest
import os
import os.path
import sys
import subprocess

from mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt4.QtCore import Qt, QModelIndex, QTimer
from PyQt4.QtTest import QTest
from PyQt4.QtGui import QColor, QFont, QPlainTextEdit, QTextOption

from enki.core.core import core
from enki.plugins.navigator.ctags import processText


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

    def test_2(self):
        """Warning about etags
        """
        stdout = ("etags (GNU Emacs 23.4)\n"
                  "Copyright (C) 2012 Free Software Foundation, Inc.\n"
                  "This program is distributed under the terms in ETAGS.README")

        def continueFunc(dialog):
            page = dialog._pageForItem["Navigator"]
            self.assertEqual(page.lExecuteError.text(),
                             ('You are trying to use etags from the Emacs package, but it is not supported. '
                             'Use Exuberant Ctags.'))

            QTest.keyClick(dialog, Qt.Key_Enter)

        with patch('enki.lib.get_console_output.get_console_output', return_value=(stdout, None)):
            self.openSettings(continueFunc)


    @base.requiresCmdlineUtility('ctags --version')
    @base.inMainLoop
    def test_3(self):
        # Sort order is configurable
        self.createFile('source.rb', RUBY_SOURCE)
        dock = self.findDock('&Navigator')
        model = dock._tagModel
        self.retryUntilPassed(200,
                              lambda: self.assertEqual([tag.name for tag in model._tags[0].children],
                                                       ['initialize', '<=>', 'to_s']))

        def continueFunc(dialog):
            page = dialog._pageForItem["Navigator"]

            page.cbSortTagsAlphabetically.setChecked(True)
            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)
        self.assertEqual(core.config()['Navigator']['SortAlphabetically'], True)

        self.retryUntilPassed(200,
                              lambda: self.assertEqual([tag.name for tag in model._tags[0].children],
                                                       ['<=>', 'initialize', 'to_s']))


class Gui(base.TestCase):
    @base.requiresCmdlineUtility('ctags --version')
    @base.inMainLoop
    def test_1(self):
        # Tags are parsed and shown
        self.createFile('source.rb', RUBY_SOURCE)
        dock = self.findDock('&Navigator')
        model = dock._tagModel
        self.assertEqual(model.rowCount(QModelIndex()), 0)

        self.retryUntilPassed(200,
                              lambda: self.assertEqual(model.rowCount(QModelIndex()), 2))

    @base.requiresCmdlineUtility('ctags --version')
    def test_2(self):
        # Tags are updated on timer
        document = self.createFile('source.rb', RUBY_SOURCE)
        dock = self.findDock('&Navigator')
        model = dock._tagModel
        self.assertEqual(model.rowCount(QModelIndex()), 0)

        self.retryUntilPassed(200,
                              lambda: self.assertEqual(model.rowCount(QModelIndex()), 2))

        document.qutepart.text = RUBY_SOURCE + '\n' + RUBY_SOURCE
        self.assertEqual(model.rowCount(QModelIndex()), 2)

        self.retryUntilPassed(2000,
                              lambda: self.assertEqual(model.rowCount(QModelIndex()), 4))

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

    @base.inMainLoop
    def test_4(self):
        # dock remembers its Enabled/Disabled state
        ruby = self.createFile('source.rb', RUBY_SOURCE)
        txt = self.createFile('file.txt', "asdf")

        dock = self.findDock('&Navigator')

        core.workspace().setCurrentDocument(ruby)

        self.retryUntilPassed(200,
                              lambda: self.assertTrue(dock.isVisible()))

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

    @base.requiresCmdlineUtility('ctags --version')
    def test_5(self):
        # error message shown if ctags not found
        core.config()['Navigator']['CtagsPath'] = 'notexisiting'

        ruby = self.createFile('source.rb', RUBY_SOURCE)

        dock = self.findDock('&Navigator')

        self.retryUntilPassed(200,
                              lambda: self.assertTrue(dock._displayWidget.isHidden()))
        self.assertFalse(dock._errorLabel.isHidden())

        core.config()['Navigator']['CtagsPath'] = 'ctags'
        ruby.qutepart.text = RUBY_SOURCE + '\n'

        self.retryUntilPassed(2000,
                              lambda: self.assertFalse(dock._displayWidget.isHidden()))
        self.assertTrue(dock._errorLabel.isHidden())

    def _currentItemText(self):
        dock = self.findDock('&Navigator')
        model = dock._tagModel
        curr = dock._tree.currentIndex()
        return model.data(curr, Qt.DisplayRole)

    @base.requiresCmdlineUtility('ctags --version')
    @base.inMainLoop
    def test_6(self):
        # Tags are filtered
        document = self.createFile('source.rb', RUBY_SOURCE)
        dock = self.findDock('&Navigator')
        model = dock._tagModel
        self.assertEqual(model.rowCount(QModelIndex()), 0)

        self.retryUntilPassed(200,
                              lambda: self.assertEqual(model.rowCount(QModelIndex()), 2))

        self.keyClick(Qt.Key_N, Qt.AltModifier)
        self.keyClicks('_s')

        self.assertEqual(model.rowCount(QModelIndex()), 1)
        curr = dock._tree.currentIndex()
        self.assertEqual(model.data(curr, Qt.DisplayRole), 'to_s')

        self.keyClick(Qt.Key_Enter)
        self.assertEqual(document.qutepart.cursorPosition, (8, 0))
        self.assertEqual(model.rowCount(QModelIndex()), 2)

    @base.requiresCmdlineUtility('ctags --version')
    @base.inMainLoop
    def test_7(self):
        # Up, down, backspace on tree
        document = self.createFile('source.rb', RUBY_SOURCE)
        dock = self.findDock('&Navigator')
        model = dock._tagModel
        self.assertEqual(model.rowCount(QModelIndex()), 0)

        self.retryUntilPassed(200,
                              lambda: self.assertEqual(model.rowCount(QModelIndex()), 2))

        self.keyClick(Qt.Key_N, Qt.AltModifier)
        self.keyClicks('t')

        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(self._currentItemText(), 'initialize')

        self.keyClick(Qt.Key_Down)
        self.assertEqual(self._currentItemText(), 'to_s')

        self.keyClick(Qt.Key_Up)
        self.assertEqual(self._currentItemText(), 'initialize')

        self.keyClick(Qt.Key_Backspace)
        self.assertEqual(model.rowCount(QModelIndex()), 2)

    @base.requiresCmdlineUtility('ctags --version')
    @base.inMainLoop
    def test_8(self):
        stdout = "ctags: unrecognized option '--fields=nKs'\n	Try `ctags --help' for a complete list of options."

        with patch('enki.lib.get_console_output.get_console_output', return_value=(stdout, None)):
            # Up, down, backspace on tree
            document = self.createFile('source.rb', RUBY_SOURCE)
            dock = self.findDock('&Navigator')

            self.retryUntilPassed(2000,
                                  lambda: self.assertTrue(dock._errorLabel is not None and \
                                                          dock._errorLabel.isVisible()))

            self.assertTrue('ctags from Emacs package is used' in dock._errorLabel.text())



CPP_CODE = """

void Func()
{
    int foo;
}

int Cls::FirstMethod()
{
    return 0
}

int Cls::SecondMethod()
{
    return 0
}"""

PY_CODE = """
class Cls:
    def foobar(a, b):
        def func():
            pass
"""

def asDicts(tags):
    return {(tag.name, tag.lineNumber): asDicts(tag.children) \
                for tag in tags}

class Parser(base.TestCase):

    def test_1(self):
        tags = processText('C++', CPP_CODE, False)
        ref = {('Func', 2): {}, ('Cls', 7): {('FirstMethod', 7): {}, ('SecondMethod', 12): {}}}
        self.assertEqual(asDicts(tags), ref)

    def test_2(self):
        tags = processText('Python', PY_CODE, False)
        ref = {('Cls', 1): {('foobar', 2): {('func', 3): {}}}}
        self.assertEqual(asDicts(tags), ref)

    def test_3(self):
        """Ignore warning from ctags"""
        tags = processText('Python',
                           'ctags: Warning: something happened\n' + PY_CODE,
                           False)
        ref = {('Cls', 2): {('foobar', 3): {('func', 4): {}}}}
        self.assertEqual(asDicts(tags), ref)


if __name__ == '__main__':
    unittest.main()
