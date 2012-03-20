"""
editortoolbar --- Shows position, save state, EOL and indent
============================================================

It also allows to change this parameters and save the file

File contains integration with the core
"""

from mks.core.core import core
import editortoolbar

class Plugin:
    """Plugin interface implementation
    
    Installs and removes editor from the system
    """
    def __init__(self):
        tb = core.mainWindow().topToolBar()
        self._sep = tb.addSeparator()
        # Modified button
        tb.addAction(core.actionManager().action( "mFile/mSave/aCurrent" ))
        # EOL indicator and switcher
        self._eol = editortoolbar.EolIndicatorAndSwitcher(tb)
        tb.addWidget(self._eol)
        # Indentation indicator and switcher        
        self._indent = editortoolbar.IndentIndicatorAndSwitcher(tb)
        tb.addWidget(self._indent)
        # Position indicator
        self._pos = editortoolbar.PositionIndicator(tb)
        tb.addWidget(self._pos)
    
    def del_(self):
        tb = core.mainWindow().topToolBar()
        tb.removeAction(core.actionManager().action( "mFile/mSave/aCurrent" ))
        tb.removeAction(self._sep)
        self._eol.deleteLater()
        self._indent.deleteLater()
        self._pos.deleteLater()

    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return None  # No any settings
