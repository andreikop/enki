"""
dockwidget --- Extended QDockWidget for Enki main window
========================================================

This class adds next features to QDockWidget:
    * has action for showing and focusing the widget
    * closes themselves on Esc
    * title bar contains QToolBar
"""

import os.path
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import QAction, QDockWidget, \
    QShortcut, QSizePolicy, QStyle, \
    QStyleOptionButton, QToolBar, QWidget, QToolButton
from PyQt5.QtGui import QFontMetrics, QIcon, \
    QKeySequence, QPainter, \
    QTransform, QPixmap
from enki.core.core import core


class _TitleBar(QToolBar):
    """Widget title bar.
    Contains standard dock widget buttons and allows to add new buttons and widgets
    """

    def __init__(self, parent, *args):
        QToolBar.__init__(self, parent, *args)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum))
        self._dock = parent

        closeIcon = self.style().standardIcon(QStyle.SP_DockWidgetCloseButton)
        if not closeIcon.availableSizes():
            # SP_DockWidgetCloseButton is missing on Fedora. Why??? Using fallback
            closeIcon = self.style().standardIcon(QStyle.SP_DialogCloseButton)

        self.aClose = QToolBar.addAction(self, closeIcon, "")

        self.setMovable(False)
        self.setFloatable(False)

        self.aClose.triggered.connect(self._dock.close)

        textHeight = QFontMetrics(self.font()).height()
        self.setIconSize(QSize(int(textHeight * 0.8), int(textHeight * 0.8)))

        # a fake spacer widget
        self._spacer = QWidget(self)
        self._spacer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding))
        self.addWidget(self._spacer)

        self.setStyleSheet('QToolBar{spacing:0px; margin:0px}')

        # The pinned/unpinned control.
        self.tbUnPinned = QToolButton()
        icon = QIcon()
        # To do: Replace with my own image and put in resources.
        icon.addPixmap(QPixmap(os.path.join(os.path.dirname(__file__), 'unpinned.png')), QIcon.Normal, QIcon.On)
        icon.addPixmap(QPixmap(os.path.join(os.path.dirname(__file__), 'pinned.png')), QIcon.Normal, QIcon.Off)
        self.tbUnPinned.setIcon(icon)
        self.tbUnPinned.setCheckable(True)
        self._configName = parent.windowTitle() + " pinned"
        if self._configName in core.config():
            self.tbUnPinned.setChecked(not core.config()[self._configName])
        self.tbUnPinned.toggled.connect(self.on_tbUnPinned_toggled)
        self.addWidget(self.tbUnPinned)

    def on_tbUnPinned_toggled(self, checked):
        core.config()[self._configName] = not checked
        core.config().flush()

    def paintEvent(self, event):
        """QToolBar.paintEvent reimplementation
        Draws buttons, dock icon and text
        """
        rect = self._spacer.rect()

        painter = QPainter(self)

        transform = QTransform()
        transform.translate(self._spacer.pos().x(), self._spacer.pos().y())
        painter.setTransform(transform)

        """ Not supported currently
        if  self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar :
            transform = QTransform()

            rect.setSize(QSize(rect.height(), rect.width()))
            transform.rotate(-90)
            transform.translate(-rect.width(), 0)

            painter.setTransform(transform)
        """

        # icon / title
        optionB = QStyleOptionButton()
        optionB.initFrom(self._dock)
        optionB.rect = rect
        optionB.text = self._dock.windowTitle()
        optionB.iconSize = self.iconSize()
        optionB.icon = self._dock.windowIcon()

        self.style().drawControl(QStyle.CE_PushButtonLabel, optionB, painter, self._dock)

    def minimumSizeHint(self):
        """QToolBar.minimumSizeHint implementation
        """
        return QToolBar.sizeHint(self)

    def sizeHint(self):
        """QToolBar.sizeHint implementation
        """
        wis = self.iconSize()
        size = QToolBar.sizeHint(self)
        fm = QFontMetrics(self.font())

        if self._dock.features() & QDockWidget.DockWidgetVerticalTitleBar:
            size.setHeight(size.height() + fm.width(self._dock.windowTitle()) + wis.width())
        else:
            size.setWidth(size.width() + fm.width(self._dock.windowTitle()) + wis.width())

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

    closed = pyqtSignal()
    """
    closed()

    **Signal** emitted, when dock is closed
    """

    shown = pyqtSignal()
    """
    shown()

    **Signal** emitted, when dock is shown
    """

    def __init__(self, parentObject, windowTitle, windowIcon=QIcon(), shortcut=None):
        QDockWidget.__init__(self, parentObject)
        self._showAction = None

        self.setObjectName(str(self.__class__))
        self.setWindowTitle(windowTitle)

        if not windowIcon.isNull():
            self.setWindowIcon(windowIcon)
        if shortcut is not None:
            self.showAction().setShortcut(shortcut)

        self._titleBar = _TitleBar(self)
        self.setTitleBarWidget(self._titleBar)

        if shortcut is not None:
            toolTip = "Move focus with <b>%s</b>,<br/>close with <b>Esc</b>" % shortcut
        else:
            toolTip = "Close with <b>Esc</b>"
        self._titleBar.setToolTip(toolTip)

        self._closeShortcut = QShortcut(QKeySequence("Esc"), self)
        self._closeShortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._closeShortcut.activated.connect(self._close)

    def keyPressEvent(self, event):
        """Catch Esc. Not using QShortcut, because dock shall be closed,
        only if child widgets haven't catched Esc event
        """
        if event.key() == Qt.Key_Escape and \
           event.modifiers() == Qt.NoModifier:
            self._hide()
        else:
            QDockWidget.keyPressEvent(self, event)

    def showAction(self):
        """Action shows the widget and set focus on it.

        Add this action to the main menu
        """
        if not self._showAction:
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

    def _close(self):
        """Hide and return focus to MainWindow focus proxy
        """
        self.close()
        if ( self.parent() is not None and
          self.parent().focusProxy() is not None and
          self.hasFocus() ):
            self.parent().focusProxy().setFocus()

    def closeEvent(self, event):
        """Widget was closed"""
        self.closed.emit()

    def show(self):
        QDockWidget.show(self)
        # If floating, then active this window so it will receive keyboard
        # input.
        if self.isFloating():
            self.activateWindow()

    def showEvent(self, event):
        """Widget was shown"""
        self.shown.emit()

    def isPinned(self):
        """True if the widget is pinned; false if unpinned (auto-hide mode)."""
        return not self._titleBar.tbUnPinned.isChecked()
