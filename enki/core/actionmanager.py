"""
actionmanager --- Provides text path based access to main menu actions
======================================================================

Use this module for adding own actions to the main menu

Shortcuts are configured by appshortcuts plugin
"""

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QMenu, QMenuBar, QAction
from PyQt5.QtGui import QIcon, QKeySequence

from enki.core.core import core


class ActionMenuBar(QMenuBar):
    """Menu bar implementation.
    Contains actions, managed by ActionManager.
    Instance is created by MainWindow
    """

    def __init__(self, parent, actionManager):
        QMenuBar.__init__(self, parent)
        self._manager = actionManager

        for action in self._manager.allActions():
            self._onActionInserted(action)

        self._manager.actionInserted.connect(self._onActionInserted)
        self._manager.actionRemoved.connect(self._onActionRemoved)

    @pyqtSlot(QAction)
    def _onActionInserted(self, action):
        parent = self._manager.parentAction(action)

        if parent is None and action.menu():
            self.addMenu(action.menu())

    @pyqtSlot(QAction)
    def _onActionRemoved(self, action):
        parent = self._manager.parentAction(action)

        if parent is None and action.menu():
            self.removeAction(action)


class ActionManager(QObject):
    """Class provides text path based access to main menu actions
    """

    actionInserted = pyqtSignal(QAction)
    """
    actionInserted(action)

    **Signal** emitted, when new action has been inserted to the menu
    """  # pylint: disable=W0105

    actionChanged = pyqtSignal(QAction)
    """
    actionChanged(action)

    **Signal** emitted, when some action datahas been changed
    """  # pylint: disable=W0105

    actionRemoved = pyqtSignal(QAction)
    """
    actionRemoved(action)

    **Signal** emitted, when action has been removed from the menu
    """  # pylint: disable=W0105

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._pathToAction = {}

    def terminate(self):
        if self._pathToAction:
            assert 0, 'ActionManager: you have to delete all actions before destroying actions model. ' + \
                      'Existing actions: ' + ', '.join(self._pathToAction.keys())

    def action(self, path):
        """Get action by its path. i.e.
            actionManager.action("mFile/mClose/aAll")
        """
        return self._pathToAction.get(path, None)

    def menu(self, path):
        """Get action by its path. i.e.
            actionManager.action("mFile/mClose/aAll")
        """
        if path in self._pathToAction:
            return self._pathToAction[path].menu()
        else:
            return None

    def path(self, action):
        """Get action path by reference to action
        """
        return action.path

    def allActions(self):
        """Reqursive list of existing actions
        """
        return iter(self._pathToAction.values())

    @staticmethod
    def _parentPath(path):
        return '/'.join(path.split('/')[0: -1])

    def addAction(self, path, action, icon=QIcon(), shortcut=None):
        """Add new action to the menu.
        Returns created QAction object.
        ``action`` might be string text or QAction instance.
        """
        subPath = self._parentPath(path)
        parentAction = self.action(subPath)
        if parentAction is None:
            assert False, "Menu path not found: " + subPath

        if isinstance(action, str):
            action = QAction(icon, action, parentAction)
        else:
            action.setParent(parentAction)

        if shortcut is not None:
            action.setShortcut(shortcut)

        parentAction.menu().addAction(action)

        self._pathToAction[path] = action
        action.path = path

        action.changed.connect(self._onActionChanged)

        """ On Ubuntu 14.04 keyboard shortcuts doesn't work without this line
        http://stackoverflow.com/questions/23916623/
            qt5-doesnt-recognised-shortcuts-unless-actions-are-added-to-a-toolbar
        """
        core.mainWindow().addAction(action)
        self.actionInserted.emit(action)

        return action

    def removeAction(self, pathOrAction):
        """Remove action from the menu
        """
        return self.removeMenu(pathOrAction)

    def addMenu(self, path, text, icon=QIcon()):
        """Add menu to the main menu or submenu of main menu
        """
        action = self.action(path)
        if action is not None:
            if action.menu():
                return action
            else:
                assert 0  # not a menu!

        parentMenuPath = self._parentPath(path)
        if parentMenuPath:
            parentAction = self.action(parentMenuPath)
        else:
            parentAction = None

        menu = QMenu()
        action = menu.menuAction()
        action._menu = menu  # avoid deleting menu by the garbadge collectors
        action.setIcon(icon)
        action.setText(text)

        if parentAction is not None:
            action.setParent(parentAction)
            parentAction.menu().addMenu(menu)
        else:
            action.setParent(self)

        self._pathToAction[path] = action
        action.path = path

        action.changed.connect(self._onActionChanged)

        self.actionInserted.emit(action)

        return action

    def removeMenu(self, action):
        """Remove menu.
        If removeEmptyPath is True - remove also empty parent menus
        """
        if isinstance(action, str):
            action = self.action(action)
        assert action is not None

        self._removeAction(action)

        return True

    def _removeAction(self, action):
        """Remove action by reference to it
        """
        parent = self.parentAction(action)
        if parent is not None:
            parent.menu().removeAction(action)

        path = action.path
        del self._pathToAction[path]
        action.changed.disconnect(self._onActionChanged)
        action.setParent(None)

        core.mainWindow().removeAction(action)

        self.actionRemoved.emit(action)

    def _removeCompleteEmptyPathNode(self, action):
        """Remove empty menu and empty parent menus
        """
        if not self.children(action):
            parentAction = self.parentAction(action)
            self._removeAction(action)
            self._removeCompleteEmptyPathNode(parentAction)

    def parentAction(self, action):
        """Parent action of the action
        """
        if action is None:
            return None

        parentObject = action.parent()
        if parentObject != self:
            return parentObject
        else:
            return None

    def children(self, action):
        """List of children of action
        """
        if action is None:
            return [object
                    for object in QObject.children(self)
                    if isinstance(object, QAction) and
                    object in iter(self._pathToAction.values())]
        else:
            return [object
                    for object in action.children()
                    if object in iter(self._pathToAction.values())]

    def defaultShortcut(self, action):
        """Get actions default shortcut
        """
        if isinstance(action, str):
            action = self.action(action)

        if action is not None:
            if hasattr(action, 'defaultShortcut'):
                return action.defaultShortcut

        return QKeySequence()

    def setDefaultShortcut(self, action, shortcut):
        """Set actions default shortcut
        """
        if isinstance(action, str):
            action = self.action(action)

        if isinstance(shortcut, str):
            shortcut = QKeySequence(shortcut)

        action.defaultShortcut = shortcut

        if not action.shortcut():
            action.setShortcut(shortcut)

    @pyqtSlot()
    def _onActionChanged(self):
        """Action changed handler.
        Retransmit signal with reference to the action
        """
        action = self.sender()
        self.actionChanged.emit(action)
