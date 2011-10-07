"""
associations --- File -> Programming language associations
==========================================================

Module detects language of a file

It contains functionality to detect file language and for edit association settings
"""

import os.path
import fnmatch

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
        for index, language in enumerate(core.config()["Associations"].iterkeys()):
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
        core.workspace().documentOpened.connect(self._onDocumentOpened)
    
    def __term__(self):
        core.moduleConfiguratorClasses.remove(Configurator)

    def _onDocumentOpened(self, document):
        """Signal handler. Executed when document is opened. Applyes lexer
        """
        language = self._getLanguage(document.filePath())
        if language:
            document.setHighlightingLanguage(language)

    def _getLanguage(self, filePath):
        """Get language name by file path
        """
        if not filePath:  #  None or empty
            return None
        fileName = os.path.basename(filePath)
        for language, patterns in core.config()["Associations"].iteritems():
            for pattern in patterns:
                if fnmatch.fnmatch(fileName, pattern):
                    return language
        else:
            return None
