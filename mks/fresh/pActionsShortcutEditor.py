import os.path

from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

class pActionsShortcutEditor(QDialog):
	def __init__(model, parent):
		QDialog.__init__(parent)
		
		
		self._model = model
		self._proxy = pRecursiveSortFilterProxyModel( self )
		
		self._proxy.setSourceModel( self._model )
		self._proxy.setFilterCaseSensitivity( Qt.CaseInsensitive )
		self._proxy.setSortCaseSensitivity( Qt.CaseInsensitive )
		
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'pActionsShortcutEditor.ui'))
		self.leFilter.setSearchButtonVisible( False )
		self.leFilter.setPromptText( tr( "Text filter..." ) )
		self.tvActions.setModel( self._proxy )
		self.tvActions.header().setResizeMode( 0, QHeaderView.Stretch )
		self.tvActions.header().setResizeMode( 1, QHeaderView.ResizeToContents )
		self.tvActions.header().setResizeMode( 2, QHeaderView.ResizeToContents )
		self.tvActions.expandAll()

		# connections
		self.tvActions.selectionModel().selectionChanged.connect(self.tvActions_selectionModel_selectionChanged)
		
		tvActions_selectionModel_selectionChanged()

	def selectedAction(self):
		proxyIndex = self.tvActions.selectionModel().selectedIndexes().value( 0 )
		index = self._proxy.mapToSource( proxyIndex )
		action = self._model.action( index )
		if action and not action.menu():
			return action
		else
			return None

	def setShortcut(self, action, shortcut ):
		if not action in self._originalShortcuts:
			self._originalShortcuts[action] = action.shortcut()

		QString error
		
		if  self._model.setShortcut( action, shortcut, &error ) :		tvActions_selectionModel_selectionChanged()

		else:
			QMessageBox.information( self, QString.null, error )



	def on_leFilter_textChanged(self, text ):
		self._proxy.setFilterWildcard( text )
		self.tvActions.expandAll()


	def tvActions_selectionModel_selectionChanged(self):
		action = selectedAction()
		
		if  action :		self.kseShortcut.setText( action.shortcut().toString() )

		else:
			self.kseShortcut.clear()

		
		self.kseShortcut.setEnabled( action )
		self.tbSet.setEnabled( False )
		self.tbClear.setEnabled( action and not action.shortcut().isEmpty() )
		self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( False )
		self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled( action and action.shortcut() != self._model.defaultShortcut( action ) )
		
		self.kseShortcut.setFocus()

	def on_kseShortcut_textChanged(self, text ):
		Q_UNUSED( text )
		action = selectedAction()
		

self.tbSet.setEnabled( action and not self.kseShortcut.text().isEmpty() )
		self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( True )
		self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled( action and action.shortcut() != self._model.defaultShortcut( action ) )


	def on_tbSet_clicked(self):
		action = selectedAction()
		
		if  action and not self.kseShortcut.text().isEmpty() :		setShortcut( action, self.kseShortcut.text() )



	def on_tbClear_clicked(self):
		action = selectedAction()
		
		if  action :		setShortcut( action, QString.null )



	def on_dbbButtons_clicked(self, button ):
		switch ( self.dbbButtons.standardButton( button ) )		case QDialogButtonBox.Reset:			tvActions_selectionModel_selectionChanged()
				break

			case QDialogButtonBox.RestoreDefaults:			action = selectedAction()
				
				if  action :				setShortcut( action, self._model.defaultShortcut( action ) )

				
				break

			case QDialogButtonBox.Ok:			accept()
				break

			case QDialogButtonBox.Cancel:			for action in self._originalShortcuts.keys():				action.setShortcut( self._originalShortcuts.value( action ) )

				
				reject()
				break

			default:
				break


