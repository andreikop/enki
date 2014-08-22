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
from PyQt4.QtCore import Qt, QPoint, QEvent
from PyQt4.QtTest import QTest
from PyQt4.QtGui import QDockWidget, QTextCursor, QKeyEvent

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
        self._showDock()
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
        # See if the dock can be opened.
        p = core.actionManager().action('mView/aPreview')
        if p:
            # Yes, so open it.
            p.trigger()
        else:
            # No, so load a dummy HTML document so that it can be opened.
            d = self.createFile('dummy.html', '')
#            d.close()

    def _visibleText(self):
        return self._widget().webView.page().mainFrame().toPlainText()

    def _html(self):
        return self._widget().webView.page().mainFrame().toHtml()

    def _logText(self):
        """Return log window text"""
        return self._widget().teLog.toPlainText()

    def _assertHtmlReady(self, start, timeout=2000):
        """ Wait for the PreviewDock to emit the htmlReady signal.

        This signal is produced by calling to start function. Assert
        if the signal isn't emitted within a timeout.

        """
        self.assertEmits(start, self._dock()._thread.htmlReady, timeout)

    def _doBasicTest(self, extension):
        # HTML files don't need processing in the worker thread.
        if extension != 'html':
            self._assertHtmlReady(lambda: self.createFile('file.' + extension, self.testText))

    def _doBasicSphinxConfig(self):
        """This function will set basic sphinx configuration options
        so that Sphinx can run in a test environment.
        """
        core.config()['Sphinx']['Enabled'] = True
        core.config()['Sphinx']['Executable'] = r'sphinx-build'
        core.config()['Sphinx']['ProjectPath'] = self.TEST_FILE_DIR
        core.config()['Sphinx']['OutputPath'] = os.path.join(self.TEST_FILE_DIR, '_build/html')
        core.config()['Sphinx']['OutputExtension'] = r'html'
        core.config()['Sphinx']['Cmdline'] = r'sphinx-build -d _build/doctrees . _build/html'

    def _doBasicSphinxTest(self, extension):
        """This function will build a basic sphinx project in the temporary
        directory. The project consists of master document content.rst and a
        simple code document code.extension. Here the extension to the code
        file can be altered. For example, the extension can be set to .rst .
        """
        # Fill in conf.py and default.css file
        sw = SettingsWidget()
        sw._copySphinxProjectTemplate()

        # Create master document contents.rst
        master = os.path.join(self.TEST_FILE_DIR, 'contents.rst')
        with codecs.open(master, 'wb', encoding='utf8') as file_:
            file_.write(""".. toctree::

   code.""" + extension)

        webViewContent = []
        def senderSignalSlot(*args):
            webViewContent.append(args)

        self._dock().webViewLoadFinishedWithContent.connect(senderSignalSlot)
        def tmp():
            self.createFile(os.path.join(self.TEST_FILE_DIR, 'code.' + extension), self.testText)

        # For some reason, self._dock() will sometimes fail to find the preview widget.
        d = self._dock()
        # First html ready will be checked such that log window content can be
        # get. After html ready we wait for loadFinished signal.
        self._assertHtmlReady(tmp, timeout=10000)
        logContent = d._widget.teLog.toPlainText()
        base.waitForSignal(lambda : None, self._dock().webViewLoadFinishedWithContent, 1000)
        d.webViewLoadFinishedWithContent.disconnect(senderSignalSlot)

        # return both webViewContent and log window content such that they can
        # be processed further
        return [None if not webViewContent else webViewContent[0][0], logContent]

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
        self._assertHtmlReady(lambda: self.createFile('test.md', 'foo'))
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

    # Cases for literate programming setting ui
    ##-----------------------------------------
    #
    @requiresModule('CodeChat')
    def test_uiCheck1(self):
        """When Enki runs for the first time, the CodeChat module should be
           disabled by default."""
        sw = SettingsWidget()
        self.assertFalse(sw.cbCodeChatEnable.isChecked())
        self.assertTrue(sw.cbCodeChatEnable.isEnabled())
        # If CodeChat module is present, user should not be able to see
        # 'CodeChat not installed' notification.
        sw.show()
        # Widgets that are not on top level will be visible only when all its
        # ancesters are visible. Check `here <http://qt-project.org/doc/qt-5/qwidget.html#visible-prop>`_
        # for more details. Calling show() function will force update on
        # setting ui.
        self.assertFalse(sw.labelCodeChatNotInstalled.isVisible())
        sw.close()

    @base.requiresCmdlineUtility('sphinx-build --version')
    def test_uiCheck1a(self):
        """By default, when sphinx is available, it is set to be disabled. all
        path setting line edits and buttons are disabled."""
        sw = SettingsWidget()
        # sphinx is enabled but unchecked.
        self.assertTrue(sw.cbSphinxEnable.isEnabled())
        self.assertFalse(sw.cbSphinxEnable.isChecked())
        # buildOnSave is not enabled nor checked.
        self.assertFalse(sw.cbBuildOnSaveEnable.isEnabled())
        self.assertFalse(sw.cbBuildOnSaveEnable.isChecked())
        # all setting directories are disabled and empty.
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
        # Verify that the CodeChat checkbox is disabled, and 'not installed'
        # notification is visible.
        with ImportFail('CodeChat'):
            reload(enki.plugins.preview)
            sw = SettingsWidget()
            enabled = sw.cbCodeChatEnable.isEnabled()
            sw.show()
            notice = sw.labelCodeChatNotInstalled.isVisible()
            sw.close()
        # When done with this test first restore the state of the preview module
        # by reloaded with the CodeChat module available, so that other tests
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
        """test_uiCheck1a has tested the case when sphinx is disabled. This
        unit test will test the case when sphinx is mannually enabled.
        """
        sw = SettingsWidget()
        # Mannually enable sphinx.
        sw.cbSphinxEnable.setChecked(True)
        # Since it is assumed the user have sphinx-build installed, sphinx
        # executable, output extension and default commandline will be initialize
        # to preset values.
        self.assertTrue(sw.cbSphinxEnable.isChecked())
        # buildOnSave is not enabled nor checked.
        self.assertTrue(sw.cbBuildOnSaveEnable.isEnabled())
        self.assertFalse(sw.cbBuildOnSaveEnable.isChecked())
        # all setting directories are enabled and empty.
        self.assertTrue(sw.leSphinxProjectPath.isEnabled())
        self.assertEqual(sw.leSphinxProjectPath.text(), '')
        self.assertTrue(sw.leSphinxOutputPath.isEnabled())
        self.assertEqual(sw.leSphinxOutputPath.text(), '')
        # executable is enabled and set to default 'sphinx-build'
        self.assertTrue(sw.leSphinxExecutable.isEnabled())
        self.assertEqual(sw.leSphinxExecutable.text(), '')
        # builder extension is enabled and set to default 'html'
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
        # Verify advanced mode setting line edits and labels are visible
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
        """Basic sphinx test: create a sphinx project in temp folder, returns
           webView content and log content after sphinx builds the project."""
        self._doBasicSphinxConfig()
        self.testText = """****
head
****

content"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')


#    @base.requiresCmdlineUtility('sphinx-build --version')
    @requiresModule('CodeChat')
    @base.inMainLoop
    def test_uiCheck4b(self):
        """Basic Sphinx with CodeChat test: create a sphinx project with codechat
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
        self.assertTrue(u'writing output... [ 33%] code.py' in logContent)

    @requiresModule('CodeChat')
    @base.inMainLoop
    def test_uiCheck5(self):
        """If Enki is opened without any configuration, the preview dock will
           be empty. This will not affect resT files or html files."""
        self.testText = u'test'
        self._doBasicTest('py')
        assert 'test' not in self._html()

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck5a(self):
        """Basic sphinx test: with sphinx and codechat disabled, no preview
           window can be found."""
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['Enabled'] = False
        self.testText = """****
head
****

content"""
        with self.assertRaises(AssertionError):
            self._doBasicSphinxTest('rst')

    @requiresModule('CodeChat')
    def test_uiCheck6(self):
        """If an empty code file is passed to Enki, the CodeChat preview panel
           should be empty."""
        core.config()['CodeChat']['Enabled'] = True
        self.testText = u''
        self._doBasicTest('py')
        self.assertEqual(self._visibleText(), self.testText)

    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck6a(self):
        """Empty code file produces a sphinx failure since file in toctree should
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
        self.assertEqual(self._visibleText(), self.testText + '\n')

#    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck7a(self):
        """Unicode string passed to sphinx should be handled properly.
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
        assert 'test' not in self._html()

        core.config()['CodeChat']['Enabled'] = True
        core.uiSettingsManager().dialogAccepted.emit();
        self._doBasicTest('py')
        assert 'test' in self._html()


