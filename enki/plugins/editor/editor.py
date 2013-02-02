"""
editor --- AbstractTextEditor implementation
============================================

Uses Qutepart internally
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextCursor, QVBoxLayout

from enki.core.core import core
from enki.core.abstractdocument import AbstractTextEditor

from qutepart import Qutepart

class Editor(AbstractTextEditor):
    """Text editor widget.
    
    Uses Qutepart internally
    """
    
    def __init__(self, parentObject, filePath, createNew=False, terminalWidget=False):
        super(Editor, self).__init__(parentObject, filePath, createNew)
        
        self._terminalWidget = terminalWidget

        self.qutepart = Qutepart(self)
        
        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.qutepart)
        self.setFocusProxy(self.qutepart)
        
        if not self._neverSaved:
            originalText = self._readFile(filePath)
            self.qutepart.text = originalText
        else:
            originalText = ''

        #autodetect eol, if need
        self._configureEolMode(originalText)
        
        self.qutepart.detectSyntax(sourceFilePath = filePath)

