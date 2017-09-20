"""
bracket-matcher --- autocompletes [], (), {}, "", '', “”, ‘’, «», ‹›, and ``.
================================================================================
"""

# DONE autocomplete defaults
# TODO custom autocompletes
# TODO custom autocompletes per file-types


from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtWidgets import (QWidget, QCheckBox, QVBoxLayout, QSpacerItem,
                             QSizePolicy, QLabel)
from PyQt5.QtGui import QTextCursor

from enki.core.core import core
from enki.core.uisettings import CheckableOption

# DONE Settings page
# DONE adhere to settings page
# DONE write closing parens
# DONE wrap parens around selected text
# DONE overwrite closing parens
# DONE delete closing char if backspace is pressed and opening charis deleted
# DONE generalize for all pairing characters
# Done Cleanup

openers = ("[", "(", "{", '"', "'", "“", "‘", "«", "‹", "`", "<")
closers = ("]", ")", "}", '"', "'", "”", "’", "»", "›", "`", ">")


class SettingsPage(QWidget):
    """Settings page for Bracket Matcher plugin"""
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        text = """
            <h2>Bracket Matcher</h2>
            <p>The Bracket Matcher plugin autocompletes [], (), {}, \"\",""" \
            """ '', “”, ‘’, «», ‹›, and ``.</p>
            <p></p>"""
        self._label = QLabel(text, self)
        self.checkbox = QCheckBox("Enable autocomplete brackets and quote "
                                  "characters.")
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self.checkbox)
        self._layout.addSpacerItem(QSpacerItem(0, 0,
                                               QSizePolicy.MinimumExpanding,
                                               QSizePolicy.MinimumExpanding))


class Plugin(QObject):
    """Plugin interface implementation

    The plugin looks for focusWindowChanged event, get all opened files
    and saves them.
    """

    def __init__(self):
        """Connect to QApplication OnFocusChanged event"""
        QObject.__init__(self)

        self._checkSettings()

        core.workspace().currentDocumentChanged.connect(
            self._onCurrentDocumentChanged)
        core.uiSettingsManager().aboutToExecute.connect(
            self._onSettingsDialogAboutToExecute)

    def terminate(self):
        """clean up"""
        core.uiSettingsManager().aboutToExecute.disconnect(
            self._onSettingsDialogAboutToExecute)

    def _onCurrentDocumentChanged(self, oldDocument, newDocument):
        if self._isAutocompletionActive():
            try:
                oldDocument.qutepart.removeEventFilter(self)
            except AttributeError:
                pass
            try:
                newDocument.qutepart.installEventFilter(self)
            except AttributeError:
                pass

    def eventFilter(self, qutepart, event):
        """The eventFilter filters for three cases of the editor (qutepart) of
        the current document and takes according action:
        - an opening character is pressed => closing character is inserted and
          cursor in moved between both characters. If text is selected, it is
          enclosed by the characters; the cursor is outside the closing
          character.
        - a closing character is pressed => if the same closing character is
          already at the current text position, the character is omitted.
        - backspace is pressed to delete an opening character =>
          if the coresponding closing character is behind the cursor, it is
          also removed.
        """
        # function definitions
        def wrap(qutepart, event, textCursor):
            """wrap the selected text with the coresponding characters"""
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

        def close(qutepart, textCursor):
            """close the inserted character with the coresponding character"""
            textCursor.insertText(opener + closer)
            textCursor.movePosition(QTextCursor.Left)
            qutepart.setTextCursor(textCursor)

        def getChar(qutepart, n):
            """return character n steps away or empty string if n is outside
            of text."""
            text = qutepart.toPlainText()
            textCursor = qutepart.textCursor()
            pos = textCursor.position() + n
            try:
                return text[pos]
            except IndexError as e:
                return ""

        def nextChar(qutepart):
            """return character right to cursor position"""
            return getChar(qutepart, 0)

        def prevChar(qutepart):
            """return character left to cursor position"""
            return getChar(qutepart, -1)
        # main part of event filter
        if (event.type() == QEvent.KeyPress and
                event.modifiers() == Qt.NoModifier):
            textCursor = qutepart.textCursor()
            # if opening character is inserted by the user, close it
            if event.text() in openers:
                index = openers.index(event.text())
                opener = openers[index]
                closer = closers[index]
                if textCursor.hasSelection():
                    wrap(qutepart, event, textCursor)
                else:
                    close(qutepart, textCursor)
                return True
            elif (event.text() in closers and
                  event.text() == nextChar(qutepart)):
                # move cursor right
                textCursor.movePosition(QTextCursor.Right)
                qutepart.setTextCursor(textCursor)
                return True
            elif event.key() == Qt.Key_Backspace:
                closer = nextChar(qutepart)
                opener = prevChar(qutepart)
                if (closer in closers and
                        opener == openers[closers.index(closer)]):
                    textCursor.deleteChar()
                    textCursor.deletePreviousChar()
                    qutepart.setTextCursor(textCursor)
                    return True
                else:
                    return False
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
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "BracketMatcher/Autocompletion",
                                            page.checkbox))

    def _checkSettings(self):
        """Check if settings are present in the core configuration file,
        else create and return them.
        """
        if "BracketMatcher" not in core.config():
            core.config()["BracketMatcher"] = {}
            core.config()["BracketMatcher"]["Autocompletion"] = False
        return core.config()["BracketMatcher"]["Autocompletion"]

    def _isAutocompletionActive(self):
        """Return if autosave is enabled"""
        return core.config()["BracketMatcher"]["Autocompletion"]
