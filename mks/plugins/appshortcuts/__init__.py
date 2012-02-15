"""
appshortcuts --- Manage application shortcuts
=============================================

Application shortcuts module transparently manages QAction shortcuts.

Here is example of global action creation: ::

    action = core.actionManager().addAction("mSettings/aShortcuts",
                                          self.tr( "Shortcuts..."),
                                          QIcon(':/mksicons/shortcuts.png'))

This code adds *Shortcuts...* action to *Edit* menu.

After action has been crated, Application shortcuts module will change its shortcut from default to defined by user 
(if defined).

Module also **loads and saves** shortcuts configuration to file and provides **shortcuts editor dialog**.
"""

import os.path

from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QIcon
from mks.fresh.actionmanager.pActionsShortcutEditor import pActionsShortcutEditor

import mks.core.defines
from mks.core.config import Config

from mks.core.core import core

def tr(text):  # pylint: disable=C0103
    """ Stub for translation procedure
    """
    return text

_CONFIG_PATH = os.path.join(mks.core.defines.CONFIG_DIR, 'shortcuts.cfg')

def _recursiveActionsList(model, parentAction = None):
    """Get recursive list of all model indexes
    """
    for action in model.children(parentAction):
        if not action.menu():
            yield action
        for action in _recursiveActionsList(model, action):
            yield action


class Plugin:
    """Module implementation
    """
    def __init__(self):
        try:
            self._config = Config(True, _CONFIG_PATH)
        except UserWarning as ex:
            core.messageToolBar().appendMessage(unicode(ex))
            self._config = None
            return

        self._actionManager = core.actionManager()
        self._actionManager.actionInserted.connect(self._onActionInserted)
        
        self._action = self._actionManager.addAction("mSettings/aApplicationShortcuts",
                                       tr( "Application shortcuts..."), 
                                       QIcon(':/mksicons/shortcuts.png'))
        self._action.setStatusTip(tr( "Edit application shortcuts..."))
        self._action.triggered.connect(self._onEditShortcuts)
        
        for action in _recursiveActionsList(self._actionManager):
            self._applyShortcut(action)

    def __del__(self):
        self._actionManager.removeAction(self._action)
    
    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return None  # No any settings

    def _applyShortcut(self, action):
        """Apply for the action its shortcut if defined
        """
        self._actionManager.setDefaultShortcut(action, action.shortcut())
        path = self._actionManager.path(action)

        try:
            shortcut = self._config.get(path)
        except KeyError:
            return

        action.setShortcut(shortcut)

    def _onActionInserted(self, action):
        """Handler of action inserted signal. Changes action shortcut from default to configured by user
        """
        if not action.menu():
            self._applyShortcut(action)

    def _saveShortcuts(self):
        """Save shortcuts to configuration file
        """
        if self._config is None:
            return
        for action in _recursiveActionsList(self._actionManager):
            path = self._actionManager.path(action)
            self._config.set(path, action.shortcut().toString())
        try:
            self._config.flush()
        except UserWarning as ex:
            core.messageToolBar().appendMessage(unicode(ex))

    def _onEditShortcuts(self):
        """Handler of *Edit->Shortcuts...* action. Shows dialog, than saves shortcuts to file
        """
        pActionsShortcutEditor (self._actionManager, core.mainWindow()).exec_()
        self._saveShortcuts()
