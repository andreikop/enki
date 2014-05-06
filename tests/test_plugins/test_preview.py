#!/usr/bin/env python
# ***************************************************
# test_preview.py - Unit tests for the Preview module
# ***************************************************
#
# Imports
# =======
# Library imports
# ---------------
import unittest
import os.path
import sys
import imp

# Local application imports
# -------------------------
# Do this before PyQt imports so that base will set up sip API correctly.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

# Third-party library imports
# ---------------------------
from PyQt4.QtCore import Qt, QPoint
from PyQt4.QtTest import QTest
from PyQt4.QtGui import QDockWidget, QTextCursor

# Local application imports
# -------------------------
from enki.core.core import core

from import_fail import ImportFail


# Preview module tests
# ====================
def requiresModule(module):
    """This decorator checks that the given python module, which is
    required for a unit test, is present.
    """
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

    def _dock(self):
        """Find then return the PreviewDock object. Fail if
        it is not found."""
        return self.findDock('&Preview')


    def _widget(self):
        """Find then return the PreviewDock widget. Fail if it is
        not found."""
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
        self.assertEmits(start, self._dock()._thread.htmlReady, 2000)

    def _doBasicTest(self, extension):
        document = self.createFile('file.' + extension, self.testText)

        self._assertHtmlReady(self._showDock)

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

    # Web to code sync tests
    ##----------------------
    # Test that mouse clicks get turned into a ``jsClick`` signal
    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    @requiresModule('docutils')
    def test_sync1(self):
        """Test that web-to-text sync occurs on clicks to the web pane.
        A click at 0, height (top left corner) should produce
        an index of 0. It doesn't; I'm not sure I understand how
        the WebView x, y coordinate system works. For now, skip
        checking the resulting index.
        """
        self._doBasicTest('rst')
        self.assertEmits(
          lambda: QTest.mouseClick(self._widget().webView,
            Qt.LeftButton, Qt.NoModifier, QPoint(0, self._widget().webView.height())),
          self._dock().jsClick,
          200)


    # Test that simulated mouse clicks at beginning/middle/end produce correct ``jsClick`` values
    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def _jsOnClick(self):
        """Simulate a mouse click by calling ``window.onclick()`` in Javascript."""
        ret = self._widget().webView.page().mainFrame().evaluateJavaScript('window.onclick()')
        assert not ret

    def _wsLen(self):
        """The web text for web-to-text sync will have extra
        whitespace in it. But ``findText`` operates on a space-less
        version of the text. Determine how many whitespace characters
        preceed the text.
        """
        wtc = self._dock()._webTextContent()
        return len(wtc) - len(wtc.lstrip())


    def _testSyncString(self, s):
        """Given a string ``s``, place the cursor after it and simulate a click
        in the web view. Verify that the index produced by ``jsClick``
        is correct.

        Params:
        s - String after which cursor will be placed.
        """
        self._doBasicTest('rst')
        wsLen = self._wsLen()
        # Choose text to find.
        ret = self._widget().webView.page().findText(s)
        assert ret
        # Now run the Javascript and see if the index with whitespace added matches.
        self.assertEmits(self._jsOnClick,
                         self._dock().jsClick,
                         100,
                         expectedSignalParams=(len(s) + wsLen,))

    @requiresModule('docutils')
    def test_sync2a(self):
        """TODO: simulate a click before the first letter. Select T, then move backwards using
        https://developer.mozilla.org/en-US/docs/Web/API/Selection.modify.
        For now, test after the letter T (the first letter).
        """
        self._testSyncString('T')

    @requiresModule('docutils')
    def test_sync2(self):
        """Simulate a click after 'The pre' and check the resulting ``jsClick`` result."""
        self._testSyncString('The pre')

    @requiresModule('docutils')
    def test_sync3(self):
        """Same as above, but with the entire string."""
        self._testSyncString(self.testText)

    # Test that sending a ``jsClick`` signal at beginning/middle/end moves cursor in code pane correctly
    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def _sendJsClick(self, index):
        """Send a ``jsClick`` signal then see if the code view gets sycned correctly.

        Params:
        index - The index into 'The preview text' string to send and check.
        """
        self._doBasicTest('rst')
        wsLen = self._wsLen()
        # Move the code cursor somewhere else, rather than index 0,
        # so working code must change its value.
        self._dock()._moveTextPaneToIndex(5)
        assert index != 5
        # Now, emit the signal for a click a given index into 'The preview text'.
        self._dock().jsClick.emit(wsLen + index)
        # Check the new index, which should be 0.
        p = core.workspace().currentDocument().qutepart.textCursor().position()
        self.assertEqual(p, index)

    @requiresModule('docutils')
    def test_sync4(self):
        """Test a click at the beginning of the string."""
        self._sendJsClick(0)

    @requiresModule('docutils')
    def test_sync5(self):
        """Test a click at the middle of the string."""
        self._sendJsClick(8)

    @requiresModule('docutils')
    def test_sync6(self):
        """Test a click at the end of the string."""
        self._sendJsClick(len(self.testText))

    # Misc tests
    ##^^^^^^^^^^
    @requiresModule('docutils')
    def test_sync7(self):
        """Test on an empty document."""
        self.testText = ''
        self.test_sync1()

    # Test after the web page was changed and therefore reloaded,
    # which might remove the JavaScript to respond to clicks.
    # No test is needed: the previous tests already check this,
    # since disabling the following lines causes lots of failures::
    #
    #   self._widget.webView.page().mainFrame(). \
    #     javaScriptWindowObjectCleared.connect(self._onJavaScriptCleared)

    @requiresModule('docutils')
    def test_sync8(self):
        """Test with javascript disabled."""
        # The ``_dock()`` method only works after the dock exists.
        # The method below creates it.
        self._doBasicTest('rst')
        self._dock()._onJavaScriptEnabledCheckbox(False)
        # Click. Nothing will happen, but make sure there's no assertion
        # or internal error.
        QTest.mouseClick(self._widget().webView, Qt.LeftButton)

    # Code to web sync tests
    ##----------------------
    # Basic text to web sync
    ##^^^^^^^^^^^^^^^^^^^^^^
    def _textToWeb(self, s, testText=u'One\n\nTwo\n\nThree', checkText=True):
        """Move the cursor in the text pane. Make sure it moves
        to the matching location in the web pane.

        Params:
        s -  The string in the text pane to click before.
        testText - The ReST string to use.
        checkText - True if the text hilighted in the web dock should be
            compared to the text in s.
        """
        # Create multi-line text.
        self.testText = testText
        self._doBasicTest('rst')
        # Find the desired string.
        index = self.testText.index(s)
        # The cursor is already at index 0. Moving here
        # produces no cursorPositionChanged signal.
        assert index != 0
        # Move to a location in the first line of the text.
        # The sync won't happen until the timer expires; wait
        # for that.
        self.assertEmits(lambda: self._dock()._moveTextPaneToIndex(index, False),
          self._dock()._cursorMovementTimer.timeout, 350)
        # The web view should have the line containing s selected now.
        if checkText:
            self.assertTrue(s in self._widget().webView.selectedText())

    @requiresModule('docutils')
    def test_sync9(self):
        # Don't use One, which is an index of 0, which causes no
        # cursor movement and therefore no text to web sync.
        self._textToWeb('ne')

    @requiresModule('docutils')
    def test_sync10(self):
        self._textToWeb('Two')

    @requiresModule('docutils')
    def test_sync11(self):
        self._textToWeb('Three')

    # More complex test to web sync
    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    @requiresModule('docutils')
    def test_sync12(self):
        """Tables with an embedded image cause findText to fail. Make sure no
        exceptions are raised.

        I can't seem to find a workaround to this: what search text does findText
        expect when a table + embedded image are involved?
        """
        self._textToWeb('table', """
================  ========================
header1           header2
================  ========================
img               .. image:: img.png
text after img    text after img
================  ========================

text after table""", False)

    @requiresModule('docutils')
    def test_sync14(self):
        """Tables without an embedded image work just fine.
        """
        self._textToWeb('table', """
================  ========================
header1           header2
================  ========================
img               image:: img.png
text after img    text after img
================  ========================

text after table""", True)

    def _row_span_rest(self):
        return """
+--------------------------------+-------------+
| Apple 1                        | Banana 2    |
+--------------------------------+             |
| Coco 3                         |             |
| Cherry 3                       | Bael 2      |
+--------------------------------+-------------+
| Text after block 1,2, and 3                  |
+----------------------------------------------+
"""

    @requiresModule('docutils')
    def test_sync15(self):
        """Text after an image works just fine.
        """
        self._textToWeb('table', """
.. image:: img.png

text after table""", True)

    @requiresModule('docutils')
    def test_sync16(self):
        """Tables with column spans produce out-of-order text, so sync in some rows
        containing a column span fails. The ReST below, copied as text after
        being redered to HTML, is:

        Apple 1
        Banana 2

        Bael 2
        Coco 3 Cherry 3
        Text after block 1,2, and 3

        Note the reordering: Bael 2 comes before Coco 3 in the plain text, but
        before it in the ReST. There's not much the approximate match can do to
        fix this.
        """
        self._textToWeb('Banana', self._row_span_rest(), True)

    @requiresModule('docutils')
    def test_sync17(self):
        """A failing case of the above test series."""
        self._textToWeb('Bael', self._row_span_rest(), False)

    @requiresModule('docutils')
    def test_sync18(self):
        """Verify that sync after the column span works."""
        self._textToWeb('Text', self._row_span_rest(), True)

    # Test no sync on closed preview window
    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def test_sync13(self):
        self._doBasicTest('rst')
        self._dock().close()
        # Move the cursor. If there's no crash, we're OK.
        qp = core.workspace().currentDocument().qutepart
        cursor = qp.textCursor()
        cursor.setPosition(1, QTextCursor.MoveAnchor)
        qp.setTextCursor(cursor)

    # Cases for _alignScrollAmount
    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Case 1: when the source y (in global coordinates) is above the target
    # window.
    def test_sync19(self):
        self._doBasicTest('rst')
        offset = self._dock()._alignScrollAmount(
          sourceGlobalTop = 0,
          sourceCursorTop = 1,
          targetGlobalTop = 2,
          targetCursorTop = 1,
          targetHeight = 4,
          targetCursorHeight = 1)
        self.assertEqual(offset, -1)

    # Case 2: when the source y (in global coordinates) is within the target
    # window.
    def test_sync20(self):
        self._doBasicTest('rst')
        offset = self._dock()._alignScrollAmount(
          sourceGlobalTop = 0,
          sourceCursorTop = 2,
          targetGlobalTop = 0,
          targetCursorTop = 1,
          targetHeight = 4,
          targetCursorHeight = 1)
        self.assertEqual(offset, 1)

    # Case 3: when the source y (in global coordinates) is belowthe target
    # window.
    def test_sync21(self):
        self._doBasicTest('rst')
        offset = self._dock()._alignScrollAmount(
          sourceGlobalTop = 5,
          sourceCursorTop = 2,
          targetGlobalTop = 0,
          targetCursorTop = 1,
          targetHeight = 4,
          targetCursorHeight = 1)
        self.assertEqual(offset, 2)

    # by default, codechat should be disabled
    def test_uiCheck1(self):
        from enki.plugins.preview import SettingsWidget
        sw = SettingsWidget()
        self.assertFalse(sw.cbEnable.isChecked())
        self.assertTrue(sw.cbEnable.isEnabled())

    # but if actively set to true. should assert true
    def test_uiCheck2(self):
        from enki.plugins.preview import SettingsWidget
        core.config()['CodeChat']['Enabled'] = True
        sw = SettingsWidget()
        self.assertTrue(sw.cbEnable.isChecked())

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
