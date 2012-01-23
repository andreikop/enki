"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import pyqtSignal, Qt, QSize, QTimer
from PyQt4.QtGui import QAction, QFontMetrics, QIcon, QLineEdit, QPainter, QPalette, \
                        QStyle, QStyleOptionFrameV3, QToolButton

def tr(text):
    return text

class pLineEdit(QLineEdit):
    _TIMEOUT = 1000
    
    searchButtonClicked = pyqtSignal()
    searchButtonActionTriggered = pyqtSignal(QAction)
    clearButtonClicked = pyqtSignal()
    searchTextChanged = pyqtSignal(unicode)
    
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.init()

    def menu(self):
        return self.tbSearch.menu()

    def setMenu(self, menu ):
        self.tbSearch.setMenu( menu )

    def isSearchButtonVisible(self):
        return self.tbSearch.isVisible()

    def promptText(self):
        return self._promptText

    def setSearchButtonVisible(self, visible ):
        self.tbSearch.setVisible( visible )
        
        left, top, right, bottom = self.getTextMargins()
        
        if  visible :
            left = self._margin + self._spacing
        else:
            left = 0

        self.setTextMargins( left, top, right, bottom )

    def setPromptText(self, prompt ):
        self._promptText = prompt
        self.update()

    def clickSearchButton(self):
        self.tbSearch.click()

    def clickClearButton(self):
        self.tbClear.click()

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
        
        self.tbSearch.resize( QSize( self._margin, self.height() -2 ) )
        self.tbSearch.move( 3, 1 )
        self.tbClear.resize( QSize( self._margin, self.height() -2 ) )
        self.tbClear.move( self.width() -self._margin -3, 0 )


    def init(self):
        self._margin = self.sizeHint().height() -2
        self._spacing = 0
        
        self.tbSearch = QToolButton( self )
        self.tbSearch.setIcon( QIcon(":mksicons/fresh/search.png"))
        self.tbSearch.setToolTip( tr( "Search Options" ) )
        self.tbSearch.setStyleSheet( 
            "QToolButton { border: none; padding: 0px; } QToolButton.menu-indicator { right: -2px; bottom: -2px; }" )
        self.tbSearch.setCursor( Qt.ArrowCursor )
        self.tbSearch.setFocusPolicy( Qt.NoFocus )
        self.tbSearch.setPopupMode( QToolButton.InstantPopup )
        
        self.tbClear = QToolButton( self )
        self.tbClear.setIcon( QIcon(":mksicons/fresh/edit-clear-rtl.png"))
        self.tbClear.setToolTip( tr( "Clear" ) )
        self.tbClear.setStyleSheet( "QToolButton { border: none; padding: 0px; }" )
        self.tbClear.setCursor( Qt.ArrowCursor )
        self.tbClear.setFocusPolicy( Qt.NoFocus )
        
        self.setSearchButtonVisible( True )
        self.setClearButtonVisible( False )
        self.setPromptText( "Search..." )
        
        self._timer = QTimer( self )
        self._timer.setInterval( pLineEdit._TIMEOUT )
        self._timer.setSingleShot( True )
        
        self.textChanged.connect(self._q_textChanged)
        self.tbSearch.clicked.connect(self.searchButtonClicked)
        self.tbSearch.triggered.connect(self.searchButtonActionTriggered)
        self.tbClear.clicked.connect(self.clear)
        self.tbClear.clicked.connect(self.clearButtonClicked)
        self._timer.timeout.connect(self.timer_timeout)

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
        self._timer.start()

    def timer_timeout(self):
        self.searchTextChanged.emit( self.text() )
