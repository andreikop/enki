from PyQt4.QtCore import QEvent, QSize, Qt
from PyQt4.QtGui import QDockWidget, QFontMetrics, QIcon, QLinearGradient, QPalette, QPainter, \
                        QSizePolicy, QStyle, \
                        QStyleOptionButton, \
                        QStyleOptionToolButton, \
                        QStyleOptionDockWidgetV2, QTransform, QToolBar, QBoxLayout, QWidget

from mks.fresh.pToolButton import pToolButton

class pDockWidgetTitleBar(QToolBar):
    
    _useNativePaintDefault = True
    
    def __init__(self, parent, *args):
        QToolBar.__init__(self, parent, *args)

        self._dock = parent
        self._useNativePaint = pDockWidgetTitleBar._useNativePaintDefault
        
        # a fake spacer widget
        spacer = QWidget( self )
        spacer.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Maximum ) )
        
        self.tbOrientation = pToolButton( self )
        self.tbOrientation.installEventFilter( self )
        self.tbFloat = pToolButton( self )
        self.tbFloat.installEventFilter( self )
        self.tbClose = pToolButton( self )
        self.tbClose.installEventFilter( self )
        
        self.addWidget( spacer )
        self.aOrientation = self.addWidget( self.tbOrientation )
        self.aFloat = self.addWidget( self.tbFloat )
        self.aClose = self.addWidget( self.tbClose )
        
        self.tbOrientation.setDefaultAction( self.aOrientation )
        self.tbFloat.setDefaultAction( self.aFloat )
        self.tbClose.setDefaultAction( self.aClose )
        
        self.setMovable( False )
        self.setFloatable( False )
        
        self.updateStyleChange()
        self.dockWidget_featuresChanged( self._dock.features() )
        
        self._dock.featuresChanged.connect(self.dockWidget_featuresChanged)
        self.aOrientation.triggered.connect(self.aOrientation_triggered)
        self.aFloat.triggered.connect(self.aFloat_triggered)
        self.aClose.triggered.connect(self._dock.close)

    def icon(self):
        icon = self._dock.toggleViewAction().icon()
        
        if  icon.isNull() :
            icon = self._dock.windowIcon()

        if  icon.isNull() :
            icon =  toggleViewAction().icon()

        if  icon.isNull() :
            icon =  windowIcon()

        if  icon.isNull() :
            icon = window().windowIcon()
        
        return icon

    def windowIconSize(self):
        if self.orientation() == Qt.Horizontal:
            size = self.height() -2
        else:
            size = self.width() -2
        
        if self.icon().isNull():
            return  QSize()
        else:
            return QSize( size, size )

    def event(self, event ):
        if event.type() == QEvent.StyleChange:
            self.updateStyleChange()
        
        return QToolBar.event( self, event )

    def eventFilter(self, object, event ):
        button = object
        
        if  button is not None and event.type() == QEvent.Paint:
            option = QStyleOptionToolButton()
            button.initStyleOption( option )
            option.icon = QIcon()
            
            button.paint( option )
            painter = QPainter( button )
            button.icon().paint( painter, button.rect(), Qt.AlignCenter, QIcon.Normal, QIcon.Off )
            
            event.accept()
            return True

        return QToolBar.eventFilter( self, object, event )

    def paintEvent(self, event ):
        rect = self.rect()
        painter = QPainter( self )
        
        # native background paint for not common style / native paint
        if  ( self._useNativePaint or \
              self.style().inherits( "QMacStyle" ) or \
              self.style().inherits( "Oxygen.Style" ) ) and \
             isinstance(self._dock, type(self._dock)):
            optionDw = QStyleOptionDockWidgetV2()
            self._dock.initStyleOption( optionDw )
            optionDw.title = ''
            optionDw.closable = False
            optionDw.floatable = False
            optionDw.movable = False
            optionDw.rect = rect
            
            self.style().drawControl( QStyle.CE_DockWidgetTitle, optionDw, painter, self._dock )
        # custom background
        else:
            topColor = palette().color( QPalette.Highlight ).lighter( 130 )
            bottomColor = palette().color( QPalette.Highlight ).darker( 130 )
            gradient = QLinearGradient( rect.topLeft(), rect.bottomLeft() )
            
            topColor.setAlphaF( .7 )
            bottomColor.setAlphaF( .7 )
            
            gradient.setColorAt( 0, topColor )
            gradient.setColorAt( 1, bottomColor )
            
            if  self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar :
                gradient.setFinalStop( rect.topRight() )
        
            painter.setPen( Qt.NoPen )
            painter.setBrush( gradient )
            painter.drawRect( rect )
            
            painter.setPen( bottomColor.darker( 130 ) )
            painter.setBrush( Qt.NoBrush )
            painter.drawRect( rect.adjusted( 0, 0, -1, -1 ) )
        
        if  self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar :
            transform = QTransform()
            
            rect.setSize( QSize( rect.height(), rect.width() ) )
            transform.rotate( -90 )
            transform.translate( -rect.width(), 0 )
            
            painter.setTransform( transform )

        # icon / title
        optionB = QStyleOptionButton()
        optionB.initFrom( self._dock )
        if self.orientation() == Qt.Horizontal:
           sh = self.minimumSizeHint().width()
        else:
           sh = self.minimumSizeHint().height()
        optionB.rect = rect.adjusted( 2, 0, -sh, 0 )
        optionB.text = self._dock.windowTitle()
        optionB.iconSize = self.windowIconSize()
        optionB.icon = self.icon()
        
        self.style().drawControl( QStyle.CE_PushButtonLabel, optionB, painter, self._dock )

    def updateStyleChange(self):
        self.setIconSize( QSize( 13, 13 ) )
        self.layout().setSpacing( 0 )
        self.layout().setMargin( 2 )
        
        icon = QIcon()
        
        icon = self.style().standardIcon( QStyle.SP_TitleBarShadeButton, None, self.widgetForAction( self.aOrientation ) )
        self.aOrientation.setIcon( icon )
        
        icon = self.style().standardIcon( QStyle.SP_TitleBarNormalButton, None, self.widgetForAction( self.aFloat ) )
        self.aFloat.setIcon( icon )
        
        icon = self.style().standardIcon( QStyle.SP_TitleBarCloseButton, None, self.widgetForAction( self.aClose ) )
        self.aClose.setIcon( icon )
        
        if  self.orientation() == Qt.Horizontal :
            self.tbOrientation.setDirection( QBoxLayout.LeftToRight )
            self.tbFloat.setDirection( QBoxLayout.LeftToRight )
            self.tbClose.setDirection( QBoxLayout.LeftToRight )
        else:
            self.tbOrientation.setDirection( QBoxLayout.BottomToTop )
            self.tbFloat.setDirection( QBoxLayout.BottomToTop )
            self.tbClose.setDirection( QBoxLayout.BottomToTop )

    def minimumSizeHint(self):
        return QToolBar.sizeHint(self)

    def sizeHint(self):
        wis = self.windowIconSize()
        size = QToolBar.sizeHint(self)
        fm = QFontMetrics ( self.font() )

        """ wtf?
        if  self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar :
            size.rheight() += fm.width( self._dock.windowTitle() ) + wis.width()
        else:
            size.rwidth() += fm.width( self._dock.windowTitle() ) + wis.width()
        """

        return size

    def addAction(self, action, index ):
        if  index != -1 :
            index += 1
        
        if  index >= 0 and index < len(self.actions()):
            QToolBar.insertAction(self, self.actions()[index], action )
        else:
            QToolBar.addAction( self, action )

        return self.widgetForAction( action )

    def addSeparator(self, index ):
        if  index != -1 :
            index += 1
    
        if  index >= 0 and index < len(self.actions()):
            QToolBar.insertSeparator( self, self.actions()[index] )
        else:
            QToolBar.addSeparator(self)

    def setNativeRendering(self, native ):
        self._useNativePaint = native
        self.update()

    def nativeRendering(self):
        return self._useNativePaint

    @staticmethod
    def setDefaultNativeRendering(native ):
        pDockWidgetTitleBar._useNativePaintDefault = native

    def defaultNativeRendering(self):
        return self._useNativePaintDefault

    def aOrientation_triggered(self):
        features = self._dock.features()
        
        if  features & QDockWidget.DockWidgetVerticalTitleBar:
            self._dock.setFeatures( features ^ QDockWidget.DockWidgetVerticalTitleBar )
        else:
            self._dock.setFeatures( features | QDockWidget.DockWidgetVerticalTitleBar )

    def aFloat_triggered(self):
        self._dock.setFloating( not self._dock.isFloating() )

    def dockWidget_featuresChanged(self, features ):
        self.aFloat.setVisible( features & QDockWidget.DockWidgetFloatable )
        self.aClose.setVisible( features & QDockWidget.DockWidgetClosable )
        
        # update toolbar orientation
        if  features & QDockWidget.DockWidgetVerticalTitleBar:
            if self.orientation() == Qt.Vertical :
                return
            self.setOrientation( Qt.Vertical )
        else:
            if  self.orientation() == Qt.Horizontal :
                return
            self.setOrientation( Qt.Horizontal )

        # re-order the actions
        actions = self.actions()[::-1]
        self.clear()
        self.addActions( actions )
        self.updateStyleChange()
