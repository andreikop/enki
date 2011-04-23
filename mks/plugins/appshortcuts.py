"""
appshortcuts --- Manage application shortcuts
=============================================

Application shortcuts module transparently manages QAction shortcuts.

Here is example of global action creation: ::

    action = core.menuBar().addAction("mEdit/aShortcuts", self.tr( "Shortcuts..."),  QIcon(':/mksicons/shortcuts.png'))

This code adds *Shortcuts...* action to *Edit* menu.

After action has been crated, Application shortcuts module will change its shortcut from default to defined by user 
(if defined).

Module also **loads and saves** shortcuts configuration to file and provides **shortcuts editor dialog**.
"""

import os.path

from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QIcon
from PyQt4.fresh import pActionsNodeShortcutEditor

from mks._3rdparty.configobj import ConfigObj, ParseError

from mks.core.core import core

_CONFIG_PATH = os.path.expanduser('~/.mksv3.shortcuts.cfg')

def _recursiveIndexesList(model, parentIndex = QModelIndex()):
    """Get recursive list of all model indexes
    """
    for childRow in range(model.rowCount(parentIndex)):
        childIndex = model.index(childRow, 0, parentIndex)
        yield model.indexToNode(childIndex)
        for index in _recursiveIndexesList(model, childIndex):
            yield index


class AppShortcuts:
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

        mbar = core.menuBar()
        self._model = mbar.model()
        self._model.rowsInserted.connect(self._onActionInserted)
        
        action = mbar.addAction("mEdit/aShortcuts", mbar.tr( "Shortcuts..."),  QIcon(':/mksicons/shortcuts.png'))
        action.setStatusTip(mbar.tr( "Edit application shortcuts..."))
        action.triggered.connect(self._onEditShortcuts)
        
        for actionNode in _recursiveIndexesList(self._model):
            if actionNode.action():
                self._applyShortcut(actionNode)

    def _applyShortcut(self, actionNode):
        """Apply for the action node its shortcut if defined
        """
        if self._config is not None:
            path = map(str, actionNode.path().split('/'))
            menuDict = self._config
            for menu in path[:-1]:
                if menu not in menuDict:
                    return
                menuDict = menuDict[menu]
            actionNode.setShortcut(menuDict[path[-1]])

    def _onActionInserted(self, parentIndex, start, end):
        """Handler of action inserted signal. Changes action shortcut from default to configured by user
        """
        for row in range(start, end + 1):
            actionIndex = self._model.index(row, 0, parentIndex)
            actionNode = self._model.indexToNode(actionIndex)
            if actionNode.action():
                self._applyShortcut(actionNode)

    def _saveShortcuts(self):
        """Save shortcuts to configuration file
        """
        if self._config is None:
            return
        for actionNode in _recursiveIndexesList(self._model):
            if actionNode.action():
                path = map(str, actionNode.path().split('/'))
                menuDict = self._config
                for menu in path[:-1]:
                    if menu not in menuDict:
                        menuDict[menu] = {}
                    menuDict = menuDict[menu]
                menuDict[path[-1]] = str(actionNode.shortcut().toString())
        self._config.write()


    def _onEditShortcuts(self):
        """Handler of *Edit->Shortcuts...* action. Shows dialog, than saves shortcuts to file
        """
        pActionsNodeShortcutEditor (self._model, core.mainWindow()).exec_()
        self._saveShortcuts()
