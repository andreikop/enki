"""The PluginsPage class"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QStyle,
                             QVBoxLayout, QLabel, QDialogButtonBox,
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from enki.core.core import core
from .constants import PLUGIN_DIR_PATH, DOWNLOAD_ICON_PATH
from .helper import loadPlugin, unloadPlugin, deletePlugin, isPluginInstalled
from .pluginspage import PluginTitlecard


class InstallPage(QWidget):
    """Settings page for the installed plugins"""
    def __init__(self, parent, userPlugins, repo):
        QWidget.__init__(self, parent)
        self._userPlugins = userPlugins
        self._repo = repo

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

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(
            """<h2>Install Plugins</h2>"""))
        for entry in repo["plugins"]:
            isInstalled = isPluginInstalled(entry["name"], self._userPlugins)
            if isInstalled:
                vbox.addWidget(PluginTitlecard(isInstalled))
            else:
                vbox.addWidget(InstallableTitlecard(entry))
        vbox.addStretch(1)
        baseWidget.setLayout(vbox)


class InstallableTitlecard(QGroupBox):
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

        self.installButton = button_box.addButton(
            'Install', QDialogButtonBox.DestructiveRole
        )
        self.installButton.setCheckable(True)
        self.installButton.clicked.connect(self._onInstallButtonClicked)
        self.installButton.setIcon(QIcon.fromTheme("download",
                                                   QIcon(DOWNLOAD_ICON_PATH)))

        hbox.addWidget(button_box)
        bottom.setLayout(hbox)
        bottom.setContentsMargins(0, 0, 0, 0)

        pluginInfoLabel = QLabel(
            """
            <h2>%s <small>%s</small></h2>
            <p>%s</p>
            <p></p>"""
            % (pluginEntry["name"],
               pluginEntry["version"],
               pluginEntry["description"]))
        pluginInfoLabel.setWordWrap(True)
        vbox = QVBoxLayout()
        vbox.addWidget(pluginInfoLabel)
        vbox.addWidget(bottom)

        self.setLayout(vbox)


    def _standardIconFromStyle(self, iconName):
        return self.style().standardIcon(getattr(QStyle, iconName))

    def _onInstallButtonClicked(self):
        print("Install Plugin")

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
