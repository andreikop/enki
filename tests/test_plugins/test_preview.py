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
import stat
import codecs

# Local application imports
# -------------------------
# Do this before PyQt imports so that base will set up sip API correctly.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

# Third-party library imports
# ---------------------------
from PyQt4.QtGui import QMessageBox
import mock

# Local application imports
# -------------------------
from enki.core.core import core
# Both of the two following lines are needed: the first, so we can later
# ``reload(enki.plugins.preview)``; the last, to instiantate ``SettingsWidget``.
import enki.plugins.preview
from enki.plugins.preview import SettingsWidget
from enki.plugins.preview import commonPrefix
from enki.plugins.preview.preview import copyTemplateFile
from import_fail import ImportFail
from enki.plugins.preview import _getSphinxVersion


# Preview module tests
# ====================

# Decorating each test function which needs it with
# @base.requiresCmdlineUtility('sphinx-build --version')
# makes the tests slow: using
# ``python -m profile -s cumtime test_preview_sync.py`` showed almost
# 7 seconds spend running this command. So, run it once here then re-use
# this value.
requiresSphinx = base.requiresCmdlineUtility('sphinx-build --version')


class PreviewTestCase(base.TestCase):
    """A class of utilities used to aid in testing the preview module."""

    def setUp(self):
        base.TestCase.setUp(self)
        self.testText = 'The preview text'
        # Open the preview dock by loading an html file.
        self.createFile('dummy.html', '')


    def _dock(self):
        """Find then return the PreviewDock object. Fail if
        it is not found."""
        return self.findVisibleDock('Previe&w')

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

    def _assertHtmlReady(self, start, timeout=2000):
        """Wait for the PreviewDock to load in updated HTML after the start
        function is called. Assert if the signal isn't emitted within a timeout.
        """
        # Wait for the worker thread to signal that it's produced
        # updated HTML.
        self.assertEmits(start, self._widget().webView.page().mainFrame().loadFinished, timeout)
        # Process any pending messages to make sure the GUI is up to
        # date. Omitting this causes failures in test_uiCheck17.
        base._processPendingEvents()

    def _doBasicTest(self, extension, name='file'):
        # HTML files don't need processing in the worker thread.
        if extension != 'html':
            self._assertHtmlReady(lambda: self.createFile('.'.join([name, extension]),
                                                          self.testText))

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
        self._assertHtmlReady(lambda : self.createFile('.'.join([name, extension]),
                                                       self.testText), timeout=10000)
        return self._html(), self._logText()

