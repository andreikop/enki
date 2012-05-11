"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import QEvent, QSize, Qt
from PyQt4.QtGui import QDockWidget, QFontMetrics, QIcon, QLinearGradient, QPalette, QPainter, \
                        QSizePolicy, QStyle, \
                        QStyleOptionButton, \
                        QStyleOptionToolButton, \
                        QStyleOptionDockWidgetV2, QTransform, QToolBar, QBoxLayout, QWidget

from mks.fresh.pToolButton import pToolButton

class pDockWidgetTitleBar(QToolBar):
    
    def __init__(self, parent, *args):
        QToolBar.__init__(self, parent, *args)

        self.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Maximum ) )
        self._dock = parent
                
        self.aClose = QToolBar.addAction(self, self.style().standardIcon( QStyle.SP_TitleBarCloseButton ), "")
                
        self.setMovable( False )
        self.setFloatable( False )
        
        self.aClose.triggered.connect(self._dock.close)
        
        textHeight = QFontMetrics(self.font()).height()
        self.setIconSize(QSize(textHeight, textHeight))
        
        # a fake spacer widget
        self._spacer = QWidget( self )
        self._spacer.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.MinimumExpanding ) )
        self.addWidget( self._spacer )

    def paintEvent(self, event ):
        rect = self._spacer.rect()

        painter = QPainter( self )
        
        transform = QTransform()
        transform.translate(self._spacer.pos().x(), self._spacer.pos().y())
        painter.setTransform( transform )
        
        """ Not supported currently
        if  self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar :
            transform = QTransform()
            
            rect.setSize( QSize( rect.height(), rect.width() ) )
            transform.rotate( -90 )
            transform.translate( -rect.width(), 0 )
            
            painter.setTransform( transform )
        """

        # icon / title
        optionB = QStyleOptionButton()
        optionB.initFrom( self._dock )
        optionB.rect = rect
        optionB.text = self._dock.windowTitle()
        optionB.iconSize = self.iconSize()
        optionB.icon = self._dock.windowIcon()
        
        self.style().drawControl( QStyle.CE_PushButtonLabel, optionB, painter, self._dock )

    def minimumSizeHint(self):
        return QToolBar.sizeHint(self)

    def sizeHint(self):
        wis = self.iconSize()
        size = QToolBar.sizeHint(self)
        fm = QFontMetrics ( self.font() )

        if  self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar :
            size.setHeight(size.height() + fm.width( self._dock.windowTitle() ) + wis.width())
        else:
            size.setWidth(size.width() + fm.width( self._dock.windowTitle() ) + wis.width())

        return size

    def addAction(self, action):
        return self.insertAction(self.aClose, action)

    def addSeparator(self):
        return self.insertSeparator(self.aClose)

    def addWidget(self, widget):
        return self.insertWidget(self.aClose, widget)