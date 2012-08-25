"""
actionmanager --- Provides text path based access to main menu actions
======================================================================

Use this module for adding own actions to the main menu

Shortcuts are configured by appshortcuts plugin
"""

import sys

from PyQt4.QtCore import pyqtSignal, QDir, QObject
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QMenu, QMenuBar

class ActionMenuBar(QMenuBar):
    """Menu bar implementation.
    Contains actions, managed by ActionManager.
    Instance is created by MainWindow
    """
    def __init__(self, parent, actionManager):
        QMenuBar.__init__(self, parent)
        self._manager = actionManager

        for action in self._manager.allActions():
            self._onActionInserted( action )
            
        self._manager.actionInserted.connect(self._onActionInserted)
        self._manager.actionRemoved.connect(self._onActionRemoved)

    def _onActionInserted(self, action ):
        parent = self._manager.parentAction( action )
        
        if parent is None and action.menu():
            self.addMenu( action.menu() )

    def _onActionRemoved(self, action):
        parent = self._manager.parentAction( action )
        
        if parent is None and action.menu():
            self.removeAction( action )


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
        QObject.__init__(self,  parent )
        self._pathToAction = {}
    
    def __del__(self):
        if self._pathToAction:
            assert 0, 'ActionManager: you have to delete all actions before destroying actions model. ' + \
                      'Existing actions: ' + str(self._pathToAction.keys())

    def action(self, path ):
        """Get action by its path. i.e.
            actionManager.action("mFile/mClose/aAll")
        """
        return self._pathToAction.get(self._cleanPath( path ), None)
    
    def path(self, action):
        """Get action path by reference to action
        """
        return action.path
    
    def allActions(self):
        """Reqursive list of existing actions
        """
        return self._pathToAction.itervalues()

    def addAction(self, _path, action, icon=QIcon(), shortcut=None):
        """Add new action to the menu
        """
        path = self._cleanPath( _path )

        subPath = '/'.join(path.split('/')[0: -1])
        parentAction = self.action(subPath)
        if parentAction is None:
            assert False, "Menu path not found: " + subPath
        
        if isinstance(action, basestring):
            action = QAction( icon, action, parentAction )
        else:
            action.setParent( parentAction )

        if shortcut is not None:
            action.setShortcut(shortcut)

        parentAction.menu().addAction( action )
        
        self._pathToAction[ path ] = action
        action.path = path
        
        action.changed.connect(self._onActionChanged)

        self.actionInserted.emit( action )
        
        return action

    def removeAction(self, pathOrAction, removeEmptyPath=False):
        """Remove action from the menu
        """
        return self.removeMenu( pathOrAction, removeEmptyPath )

    def addMenu(self, path, text, icon=QIcon() ):
        """Add menu to the main menu or submenu of main menu
        """
        action = self.action(path)
        if action is not None:
            if action.menu():
               return action
            else:
               assert 0 # not a menu!

        parentMenuPath = '/'.join(path.split('/')[0:-1])
        if parentMenuPath:
            parentAction = self.action(parentMenuPath)
        else:
            parentAction = None
        
        menu = QMenu()
        action = menu.menuAction()
        action._menu = menu  # avoid deleting menu by the garbadge collectors        
        action.setIcon( icon )
        action.setText( text )

        if parentAction is not None:
            action.setParent( parentAction )
            parentAction.menu().addMenu( menu )
        else:
            action.setParent( self )

        self._pathToAction[ path ] = action
        action.path = path
        
        action.changed.connect(self._onActionChanged)
                
        self.actionInserted.emit( action )
        
        return action

    def removeMenu(self, action, removeEmptyPath=False ):
        """Remove menu.
        If removeEmptyPath is True - remove also empty parent menus
        """
        if isinstance(action, basestring):
            action = self.action( action )
        assert action is not None
        
        self._removeAction( action)
        
        if  removeEmptyPath :
            self._removeCompleteEmptyPathNode( parentAction )

        return True

    def _removeAction(self, action):
        """Remove action by reference to it
        """
        parent = self.parentAction( action )
        if  parent is not None:
            parent.menu().removeAction( action )

        path = action.path
        del self._pathToAction[path]

        self.actionRemoved.emit( action )

    def _removeCompleteEmptyPathNode(self, action ):        
        """Remove empty menu and empty parent menus
        """
        if not self.children( action ) :
            parentAction = self.parentAction( action )
            self._removeAction(action)
            self._removeCompleteEmptyPathNode( parentAction )

    def _cleanPath(self, path ):
        """Escape \\ in the path
        """
        return path.strip('/')

    def parentAction(self, action ):
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
            return [object for object in QObject.children(self) if \
                        isinstance(object, QAction)]
        else:
            return action.children()

    def defaultShortcut(self, action ):
        """Get actions default shortcut
        """
        if isinstance(action, basestring):
            action = self.action( action )

        if action is not None:
            if hasattr(action, 'defaultShortcut'):
                return action.defaultShortcut
        
        return QKeySequence()

    def setDefaultShortcut(self, action, shortcut ):
        """Set actions default shortcut
        """
        if isinstance(action, basestring):
            action = self.action( action )
        
        if isinstance(shortcut, basestring):
            shortcut = QKeySequence(shortcut)

        action.defaultShortcut = shortcut
        
        if not action.shortcut():
            action.setShortcut( shortcut )

    def _onActionChanged(self):
        """Action changed handler.
        Retransmit signal with reference to the action
        """
        action = self.sender()
        self.actionChanged.emit( action )
