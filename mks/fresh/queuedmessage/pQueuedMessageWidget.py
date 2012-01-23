"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import pyqtSignal, Qt, QTimer
from PyQt4.QtGui import QAbstractButton, QColor, QBrush, QDialogButtonBox, QHBoxLayout, \
                        QLabel, QPainter, QPixmap, QSizePolicy, QWidget

class pQueuedMessage:
    def __init__(self):
        self.milliSeconds = -1
        self.background = QBrush( Qt.NoBrush )
        self.foreground = QBrush( Qt.NoBrush )
        self.slot = None
        self.buttons = {}

class pQueuedMessageWidget(QWidget):
    
    cleared = pyqtSignal()
    finished = pyqtSignal()
    shown = pyqtSignal()
    closed = pyqtSignal()
    linkActivated = pyqtSignal(unicode)
    linkHovered= pyqtSignal(unicode)
    buttonClicked = pyqtSignal(QAbstractButton)
    
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self._messages = []
        self._defaultTimeout = 0
        self._defaultPixmap = QPixmap(":/mksicons/fresh/info.png" )
        self._defaultBackground = QBrush( QColor( 250, 230, 147 ) )
        self._defaultForeground = QBrush( QColor( 0, 0, 0 ) )
        
        # pixmap
        self.lPixmap = QLabel( self )
        self.lPixmap.setAlignment( Qt.AlignCenter )
        self.lPixmap.setSizePolicy( QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Preferred ) )
        
        # message
        self.lMessage = QLabel( self )
        self.lMessage.setAlignment( Qt.AlignVCenter | Qt.AlignLeft )
        self.lMessage.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred ) )
        self.lMessage.setWordWrap( True )
        self.lMessage.setOpenExternalLinks( True )
        self.lMessage.setTextInteractionFlags( Qt.TextBrowserInteraction )
        
        # button
        self.dbbButtons = QDialogButtonBox( self )
        self.dbbButtons.setSizePolicy( QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Preferred ) )
        
        self.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Maximum ) )
        
        # layout
        self.hbl = QHBoxLayout( self )
        self.hbl.setMargin( 0 )
        self.hbl.addWidget( self.lPixmap, 0, Qt.AlignCenter )
        self.hbl.addWidget( self.lMessage )
        self.hbl.addWidget( self.dbbButtons, 0, Qt.AlignCenter )
        
        # connections
        self.lMessage.linkActivated.connect(self.linkActivated)
        self.lMessage.linkHovered.connect(self.linkHovered)
        self.dbbButtons.clicked.connect(self.buttonClicked)

    def sizeHint(self):
        return QWidget.minimumSizeHint(self)

    def openExternalLinks(self):
        return self.lMessage.openExternalLinks()

    def defaultTimeout(self):
        return self._defaultTimeout

    def defaultPixmap(self):
        return self._defaultPixmap

    def defaultBackground(self):
        return self._defaultBackground

    def defaultForeground(self):
        return self._defaultForeground

    def currentMessageInformations(self):
        return self.currentMessagePixmap(), self.currentMessageBackground(), self.currentMessageForeground()

    def pendingMessageCount(self):
        return len(self._messages)

    def currentMessage(self):
        return self._messages[0]

    def append(self, message, milliSeconds ):
        msg = pQueuedMessage()
        msg.message = message
        if milliSeconds == -1:
            msg.milliSeconds = self._defaultTimeout
        else:
           msg.milliSeconds = milliSeconds
        msg.pixmap = self._defaultPixmap
        msg.background = self._defaultBackground
        msg.foreground = self._defaultForeground
        
        self._messages.append(msg)
            
        if  len(self._messages) == 1 :
            QTimer.singleShot( 0, self.showMessage)

    def setOpenExternalLinks(self, open ):
        self.lMessage.setOpenExternalLinks( open )

    def setDefaultTimeout(self, timeout ):
        self._defaultTimeout = timeout

    def setDefaultPixmap(self, pixmap ):
        self._defaultPixmap = pixmap

    def setDefaultBackground(self, brush ):
        self._defaultBackground = brush

    def setDefaultForeground(self, brush ):
        self._defaultForeground = brush

    def remove(self, message ):
        raise NotImplemented()  # incorrect port from cpp fresh
        if not self._messages or self._messages.first() == message:
            return

        self._messages.removeOne( message )

    def clear(self):
        self._messages.clear()
        self.lPixmap.clear()
        self.lMessage.clear()
        self.dbbButtons.clear()
        self.cleared.emit()

    def currentMessagePixmap(self):
        msg = self.currentMessage()
        if msg.pixmap.isNull():
            return self._defaultPixmap
        else:
            return msg.pixmap

    def currentMessageBackground(self):
        msg = self.currentMessage()
        if msg.background == QBrush( Qt.NoBrush ):
            return self._defaultBackground
        else:
            return msg.background

    def currentMessageForeground(self):
        msg = self.currentMessage()
        if msg.foreground == QBrush( Qt.NoBrush ):
            return self._defaultForeground
        else:
            return msg.foreground

    def paintEvent(self, event ):
        if  self.pendingMessageCount() == 0 :
            QWidget.paintEvent(self, event )
            return
        
        painter = QPainter( self )
        painter.setPen( Qt.NoPen )
        painter.setBrush( self.currentMessageBackground() )
        painter.drawRect( self.contentsRect() )

    def buttonClicked(self, button ):
        msg = self.currentMessage()
        standardButton = self.dbbButtons.standardButton( button )
        
        if msg.slot is not None:
            msg.slot(standardButton, msg)
        
        self.closeMessage()

    def showMessage(self):
        # get message
        msg = self.currentMessage()
        
        # update palette
        pal = self.lMessage.palette()
        pal.setBrush( self.lMessage.foregroundRole(), self.currentMessageForeground() )
        self.lMessage.setPalette( pal )
        
        # format widget
        self.lPixmap.setPixmap( self.currentMessagePixmap() )
        self.lMessage.setText( msg.message )
        self.lMessage.setToolTip( msg.message )
        self.lMessage.setWhatsThis( msg.message )
        
        # set buttons
        if not msg.buttons:
            msg.buttons[ QDialogButtonBox.Ok ] = None

        self.dbbButtons.clear()
        
        for button in msg.buttons.keys():
            pb = self.dbbButtons.addButton( button )
            
            if button in msg.buttons:
                pb.setText( msg.buttons[ button ] )
        
        # auto close if needed
        if msg.milliSeconds == -1:
            timeout = self._defaultTimeout
        else:
            timeout =  msg.milliSeconds
        
        if  timeout > 0:
            QTimer.singleShot( timeout, self.closeMessage )
        
        # signal.emit
        self.shown.emit()

    def closeMessage(self):
        # message.emit
        self.closed.emit()
        
        # remove remove current message from hash
        self._messages = self._messages[1:]
        
        # process next if possible, clear gui
        if self._messages:
            QTimer.singleShot( 0, self.showMessage)
        else:
            QTimer.singleShot( 0, self.clearMessage)
        
        # finished.emit message if needed
        if not self._messages:
            self.finished.emit()

    def clearMessage(self):
        self.lPixmap.clear()
        self.lMessage.clear()
        self.dbbButtons.clear()
