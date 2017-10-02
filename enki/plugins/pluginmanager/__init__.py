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
# DOING Study packagecontrol, atom, kate and vscode
# DOING Think about features and design ui
# DONE Settings page
# DONE Enable a plugin
# DONE Disable plugin
# TODO Delete a plugin
# TODO Cleanup code (Terminate plugin, etc.)
# TODO Create tests
# TODO Make it easy to create your own plugin,
#      that I can get start with plugin development fast.
# MAYBE checkbox if plugin is activated

import os
import pkgutil
import sys
import importlib
import shutil
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
# {'module': Module
#  'plugin': Plugin or None,
#  'isloaded': Bool,
#  'name': String,
#  'author': String,
#  'version': String,
#  'doc': String}
#
# ListOfUserpluginEntry is one of:
# - []
# - lou.append(userpluginEntry)

def create_UE(module, isLoaded, modulename, pluginname,
    author, version, doc, plugin=None):
    """Create a new userpluginEntry"""
    return {'module': module,
            'plugin': plugin,
            'isLoaded': isLoaded,
            'modulename': modulename,
            'pluginname': pluginname,
            'author': author,
            'version': version,
            'doc': doc}

def loadPlugin(pluginEntry):
    """Load the plugin into core._loadedPlugins, based on it's 'isLoaded'
    return pluginEntry
    """
    if pluginEntry['isLoaded'] == True:
        pluginEntry['plugin'] = pluginEntry['module'].Plugin()
        core.loadedPlugins().append(pluginEntry['plugin'])
    return pluginEntry

def unloadPlugin(pluginEntry):
    """Load the plugin into core._loadedPlugins, based on it's 'isLoaded'
    return pluginEntry
    """
    if pluginEntry['isLoaded'] == False:
        pluginEntry['plugin'].terminate()
        idx = core.loadedPlugins().index(pluginEntry['plugin'])
        core.loadedPlugins().pop(idx)
        pluginEntry['plugin'] = None
    return pluginEntry

def deletePlugin(pluginEntry):
    """Delete the plugin directory or file"""
    pass #shutil.rmtree(os.path.join())

class Plugin:
    """Plugin interface implementation

    Activate, Deactivate and Uninstall plugins in your user directory.
    """
    def __init__(self):
        """Setup settings and activate plugin, if feasable."""
        self._userPlugins = [] # of type ListOfUserpluginEntry
        self._checkPaths()
        self._checkSettings()

        self._userPlugins = self._initPlugins()

        self._checkSettings()
        core.uiSettingsManager().aboutToExecute.connect(
             self._onSettingsDialogAboutToExecute)
        # core.uiSettingsManager().dialogAccepted.connect(
        #     self._onSettingsDialogAccepted)

    def _initPlugins(self):
        """Loads all userplugins and returns them as a ListOfUserpluginEntry"""
        userPlugins = []
        for loader, name, isPackage in pkgutil.iter_modules([_PLUGIN_DIR_PATH]):
            userPlugins.append(self._initPlugin(name))
        return userPlugins

    def _initPlugin(self, name):
        """Load plugin by it's module name
        returns userpluginEntry
        """
        module = importlib.import_module('userplugins.%s' % name)
        pluginEntry = create_UE(
            module,
            self._shouldPluginLoad(name),
            name,
            module.__pluginname__,
            module.__author__,
            module.__version__,
            module.__doc__
        )
        print(module.__file__)
        loadPlugin(pluginEntry)
        return pluginEntry

    def _shouldPluginLoad(self, name):
        """Consumes a name of a plugin and checks in the settings if it should be loaded.
           If no setting is available for the plugin, it gets created.
           Returns the setting (Bool)
        """
        if name not in core.config()["PluginManager"]:
            core.config()["PluginManager"][name] = {}
        if "Enabled" not in core.config()["PluginManager"][name]:
            core.config()["PluginManager"][name]["Enabled"] = False
        return core.config()["PluginManager"][name]["Enabled"]


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
        if "Plugins" not in core.config()["PluginManager"]:
            core.config()["PluginManager"]["Plugins"] = {}


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
            (pluginEntry["pluginname"], pluginEntry["version"],
             pluginEntry["doc"])))
        vbox.addWidget(bottom)

        self.setLayout(vbox)

    def _onUninstallButtonClicked(self):
        msgBox = QMessageBox(QMessageBox.Warning,
            "Uninstall erases the %s plugin permanently from your disk." % \
                self._pluginEntry["pluginname"],
            """Do you really want to delete the %s plugin from your disk.
            have to reinstall it, if you want to use it again.""" % \
                self._pluginEntry["pluginname"]
        )
        okButton = msgBox.addButton("Uninstall", QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton("Cancel", QMessageBox.RejectRole)
        cancelButton.setIcon(self._standardIconFromStyle('SP_DialogCancelButton'))
        msgBox.setDefaultButton(cancelButton)
        if msgBox.exec() == 0:
            self.setParent(None)
            unloadPlugin(self._pluginEntry)
            deletePlugin(self._pluginEntry)

    def _standardIconFromStyle(self, iconName):
        return self.style().standardIcon(getattr(QStyle, iconName))

    def _onStartStopButtonClicked(self):
        name = self._pluginEntry['modulename']
        if self._pluginEntry['isLoaded'] is True:
            self._pluginEntry['isLoaded'] = False
            core.config()["PluginManager"][name]["Enabled"] = False
            unloadPlugin(self._pluginEntry)
        else:
            self._pluginEntry['isLoaded'] = True
            core.config()["PluginManager"][name]["Enabled"] = True
            loadPlugin(self._pluginEntry)
        self._setStartStopButton()
        print(core.loadedPlugins())

    def _setStartStopButton(self):
        if self._pluginEntry['isLoaded'] is True:
            self.startStopButton.setText("Disable")
            self.startStopButton.setIcon(self.style().standardIcon(getattr(QStyle,'SP_MediaPause')))
            self.startStopButton.setDown(True)
        else:
            self.startStopButton.setText("Enable")
            self.startStopButton.setIcon(self.style().standardIcon(getattr(QStyle,'SP_MediaPlay')))
            self.startStopButton.setDown(False)
