"""Queued message tool bar. Not a public API, but available via MainWindow.appendMessage()
"""

from PyQt4.QtCore import pyqtSignal, QEvent, Qt, QTimer
from PyQt4.QtGui import QAbstractButton, QColor, QBrush, QDialogButtonBox, QHBoxLayout, \
                        QLabel, QPainter, QPixmap, QSizePolicy, QToolBar, QWidget


class _QueuedMessage:
    def __init__(self):
        self.milliSeconds = -1
        self.background = QBrush( Qt.NoBrush )
        self.foreground = QBrush( Qt.NoBrush )
        self.slot = None
        self.buttons = {}

class _QueuedMessageWidget(QWidget):

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
        self._defaultPixmap = QPixmap(":/enkiicons/infos.png" )
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

        # if false - buttons don't have neither text nor icons
        self.dbbButtons.setStyleSheet("dialogbuttonbox-buttons-have-icons: true;")

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
        msg = _QueuedMessage()
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
            msg.buttons[ QDialogButtonBox.Close ] = None

        self.dbbButtons.clear()

        for button in msg.buttons.iterkeys():
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


class QueuedMessageToolBar(QToolBar):
    def __init__(self, *args):
        QToolBar.__init__(self, *args)
        self._queuedWidget = _QueuedMessageWidget( self )

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
