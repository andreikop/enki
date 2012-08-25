"""
dockwidget --- Extended QDockWidget for Enki main window
========================================================

This class adds next features to QDockWidget:
    * has action for showing and focusing the widget
    * closes themselves on Esc
    * title bar contains QToolBar
"""

from PyQt4.QtCore import pyqtSignal, QSize, Qt, QTimer
from PyQt4.QtGui import QAction, QColor, QDockWidget, QFontMetrics, QIcon, \
                        QKeySequence, QPainter, QShortcut, QSizePolicy, QStyle, QStyleOptionButton, \
                        QTransform, QToolBar, QWidget


class _TitleBar(QToolBar):
    """Widget title bar.
    Contains standard dock widget buttons and allows to add new buttons and widgets
    """
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
        """QToolBar.paintEvent reimplementation
        Draws buttons, dock icon and text
        """
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
        """QToolBar.minimumSizeHint implementation
        """
        return QToolBar.sizeHint(self)

    def sizeHint(self):
        """QToolBar.sizeHint implementation
        """
        wis = self.iconSize()
        size = QToolBar.sizeHint(self)
        fm = QFontMetrics ( self.font() )

        if  self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar :
            size.setHeight(size.height() + fm.width( self._dock.windowTitle() ) + wis.width())
        else:
            size.setWidth(size.width() + fm.width( self._dock.windowTitle() ) + wis.width())

        return size

    def addAction(self, action):
        """QToolBar.addAction implementation
        Adjusts indexes for behaving like standard empty QTitleBar
        """
        return self.insertAction(self.aClose, action)

    def addSeparator(self):
        """QToolBar.addAction implementation
        Adjusts indexes for behaving like standard empty QTitleBar
        """
        return self.insertSeparator(self.aClose)

    def addWidget(self, widget):
        """QToolBar.addAction implementation
        Adjusts indexes for behaving like standard empty QTitleBar
        """
        return self.insertWidget(self.aClose, widget)


class DockWidget(QDockWidget):
    """Extended QDockWidget for Enki main window
    """
    def __init__(self, parentObject, objectName, windowTitle, windowIcon = QIcon(), shortcut = None):
        QDockWidget.__init__(self, parentObject)
        self._showAction = None

        self.setObjectName(objectName)
        self.setWindowTitle(windowTitle)
        
        if not windowIcon.isNull():
            self.setWindowIcon(windowIcon)
        if shortcut is not None:
            self.showAction().setShortcut(shortcut)

        self._titleBar = _TitleBar( self )
        self.setTitleBarWidget( self._titleBar )
        
        self._closeShortcut = QShortcut( QKeySequence( "Esc" ), self )
        self._closeShortcut.setContext( Qt.WidgetWithChildrenShortcut )
        self._closeShortcut.activated.connect(self._hide)

    def showAction(self):
        """Action shows the widget and set focus on it.
        
        Add this action to the main menu
        """
        if  not self._showAction :
            self._showAction = QAction(self.windowIcon(), self.windowTitle(), self)
            self._showAction.triggered.connect(self.show)
            self._showAction.triggered.connect(self._handleFocusProxy)

        return self._showAction

    def titleBarWidget(self):
        """QToolBar on the title.
        
        You may add own actions to this tool bar
        """
        # method was added only for documenting
        return QDockWidget.titleBarWidget(self)
    
    def _handleFocusProxy(self):
        """Set focus to focus proxy.
        Called after widget has been shown
        """
        if self.focusProxy() is not None:
            self.setFocus()

    def _hide(self):
        """Hide and return focus to MainWindow focus proxy
        """
        self.hide()
        if self.parent() is not None and \
           self.parent().focusProxy() is not None:
            self.parent().focusProxy().setFocus()
