"""The InstallPage"""

import os
import uuid

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QStyle,
                             QVBoxLayout, QLabel, QDialogButtonBox,
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, qWarning
from PyQt5.QtGui import QIcon, QMovie

from enki.core.core import core

from .constants import DOWNLOAD_ICON_PATH, SPINNER_ICON_PATH, TMP
from . import helper, pluginspage


class InstallPage(QWidget):
    """Settings page for the installed plugins"""
    def __init__(self, parent, repo):
        """QWidget Dictionary -> Void
        Consumes the parent and the repository dictionary and sets up the
        install page in the settings area"""
        QWidget.__init__(self, parent)
        self._userPlugins = helper.getPlugins()
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

        self._vbox = QVBoxLayout()
        self._vbox.addStretch(1)
        baseWidget.setLayout(self._vbox)

    def update(self, userPlugins):
        """ListOfUserpluginEntry -> Void
        Consume a list of UserpluginEntry and repopulates the install page"""
        for i in reversed(range(self._vbox.count())):
            try:
                self._vbox.itemAt(i).widget().setParent(None)
            except AttributeError as e:
                qWarning("Can't call setParent of None type")

        self._vbox.addWidget(QLabel(
            """<h2>Install Plugins</h2>"""))
        for entry in self._repo["plugins"]:
            isInstalled = helper.isPluginInstalled(entry["name"], userPlugins)
            if isInstalled:
                self._vbox.addWidget(pluginspage.PluginTitlecard(isInstalled))
            else:
                self._vbox.addWidget(InstallableTitlecard(entry, self))

    def addPluginToUserPlugins(self, installableTitlecard):
        """InstallableTitlecard -> Void
        Consumes an InstallableTitlecard and insert an PluginTitleCard instead
        of itself"""
        index = self._vbox.indexOf(installableTitlecard)
        name = installableTitlecard.modulename()
        pluginEntry = helper.initPlugin(name)

        if pluginEntry:
            self._userPlugins.append(pluginEntry)
            self._vbox.insertWidget(index,
                                    pluginspage.PluginTitlecard(pluginEntry))


class InstallableTitlecard(QGroupBox):
    """An titlecard for the install page in the settings view"""
    def __init__(self, pluginEntry, parent):
        """PluginEntry QWidget -> Void
        Consumes a PluginEntry and the parent widget of the titlecard
        sets up the titlecard to the pluginEntry"""
        super().__init__()
        self.__parent = parent
        self._pluginEntry = pluginEntry
        # Should be set to 150, when there a some kind of info link / button.
        self.setMaximumHeight(300)

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
        """String -> QIcon
        Consumes the iconName for a given standard icon
        returns the corresponding icon on the current platform."""
        return self.style().standardIcon(getattr(QStyle, iconName))

    def _setInstallButtonIcon(self, frame):
        """QFrame -> Void
        Handles everey new frame in the spinner animation"""
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

    def _onInstallButtonClicked(self):
        """Handler for install button"""
        url = self._pluginEntry["download"]
        tmpName = str(uuid.uuid4()) + ".zip"
        self._downloadPath = os.path.join(TMP, tmpName)

        downloadThread = DownloadPluginThread(url, self._downloadPath)
        downloadThread.success.connect(self._onDownloadSuccess)
        downloadThread.failed.connect(self._onDownloadFailed)
        downloadThread.start()

        self._spinner = QMovie(SPINNER_ICON_PATH)
        self._spinner.frameChanged.connect(self._setInstallButtonIcon)
        self._spinner.start()
        self.installButton.setText("Installing...")
        self.installButton.setDisabled(True)

    def _onDownloadSuccess(self):
        """Install plugin if download succeeded"""
        helper.extractPlugin(self._downloadPath)
        # DONE rename folder to name Without version number
        newFolderName = self.modulename()
        oldFolderName = newFolderName + "-" + self._pluginEntry["version"]
        helper.renamePluginFolder(oldFolderName, newFolderName)
        # DONE load plugin
        self.__parent.addPluginToUserPlugins(self)
        self.setParent(None)

    def _onDownloadFailed(self):
        """Cleans up, if the download failed"""
        self.installButton.setIcon(QIcon.fromTheme("run-install",
                                                   QIcon(DOWNLOAD_ICON_PATH)))
        QMessageBox(
            QMessageBox.Warning,
            "Could not install %s plugin."
            % self._pluginEntry["pluginname"],
            """The %s plugin could not be downloaded. Please
            check your internet connection."""
            % self._pluginEntry["pluginname"])

    def modulename(self):
        """Extracts the modulename detail url"""
        return self._pluginEntry["details"].split("/")[-1]


class DownloadPluginThread(QThread):
    """Downloads the plugin in it's own thread."""
    success = pyqtSignal()
    failed = pyqtSignal()

    def __init__(self, url, tmpPath, parent=None):
        """String String -> Void
        Consumes the url to the plugin archive and the path where to download
        the archive"""
        super(DownloadPluginThread, self).__init__(parent)
        self._url = url
        self._tmpPath = tmpPath

    def __del__(self):
        self.wait()

    def run(self):
        """Download the plugin"""
        isDownloadSuccessful = helper.downloadPlugin(self._url, self._tmpPath)
        if isDownloadSuccessful:
            self.success.emit()
        else:
            self.failed.emit()
