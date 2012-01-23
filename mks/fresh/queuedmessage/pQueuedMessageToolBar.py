"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import QEvent, Qt
from PyQt4.QtGui import QPainter, QToolBar

from .pQueuedMessageWidget import pQueuedMessageWidget

class pQueuedMessageToolBar(QToolBar):
    def __init__(self, *args):
        QToolBar.__init__(self, *args)
        self._queuedWidget = pQueuedMessageWidget( self )
        
        self.setObjectName( self.metaObject().className() )
        self.setMovable( False )
        self.setFloatable( False )
        self.setAllowedAreas( Qt.TopToolBarArea )
        self.toggleViewAction().setEnabled( False )
        self.toggleViewAction().setVisible( False )
        
        self.addWidget( self._queuedWidget )
        self.layout().setMargin( 3 )
        
        # connections
        self._queuedWidget.shown.connect(self.messageShown)
        self._queuedWidget.finished.connect(self.messageFinished)

    def queuedMessageWidget(self):
        return self._queuedWidget

    def changeEvent(self, event ):
        if  event.type() == QEvent.FontChange :
            self._queuedWidget.setFont( self.font() )

        QToolBar.changeEvent( self, event )

    def paintEvent(self, event ):
        if  self._queuedWidget.pendingMessageCount() == 0 :
            QToolBar.paintEvent( self, event )
            return

        brush = self._queuedWidget.currentMessageBackground()
        painter = QPainter( self )
        painter.setPen( brush.color().darker( 150 ) )
        painter.setBrush( brush )
        painter.drawRect( self.contentsRect().adjusted( 0, 0, -1, -1 ) )

    def appendMessage(self, message, milliSeconds = -1):
        return self._queuedWidget.append( message, milliSeconds )

    def removeMessage(self, message ):
        self._queuedWidget.remove( message )

    def messageShown(self):
        if  not self.isVisible() :
            self.setVisible( True )

    def messageFinished(self):
        if self.isVisible() :
            self.setVisible( False )
