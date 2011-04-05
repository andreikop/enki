from PyQt4.QtCore import QModelIndex

from mks.monkeycore import core

def _recursiveIndexesList(model, parentIndex = QModelIndex()):
	"""Get recursive list of all model indexes
	"""
	for childRow in range(model.rowCount(parentIndex)):
		childIndex = model.index(childRow, 0, parentIndex)
		yield childIndex
		for index in _recursiveIndexesList(model, childIndex):
			yield index


class ActionManager:
	"""Action manager class creates actions and manages its shortcuts
	"""
	def __init__(self):
		self._model = core.menuBar().model()
		self._model.rowsInserted.connect(self._onActionInserted)
		
		for actionIndex in _recursiveIndexesList(self._model):
			actionNode = self._model.indexToNode(actionIndex)
			if actionNode.action():
				self._applyShortcut(actionNode)
			
	def __term__(self):
		pass

	def _applyShortcut(self, actionNode):
		print 'apply shortcut for', actionNode.path()

	def _onActionInserted(self, parentIndex, start, end):
		for row in range(start, end + 1):
			actionIndex = self._model.index(row, 0, parentIndex)
			actionNode = self._model.indexToNode(actionIndex)
			if actionNode.action():
				self._applyShortcut(actionNode)
