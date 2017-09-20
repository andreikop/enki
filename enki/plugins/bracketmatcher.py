"""
bracket-matcher --- autocompletes [], (), {}, "", '', “”, ‘’, «», ‹›, and ``.
================================================================================
"""

# TODO autocomplete defaults
# TODO custom autocompletes
# TODO custom autocompletes per file-types


import os, sys

from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout, \
                            QSpacerItem, QSizePolicy, QLabel
from PyQt5.QtGui import QTextCursor

from enki.core.core import core
from enki.core.uisettings import CheckableOption

# DONE Settings page
# TODO adhere to settings page
# DONE write closing parens
# DONE wrap parens around selected text
# TODO overwrite closing parens
# TODO delete closing paren if backspace is pressed and opening paren is deleted
# DONE generalize for all pairing characters

openers = ("[", "(", "{", '"', "'", "“", "‘", "«", "‹", "`")
closers = ("]", ")", "}", '"', "'", "”", "’", "»", "›", "`")

class SettingsPage(QWidget):
    """Settings page for Bracket Matcher plugin"""
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        text = """
            <h2>Bracket Matcher</h2>
            <p>The Bracket Matcher plugin autocompletes [], (), {}, \"\", '', “”, ‘’, «», ‹›, and ``.</p>
            <p></p>"""
        self._label = QLabel(text, self)
        self.checkbox = QCheckBox("Enable autocomplet brackets and quote characters.")
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self.checkbox)
        self._layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

class Plugin(QObject):
    """Plugin interface implementation

    The plugin looks for focusWindowChanged event, get all opened files
    and saves them.
    """

    def __init__(self):
        """Connect to QApplication OnFocusChanged event"""
        QObject.__init__(self)

        self._checkSettings()

        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

    def terminate(self):
        """clean up"""
        core.uiSettingsManager().aboutToExecute.disconnect(self._onSettingsDialogAboutToExecute)

    def _onCurrentDocumentChanged(self, oldDocument, newDocument):
        try:
            oldDocument.qutepart.removeEventFilter(self)
        except AttributeError:
            pass
        try:
            newDocument.qutepart.installEventFilter(self)
        except AttributeError:
            pass

    def eventFilter(self, qutepart, event):
        if event.type() == QEvent.KeyPress and event.modifiers() == Qt.NoModifier:
            if event.text() in openers:
                index = openers.index(event.text())
                opener = openers[index]
                closer = closers[index]
                textCursor = qutepart.textCursor()
                if textCursor.hasSelection():
                    # it's important to get selectionStart and selectionEnd
                    # before we change the textCursor, otherwise they will
                    # change when we do operations like insertText
                    selectionStart = textCursor.selectionStart()
                    selectionEnd = textCursor.selectionEnd() + 1

                    textCursor.setPosition(selectionStart)
                    textCursor.insertText(opener)
                    qutepart.setTextCursor(textCursor)
                    textCursor.setPosition(selectionEnd)
                    textCursor.insertText(closer)
                    qutepart.setTextCursor(textCursor)
                else:
                    textCursor.insertText(opener + closer)
                    textCursor.movePosition(QTextCursor.Left)
                    qutepart.setTextCursor(textCursor)
                return True
        return False

    def _onTextChanged(self):
        pass

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        page = SettingsPage(dialog)
        dialog.appendPage(u"Bracket Matcher", page)

        # Options
        dialog.appendOption(CheckableOption(dialog, core.config(), "BracketMatcher/Autocompletion", page.checkbox))

    def _checkSettings(self):
        """Check if settings are present in the core configuration file,
        else create and return them.
        """
        if not "BracketMatcher" in core.config():
            core.config()["BracketMatcher"] = {}
            core.config()["BracketMatcher"]["Autocompletion"] = False
        return core.config()["BracketMatcher"]["Autocompletion"]

    def _isAutocompletionActive(self):
        """Return if autosave is enabled"""
        return core.config()["BracketMatcher"]["Autocompletion"]
