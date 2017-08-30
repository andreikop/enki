"""
repl --- MIT Scheme and Standard ML REPL
========================================

File contains plugin functionality implementation
"""

import os
import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5 import uic
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.client import QtKernelClient
from qtconsole.manager import QtKernelManager

from enki.core.core import core
from enki.widgets.dockwidget import DockWidget

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

        # Copied from https://github.com/jupyter/qtconsole/blob/master/examples/inprocess_qtconsole.py, then modified based on https://github.com/jupyter/qtconsole/blob/master/qtconsole/qtconsoleapp.py -- the QtInProcessKernelManager is blocking, so infinite loops crash Enki!
        kernel_manager = QtKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.client_factory = QtKernelClient
        kernel_manager.kernel.gui = 'qt'

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        self.ipython_widget = RichJupyterWidget()
        self.ipython_widget.kernel_manager = kernel_manager
        self.ipython_widget.kernel_client = kernel_client
        # By default, iPython adds a blank line between inputs. Per Monika's request, this eliminates the extra line. See https://qtconsole.readthedocs.io/en/latest/config_options.html#options; this fix was based on info from https://stackoverflow.com/questions/38652671/ipython-5-0-remove-spaces-between-input-lines.
        self.ipython_widget.input_sep = ''
        self.ipython_widget.show()

        self.setWidget(self.ipython_widget)
        self.setFocusProxy(self.ipython_widget)

