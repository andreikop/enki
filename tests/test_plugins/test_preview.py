#!/usr/bin/env python3
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
import codecs
from unittest.mock import patch

# Local application imports
# -------------------------
# Do this before PyQt imports so that base will set up sip API correctly.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base
from base import WaitForSignal

# Third-party library imports
# ---------------------------
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtCore import Qt, QPointF, QPoint
from PyQt5.QtTest import QTest

# Local application imports
# -------------------------
from enki.core.core import core
from enki.core.uisettings import UISettings
# Both of the two following lines are needed: the first, so we can later
# ``reload(enki.plugins.preview)``; the last, to instiantate ``SettingsWidget``.
import enki.plugins.preview
from enki.plugins.preview import CodeChatSettingsWidget, SphinxSettingsWidget
from .import_fail import ImportFail
from enki.plugins.preview import _getSphinxVersion


_SPHINX_VERSION = [1, 3, 0]
try:
    sphinxVersion = _getSphinxVersion('sphinx-build')
except:
    sphinxIsAvailable = False
    sphinxVersion = None
else:
    sphinxIsAvailable = sphinxVersion >= _SPHINX_VERSION


def requiresSphinx():
    """ A decorator: a test requires Sphinx """
    if sphinxIsAvailable:
        return lambda func: func
    elif sphinxVersion is not None:
        return unittest.skip('Sphinx is too old. {} required'.format(_SPHINX_VERSION))
    else:
        return unittest.skip('Sphinx not found')


# Preview module tests
# ====================


class SimplePreviewTestCase(base.TestCase):
    """Only for very minimal testing of the Preview dock."""

    def _dock(self):
        """Find then return the PreviewDock object. Fail if
        it is not found."""
        return self.findVisibleDock('Previe&w')


