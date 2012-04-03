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
import json

from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QIcon
from mks.fresh.actionmanager.pActionsShortcutEditor import pActionsShortcutEditor

import mks.core.defines

from mks.core.core import core

def tr(text):  # pylint: disable=C0103
    """ Stub for translation procedure
    """
    return text

_CONFIG_PATH = os.path.join(mks.core.defines.CONFIG_DIR, 'shortcuts.json')


class Plugin:
    """Module implementation
    """
    def __init__(self):
        self._config = self._load()

        self._actionManager = core.actionManager()
        
        self._action = self._actionManager.addAction("mSettings/aApplicationShortcuts",
                                       tr( "Application shortcuts..."), 
                                       QIcon(':/mksicons/shortcuts.png'))
        self._action.setStatusTip(tr( "Edit application shortcuts..."))
        self._action.triggered.connect(self._onEditShortcuts)
        
        for action in self._actionManager.allActions():
            if not action.menu():
                self._applyShortcut(action)
        
        self._actionManager.actionInserted.connect(self._onActionInserted)

    def del_(self):
        self._actionManager.removeAction(self._action)

    def _applyShortcut(self, action):
        """Apply for the action its shortcut if defined
        """
        self._actionManager.setDefaultShortcut(action, action.shortcut())

        if self._config is None:  # No file, use default settings
            return
        
        path = self._actionManager.path(action)

        try:
            shortcut = self._config[path]
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
            self._config = {}
        
        for action in self._actionManager.allActions():
            if not action.menu():
                path = self._actionManager.path(action)
                # Remove default values
                if action.shortcut().toString() != self._actionManager.defaultShortcut(action).toString():
                    self._config[path] = action.shortcut().toString()
                else:
                    try:
                        del self._config[path]
                    except KeyError:
                        pass
        self._save()

    def _onEditShortcuts(self):
        """Handler of *Edit->Shortcuts...* action. Shows dialog, than saves shortcuts to file
        """
        pActionsShortcutEditor (self._actionManager, core.mainWindow()).exec_()
        self._saveShortcuts()

    def _load(self):
        """Load the config
        """
        if not os.path.exists(_CONFIG_PATH):
            return None
        
        try:
            with open(_CONFIG_PATH, 'r') as f:
                return json.load(f)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            text = "Failed to load shortcut settings file '%s': %s" % (_CONFIG_PATH, error)
            core.mainWindow().appendMessage(text)
            return None

        
    def _save(self):
        """Save the config
        """
        if self._config:
            try:
                with open(_CONFIG_PATH, 'w') as f:
                    json.dump(self._config, f, sort_keys=True, indent=4)
            except (OSError, IOError), ex:
                error = unicode(str(ex), 'utf8')
                text = "Failed to save shortcut settings file '%s': %s" % (_CONFIG_PATH, error)
                core.mainWindow().appendMessage(text)
        else:  # config is empty, remove the file
            try:
                os.unlink(_CONFIG_PATH)
            except:  # File may be not existing. Even if something is wrong, no reason to notify user now
                pass
