"""Status bar shows shows current line, column, save state, EOL and indent mode
"""

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QFrame, QIcon, QLabel, QMenu, QPixmap, QStatusBar

import mks.monkeycore

"""AK: Idea of _EolIndicatorAndSwitcher, and icons for it was taken from juffed
"""

class _EolIndicatorAndSwitcher(QLabel):
    """This widget is visible on Status Bar as EOL type icon.
    It draws menu with EOL choise and switches EOL
    """
    _ICON_FOR_MODE = {r'\r\n'   : "winEol.png",
                      r'\r'     : "macEol.png",
                      r'\n'     : "unixEol.png"}
    
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setEnabled(False)
        self.setToolTip(self.tr("Line endings. Click for convert"))
        mks.monkeycore.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
    
    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):
        if currentDocument is not None:
            self._setEolMode( currentDocument.eolMode() )
        else:
            self._setEolMode(None)
    
    def mouseReleaseEvent(self, event):
        editor = mks.monkeycore.workspace().currentDocument()
        if editor is not None:
            currentMode = editor.eolMode()
            self._eolMenu(currentMode).exec_(event.globalPos())

    def _eolMenu(self, currentMode):
        """Generate EOL menu
        """
        def addAction(menu, text, eolMode):
            action = menu.addAction(QIcon(':/mksicons/' + self._ICON_FOR_MODE[eolMode]), text)
            action.triggered.connect(self._onEolActionTriggered)
            action.setData(eolMode)
            if eolMode == currentMode:
                action.setCheckable(True)
                action.setChecked(True)
            return action
        eolMenu = QMenu()
        addAction(eolMenu, self.tr("CR+LF: Windows"), r'\r\n')
        addAction(eolMenu, self.tr("CR: Mac OS (but not Mac OS X)"), r'\r')
        addAction(eolMenu, self.tr("LF: Unix"), r'\n')
        return eolMenu

    def _onEolActionTriggered(self):
        action = self.sender()
        newEol = str(action.data().toString())
        editor = mks.monkeycore.workspace().currentDocument()
        editor.setEolMode(newEol)
        self._setEolMode(editor.eolMode())

    def _setEolMode(self, mode):
        if mode is not None:
            icon = QIcon(':/mksicons/' + self._ICON_FOR_MODE[mode])
            self.setPixmap(icon.pixmap(16, 16))
            self.setEnabled(True)
        else:
            self.setEnabled(False)

class StatusBar(QStatusBar):
    """Class implementes statusbar. Bar shows current line, column, save state, EOL and indent mode
    """

    def __init__(self, parent):
        QStatusBar.__init__(self, parent)
        # create labels
        
        def createLabel(tip):
            label = QLabel(self)
            label.setToolTip(tip)
            label.setMargin( 2 )
            label.setFrameStyle( QFrame.NoFrame )
            label.setAttribute( Qt.WA_MacSmallSize )
            self.addPermanentWidget( label )
            return label
        
        self._cursorPos = createLabel(self.tr("Cursor position"))
        self._modified = createLabel(self.tr("Modification state of file"))
        
        # EOL indicator and switcher
        self._eolSwitcher = _EolIndicatorAndSwitcher(self)
        self.addPermanentWidget(self._eolSwitcher)
        
        self._indentation = createLabel(self.tr("Indentation mode"))
        createLabel(self.tr("Line")).setText("Line:")
        self._line = createLabel(self.tr("Line"))
        createLabel(self.tr("Column")).setText("Column:")
        self._col = createLabel(self.tr("Column"))
        
        # Avoid flickering, when line length of a number changes
        self._line.setMinimumWidth(30)
        self._line.setMargin(0)
        self._col.setMinimumWidth(30)
        self._line.setMargin(0)
        
        # force remove statusbar label frame
        self.setStyleSheet( "QStatusBar.item { border: 0px; }" )
        
        # connections
        self.messageChanged.connect(self.setMessage)
        
        mks.monkeycore.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)

    def _onCurrentDocumentChanged(self, oldDocument, currentDocument):
        # Update connections
        if oldDocument is not None:
            oldDocument.cursorPositionChanged.disconnect(self._setCursorPosition)
            oldDocument.modifiedChanged.disconnect(self._setModified)
        if currentDocument is not None:
            currentDocument.cursorPositionChanged.connect(self._setCursorPosition)
            currentDocument.modifiedChanged.connect(self._setModified)
        
        # Update info
        if currentDocument is not None:
            self._setModified( currentDocument.isModified() )
            #self.setIndentMode( currentDocument.indentationsUseTabs())
            self._setCursorPosition( *currentDocument.cursorPosition())
        else:
            self._setModified(False)
            #self.setIndentMode( document.indentationsUseTabs())
            self._setCursorPosition(-1, -1)

    def setMessage(self, message ):
        self.showMessage( message )
        self.setToolTip( message )

    def _setModified(self, modified):
        icon = QIcon( ":/mksicons/save.png" )
        if modified:
            pixmap = icon.pixmap(16, 16, QIcon.Normal)
        else:
            pixmap = icon.pixmap(16, 16, QIcon.Disabled)
        self._modified.setPixmap(pixmap)
    
    def setIndentMode(self, mode ):
        self._indentation.setText(mode)

    def _setCursorPosition(self, line, col):
        if line != -1 and col != -1:
            self._line.setText(str(line))
            self._col.setText(str(col))
        else:
            self._line.setText('-')
            self._col.setText('-')
