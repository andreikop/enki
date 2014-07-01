#!/usr/bin/env python
# .. -*- coding: utf-8 -*-
#
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
import codecs

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
from enki.widgets.dockwidget import DockWidget
# Both of the two following lines are needed: the first, so we can later
# ``reload(enki.plugins.preview)``; the last, to instiantate ``SettingsWidget``.
import enki.plugins.preview
from enki.plugins.preview import SettingsWidget
from import_fail import ImportFail


# Preview module tests
# ====================
def requiresModule(module):
    """This decorator checks that the given python module, which is
       required for a unit test, is present. If not, it skips the test."""
    try:
        imp.find_module(module)
    except ImportError:
        return unittest.skip("This test requires python-{}".format(module))
    return lambda func: func


class PreviewTestCase(base.TestCase):
    """A class of utilities used to aid in testing the preview module."""

    def setUp(self):
        base.TestCase.setUp(self)
        self.testText = 'The preview text'

    def _dock(self):
        """Find then return the PreviewDock object. Fail if
        it is not found."""
        return self.findDock('Previe&w')


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

    def _logText(self):
        return self._widget().teLog.toPlainText()

    def _assertHtmlReady(self, start, timeout=2000):
        """ Wait for the PreviewDock to emit the htmlReady signal.

        This signal is produced by calling to start function. Assert
        if the signal isn't emitted within a timeout.

        """
        self.assertEmits(start, self._dock()._thread.htmlReady, timeout)

    def _doBasicTest(self, extension):
        document = self.createFile('file.' + extension, self.testText)

        self._assertHtmlReady(self._showDock)

    def _doBasicSphinxTest(self, extension):
        """ This function will build a basic sphinx project in the temporary
        directory. The project consists of master document content.rst and a
        simple code document code.extension. Here the extension to the code
        file can be altered. For example, the extension can be set to .rst .
        """
        # Create master document contents.rst
        master = os.path.join(self.TEST_FILE_DIR, 'contents.rst')
        with codecs.open(master, 'wb', encoding='utf8') as file_:
            file_.write(""".. toctree::

   code2.""")
        # Create code file
        code = os.path.join(self.TEST_FILE_DIR, 'code.' + extension)
        with codecs.open(code, 'wb', encoding='utf8') as file_:
            file_.write(self.testText)

        # Open the code file. Wait for Html ready signal
        masterFile = core.workspace().openFile(master)
        codeFile = core.workspace().openFile(code)
        print '=============LISTING DIRECTORY================\n', os.listdir('C:\Users\Pan\AppData\Local\Temp\enki-tests')
        self._assertHtmlReady(self._showDock, timeout = 5000)

class Test(PreviewTestCase):
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

