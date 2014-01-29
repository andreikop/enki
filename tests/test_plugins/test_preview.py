#!/usr/bin/env python
# ***************************************************
# test_preview.py - Unit tests for the Preview module
# ***************************************************

import unittest
import os.path
import sys
import imp

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
import base

from PyQt4.QtCore import Qt, QPoint
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
    def setUp(self):
        base.TestCase.setUp(self)
        self.testText = 'The preview text'

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

    def _assertHtmlReady(self, start):
        """ Wait for the PreviewDock to emit the htmlReady signal.

        This signal is produced by calling to start function. Assert
        if the signal isn't emitted within a timeout.

        """
        self.assertEmits(start, self._dock()._thread.htmlReady, 1000)

    def _doBasicTest(self, extension):
        document = self.createFile('file.' + extension, self.testText)

        self._assertHtmlReady(self._showDock)
        self.assertTrue(self.testText in self._visibleText())

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

# Preview sync tests
# ^^^^^^^^^^^^^^^^^^
# To do:
#
# #. ``js_click.emit(0)`` and verify that the cursor is at the beginning of doc.
# #. Same as above, but emit(preview_text_mid_index) for middle of doc.
# #. Same as above, but emit(preview_text.len) for end of doc.
# #. Test all three above on an empty doc.
# #. Repeat above tests for code to web sync.
# #. Test that when javascript is disabled, web-to-code doesn't produce an exception.
# #. Same as above, but for code to web.
# #. Test that when the preview window is hidden, code-to-web sync stops working.
#
# Test that mouse clicks get turned into a js_click signal
# """"""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Test that web-to-code sync occurs on clicks to the web pane.
    # A click at 0, height (top left corner) should produce
    # an index of 0. It doesn't; I'm not sure I understand how
    # the WebView x, y coordinate system works. For now, skip
    # checking the resulting index.
    @requiresModule('docutils')
    def test_sync1(self):
        self._doBasicTest('rst')
        self.assertEmits(
          lambda: QTest.mouseClick(self._widget().webView,
            Qt.LeftButton, Qt.NoModifier, QPoint(0, self._widget().webView.height())),
          self._dock().js_click)
        
        
# Test that simulated mouse clicks at beginning/middle/end produce correct js_click values
# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Simulate a mouse click by calling window.onclick() in Javascript.
    def _jsOnClick(self):
        ret = self._widget().webView.page().mainFrame().evaluateJavaScript('window.onclick()')
        assert not ret
        
    # The web text for web-to-code sync will have extra
    # whitespace in it. But findText operates on a space-less
    # version of the text. Determine how many whitespace characters
    # preceed the text.
    def _wsLen(self):
        wtc = self._dock()._webTextContent()
        return len(wtc) - len(wtc.lstrip())
        
        
    # Given a string s, place the cursor after it and simulate a click
    # in the web view. Verify that the index produced by js_click
    # is correct.
    def _testSyncString(self, s):
        self._doBasicTest('rst')
        wsLen = self._wsLen()
        # Choose text to find.
        ret = self._widget().webView.page().findText(s)
        assert ret
        # Now run the Javascript and see if the index with whitespace added matches.
        self.assertEmits(self._jsOnClick, 
          self._dock().js_click, expectedSignalParams=(len(s) + wsLen,) )
        
    # To do: simulate a click before the first letter. Select T, then move backwards?
    # I seem to remember some sort of move command in Javascript, but can't find it now.`
        
    # Simulate a click after 'The pre' and check the resulting js_click result.
    @requiresModule('docutils')
    def test_sync2(self):
        self._testSyncString('The pre')

    # Same as above, but with the entire string.
    @requiresModule('docutils')
    def test_sync3(self):
        self._testSyncString(self.testText)

# Test that sending a js_click signal at beginning/middle/end moves cursor in code pane correctly
# """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Send a js_click signal then see if the code view gets sycned correctly.
    def _sendJsClick(self,
                     index):
                     # The index into 'The preview text' string to send and check.
        self._doBasicTest('rst')
        wsLen = self._wsLen()
        # Move the code cursor somewhere else, rather than index 0,
        # so working code must change its value.
        self._dock()._moveTextPaneToIndex(5)
        # Now, emit the signal for a click at the beginning of 'The preview text'.
        self._dock().js_click.emit(wsLen + index)
        # Check the new index, which should be 0.
        p = core.workspace().currentDocument().qutepart.textCursor().position()
        self.assertEqual(p, index)
    
    # Test a click at the beginning of the string.
    @requiresModule('docutils')
    def test_sync4(self):
        self._sendJsClick(0)
        
    # Test a click at the middle of the string.
    @requiresModule('docutils')
    def test_sync5(self):
        self._sendJsClick(8)
        
    # Test a click at the end of the string.
    @requiresModule('docutils')
    def test_sync6(self):
        self._sendJsClick(len(self.testText))
        

if __name__ == '__main__':
    unittest.main()
