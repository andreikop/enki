"""
associations --- Syntax highlighting support
============================================

Functionality:

* Detect programming languge of the file
* Automatically apply it via :func:`mks.core.abstractdocument.AbstractDocument.setHighlightingLanguage` 
  for newly opened editors
* Edit associations settings via GUI
"""

import os.path
import fnmatch

from PyQt4 import uic
from PyQt4.QtCore import QFileInfo
from PyQt4.QtGui import QAction, QIcon, QWidget, QTreeWidgetItem

from mks.core.core import core
from mks.core.uisettings import ListOnePerLineOption, ModuleConfigurator


class Configurator(ModuleConfigurator):
    """ Module configurator.
    
    Used to configure associations on the settings dialogue
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        self._options = []
        for index, language in enumerate(Plugin.instance.iterLanguages()):
            languageName, fileNameGlobs, firstLineGlobs, iconPath = language  # pylint: disable=W0612
            # Widget
            widget = self._createWidget(dialog)
            dialog.appendPage(u"File associations/%s" % languageName, widget, QIcon(iconPath))
            # Options
            optionPath = "Associations/%s/FileName" % languageName
            option = ListOnePerLineOption(dialog, core.config(), optionPath, widget.pteFileNameGlobs)
            self._options.append(option)
            optionPath = "Associations/%s/FirstLine" % languageName
            option = ListOnePerLineOption(dialog, core.config(), optionPath, widget.pteFirstLineGlobs)
            self._options.append(option)

    def _createWidget(self, dialog):
        """Create configuration widget
        """
        widget = QWidget(dialog)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Associations.ui'), widget)
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
        for document in core.workspace().documents():
            Plugin.instance.applyLanguageToDocument(document)

class Plugin():
    """Module functionality
    """
    
    instance = None

    def __init__(self):
        core.workspace().documentOpened.connect(self.applyLanguageToDocument)
        
        self._menu = core.actionManager().addMenu("mView/mHighlighting", "Highlighting").menu()
        
        self._menu.aboutToShow.connect(self._onMenuAboutToShow)
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        core.workspace().modifiedChanged.connect(self._onDocumentModifiedChanged)
        
        Plugin.instance = self

    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return Configurator
    
    def del_(self):
        """Plugin termination
        """
        core.actionManager().removeMenu("mView/mHighlighting")

    def iterLanguages(self):
        """Get list of available languages as tuple (name, file name globs, first line globs, icon path)
        """
        for languageName, params in core.config()["Associations"].iteritems():
            QTreeWidgetItem([languageName])
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
    
    def _onDocumentModifiedChanged(self, document, modified):
        """Signal handler. Try to redetect language, if document has been changed
        """
        if modified:
            return
        
        if not hasattr(document, "languageIsManualySet"):
            self.applyLanguageToDocument(document)

    def _getLanguage(self, document):
        """Get language name by file path
        """
        fileName = document.fileName()

        if not fileName:
            return

        for languageName, fileNameGlobs, firstLineGlobs, iconPath in self.iterLanguages():  # pylint: disable=W0612
            for fileNameGlob in fileNameGlobs:
                # Empty patterns are ignored
                if fileNameGlob and \
                    fnmatch.fnmatch(fileName, fileNameGlob):
                    return languageName

        firstLine = document.line(0).strip()  # first line without \n and other spaces
        if firstLine is not None:
            for languageName, fileNameGlobs, firstLineGlobs, iconPath in self.iterLanguages():
                for firstLineGlob in firstLineGlobs:
                    # Empty patterns are ignored
                    if firstLineGlob and \
                       fnmatch.fnmatch(firstLine, firstLineGlob):
                        return languageName

        return None

    def _onMenuAboutToShow(self):
        """View -> Highlighting menu is about to show. Fill it with items
        """
        self._menu.clear()
        currentLanguage = core.workspace().currentDocument().highlightingLanguage()
        for languageName, fileNameGlobs, firstLineGlobs, iconPath in self.iterLanguages():  # pylint: disable=W0612
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
        document = core.workspace().currentDocument()
        document.setHighlightingLanguage(languageName)
        document.languageIsManualySet = True

    def _onCurrentDocumentChanged(self, old, new):  # pylint: disable=W0613
        """Handler of current document change. Updates View -> Highlighting menu state
        """
        self._menu.setEnabled(new is not None)
