"""
assotiations --- File -> Programming language assotiations
==========================================================

Module detects language of a file

It contains functionality to detect file language and for edit assotiation settings
"""

from PyQt4.QtGui import QWidget

from mks.core.core import core
from mks.core.uisettings import ListOnePerLineOption, ModuleConfigurator


class Configurator(ModuleConfigurator):
    """ Module configurator.
    
    Used for configure associations
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        for language in core.config()["Assotiations"].keys():
            dialog.tboxAssociations.addItem(QWidget(), language)
    
    def saveSettings(self):
        pass
    
    def applySettings(self):
        pass

class Assotiations():
    """Module functionality
    """
    def __init__(self):
        core.moduleConfiguratorClasses.append(Configurator)
    
    def __term__(self):
        core.moduleConfiguratorClasses.remove(Configurator)

