import sys

from PyQt4.QtCore import pyqtSignal, QDir, QObject
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QMenu

class ActionManager(QObject):

    actionInserted = pyqtSignal(QAction)
    actionChanged = pyqtSignal(QAction)
    actionRemoved = pyqtSignal(QAction)

    def __init__(self, parent=None):
        QObject.__init__(self,  parent )
        self._pathToAction = {}
    
    def __del__(self):
        if self._pathToAction:
            print >> sys.stderr, 'ActionManager: you have to delete all actions before destroying actions model'
            print >> sys.stderr, 'Existing actions:', self._pathToAction.keys()
            assert 0

    def action(self, path ):
        return self._pathToAction.get(self._cleanPath( path ), None)
    
    def allActions(self):
        return self._pathToAction.itervalues()

    def path(self, action ):
        return action.path

    def addAction(self, _path, action, icon=QIcon(), shortcut=None):
        path = self._cleanPath( _path )

        subPath = '/'.join(path.split('/')[0: -1])
        parentAction = self.action(subPath)
        if parentAction is None:
            print >> sys.stderr, "Menu path not found", subPath
            assert False
        
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
        return self.removeMenu( pathOrAction, removeEmptyPath )

    def addMenu(self, path, text, icon=QIcon() ):
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
        if isinstance(action, basestring):
            action = self.action( action )
        assert action is not None
        
        self._removeAction( action)
        
        if  removeEmptyPath :
            self._removeCompleteEmptyPathNode( parentAction )

        return True

    def _removeAction(self, action):
        parent = self.parentAction( action )
        if  parent is not None:
            parent.menu().removeAction( action )

        path = self.path( action )
        del self._pathToAction[path]

        self.actionRemoved.emit( action )

    def _removeCompleteEmptyPathNode(self, action ):        
        if not self.children( action ) :
            parentAction = self.parentAction( action )
            self._removeAction(action)
            self._removeCompleteEmptyPathNode( parentAction )

    def _cleanPath(self, path ):
        data = QDir.cleanPath( path ).replace( '\\', '/' ).strip()
        return data.strip('/')

    def parentAction(self, action ):
        if action is None:
            return None
        
        parentObject = action.parent()
        if parentObject != self:
            return parentObject
        else:
            return None

    def children(self, action ):
        if action is None:
            return filter(lambda o: isinstance(o, QAction), QObject.children(self))
        else:
            return action.children()

    def defaultShortcut(self, action ):
        if isinstance(action, basestring):
            action = self.action( action )

        if action is not None:
            if hasattr(action, 'defaultShortcut'):
                return action.defaultShortcut
        
        return QKeySequence()

    def setDefaultShortcut(self, action, shortcut ):
        if isinstance(action, basestring):
            action = self.action( action )
        
        if isinstance(shortcut, basestring):
            shortcut = QKeySequence(shortcut)

        action.defaultShortcut = shortcut
        
        if not action.shortcut():
            action.setShortcut( shortcut )

    def _onActionChanged(self):
        action = self.sender()
        self.actionChanged.emit( action )
