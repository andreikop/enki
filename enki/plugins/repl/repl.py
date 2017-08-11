"""
repl --- MIT Scheme and Standard ML REPL
========================================

File contains plugin functionality implementation
"""

import os
import os.path

from PyQt5.QtCore import pyqtSignal, QObject, Qt, QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt5.QtGui import QFont
from PyQt5 import uic
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

from enki.core.core import core

from enki.widgets.dockwidget import DockWidget

import enki.lib.buffpopen
import enki.widgets.termwidget

#
# Integration with the core
#


class SettingsWidget(QWidget):
    """Settings widget. Insertted as a page to UISettings
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        self.pbInterpreterPath.clicked.connect(self._onPbInterpreterPathClicked)

    def _onPbInterpreterPathClicked(self):
        path, _ = QFileDialog.getOpenFileName(core.mainWindow(), 'Interpreter path')
        if path:
            self.leInterpreterPath.setText(path)


class ReplDock(DockWidget):
    """Dock widget with terminal emulator
    """

    def __init__(self, title, icon):
        DockWidget.__init__(self, core.mainWindow(), title, icon, "Alt+I")
        self.setObjectName(title)

        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Copied from https://github.com/jupyter/qtconsole/blob/master/examples/inprocess_qtconsole.py.
        # Create an in-process kernel
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel = kernel_manager.kernel
        kernel.gui = 'qt'

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        self.ipython_widget = RichJupyterWidget()
        self.ipython_widget.kernel_manager = kernel_manager
        self.ipython_widget.kernel_client = kernel_client
        self.ipython_widget.show()

        self.setWidget(self.ipython_widget)
        self.setFocusProxy(self.ipython_widget)

