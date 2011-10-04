"""
associations --- File -> Programming language associations
==========================================================

Module detects language of a file

It contains functionality to detect file language and for edit association settings
"""

from PyQt4.QtGui import QLabel

from mks.core.core import core
from mks.core.uisettings import ListOnePerLineOption, ModuleConfigurator


class Configurator(ModuleConfigurator):
    """ Module configurator.
    
    Used for configure associations
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        dialog.tboxAssociations.removeItem(0)
        for language in core.config()["Associations"].keys():
            widget = QLabel(language)
            dialog.tboxAssociations.addItem(widget, language)
    
    def saveSettings(self):
        pass
    
    def applySettings(self):
        pass

class Associations():
    """Module functionality
    """
    def __init__(self):
        core.moduleConfiguratorClasses.append(Configurator)
    
    def __term__(self):
        core.moduleConfiguratorClasses.remove(Configurator)
