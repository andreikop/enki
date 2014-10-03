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
import imp
import codecs

# Local application imports
# -------------------------
# Do this before PyQt imports so that base will set up sip API correctly.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

# Third-party library imports
# ---------------------------
from PyQt4.QtGui import QTextCursor

# Local application imports
# -------------------------
from enki.core.core import core
# Both of the two following lines are needed: the first, so we can later
# ``reload(enki.plugins.preview)``; the last, to instiantate ``SettingsWidget``.
import enki.plugins.preview
from enki.plugins.preview import SettingsWidget
from enki.plugins.preview.preview import commonPrefix
from enki.plugins.preview.preview import copyTemplateFile
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

    def _doBasicTest(self, extension):
        # HTML files don't need processing in the worker thread.
        if extension != 'html':
            self._assertHtmlReady(lambda: self.createFile('file.' + extension, self.testText))

    def _doBasicSphinxConfig(self):
        """This function will set basic Sphinx configuration options
        so that Sphinx can run in a test environment.
        """
        core.config()['Sphinx']['Enabled'] = True
        core.config()['Sphinx']['Executable'] = r'sphinx-build'
        core.config()['Sphinx']['ProjectPath'] = self.TEST_FILE_DIR
        core.config()['Sphinx']['OutputPath'] = os.path.join(self.TEST_FILE_DIR, '_build', 'html')
        core.config()['Sphinx']['OutputExtension'] = r'html'
        core.config()['Sphinx']['AdvancedMode'] = False

    def _doBasicSphinxTest(self, extension):
        """This function will build a basic Sphinx project in the temporary
        directory. The project consists of master document content.rst and a
        simple code document code.extension. Here the extension to the code
        file can be altered. For example, the extension can be set to .rst .
        """
        # Fill in conf.py and default.css file
        #enki.plugins.preview.copySphinxProjectTemplate()

        # Create master document index.rst
        master = os.path.join(self.TEST_FILE_DIR, 'index.rst')
        with codecs.open(master, 'wb', encoding='utf8') as file_:
            file_.write(""".. toctree::

   code.""" + extension)

        # Build the HTML, then return it and the log.
        self._assertHtmlReady(lambda : self.createFile('code.' + extension, self.testText), timeout=10000)
        return self._html(), self._logText()

