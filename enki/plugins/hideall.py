"""
hideall --- Hide all widgets and restore state
==============================================
"""

from PyQt4.QtCore import QObject

from enki.core.core import core
from enki.widgets.dockwidget import DockWidget


class Plugin(QObject):
    """Plugin interface
    """
    def __init__(self):
        QObject.__init__(self)

        core.actionManager().action( "mView/aHideAll" ).triggered.connect(self._onHideAllWindows)
        self._mainWindowState = None

    def del_(self):
        pass

    def _onHideAllWindows(self):
        """Close all visible windows for get as much space on the screen, as possible
        """
        mainWindow = core.mainWindow()
        docks = mainWindow.findChildren(DockWidget)

        if all([dock.isHidden() \
                    for dock in docks]):
            if self._mainWindowState is not None:
                mainWindow.restoreState(self._mainWindowState)
        else:
            self._mainWindowState = mainWindow.saveState()
            mainWindow.hideAllWindows.emit()
            for dock in docks:
                dock.hide()
