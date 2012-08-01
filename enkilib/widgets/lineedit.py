"""
lineedit --- Extended QLineEdit. Supports prompt and Clear button
=================================================================

This class:
    * shows prompt text, which is visible only if line edit is empty
    * shows Clear button, which is visible only when widget is not empty

Don't use this class if you need classical line edit
"""

from PyQt4.QtCore import pyqtSignal, Qt, QSize
from PyQt4.QtGui import QFontMetrics, QIcon, QLineEdit, QPainter, QPalette, \
                        QStyle, QStyleOptionFrameV3, QToolButton

def tr(text):
    return text

class LineEdit(QLineEdit):
    """Extended QLineEdit.
    Supports prompt and Clear button
    """
    
    clearButtonClicked = pyqtSignal()
    """
    clearButtonClicked()
    
    **Signal** emitted, when Clear button has been clicked
    """

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)

        self._margin = self.sizeHint().height() -2
        self._spacing = 0
        
        self._tbClear = QToolButton( self )
        self._tbClear.setIcon( QIcon(":enkiicons/fresh/edit-clear-rtl.png"))
        self._tbClear.setToolTip( tr( "Clear" ) )
        self._tbClear.setStyleSheet( "QToolButton { border: none; padding: 0px; }" )
        self._tbClear.setCursor( Qt.ArrowCursor )
        self._tbClear.setFocusPolicy( Qt.NoFocus )
        
        self.setClearButtonVisible( False )
        
        self.textChanged.connect(self._onTextChanged)
        self._tbClear.clicked.connect(self.clear)
        self._tbClear.clicked.connect(self.clearButtonClicked)

    def promptText(self):
        """Current prompt text
        """
        return self._promptText

    def setPromptText(self, prompt ):
        """Set prompt text
        """
        self._promptText = prompt
        self.update()

    def paintEvent(self, event ):
        """QLineEdit.paintEvent implementation.
        Draws prompt
        """
        QLineEdit.paintEvent( self, event )
        
        if self._promptText and not self.text() and self.isEnabled() :
            option = QStyleOptionFrameV3()
            self.initStyleOption( option )
            
            left, top, right, bottom = self.getTextMargins()
            
            va = self.style().visualAlignment( self.layoutDirection(), self.alignment() )
            rect = self.style().subElementRect( 
                QStyle.SE_LineEditContents, option, self ).adjusted( 2, 0, 0, 0 ).adjusted( left, top, -right, -bottom )
            fm = QFontMetrics ( self.font() )
            text = fm.elidedText( self._promptText, Qt.ElideRight, rect.width() )
            painter = QPainter ( self )
            
            painter.setPen( self.palette().color( QPalette.Disabled, QPalette.Text ) )
            painter.drawText( rect, va, text )

    def resizeEvent(self, event ):
        """QLineEdit.resizeEvent implementation
        Adjusts Clear button position
        """
        QLineEdit.resizeEvent( self, event )
        
        self._tbClear.resize( QSize( self._margin, self.height() -2 ) )
        self._tbClear.move( self.width() -self._margin -3, 0 )

    def setClearButtonVisible(self, visible ):
        """Set Clear button visible
        """
        self._tbClear.setVisible( visible )
        
        left, top, right, bottom = self.getTextMargins()
        
        if  visible :
            right = self._margin +self._spacing
        else:
            right = 0

        self.setTextMargins( left, top, right, bottom )

    def _onTextChanged(self, text ):
        """Text changed, update Clear button visibility
        """
        self.setClearButtonVisible( len(text) > 0 )
