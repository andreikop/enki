"""
editortoolbar --- Shows position, save state, EOL and indent
============================================================

It also allows to change this parameters and save the file

File contains module implementation
"""

import os.path


from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QMenu, QToolButton
from PyQt5.QtGui import QFontMetrics, QIcon, QPalette
from PyQt5 import uic

from enki.core.core import core


class VimModeIndicator(QLabel):
    setMeVisible = pyqtSignal(bool)

    def __init__(self, *args):
        QLabel.__init__(self, *args)

        self.setMinimumWidth(QFontMetrics(self.font()).width("Xreplace charX"))
        self.setAlignment(Qt.AlignCenter)

        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)

    def terminate(self):
        core.workspace().currentDocumentChanged.disconnect(self._onCurrentDocumentChanged)

    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):  # pylint: disable=W0613
        if oldDocument is not None:
            oldDocument.qutepart.vimModeEnabledChanged.disconnect(self._onVimModeEnabled)
            oldDocument.qutepart.vimModeIndicationChanged.disconnect(self._onIndicationChanged)

        if currentDocument is not None:
            currentDocument.qutepart.vimModeEnabledChanged.connect(self._onVimModeEnabled)
            currentDocument.qutepart.vimModeIndicationChanged.connect(self._onIndicationChanged)
            if currentDocument.qutepart.vimModeEnabled:
                self._updateIndication()

        self.setMeVisible.emit(currentDocument is not None and currentDocument.qutepart.vimModeEnabled)
        self._updateIndication()

    def _updateIndication(self):
        doc = core.workspace().currentDocument()
        if doc:
            qpart = doc.qutepart
            if qpart.vimModeEnabled:
                self._onIndicationChanged(*doc.qutepart.vimModeIndication)

    def _onIndicationChanged(self, color, text):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        style = 'background: {}; border: 4px solid transparent; border-radius: 10px;'.format(color.name())
        self.setStyleSheet(style)
        self.setText(text)

    def _onVimModeEnabled(self, enabled):
        self.setMeVisible.emit(enabled)

        if enabled:
            self._updateIndication()


# AK: Idea of _EolIndicatorAndSwitcher, and icons for it was taken from juffed

class EolIndicatorAndSwitcher(QToolButton):
    """This widget is visible on Status Bar as EOL type icon.

    It draws menu with EOL choise and switches EOL
    """
    _ICON_FOR_MODE = {'\r\n': "winEol.png",
                      '\r': "macEol.png",
                      '\n': "unixEol.png"}

    def __init__(self, parent):
        QToolButton.__init__(self, parent)
        self.setEnabled(False)
        self.setToolTip(self.tr("Line endings. Click for convert"))
        self.setIconSize(QSize(16, 16))
        self.setIcon(QIcon(':/enkiicons/unixEol.png'))
        self.setPopupMode(QToolButton.InstantPopup)

        menu = QMenu(self)  # menu filled on popup. Performance optimisation for quicker start up
        self.setMenu(menu)
        menu.aboutToShow.connect(self._onMenuAboutToShow)
        menu.triggered.connect(self._onEolActionTriggered)

        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        core.workspace().eolChanged.connect(self._setEolMode)

    def terminate(self):
        core.workspace().currentDocumentChanged.disconnect(self._onCurrentDocumentChanged)
        core.workspace().eolChanged.disconnect(self._setEolMode)

    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):  # pylint: disable=W0613
        """Current document on workspace has been changed
        """
        if currentDocument is not None:
            self._setEolMode(None, currentDocument.qutepart.eol)
            self.setEnabled(True)
        else:
            self._setEolMode(None, None)
            self.setEnabled(False)

    def _onMenuAboutToShow(self):
        """EOL menu has been requested
        """
        document = core.workspace().currentDocument()
        if document is not None:
            currentMode = document.qutepart.eol
            self._updateEolMenu(currentMode)

    def _updateEolMenu(self, currentMode):
        """Generate EOL menu
        """
        self.menu().clear()

        def addAction(text, eolMode):
            """Add an action to the EOL menu"""
            action = self.menu().addAction(QIcon(':/enkiicons/' + self._ICON_FOR_MODE[eolMode]), text)
            action.setData(eolMode)
            if eolMode == currentMode:
                action.setCheckable(True)
                action.setChecked(True)
            return action

        addAction(self.tr("CR+LF: Windows"), '\r\n')
        addAction(self.tr("CR: Mac OS (but not Mac OS X)"), '\r')
        addAction(self.tr("LF: Unix"), '\n')

    def _onEolActionTriggered(self, action):
        """EOL mode selected
        """
        newEol = action.data()
        document = core.workspace().currentDocument()
        document.qutepart.eol = newEol
        document.qutepart.document().setModified(True)
        self._setEolMode(None, document.qutepart.eol)

    def _setEolMode(self, document, mode):
        """Change EOL mode on GUI
        """
        if mode is not None:
            self.setIcon(QIcon(':/enkiicons/' + self._ICON_FOR_MODE[mode]))