class Test(PreviewTestCase):
    @base.requiresModule('CodeChat')
    def test_emptyCodeChatDocument(self):
        core.config()['CodeChat']['Enabled'] = True
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    @requiresSphinx
    def test_emptySphinxDocument(self):
        core.config()['Sphinx']['Enabled'] = True
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    def test_emptyDocument(self):
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    @base.inMainLoop
    def test_html(self):
        self._doBasicTest('html')
        self.assertFalse(self._widget().prgStatus.isVisible())

    @base.requiresModule('docutils')
    @base.inMainLoop
    def test_rst(self):
        self._doBasicTest('rst')

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

        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('Default')))
        self.assertFalse('body {color: white; background: black;}' in self._plainText())
        self.assertFalse('body {color: white; background: black;}' in self._html())
        self.assertEqual(core.config()['Preview']['Template'], 'Default')

        self._assertHtmlReady(lambda: combo.setCurrentIndex(combo.findText('WhiteOnBlack')))
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
    ##-----------------------------------------
    @base.requiresModule('CodeChat')
    def test_settingUiCheck1(self):
        """When Enki runs for the first time, the CodeChat module should be
           disabled by default."""
        sw = SettingsWidget()
        self.assertFalse(sw.gbCodeChat.isChecked())
        self.assertTrue(sw.gbCodeChat.isEnabled())
        # If the CodeChat module is present, the user should not be able to see
        # the 'CodeChat not installed' notification.
        #
        # Widgets that are not on the top level will be visible only when all their
        # ancesters are visible. Check `here <http://qt-project.org/doc/qt-5/qwidget.html#visible-prop>`_
        # for more details. Calling show() function will force update on
        # setting ui.
        sw.show()
        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
        sw.close()

    @base.requiresModule('CodeChat')
    def test_settingUiCheck3(self):
        """ The Enable CodeChat checkbox should only be enabled if CodeChat can
            be imported; otherwise, it should be disabled."""
        # Trick Python into thinking that the CodeChat module doesn't exist.
        # Verify that the CodeChat checkbox is disabled, and the 'not installed'
        # notification is visible.
        with ImportFail(['CodeChat'], [enki.plugins.preview]):
            sw = SettingsWidget()
            self.assertFalse(sw.cbCodeChat.isEnabled())
            sw.show()
            self.assertTrue(sw.labelCodeChatNotInstalled.isVisible())
            self.assertTrue(sw.labelCodeChatNotInstalled.isEnabled())
            self.assertTrue(sw.labelCodeChatIntro.isEnabled())
            sw.close()

        # Now, prove that the reload worked: CodeChat should now be enabled, but
        # remain unchecked just like the first time enki starts. 'not installed'
        # notification should be invisible.
        sw = SettingsWidget()
        self.assertTrue(sw.cbCodeChat.isEnabled())
        sw.show()
        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
        self.assertTrue(sw.labelCodeChatIntro.isEnabled())
        sw.close()

    @requiresSphinx
    def test_settingUiCheck3a(self):
        """test_uiCheck1a has tested the case when Sphinx is disabled. This
        unit test will test the case when Sphinx is mannually enabled.
        """
        sw = SettingsWidget()
        # Mannually enable Sphinx.
        sw.gbSphinxProject.setChecked(True)
        # Since it is assumed that the user has sphinx-build installed, the Sphinx
        # executable, output extension and default commandline will be initialize
        # to preset values.
        self.assertTrue(sw.gbSphinxProject.isChecked())
        # Build option is enabled and automatically set to Build only on save.
        self.assertTrue(sw.rbBuildOnlyOnSave.isEnabled())
        self.assertTrue(sw.rbBuildOnlyOnSave.isChecked())
        self.assertTrue(sw.rbBuildOnFileChange.isEnabled())
        self.assertFalse(sw.rbBuildOnFileChange.isChecked())
        # All setting directories are enabled and empty.
        self.assertTrue(sw.leSphinxProjectPath.isEnabled())
        self.assertEqual(sw.leSphinxProjectPath.text(), '')
        self.assertTrue(sw.leSphinxOutputPath.isEnabled())
        self.assertEqual(sw.leSphinxOutputPath.text(), '')
        # Executable is enabled and set to default 'sphinx-build'
        self.assertTrue(sw.leSphinxExecutable.isEnabled())
        self.assertEqual(sw.leSphinxExecutable.text(), '')
        # Assert advanced mode toggle label enabled and reads 'Advanced Mode'
        self.assertTrue(sw.lbSphinxEnableAdvMode.isEnabled())
        self.assertTrue('Advanced Mode' in sw.lbSphinxEnableAdvMode.text())
        sw.show()
        # Assert user cannot see any advanced setting items.
        self.assertFalse(sw.lbSphinxCmdline.isVisible())
        self.assertFalse(sw.leSphinxCmdline.isVisible())
        self.assertFalse(sw.lbSphinxReference.isVisible())
        sw.close()

        # Now simulate a keypress event on advanced setting toggle label
        sw.lbSphinxEnableAdvMode.mousePressEvent()
        # Verify that in advanced setting mode, default command line commands are used.
        self.assertEqual(sw.leSphinxCmdline.text(), u'')
        # Assert advanced model toggle label now reads 'Normal Mode'
        self.assertTrue('Normal Mode' in sw.lbSphinxEnableAdvMode.text())
        sw.show()
        # Verify that normal mode setting line edits and pushbuttons are all gone
        for i in range(sw.gridLtNotAdvancedSettings.count()):
            self.assertFalse(sw.gridLtNotAdvancedSettings.itemAt(i).widget().isVisible())
        # Verify advanced mode setting line edits and labels are visible.
        self.assertTrue(sw.lbSphinxCmdline.isVisible())
        self.assertTrue(sw.leSphinxCmdline.isVisible())
        self.assertTrue(sw.lbSphinxReference.isVisible())
        sw.close()

    # Cases for code preview using Codechat or Sphinx
    ##-----------------------------------------------
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck1(self):
        """If Enki is opened with CodeChat enabled, the preview dock should be
           found."""
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicTest('py')
        self._dock()
        self.assertTrue(self._widget().prgStatus.isVisible())

    @requiresSphinx
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

    @requiresSphinx
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

    @requiresSphinx
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck3a(self):
        """Basic Sphinx with CodeChat test. Output directory is a absolute
        directory.
        """
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['OutputPath'] = os.path.join(self.TEST_FILE_DIR, '_build', 'html')

        self.testText = u"""# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue(u'<p>content</p>' in webViewContent)
        self.assertTrue(u'Processing code.py to code.py.rst' in logContent)

    @requiresSphinx
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck3(self):
        """Basic Sphinx with CodeChat test: create a Sphinx project with codechat
        enabled."""
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()

        self.testText = u"""# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue(u'<p>content</p>' in webViewContent)
        self.assertTrue(u'Processing code.py to code.py.rst' in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck4(self):
        """If Enki is opened without any configuration, the preview dock will
        not appear. This will not affect resT files or html files."""
        self.testText = u'test'
        self._doBasicTest('py')
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    @requiresSphinx
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
        # After calling doBasicSphinxText, self._dock() can't be found.
        # So, save it here.
        d = self._dock()
        self._doBasicSphinxTest('rst')
        self.assertNotIn('<h1>head', d._widget.webView.page().mainFrame().toHtml())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck6(self):
        """If an empty code file is passed to Enki, the CodeChat preview panel
           should be empty."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u''
        self._doBasicTest('py')
        self.assertEqual(self._plainText(), self.testText)

    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck6a(self):
        """Empty code file produces a Sphinx failure since file in toctree should
           always have a header."""
        self._doBasicSphinxConfig()
        self.testText = u''
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(u"doesn't have a title" in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck7(self):
        """Test that Unicode characters are handled properly.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u'Енки'
        self._doBasicTest('py')
        # Plaintext captured from the preview dock will append a newline if
        # preview dock is not empty. A '\n' is added accordingly.
        self.assertEqual(self._plainText(), self.testText + '\n')

    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck7a(self):
        """Unicode string passed to Sphinx should be handled properly.
        """
        self._doBasicSphinxConfig()
        self.testText = u"""**********
Енки
**********

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(u"<h1>Енки" in webViewContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck8(self):
        """Start with a short code file, make sure the preview window isn't
           opened, then enable the CodeChat module and refresh Enki.
           The preview window should now be opened."""
        self.testText = u'test'
        self._doBasicTest('py')
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()
        core.config()['CodeChat']['Enabled'] = True
        core.uiSettingsManager().dialogAccepted.emit();
        self._doBasicTest('py')
        assert 'test' in self._html()


    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck8a(self):
        """Start with Sphinx disabled, make sure rst file will be rendered by
        docutils.core.publish_string. Then enable Sphinx, force document refresh
        by calling scheduleDucomentProcessing. Make sure now Sphinx kicks in.
        """
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['Enabled'] = False
        self.testText = u''
        self._doBasicSphinxTest('rst')
        self.assertEqual(self._plainText(), '')
        self.assertEqual(self._logText(), '')

    @base.requiresCmdlineUtility('sphinx-build')
    @base.inMainLoop
    def test_previewCheck9b(self):
        """Empty code file should be rendered correctly with 'no title' warning.
        """
        self._doBasicSphinxConfig()
        self.testText = u''
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(u"""doesn't have a title""" in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck9(self):
        """Uninterpretable reStructuredText syntax in source code will generate
           errors and be displayed in the output log window."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u'# .. wrong::'
        self._doBasicTest('py')
        self.assertTrue("""Unknown directive type "wrong".""" in self._logText())
        # do the same test for restructuredText
        self.testText = u'.. wrong::'
        self._doBasicTest('rst')
        self.assertTrue("""Unknown directive type "wrong".""" in self._logText())

    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck9a(self):
        """Test Sphinx error can be captured correctly"""
        self._doBasicSphinxConfig()
        self.testText = u"""****
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
        self.testText = u''
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
        self.testText = u'# .. Енки::'
        self._doBasicTest('py')
        self.assertTrue(u'Енки' in self._logText())
        self.testText = u'.. Енки::'
        self._doBasicTest('rst')
        self.assertTrue(u'Енки' in self._logText())

    @unittest.skip("Unicode isn't presented in the log window")
    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck12(self):
        """Unicode in log window while in Sphinx mode does not work since Sphinx
           error output is not in unicode.
        """
        self._doBasicSphinxConfig()
        self.testText = u"""****
head
****

.. Енки::"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        # Unicode cannot be found in Sphinx error message output.
        self.assertTrue(u'Енки' in logContent)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck13(self):
        """Test progress bar status (100%) when building reST / CodeChat.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.createFile('file.py', self.testText)
        self.assertEqual(self._widget().prgStatus.value(), 100)

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck14(self):
        """Check different progressbar color given different scenarios.
        """
        core.config()['CodeChat']['Enabled'] = True
        # First, First, working code with no errors or warnings.
        self.testText = u'abc'
        self._doBasicTest('rst')
        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QProgressBar::chunk {}')

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck15(self):
        core.config()['CodeChat']['Enabled'] = True
        # Next, test a code piece with only warnings.
        self.testText = u'`abc'
        self._doBasicTest('rst')
        self.assertTrue('#FF9955' in self._widget().prgStatus.styleSheet())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck16(self):
        core.config()['CodeChat']['Enabled'] = True
        # Next, test a code piece with only errors.
        self.testText = u'# .. ERROR::'
        self._doBasicTest('py')
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())

    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck17(self):
        """A complex test case that tests both the log parser regexp and
        the progress bar color when both warnings and errors are present.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u'# .. ERROR::\n# `WARNING_'
        self._doBasicTest('py')
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 2, error(s): 2' in self._logText())

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
        # then an error free case.
        document3 = self.createFile('file3.py', '# <>_')

        # switch to document 1
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        self.assertIn('#FF9955', self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 1, error(s): 0' in self._logText())
        # switch to document 2
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 0, error(s): 1' in self._logText())
        # switch to document 3
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QProgressBar::chunk {}')
        self.assertEqual(self._logText(), '')

    @requiresSphinx
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

        self.testText = u"""# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue(u'<p>content</p>' in webViewContent)
        self.assertTrue(u'Processing code.py to code.py.rst' in logContent)

    @requiresSphinx
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

        self.testText = u"""# ****
# head
# ****
#
# content"""
        try:
            webViewContent, logContent = self._doBasicSphinxTest('py')
        finally:
            self.TEST_FILE_DIR = testFileDir
        self.assertTrue(u'<p>content</p>' in webViewContent)
        self.assertTrue(u'Processing code.py to code.py.rst' in logContent)

    @requiresSphinx
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

        self.testText = u"""# ****
# head
# ****
#
# content"""
        try:
            webViewContent, logContent = self._doBasicSphinxTest('py')
        finally:
            self.TEST_FILE_DIR = testFileDir
        self.assertTrue(u'<p>content</p>' in webViewContent)
        self.assertTrue(u'Processing code.py to code.py.rst' in logContent)

    @requiresSphinx
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck21(self):
        """When user hit ok button in setting window, the project will get
        rebuild.
        """
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()

        self.testText = u"""# ****
# head
# ****
#
# :doc:`missing.file`"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue(u'<span class="pre">missing.file</span>' in webViewContent)
        self.assertTrue(u'unknown document: missing.file' in logContent)
        core.config()['Sphinx']['Enabled'] = False
        core.uiSettingsManager().dialogAccepted.emit()
        self._assertHtmlReady(lambda: None, timeout = 10000)
        self.assertTrue(u'Unknown interpreted text role "doc"' in self._logText())

    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck22(self):
        """ Assume codechat is not installed, render a .rst file using
        restructuredText and then render using sphinx.
        """
        with ImportFail(['CodeChat']):
            self.testText = u'Underlying :download:`source code <file.rst>`.'
            self._doBasicTest('rst')
            self.assertTrue(u'Unknown interpreted text role "download".' in self._logText())
            self.assertTrue('red' in self._widget().prgStatus.styleSheet())

            self._doBasicSphinxConfig()
            core.uiSettingsManager().dialogAccepted.emit()
            self._assertHtmlReady(lambda: None, timeout = 10000)
            self.assertTrue(u"document isn't included in any toctree" in self._logText())
            self.assertTrue('#FF9955' in self._widget().prgStatus.styleSheet())

    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck23(self):
        """If the document is modified externally, then build on save will be
        automatically enabled. Calling scheduledocumentprocessing will not
        trigger a rebuild.
        """
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['BuildOnSave'] = False
        core.config().flush()
        self.codeText = u"""****
