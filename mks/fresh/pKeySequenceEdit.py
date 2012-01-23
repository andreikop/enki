"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtCore import QEvent, Qt
from PyQt4.QtGui import QKeySequence

from mks.fresh.pLineEdit import pLineEdit

def tr(text):
    return text

class pKeySequenceEdit(pLineEdit):
    def __init__(self, parent):
        pLineEdit.__init__(self, parent )
        self._finished = True
    
        self.setSearchButtonVisible( False )
        self.setPromptText( tr( "Press a keybord shortcut..." ) )

    def shortcut(self):
        return QKeySequence.fromString(self.text())

    def keyPressEvent(self, event ):
        # return if auto repeat
        if  event.isAutoRepeat():
            return
        
        # if user press something, is not finished
        self._finished = False
        
        # show current sequence
        self.setText( self.keySequence( event ) )

    def keyReleaseEvent(self, event ):
        # return if auto repeat
        if  event.isAutoRepeat() :
            return

        # check if sequence is finished or not
        if  self._finished :
            return

        # show current sequence
        self.setText( self.keySequence( event ) )

    def keySequence(self, event ):
        # is key pressed or key released ?
        keyPressed = event.type() == QEvent.KeyPress
        
        # or-ed keys
        self._keys = 0
        
        # check modifiers pressed
        if  event.modifiers() & Qt.ControlModifier :
            self._keys |= Qt.ControlModifier
        if  event.modifiers() & Qt.AltModifier :
            self._keys |= Qt.AltModifier
        if  event.modifiers() & Qt.ShiftModifier :
            self._keys |= Qt.ShiftModifier
        if  event.modifiers() & Qt.MetaModifier :
            self._keys |= Qt.MetaModifier

        if  keyPressed :        # get press key
            if event.key() in  (Qt.Key_Control,
                                Qt.Key_Alt,
                                Qt.Key_AltGr,
                                Qt.Key_Shift,
                                Qt.Key_Meta,
                                Qt.Key_Super_L,
                                Qt.Key_Super_R,
                                Qt.Key_Menu,
                                Qt.Key_Hyper_L,
                                Qt.Key_Hyper_R,
                                Qt.Key_Help,
                                Qt.Key_Direction_L,
                                Qt.Key_Direction_R):
                pass
            else:
                # add pressed key
                self._keys |= event.key()
                    
                # set sequence finished
                self._finished = True
        
        # return human readable key sequence
        return QKeySequence( self._keys ).toString()
