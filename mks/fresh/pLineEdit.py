"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import pyqtSignal, Qt, QSize
from PyQt4.QtGui import QAction, QFontMetrics, QIcon, QLineEdit, QPainter, QPalette, \
                        QStyle, QStyleOptionFrameV3, QToolButton

def tr(text):
    return text

class pLineEdit(QLineEdit):
    clearButtonClicked = pyqtSignal()
    
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.init()

    def promptText(self):
        return self._promptText

    def setPromptText(self, prompt ):
        self._promptText = prompt
        self.update()

    def paintEvent(self, event ):
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
        QLineEdit.resizeEvent( self, event )
        
        self.tbClear.resize( QSize( self._margin, self.height() -2 ) )
        self.tbClear.move( self.width() -self._margin -3, 0 )


    def init(self):
        self._margin = self.sizeHint().height() -2
        self._spacing = 0
        
        self.tbClear = QToolButton( self )
        self.tbClear.setIcon( QIcon(":mksicons/fresh/edit-clear-rtl.png"))
        self.tbClear.setToolTip( tr( "Clear" ) )
        self.tbClear.setStyleSheet( "QToolButton { border: none; padding: 0px; }" )
        self.tbClear.setCursor( Qt.ArrowCursor )
        self.tbClear.setFocusPolicy( Qt.NoFocus )
        
        self.setClearButtonVisible( False )
        
        self.textChanged.connect(self._q_textChanged)
        self.tbClear.clicked.connect(self.clear)
        self.tbClear.clicked.connect(self.clearButtonClicked)

    def setClearButtonVisible(self, visible ):
        self.tbClear.setVisible( visible )
        
        left, top, right, bottom = self.getTextMargins()
        
        if  visible :
            right = self._margin +self._spacing
        else:
            right = 0

        self.setTextMargins( left, top, right, bottom )

    def _q_textChanged(self, text ):
        self.setClearButtonVisible( len(text) > 0 )
