"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QDir, QModelIndex, Qt, QVariant
from PyQt4.QtGui import QAction, QKeySequence, QIcon, QMenu

def tr(text):
    return text

class pActionsModel(QAbstractItemModel):

    actionInserted = pyqtSignal(QAction)
    actionChanged = pyqtSignal(QAction)
    actionRemoved = pyqtSignal(QAction)
    actionsCleared = pyqtSignal()

    _COLUMN_COUNT = 3
    
    Action = 0
    Shortcut = 1
    DefaultShortcut = 2
    
    MenuRole = Qt.UserRole
    ActionRole = Qt.UserRole + 1

    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self,  parent )
        self._actions = {}
        self._children = {}
        self._createdMenuForAction = {}
    
    def __term__(self):
        self.clear()

    def columnCount(self, parent=QModelIndex()):
        return pActionsModel._COLUMN_COUNT

    def data(self, index, role=Qt.DisplayRole):
        action = self.action( index )
        
        if action is None:
            return QVariant()

        if role == Qt.DecorationRole:
            if index.column() == 0:
                return action.icon()
            else:
                pass
        elif role in (Qt.DisplayRole, Qt.ToolTipRole):
            if index.column() == pActionsModel.Action:
                return self.cleanText( action.text() )
            elif index.column() == pActionsModel.Shortcut:
                return action.shortcut().toString( QKeySequence.NativeText )
            elif index.column() == pActionsModel.DefaultShortcut:
                return self.defaultShortcut( action ).toString( QKeySequence.NativeText )
        elif role == Qt.FontRole:
            font = action.font()
            if  action.menu():
                font.setBold( True )
            return font
            '''case Qt.BackgroundRole:
                return action.menu() ? QBrush( QColor( 0, 0, 255, 20 ) ) : QVariant();'''
        elif role == pActionsModel.MenuRole:
            return QVariant.fromValue( action.menu() )
        elif role == pActionsModel.ActionRole:
            return QVariant.fromValue( action )

        return QVariant()

    def index(self, row, column, parent = QModelIndex()):
        action = self.action( parent )
        actions = self.children( action )
        
        if  row < 0 or row >= len(actions) or \
            column < 0 or column >= pActionsModel._COLUMN_COUNT or \
            ( parent.column() != 0 and parent.isValid() ):
            return QModelIndex()

        return self.createIndex( row, column, actions[row] )

    def _index(self, action, column = 0):
        path = self.path( action )
        
        if not path in self._actions:
            return QModelIndex()
        
        parentAction = self.parentAction( action )
        try:
            row = self.children( parentAction ).index( action )
        except ValueError:
            return QModelIndex()
        
        return self.createIndex( row, column, self._actions[ path ] )

    def parent(self, index ):
        assert isinstance(index, QModelIndex)
        action = self.action( index )
        parentAction = self.parentAction( action )
        return self._index(parentAction)
        
        return self.createIndex( row, 0, parentAction )

    def rowCount(self, parent = QModelIndex()):
        action = self.action( parent )
        if ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex():
            return len(self.children( action ))
        else:
            return 0

    def hasChildren(self, param=QModelIndex()):
        if isinstance(param, QModelIndex):
            parent = param
            action = self.action( parent )
            if ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex():
                return self.hasChildren( action )
            else:
                return False
        else:
            action = param
            return action in self._children

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if  role == Qt.DisplayRole or role == Qt.ToolTipRole :
                if section == pActionsModel.Action:
                    return tr( "Action" )
                elif section == pActionsModel.Shortcut:
                    return tr( "Shortcut" )
                elif section == pActionsModel.DefaultShortcut:
                    return tr( "Default Shortcut" )
        
        return QAbstractItemModel.headerData(self,  section, orientation, role )

    def action(self, indexOrPath ):
        if isinstance(indexOrPath, QModelIndex):
            index = indexOrPath
            if index.isValid():
                return index.internalPointer()
            else:
                return None
        else:
            path = indexOrPath
            return self._actions.get(self.cleanPath( path ), None)

    def path(self, action ):
        reverse = {v:k for k, v in self._actions.iteritems()}
        return reverse.get(action, None)

    def clear(self):
        count = self.rowCount()
        
        if  count == 0:
            return
        
        self.beginRemoveRows( QModelIndex(), 0, count -1 )
        #qDeleteAll( self._children[0] )
        self._children = {}
        self._actions = {}
        self.endRemoveRows()
        
        self.actionsCleared.emit()

    def addAction(self, _path, action, icon=QIcon() ):
        if isinstance(action, QAction):
            path = self.cleanPath( _path )

            subPath = '/'.join(path.split('/')[0: -1])
            parentAction = self.createCompletePathNode( subPath )
            if parentAction is None:
                return False
            
            row = len(self.children( parentAction ))
            self.insertAction( path, action, parentAction, row )
            return True
        else:
            text = action
            action = QAction( icon, text, self )
            if not self.addAction( _path, action ) :
                return None

            return action

    def addMenu(self, path, text, icon=QIcon() ):
        action = self.createCompletePathNode( path )
        
        if  action is not None:
            action.setIcon( icon )
        if  text:
            action.setText( text )
        
        return action

    def removeAction(self, pathOrAction, removeEmptyPath=False):
        return self.removeMenu( pathOrAction, removeEmptyPath )

    def _removeAction(self, action, parent, row ):        
        self.beginRemoveRows( self._index( parent ), row, row )
        if  parent is not None:
            parent.menu().removeAction( action )

        self.cleanTree( action, parent )
        self.endRemoveRows()
        
        self.actionRemoved.emit( action )
        
        action.deleteLater()

    def removeMenu(self, action, removeEmptyPath=False ):
        if isinstance(action, basestring):
            action = self.action( action )
        
        if action is None:
            return False
        
        parentAction = self.parentAction( action )
        if parentAction is not None:
            row = self.children( parentAction ).index( action )
            self._removeAction( action, parentAction, row )
        
        if  removeEmptyPath :
            self.removeCompleteEmptyPathNode( parentAction )

        return True

    def parentAction(self, action ):
        assert isinstance(action, QAction)
        return self._actions.get('/'.join(self.path( action ).split('/')[0: -1]), None)

    def children(self, action ):
        return self._children.get(action, [])

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
            self.setShortcut( action, shortcut )

    def setShortcut(self, action, shortcut):
        if isinstance(action, basestring):
            action = self.action( action )

        for a in self._actions.itervalues():
            if  a != action :
                if a.shortcut():
                    if  a.shortcut() == shortcut :
                        error = tr( "Can't set shortcut, it's already used by action '%s'." % \
                                        self.cleanText( a.text() ))
                        return False, error

        action.setShortcut( shortcut )
        return True, None

    def cleanPath(self, path ):
        data = QDir.cleanPath( path ).replace( '\\', '/' ).strip()
        
        while ( data.startswith( '/' ) ):
            data = data[1:]

        while ( data.endswith( '/' ) ):
            data = data[:-1]
        
        return data

    def isValid(self, index ):
        if  not index.isValid() or \
            index.row() < 0 or \
            index.column() < 0 or \
            index.column() >= pActionsModel._COLUMN_COUNT :
            return False

        action = index.internalPointer()
        parentAction = self.parentAction( action )
        
        if  action is None:
            return False

        if  index.row() >= len(self.children( parentAction )):
            return False

        return True

    def cleanText(self, text ):
        sep = "\001"
        return text.replace( "and", sep ).replace( "&", "" ).replace( sep, "and" )

    def insertAction(self, path, actionOrMenu, parent, row ):
        p = parent
        if p is None:
            p = self
        
        if isinstance(actionOrMenu, QAction):
            action = actionOrMenu
            menu = action.menu()
            menuIsSet = False
        else:
            menu = actionOrMenu
            action = menu.menuAction()
            menuIsSet = True
        
        self.beginInsertRows( self._index( parent ), row, row )
        action.setObjectName( path.replace( "/", "_" ) )
        action.setParent( p )
        if  parent:
            if menuIsSet:
                parent.menu().addMenu( menu )
            else:
                parent.menu().addAction( action )

        if not action.text():
            action.setText( path.split('/')[-1] )

        if not parent in self._children:
            self._children[ parent ] = []
        self._children[ parent ].append(action)
        self._actions[ path ] = action
        action.changed.connect(self._onActionChanged)
        action.destroyed.connect(self.actionDestroyed)
        self.endInsertRows()
        
        self.actionInserted.emit( action )

    def cleanTree(self, action, parent ):

        parentChildren = self._children[ parent ]
        parentChildren.remove( action )

        if action in self._children:
            for a in self._children.get(action, []):
                self.cleanTree( a, action )
            del self._children[action]

        del self._actions[self.path( action )]
        if action in self._createdMenuForAction:
            del self._createdMenuForAction[action]

    def createCompletePathNode(self, path ):
        action = self._actions.get( path, None )
        
        if action is not None:
            if action.menu() is not None:
                return action
            else:
                return None

        separatorCount = path.count( "/" ) + 1
        parentAction = None
        
        for i in range(separatorCount):
            subPath = '/'.join(path.split('/')[0:i + 1])
            action = self._actions.get( subPath, None )
            
            if action is not None:
                if  path != subPath :
                    continue
            
                if action.menu():
                   return action
                else:
                   return None
            
            if i == 0:
                parentAction = self._actions.get(None, None)
            else:
                parentAction = self._actions.get('/'.join(path.split('/')[0:i]), None)
            row = len(self.children( parentAction ))
            menu = QMenu()
            action = menu.menuAction()

            self._createdMenuForAction[action] = menu

            action.setText( '/'.join(path.split('/')[i:i + 1]) )
            self.insertAction( subPath, menu, parentAction, row )

        return action

    def removeCompleteEmptyPathNode(self, action ):
        if action is None or not self.path( action ) in self._actions:
            return
        
        if not self.hasChildren( action ) :
            parentAction = self.parentAction( action )
            row = self.children( parentAction ).index( action )
            
            self._removeAction( action, parentAction, row )
            self.removeCompleteEmptyPathNode( parentAction )

    def _onActionChanged(self):
        action = self.sender()
        
        if  action is not None:
            self.dataChanged.emit( self._index( action, 0 ), self._index( action, pActionsModel._COLUMN_COUNT -1 ) )
            self.actionChanged.emit( action )

    def actionDestroyed(self, object ):
        action = object
        path = self.path( action )
        
        if  path in self._actions:
            self.removeAction( path )
