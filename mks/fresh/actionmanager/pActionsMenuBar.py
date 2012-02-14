"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtGui import QMenuBar

from .pActionsModel import pActionsManager

class pActionsMenuBar(QMenuBar):
    def __init__(self, parent):
        QMenuBar.__init__(self, parent)
        self._manager = None

    def setModel(self, model ):
        if self._manager is not None:
            self._manager.actionInserted.disconnect(self.model_actionInserted)
            self._manager.actionsCleared.disconnect(self.model_actionsCleared)
            self.clear()
            self._manager = None
        
        self._manager = model
        
        if  self._manager is not None:
            for action in self._manager.children(None):
                self.model_actionInserted( action )

        if self._manager is not None:
            self._manager.actionInserted.connect(self.model_actionInserted)
            self._manager.actionsCleared.connect(self.model_actionsCleared)

    def model(self):
        if self._manager is None:
            self.setModel( pActionsManager(self) )

        return self._manager

    def model_actionInserted(self, action ):
        parent = self._manager.parentAction( action )
        
        if parent is None and action.menu():
            self.addMenu( action.menu() )

    def model_actionsCleared(self):
        self.clear()
