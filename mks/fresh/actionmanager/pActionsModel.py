"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""
import sys

from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QDir, QModelIndex, Qt, QObject, QVariant
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
        self._pathToAction = {}
        #from modeltest import ModelTest
        #self.test = ModelTest(self, self)
    
    def __del__(self):
        if self._pathToAction:
            print >> sys.stderr, 'pActionsModel: you have to delete all actions before destroying actions model'
            print >> sys.stderr, 'Existing actions:', self._pathToAction.keys()
            assert 0

    def action(self, path ):
        return self._pathToAction[self.cleanPath( path )]

    def path(self, action ):
        return action.path

    def clear(self):
        self.beginRemoveRows( QModelIndex(), 0, self.rowCount() -1 )
        self._pathToAction = {}
        self.endRemoveRows()
        
        self.actionsCleared.emit()

    def addAction(self, _path, action, icon=QIcon() ):
        if isinstance(action, QAction):
            path = self.cleanPath( _path )

            subPath = '/'.join(path.split('/')[0: -1])
            parentAction = self._pathToAction[subPath]
            assert parentAction is not None  # At first create menu, than actions
            
            row = len(self.children( parentAction ))
            self._insertAction( path, action, parentAction, row )
            return True
        else:
            text = action
            action = QAction( icon, text, self )
            if not self.addAction( _path, action ) :
                return None

            return action

    def addMenu(self, path, text, icon=QIcon() ):
        action = self._pathToAction.get( path, None )
        if action is not None:
            if action.menu():
               return action
            else:
               assert 0 # not a menu!

        separatorCount = path.count( "/" ) + 1
        if separatorCount:
            parentAction = self._pathToAction.get('/'.join(path.split('/')[0:-1]), None)
        else:
            parentAction = self._pathToAction.get(None, None)
        
        row = len(self.children( parentAction ))
        menu = QMenu()
        action = menu.menuAction()
        action._menu = menu  # avoid deleting menu by the garbadge collectors
        
        self._insertMenu( path, menu, parentAction, row )
        
        action.setIcon( icon )
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
        else:
            assert action is not None
        
        parentAction = self.parentAction( action )
        row = self.children( parentAction ).index( action )
        self._removeAction( action, parentAction, row )
        
        if  removeEmptyPath :
            self.removeCompleteEmptyPathNode( parentAction )

        return True

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
            return QObject.children(self)
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

    def setShortcut(self, action, shortcut):
        if isinstance(action, basestring):
            action = self.action( action )

        if shortcut is None:
            shortcut = QKeySequence()

        for a in self._pathToAction.itervalues():
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

    def cleanText(self, text ):
        sep = "\001"
        return text.replace( "and", sep ).replace( "&", "" ).replace( sep, "and" )

    def _insertAction(self, path, action, parent, row ):
        action.setParent( parent )
        
        self.beginInsertRows( self._index( parent ), row, row )
        
        self._pathToAction[ path ] = action
        action.path = path
        action.changed.connect(self._onActionChanged)
        action.destroyed.connect(self.actionDestroyed)
        
        if  parent:
            parent.menu().addAction( action )
        
        self.endInsertRows()
        
        self.actionInserted.emit( action )

    def _insertMenu(self, path, menu, parent, row ):        
        action = menu.menuAction()

        if parent is not None:
            action.setParent( parent )
        else:
            action.setParent( self )

        self.beginInsertRows( self._index( parent ), row, row )

        self._pathToAction[ path ] = action
        action.path = path
        action.changed.connect(self._onActionChanged)
        action.destroyed.connect(self.actionDestroyed)
        if  parent:
            parent.menu().addMenu( menu )
        self.endInsertRows()
        
        self.actionInserted.emit( action )

    def cleanTree(self, action, parent ):
        path = self.path( action )
        del self._pathToAction[path]

    def removeCompleteEmptyPathNode(self, action ):
        if action is None or not self.path( action ) in self._pathToAction:
            return
        
        if not self.children( action ) :
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
        
        if  path in self._pathToAction:
            self.removeAction( path )
    
    #
    # QAbstractItemModel interface implementation
    #
    def actionByIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return None

    def columnCount(self, parent=QModelIndex()):
        return pActionsModel._COLUMN_COUNT

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
        actions = self.children(self.actionByIndex(parent))
        
        if  row < 0 or row >= len(actions) or \
            column < 0 or column >= pActionsModel._COLUMN_COUNT or \
            ( parent.column() != 0 and parent.isValid() ):
            return QModelIndex()

        return self.createIndex( row, column, actions[row] )

    def _index(self, action, column = 0):
        if action is None:
            return QModelIndex()
        
        parentAction = self.parentAction( action )
        try:
            row = self.children( parentAction ).index( action )
        except ValueError:
            return QModelIndex()
        
        return self.createIndex( row, column, action )

    def parent(self, index ):
        assert isinstance(index, QModelIndex)
        action = self.actionByIndex( index )
        parentAction = self.parentAction( action )
        return self._index(parentAction)
        
        return self.createIndex( row, 0, parentAction )

    def rowCount(self, parent = QModelIndex()):
        action = self.actionByIndex( parent )
        if ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex():
            return len(self.children( action ))
        else:
            return 0

    def hasChildren(self, param=QModelIndex()):
        if isinstance(param, QModelIndex):
            parent = param
            action = self.actionByIndex( parent )
            if ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex():
                return len(self.children( action )) > 0
            else:
                return False

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
    
    def isValid(self, index ):
        if  not index.isValid() or \
            index.row() < 0 or \
            index.column() < 0 or \
            index.column() >= pActionsModel._COLUMN_COUNT :
            return False

        if index.internalPointer() is None:
            return False

        return True