class Test(PreviewTestCase):
    @requiresModule('CodeChat')
    def test_emptyCodeChatDocument(self):
        core.config()['CodeChat']['Enabled'] = True
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    @base.requiresCmdlineUtility('sphinx-build --version')
    def test_emptySphinxDocument(self):
        core.config()['Sphinx']['Enabled'] = True
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    def test_emptyDocument(self):
        core.workspace().createEmptyNotSavedDocument()
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    def test_html(self):
        self._doBasicTest('html')

    @requiresModule('docutils')
    def test_rst(self):
        self._doBasicTest('rst')

    @requiresModule('markdown')
    def test_markdown(self):
        self._doBasicTest('md')

    @requiresModule('markdown')
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

    @requiresModule('markdown')
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
    @requiresModule('CodeChat')
    def test_uiCheck1(self):
        """When Enki runs for the first time, the CodeChat module should be
           disabled by default."""
        sw = SettingsWidget()
        self.assertFalse(sw.cbCodeChatEnable.isChecked())
        self.assertTrue(sw.cbCodeChatEnable.isEnabled())
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

    @base.requiresCmdlineUtility('sphinx-build --version')
    def test_uiCheck1a(self):
        """By default, when Sphinx is available, it is set to be disabled. all
        path setting line edits and buttons are disabled."""
        sw = SettingsWidget()
        # Sphinx is enabled but unchecked.
        self.assertTrue(sw.cbSphinxEnable.isEnabled())
        self.assertFalse(sw.cbSphinxEnable.isChecked())
        # buildOnSave is not enabled nor checked.
        self.assertFalse(sw.cbBuildOnSaveEnable.isEnabled())
        self.assertFalse(sw.cbBuildOnSaveEnable.isChecked())
        # All setting directories are disabled and empty.
        self.assertFalse(sw.leSphinxProjectPath.isEnabled())
        self.assertEqual(sw.leSphinxProjectPath.text(), '')
        self.assertFalse(sw.leSphinxOutputPath.isEnabled())
        self.assertEqual(sw.leSphinxOutputPath.text(), '')
        # executable is disabled and set to default 'sphinx-build'
        self.assertFalse(sw.leSphinxExecutable.isEnabled())
        self.assertEqual(sw.leSphinxExecutable.text(), '')
        # builder extension is disabled and set to default 'html'
        self.assertFalse(sw.cmbSphinxOutputExtension.isEnabled())
        self.assertEqual(sw.cmbSphinxOutputExtension.lineEdit().text(), 'html')
        # Assert advanced mode toggle label disabled and reads 'Advanced Mode'
        self.assertFalse(sw.lbSphinxEnableAdvMode.isEnabled())
        self.assertTrue('Advanced Mode' in sw.lbSphinxEnableAdvMode.text())
        sw.show()
        # Assert user cannot see any advanced setting items.
        self.assertFalse(sw.lbSphinxCmdline.isVisible())
        self.assertFalse(sw.leSphinxCmdline.isVisible())
        self.assertFalse(sw.lbSphinxReference.isVisible())
        sw.close()

    @requiresModule('CodeChat')
    def test_uiCheck3(self):
        """ The Enable CodeChat checkbox should only be enabled if CodeChat can
            be imported; otherwise, it should be disabled."""
        # Trick Python into thinking that the CodeChat module doesn't exist.
        # Verify that the CodeChat checkbox is disabled, and the 'not installed'
        # notification is visible.
        with ImportFail('CodeChat'):
            reload(enki.plugins.preview)
            sw = SettingsWidget()
            enabled = sw.cbCodeChatEnable.isEnabled()
            sw.show()
            notice = sw.labelCodeChatNotInstalled.isVisible()
            sw.close()
        # When done with this test first restore the state of the preview module
        # by reloading with the CodeChat module available, so that other tests
        # won't be affected. Therefore, only do an assertFalse **after** the
        # reload, since statements after the assert might not run (if the assert
        # fails).
        reload(enki.plugins.preview)
        self.assertFalse(enabled)
        self.assertTrue(notice)

        # Now, prove that the reload worked: CodeChat should now be enabled,
        # and 'not installed' notification should be invisible.
        sw = SettingsWidget()
        self.assertTrue(sw.cbCodeChatEnable.isEnabled())
        sw.show()
        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
        sw.close()

    @base.requiresCmdlineUtility('sphinx-build --version')
    def test_uiCheck3a(self):
        """test_uiCheck1a has tested the case when Sphinx is disabled. This
        unit test will test the case when Sphinx is mannually enabled.
        """
        sw = SettingsWidget()
        # Mannually enable Sphinx.
        sw.cbSphinxEnable.setChecked(True)
        # Since it is assumed that the user has sphinx-build installed, the Sphinx
        # executable, output extension and default commandline will be initialize
        # to preset values.
        self.assertTrue(sw.cbSphinxEnable.isChecked())
        # buildOnSave is not enabled nor checked.
        self.assertTrue(sw.cbBuildOnSaveEnable.isEnabled())
        self.assertFalse(sw.cbBuildOnSaveEnable.isChecked())
        # All setting directories are enabled and empty.
        self.assertTrue(sw.leSphinxProjectPath.isEnabled())
        self.assertEqual(sw.leSphinxProjectPath.text(), '')
        self.assertTrue(sw.leSphinxOutputPath.isEnabled())
        self.assertEqual(sw.leSphinxOutputPath.text(), '')
        # Executable is enabled and set to default 'sphinx-build'
        self.assertTrue(sw.leSphinxExecutable.isEnabled())
        self.assertEqual(sw.leSphinxExecutable.text(), '')
        # Builder extension is enabled and set to default 'html'
        self.assertTrue(sw.cmbSphinxOutputExtension.isEnabled())
        self.assertEqual(sw.cmbSphinxOutputExtension.lineEdit().text(), 'html')
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
        for i in range(sw.gridLayout.count()):
            self.assertFalse(sw.gridLayout.itemAt(i).widget().isVisible())
        # Verify advanced mode setting line edits and labels are visible.
        self.assertTrue(sw.lbSphinxCmdline.isVisible())
        self.assertTrue(sw.leSphinxCmdline.isVisible())
        self.assertTrue(sw.lbSphinxReference.isVisible())
        sw.close()

    @requiresModule('CodeChat')
    def test_uiCheck4(self):
        """If Enki is opened with CodeChat enabled, the preview dock should be
           found."""
        core.config()['CodeChat']['Enabled'] = True
        self._doBasicTest('py')
        # The next line of code is unnecessary since self._doBasicTest() will
        # call self._dock()
        #self._dock()

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck4a(self):
        """Basic Sphinx test: create a Sphinx project in a temp folder, return
           webView content and log content after Sphinx builds the project."""
        self._doBasicSphinxConfig()
        self.testText = """****
head
****

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')


    @base.requiresCmdlineUtility('sphinx-build --version')
    @requiresModule('CodeChat')
    @base.inMainLoop
    def test_uiCheck4b(self):
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

    @requiresModule('CodeChat')
    def test_uiCheck5(self):
        """If Enki is opened without any configuration, the preview dock will
        not appear. This will not affect resT files or html files."""
        self.testText = u'test'
        self._doBasicTest('py')
        with self.assertRaisesRegexp(AssertionError, 'Dock Previe&w not found'):
            self._dock()

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck5a(self):
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

    @requiresModule('CodeChat')
    def test_uiCheck6(self):
        """If an empty code file is passed to Enki, the CodeChat preview panel
           should be empty."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u''
        self._doBasicTest('py')
        self.assertEqual(self._plainText(), self.testText)

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck6a(self):
        """Empty code file produces a Sphinx failure since file in toctree should
           always have a header."""
        self._doBasicSphinxConfig()
        self.testText = u''
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(u"doesn't have a title" in logContent)

    @requiresModule('CodeChat')
    def test_uiCheck7(self):
        """Test that Unicode characters are handled properly.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u'Niederösterreich'
        self._doBasicTest('py')
        # Plaintext captured from the preview dock will append a newline if
        # preview dock is not empty. A '\n' is added accordingly.
        self.assertEqual(self._plainText(), self.testText + '\n')

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck7a(self):
        """Unicode string passed to Sphinx should be handled properly.
        """
        self._doBasicSphinxConfig()
        self.testText = u"""**********
