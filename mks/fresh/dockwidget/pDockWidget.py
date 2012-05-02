"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import pyqtSignal, Qt, QTimer
from PyQt4.QtGui import QAction, QColor, QDockWidget, QKeySequence, QPainter, QShortcut

from .pDockWidgetTitleBar import pDockWidgetTitleBar

class pDockWidget(QDockWidget):
    
    toggleViewAction_triggered = pyqtSignal()
    
    def __init__(self, *args):
        QDockWidget.__init__(self, *args)

        self._showAction = None
        self._titleBar = pDockWidgetTitleBar( self )
        self.setTitleBarWidget( self._titleBar )
        self.toggleViewAction().triggered.connect(self.toggleViewAction_triggered)
        
        self._closeShortcut = QShortcut( QKeySequence( "Esc" ), self )
        self._closeShortcut.setContext( Qt.WidgetWithChildrenShortcut )
        self._closeShortcut.activated.connect(self._hide)

    def paintEvent(self, event ):
        QDockWidget.paintEvent(self,  event )
        
        if  self.isFloating() and self.style().objectName().lower() != "Oxygen".lower():
            rect = self.rect().adjusted( 0, 0, -1, -1 )
            
            painter = QPainter( self )
            painter.setPen( QColor( 145, 142, 142 ) )
            painter.setBrush( Qt.NoBrush )
            painter.drawRect( rect )

    def titleBar(self):
        return self._titleBar

    def showAction(self):
        if  not self._showAction :
            self._showAction = QAction(self.windowIcon(), self.windowTitle(), self)
            self._showAction.triggered.connect(self.show)
            self._showAction.triggered.connect(self.handleFocusProxy)

        return self._showAction

    def toggleViewAction_triggered(self, toggled ):
        if toggled and self.focusProxy() is not None:
            if  self.isFloating():
                QTimer.singleShot( 0, self.handleWindowActivation )
            else:
                QTimer.singleShot( 0, self.handleFocusProxy )

    def handleWindowActivation(self):
        self.activateWindow()
        QTimer.singleShot( 0, self.handleFocusProxy )

    def handleFocusProxy(self):
        if self.focusProxy() is not None:
            self.setFocus()

    def _hide(self):
        """Hide and return focus to MainWindow focus proxy
        """
        self.hide()
        if self.parent() is not None and \
           self.parent().focusProxy() is not None:
            self.parent().focusProxy().setFocus()
