"""
qpartsettings --- GUI dialogs for Qutepart settings
===================================================

Appends pages to the settings dialogue.

This is not a True plugin, because it 'knows' pathes to editor settings,
which are not a part of enki API. But, this code has been moved out
from the core for make it smaller.
"""

import os

from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

from enki.core.core import core

from enki.core.uisettings import CheckableOption, ChoiseOption, FontOption, NumericOption, ColorOption


class _SettingsPageWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """

    def __init__(self, formName, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), formName), self)


class _FontSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Font.ui'), self)


class _IndentationSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Indentation.ui'), self)


class _AutocompletionSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Autocompletion.ui'), self)


class _EolSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Eol.ui'), self)


class Plugin:
    """Plugin interface implementation

    Waits for GUI dialogue invocation.
    Adds options to the dialogue.
    Applies settings.
    """

    def __init__(self):
        Plugin.instance = self
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

        showTrailingAction = core.actionManager().action('mView/aShowIncorrectIndentation')
        showTrailingAction.triggered.connect(self._onShowIncorrectTriggered)
        showTrailingAction.setChecked(self._confShowIncorrect())
        showTrailingAction.setEnabled(not self._confShowAnyWhitespace())

        showAnyIndentAction = core.actionManager().action('mView/aShowAnyWhitespaces')
        showAnyIndentAction.triggered.connect(self._onShowAnyWhitespaceTriggered)
        showAnyIndentAction.setChecked(self._confShowAnyWhitespace())
        showAnyIndentAction.setEnabled(True)

        stripTrailingWhitespaceAction = core.actionManager().action('mEdit/aStripTrailingWhitespace')
        stripTrailingWhitespaceAction.triggered.connect(self._onStripTrailingTriggered)
        stripTrailingWhitespaceAction.setChecked(self._confStripTrailing())
        stripTrailingWhitespaceAction.setEnabled(True)

        enableVimMode = core.actionManager().action('mEdit/aEnableVimMode')
        enableVimMode.triggered.connect(self._onVimModeEnabledChanged)
        enableVimMode.setChecked(self._confVimModeEnabled())
        enableVimMode.setEnabled(True)

    def terminate(self):
        pass

    @staticmethod
    def _confShowIncorrect():
        return core.config()['Qutepart']['WhiteSpaceVisibility']['Incorrect']

    @staticmethod
    def _confShowAnyWhitespace():
        return core.config()['Qutepart']['WhiteSpaceVisibility']['Any']

    @staticmethod
    def _confStripTrailing():
        return core.config()['Qutepart']['StripTrailingWhitespace']

    @staticmethod
    def _confVimModeEnabled():
        return core.config()['Qutepart']['VimModeEnabled']

    def _onDocumentOpened(self, document):
        document.qutepart.drawIncorrectIndentation = self._confShowIncorrect()
        document.qutepart.drawAnyWhitespace = self._confShowAnyWhitespace()
        document.qutepart.vimModeEnabled = self._confVimModeEnabled()

    def _onShowIncorrectTriggered(self, checked):
        for document in core.workspace().documents():
            document.qutepart.drawIncorrectIndentation = checked
        core.config()['Qutepart']['WhiteSpaceVisibility']['Incorrect'] = checked
        core.config().flush()

    def _onShowAnyWhitespaceTriggered(self, checked):
        for document in core.workspace().documents():
            document.qutepart.drawAnyWhitespace = checked
        core.config()['Qutepart']['WhiteSpaceVisibility']['Any'] = checked
        core.config().flush()

        core.actionManager().action('mView/aShowIncorrectIndentation').setEnabled(not checked)

    def _onStripTrailingTriggered(self, checked):
        core.config()['Qutepart']['StripTrailingWhitespace'] = checked
        core.config().flush()

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        fontWidget = _SettingsPageWidget('Font.ui', dialog)
        indentWidget = _SettingsPageWidget('Indentation.ui', dialog)
        complWidget = _SettingsPageWidget('Autocompletion.ui', dialog)
        eolWidget = _SettingsPageWidget('Eol.ui', dialog)
        longLinesWidget = _SettingsPageWidget('LongLines.ui', dialog)

        dialog.appendPage("Editor/Font", fontWidget)
        dialog.appendPage("Editor/Indentation", indentWidget)
        dialog.appendPage("Editor/Autocompletion", complWidget)
        dialog.appendPage("Editor/EOL", eolWidget)
        dialog.appendPage("Editor/Long Lines", longLinesWidget)

        cfg = core.config()
        options = \
            (
                FontOption(dialog, cfg, "Qutepart/Font/Family", "Qutepart/Font/Size",
                           fontWidget.lFont, fontWidget.pbFont),

                ChoiseOption(dialog, cfg, "Qutepart/Indentation/UseTabs",
                             {indentWidget.rbIndentationSpaces: False,
                              indentWidget.rbIndentationTabs: True}),
                NumericOption(dialog, cfg, "Qutepart/Indentation/Width", indentWidget.sIndentationWidth),
                CheckableOption(dialog, cfg, "Qutepart/Indentation/AutoDetect", indentWidget.cbAutodetectIndent),

                ChoiseOption(dialog, cfg, "Qutepart/EOL/Mode",
                             {eolWidget.rbEolUnix: r'\n',
                              eolWidget.rbEolWindows: r'\r\n',
                              eolWidget.rbEolMac: r'\r'}),
                CheckableOption(dialog, cfg, "Qutepart/EOL/AutoDetect", eolWidget.cbAutoDetectEol),

                CheckableOption(dialog, cfg, "Qutepart/Edge/Enabled", longLinesWidget.gbEdgeEnabled),
                NumericOption(dialog, cfg, "Qutepart/Edge/Column", longLinesWidget.sEdgeColumnNumber),
                ColorOption(dialog, cfg, "Qutepart/Edge/Color", longLinesWidget.tbEdgeColor),

                CheckableOption(dialog, cfg, "Qutepart/AutoCompletion/Enabled", complWidget.gbAutoCompletion),
                NumericOption(dialog, cfg, "Qutepart/AutoCompletion/Threshold", complWidget.sThreshold),

                CheckableOption(dialog, cfg, "Qutepart/Wrap/Enabled", longLinesWidget.gbWrapEnabled),
                ChoiseOption(dialog, cfg, "Qutepart/Wrap/Mode",
                             {longLinesWidget.rbWrapAtWord: "WrapAtWord",
                              longLinesWidget.rbWrapAnywhere: "WrapAnywhere"}),
            )

        for option in options:
            dialog.appendOption(option)

        eolWidget.lReloadToReapply.setVisible(eolWidget.cbAutoDetectEol.isChecked())

    def _onVimModeEnabledChanged(self, checked):
        for document in core.workspace().documents():
            document.qutepart.vimModeEnabled = checked
        core.config()['Qutepart']['VimModeEnabled'] = checked
        core.config().flush()