#    def test_html(self):
#        self._doBasicTest('html')
#
#    @requiresModule('docutils')
#    def test_rst(self):
#        self._doBasicTest('rst')
#
#    @requiresModule('markdown')
#    def test_markdown(self):
#        self._doBasicTest('md')
#
#    @requiresModule('markdown')
#    def test_markdown_templates(self):
#        core.config()['Preview']['Template'] = 'WhiteOnBlack'
#        document = self.createFile('test.md', 'foo')
#
#        self._assertHtmlReady(self._showDock)
#        combo = self._widget().cbTemplate
#        self.assertEqual(combo.currentText(), 'WhiteOnBlack')
#        self.assertFalse('body {color: white; background: black;}' in self._visibleText())
#        self.assertTrue('body {color: white; background: black;}' in self._html())
#
#        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('Default')))
#        self.assertFalse('body {color: white; background: black;}' in self._visibleText())
#        self.assertFalse('body {color: white; background: black;}' in self._html())
#        self.assertEqual(core.config()['Preview']['Template'], 'Default')
#
#        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('WhiteOnBlack')))
#        self.assertEqual(combo.currentText(), 'WhiteOnBlack')
#        self.assertFalse('body {color: white; background: black;}' in self._visibleText())
#        self.assertTrue('body {color: white; background: black;}' in self._html())
#
#    @requiresModule('markdown')
#    def test_markdown_templates_help(self):
#        core.config()['Preview']['Template'] = 'WhiteOnBlack'
#        document = self.createFile('test.md', 'foo')
#        self._showDock()
#
#        combo = self._widget().cbTemplate
#
#        def inDialog(dialog):
#            self.assertEqual(dialog.windowTitle(), 'Custom templaes help')
#            dialog.accept()
#
#        self.openDialog(lambda: combo.setCurrentIndex(combo.count() - 1), inDialog)
#
#    # Web to code sync tests
#    ##----------------------
#    # Test that mouse clicks get turned into a ``jsClick`` signal
#    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    @requiresModule('docutils')
#    def test_sync1(self):
#        """Test that web-to-text sync occurs on clicks to the web pane.
#        A click at 0, height (top left corner) should produce
#        an index of 0. It doesn't; I'm not sure I understand how
#        the WebView x, y coordinate system works. For now, skip
#        checking the resulting index.
#        """
#        self._doBasicTest('rst')
#        self.assertEmits(
#          lambda: QTest.mouseClick(self._widget().webView,
#            Qt.LeftButton, Qt.NoModifier, QPoint(0, self._widget().webView.height())),
#          self._dock().jsClick,
#          200)
#
#
#    # Test that simulated mouse clicks at beginning/middle/end produce correct ``jsClick`` values
#    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    def _jsOnClick(self):
#        """Simulate a mouse click by calling ``window.onclick()`` in Javascript."""
#        ret = self._widget().webView.page().mainFrame().evaluateJavaScript('window.onclick()')
#        assert not ret
#
#    def _wsLen(self):
#        """The web text for web-to-text sync will have extra
#        whitespace in it. But ``findText`` operates on a space-less
#        version of the text. Determine how many whitespace characters
#        preceed the text.
#        """
#        wtc = self._dock()._webTextContent()
#        return len(wtc) - len(wtc.lstrip())
#
#
#    def _testSyncString(self, s):
#        """Given a string ``s``, place the cursor after it and simulate a click
#        in the web view. Verify that the index produced by ``jsClick``
#        is correct.
#
#        Params:
#        s - String after which cursor will be placed.
#        """
#        self._doBasicTest('rst')
#        wsLen = self._wsLen()
#        # Choose text to find.
#        ret = self._widget().webView.page().findText(s)
#        assert ret
#        # Now run the Javascript and see if the index with whitespace added matches.
#        self.assertEmits(self._jsOnClick,
#                         self._dock().jsClick,
#                         100,
#                         expectedSignalParams=(len(s) + wsLen,))
#
#    @requiresModule('docutils')
#    def test_sync2a(self):
#        """TODO: simulate a click before the first letter. Select T, then move backwards using
#        https://developer.mozilla.org/en-US/docs/Web/API/Selection.modify.
#        For now, test after the letter T (the first letter).
#        """
#        self._testSyncString('T')
#
#    @requiresModule('docutils')
#    def test_sync2(self):
#        """Simulate a click after 'The pre' and check the resulting ``jsClick`` result."""
#        self._testSyncString('The pre')
#
#    @requiresModule('docutils')
#    def test_sync3(self):
#        """Same as above, but with the entire string."""
#        self._testSyncString(self.testText)
#
#    # Test that sending a ``jsClick`` signal at beginning/middle/end moves cursor in code pane correctly
#    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    def _sendJsClick(self, index):
#        """Send a ``jsClick`` signal then see if the code view gets sycned correctly.
#
#        Params:
#        index - The index into 'The preview text' string to send and check.
#        """
#        self._doBasicTest('rst')
#        wsLen = self._wsLen()
#        # Move the code cursor somewhere else, rather than index 0,
#        # so working code must change its value.
#        self._dock()._moveTextPaneToIndex(5)
#        assert index != 5
#        # Now, emit the signal for a click a given index into 'The preview text'.
#        self._dock().jsClick.emit(wsLen + index)
#        # Check the new index, which should be 0.
#        p = core.workspace().currentDocument().qutepart.textCursor().position()
#        self.assertEqual(p, index)
#
#    @requiresModule('docutils')
#    def test_sync4(self):
#        """Test a click at the beginning of the string."""
#        self._sendJsClick(0)
#
#    @requiresModule('docutils')
#    def test_sync5(self):
#        """Test a click at the middle of the string."""
#        self._sendJsClick(8)
#
#    @requiresModule('docutils')
#    def test_sync6(self):
#        """Test a click at the end of the string."""
#        self._sendJsClick(len(self.testText))
#
#    # Misc tests
#    ##^^^^^^^^^^
#    @requiresModule('docutils')
#    def test_sync7(self):
#        """Test on an empty document."""
#        self.testText = ''
#        self.test_sync1()
#
#    # Test after the web page was changed and therefore reloaded,
#    # which might remove the JavaScript to respond to clicks.
#    # No test is needed: the previous tests already check this,
#    # since disabling the following lines causes lots of failures::
#    #
#    #   self._widget.webView.page().mainFrame(). \
#    #     javaScriptWindowObjectCleared.connect(self._onJavaScriptCleared)
#
#    @requiresModule('docutils')
#    def test_sync8(self):
#        """Test with javascript disabled."""
#        # The ``_dock()`` method only works after the dock exists.
#        # The method below creates it.
#        self._doBasicTest('rst')
#        self._dock()._onJavaScriptEnabledCheckbox(False)
#        # Click. Nothing will happen, but make sure there's no assertion
#        # or internal error.
#        QTest.mouseClick(self._widget().webView, Qt.LeftButton)
#
#    # Code to web sync tests
#    ##----------------------
#    # Basic text to web sync
#    ##^^^^^^^^^^^^^^^^^^^^^^
#    def _textToWeb(self, s, testText=u'One\n\nTwo\n\nThree', checkText=True):
#        """Move the cursor in the text pane. Make sure it moves
#        to the matching location in the web pane.
#
#        Params:
#        s -  The string in the text pane to click before.
#        testText - The ReST string to use.
#        checkText - True if the text hilighted in the web dock should be
#            compared to the text in s.
#        """
#        # Create multi-line text.
#        self.testText = testText
#        self._doBasicTest('rst')
#        # Find the desired string.
#        index = self.testText.index(s)
#        # The cursor is already at index 0. Moving here
#        # produces no cursorPositionChanged signal.
#        assert index != 0
#        # Move to a location in the first line of the text.
#        # The sync won't happen until the timer expires; wait
#        # for that.
#        self.assertEmits(lambda: self._dock()._moveTextPaneToIndex(index, False),
#          self._dock()._cursorMovementTimer.timeout, 350)
#        # The web view should have the line containing s selected now.
#        if checkText:
#            self.assertTrue(s in self._widget().webView.selectedText())
#
#    @requiresModule('docutils')
#    def test_sync9(self):
#        # Don't use One, which is an index of 0, which causes no
#        # cursor movement and therefore no text to web sync.
#        self._textToWeb('ne')
#
#    @requiresModule('docutils')
#    def test_sync10(self):
#        self._textToWeb('Two')
#
#    @requiresModule('docutils')
#    def test_sync11(self):
#        self._textToWeb('Three')
#
#    # More complex test to web sync
#    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    @requiresModule('docutils')
#    def test_sync12(self):
#        """Tables with an embedded image cause findText to fail. Make sure no
#        exceptions are raised.
#
#        I can't seem to find a workaround to this: what search text does findText
#        expect when a table + embedded image are involved?
#        """
#        self._textToWeb('table', """
#================  ========================
#header1           header2
#================  ========================
#img               .. image:: img.png
#text after img    text after img
#================  ========================
#
#text after table""", False)
#
#    @requiresModule('docutils')
#    def test_sync14(self):
#        """Tables without an embedded image work just fine.
#        """
#        self._textToWeb('table', """
#================  ========================
#header1           header2
#================  ========================
#img               image:: img.png
#text after img    text after img
#================  ========================
#
#text after table""", True)
#
#    def _row_span_rest(self):
#        return """
#+--------------------------------+-------------+
#| Apple 1                        | Banana 2    |
#+--------------------------------+             |
#| Coco 3                         |             |
#| Cherry 3                       | Bael 2      |
#+--------------------------------+-------------+
#| Text after block 1,2, and 3                  |
#+----------------------------------------------+
#"""
#
#    @requiresModule('docutils')
#    def test_sync15(self):
#        """Text after an image works just fine.
#        """
#        self._textToWeb('table', """
#.. image:: img.png
#
#text after table""", True)
#
#    @requiresModule('docutils')
#    def test_sync16(self):
#        """Tables with column spans produce out-of-order text, so sync in some rows
#        containing a column span fails. The ReST below, copied as text after
#        being redered to HTML, is:
#
#        Apple 1
#        Banana 2
#
#        Bael 2
#        Coco 3 Cherry 3
#        Text after block 1,2, and 3
#
#        Note the reordering: Bael 2 comes before Coco 3 in the plain text, but
#        before it in the ReST. There's not much the approximate match can do to
#        fix this.
#        """
#        self._textToWeb('Banana', self._row_span_rest(), True)
#
#    @requiresModule('docutils')
#    def test_sync17(self):
#        """A failing case of the above test series."""
#        self._textToWeb('Bael', self._row_span_rest(), False)
#
#    @requiresModule('docutils')
#    def test_sync18(self):
#        """Verify that sync after the column span works."""
#        self._textToWeb('Text', self._row_span_rest(), True)
#
#    # Test no sync on closed preview window
#    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    def test_sync13(self):
#        self._doBasicTest('rst')
#        self._dock().close()
#        # Move the cursor. If there's no crash, we're OK.
#        qp = core.workspace().currentDocument().qutepart
#        cursor = qp.textCursor()
#        cursor.setPosition(1, QTextCursor.MoveAnchor)
#        qp.setTextCursor(cursor)
#
#    # Cases for _alignScrollAmount
#    ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    # Case 1: when the source y (in global coordinates) is above the target
#    # window.
#    def test_sync19(self):
#        self._doBasicTest('rst')
#        offset = self._dock()._alignScrollAmount(
#          sourceGlobalTop = 0,
#          sourceCursorTop = 1,
#          targetGlobalTop = 2,
#          targetCursorTop = 1,
#          targetHeight = 4,
#          targetCursorHeight = 1)
#        self.assertEqual(offset, -1)
#
#    # Case 2: when the source y (in global coordinates) is within the target
#    # window.
#    def test_sync20(self):
#        self._doBasicTest('rst')
#        offset = self._dock()._alignScrollAmount(
#          sourceGlobalTop = 0,
#          sourceCursorTop = 2,
#          targetGlobalTop = 0,
#          targetCursorTop = 1,
#          targetHeight = 4,
#          targetCursorHeight = 1)
#        self.assertEqual(offset, 1)
#
#    # Case 3: when the source y (in global coordinates) is belowthe target
#    # window.
#    def test_sync21(self):
#        self._doBasicTest('rst')
#        offset = self._dock()._alignScrollAmount(
#          sourceGlobalTop = 5,
#          sourceCursorTop = 2,
#          targetGlobalTop = 0,
#          targetCursorTop = 1,
#          targetHeight = 4,
#          targetCursorHeight = 1)
#        self.assertEqual(offset, 2)
#
#    # Cases for CodeChat setting ui
#    ##-----------------------------
#    #
#    @requiresModule('CodeChat')
#    def test_uiCheck1(self):
#        """When Enki runs for the first time, the CodeChat module should be
#           disabled by default."""
#        from enki.plugins.preview import SettingsWidget
#        sw = SettingsWidget()
#        self.assertFalse(sw.cbCodeChatEnable.isChecked())
#        self.assertTrue(sw.cbCodeChatEnable.isEnabled())
#        # If CodeChat module is present, user should not be able to see
#        # 'CodeChat not installed' notification.
#        sw.show()
#        # Widgets that are not on top level will be visible only when all its
#        # ancesters are visible. Check `here <http://qt-project.org/doc/qt-5/qwidget.html#visible-prop>`_
#        # for more details. Calling show() function will force update on
#        # setting ui.
#        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
#
#    @requiresModule('sphinx')
#    def test_uiCheck1a(self):
#        """By default, when sphinx is available, it is set to be disabled. So
#           does 'buildOnSave' function"""
#        from enki.plugins.preview import SettingsWidget
#        sw = SettingsWidget()
#        # sphinx is enabled but unchecked.
#        self.assertTrue(sw.cbSphinxEnable.isEnabled())
#        self.assertFalse(sw.cbSphinxEnable.isChecked())
#        # buildOnSave is also enabled but unchecked.
#        self.assertTrue(sw.cbBuildOnSaveEnable.isEnabled())
#        self.assertFalse(sw.cbBuildOnSaveEnable.isChecked())
#        # all setting directory are enabled but empty.
#        self.assertTrue(sw.leSphinxProjectPath.isEnabled())
#        self.assertEqual(sw.leSphinxProjectPath.text(), '')
#        self.assertTrue(sw.leSphinxOutputPath.isEnabled())
#        self.assertEqual(sw.leSphinxOutputPath.text(), '')
#        # builder extension is enabled and set to default 'html'
#        self.assertTrue(sw.leSphinxOutputExtension.isEnabled())
#        self.assertEqual(sw.leSphinxOutputExtension.text(), 'html')
#        # Assert user cannot see 'sphinx not installed notification'
#        sw.show()
#        self.assertFalse(sw.labelSphinxNotInstalled.isVisible())
#
#    @requiresModule('CodeChat')
#    def test_uiCheck3(self):
#        """ The Enable CodeChat checkbox should only be enabled if CodeChat can
#            be imported; otherwise, it should be disabled."""
#        # Trick Python into thinking that the CodeChat module doesn't exist.
#        # Verify that the CodeChat checkbox is disabled, and 'not installed'
#        # notification is visible.
#        with ImportFail('CodeChat'):
#            reload(enki.plugins.preview)
#            sw = SettingsWidget()
#            enabled = sw.cbCodeChatEnable.isEnabled()
#            sw.show()
#            notice = sw.labelCodeChatNotInstalled.isVisible()
#        # When done with this test first restore the state of the preview module
#        # by reloaded with the CodeChat module available, so that other tests
#        # won't be affected. Therefore, only do an assertFalse **after** the
#        # reload, since statements after the assert might not run (if the assert
#        # fails).
#        reload(enki.plugins.preview)
#        self.assertFalse(enabled)
#        self.assertTrue(notice)
#
#        # Now, prove that the reload worked: CodeChat should now be enabled,
#        # and 'not installed' notification should be invisible.
#        sw = SettingsWidget()
#        self.assertTrue(sw.cbCodeChatEnable.isEnabled())
#        sw.show()
#        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
#
#    @requiresModule('sphinx')
#    def test_uiCheck3a(self):
#        """Check sphinx setting GUI behavior if sphinx is not available."""
#        with ImportFail('sphinx'):
#            reload(enki.plugins.preview)
#            sw = SettingsWidget()
#            # Store current checkboxes' states, lineedits' states and
#            # label visibility.
#            sphinxEnabled = sw.cbSphinxEnable.isEnabled()
#            sphinxChecked = sw.cbSphinxEnable.isChecked()
#            buildOnSaveEnabled = sw.cbBuildOnSaveEnable.isEnabled()
#            buildOnSaveChecked = sw.cbBuildOnSaveEnable.isChecked()
#            projectPathEnabled = sw.leSphinxProjectPath.isEnabled()
#            projectPathContent = sw.leSphinxProjectPath.text()
#            outputPathEnabled = sw.leSphinxOutputPath.isEnabled()
#            outputPathContent = sw.leSphinxOutputPath.text()
#            extensionEnabled = sw.leSphinxOutputExtension.isEnabled()
#            extensionContent = sw.leSphinxOutputExtension.text()
#            sw.show()
#            noticeVisible = sw.labelSphinxNotInstalled.isVisible()
#        # When all states have been stored, reenable sphinx module, reload
#        # setting ui before checking previous states in case assersion fail
#        # will effect other test cases.
#        reload(enki.plugins.preview)
#        self.assertTrue(not sphinxEnabled and not sphinxChecked)
#        self.assertTrue(not buildOnSaveEnabled and not buildOnSaveChecked)
#        self.assertFalse(projectPathEnabled)
#        self.assertEqual(projectPathContent, '')
#        self.assertFalse(outputPathEnabled)
#        self.assertEqual(outputPathContent, '')
#        self.assertFalse(extensionEnabled)
#        self.assertEqual(extensionContent, '')
#        self.assertTrue(noticeVisible)
#
#        # After reload, as in test_uiCheck1a, make sure everything works again.
#        sw = SettingsWidget()
#        self.assertTrue(sw.cbSphinxEnable.isEnabled() and not sw.cbSphinxEnable.isChecked())
#        self.assertTrue(sw.cbBuildOnSaveEnable.isEnabled() and not \
#                        sw.cbBuildOnSaveEnable.isChecked())
#        self.assertTrue(sw.leSphinxProjectPath.isEnabled())
#        self.assertEqual(sw.leSphinxProjectPath.text(), '')
#        self.assertTrue(sw.leSphinxOutputPath.isEnabled())
#        self.assertEqual(sw.leSphinxOutputPath.text(), '')
#        self.assertTrue(sw.leSphinxOutputExtension.isEnabled())
#        self.assertEqual(sw.leSphinxOutputExtension.text(), 'html')
#        sw.show()
#        self.assertFalse(sw.labelSphinxNotInstalled.isVisible())
#
#    @requiresModule('CodeChat')
#    def test_uiCheck4(self):
#        """If Enki is opened with CodeChat enabled, the preview dock should be
#           found."""
#        core.config()['CodeChat']['Enabled'] = True
#        self._doBasicTest('py')
#        # The next line of code is unnecessary since self._doBasicTest() will
#        # call self._dock()
#        #self._dock()
#
#    @requiresModule('CodeChat')
#    def test_uiCheck5(self):
#        """If Enki is opened without any configuration, the preview dock cannot
#           be found if the opened file is a code file. This will not affect reST
#           files or html files."""
#        with self.assertRaises(AssertionError):
#            self._doBasicTest('py')
#            #self._dock()
#
#    @requiresModule('CodeChat')
#    def test_uiCheck6(self):
#        """If an empty code file is passed to Enki, the CodeChat preview panel
#           should be empty."""
#        core.config()['CodeChat']['Enabled'] = True
#        self.testText = u''
#        self._doBasicTest('py')
#        self.assertEqual(self._visibleText(), self.testText)
#
#    @requiresModule('CodeChat')
#    def test_uiCheck7(self):
#        """Test that Unicode characters are handled properly.
#        """
#        core.config()['CodeChat']['Enabled'] = True
#        self.testText = u'Niederösterreich'
#        self._doBasicTest('py')
#        # Plaintext captured from the preview dock will append a newline if
#        # preview dock is not empty. A '\n' is added accordingly.
#        self.assertEqual(self._visibleText(), self.testText+'\n')
#
#    @requiresModule('CodeChat')
#    def test_uiCheck8(self):
#        """Start with a short code file, make sure the preview window isn't
#           opened, then enable the CodeChat module and refresh Enki.
#           The preview window should now be opened."""
#        self.testText = u'test'
#        with self.assertRaises(AssertionError):
#            self._doBasicTest('py')
#        core.config()['CodeChat']['Enabled'] = True
#        core.uiSettingsManager().dialogAccepted.emit();
#        self._doBasicTest('py')
#
#    @requiresModule('CodeChat')
#    def test_uiCheck9(self):
#        """Uninterpretable reStructuredText syntax in source code will generate
#           errors and be displayed in the output log window."""
#        core.config()['CodeChat']['Enabled'] = True
#        self.testText = u'# .. wrong::'
#        self._doBasicTest('py')
#        self.assertTrue("""Unknown directive type "wrong".""" in self._logText())
#        # do the same test for restructuredText
#        self.testText = u'.. wrong::'
#        self._doBasicTest('rst')
#        self.assertTrue("""Unknown directive type "wrong".""" in self._logText())
#
#    @requiresModule('CodeChat')
#    def test_uiCheck10(self):
#        """Empty input should generate an empty log.
#        """
#        core.config()['CodeChat']['Enabled'] = True
#        self.testText = u''
#        self._doBasicTest('py')
#        self.assertEqual(self._logText(), '')
#        # do the same test for restructuredText
#        self._doBasicTest('rst')
#        self.assertEqual(self._logText(), '')
#
#    @requiresModule('CodeChat')
#    def test_uiCheck11(self):
#        """Unicode should display correctly in log window too.
#        """
#        core.config()['CodeChat']['Enabled'] = True
#        self.testText = u'# .. Niederösterreich::'
#        self._doBasicTest('py')
#        self.assertTrue(u'Niederösterreich' in self._logText())
#        # do the same test for reStructuredText
#        self.testText = u'.. Niederösterreich::'
#        self._doBasicTest('rst')
#        self.assertTrue(u'Niederösterreich' in self._logText())
#
#    @requiresModule('CodeChat')
#    def test_uiCheck12(self):
#        """Test progress bar status (indefinite) when building.
#        """
#        core.config()['CodeChat']['Enabled'] = True
#        self.createFile('file.py', self.testText)
#        self.assertEqual(self._widget().prgStatus.maximum(), 0)
#        self.assertEqual(self._widget().prgStatus.minimum(), 0)
#
#    @requiresModule('CodeChat')
#    def test_uiCheck13(self):
#        """Check different progressbar colors given different scenarios.
#        """
#        core.config()['CodeChat']['Enabled'] = True
#        # First, working code with no errors or warnings.
#        self.testText = u'abc'
#        self._doBasicTest('rst')
#        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QProgressBar::chunk {}')
#
#    @requiresModule('CodeChat')
#    def test_uiCheck14(self):
#        core.config()['CodeChat']['Enabled'] = True
#        # Next, test a code piece with only warnings.
#        self.testText = u'`abc'
#        self._doBasicTest('rst')
#        self.assertTrue('yellow' in self._widget().prgStatus.styleSheet())
#
#    @requiresModule('CodeChat')
#    def test_uiCheck15(self):
#        core.config()['CodeChat']['Enabled'] = True
#        # Next, test a code piece with only errors.
#        self.testText = u'# .. ERROR::'
#        self._doBasicTest('py')
#        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
#
#    @requiresModule('CodeChat')
#    def test_uiCheck16(self):
#        """A complex test case that tests both the log parser regexp and
#        the progress bar color when both warnings and errors are present.
#        """
#        core.config()['CodeChat']['Enabled'] = True
#        self.testText = u'# .. ERROR::\n# `WARNING_'
#        self._doBasicTest('py')
#        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
#        self.assertTrue('Warning(s): 2 Error(s): 2' in self._logText())
#
#    @requiresModule('CodeChat')
#    def test_uiCheck17(self):
#        """Switching between different files should update the log
#        window accordingly.
#        """
#        core.config()['CodeChat']['Enabled'] = True
#        # First creat a warning only test case
#        document1 = self.createFile('file1.py', '# `<>_')
#        # then an error only case
#        document2 = self.createFile('file2.py', '# .. h::')
#        # then a error free case
#        document3 = self.createFile('file3.py', '# <>_')
#        # switch to document 1
#        core.workspace().setCurrentDocument(document1)
#        self._assertHtmlReady(self._showDock)
#        self.assertTrue('yellow' in self._widget().prgStatus.styleSheet())
#        self.assertTrue('Warning(s): 1 Error(s): 0' in self._logText())
#        # switch to document 2
#        core.workspace().setCurrentDocument(document2)
#        self._assertHtmlReady(self._showDock)
#        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
#        self.assertTrue('Warning(s): 0 Error(s): 1' in self._logText())
#        # switch to document 3
#        core.workspace().setCurrentDocument(document3)
#        self._assertHtmlReady(self._showDock)
#        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QProgressBar::chunk {}')
#        self.assertEqual(self._logText(), '')

    @requiresModule('sphinx')
    def test_uiCheck18(self):
        """Basic sphinx test"""
        core.config()['sphinx']['Enabled'] = True
        core.config()['sphinx']['ProjectPath'] = self.TEST_FILE_DIR
        core.config()['sphinx']['OutputPath'] = os.path.join(self.TEST_FILE_DIR, '_build\\html')
        core.config()['sphinx']['OutputExtension'] = 'html'
        sw = SettingsWidget()
        sw._buildSphinxProject()
        self.testText = """****
head1
****"""
        self._doBasicSphinxTest('rst')
        print '=============LISTING DIRECTORY================\n', os.listdir('C:\Users\Pan\AppData\Local\Temp\enki-tests')
#        import time
#        time.sleep(550)

        print "================CURRENT HTML==================\nhtml:"
        print self._html()
        print "================CURRENT LOG===================\n\nLog text:"
        print self._logText()

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
