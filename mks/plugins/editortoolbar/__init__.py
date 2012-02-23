"""
editortoolbar --- Shows position, save state, EOL and indent
============================================================

It also allows to change this parameters and save the file

File contains integration with the core
"""

from mks.core.core import core

from editortoolbar import EditorToolBar

class Plugin:
    """Plugin interface implementation
    
    Installs and removes editor from the system
    """
    def __init__(self):
        statusBar = core.mainWindow().statusBar()
        self._editorToolBar = EditorToolBar(statusBar)
        statusBar.addPermanentWidget(self._editorToolBar)
    
    def __del__(self):
        del self._editorToolBar

    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return None  # No any settings
