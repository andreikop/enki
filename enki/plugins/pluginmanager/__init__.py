#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plugin manager --- Enki package manager that makes it simple to find,
                   install and keep packages up-to-date.
=====================================================================

Released under the GPL3 license
https://www.gnu.org/licenses/old-licenses/gpl-3.0.en.html
"""
__author__ = "Marco Laspe"
__pluginname__ = "Plugin Manager"
__copyright__ = "Copyright 2017"
__credits__ = ["Marco Laspe", "Andrei Kopats",
               "Filipe Azevedo", "Bryan A. Jones"]
__license__ = "GPL3"
__version__ = "0.0.1"
__maintainer__ = "Marco Laspe"
__email__ = "marco@rockiger.com"
__status__ = "Beta"

import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import qDebug, QThread, pyqtSignal

from enki.core.core import core
from enki.core.defines import CONFIG_DIR

from .constants import PLUGIN_DIR_PATH, PLUGINS_ICON_PATH, INSTALL_ICON_PATH
from . import helper, constants
from .pluginspage import PluginsPage
from .installpage import InstallPage


class Plugin:
    """Plugin interface implementation

    Activate, Deactivate and Uninstall plugins in your user directory.
    """
    def __init__(self):
        """Setup settings and activate plugin, if feasable."""
        self._checkPaths()
        self._checkSettings()
        self._repo = constants.EMPTY_REPO
        helper.initPlugins()

        core.uiSettingsManager().aboutToExecute.connect(
            self._onSettingsDialogAboutToExecute)

        getRepoThread = GetRepoThread()
        getRepoThread.success.connect(self._onSuccessGetRepo)
        getRepoThread.start()

    def terminate(self):
        """clean up"""
        core.uiSettingsManager().aboutToExecute.disconnect(
            self._onSettingsDialogAboutToExecute)

    def _checkPaths(self):
        """Checks if all neccessary paths are present and if not
        creates them
        """
        initPath = os.path.join(PLUGIN_DIR_PATH, "__init__.py")
        if not os.path.isdir(PLUGIN_DIR_PATH):
            os.makedirs(PLUGIN_DIR_PATH)
            # create __init__.py in userplugins im neccessary
        if not os.path.exists(initPath):
            open(initPath, 'a').close()
        sys.path.append(CONFIG_DIR)

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        """
        self._pluginsPage = PluginsPage(dialog)
        self._installPage = InstallPage(dialog, self._repo)
        dialog.appendPage(
            u"Plugins",
            self._pluginsPage,
            QIcon.fromTheme("preferences-plugin", QIcon(PLUGINS_ICON_PATH)))
        dialog.appendPage(
            u"Install",
            self._installPage,
            QIcon.fromTheme("document-new", QIcon(INSTALL_ICON_PATH)))

        self._twMenu = dialog.twMenu
        self._twMenu.itemSelectionChanged.connect(self._onItemSelectionChanged)

    def _onItemActivated(self, item, column):
        qDebug(item)

    def _onItemSelectionChanged(self):
        itemText = self._twMenu.selectedItems()[0].text(0)
        if itemText == "Plugins":
            qDebug("update pluginspage")
            self._pluginsPage.update(helper.getPlugins())
        elif itemText == "Install":
            qDebug("update installpage")
            self._installPage.update(helper.getPlugins())

    def _onSettingsDialogAccepted(self):
        pass

    def _checkSettings(self):
        """Check if settings are present in the core configuration file,
        else create them.
        """
        if "PluginManager" not in core.config():
            core.config()["PluginManager"] = {}
        if "Plugins" not in core.config()["PluginManager"]:
            core.config()["PluginManager"]["Plugins"] = {}

    def _onSuccessGetRepo(self, repo):
        self._repo = repo


class GetRepoThread(QThread):
    """Download the pluginrepository in its own thread?"""

    success = pyqtSignal(dict)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        repo = helper.getRepo()
        self.success.emit(repo)
