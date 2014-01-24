#!/usr/bin/env python

import unittest
import os.path
import sys
import imp

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base

from PyQt4.QtTest import QTest
from PyQt4.QtGui import QDockWidget

from enki.core.core import core


def requiresModule(module):
    def realDecorator(func):
        def wrapped(self):
            try:
                imp.find_module(module)
            except ImportError:
                self.fail("This test requires python-{}".format(module))
            else:
                func(self)
        return wrapped
    return realDecorator


class Test(base.TestCase):
    # Find then return the PreviewDock object. Fail if
    # it is not found.
    def _dock(self):
        return self.findDock('&Preview')

    # Find then return the PreviewDock widget. Fail if it is
    # not found.
    def _widget(self):
        return self._dock().widget()

    def _showDock(self):
        core.actionManager().action('mView/aPreview').trigger()

    def _visibleText(self):
        return self._widget().webView.page().mainFrame().toPlainText()

    def _html(self):
        return self._widget().webView.page().mainFrame().toHtml()
    
    # Wait for the PreviewDock to emit the htmlReady signal,
    # which is produced by calling to start function. Assert
    # if the signal isn't emitted within a timeout.
    def _assertHtmlReady(self, start):
        self.assertEmits(start, self._dock()._thread.htmlReady, 1000)

    def _doBasicTest(self, extension):
        text = 'The preview text'
        document = self.createFile('file.' + extension, text)

        self._assertHtmlReady(self._showDock)
        self.assertTrue(text in self._visibleText())

    def test_html(self):
        self._doBasicTest('html')

    @requiresModule('docutils')
    def test_rst(self):
        self._doBasicTest('rst')

    @requiresModule('markdown')
    def test_markdown(self):
        self._doBasicTest('md')

    @requiresModule('markdown')
    def test_markdown_templates(self):
        core.config()['Preview']['Template'] = 'WhiteOnBlack'
        document = self.createFile('test.md', 'foo')

        self._assertHtmlReady(self._showDock)
        combo = self._widget().cbTemplate
        self.assertEqual(combo.currentText(), 'WhiteOnBlack')
        self.assertFalse('body {color: white; background: black;}' in self._visibleText())
        self.assertTrue('body {color: white; background: black;}' in self._html())

        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('Default')))
        self.assertFalse('body {color: white; background: black;}' in self._visibleText())
        self.assertFalse('body {color: white; background: black;}' in self._html())
        self.assertEqual(core.config()['Preview']['Template'], 'Default')

        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('WhiteOnBlack')))
        self.assertEqual(combo.currentText(), 'WhiteOnBlack')
        self.assertFalse('body {color: white; background: black;}' in self._visibleText())
        self.assertTrue('body {color: white; background: black;}' in self._html())

    @requiresModule('markdown')
    def test_markdown_templates_help(self):
        core.config()['Preview']['Template'] = 'WhiteOnBlack'
        document = self.createFile('test.md', 'foo')
        self._showDock()

        combo = self._widget().cbTemplate

        def inDialog(dialog):
            self.assertEqual(dialog.windowTitle(), 'Custom templaes help')
            dialog.accept()

        self.openDialog(lambda: combo.setCurrentIndex(combo.count() - 1), inDialog)

if __name__ == '__main__':
    unittest.main()
