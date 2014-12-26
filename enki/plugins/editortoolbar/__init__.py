"""
editortoolbar --- Shows position, save state, EOL and indent
============================================================

It also allows to change this parameters and save the file

File contains integration with the core
"""

from enki.core.core import core
import editortoolbar

class Plugin:
    """Plugin interface implementation

    Installs and removes editor from the system
    """
    def __init__(self):
        tb = core.mainWindow().topToolBar()
        self._vim = editortoolbar.VimModeIndicator(tb)
        self._vimAct = tb.addWidget(self._vim)
        self._vim.setMeVisible.connect(self._vimAct.setVisible)
        # EOL indicator and switcher
        self._eol = editortoolbar.EolIndicatorAndSwitcher(tb)
        self._eolAct = tb.addWidget(self._eol)
        # Indentation indicator and switcher
        self._indent = editortoolbar.IndentIndicatorAndSwitcher(tb)
        self._indentAct = tb.addWidget(self._indent)
        # Position indicator
        self._pos = editortoolbar.PositionIndicator(tb)
        self._posAct = tb.addWidget(self._pos)

    def del_(self):
        tb = core.mainWindow().topToolBar()
        tb.removeAction(self._eolAct)
        tb.removeAction(self._indentAct)
        tb.removeAction(self._posAct)
        tb.removeAction(self._vimAct)
