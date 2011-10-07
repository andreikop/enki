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
        """Settings are stored in the core configuration file, therefore nothing to do here
        Called by uisettings TODO documentation link
        """
        pass
    
    def applySettings(self):
        """Apply associations to opened documents.
        Called by uisettings TODO documentation link
        """
        for document in core.workspace().openedDocuments():
            Associations.instance.applyLanguageToDocument(document)

class Associations():
    """Module functionality
    """
    
    instance = None

    def __init__(self):
        core.moduleConfiguratorClasses.append(Configurator)
        core.workspace().documentOpened.connect(self.applyLanguageToDocument)
        Associations.instance = self
    
    def __term__(self):
        core.moduleConfiguratorClasses.remove(Configurator)

    def applyLanguageToDocument(self, document):
        """Signal handler. Executed when document is opened. Applyes lexer
        """
        language = self._getLanguage(document)
        if language:
            document.setHighlightingLanguage(language)

    def _getLanguage(self, document):
        """Get language name by file path
        """
        fileName = document.fileName()

        if not fileName:
            return

        for language, patterns in core.config()["Associations"].iteritems():
            for pattern in patterns:
                if fnmatch.fnmatch(fileName, pattern):
                    return language
        else:
            return None
