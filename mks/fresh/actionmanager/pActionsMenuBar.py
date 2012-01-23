"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtGui import QMenuBar

from .pActionsModel import pActionsModel

class pActionsMenuBar(QMenuBar):
    def __init__(self, parent):
        QMenuBar.__init__(self, parent)
        self._model = None

    def setModel(self, model ):
        if self._model is not None:
            self._model.actionInserted.disconnect(self.model_actionInserted)
            self._model.actionsCleared.disconnect(self.model_actionsCleared)
            self.clear()
            self._model = None
        
        self._model = model
        
        if  self._model is not None:
            for i in range(self._model.rowCount()):
                action = self._model.action( self._model.index( i, 0 ) )
                self.model_actionInserted( action )

        if self._model is not None:
            self._model.actionInserted.connect(self.model_actionInserted)
            self._model.actionsCleared.connect(self.model_actionsCleared)

    def model(self):
        if self._model is None:
            self.setModel( pActionsModel(self) )

        return self._model

    def model_actionInserted(self, action ):
        parent = self._model.parentAction( action )
        
        if parent is None and action.menu():
            self.addMenu( action.menu() )

    def model_actionsCleared(self):
        self.clear()
