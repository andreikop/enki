"""The PluginsPage class"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QStyle,
                             QVBoxLayout, QLabel, QDialogButtonBox,
                             QScrollArea, QMessageBox)
from enki.core.core import core
from .constants import PLUGIN_DIR_PATH
from .helper import loadPlugin, unloadPlugin, deletePlugin


class PluginsPage(QWidget):
    """Settings page for the installed plugins"""
    def __init__(self, parent, userPlugins):
        QWidget.__init__(self, parent)
        self._userPlugins = userPlugins

        # Add a scrollArea that if they are more plugins that fit into the
        # settings page
        scrollArea = QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        baseLayout = QVBoxLayout()
        self.setLayout(baseLayout)
        baseWidget = QWidget()
        scrollArea.setWidget(baseWidget)
        baseLayout.addWidget(scrollArea)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(
            """<h2>Installed Plugins: <code>%i</code></h2>
            <p>Add plugins by putting them into <code>%s</code></p>
            <p><\p>""" % (len(userPlugins), PLUGIN_DIR_PATH)))
        for entry in userPlugins:
            vbox.addWidget(PluginTitlecard(entry))
        vbox.addStretch(1)
        baseWidget.setLayout(vbox)


class PluginTitlecard(QGroupBox):
    def __init__(self, pluginEntry):
        super().__init__()
        self._pluginEntry = pluginEntry
        self.setMaximumHeight(150)

        bottom = QWidget()
        hbox = QHBoxLayout()
        bottom_label = QLabel(pluginEntry["author"])
        bottom_label.setMargin(0)
        bottom_label.setIndent(0)
        hbox.addWidget(bottom_label)
        button_box = QDialogButtonBox(self)

        self.startStopButton = button_box.addButton(
            'Enable', QDialogButtonBox.DestructiveRole
        )
        self.startStopButton.setCheckable(True)
        self._setStartStopButton()
        self.startStopButton.clicked.connect(self._onStartStopButtonClicked)

        uninstallButton = button_box.addButton(
            'Uninstall', QDialogButtonBox.ActionRole
        )
        uninstallButton.setIcon(
            self.style().standardIcon(getattr(QStyle, 'SP_TrashIcon'))
        )
        uninstallButton.clicked.connect(self._onUninstallButtonClicked)

        hbox.addWidget(button_box)
        bottom.setLayout(hbox)
        bottom.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(
            """
            <h2>%s <small>%s</small></h2>
            <p>%s</p>
            <p></p>"""
            % (pluginEntry["pluginname"],
               pluginEntry["version"],
               pluginEntry["doc"])))
        vbox.addWidget(bottom)

        self.setLayout(vbox)

    def _onUninstallButtonClicked(self):
        msgBox = QMessageBox(
            QMessageBox.Warning,
            "Uninstall erases the %s plugin permanently from your disk."
            % self._pluginEntry["pluginname"],
            """Do you really want to delete the %s plugin from your disk.
            have to reinstall it, if you want to use it again."""
            % self._pluginEntry["pluginname"])
        msgBox.addButton("Uninstall", QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton("Cancel", QMessageBox.RejectRole)
        cancelButton.setIcon(
            self._standardIconFromStyle('SP_DialogCancelButton'))
        msgBox.setDefaultButton(cancelButton)
        if msgBox.exec() == 0:
            self.setParent(None)
            self._pluginEntry['isLoaded'] = False
            name = self._pluginEntry['modulename']
            core.config()["PluginManager"]["Plugins"][name]["Enabled"] = False
            deletePlugin(self._pluginEntry)

    def _standardIconFromStyle(self, iconName):
        return self.style().standardIcon(getattr(QStyle, iconName))

    def _onStartStopButtonClicked(self):
        name = self._pluginEntry['modulename']
        if self._pluginEntry['isLoaded'] is True:
            self._pluginEntry['isLoaded'] = False
            core.config()["PluginManager"]["Plugins"][name]["Enabled"] = False
            unloadPlugin(self._pluginEntry)
        else:
            self._pluginEntry['isLoaded'] = True
            core.config()["PluginManager"]["Plugins"][name]["Enabled"] = True
            loadPlugin(self._pluginEntry)
        self._setStartStopButton()

    def _setStartStopButton(self):
        if self._pluginEntry['isLoaded'] is True:
            self.startStopButton.setText("Disable")
            self.startStopButton.setIcon(self.style().standardIcon(
                getattr(QStyle, 'SP_MediaPause')))
            self.startStopButton.setDown(True)
        else:
            self.startStopButton.setText("Enable")
            self.startStopButton.setIcon(self.style().standardIcon(
                getattr(QStyle, 'SP_MediaPlay')))
            self.startStopButton.setDown(False)
