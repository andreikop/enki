"""The PluginsPage class"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QStyle,
                             QVBoxLayout, QLabel, QDialogButtonBox,
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, qWarning
from enki.core.core import core
from .constants import PLUGIN_DIR_PATH
from .helper import loadPlugin, unloadPlugin, deletePlugin


class PluginsPage(QWidget):
    """Settings page for the installed plugins"""
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        # Add a scrollArea that if they are more plugins that fit into the
        # settings page
        scrollArea = QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        baseLayout = QVBoxLayout()
        self.setLayout(baseLayout)
        baseWidget = QWidget()
        scrollArea.setWidget(baseWidget)
        baseLayout.addWidget(scrollArea)

        self._vbox = QVBoxLayout()
        baseWidget.setLayout(self._vbox)

    def update(self, userPlugins):
        """ListOfUserpluginEntry -> Void
        Consume a list of UserpluginEntry and repopulates the plugins page"""
        for i in reversed(range(self._vbox.count())):
            try:
                self._vbox.itemAt(i).widget().setParent(None)
            except AttributeError as e:
                qWarning("Can't call setParent of None type")

        self._vbox.addWidget(QLabel(
            """<h2>Installed Plugins: <code>%i</code></h2>
            <p>Add plugins by putting them into <code>%s</code></p>
            <p></p>""" % (len(userPlugins), PLUGIN_DIR_PATH)))
        for entry in userPlugins:
            self._vbox.addWidget(PluginTitlecard(entry))

        self._vbox.addStretch(1)


class PluginTitlecard(QGroupBox):
    def __init__(self, pluginEntry):
        super().__init__()
        self._pluginEntry = pluginEntry
        # Should be set to 150, when there a some kind of info link / button.
        self.setMaximumHeight(300)

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

        pluginInfoLabel = QLabel(
            """
            <h2>%s <small>%s</small></h2>
            <p>%s</p>
            <p></p>"""
            % (pluginEntry["pluginname"],
               pluginEntry["version"],
               pluginEntry["doc"]))
        pluginInfoLabel.setWordWrap(True)
        vbox = QVBoxLayout()
        vbox.addWidget(pluginInfoLabel)
        vbox.addWidget(bottom)

        self.setLayout(vbox)

    def _onUninstallButtonClicked(self):
        msgBox = QMessageBox(
            QMessageBox.Warning,
            "Uninstall erases the %s plugin permanently from your disk."
            % self._pluginEntry["pluginname"],
            """Do you really want to delete the %s plugin from your disk.
            You have to reinstall it, if you want to use it again."""
            % self._pluginEntry["pluginname"])
        msgBox.addButton("Uninstall", QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton("Cancel", QMessageBox.RejectRole)
        cancelButton.setIcon(
            self._standardIconFromStyle('SP_DialogCancelButton'))
        msgBox.setDefaultButton(cancelButton)
        if msgBox.exec() == 0:
            self._uninstallPlugin()

    def _uninstallPlugin(self):
        """Uninstall the the plugin connected to the titlecard"""
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
            self._disablePluginInConfig(name)
            unloadPlugin(self._pluginEntry)
        else:
            self._pluginEntry['isLoaded'] = True
            self._enablePluginInConfig(name)
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

    def _enablePluginInConfig(self, name):
        """String -> Bool
        Consumes the name of a plugin and enables it in the config"""
        return self._togglePluginInConfig(name, True)

    def _disablePluginInConfig(self, name):
        """String -> Bool
        Consumes the name of a plugin and disables it in the config"""
        return self._togglePluginInConfig(name, False)

    def _togglePluginInConfig(self, name, state):
        """String Bool -> Bool
        Consumes a name of a plugin and a state, sets the setting to state.
        If no setting is available for the plugin, it gets created.
        Returns the setting (Bool)
        """
        if name not in core.config()["PluginManager"]["Plugins"]:
            core.config()["PluginManager"]["Plugins"][name] = {}
        core.config()["PluginManager"]["Plugins"][name]["Enabled"] = state
        return core.config()["PluginManager"]["Plugins"][name]["Enabled"]
