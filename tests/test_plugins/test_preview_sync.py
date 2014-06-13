#!/usr/bin/env python
# .. -*- coding: utf-8 -*-
#
# *************************************************************
# test_preview_sync.py - Unit tests for the Preview Sync module
# *************************************************************
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
from test_preview import requiresModule, PreviewTestCase
# Both of the two following lines are needed: the first, so we can later
# ``reload(enki.plugins.preview)``; the last, to instiantate ``SettingsWidget``.
import enki.plugins.preview
from enki.plugins.preview import SettingsWidget
from import_fail import ImportFail


@requiresModule('tre')
class Test(PreviewTestCase):
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
          self._dock().previewSync.jsClick,
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
        wtc = self._dock().previewSync._webTextContent()
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
                         self._dock().previewSync.jsClick,
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
        self._dock().previewSync._moveTextPaneToIndex(5)
        assert index != 5
        # Now, emit the signal for a click a given index into 'The preview text'.
        self._dock().previewSync.jsClick.emit(wsLen + index)
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
        self.assertEmits(lambda: self._dock().previewSync._moveTextPaneToIndex(index, False),
          self._dock().previewSync._cursorMovementTimer.timeout, 350)
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
        offset = self._dock().previewSync._alignScrollAmount(
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
        offset = self._dock().previewSync._alignScrollAmount(
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
        offset = self._dock().previewSync._alignScrollAmount(
          sourceGlobalTop = 5,
          sourceCursorTop = 2,
          targetGlobalTop = 0,
          targetCursorTop = 1,
          targetHeight = 4,
          targetCursorHeight = 1)
        self.assertEqual(offset, 2)

    # Cases for CodeChat setting ui
    ##-----------------------------
    #
    @requiresModule('CodeChat')
    def test_uiCheck1(self):
        """When Enki runs for the first time, the CodeChat module should be
           disabled by default."""
        from enki.plugins.preview import SettingsWidget
        sw = SettingsWidget()
        self.assertFalse(sw.cbEnable.isChecked())
        self.assertTrue(sw.cbEnable.isEnabled())

    def test_uiCheck3(self):
        """ The Enable CodeChat checkbox should only be enabled if CodeChat can
            be imported; otherwise, it should be disabled."""
        # Trick Python into thinking that the CodeChat module doesn't exist.
        # Verify that the CodeChat checkbox is disabled.
        with ImportFail('CodeChat'):
            reload(enki.plugins.preview)
            sw = SettingsWidget()
            enabled = sw.cbEnable.isEnabled()
        # When done with this test first restore the state of the preview module
        # by reloaded with the CodeChat module available, so that other tests
        # won't be affected. Therefore, only do an assertFalse **after** the
        # reload, since statements after the assert might not run (if the assert
        # fails).
        reload(enki.plugins.preview)
        self.assertFalse(enabled)

        # Now, prove that the reload worked: CodeChat should now be enabled.
        sw = SettingsWidget()
        self.assertTrue(sw.cbEnable.isEnabled())


    @requiresModule('CodeChat')
    def test_uiCheck4(self):
        """If Enki is opened with CodeChat enabled, the preview dock should be
           found."""
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicTest('py')
        # The next line of code is unnecessary since self._doBasicTest() will
        # call self._dock()
        #self._dock()


    @requiresModule('CodeChat')
    def test_uiCheck5(self):
        """If Enki is opened without any configuration, the preview dock cannot
           be found if the opened file is a code file. This will not affect rsT
           files or html files."""
        with self.assertRaises(AssertionError):
            self._doBasicTest('py')
            #self._dock()

    @requiresModule('CodeChat')
    def test_uiCheck6(self):
        """If an empty code file is passed to Enki, the CodeChat preview panel
           should be empty."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u''
        self._doBasicTest('py')
        self.assertEqual(self._visibleText(), self.testText)

    @requiresModule('CodeChat')
    def test_uiCheck7(self):
        """Test that Unicode characters are handled properly.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u'Niederösterreich'
        self._doBasicTest('py')
        # Plaintext captured from the preview dock will append a newline if
        # preview dock is not empty. A '\n' is added accordingly.
        self.assertEqual(self._visibleText(), self.testText+'\n')

    @requiresModule('CodeChat')
    def test_uiCheck8(self):
        """Start with a short code file, make sure the preview window isn't
           opened, then enable the CodeChat module and refresh Enki.
           The preview winndow should be be opened."""
        self.testText = u'test'
        with self.assertRaises(AssertionError):
            self._doBasicTest('py')
        core.config()['CodeChat']['Enabled'] = True
        core.uiSettingsManager().dialogAccepted.emit();
        self._doBasicTest('py')

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