#    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck8a(self):
        """Start with sphinx disabled, make sure rst file will be rendered by
        docutils.core.publish_string. Then enable sphinx, force document refresh
        by calling scheduleDucomentProcessing. Make sure now sphinx kicks in.
        """
        self._doBasicSphinxConfig()
        core.config()['Sphinx']['Enabled'] = False
        self.testText = u''
        self._doBasicSphinxTest('rst')
        self.assertEqual(self._visibleText(), '')
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

#    @base.requiresCmdlineUtility('sphinx-build --version')
    @base.inMainLoop
    def test_uiCheck9a(self):
        """Test sphinx error can be captured correctly"""
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
        """Unicode in log window while in sphinx mode does not work since sphinx
           error output is not in unicode.
        """
        core.config()['Sphinx']['Enabled'] = True
        core.config()['Sphinx']['ProjectPath'] = self.TEST_FILE_DIR
        core.config()['Sphinx']['OutputPath'] = os.path.join(self.TEST_FILE_DIR, '_build/html')
        core.config()['Sphinx']['OutputExtension'] = 'html'

        self.testText = u"""****
head
****

.. Енки::"""
        webViewContent, logContent = self._doBasicSphinxTest('rst')
        # Unicode cannot be found in sphinx error message output.
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
        self.assertEmits(lambda: core.workspace().setCurrentDocument(document1), self._dock().setHtmlDone, 10000)
        # Process messages (wait for something that won't happen). This seems to
        # make all the tests happy. ???
        base.waitForSignal(lambda: None, self._dock().closed, 1000)
        self.assertIn('yellow', self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 1 Error(s): 0' in self._logText())
        # switch to document 2
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document2))
        self.assertTrue('red' in self._widget().prgStatus.styleSheet())
        self.assertTrue('Warning(s): 0 Error(s): 1' in self._logText())
        # switch to document 3
        self._assertHtmlReady(lambda: core.workspace().setCurrentDocument(document3))
        self.assertEqual(self._widget().prgStatus.styleSheet(), 'QProgressBar::chunk {}')
        self.assertEqual(self._logText(), '')

# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main(verbosity=2)
