"""
associations --- Syntax highlighting support
============================================

Functionality:

* Detect programming languge of the file
* Automatically apply it via :func:`mks.core.abstractdocument.AbstractDocument.setHighlightingLanguage` for newly opened editors
* Edit associations settings via GUI
"""

import os.path
import fnmatch

from PyQt4 import uic
from PyQt4.QtCore import QFileInfo
from PyQt4.QtGui import QAction, QIcon, QWidget, QTreeWidgetItem

from mks.core.core import core, DATA_FILES_PATH
from mks.core.uisettings import ListOnePerLineOption, ModuleConfigurator


class Configurator(ModuleConfigurator):
    """ Module configurator.
    
    Used to configure associations on the settings dialogue
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        self._options = []
        fileAssociationsItem = dialog.twMenu.topLevelItem(1)
        for index, language in enumerate(Associations.instance.iterLanguages()):
            languageName, fileNameGlobs, firstLineGlobs, iconPath = language
            # Item to the tree
            item = QTreeWidgetItem([languageName])
            item.setIcon(0, QIcon(iconPath))
            fileAssociationsItem.addChild(item)
            # Widget
            widget = self._createWidget(dialog, languageName)
            dialog.swPages.insertWidget(index + 2, widget)
            # Options
            optionPath = "Associations/%s/FileName" % languageName
            option = ListOnePerLineOption(dialog, core.config(), optionPath, widget.pteFileNameGlobs)
            self._options.append(option)
            optionPath = "Associations/%s/FirstLine" % languageName
            option = ListOnePerLineOption(dialog, core.config(), optionPath, widget.pteFirstLineGlobs)
            self._options.append(option)

    def _createWidget(self, dialog, language):
        """Create configuration widget
        """
        widget = QWidget(dialog)
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/Associations.ui'), widget)
        return widget
    
    def saveSettings(self):
        """Settings are stored in the core configuration file, therefore nothing to do here.
        
        Called by :mod:`mks.core.uisettings`
        """
        pass
    
    def applySettings(self):
        """Apply associations to opened documents.
        
        Called by :mod:`mks.core.uisettings`
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
        
        self._menu = core.actionModel().addMenu("mView/mHighlighting", "Highlighting").menu()
        
        self._menu.aboutToShow.connect(self._onMenuAboutToShow)
        self._menu.aboutToHide.connect(self._menu.clear)
        
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        
        Associations.instance = self
    
    def __term__(self):
        core.moduleConfiguratorClasses.remove(Configurator)

    def iterLanguages(self):
        """Get list of available languages as touple (name, file name globs, first line globs, icon path)
        """
        for languageName, params in core.config()["Associations"].iteritems():
            item = QTreeWidgetItem([languageName])
            iconPath = ":/mksicons/languages/%s.png" % languageName.lower()
            if not QFileInfo(iconPath).exists():
                iconPath = ":/mksicons/transparent.png"
            yield (languageName, params["FileName"], params["FirstLine"], iconPath)

    def applyLanguageToDocument(self, document):
        """Signal handler. Executed when document has been opened. Applyes lexer
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

        for languageName, fileNameGlobs, firstLineGlobs, iconPath in self.iterLanguages():
            for fileNameGlob in fileNameGlobs:
                if fnmatch.fnmatch(fileName, fileNameGlob):
                    return languageName

        firstLine = document.line(0)
        if firstLine is not None:
            for languageName, fileNameGlobs, firstLineGlobs, iconPath in self.iterLanguages():
                for firstLineGlob in firstLineGlobs:
                    if fnmatch.fnmatch(firstLine, firstLineGlob):
                        return languageName

        return None

    def _onMenuAboutToShow(self):
        """View -> Highlighting menu is about to show. Fill it with items
        """
        currentLanguage = core.workspace().currentDocument().highlightingLanguage()
        for languageName, fileNameGlobs, firstLineGlobs, iconPath in self.iterLanguages():
            action = QAction(QIcon(iconPath), languageName, self._menu)
            action.setCheckable(True)
            if languageName == currentLanguage:
                action.setChecked(True)
            self._menu.addAction(action)
        self._menu.triggered.connect(self._onMenuTriggered)
    
    def _onMenuTriggered(self, action):
        """View -> Highlighting -> Some language triggered
        Change current file highlighting mode
        """
        languageName = action.text()
        core.workspace().currentDocument().setHighlightingLanguage(languageName)

    def _onCurrentDocumentChanged(self, old, new):
        """Handler of current document change. Updates View -> Highlighting menu state
        """
        self._menu.setEnabled(new is not None)
