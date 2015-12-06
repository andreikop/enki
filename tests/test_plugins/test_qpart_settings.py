#!/usr/bin/env python3

import unittest
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QColor, QFont, QTextOption

from enki.core.core import core


class _BaseTestCase(base.TestCase):
    def setUp(self):
        base.TestCase.setUp(self)
        self.createFile("asdf.txt", "")


class Font(_BaseTestCase):
    def test_1(self):
        font = QFont("Arial", 88)

        def continueFunc(dialog):
            page = dialog._pageForItem["Editor/Font"]

            page.lFont.setFont(font)

            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

        self.assertEqual(core.config()['Qutepart']['Font']['Family'], font.family())
        self.assertEqual(core.config()['Qutepart']['Font']['Size'], font.pointSize())

        self.assertEqual(core.workspace().currentDocument().qutepart.font().family(), font.family())
        self.assertEqual(core.workspace().currentDocument().qutepart.font().pointSize(), font.pointSize())


class Indent(_BaseTestCase):
    def _doTest(self, useTabs, width, autoDetect):
        def continueFunc(dialog):
            page = dialog._pageForItem["Editor/Indentation"]

            if useTabs:
                page.rbIndentationTabs.setChecked(True)
            else:
                page.rbIndentationSpaces.setChecked(True)

            page.sIndentationWidth.setValue(width)
            page.cbAutodetectIndent.setChecked(autoDetect)

            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

        self.assertEqual(core.config()['Qutepart']['Indentation']['UseTabs'], useTabs)
        self.assertEqual(core.config()['Qutepart']['Indentation']['Width'], width)
        self.assertEqual(core.config()['Qutepart']['Indentation']['AutoDetect'], autoDetect)

        self.assertEqual(core.workspace().currentDocument().qutepart.indentUseTabs, useTabs)
        self.assertEqual(core.workspace().currentDocument().qutepart.indentWidth, width)

    def test_1(self):
        self._doTest(True, 4, False)

    def test_2(self):
        self._doTest(False, 8, True)


class AutoCompletion(_BaseTestCase):
    def _doTest(self, enabled, threshold):
        def continueFunc(dialog):
            page = dialog._pageForItem["Editor/Autocompletion"]

            page.gbAutoCompletion.setChecked(enabled)
            page.sThreshold.setValue(threshold)

            self.assertTrue(page.lcdNumber.value(), threshold)

            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

        self.assertEqual(core.config()['Qutepart']['AutoCompletion']['Enabled'], enabled)
        self.assertEqual(core.config()['Qutepart']['AutoCompletion']['Threshold'], threshold)

        self.assertEqual(core.workspace().currentDocument().qutepart.completionEnabled, enabled)
        self.assertEqual(core.workspace().currentDocument().qutepart.completionThreshold, threshold)

    def test_1(self):
        self._doTest(False, 2)

    def test_2(self):
        self._doTest(True, 6)


class Edge(_BaseTestCase):
    def _doTest(self, enabled, width, colorName):
        def continueFunc(dialog):
            page = dialog._pageForItem["Editor/Long Lines"]

            page.gbEdgeEnabled.setChecked(enabled)
            page.sEdgeColumnNumber.setValue(width)
            page.tbEdgeColor.setColor(QColor(colorName))

            dialog.accept()

        self.openSettings(continueFunc)

        self.assertEqual(core.config()['Qutepart']['Edge']['Enabled'], enabled)
        self.assertEqual(core.config()['Qutepart']['Edge']['Column'], width)
        self.assertEqual(core.config()['Qutepart']['Edge']['Color'], colorName)

        self.assertEqual(core.workspace().currentDocument().qutepart.lineLengthEdge,
                         width if enabled else None)
        self.assertEqual(core.workspace().currentDocument().qutepart.lineLengthEdgeColor.name(), colorName)

    def test_1(self):
        self._doTest(True, 80, '#ff0000')

    def test_2(self):
        self._doTest(False, 80, '#ff0000')

    def test_3(self):
        self._doTest(True, 120, '#ff0000')

    def test_4(self):
        self._doTest(True, 120, '#00ff00')


