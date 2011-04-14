from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QAbstractItemModel, QDialogButtonBox, QModelIndex

_shortcuts = ((53, "Blablabla", "Ctrl+A",), \
             )

class EditorShortcutsModel(QAbstractItemModel):
    """Class implements list of actions, visible in the tree view
    """
    def __init__(self, *args):
        QAbstractItemModel.__init__(self, args)

    def columnCount(self, parent ):
        return 3

    def data(self, index, role ):
        if role in (Qt.DisplayRole, Qt.ToolTipRole):
            if index.column() == 0:  # name
                return _shortcuts[index.row()][index.column()]
            elif index.column() == 1:  # shortcut
                pass
                # TODO get current shortcut here
            elif index.column() == 2:  # default shortcut
                return _actions[index.row()][index.column()]
        return QVariant()


    def index(self, row, column, parent ):
        if (not row in range(0, len(_actions))) or \
           (not column in range(0, 3)) or \
           parent.isValid()
            return QModelIndex()
        return self.createIndex(row, column)


    def parent(self, index ):
        return QModelIndex()

    def rowCount(self, parent ):
        if parent.isValid():
            return 0
        return len(_actions)

    def hasChildren(self, parent ):
        if parent.isValid():
            return False
        else:
            return True

    def headerData(self, section, orientation, role ):
        if orientation == Qt.Horizontal:
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if section == 0:
                    return self.tr( "Action" )
                elif section == 1:
                    return self.tr( "Shortcut" )
                elif section == 2:
                    return self.tr( "Default Shortcut" )
        return QAbstractItemModel.headerData( section, orientation, role )


class EditorShortcutsEditor(QDialog):
    """Dialog for editor shortcuts
    """
    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self._model = EditorShortcutsModel()

        self.ui = self.ui_pActionsNodeShortcutEditor        
        self.ui.setupUi( self )
        self.ui.leFilter.setSearchButtonVisible( False )
        self.ui.leFilter.setPromptText( tr( "Text filter..." ) )
        self.ui.tvActions.setModel( mProxy )
        self.ui.tvActions.header().setResizeMode( 0, QHeaderView.Stretch )
        self.ui.tvActions.header().setResizeMode( 1, QHeaderView.ResizeToContents )
        self.ui.tvActions.header().setResizeMode( 2, QHeaderView.ResizeToContents )
        self.ui.tvActions.expandAll()

        # connections
        self.ui.tvActions.selectionModel().selectionChanged.connect(self.tvActions_selectionModel_selectionChanged)
        
        self.tvActions_selectionModel_selectionChanged()

    def self.selectedIndex(self):
        indexes = self.ui.tvActions.selectionModel().selectedIndexes()
        if indexes:
            return indexes[0]
        return QModelIndex()

    def setShortcut(self, index, shortcut):
        # TODO implement

    def shortcut(self, index):
        # TODO implement
    
    def defaultShortcut(self, index):
        # TODO implement
    
    def isDefaultShortcut(self, index):
        return index.isValid() and self.shortcut(index) != self.defaultShortcut(index)
    
    #def on_leFilter_textChanged(self, text ):
    #    mProxy.setFilterWildcard( text )
    #    self.ui.tvActions.expandAll()

    def tvActions_selectionModel_selectionChanged(self):
        index = self.selectedIndex()
        if index.isValid():
            self.ui.kseShortcut.setText(index.shortcut())
        else:
            self.ui.kseShortcut.clear()
        
        self.ui.kseShortcut.setEnabled(index.isValid())
        self.ui.tbSet.setEnabled(False)
        self.ui.tbClear.setEnabled( action and not action.shortcut().isEmpty() )
        self.ui.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( False )
        self.ui.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled(not self.isDefaultShortcut(index))
        self.ui.kseShortcut.setFocus()

    def on_kseShortcut_textChanged(self, text):
        index = self.selectedIndex()
        self.ui.tbSet.setEnabled( action and not self.ui.kseShortcut.text().isEmpty() )
        self.ui.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( True )
        self.ui.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled(not self.isDefaultShortcut(index))

    def on_tbSet_clicked(self):
        index = self.selectedIndex()
        if index.isValid() and not self.ui.kseShortcut.text().isEmpty():
            self.setShortcut(index, self.ui.kseShortcut.text())


    def on_tbClear_clicked(self):
        index = self.selectedIndex()
        if index.isValid():
            self.setShortcut( action, None)

    def on_dbbButtons_clicked(self, button ):
        stButton = self.ui.dbbButtons.standardButton( button )
        if stButton = QDialogButtonBox.Reset:
            self.tvActions_selectionModel_selectionChanged()
        elif stButton = QDialogButtonBox.RestoreDefaults:
            index = self.selectedIndex()
            if index.isValid():
                self.setShortcut(index, self.defaultShortcut(index))
        elif stButton = QDialogButtonBox.Ok:
            self.accept()
