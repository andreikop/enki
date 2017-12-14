"""The PluginsPage class"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QStyle,
                             QVBoxLayout, QLabel, QDialogButtonBox,
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QFile, QUrl, QIODevice
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager

from enki.core.core import core

from .constants import (PLUGIN_DIR_PATH, DOWNLOAD_ICON_PATH, SPINNER_ICON_PATH,
                        TMP)
from . import helper, pluginspage


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
            isInstalled = helper.isPluginInstalled(entry["name"], self._userPlugins)
            if isInstalled:
                vbox.addWidget(pluginspage.PluginTitlecard(isInstalled))
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
        self._networkManager = QNetworkAccessManager()
        self._networkManager.finished.connect(self._onDownloadFinished)

        bottom = QWidget()
        hbox = QHBoxLayout()
        bottom_label = QLabel(pluginEntry["author"])
        bottom_label.setMargin(0)
        bottom_label.setIndent(0)
        hbox.addWidget(bottom_label)

        moreInfoLabel = QLabel("<a href='%s'>Details</a>"
                               % pluginEntry["details"])
        moreInfoLabel.setOpenExternalLinks(True)
        hbox.addWidget(moreInfoLabel)

        button_box = QDialogButtonBox(self)
        self.installButton = button_box.addButton(
            'Install', QDialogButtonBox.DestructiveRole
        )
        self.installButton.setCheckable(True)
        self.installButton.clicked.connect(self._onInstallButtonClicked)
        self.installButton.setIcon(QIcon.fromTheme("run-install",
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

    def _setInstallButtonIcon(self, frame):
        self.installButton.setIcon(QIcon(self._spinner.currentPixmap()))

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

    def _onDownloadFinished(self, reply):
        if reply.error():
            print("Failed to download")
        else:
            zipFile = QFile("/tmp/enkiplugin_zipfile.zip")
            zipFile.open(QIODevice.WriteOnly)
            zipFile.write(reply.readAll())
            zipFile.close()
            print("Download Succes")
            # DONE unzip file to userPlugins
            # DONE rename folder to name Without version number
        reply.deleteLater()

    def _onInstallButtonClicked(self):
        print("Install Plugin")
        self._spinner = QMovie(SPINNER_ICON_PATH)
        self._spinner.frameChanged.connect(self._setInstallButtonIcon)
        self._spinner.start()
        self.installButton.setText("Installing...")
        self.installButton.setDisabled(True)

        url = self._pluginEntry["download"]
        print(url)
        downloadPath = helper.downloadPlugin(url)
        if downloadPath:
            self._onDownloadSuccess(downloadPath)
        else:
            self._onDownloadFailed()

    def _onDownloadSuccess(self, downloadPath):
        helper.extractPlugin(downloadPath)
        # DONE rename folder to name Without version number
        newFolderName = self._pluginEntry["details"].split("/")[-1]
        oldFolderName = newFolderName + "-" + self._pluginEntry["version"]
        helper.renamePluginFolder(oldFolderName, newFolderName)
        # TODO load plugin
        pass

    def _onDownloadFailed(self):
        # TODO Change button back to install icon
        # TODO message that download failed
        pass
