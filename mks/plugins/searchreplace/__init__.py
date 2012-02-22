"""
searchreplace --- Search and replace functionality
==================================================

Contains search dialog and search/replace in file/directory functionality
"""

import os.path
import re
import time
import pkgutil
import encodings
import fnmatch

from PyQt4 import uic
from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QAction, QIcon

from mks.core.core import core

ModeFlagSearch = 0x1
ModeFlagReplace = 0x2
ModeFlagFile = 0x4
ModeFlagDirectory = 0x8
ModeFlagProjectFiles = 0x10
ModeFlagOpenedFiles = 0x20

ModeNo = 0
ModeSearch = ModeFlagSearch | ModeFlagFile
ModeReplace = ModeFlagReplace | ModeFlagFile
ModeSearchDirectory = ModeFlagSearch | ModeFlagDirectory
ModeReplaceDirectory = ModeFlagReplace | ModeFlagDirectory
ModeSearchProjectFiles = ModeFlagSearch | ModeFlagProjectFiles
ModeReplaceProjectFiles = ModeFlagReplace | ModeFlagProjectFiles
ModeSearchOpenedFiles = ModeFlagSearch | ModeFlagOpenedFiles
ModeReplaceOpenedFiles = ModeFlagReplace | ModeFlagOpenedFiles


class Plugin(QObject):
    """Main class of the plugin. Installs and uninstalls plugin to the system
    """
    
    def __init__(self):
        """Plugin initialisation
        """
        QObject.__init__(self)
        self.widget = None
        self.dock = None
        actManager = core.actionManager()
        
        self._createdActions = []
        
        def createAction(path, text, icon, shortcut, tooltip, slot, data, enabled=True):  # pylint: disable=R0913
            """Create action object
            """
            actObject = core.actionManager().addAction( 'mNavigation/mSearchReplace/' + path,
                                                        self.tr(text),
                                                        QIcon(':/mksicons/' + icon),
                                                        shortcut)
            actObject.setToolTip(self.tr(tooltip))
            if slot:
                actObject.triggered.connect(slot)
            actObject.setData(data)
            actObject.setEnabled(enabled)
            self._createdActions.append(actObject)

        # List if search actions.
        # First acition created by MainWindow, so, do not fill text
        createAction("aSearchFile", "&Search...", 
                      "search.png", "Ctrl+F",
                      "Search in the current file...", 
                      self._modeSwitchTriggered, ModeSearch)
        createAction("aSearchDirectory", "Search in &Directory...", 
                      "search-replace-directory.png", "Ctrl+Shift+F", 
                      "Search in directory...",
                      self._modeSwitchTriggered, ModeSearchDirectory)
        createAction("aReplaceDirectory", "Replace in Director&y...",
                      "search-replace-directory.png", "Ctrl+Shift+R",
                      "Replace in directory...",
                      self._modeSwitchTriggered, ModeReplaceDirectory)
        createAction("aReplaceFile", "&Replace...",
                      "replace.png", "Ctrl+R",
                      "Replace in the current file...",
                      self._modeSwitchTriggered, ModeReplace)
        createAction("aSearchPrevious", "Search &Previous",
                      "previous.png", "Shift+F3",
                      "Search previous occurrence",
                      None, None,
                      False)  # will be connected to search widget, when it is created
        createAction("aSearchNext", "Search &Next",
                      "next.png", "F3",
                      "Search next occurrence",
                      None, None,
                      False)  # will be connected to search widget, when it is created
        createAction("aSearchOpenedFiles", "Search in &Opened Files...",
                      "search-replace-opened-files.png",
                      "Ctrl+Alt+Meta+F", "Search in opened files...",
                      self._modeSwitchTriggered, ModeSearchOpenedFiles)
        createAction("aReplaceOpenedFiles", "Replace in Open&ed Files...",
                      "search-replace-opened-files.png", "Ctrl+Alt+Meta+R",
                      "Replace in opened files...",
                      self._modeSwitchTriggered, ModeReplaceOpenedFiles)
        #TODO search in project
        #                ("aSearchProjectFiles", "Search in Project &Files...",
        #                "search-replace-project-files.png", "Ctrl+Meta+F",
        #                "Search in the current project files..",
        #                self.modeSwitchTriggered, ModeSearchProjectFiles),
        #                ("aReplaceProjectFiles", "Replace in Projec&t Files...",
        #                "search-replace-project-files.png", "Ctrl+Meta+R",
        #                "Replace in the current project files...",
        #                self.modeSwitchTriggered, ModeReplaceProjectFiles),
    
    def del_(self):
        """Plugin termination
        """
        for action in self._createdActions:
            core.actionManager().removeAction(action)
        if self.dock is not None:
            self.dock.del_()
    
    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return None  # No any settings

    def _modeSwitchTriggered(self):
        """Changing mode, i.e. from "Search file" to "Replace file"
        """
        
        if not self.widget:
            self._createWidgets()
        
        newMode = self.sender().data().toInt()[0]
        if newMode & ModeFlagFile:
            self.widget.setMode(newMode)
        elif newMode & ModeFlagDirectory:
            self.widget.setMode(newMode)
        elif newMode & ModeFlagProjectFiles:
            pass  # TODO search in project support
        elif newMode & ModeFlagOpenedFiles:
            # TODO check if have file based document
            if core.workspace().openedDocuments():
                self.widget.setMode(newMode)
    
    def _createWidgets(self):
        """ Create search widget and dock. Called only when user requested it first time
        """
        import searchwidget
        self.widget = searchwidget.SearchWidget( self )
        core.mainWindow().centralLayout().addWidget( self.widget )
        self.widget.setVisible( False )
        
        # FIXME create dock, only when have some search results!!!
        import searchresultsdock
        self.dock = searchresultsdock.SearchResultsDock( self.widget.searchThread )
        core.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self.dock)
        self.dock.setVisible( False )

        self.widget.setResultsDock( self.dock )