class Eol(_BaseTestCase):
    def _doTest(self, mode, autoDetect):
        def continueFunc(dialog):
            page = dialog._pageForItem["Editor/EOL"]

            if mode == r'\n':
                page.rbEolUnix.setChecked(True)
            elif mode == r'\r\n':
                page.rbEolWindows.setChecked(True)
            elif mode == r'\r':
                page.rbEolMac.setChecked(True)
            else:
                assert 0

            if page.cbAutoDetectEol.isChecked() != autoDetect:
                QTest.mouseClick(page.cbAutoDetectEol, Qt.LeftButton)

            self.assertEqual(not page.lReloadToReapply.isHidden(), autoDetect)

            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

        self.assertEqual(core.config()['Qutepart']['EOL']['Mode'], mode)
        self.assertEqual(core.config()['Qutepart']['EOL']['AutoDetect'], autoDetect)

        conv = {r'\n': '\n',
                r'\r\n': '\r\n',
                r'\r': '\r'}

        if not autoDetect:  # if autodetection is active - not applied
            self.assertEqual(core.workspace().currentDocument().qutepart.eol, conv[mode])

    def test_1(self):
        self._doTest(r'\n', False)

    def test_2(self):
        self._doTest(r'\r\n', False)

    def test_3(self):
        self._doTest(r'\r', False)

    def test_4(self):
        self._doTest(r'\n', True)


class Wrap(_BaseTestCase):
    def _doTest(self, enabled, atWord, lineWrapMode, wordWrapMode, wordWrapText):
        def continueFunc(dialog):
            page = dialog._pageForItem["Editor/Long Lines"]

            page.gbWrapEnabled.setChecked(enabled)
            if atWord:
                page.rbWrapAtWord.setChecked(True)
            else:
                page.rbWrapAnywhere.setChecked(True)

            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

        self.assertEqual(core.config()['Qutepart']['Wrap']['Enabled'], enabled)
        self.assertEqual(core.config()['Qutepart']['Wrap']['Mode'], wordWrapText)

        self.assertEqual(core.workspace().currentDocument().qutepart.lineWrapMode(),
                         lineWrapMode)
        self.assertEqual(core.workspace().currentDocument().qutepart.wordWrapMode(),
                         wordWrapMode)


    def test_1(self):
        self._doTest(True, True, QPlainTextEdit.WidgetWidth, QTextOption.WrapAtWordBoundaryOrAnywhere, "WrapAtWord")

    def test_2(self):
        self._doTest(True, False, QPlainTextEdit.WidgetWidth, QTextOption.WrapAnywhere, "WrapAnywhere")

    def test_3(self):
        self._doTest(False, False, QPlainTextEdit.NoWrap, QTextOption.WrapAnywhere, "WrapAnywhere")


class WhiteSpaceVisibility(_BaseTestCase):
    def _doTest(self, incorrect, anyIndent):
        incorrectAction = core.actionManager().action('mView/aShowIncorrectIndentation')
        anyIndentAction = core.actionManager().action('mView/aShowAnyWhitespaces')

        if anyIndentAction.isChecked() != anyIndent:
            anyIndentAction.trigger()

        if not anyIndent:
            if incorrectAction.isChecked() != incorrect:
                incorrectAction.trigger()

        self.assertEqual(core.config()['Qutepart']['WhiteSpaceVisibility']['Any'], anyIndent)
        self.assertEqual(core.workspace().currentDocument().qutepart.drawAnyWhitespace,
                         anyIndent)

        if not anyIndent:
            self.assertEqual(core.config()['Qutepart']['WhiteSpaceVisibility']['Incorrect'], incorrect)
            self.assertEqual(core.workspace().currentDocument().qutepart.drawIncorrectIndentation,
                             incorrect)

        self.assertEqual(incorrectAction.isEnabled(), not anyIndent)

    def test_1(self):
        combinations = []
        for incorrect in (True, False):
            for anyIndent in (True, False):
                combinations.append((incorrect, anyIndent))

        combinationsOfCombinations = []
        for a in combinations:
            for b in combinations:
                combinationsOfCombinations.append((a, b))

        # test transition from any state to any
        for a, b in combinationsOfCombinations:
            self._doTest(*a)
            self._doTest(*b)


class WhitespaceStrip(_BaseTestCase):
    def _doTest(self, checked):
        action = core.actionManager().action('mEdit/aStripTrailingWhitespace')

        if action.isChecked() != checked:
            action.trigger()

        self.assertEqual(core.config()['Qutepart']['StripTrailingWhitespace'], checked)

        document = core.workspace().currentDocument()
        document.qutepart.text = 'asdf   '
        document.saveFile()

        expectedText = 'asdf' if checked else 'asdf   '
        self.assertEqual(document.qutepart.text, expectedText)

    def test_1(self):
        combinations = []
        for first in (True, False):
            for second in (True, False):
                combinations.append((first, second))

        # test transition from any state to any
        for first, second in combinations:
            self._doTest(first)
            self._doTest(second)


if __name__ == '__main__':
    unittest.main()