class TestSimplePreview(SimplePreviewTestCase):

    @base.requiresModule('CodeChat')
    def test_emptyCodeChatDocument(self):
        core.config()['CodeChat']['Enabled'] = True
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegex(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    @requiresSphinx()
    def test_emptySphinxDocument(self):
        core.config()['Sphinx']['Enabled'] = True
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegex(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    def test_emptyDocument(self):
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegex(AssertionError, 'Dock Previe&w not found'):
            self._dock()


class PreviewTestCase(SimplePreviewTestCase):
    """A class of utilities used to aid in testing the preview module."""

    def setUp(self):
        SimplePreviewTestCase.setUp(self)
        self.testText = 'The preview text'
        # Open the preview dock by loading an html file.
        self.createFile('dummy.html', '')

    def tearDown(self):
        # Note that base.tearDown sets each document's contents to '' to avoid
        # the save files dialog popping up. However, this causes Sphinx to be
        # re-run on the modified document (if it's enabled), which wastes time.
        # So, disable it.
        core.config()['Sphinx']['Enabled'] = False

        SimplePreviewTestCase.tearDown(self)

    def _widget(self):
        """Find then return the PreviewDock widget. Fail if it is
        not found."""
        return self._dock().widget()

    def _plainText(self):
        return self._widget().webView.page().mainFrame().toPlainText()

    def _html(self):
        return self._widget().webView.page().mainFrame().toHtml()

    def _logText(self):
        """Return log window text"""
        return self._widget().teLog.toPlainText()

    def _WaitForHtmlReady(self, timeout=8000, numEmittedExpected=2):
        # Expect two calls to loadFinished: one
        # produced by _clear(), then the second when the page is actually ready.
        lf = self._widget().webView.page().mainFrame().loadFinished
        return WaitForSignal(lf, timeout,
                             numEmittedExpected=numEmittedExpected)

    def _assertHtmlReady(self, start, timeout=8000, numEmittedExpected=2):
        """Wait for the PreviewDock to load in updated HTML after the start
        function is called. Assert if the signal isn't emitted within a timeout.
        """
        with self._WaitForHtmlReady(timeout,
                                    numEmittedExpected=numEmittedExpected):
            start()

    def _doBasicTest(self, extension, name='file', numEmittedExpected=2):
        # HTML files don't need processing in the worker thread.
        if extension != 'html':
            self._assertHtmlReady(lambda: self.createFile('.'.join([name, extension]),
                                                          self.testText), numEmittedExpected=numEmittedExpected)

    def _doBasicSphinxConfig(self):
        """This function will set basic Sphinx configuration options
        so that Sphinx can run in a test environment.
        """
        core.config()['Sphinx']['Enabled'] = True
        core.config()['Sphinx']['Executable'] = r'sphinx-build'
        core.config()['Sphinx']['ProjectPath'] = self.TEST_FILE_DIR
        core.config()['Sphinx']['OutputPath'] = os.path.join('_build', 'html')
        core.config()['Sphinx']['OutputExtension'] = r'html'
        core.config()['Sphinx']['AdvancedMode'] = False
        self._dock()._sphinxTemplateCheckIgnoreList = [QMessageBox.Yes]

    def _doBasicSphinxTest(self, extension, name='code'):
        """This function will build a basic Sphinx project in the temporary
        directory. The project consists of master document content.rst and a
        simple code document code.extension. Here the extension to the code
        file can be altered. For example, the extension can be set to .rst .
        """
        # Create master document index.rst
        master = os.path.join(self.TEST_FILE_DIR, 'index.rst')
        with codecs.open(master, 'wb', encoding='utf8') as file_:
            file_.write(""".. toctree::

   code.""" + extension)

        # Build the HTML, then return it and the log.
        self._assertHtmlReady(lambda: self.createFile('.'.join([name, extension]),
                                                      self.testText), timeout=10000)
        return self._html(), self._logText()


class TestPreview(PreviewTestCase):

    @base.inMainLoop
    def test_html(self):
        self._doBasicTest('html')
        self.assertFalse(self._widget().prgStatus.isVisible())

    @base.requiresModule('docutils')
    @base.inMainLoop
    def test_rst(self):
        self._doBasicTest('rst')
        self.assertTrue(self._widget().prgStatus.isVisible())

    @base.requiresModule('markdown')
    @base.inMainLoop
    def test_markdown(self):
        self._doBasicTest('md')
        self.assertFalse(self._widget().prgStatus.isVisible())

    @base.requiresModule('markdown')
    @base.inMainLoop
    def test_markdown_templates(self):
        core.config()['Preview']['Template'] = 'WhiteOnBlack'
        self._dock()._restorePreviousTemplate()
        self._assertHtmlReady(lambda: self.createFile('test.md', 'foo'))
        combo = self._widget().cbTemplate
        self.assertEqual(combo.currentText(), 'WhiteOnBlack')
        self.assertNotIn('body {color: white; background: black;}', self._plainText())
        self.assertIn('body {color: white; background: black;}', self._html())

        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('Default')),
                              numEmittedExpected=1)
        self.assertFalse('body {color: white; background: black;}' in self._plainText())
        self.assertFalse('body {color: white; background: black;}' in self._html())
        self.assertEqual(core.config()['Preview']['Template'], 'Default')

        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('WhiteOnBlack')),
                              numEmittedExpected=1)
        self.assertEqual(combo.currentText(), 'WhiteOnBlack')
        self.assertFalse('body {color: white; background: black;}' in self._plainText())
        self.assertTrue('body {color: white; background: black;}' in self._html())

    @base.requiresModule('markdown')
    @base.inMainLoop
    def test_markdown_templates_help(self):
        core.config()['Preview']['Template'] = 'WhiteOnBlack'
        document = self.createFile('test.md', 'foo')

        combo = self._widget().cbTemplate

        def inDialog(dialog):
            self.assertEqual(dialog.windowTitle(), 'Custom templaes help')
            dialog.accept()

        self.openDialog(lambda: combo.setCurrentIndex(combo.count() - 1), inDialog)

    # Cases for literate programming setting ui
    # -----------------------------------------
    def setupSettingsWidget(self, WidgetClass):
        """To use a widget embedded in a UISettings requres a bit of
        manipulation, which this helper function encapsulates.
        """
        us = UISettings(None)
        wc = WidgetClass(us)
        # Important: show() causes all the GUI buttons, checkboxes, etc. to
        # work. For example, setting a checkbox to checked then immediately
        # reading it before calling show() results in Qt reporting an unchecked
        # checkbox. However, show() only operates on the currently visible page
        # of the settings. Hence, make the page being tested the current page,
        # then show() it.
        us.swPages.setCurrentWidget(wc)
        us.show()
        return us, wc

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_settingUiCheck1(self):
        """When Enki runs for the first time, the CodeChat module should be
           disabled by default."""
        us, sw = self.setupSettingsWidget(CodeChatSettingsWidget)
        self.assertFalse(sw.cbCodeChat.isChecked())
        self.assertTrue(sw.cbCodeChat.isEnabled())
        # If the CodeChat module is present, the user should not be able to see
        # the 'CodeChat not installed' notification.
        #
        # Widgets that are not on the top level will be visible only when all their
        # ancesters are visible. Check `here
        # <http://qt-project.org/doc/qt-5/qwidget.html#visible-prop>`_
        # for more details. Calling show() function will force update on
        # setting ui.
        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
        us.close()

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_settingUiCheck3(self):
        """ The Enable CodeChat checkbox should only be enabled if CodeChat can
            be imported; otherwise, it should be disabled."""
        # Trick Python into thinking that the CodeChat module doesn't exist.
        # Verify that the CodeChat checkbox is disabled, and the 'not installed'
        # notification is visible.
        with ImportFail(['CodeChat'], [enki.plugins.preview]):
            us, sw = self.setupSettingsWidget(CodeChatSettingsWidget)
            self.assertFalse(sw.cbCodeChat.isEnabled())
            self.assertTrue(sw.labelCodeChatNotInstalled.isVisible())
            self.assertTrue(sw.labelCodeChatNotInstalled.isEnabled())
            self.assertTrue(sw.labelCodeChatIntro.isEnabled())
            us.close()

        # Now, prove that the reload worked: CodeChat should now be enabled, but
        # remain unchecked just like the first time enki starts. 'not installed'
        # notification should be invisible.
        us, sw = self.setupSettingsWidget(CodeChatSettingsWidget)
        self.assertTrue(sw.cbCodeChat.isEnabled())
        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
        self.assertTrue(sw.labelCodeChatIntro.isEnabled())
        us.close()

    @requiresSphinx()
    @base.inMainLoop
    def test_settingUiCheck3a(self):
        """test_uiCheck1a has tested the case when Sphinx is disabled. This
        unit test will test the case when Sphinx is mannually enabled.
        """
        us, sw = self.setupSettingsWidget(SphinxSettingsWidget)
        # Mannually enable Sphinx.
        sw.gbSphinxProject.setChecked(True)
        # Since it is assumed that the user has sphinx-build installed, the Sphinx
        # executable, output extension and default commandline will be initialize
        # to preset values.
        self.assertTrue(sw.gbSphinxProject.isChecked())
        # Build option is enabled and automatically set to Build only on save.
        self.assertTrue(sw.rbBuildOnlyOnSave.isEnabled())
        self.assertTrue(sw.rbBuildOnFileChange.isEnabled())
        # All setting directories are enabled and empty.
        self.assertTrue(sw.leSphinxProjectPath.isEnabled())
        self.assertTrue(sw.leSphinxOutputPath.isEnabled())
        # Executable is enabled and set to default 'sphinx-build'
        self.assertTrue(sw.leSphinxExecutable.isEnabled())
        # Assert advanced mode toggle label enabled and reads 'Advanced Mode'
        self.assertTrue(sw.lbSphinxEnableAdvMode.isEnabled())
        self.assertTrue('Advanced Mode' in sw.lbSphinxEnableAdvMode.text())
        # Assert user cannot see any advanced setting items.
        self.assertFalse(sw.lbSphinxCmdline.isVisible())
        self.assertFalse(sw.leSphinxCmdline.isVisible())
        self.assertFalse(sw.lbSphinxReference.isVisible())

        # Now simulate a keypress event on advanced setting toggle label
        sw.lbSphinxEnableAdvMode.mousePressEvent()
        # Assert advanced model toggle label now reads 'Normal Mode'
        self.assertTrue('Normal Mode' in sw.lbSphinxEnableAdvMode.text())
        # Verify that normal mode setting line edits and pushbuttons are all gone
        for i in range(sw.gridLtNotAdvancedSettings.count()):
            self.assertFalse(sw.gridLtNotAdvancedSettings.itemAt(i).widget().isVisible())
        # Verify advanced mode setting line edits and labels are visible.
        self.assertTrue(sw.lbSphinxCmdline.isVisible())
        self.assertTrue(sw.leSphinxCmdline.isVisible())
        self.assertTrue(sw.lbSphinxReference.isVisible())
        us.close()

    # Cases for code preview using Codechat or Sphinx
    # -----------------------------------------------
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck1(self):
        """If Enki is opened with CodeChat enabled, the preview dock should be
           found."""
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicTest('py')
        self.assertTrue(self._widget().prgStatus.isVisible())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck1a(self):
        """If a non-supported language with a known extension is provided to
           CodeChat, make sure an appropriate error is generated."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = '(* A comment *)\nZ -> Z * Z'
        self._doBasicTest('v')
        self.assertTrue(self._widget().prgStatus.isVisible())
        self.assertIn('this file is not supported by CodeChat', self._logText())

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck2(self):
        """Basic Sphinx test: create a Sphinx project in a temp folder, return
           webView content and log content after Sphinx builds the project."""
        self._doBasicSphinxConfig()
        self.testText = """****
