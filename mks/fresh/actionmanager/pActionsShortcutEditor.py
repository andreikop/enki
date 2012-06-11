"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

import os.path

from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QDialogButtonBox, QHeaderView, QMessageBox, QSortFilterProxyModel

from pActionsModel import ActionModel

def tr(text):
    return text

class pRecursiveSortFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index( source_row, 0, source_parent )
        rowCount = self.sourceModel().rowCount( index )
        accepted = QSortFilterProxyModel.filterAcceptsRow( self, source_row, source_parent )
        
        if rowCount > 0 and not accepted :
            for row in range(rowCount):
                if  self.filterAcceptsRow(row, index):
                    return True
    
        return accepted

class pActionsShortcutEditor(QDialog):
    def __init__(self, manager, parent):
        QDialog.__init__(self, parent)

        self._manager = manager
        self._model = ActionModel(manager)
        self._originalShortcuts = {}
        self._proxy = pRecursiveSortFilterProxyModel( self )
        
        self._proxy.setSourceModel( self._model )
        self._proxy.setFilterCaseSensitivity( Qt.CaseInsensitive )
        self._proxy.setSortCaseSensitivity( Qt.CaseInsensitive )
        
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'pActionsShortcutEditor.ui'), self)
        self.leFilter.setSearchButtonVisible( False )
        self.leFilter.setPromptText( tr( "Text filter..." ) )
        self.tvActions.setModel( self._proxy )
        self.tvActions.header().setResizeMode( 0, QHeaderView.Stretch )
        self.tvActions.header().setResizeMode( 1, QHeaderView.ResizeToContents )
        self.tvActions.header().setResizeMode( 2, QHeaderView.ResizeToContents )
        self.tvActions.expandAll()

        # connections
        self.tvActions.selectionModel().selectionChanged.connect(self.tvActions_selectionModel_selectionChanged)
        
        self.tvActions_selectionModel_selectionChanged()

    def selectedAction(self):
        selected = self.tvActions.selectionModel().selectedIndexes()
        if selected:
            proxyIndex = selected[0]
            index = self._proxy.mapToSource( proxyIndex )
            action = self._model.actionByIndex( index )
            if not action.menu():
                return action
        
        return None

    def setShortcut(self, action, shortcut ):
        if not action in self._originalShortcuts:
            self._originalShortcuts[action] = action.shortcut()

        try:
            self._model.setShortcut( action, shortcut)
        except UserWarning as ex:
            QMessageBox.information(self, None, unicode(ex))
            return
        
        self.tvActions_selectionModel_selectionChanged()

    def on_leFilter_textChanged(self, text ):
        self._proxy.setFilterWildcard( text )
        self.tvActions.expandAll()

    def tvActions_selectionModel_selectionChanged(self):
        action = self.selectedAction()
        
        if action is not None:
            self.kseShortcut.setText( action.shortcut().toString() )
        else:
            self.kseShortcut.clear()
        
        self.kseShortcut.setEnabled( action is not None )
        self.tbSet.setEnabled( False )
        self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( False )
        self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled(
                    action is not None and action.shortcut() != self._manager.defaultShortcut( action ) )
        self.kseShortcut.setFocus()

    def on_kseShortcut_textChanged(self, text ):
        action = self.selectedAction()
        
        self.tbSet.setEnabled( action is not None and self.kseShortcut.text() is not None )
        self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( True )
        self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled( 
                            action is not None and action.shortcut() != self._manager.defaultShortcut( action ) )

    def on_tbSet_pressed(self):
        action = self.selectedAction()
        
        if  action is not None:
            self.setShortcut( action, self.kseShortcut.text() )

    def on_dbbButtons_clicked(self, button ):
        if self.dbbButtons.standardButton( button ) == QDialogButtonBox.Reset:
            self.tvActions_selectionModel_selectionChanged()
        elif self.dbbButtons.standardButton( button ) == QDialogButtonBox.RestoreDefaults:
            action = self.selectedAction()
            if action is not None:
                self.setShortcut( action, self._manager.defaultShortcut( action ) )
        elif self.dbbButtons.standardButton( button ) == QDialogButtonBox.Ok:
            self.accept()
        elif self.dbbButtons.standardButton( button ) == QDialogButtonBox.Cancel:
            for action in self._originalShortcuts.keys():
                action.setShortcut( self._originalShortcuts[action] )
            self.reject()
        else:
            assert 0
