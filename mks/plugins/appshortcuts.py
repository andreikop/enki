"""
appshortcuts --- Manage application shortcuts
=============================================

Application shortcuts module transparently manages QAction shortcuts.

Here is example of global action creation: ::

    action = core.actionModel().addAction("mSettings/aShortcuts", self.tr( "Shortcuts..."),  QIcon(':/mksicons/shortcuts.png'))

This code adds *Shortcuts...* action to *Edit* menu.

After action has been crated, Application shortcuts module will change its shortcut from default to defined by user 
(if defined).

Module also **loads and saves** shortcuts configuration to file and provides **shortcuts editor dialog**.
"""

import os.path

from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QIcon
from PyQt4.fresh import pActionsShortcutEditor

from mks._3rdparty.configobj import ConfigObj, ParseError

from mks.core.core import core

def tr(s):
    return s

_CONFIG_PATH = os.path.expanduser('~/.mksv3.shortcuts.cfg')

def _recursiveActionsList(model, parentIndex = QModelIndex()):
    """Get recursive list of all model indexes
    """
    for childRow in range(model.rowCount(parentIndex)):
        childIndex = model.index(childRow, 0, parentIndex)
        action = model.action(childIndex)
        if not action.menu():
            yield action
        for action in _recursiveActionsList(model, childIndex):
            yield action


class Plugin:
    """Module implementation
    """
    def __init__(self):
        try:
            self._config = ConfigObj(_CONFIG_PATH)
        except ParseError, ex:
            core.messageManager().appendMessage('Failed to parse configuration file %s\n'
                                                'Error:\n'
                                                '%s\n'
                                                'Fix the file or delete it.' % 
                                                    (_CONFIG_PATH, unicode(str(ex), 'utf_8')))
            self._config = None

        self._model = core.actionModel()
        self._model.rowsInserted.connect(self._onActionInserted)
        
        self._action = self._model.addAction("mSettings/aApplicationShortcuts",
                                       tr( "Application shortcuts..."), 
                                       QIcon(':/mksicons/shortcuts.png'))
        self._action.setStatusTip(tr( "Edit application shortcuts..."))
        self._action.triggered.connect(self._onEditShortcuts)
        
        for action in _recursiveActionsList(self._model):
            self._applyShortcut(action)

    def __term__(self):
        self._model.removeAction(self._action)
    
    def _applyShortcut(self, action):
        """Apply for the action its shortcut if defined
        """
        
        if self._config is not None:
            path = map(str, self._model.path(action).split('/'))
            menuDict = self._config
            for menu in path[:-1]:
                if menu not in menuDict:
                    return
                menuDict = menuDict[menu]
            if not path[-1] in menuDict:
                return
            action.setShortcut(menuDict[path[-1]])

    def _onActionInserted(self, parentIndex, start, end):
        """Handler of action inserted signal. Changes action shortcut from default to configured by user
        """
        for row in range(start, end + 1):
            actionIndex = self._model.index(row, 0, parentIndex)
            action = self._model.action(actionIndex)
            if action is not None and \
               not action.menu():
                self._applyShortcut(action)

    def _saveShortcuts(self):
        """Save shortcuts to configuration file
        """
        if self._config is None:
            return
        for action in _recursiveActionsList(self._model):
            path = map(str, self._model.path(action).split('/'))
            menuDict = self._config
            for menu in path[:-1]:
                if menu not in menuDict:
                    menuDict[menu] = {}
                menuDict = menuDict[menu]
            menuDict[path[-1]] = str(action.shortcut().toString())
        self._config.write()

    def _onEditShortcuts(self):
        """Handler of *Edit->Shortcuts...* action. Shows dialog, than saves shortcuts to file
        """
        pActionsShortcutEditor (self._model, core.mainWindow()).exec_()
        self._saveShortcuts()