class _IndentationDialog(QDialog):
    """Indentation dialog appears, if indentation label on the status bar clicked
    """

    def __init__(self, parent, document):
        QDialog.__init__(self, parent)
        self._document = document

        uic.loadUi(os.path.join(os.path.dirname(__file__), 'IndentationDialog.ui'), self)
        self._widthSlider.setValue(document.qutepart.indentWidth)
        self._updateWidthLabel()
        self._widthSlider.valueChanged.connect(self._onWidthChanged)

        if document.qutepart.indentUseTabs:
            self._tabsRadio.setChecked(True)
        else:
            self._spacesRadio.setChecked(True)
        self._tabsRadio.toggled.connect(self._onTabsToggled)

    def _updateWidthLabel(self):
        """Update indentation with on GUI
        """
        template = self.tr("Width: %d")
        self._widthLabel.setText(template % self._document.qutepart.indentWidth)

    def _onWidthChanged(self, value):
        """Handler of change of indentation width
        """
        self._document.qutepart.indentWidth = value
        self._updateWidthLabel()

    def _onTabsToggled(self, toggled):
        """Handler of change of 'Indentation uses tabs' flag
        """
        self._document.qutepart.indentUseTabs = toggled


class IndentIndicatorAndSwitcher(QToolButton):
    """This widget is visible on Status Bar as indent type label

    It draws menu with indent choise and switches indent
    """

    def __init__(self, parent):
        QToolButton.__init__(self, parent)
        self.setText(self.tr("Tabs"))
        self.setEnabled(False)

        self.setToolTip(self.tr("Indentation mode. Click to change"))

        self.clicked.connect(self._onClicked)
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        core.workspace().indentUseTabsChanged.connect(self._onIndentSettingsChanged)
        core.workspace().indentWidthChanged.connect(self._onIndentSettingsChanged)

    def terminate(self):
        core.workspace().currentDocumentChanged.disconnect(self._onCurrentDocumentChanged)
        core.workspace().indentUseTabsChanged.disconnect(self._onIndentSettingsChanged)
        core.workspace().indentWidthChanged.disconnect(self._onIndentSettingsChanged)

    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):  # pylint: disable=W0613
        """Current document on workspace has been changed
        """
        if currentDocument is not None:
            self._setIndentMode(currentDocument.qutepart.indentWidth,
                                currentDocument.qutepart.indentUseTabs)
        else:
            self._clearIndentMode()

    def _onIndentSettingsChanged(self, document, newValue):
        """Document settings changed. Update themselves, if necessary
        """
        if document == core.workspace().currentDocument():
            self._setIndentMode(document.qutepart.indentWidth,
                                document.qutepart.indentUseTabs)

    def _onClicked(self):
        """Indentation button clicked. Show dialog
        """
        document = core.workspace().currentDocument()
        if document is not None:
            dialog = _IndentationDialog(self, document)
            dialog.exec_()
            self._setIndentMode(document.qutepart.indentWidth, document.qutepart.indentUseTabs)

    def _setIndentMode(self, width, useTabs):
        """Update indentation mode on GUI
        """
        if useTabs:
            self.setText(self.tr("Tabs"))
        else:
            self.setText(self.tr("%s spaces" % width))
        self.setEnabled(True)

    def _clearIndentMode(self):
        """Last document has been closed, update indentation mode
        """
        self.setEnabled(False)


class PositionIndicator(QToolButton):
    """Indicator, which shows text "Line: yy Column: xx"
    """

    def __init__(self, parent):
        QToolButton.__init__(self, parent)
        self.setToolTip(self.tr("Cursor position"))
        self.setEnabled(False)
        self._setCursorPosition(-1, -1)
        minWidth = QFontMetrics(self.font()).width("Line: xxxxx Column: xxx")
        minWidth += 30  # for the button borders
        self.setMinimumWidth(minWidth)  # Avoid flickering when text width changed
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)

        core.workspace().cursorPositionChanged.connect(self._onCursorPositionChanged)

        self._timer = QTimer()
        self._timer.setInterval(200)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._onUpdatePositionTimer)
        self._passedUpdate = False

    def terminate(self):
        if self._timer.isActive():
            self._timer.stop()

        core.workspace().currentDocumentChanged.disconnect(self._onCurrentDocumentChanged)
        core.workspace().cursorPositionChanged.disconnect(self._onCursorPositionChanged)

    def _onUpdatePositionTimer(self):
        """Update text on GUI according to current position
        """
        if self._passedUpdate:
            document = core.workspace().currentDocument()
            self._setCursorPosition(*document.qutepart.cursorPosition)
            self._passedUpdate = False

    def _onCursorPositionChanged(self, document):
        """Cursor position changed.
        Update it now or schedule update later
        """
        if self._timer.isActive():
            self._passedUpdate = True
        else:
            self._setCursorPosition(*document.qutepart.cursorPosition)
            self._timer.start()  # one more update after timeout.

    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):
        """Current document has been changed
        """
        if self._timer.isActive():
            self._timer.stop()

        # Update connections
        if oldDocument is not None:
            self.clicked.disconnect(oldDocument.invokeGoTo)
        if currentDocument is not None:
            self.clicked.connect(currentDocument.invokeGoTo)

        # Update info
        if currentDocument is not None:
            self._setCursorPosition(*currentDocument.qutepart.cursorPosition)
            self.setEnabled(True)
        else:
            self._setCursorPosition(-1, -1)
            self.setEnabled(False)

    def _setCursorPosition(self, line, col):
        """Update cursor position on GUI.
        """
        template = self.tr("Line: %s Column: %s")
        if line != -1 and col != -1:
            line = str(line + 1)
            col = str(col)
        else:
            line = '-'
            col = '-'
        self.setText(template % (line, col))
