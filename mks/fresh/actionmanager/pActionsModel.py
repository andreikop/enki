"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""
import sys

from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QDir, QModelIndex, Qt, QObject, QVariant
from PyQt4.QtGui import QAction, QKeySequence, QIcon, QMenu

def tr(text):
    return text

class pActionsManager(QObject):

    actionInserted = pyqtSignal(QAction)
    actionChanged = pyqtSignal(QAction)
    actionRemoved = pyqtSignal(QAction)

    def __init__(self, parent=None):
        QObject.__init__(self,  parent )
        self._pathToAction = {}
    
    def __del__(self):
        if self._pathToAction:
            print >> sys.stderr, 'pActionsManager: you have to delete all actions before destroying actions model'
            print >> sys.stderr, 'Existing actions:', self._pathToAction.keys()
            assert 0

    def model(self):
        return ActionModel(self)

    def action(self, path ):
        return self._pathToAction.get(self._cleanPath( path ), None)
    
    def allActions(self):
        return self._pathToAction.itervalues()

    def path(self, action ):
        return action.path

    def addAction(self, _path, action, icon=QIcon() ):        
        path = self._cleanPath( _path )

        subPath = '/'.join(path.split('/')[0: -1])
        parentAction = self.action(subPath)
        assert parentAction is not None  # At first create menu, than actions
        
        if isinstance(action, basestring):
            action = QAction( icon, action, parentAction )
        else:
            action.setParent( parentAction )
        
        parentAction.menu().addAction( action )
        
        self._pathToAction[ path ] = action
        action.path = path
        
        action.changed.connect(self._onActionChanged)
        action.destroyed.connect(self._onActionDestroyed)

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
        action.destroyed.connect(self._onActionDestroyed)
                
        self.actionInserted.emit( action )
        
        return action

    def removeMenu(self, action, removeEmptyPath=False ):
        if isinstance(action, basestring):
            action = self.action( action )
        
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
        action.deleteLater()

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

    def _onActionDestroyed(self, object ):
        action = object
        path = self.path( action )
        self.removeAction( path )


class ActionModel(QAbstractItemModel):
    _COLUMN_COUNT = 3
    
    Action = 0
    Shortcut = 1
    DefaultShortcut = 2
    
    MenuRole = Qt.UserRole
    ActionRole = Qt.UserRole + 1

    def __init__(self, manager):
        QAbstractItemModel.__init__(self, manager)
        self._manager = manager
    
    def actionByIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return None

    def columnCount(self, parent=QModelIndex()):
        return ActionModel._COLUMN_COUNT

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        action = index.internalPointer()

        if role == Qt.DecorationRole:
            if index.column() == 0:
                return action.icon()
            else:
                pass
        elif role in (Qt.DisplayRole, Qt.ToolTipRole):
            if index.column() == ActionModel.Action:
                return self._manager._cleanText( action.text() )
            elif index.column() == ActionModel.Shortcut:
                return action.shortcut().toString( QKeySequence.NativeText )
            elif index.column() == ActionModel.DefaultShortcut:
                return self._manager.defaultShortcut( action ).toString( QKeySequence.NativeText )
        elif role == Qt.FontRole:
            font = action.font()
            if  action.menu():
                font.setBold( True )
            return font
            '''case Qt.BackgroundRole:
                return action.menu() ? QBrush( QColor( 0, 0, 255, 20 ) ) : QVariant();'''
        elif role == ActionModel.MenuRole:
            return QVariant.fromValue( action.menu() )
        elif role == ActionModel.ActionRole:
            return QVariant.fromValue( action )

        return QVariant()

    def index(self, row, column, parent = QModelIndex()):
        actions = self._manager.children(self.actionByIndex(parent))
        
        if  row < 0 or row >= len(actions) or \
            column < 0 or column >= ActionModel._COLUMN_COUNT or \
            ( parent.column() != 0 and parent.isValid() ):
            return QModelIndex()

        assert isinstance(actions[row], QAction)
        return self.createIndex( row, column, actions[row] )

    def _index(self, action, column = 0):
        if action is None:
            return QModelIndex()
        
        parentAction = self._manager.parentAction( action )
        try:
            row = self._manager.children( parentAction ).index( action )
        except ValueError:
            return QModelIndex()
        
        assert isinstance(action, QAction)
        return self.createIndex( row, column, action )

    def parent(self, index ):
        assert isinstance(index, QModelIndex)
        action = self.actionByIndex( index )
        parentAction = self._manager.parentAction( action )
        return self._index(parentAction)

    def rowCount(self, parent = QModelIndex()):
        action = self.actionByIndex( parent )
        if ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex():
            return len(self._manager.children( action ))
        else:
            return 0

    def hasChildren(self, param=QModelIndex()):
        if isinstance(param, QModelIndex):
            parent = param
            action = self.actionByIndex( parent )
            if ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex():
                return len(self._manager.children( action )) > 0
            else:
                return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if  role == Qt.DisplayRole or role == Qt.ToolTipRole :
                if section == ActionModel.Action:
                    return tr( "Action" )
                elif section == ActionModel.Shortcut:
                    return tr( "Shortcut" )
                elif section == ActionModel.DefaultShortcut:
                    return tr( "Default Shortcut" )
        
        return QAbstractItemModel.headerData(self,  section, orientation, role )
    
    def isValid(self, index ):
        if  not index.isValid() or \
            index.row() < 0 or \
            index.column() < 0 or \
            index.column() >= ActionModel._COLUMN_COUNT :
            return False

        if index.internalPointer() is None:
            return False

        return True

    def setShortcut(self, action, shortcut):
        if isinstance(action, basestring):
            action = self.action( action )

        if shortcut is None:
            shortcut = QKeySequence()

        for a in self._manager.allActions():
            if  a != action :
                if a.shortcut():
                    if  a.shortcut() == shortcut :
                        error = tr( "Can't set shortcut, it's already used by action '%s'." % \
                                        self._cleanText( a.text() ))
                        return False, error

        action.setShortcut( shortcut )
        return True, None
    
    def _cleanText(self, text ):
        sep = "\001"
        return text.replace( "and", sep ).replace( "&", "" ).replace( sep, "and" )

