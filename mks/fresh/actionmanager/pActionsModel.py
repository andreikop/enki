"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant
from PyQt4.QtGui import QAction, QKeySequence

def tr(text):
    return text

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
        self._indexCache = {}
    
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
                return self._cleanText( action.text() )
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
        parentAction = self.actionByIndex(parent)
        try:
            return self._indexCache[(parentAction, row, column)]
        except KeyError:
            actions = self._manager.children(self.actionByIndex(parent))
            
            if  row < 0 or row >= len(actions) or \
                column < 0 or column >= ActionModel._COLUMN_COUNT or \
                ( parent.column() != 0 and parent.isValid() ):
                return QModelIndex()

            index = self.createIndex( row, column, actions[row] )
            self._indexCache[(parentAction, row, column)] = index
            return index

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
        index = self._index(action, 1)
        self.dataChanged.emit(index, index)
        
        return True, None
    
    def _cleanText(self, text ):
        sep = "\001"
        return text.replace( "and", sep ).replace( "&", "" ).replace( sep, "and" )

