"""
controller --- Main module. Business logic
==========================================

This module implements S&R plugin functionality. It joins together all other modules
"""


from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QAction, QIcon

from mks.core.core import core

from threads import SearchThread, ReplaceThread  # TODO why it is created here???

ModeFlagSearch = 0x1
ModeFlagReplace = 0x2
ModeFlagFile = 0x4
ModeFlagDirectory = 0x8
ModeFlagOpenedFiles = 0x10

ModeSearch = ModeFlagSearch | ModeFlagFile
ModeReplace = ModeFlagReplace | ModeFlagFile
ModeSearchDirectory = ModeFlagSearch | ModeFlagDirectory
ModeReplaceDirectory = ModeFlagReplace | ModeFlagDirectory
ModeSearchOpenedFiles = ModeFlagSearch | ModeFlagOpenedFiles
ModeReplaceOpenedFiles = ModeFlagReplace | ModeFlagOpenedFiles


class Controller(QObject):
    """S&R module business logic
    """
    def __init__(self):
        QObject.__init__(self)
        self._mode = None
        self.widget = None  # FIXME make private
        self.dock = None # FIXME make private
        self._createActions()
        
        self._searchThread = SearchThread()  # FIXME delayed initialisation


    def del_(self):
        """Explicitly called destructor
        """
        for action in self._createdActions:
            core.actionManager().removeAction(action)
        if self.dock is not None:
            self.dock.del_()

    def _createActions(self):
        """Create main menu actions
        """
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
                      self._onModeSwitchTriggered, ModeSearch)
        createAction("aSearchDirectory", "Search in &Directory...", 
                      "search-replace-directory.png", "Ctrl+Shift+F", 
                      "Search in directory...",
                      self._onModeSwitchTriggered, ModeSearchDirectory)
        createAction("aReplaceDirectory", "Replace in Director&y...",
                      "search-replace-directory.png", "Ctrl+Shift+R",
                      "Replace in directory...",
                      self._onModeSwitchTriggered, ModeReplaceDirectory)
        createAction("aReplaceFile", "&Replace...",
                      "replace.png", "Ctrl+R",
                      "Replace in the current file...",
                      self._onModeSwitchTriggered, ModeReplace)
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
                      self._onModeSwitchTriggered, ModeSearchOpenedFiles)
        createAction("aReplaceOpenedFiles", "Replace in Open&ed Files...",
                      "search-replace-opened-files.png", "Ctrl+Alt+Meta+R",
                      "Replace in opened files...",
                      self._onModeSwitchTriggered, ModeReplaceOpenedFiles)

    def _onModeSwitchTriggered(self):
        """Changing mode, i.e. from "Search file" to "Replace file"
        """
        
        if not self.widget:
            self._createWidgets()
        
        newMode = self.sender().data().toInt()[0]
        
        if newMode & ModeFlagOpenedFiles and \
           not core.workspace().openedDocuments():
            return
        
        self.widget.setMode(newMode)
        
        self._searchThread.stop()
        
        self._mode = newMode
    
    def _createWidgets(self):
        """ Create search widget and dock. Called only when user requested it first time
        """
        import searchwidget
        self.widget = searchwidget.SearchWidget( self )
        self.widget.searchInDirectoryStartPressed.connect(self._onSearchInDirectoryStartPressed)
        self.widget.searchInDirectoryStopPressed.connect(self._onSearchInDirectoryStopPressed)

        # FIXME to thread creation
        self._searchThread.finished.connect(self._onSearchThreadFinished)
        self._searchThread.progressChanged.connect(\
                                        self.widget.onSearchProgressChanged)

        core.mainWindow().centralLayout().addWidget( self.widget )
        self.widget.setVisible( False )
        
        # FIXME create dock, only when have some search results!!!
        import searchresultsdock
        self.dock = searchresultsdock.SearchResultsDock()
        self._searchThread.resultsAvailable.connect(self.dock.appendResults)

        core.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self.dock)
        self.dock.setVisible( False )

        self.widget.setResultsDock( self.dock )
    
    def _onSearchInDirectoryStartPressed(self, regEx, mask, path):
        """Handler for 'search in directory' action
        """
        inOpenedFiles = self._mode in (ModeSearchOpenedFiles, ModeReplaceOpenedFiles,)
        forReplace = self._mode & ModeFlagReplace
        self.widget.setSearchInProgress(True)
        self.dock.clear()
        self._searchThread.search( regEx,
                                   mask,
                                   inOpenedFiles,
                                   forReplace,
                                   path)

    def _onSearchInDirectoryStopPressed(self):
        """Handler for 'search in directory' action
        """
        self._searchThread.stop()

    def _onSearchThreadFinished(self):
        """Handler for search in directory finished
        """
        self.widget.setSearchInProgress(False)