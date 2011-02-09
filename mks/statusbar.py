"""Status bar shows shows current line, column, save state, EOL and indent mode
"""

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QFrame, QIcon, QLabel, QPixmap, QStatusBar

import mks.monkeycore

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
        self._EOL = createLabel(self.tr("EOL mode"))
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
            oldDocument.cursorPositionChanged.disconnect(self.setCursorPosition)
            oldDocument.modifiedChanged.disconnect(self.setModified)
        if currentDocument is not None:
            currentDocument.cursorPositionChanged.connect(self.setCursorPosition)
            currentDocument.modifiedChanged.connect(self.setModified)
        
        # Update info
        if currentDocument is not None:
            self.setModified( currentDocument.isModified() )
            #self.setEOLMode( currentDocument.eolMode() )
            #self.setIndentMode( currentDocument.indentationsUseTabs())
            self.setCursorPosition( *currentDocument.cursorPosition())
        else:
            self.setModified(False)
            #self.setEOLMode(None)
            #self.setIndentMode( document.indentationsUseTabs())
            self.setCursorPosition(-1, -1)

    def setMessage(self, message ):
        self.showMessage( message )
        self.setToolTip( message )

    def setModified(self, modified):
        icon = QIcon( ":/mksicons/save.png" )
        if modified:
            pixmap = icon.pixmap(16, 16, QIcon.Normal)
        else:
            pixmap = icon.pixmap(16, 16, QIcon.Disabled)
        self._modified.setPixmap(pixmap)

    def setEOLMode(self, mode ):
        convertor = {QsciScintilla.EolWindows: "Win",
                     QsciScintilla.EolUnix: "Unix"}
        self._EOL.setText(convertor[mode])

    def setIndentMode(self, mode ):
        self._indentation.setText(mode)

    def setCursorPosition(self, line, col):
        if line != -1 and col != -1:
            self._line.setText(str(line))
            self._col.setText(str(col))
        else:
            self._line.setText('-')
            self._col.setText('-')
