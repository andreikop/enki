"""
editortoolbar --- Shows position, save state, EOL and indent
============================================================

It also allows to change this parameters and save the file

File contains module implementation
"""

import os.path


from PyQt4.QtCore import QSize, QTimer
from PyQt4.QtGui import QDialog, QFontMetrics, QIcon, QMenu, QToolButton

from enki.core.core import core

# AK: Idea of _EolIndicatorAndSwitcher, and icons for it was taken from juffed

class EolIndicatorAndSwitcher(QToolButton):
    """This widget is visible on Status Bar as EOL type icon.
    
    It draws menu with EOL choise and switches EOL
    """
    _ICON_FOR_MODE = {r'\r\n'   : "winEol.png",
                      r'\r'     : "macEol.png",
                      r'\n'     : "unixEol.png"}
    
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
    
    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):  # pylint: disable=W0613
        """Current document on workspace has been changed
        """
        if currentDocument is not None:
            self._setEolMode( currentDocument.eolMode() )
            self.setEnabled(True)
        else:
            self._setEolMode(None)
            self.setEnabled(False)

    def _onMenuAboutToShow(self):
        """EOL menu has been requested
        """
        document = core.workspace().currentDocument()
        if document is not None:
            currentMode = document.eolMode()
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

        addAction(self.tr("CR+LF: Windows"), r'\r\n')
        addAction(self.tr("CR: Mac OS (but not Mac OS X)"), r'\r')
        addAction(self.tr("LF: Unix"), r'\n')

    def _onEolActionTriggered(self, action):
        """EOL mode selected
        """
        newEol = str(action.data().toString())
        editor = core.workspace().currentDocument()
        editor.setEolMode(newEol)
        self._setEolMode(editor.eolMode())

    def _setEolMode(self, mode):
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
        
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'IndentationDialog.ui'), self)
        self._widthSlider.setValue(document.indentWidth())
        self._updateWidthLabel()
        self._widthSlider.valueChanged.connect(self._onWidthChanged)
        
        if document.indentUseTabs():
            self._tabsRadio.setChecked(True)
        else:
            self._spacesRadio.setChecked(True)
        self._tabsRadio.toggled.connect(self._onTabsToggled)        
        
        self._convertButton.clicked.connect(self._onConvertClicked)
    
    def _updateWidthLabel(self):
        """Update indentation with on GUI
        """
        template = self.tr("Width: %d")
        self._widthLabel.setText(template % self._document.indentWidth())
        
    def _onWidthChanged(self, value):
        """Handler of change of indentation width
        """
        self._document.setIndentWidth(value)
        self._updateWidthLabel()
    
    def _onConvertClicked(self):
        """Handler of Convert button.
        Not implemented yet
        """
        pass
    
    def _onTabsToggled(self, toggled):
        """Handler of change of 'Indentation uses tabs' flag
        """
        self._document.setIndentUseTabs(toggled)

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
    
    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):  # pylint: disable=W0613
        """Current document on workspace has been changed
        """
        if currentDocument is not None:
            self._setIndentMode( currentDocument.indentWidth(), currentDocument.indentUseTabs() )
        else:
            self._clearIndentMode()

    def _onIndentSettingsChanged(self, document, newValue):
        """Document settings changed. Update themselves, if necessary
        """
        if document == core.workspace().currentDocument():
            self._setIndentMode(document.indentWidth(), document.indentUseTabs())
    
    def _onClicked(self):
        """Indentation button clicked. Show dialog
        """
        document = core.workspace().currentDocument()
        if document is not None:
            dialog = _IndentationDialog(self, document)
            dialog.exec_()
            self._setIndentMode(document.indentWidth(), document.indentUseTabs())
    
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
    
    def __del__(self):
        if self._timer.isActive():
            self._timer.stop()
    
    def _onUpdatePositionTimer(self):
        """Update text on GUI according to current position
        """
        if self._passedUpdate:
            document = core.workspace().currentDocument()
            self._setCursorPosition( *document.qutepart.cursorPosition())
            self._passedUpdate = False

    def _onCursorPositionChanged(self, document):
        """Cursor position changed.
        Update it now or schedule update later
        """
        if self._timer.isActive():
            self._passedUpdate = True
        else:
            self._setCursorPosition(*document.qutepart.cursorPosition())
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
            self._setCursorPosition( *currentDocument.qutepart.cursorPosition())
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
