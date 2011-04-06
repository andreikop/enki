import os.path

from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QIcon
from PyQt4.fresh import pActionsNodeShortcutEditor

from mks._3rdparty.configobj import ConfigObj, ParseError

from mks.monkeycore import core

_CONFIG_PATH = os.path.expanduser('~/.mksv3.shortcuts.cfg')

def _recursiveIndexesList(model, parentIndex = QModelIndex()):
    """Get recursive list of all model indexes
    """
    for childRow in range(model.rowCount(parentIndex)):
        childIndex = model.index(childRow, 0, parentIndex)
        yield model.indexToNode(childIndex)
        for index in _recursiveIndexesList(model, childIndex):
            yield index


class ActionManager:
    """Action manager class creates actions and manages its shortcuts
    """
    def __init__(self):
        try:
            self._config = ConfigObj(_CONFIG_PATH)
        except ParseError, ex:
            core.messageManager().appendMessage('Failed to parse configuration file %s\n'
                                                'Error:\n'
                                                '%s\n'
                                                'Fix the file or delete it.' % (_CONFIG_PATH, unicode(str(ex), 'utf_8')))
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


    def __term__(self):
        pass

    def _applyShortcut(self, actionNode):
        if self._config is not None:
            path = map(str, actionNode.path().split('/'))
            menuDict = self._config
            for menu in path[:-1]:
                if menu not in menuDict:
                    return
                menuDict = menuDict[menu]
            actionNode.setShortcut(menuDict[path[-1]])

    def _onActionInserted(self, parentIndex, start, end):
        for row in range(start, end + 1):
            actionIndex = self._model.index(row, 0, parentIndex)
            actionNode = self._model.indexToNode(actionIndex)
            if actionNode.action():
                self._applyShortcut(actionNode)

    def _saveShortcuts(self):
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
        pActionsNodeShortcutEditor (self._model, core.mainWindow()).exec_()
        self._saveShortcuts()