head
****

"""
        self.masterText = u""".. toctree::

   code.rst"""
        codeDoc = self.createFile('code.rst', self.testText)
        masterDoc = self.createFile('index.rst', self.testText)
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(codeDoc), timeout=10000)
        # Modify this file externally.
        with open("code.rst", 'a') as f:
            f.write (".. mytag::")
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

    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck24(self):
        self._doBasicSphinxConfig()
        self.testText = u"""# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertFalse(os.path.isfile(os.path.join(self.TEST_FILE_DIR, 'CodeChat.css')))

    @requiresSphinx
    @base.requiresModule('CodeChat')
    @base.inMainLoop
    def test_previewCheck20a(self):
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicSphinxConfig()

        self.testText = u"""# ****
# head
# ****
#
# content"""
        webViewContent, logContent = self._doBasicSphinxTest('py')
        self.assertTrue(os.path.isfile(os.path.join(self.TEST_FILE_DIR, 'CodeChat.css')))

    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck25(self):
        """If the file to be previewed is older than the source, an error
        should appear."""
        # First, run Sphinx and generate some output.
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['BuildOnSave'] = False
        core.config().flush()
        self.testText = u'Testing'
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(u'Testing' in webViewContent)

        # Now, exclude this from the build and re-run.
        conf = os.path.join(self.TEST_FILE_DIR, 'conf.py')
        with open(conf, 'a') as f:
            f.write('\n\nexclude_patterns = ["code.rst"]')
        # Run Sphinx again.
        qp = core.workspace().currentDocument().qutepart
        self._assertHtmlReady(lambda: qp.appendPlainText('xxx'),
                              timeout=10000)
        webViewContent, logContent = (self._html(), self._logText())
        self.assertIn(u'is older than the source file', webViewContent)

    @mock.patch('os.path.getmtime')
    @requiresSphinx
    @base.inMainLoop
    def test_previewCheck25(self, _getmtime):
        """Check exception handling in date comparison code."""
        # Make getmtime fail.
        _getmtime.side_effect=OSError()
        # First, run Sphinx and generate some output.
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['BuildOnSave'] = False
        core.config().flush()
        self.testText = u'Testing'
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertIn(u'modification', webViewContent)


    # Cases testing commonprefix
    ##--------------------------
    # Basic checks
    def test_commonPrefix1(self):
        self.assertEqual(commonPrefix('a', 'a'), 'a')

    def test_commonPrefix2(self):
        self.assertEqual(commonPrefix('a', 'b'), '')

    def test_commonPrefix3(self):
        self.assertEqual(commonPrefix('', 'a'), '')

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    # Test using various path separators.
    def test_commonPrefix5(self):
        self.assertEqual(commonPrefix('a\\b', 'a\\b'), os.path.join('a','b'))

    def test_commonPrefix6(self):
        self.assertEqual(commonPrefix('a/b', 'a/b'), os.path.join('a','b'))

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix7(self):
        self.assertEqual(commonPrefix('a/b', 'a\\b'), os.path.join('a','b'))

    # Check for the bug in os.path.commonprefix.
    def test_commonPrefix8(self):
        self.assertEqual(commonPrefix(os.path.join('a', 'bc'), os.path.join('a','b')), 'a')

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix9(self):
        self.assertEqual(commonPrefix('a\\b\\..', 'a\\b'), 'a')

    def test_commonPrefix9a(self):
        self.assertEqual(commonPrefix('a/b/..', 'a/b'), 'a')

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix10(self):
        self.assertEqual(commonPrefix('a\\.\\b', 'a\\b'), os.path.join('a','b'))

    def test_commonPrefix10a(self):
        self.assertEqual(commonPrefix('a/./b', 'a/b'), os.path.join('a','b'))

    def test_commonPrefix11(self):
        """Check that leading ../current_subdir will be removed after path
           clearnup."""
        # Get the name of the current directory
        d = os.path.basename(os.getcwd())
        self.assertEqual(commonPrefix('../' + d + '/a/b', 'a/b'), os.path.join('a','b'))

    def test_commonPrefix11a(self):
        # if any input directory is abs path, return abs commonprefix
        d1 = os.path.join(os.getcwd(), 'a1')
        self.assertEqual(commonPrefix(d1, 'a2'), os.path.normcase(os.getcwd()))

    # Test for paths with spaces (Windows version)
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix12(self):
        # Cases like this only applies to Windows. Since Unix separator
        # is not '\\' but '/'. Unix will treat '\\' as part of file name.
        self.assertEqual(commonPrefix('a a\\b b\\c c', 'a a\\b b'), os.path.join('a a','b b'))

    # Test for paths with spaces (Platform independent version)
    def test_commonPrefix12a(self):
        # Cases like this only applies to Windows. Since Unix separator
        # is not '\\' but '/'. Unix will treat '\\' as part of file name.
        self.assertEqual(commonPrefix(os.path.join('a a', 'b b', 'c c'), os.path.join('a a', 'b b')), os.path.join('a a','b b'))

    # Test for paths with different cases (Windows only)
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_commonPrefix13(self):
        self.assertEqual(commonPrefix('aa\\bb', 'Aa\\bB'), os.path.join('aa','bb'))

    def test_commonPrefix14(self):
        # Empty input list should generate empty result
        self.assertEqual(commonPrefix(), '')

    def test_commonPrefix15(self):
        # if current working directory is 'a/b', for ".." and "", what part is
        # the commonprefix? It should be an absolute path "a"
        self.assertEqual(commonPrefix('..', ''), os.path.normcase(os.path.dirname(os.getcwd())))

    def test_commonPrefix16(self):
        # commonPrefix use the assumption that all relativepaths are based on
        # current working directory. If the resulting common prefix does not
        # have current workign directory as one of its parent directories, then
        # the absolute path will be used.
        self.assertEqual(commonPrefix(os.path.join('..', 'AVeryLongFileName'),
                                      os.path.join('..', 'AVeryLongFileName')),
         os.path.normcase(os.path.abspath(os.path.join('..', 'AVeryLongFileName'))))

    # TODO: need symbolic link test case.

    # Cases testing copyTemplateFile
    ##------------------------------
    # Basic checks
    # TODO: Do we need to modularize these test cases? It seems we have many
    # tunable parameters, yet all testcases look alike.
    def test_copyTemplateFile1(self):
        # copyTemplateFile has function header:
        # ``copyTemplateFile(errors, source, templateFileName, dest, newName=None)``
        # Basic test would be copy one ``file`` from one valid source directory
        # to a valid ``dest`` directory with no ``newName`` or ``error``.
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        copyTemplateFile(errors, source, 'dummy.html', dest)
        self.assertEqual(errors, [])
        self.assertTrue(os.path.isfile(os.path.join(source, 'dummy.html')))
        self.assertTrue(os.path.isfile(os.path.join(dest, 'dummy.html')))

    def test_copyTemplateFile2(self):
        # Test invalid source directory.
        source = os.path.join(self.TEST_FILE_DIR, 'invalid')
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        copyTemplateFile(errors, source, 'missing.file', dest)
        self.assertNotEqual(filter(lambda x: x.startswith("[Errno 2] No such file or directory"),
                                   errors[0]), ())

    def test_copyTemplateFile2a(self):
        # Test empty source directory.
        source = None
        dest = os.path.join(self.TEST_FILE_DIR, 'sub')
        os.makedirs(dest)
        errors = []
        with self.assertRaisesRegexp(OSError,
          "Input or output directory cannot be None"):
            copyTemplateFile(errors, source, 'missing.file', dest)

    def test_copyTemplateFile3(self):
        # Test invalid destination directory.
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        errors = []
        copyTemplateFile(errors, source, 'dummy.html', dest)
        self.assertNotEqual(filter(lambda x: x.startswith("[Errno 2] No such file or directory"),
                                   errors[0]), ())

    def test_copyTemplateFile3a(self):
        # Test empty destination directory.
        source = self.TEST_FILE_DIR
        dest = None
        errors = []
        with self.assertRaisesRegexp(OSError,
          "Input or output directory cannot be None"):
            copyTemplateFile(errors, source, 'dummy.html', dest)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_copyTemplateFile4(self):
        # Make target directory read only, causing access error (*nix only since
        # NTFS does not have Write-only property)
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        # Make the source file write only
        mode = os.stat(os.path.join(source, 'dummy.html'))[0]
        os.chmod(os.path.join(source, 'dummy.html'), stat.S_IWRITE)
        copyTemplateFile(errors, source, 'dummy.html', dest)
        # Restore source file's attribute
        os.chmod(os.path.join(source, 'dummy.html'), mode)
        self.assertNotEqual(filter(lambda x: "Permission denied" in x, errors[0]), ())

    def test_copyTemplateFile5(self):
        # Test the fifth argument of copyTemplateFile: newName, that will alter
        # copied file's name.
        source = self.TEST_FILE_DIR
        dest = os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        copyTemplateFile(errors, source, 'dummy.html', dest, 'newFile.name')
        self.assertEqual(errors, [])
        self.assertTrue(os.path.isfile(os.path.join(source, 'dummy.html')))
        self.assertTrue(os.path.isfile(os.path.join(dest, 'newFile.name')))

    # Cases testing logwindow splitter
    ##--------------------------------
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
        # User manually change error state splitter size such that log window
        # is hidden.
        self._widget().splitter.setSizes([1, 0])
        self._widget().splitter.splitterMoved.emit(1, 1)
        # Switch to document 2. Log window is hidden now.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        self.assertFalse(self._widget().splitter.sizes()[1])
        # Switch to document 3. Log window should keep hidden.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        self.assertFalse(self._widget().splitter.sizes()[1])

    def test_getSphinxVersion1(self):
        """Check that _getSphinxVersion raises an exception if the binary isn't
        present."""
        with self.assertRaises(OSError):
            _getSphinxVersion('this_executable_does_not_exist')

    # For mocking, mock an item where it is used, not where it came from. See
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch and
    # http://www.toptal.com/python/an-introduction-to-mocking-in-python.
    @mock.patch('enki.plugins.preview.get_console_output')
    def test_getSphinxVersion2(self, mock_gca):
        """Check that _getSphinxVersion raises an exception if the Sphinx
        version info isn't present."""
        mock_gca.return_value = ("stderr",
          "stdout - no version info here, sorry!")
        with self.assertRaises(ValueError):
            _getSphinxVersion('anything_since_replaced_by_mock')

    @mock.patch('enki.plugins.preview.get_console_output')
    def test_getSphinxVersion3(self, mock_gca):
        """Check that _getSphinxVersion raises an exception if the Sphinx
        version info isn't present."""
        mock_gca.return_value = ("stderr", \
"""Error: Insufficient arguments.

Sphinx v1.2.3
Usage: C:\Python27\Scripts\sphinx-build [options] sourcedir outdir [filenames...
]
""")
        self.assertEqual(_getSphinxVersion('anything_since_replaced_by_mock'),
                         [1, 2, 3])

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main(verbosity=2)