head
****

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(self._widget().prgStatus.isVisible())

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck2a(self):
        """Basic Sphinx test. Output directory is an absolute directory
        """
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['OutputPath'] = os.path.join(self.TEST_FILE_DIR, '_build', 'html')
        self.testText = """****
head
****

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck2b(self):
        """Check for double builds.
        """
        self._doBasicSphinxConfig()
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        # After the inital ``_clear`` then a build with text, we expect to
        # see two builds.
        self.assertEqual(self._dock()._sphinxConverter._SphinxInvocationCount, 2)

        # Inserting a character when auto-save is enabled can cause a double
        # build: the save made in preparation for the first build also invokes
        # the second build.
        qp = core.workspace().currentDocument().qutepart
        core.config()['Sphinx']['BuildOnSave'] = False
        with self._WaitForHtmlReady(timeout=10000, numEmittedExpected=1):
            qp.lines[0] += ' '
        self.assertEqual(self._dock()._sphinxConverter._SphinxInvocationCount, 3)

        # Inserting a space at the end of the line can cause a double build,
        # since the StripTrailingWhitespace option deletes the space, then
        # the auto-save and build code restores it.
        #
        # However, double builds still only produce a single ``loadFinished``
        # signal.
        core.config()["Qutepart"]["StripTrailingWhitespace"] = True
        qp = core.workspace().currentDocument().qutepart
        with self._WaitForHtmlReady(timeout=10000, numEmittedExpected=1):
            qp.appendPlainText('\nTesting...')
        self.assertEqual(self._dock()._sphinxConverter._SphinxInvocationCount, 4)

    @requiresSphinx()
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck3a(self):
        """Basic Sphinx with CodeChat test. Output directory is a absolute
        directory.
        """
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['OutputPath'] = os.path.join(self.TEST_FILE_DIR, '_build', 'html')

        self.testText = """# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue('<p>content</p>' in webViewContent)

    @requiresSphinx()
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck3(self):
        """Basic Sphinx with CodeChat test: create a Sphinx project with codechat
        enabled."""
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()

        self.testText = """# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue('<p>content</p>' in webViewContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck4(self):
        """If Enki is opened without any configuration, the preview dock will
        not appear. This will not affect resT files or html files."""
        self.testText = 'test'
        self.createFile('file.py', self.testText)
        with self.assertRaisesRegex(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck5(self):
        """Basic Sphinx test: with Sphinx and codechat disabled, no preview
           window results are generated."""
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['Enabled'] = False
        self.testText = """****