Енки
**********

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(u"<h1>Енки" in webViewContent)

    @requiresModule('CodeChat')
    def test_uiCheck8(self):
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


    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck8a(self):
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

    @base.inMainLoop
    def test_uiCheck9b(self):
        self._doBasicSphinxConfig()
        self.testText = u''
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue(u"""doesn't have a title""" in logContent)

    @requiresModule('CodeChat')
    def test_uiCheck9(self):
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

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck9a(self):
        """Test Sphinx error can be captured correctly"""
        self._doBasicSphinxConfig()
        self.testText = u"""****
head3
****

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        self.assertTrue("Title overline too short" in logContent)

    @requiresModule('CodeChat')
    def test_uiCheck10(self):
        """Empty input should generate an empty log.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u''
        self._doBasicTest('py')
        self.assertEqual(self._logText(), '')
        # do the same test for restructuredText
        self._doBasicTest('rst')
        self.assertEqual(self._logText(), '')

    @requiresModule('CodeChat')
    def test_uiCheck11(self):
        """Unicode should display correctly in log window too.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u'# .. Енки::'
        self._doBasicTest('py')
        self.assertTrue(u'Енки' in self._logText())
        self.testText = u'.. Енки::'
        self._doBasicTest('rst')
        self.assertTrue(u'Енки' in self._logText())

    @unittest.expectedFailure
    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck11a(self):
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

    @requiresModule('CodeChat')
    def test_uiCheck12(self):
        """Test progress bar status (indefinitely) when building
        """
        core.config()['CodeChat']['Enabled'] = True
        self.createFile('file.py', self.testText)
        self.assertEqual(self._widget().prgStatus.maximum(), 0)
        self.assertEqual(self._widget().prgStatus.minimum(), 0)

    @requiresModule('CodeChat')
    def test_uiCheck13(self):
        """Check different progressbar color given different scenarios.
        """
        core.config()['CodeChat']['Enabled'] = True
        # First, First, working code with no errors or warnings.
        self.testText = u'abc'
        self._doBasicTest('rst')
        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QProgressBar::chunk {}')

    @requiresModule('CodeChat')
    def test_uiCheck14(self):
        core.config()['CodeChat']['Enabled'] = True
        # Next, test a code piece with only warnings.
        self.testText = u'`abc'
        self._doBasicTest('rst')
        self.assertTrue('yellow' in self._widget().prgStatus.styleSheet())

    @requiresModule('CodeChat')
    def test_uiCheck15(self):
        core.config()['CodeChat']['Enabled'] = True
        # Next, test a code piece with only errors.
        self.testText = u'# .. ERROR::'
        self._doBasicTest('py')
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())

    @requiresModule('CodeChat')
    def test_uiCheck16(self):
        """A complex test case that tests both the log parser regexp and
        the progress bar color when both warnings and errors are present.
        """
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u'# .. ERROR::\n# `WARNING_'
        self._doBasicTest('py')
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 2 Error(s): 2' in self._logText())

    @base.inMainLoop
    @requiresModule('CodeChat')
    def test_uiCheck17(self):
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
        self.assertIn('yellow', self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 1 Error(s): 0' in self._logText())
        # switch to document 2
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 0 Error(s): 1' in self._logText())
        # switch to document 3
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        base.waitForSignal(lambda: None, self._widget().webView.page().mainFrame().loadFinished, 200)
        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QProgressBar::chunk {}')
        self.assertEqual(self._logText(), '')

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    @requiresModule('CodeChat')
    def test_uiCheck18(self):
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

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    @requiresModule('CodeChat')
    def test_uiCheck19(self):
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

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    @requiresModule('CodeChat')
    def test_uiCheck19a(self):
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

    # Cases testing commonprefix
    ##--------------------------
    # Basic checks
    def test_commonPrefix1(self):
        self.assertEqual(commonPrefix('a', 'a'), 'a')

    def test_commonPrefix2(self):
        self.assertEqual(commonPrefix('a', 'b'), '')

    def test_commonPrefix3(self):
        self.assertEqual(commonPrefix('', 'a'), '')

    # Test using various path separators.
    # TODO: this case does not work on linux
    def test_commonPrefix5(self):
        self.assertEqual(commonPrefix('a\\b', 'a\\b'), os.path.join('a','b'))

    def test_commonPrefix6(self):
        self.assertEqual(commonPrefix('a/b', 'a/b'), os.path.join('a','b'))

    def test_commonPrefix7(self):
        # TODO: this case does not work on linux
        self.assertEqual(commonPrefix('a/b', 'a\\b'), os.path.join('a','b'))

    # Check for the bug in os.path.commonprefix.
    def test_commonPrefix8(self):
        self.assertEqual(commonPrefix('a\\bc', 'a\\b'), 'a')

    # Test for relative paths.
    def test_commonPrefix9(self):
        # TODO: this case does not work on linux
        self.assertEqual(commonPrefix('a\\b\\..', 'a\\b'), 'a')

    def test_commonPrefix9a(self):
        self.assertEqual(commonPrefix('a/b/..', 'a/b'), 'a')

    def test_commonPrefix10(self):
        # TODO: this case does not work on linux
        self.assertEqual(commonPrefix('a\\.\\b', 'a\\b'), os.path.join('a','b'))

    def test_commonPrefix10a(self):
        self.assertEqual(commonPrefix('a/./b', 'a/b'), os.path.join('a','b'))

    def test_commonPrefix11(self):
        """Check that leading ../current_subdir will be removed after path
           clearnup."""
        # Get the name of the current directory
        # Pan: Would you test this?
        d = os.path.basename(os.getcwd())
        self.assertEqual(commonPrefix('../' + d + '/a/b', 'a/b'), os.path.join('a','b'))

    def test_commonPrefix11a(self):
        # if any input directory is abs path, return abs commonprefix
        d1 = os.path.join(os.getcwd(), 'a1')
        self.assertEqual(commonPrefix(d1, 'a2'), os.path.normcase(os.getcwd()))

    # Test for paths with spaces
    def test_commonPrefix12(self):
        self.assertEqual(commonPrefix('a a\\b b\\c c', 'a a\\b b'), os.path.join('a a','b b'))

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
        self.assertEqual(commonPrefix('..\\AVeryLongFileName', '..\\AVeryLongFileName'), os.path.normcase(os.path.abspath("../AVeryLongFileName")))

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
        copyTemplateFile(errors, source, 'missing.file', dest)
        self.assertTrue(errors[0][2].startswith("Input or output directory cannot be None"))

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
        copyTemplateFile(errors, source, 'dummy.html', dest)
        self.assertTrue(errors[0][2].startswith("Input or output directory cannot be None"))

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_copyTemplateFile4(self):
        # Make target directory read only, causing access error (*nix only since
        # NTFS does not have Write-only property)
        source = self.TEST_FILE_DIR
        dest= os.path.join(source, 'sub')
        os.makedirs(dest)
        errors = []
        # Make the source file write only
        mode = os.stat(os.path.join(source, 'dummy.html'))[0]
        os.chmod(os.path.join(source, 'dummy.html'), stat.S_IREAD)
        copyTemplateFile(errors, source, 'dummy.html', dest)
        # Restore source file's attribute
        os.chmod(os.path.join(source, 'dummy.html'), mode)
        self.assertNotEqual(filter(lambda x: "Access denied" in x, errors[0]), ())

    # TODO: finish the following 5 test cases
    #
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
    # The following test cases will test all three features with two special cases:
    #
    # #. create rst file with error, change splitter size, save file,
    #    delete all content, save file. Add new error. Will splitter size be
    #    preserved?
    #
    # #. User hide splitter size. Then switch to another error-free document.
    #    Switch back. Will log window keep hidden?

    def test_logWindowSplitter1(self):
        """Feature 1. Created files will have same default splitter size.
        """
        defaultSplitterSize = [199, 50]
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '.. file2::')
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        # Check splitter size of document 2.
        self.assertEqual(self._widget().splitter.sizes(), defaultSplitterSize)
        # Switch to document 1. Splitter size should be the same.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        # Make sure all documents have the same splitter size.
        self.assertEqual(self._widget().splitter.sizes(), defaultSplitterSize)

    def test_logWindowSplitter2(self):
        """Feature 2. All build-with-error files' splitter size are connected.
        """
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '.. file2::')
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        # Change splitter location of document 2.
        newSplitterSize = [125, 124]
        self._widget().splitter.setSizes(newSplitterSize)
        # Calling setSizes directly will not trigger splitter's ``splitterMoved``
        # signal. We need to manually emit this signal with two arguments (not
        # important here.)
        self._widget().splitter.splitterMoved.emit(newSplitterSize[0], 1)
        self.assertEqual(self._widget().splitter.sizes(), newSplitterSize)
        # Switch to document 1, make sure its splitter size is changed, too.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        self.assertEqual(self._widget().splitter.sizes(), newSplitterSize)

    def test_logWindowSplitter3(self):
        """Feature 3. Error free document will not affect other documents'
        splitter size.
        """
        defaultSplitterSize = [199, 50]
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '')
        document3 = self.createFile('file3.rst', '.. file3::')
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        # Check splitter size of document 1.
        self.assertEqual(self._widget().splitter.sizes(), defaultSplitterSize)
        # Switch to document 2. Log window is hidden now.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        self.assertFalse(self._widget().splitter.sizes()[1])
        # Switch to document 3. Log window should be restore to original size.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        self.assertEqual(self._widget().splitter.sizes(), defaultSplitterSize)

    def test_logWindowSplitter3a(self):
        """Feature 1,2,3. A combination of the above test cases.
        """
        document1 = self.createFile('file1.rst', '.. file1::')
        document2 = self.createFile('file2.rst', '')
        document3 = self.createFile('file3.rst', '.. file3::')
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document1))
        # Change splitter setting of document 1.
        newSplitterSize = [125, 124]
        self._widget().splitter.setSizes(newSplitterSize)
        self._widget().splitter.splitterMoved.emit(newSplitterSize[0], 1)
        self.assertEqual(self._widget().splitter.sizes(), newSplitterSize)
        # Switch to an error-free document, assert log window hidden.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        self.assertFalse(self._widget().splitter.sizes()[1])
        # Switch to file3 which will cause build error, check splitter size.
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        self.assertEqual(self._widget().splitter.sizes(), newSplitterSize)

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main(verbosity=2)
