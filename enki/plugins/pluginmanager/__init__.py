#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plugin manager --- Enki package manager that makes it simple to find,
                   install and keep packages up-to-date.
================================================================

@author: Marco Laspe <marco@rockiger.com>

Released under the GPL2 license
https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
"""
# DONE Proof of Concept
# TODO Study packagecontrol, atom, kate and vscode
# TODO Think about features and design ui
# DONE Settings page
# TODO Delete a plugin
# TODO Enable a plugin
# TODO Disable plugin
# TODO Cleanup code (Terminate plugin, etc.)
# TODO Make it easy to create your own plugin, 
#      that I can get start with plugin development fast.
# MAYBE checkbox if plugin is activated

import os
import pkgutil
import sys
import importlib
from os.path import expanduser, isdir
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QWidget, QHBoxLayout, QGroupBox, QStyle,
                             QVBoxLayout, QLabel, QDialogButtonBox,
                             QScrollArea, QMessageBox)
from PyQt5.QtGui import QFontMetrics

from enki.core.core import core
from enki.core.defines import CONFIG_DIR
from enki.core.uisettings import CheckableOption

# use userplugins to differentiate from plugins namespace that come with enki
_PLUGIN_DIR_PATH = os.path.join(CONFIG_DIR, 'userplugins')
_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'icon.svg')
print(_ICON_PATH)

# Data Definitions
# ==================
# userpluginEntry consist of
# {'plugin': Module,
#  'isloaded': Bool,
#  'name': String,
#  'author': String,
#  'version': String,
#  'doc': String}
#
# ListOfUserpluginEntry is one of:
# - []
# - lou.append(userpluginEntry)

def create_UE(plugin, isLoaded, name, author, version, doc ):
    """Create a new userpluginEntry"""
    return {'plugin': plugin,
            'isLoaded': isLoaded,
            'name': name,
            'author': author,
            'version': version,
            'doc': doc}

class Plugin:
    """Plugin interface implementation

    Activate, Deactivate and Uninstall plugins in your user directory.
    """
    def __init__(self):
        """Setup settings and activate plugin, if feasable."""
        self._userPlugins = [] # of type ListOfUserpluginEntry
        self._checkPaths()
        self._userPlugins = self._loadPlugins()

        self._checkSettings()
        core.uiSettingsManager().aboutToExecute.connect(
             self._onSettingsDialogAboutToExecute)
        # core.uiSettingsManager().dialogAccepted.connect(
        #     self._onSettingsDialogAccepted)

    def _loadPlugins(self):
        """Loads all userplugins and returns them as a ListOfUserpluginEntry"""
        userPlugins = []
        for loader, name, isPackage in pkgutil.iter_modules([_PLUGIN_DIR_PATH]):
            userPlugins.append(self._loadPlugin(name))
        return userPlugins

    def _loadPlugin(self, name):
        """Load plugin by it's module name
        """
        module = importlib.import_module('userplugins.%s' % name)
        core.loadedPlugins().append(module.Plugin()) # TODO check if plugin is activated by user
        return create_UE(
            module,
            False,
            module.__pluginname__,
            module.__author__,
            module.__version__,
            module.__doc__
        )

    def _checkPaths(self):
        """Checks if all neccessary paths a present and if not
        creates them
        """
        initPath = os.path.join(_PLUGIN_DIR_PATH,"__init__.py")
        if not os.path.isdir(_PLUGIN_DIR_PATH):
            os.makedirs(_PLUGIN_DIR_PATH)
            # create __init__.py in userplugins im neccessary
        if not os.path.exists(initPath):
            open(initPath, 'a').close()
        sys.path.append(CONFIG_DIR)

    def terminate(self):
        """clean up"""
        core.uiSettingsManager().aboutToExecute.disconnect(
             self._onSettingsDialogAboutToExecute)

    def _activate(self):
        """Create the dialog, add actions to the main menu."""
        self._fileswitcher = Fileswitcher(core.mainWindow())
        self._addActions()
        core.workspace().documentOpened.connect(self._onDocumentOpenedOrClosed)
        core.workspace().documentClosed.connect(self._onDocumentOpenedOrClosed)

    def _deactivate(self):
        """Destroy the dialog, remove actions from the main menu."""
        self._fileswitcher = None
        self._removeActions()
        core.workspace().documentOpened.disconnect(
            self._onDocumentOpenedOrClosed)
        core.workspace().documentClosed.disconnect(
            self._onDocumentOpenedOrClosed)

    def _addActions(self):
        """Add actions to main menu"""
        pass

    def _removeActions(self):
        """Remove actions from mein menu"""
        pass

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        """
        pluginsPage = PluginsPage(dialog, self._userPlugins)
        dialog.appendPage(u"Plugins", pluginsPage,
            QIcon.fromTheme("preferences-plugin", QIcon(_ICON_PATH)))

    def _onSettingsDialogAccepted(self):
        pass

    def _checkSettings(self):
        """Check if settings are present in the core configuration file,
        else create them.
        """
        if "PluginManager" not in core.config():
            core.config()["PluginManager"] = {}


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
            """<h2>Installed Plugins</h2>
            <p>Add plugins by putting them into <code>%s</code></p>
            <p><\p>""" % _PLUGIN_DIR_PATH))
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
            self.style().standardIcon(getattr(QStyle,'SP_TrashIcon'))
        )
        uninstallButton.clicked.connect(self._onUninstallButtonClicked)

        hbox.addWidget(button_box)
        bottom.setLayout(hbox)
        bottom.setContentsMargins(0,0,0,0)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("""
            <h2>%s <small>%s</small></h2>
            <p>%s</p>
            <p></p>""" %
            (pluginEntry["name"], pluginEntry["version"], pluginEntry["doc"])))
        vbox.addWidget(bottom)

        self.setLayout(vbox)

    def _onUninstallButtonClicked(self):
        msgBox = QMessageBox(QMessageBox.Warning,
            "Uninstall erases the %s plugin permanently from your disk." % \
                self._pluginEntry["name"],
            """Do you really want to delete the %s plugin from your disk.
            have to reinstall it, if you want to use it again.""" % \
                self._pluginEntry["name"]
        )
        okButton = msgBox.addButton("Uninstall", QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton("Cancel", QMessageBox.RejectRole)
        cancelButton.setIcon(self._standardIconFromStyle('SP_DialogCancelButton'))
        msgBox.setDefaultButton(cancelButton)
        if msgBox.exec() == 0:
            self.setParent(None)
            # Terminate plugin
            # delete plugin from disk

    def _standardIconFromStyle(self, iconName):
        return self.style().standardIcon(getattr(QStyle, iconName))

    def _onStartStopButtonClicked(self):
        self._pluginEntry['isLoaded'] = False \
            if self._pluginEntry['isLoaded'] is True else True
        self._setStartStopButton()

    def _setStartStopButton(self):
        if self._pluginEntry['isLoaded'] is True:
            self.startStopButton.setText("Disable")
            self.startStopButton.setIcon(self.style().standardIcon(getattr(QStyle,'SP_MediaPause')))
            self.startStopButton.setDown(True)
            # Terminate plugin
        else:
            self.startStopButton.setText("Enable")
            self.startStopButton.setIcon(self.style().standardIcon(getattr(QStyle,'SP_MediaPlay')))
            self.startStopButton.setDown(False)
            # load plugin
