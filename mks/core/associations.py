"""
associations --- File -> Programming language associations
==========================================================

Module detects language of a file

It contains functionality to detect file language and for edit association settings
"""

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QWidget, QTreeWidgetItem

from mks.core.core import core, DATA_FILES_PATH
from mks.core.uisettings import ListOnePerLineOption, ModuleConfigurator


class Configurator(ModuleConfigurator):
    """ Module configurator.
    
    Used for configure associations
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        self._options = []
        fileAssociationsItem = dialog.twMenu.topLevelItem(1)
        for index, language in enumerate(core.config()["Associations"].keys()):
            # Item to the tree
            fileAssociationsItem.addChild(QTreeWidgetItem([language]))
            # Widget
            widget = self._createWidget(dialog, language)
            dialog.swPages.insertWidget(index + 2, widget)
            # Options
            option = ListOnePerLineOption(dialog, core.config(), "Associations/%s" % language, widget.pteFileNameGlobs)
            self._options.append(option)

    def _createWidget(self, dialog, language):
        """Create configuration widget
        """
        widget = QWidget(dialog)
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/Associations.ui'), widget)
        return widget
    
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