head
****

content"""
        self._doBasicSphinxTest('rst')
        self.assertNotIn('<h1>head', self._widget().webView.page().mainFrame().toHtml())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck6(self):
        """If an empty code file is passed to Enki, the CodeChat preview panel
           should be empty."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = ''
        self._doBasicTest('py')
        self.assertEqual(self._plainText(), ' \n')

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck6a(self):
        """Empty code file produces a Sphinx failure since file in toctree should
           always have a header."""
        self._doBasicSphinxConfig()
        self.testText = ''
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue("doesn't have a title" in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck7(self):
        """Test that Unicode characters are handled properly.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = 'Енки'
        self._doBasicTest('py')
        # Plaintext captured from the preview dock will append a newline if
        # preview dock is not empty. A '\n' is added accordingly.
        self.assertEqual(self._plainText(), self.testText + '\n')

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck7a(self):
        """Unicode string passed to Sphinx should be handled properly.
        """
        self._doBasicSphinxConfig()
        self.testText = """**********
Енки
**********

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue("<h1>Енки" in webViewContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck8(self):
        """Start with a short code file, make sure the preview window isn't
           opened, then enable the CodeChat module and refresh Enki.
           The preview window should now be opened."""
        self.testText = 'test'
        self.createFile('file.py', self.testText)
        with self.assertRaisesRegex(AssertionError, 'Dock Previe&w not found'):
            self._dock()
        core.config()['CodeChat']['Enabled'] = True
        core.uiSettingsManager().dialogAccepted.emit()
        self._doBasicTest('py', numEmittedExpected=1)
        assert 'test' in self._html()

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck8a(self):
        """Start with Sphinx disabled, make sure rst file will be rendered by
        docutils.core.publish_string. Then enable Sphinx, force document refresh
        by calling scheduleDucomentProcessing. Make sure now Sphinx kicks in.
        """
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['Enabled'] = False
        self.testText = ''
        self._doBasicSphinxTest('rst')
        self.assertEqual(self._plainText(), '')
        self.assertEqual(self._logText(), '')

    @base.requiresCmdlineUtility('sphinx-build')
    @base.inMainLoop
    def test_previewCheck9b(self):
        """Empty code file should be rendered correctly with 'no title' warning.
        """
        self._doBasicSphinxConfig()
        self.testText = ''
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue("""doesn't have a title""" in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck9(self):
        """Uninterpretable reStructuredText syntax in source code will generate
           errors and be displayed in the output log window."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = '# .. wrong::'
        self._doBasicTest('py')
        self.assertTrue("""Unknown directive type "wrong".""" in self._logText())
        # do the same test for restructuredText
        self.testText = '.. wrong::'
        self._doBasicTest('rst')
        self.assertTrue("""Unknown directive type "wrong".""" in self._logText())

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck9a(self):
        """Test Sphinx error can be captured correctly"""
        self._doBasicSphinxConfig()
        self.testText = """****
head3
****

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue("Title overline too short" in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck10(self):
        """Empty input should generate an empty log.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = ''
        self._doBasicTest('py')
        self.assertEqual(self._logText(), '')
        # do the same test for restructuredText
        self._doBasicTest('rst')
        self.assertEqual(self._logText(), '')

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck11(self):
        """Unicode should display correctly in log window too.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = '# .. Енки::'
        self._doBasicTest('py')
        self.assertTrue('Енки' in self._logText())
        self.testText = '.. Енки::'
        self._doBasicTest('rst')
        self.assertTrue('Енки' in self._logText())

    @unittest.skip("Unicode isn't presented in the log window")
    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck12(self):
        """Unicode in log window while in Sphinx mode does not work since Sphinx
           error output is not in unicode.
        """
        self._doBasicSphinxConfig()
        self.testText = """****
head
****

.. Енки::"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        # Unicode cannot be found in Sphinx error message output.
        self.assertTrue('Енки' in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck13(self):
        """Test progress bar status (100%) when building reST / CodeChat.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.createFile('file.py', self.testText)
        self.assertEqual(self._widget().prgStatus.text(), 'Building...')

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck14(self):
        """Check different progressbar color given different scenarios.
        """
        core.config()['CodeChat']['Enabled'] = True
        # First, First, working code with no errors or warnings.
        self.testText = 'abc'
        self._doBasicTest('rst')
        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QLabel {}')

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck15(self):
        core.config()['CodeChat']['Enabled'] = True
        # Next, test a code piece with only warnings.
        self.testText = '`abc'
        self._doBasicTest('rst')
        self.assertTrue('#FF9955' in self._widget().prgStatus.styleSheet())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck16(self):
        core.config()['CodeChat']['Enabled'] = True
        # Next, test a code piece with only errors.
        self.testText = '# .. ERROR::'
        self._doBasicTest('py')
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck17(self):
        """A complex test case that tests both the log parser regexp and
        the progress bar color when both warnings and errors are present.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = '# .. ERROR::\n# `WARNING_'
        self._doBasicTest('py')
        ps = self._widget().prgStatus
        self.assertIn('red', ps.styleSheet())
        self.assertIn('Error(s): 2, warning(s): 2', ps.text())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck18(self):
        """Switching between different files should update the log
        window accordingly.
        """
        core.config()['CodeChat']['Enabled'] = True
        # First create a warning only test case,
        document1 = self.createFile('file1.py', '# `<>_')
        # then an error only case,
        document2 = self.createFile('file2.py', '# .. h::')
        # then an error free case. Wait for the HTML to be generated before
        # continuing, so that the next assertHtmlReady won't accidentally catch
        # the HTML ready generated here.
        with self._WaitForHtmlReady():
            document3 = self.createFile('file3.py', '# <>_')
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)

        # switch to document 1
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        ps = self._widget().prgStatus
        self.assertIn('#FF9955', ps.styleSheet())
        self.assertIn('Error(s): 0, warning(s): 1', ps.text())
        # switch to document 2
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        self.assertIn('red', ps.styleSheet())
        self.assertIn('Error(s): 1, warning(s): 0', ps.text())
        # switch to document 3
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QLabel {}')
        self.assertEqual(self._logText(), '')

    @requiresSphinx()
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck19(self):
        """Check Advanced Mode. In this case Advanced Mode does not have
        space in its path.
        """
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['AdvancedMode'] = True
        core.config()['Sphinx']['Cmdline'] = r'sphinx-build -d ' + os.path.join('_build', 'doctrees') \
                                             + ' . ' + os.path.join('_build', 'html')

        self.testText = """# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue('<p>content</p>' in webViewContent)

    @requiresSphinx()
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck20(self):
        """Check space in path name. Advanced mode is not enabled.
        """
        core.config()['CodeChat']['Enabled'] = True
        testFileDir = self.TEST_FILE_DIR
        self.TEST_FILE_DIR = os.path.join(self.TEST_FILE_DIR, 'a b')
        if not os.path.exists(self.TEST_FILE_DIR):
            os.makedirs(self.TEST_FILE_DIR)
        self._doBasicSphinxConfig()

        self.testText = """# ****
# head
# ****
#
# content"""
        try:
            webViewContent, logContent = self._doBasicSphinxTest('py')
        finally:
            self.TEST_FILE_DIR = testFileDir
        self.assertTrue('<p>content</p>' in webViewContent)

    @requiresSphinx()
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck20a(self):
        """Check spaces in path name. Advanced mode is enabled.
        """
        core.config()['CodeChat']['Enabled'] = True
        testFileDir = self.TEST_FILE_DIR
        self.TEST_FILE_DIR = os.path.join(self.TEST_FILE_DIR, 'a b')
        if not os.path.exists(self.TEST_FILE_DIR):
            os.makedirs(self.TEST_FILE_DIR)
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['AdvancedMode'] = True
        core.config()['Sphinx']['Cmdline'] = r'sphinx-build -d ' + os.path.join('_build', 'doctrees') \
                                             + ' "' + self.TEST_FILE_DIR \
                                             + '" ' + os.path.join('_build', 'html')

        self.testText = """# ****
# head
# ****
#
# content"""
        try:
            webViewContent, logContent = self._doBasicSphinxTest('py')
        finally:
            self.TEST_FILE_DIR = testFileDir
        self.assertTrue('<p>content</p>' in webViewContent)

    @requiresSphinx()
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck21(self):
        """When user hit ok button in setting window, the project will get
        rebuild.
        """
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()

        self.testText = """# ****
# head
# ****
#
# :doc:`missing.file`"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue('<span class="xref doc">missing.file</span>' in webViewContent)
        self.assertTrue('unknown document: missing.file' in logContent)
        core.config()['Sphinx']['Enabled'] = False
        core.uiSettingsManager().dialogAccepted.emit()
        self._assertHtmlReady(lambda: None, timeout=10000,
                              numEmittedExpected=1)
        self.assertTrue('Unknown interpreted text role "doc"' in self._logText())

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck22(self):
        """ Assume codechat is not installed, render a .rst file using
        restructuredText and then render using sphinx.
        """
        with ImportFail(['CodeChat']):
            self.testText = 'Underlying :download:`source code <file.rst>`.'
            self._doBasicTest('rst')
            self.assertTrue('Unknown interpreted text role "download".' in self._logText())
            self.assertTrue('red' in self._widget().prgStatus.styleSheet())

            self._doBasicSphinxConfig()
            core.uiSettingsManager().dialogAccepted.emit()
            self._assertHtmlReady(lambda: None, timeout=10000,
                                  numEmittedExpected=1)
            self.assertTrue("document isn't included in any toctree" in self._logText())
            self.assertTrue('#FF9955' in self._widget().prgStatus.styleSheet())

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck23(self):
        """If the document is modified externally, then build on save will be
        automatically enabled. Calling scheduledocumentprocessing will not
        trigger a rebuild.
        """
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['BuildOnSave'] = False
        core.config().flush()
        self.codeText = """****
head
****

"""
        self.masterText = """.. toctree::

   code.rst"""
        codeDoc = self.createFile('code.rst', self.testText)
        masterDoc = self.createFile('index.rst', self.testText)
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(codeDoc), timeout=10000)
        # Modify this file externally.
        with open("code.rst", 'a') as f:
            f.write(".. mytag::")
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(masterDoc), timeout=10000)
        core.workspace().setCurrentDocument(codeDoc)

        # Modify this file internally, then wait for the typing timer to expire.
        qp = core.workspace().currentDocument().qutepart
        self.assertEmits(lambda: qp.appendPlainText('xxx'),
                         self._dock()._typingTimer.timeout, timeoutMs=1000)
        # The typing timer invokes _scheduleDocumentProcessing. Make sure
        # it completes by waiting until all events are processed.
        base._processPendingEvents()
        # Make sure the file wasn't saved.
        self.assertTrue(qp.document().isModified())

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck24(self):
        self._doBasicSphinxConfig()
        self.testText = """# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertFalse(os.path.isfile(os.path.join(self.TEST_FILE_DIR, 'CodeChat.css')))

    @requiresSphinx()
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck20a(self):
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()

        self.testText = """# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue(os.path.isfile(os.path.join(self.TEST_FILE_DIR, 'CodeChat.css')))

    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck25(self):
        """If the file to be previewed is older than the source, an error
        should appear."""
        # First, run Sphinx and generate some output.
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['BuildOnSave'] = False
        core.config().flush()
        self.testText = 'Testing'
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue('Testing' in webViewContent)

        # Now, exclude this from the build and re-run.
        conf = os.path.join(self.TEST_FILE_DIR, 'conf.py')
        with open(conf, 'a') as f:
            f.write('\n\nexclude_patterns = ["code.rst"]')
        # Run Sphinx again.
        qp = core.workspace().currentDocument().qutepart
        self._assertHtmlReady(lambda: qp.appendPlainText('xxx'),
                              timeout=10000)
        webViewContent, logContent = (self._html(), self._logText())
        self.assertIn('is older than the source file', webViewContent)

    @patch('os.path.getmtime')
    @requiresSphinx()
    @base.inMainLoop
    def test_previewCheck25(self, _getmtime):
        """Check exception handling in date comparison code."""
        # Make getmtime fail.
        _getmtime.side_effect = OSError()
        # First, run Sphinx and generate some output.
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['BuildOnSave'] = False
        core.config().flush()
        self.testText = 'Testing'
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertIn('modification', webViewContent)

    # Cases testing logwindow splitter
    # --------------------------------
    # Log splitter has three features:
    #
    # #. When created, different files will have same default splitter size
    #
    # #. Changing one file's splitter size will affect the other file's splitter
    #    size.
    #
    # #. If three files are present, with one of them error-free, then the splitter
    #    size will be the same only between those files with building errors.
    #
    # The following test cases will test all three features with one special cases:
    #
    # #. User hide splitter size. Then switch to another error-free document.
    #    Switch back. Will log window keep hidden?

    @base.inMainLoop
    def test_logWindowSplitter1(self):
        """Feature 1. Created files will have same splitter size.
        """
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '.. file2::')
        document3 = self.createFile('file3.rst', '.. file3::')
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        # Store default splitter size
        defaultSplitterSize = self._widget().splitter.sizes()
        self.assertTrue(defaultSplitterSize[1])
        # Switch to other two documents, they should have the same splitter size
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        self.assertEqual(self._widget().splitter.sizes(), defaultSplitterSize)
        # Check splitter size of document 2.
        # Switch to other two documents, they should have the same splitter size
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        self.assertEqual(self._widget().splitter.sizes(), defaultSplitterSize)

    @base.inMainLoop
    def test_logWindowSplitter2(self):
        """Feature 2. All build-with-error files' splitter size are connected.
        """
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '.. file2::')
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        # Change splitter location of document 2.
        newSplitterSize = [124, 123]
        self._widget().splitter.setSizes(newSplitterSize)
        # Calling setSizes directly will not trigger splitter's ``splitterMoved``
        # signal. We need to manually emit this signal with two arguments (not
        # important here.)
        self._widget().splitter.splitterMoved.emit(newSplitterSize[0], 1)
        # Assert preview window and log window are visible and are of almost equal size
        self.assertNotIn(0, self._widget().splitter.sizes())
        self.assertAlmostEqual(self._widget().splitter.sizes()[0], self._widget().splitter.sizes()[1], delta=10)
        # Switch to document 1, make sure its splitter size is changed, too.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        self.assertNotIn(0, self._widget().splitter.sizes())
        self.assertAlmostEqual(self._widget().splitter.sizes()[0], self._widget().splitter.sizes()[1], delta=10)

    @base.inMainLoop
    def test_logWindowSplitter3(self):
        """Feature 3. Error free document will not affect other documents'
        splitter size.
        """
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '')
        document3 = self.createFile('file3.rst', '.. file3::')
        self._assertHtmlReady(lambda: None)
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        # Need to wait for events to be processed before the splitter sizes are
        # updated. `base._processPendingEvents()` doesn't help.
        QTest.qWait(100)
        defaultSplitterSize = self._widget().splitter.sizes()
        self.assertTrue(defaultSplitterSize[1])
        # Switch to document 2. Log window is hidden now.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        self.assertFalse(self._widget().splitter.sizes()[1])
        # Switch to document 3. Log window should be restore to original size.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        self.assertTrue(self._widget().splitter.sizes()[0])
        self.assertEqual(self._widget().splitter.sizes(), defaultSplitterSize)

    @base.inMainLoop
    def test_logWindowSplitter3a(self):
        """Feature 1,2,3. A combination of the above test cases.
        """
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '')
        document3 = self.createFile('file3.rst', '.. file3::')
        self._assertHtmlReady(lambda: None)
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        # Wait for events to process. See qWait comment above.
        QTest.qWait(100)
        # Change splitter setting of document 1.
        newSplitterSize = [125, 124]
        self._widget().splitter.setSizes(newSplitterSize)
        self._widget().splitter.splitterMoved.emit(newSplitterSize[0], 1)
        # Assert log window and preview window are visible and are of almost
        # equal size.
        self.assertNotIn(0, self._widget().splitter.sizes())
        self.assertAlmostEqual(self._widget().splitter.sizes()[0], self._widget().splitter.sizes()[1], delta=10)
        # Switch to an error-free document, assert log window hidden.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        # Wait for events to process. See qWait comment above.
        QTest.qWait(100)
        self.assertFalse(self._widget().splitter.sizes()[1])
        # Switch to file3 which will cause build error, check splitter size.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        self.assertNotIn(0, self._widget().splitter.sizes())
        self.assertAlmostEqual(self._widget().splitter.sizes()[0], self._widget().splitter.sizes()[1], delta=10)

    @base.inMainLoop
    def test_logWindowSplitter4(self):
        """User actively hide log window, Enki should be able to remember this.
        """
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '')
        document3 = self.createFile('file3.rst', '.. file3::')
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        # Wait for events to process. See qWait comment above.
        QTest.qWait(100)
        # User manually change error state splitter size such that log window
        # is hidden.
        self._widget().splitter.setSizes([1, 0])
        self._widget().splitter.splitterMoved.emit(1, 1)
        # Switch to document 2. Log window is hidden now.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        # Wait for events to process. See qWait comment above.
        QTest.qWait(100)
        self.assertFalse(self._widget().splitter.sizes()[1])
        # Switch to document 3. Log window should keep hidden.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        # Wait for events to process. See qWait comment above.
        QTest.qWait(100)
        self.assertFalse(self._widget().splitter.sizes()[1])

    @base.inMainLoop
    def test_zoom(self):
        webView = self._widget().webView
        self.assertEqual(webView.zoomFactor(), 1)

        def makeEv(delta):
            return QWheelEvent(QPointF(10, 10), QPointF(webView.mapToGlobal(QPoint(10, 10))),
                               QPoint(0, 0), QPoint(0, delta),
                               delta,
                               Qt.Horizontal,
                               Qt.NoButton,
                               Qt.ControlModifier)
        zoom_out = makeEv(-120)
        zoom_in = makeEv(120)

        QApplication.instance().sendEvent(webView, zoom_out)
        self.assertTrue(0.85 < webView.zoomFactor() < 0.95)

        QApplication.instance().sendEvent(webView, zoom_in)
        self.assertTrue(0.95 < webView.zoomFactor() < 1.05)

        QApplication.instance().sendEvent(webView, zoom_in)
        self.assertTrue(1.05 < webView.zoomFactor() < 1.15)

    @requiresSphinx()
    @base.inMainLoop
    def test_saveAndBuildWhitespace1(self):
        """See if whitespace is preserved on the current line
           when auto build and save is enabled."""
        # Get Sphinx auto-save-and-build plus strip trailing whitespace set up.
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['BuildOnSave'] = False
        core.config()["Qutepart"]["StripTrailingWhitespace"] = True
        self.testText = "testing "
        webViewContent, logContent = self._doBasicSphinxTest('rst')

        # Move to the end of the document and add a space on the next line,
        # which should be preserved through the auto-save. The space at the
        # end of the first line should be removed.
        qp = core.workspace().currentDocument().qutepart
        # The format is line, column. This goes to the next line ???
        qp.cursorPosition = 0, len(self.testText)
        with self._WaitForHtmlReady(timeout=5000, numEmittedExpected=1):
            qp.appendPlainText(' ')
            self.assertTrue(qp.document().isModified())
        self.assertEqual(qp.text, "testing\n ")
        self.assertFalse(qp.document().isModified())

    @base.requiresModule('markdown')
    @base.inMainLoop
    def test_preview_save(self):
        """Save the HTML shown in the preview window."""
        self.testText = 'Testing 1, 2, 3...'
        self._doBasicTest('md')
        path = os.path.join(self.TEST_FILE_DIR, 'test.html')
        self._dock()._previewSave(path)
        with open(path, 'r', encoding='utf-8') as f:
            self.assertIn(self.testText, f.read())

    @base.requiresModule('docutils')
    @base.inMainLoop
    def test_rst_include(self):
        """Check that the .. include:: directive works."""
        includeText = 'Unicode test: Енки'
        self.createFile('inc.rst', includeText)
        self.testText = '.. include:: inc.rst'
        self._doBasicTest('rst')
        with open('inc.rst', 'r', encoding='utf-8') as f:
            self.assertIn(includeText, f.read())



#
# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main(verbosity=2)
