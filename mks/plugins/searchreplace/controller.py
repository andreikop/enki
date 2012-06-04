"""
controller --- Main module. Business logic
==========================================

This module implements S&R plugin functionality. It joins together all other modules
"""


from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QApplication, QAction, QIcon, QMessageBox


from mks.core.core import core

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
        self._searchThread = None
        self._replaceThread = None
        self._widget = None
        self._dock = None
        self._searchInFileStartPoint = None
        self._searchInFileLastCursorPos = None
        self._createActions()
        
        core.workspace().currentDocumentChanged.connect(self._resetSearchInFileStartPoint)
        QApplication.instance().focusChanged.connect(self._resetSearchInFileStartPoint)
        # QScintilla .cursorPositionChanged is emitted with delay.

    def del_(self):
        """Explicitly called destructor
        """
        for action in self._createdActions:
            core.actionManager().removeAction(action)
        if self._dock is not None:
            self._dock.del_()

    def _createActions(self):
        """Create main menu actions
        """
        actManager = core.actionManager()
        
        self._createdActions = []
        
        menu = 'mNavigation/mSearchReplace/'
        
        def createAction(path, text, icon, shortcut, tooltip, slot, data, enabled=True):  # pylint: disable=R0913
            """Create action object
            """
            actObject = core.actionManager().addAction( menu + path,
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
                      self._onSearchPrevious, None,
                      False)  # will be connected to search widget, when it is created
        createAction("aSearchNext", "Search &Next",
                      "next.png", "F3",
                      "Search next occurrence",
                      self._onSearchNext, None,
                      False)  # will be connected to search widget, when it is created
        createAction("aSearchOpenedFiles", "Search in &Opened Files...",
                      "search-replace-opened-files.png",
                      "Ctrl+Alt+Meta+F", "Search in opened files...",
                      self._onModeSwitchTriggered, ModeSearchOpenedFiles)
        createAction("aReplaceOpenedFiles", "Replace in Open&ed Files...",
                      "search-replace-opened-files.png", "Ctrl+Alt+Meta+R",
                      "Replace in opened files...",
                      self._onModeSwitchTriggered, ModeReplaceOpenedFiles)
        
        am = core.actionManager()
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "aSearchFile").setEnabled(new is not None))
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "aReplaceFile").setEnabled(new is not None))
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "aSearchOpenedFiles").setEnabled(new is not None))
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "aReplaceOpenedFiles").setEnabled(new is not None))

    def _createSearchWidget(self):
        """ Create search widget. Called only when user requested it first time
        """
        import searchwidget
        self._widget = searchwidget.SearchWidget( self )
        self._widget.searchInDirectoryStartPressed.connect(self._onSearchInDirectoryStartPressed)
        self._widget.searchInDirectoryStopPressed.connect(self._onSearchInDirectoryStopPressed)
        self._widget.replaceCheckedStartPressed.connect(self._onReplaceCheckedStartPressed)
        self._widget.replaceCheckedStopPressed.connect(self._onReplaceCheckedStopPressed)
        
        self._widget.searchRegExpChanged.connect(self._updateFileActionsState)
        self._widget.searchRegExpChanged.connect(self._onRegExpChanged)
        
        self._widget.searchNext.connect(self._onSearchNext)
        self._widget.searchPrevious.connect(self._onSearchPrevious)
        
        self._widget.replaceFileOne.connect(self._onReplaceFileOne)
        self._widget.replaceFileAll.connect(self._onReplaceFileAll)
        
        core.workspace().currentDocumentChanged.connect(self._updateFileActionsState)  # always disabled, if no widget

        core.mainWindow().centralLayout().addWidget( self._widget )
        self._widget.setVisible( False )
        self._updateFileActionsState()

    def _createDockWidget(self):
        """Create dock widget, which displays search results.
        Called only when search in direcory process starts
        """
        import searchresultsdock
        self._dock = searchresultsdock.SearchResultsDock()

        core.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self._dock)
        self._dock.setVisible( False )
        self._dock.setReplaceMode(self._mode == ModeReplaceDirectory or \
                                  self._mode == ModeReplaceOpenedFiles)

    def _onModeSwitchTriggered(self):
        """Changing mode, i.e. from "Search file" to "Replace file"
        """
        if not self._widget:
            self._createSearchWidget()
        
        newMode = self.sender().data().toInt()[0]
        
        if newMode & ModeFlagOpenedFiles and \
           not core.workspace().documents():
            return
        
        self._widget.setMode(newMode)
        
        if self._searchThread is not None:
            self._searchThread.stop()
        if self._replaceThread is not None:
            self._replaceThread.stop()

        #self._resetSearchInFileStartPoint()

        self._mode = newMode
        
        if self._dock is not None:
            self._dock.setReplaceMode(self._mode == ModeReplaceDirectory or \
                                      self._mode == ModeReplaceOpenedFiles)
            

    #
    # Search and replace in file
    #
    
    def _resetSearchInFileStartPoint(self):
        """Reset the start point.
        Something changed, restart the search process
        """
        self._searchInFileStartPoint = None

    def _updateFileActionsState(self):
        """Update actions enabled/disabled state.
        Called if current document had been changed or if reg exp had been changed
        """
        valid, error = self._widget.isSearchRegExpValid()
        searchAvailable = valid 
        searchInFileAvailable = valid and core.workspace().currentDocument() is not None
        
        self._widget.setSearchInFileActionsEnabled(searchInFileAvailable)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchNext").setEnabled(searchInFileAvailable)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchPrevious").setEnabled(searchInFileAvailable)

    def _onRegExpChanged(self, regExp):
        """Search regExp changed. Do incremental search
        """
        if self._mode in (ModeSearch, ModeReplace) and \
           core.workspace().currentDocument() is not None:
            if regExp.pattern:
                self._searchFile( forward=True, incremental=True )
            else:  # Clear selection
                line, column = core.workspace().currentDocument().cursorPosition()
                core.workspace().currentDocument().goTo(line=line, column=column)

    def _onSearchNext(self):
        """Search Next clicked
        """
        self._searchFile( forward=True, incremental=False )

    def _onSearchPrevious(self):
        """Search Previous clicked
        """
        self._searchFile( forward=False, incremental=False )

    def _searchFile(self, forward, incremental=False):
        """Do search in file operation. Will select next found item
        """
        document = core.workspace().currentDocument()
        regExp = self._widget.getRegExp()

        if document.absCursorPosition() != self._searchInFileLastCursorPos:
            self._searchInFileStartPoint = None
        
        if self._searchInFileStartPoint is None or not incremental:
            # get cursor position        
            start, end = document.absSelection()

            if start is None:
                start = 0
                end = 0
        
            if forward:
                if  incremental :
                    self._searchInFileStartPoint = start
                else:
                    self._searchInFileStartPoint = end
            else:
                self._searchInFileStartPoint = start
        
        matches = [m for m in regExp.finditer(document.text())]
        if matches:
            if forward:
                matchesAfter = [match for match in matches \
                                    if match.start() >= self._searchInFileStartPoint]
                if matchesAfter:
                    match = matchesAfter[0]
                else:  # wrap, search from start
                    match = matches[0]
            else:  # reverse search
                matchesBefore = [match for match in matches \
                                    if match.start() < self._searchInFileStartPoint]
                if matchesBefore:
                    match = matchesBefore[-1]
                else:  # wrap, search from end
                    match = matches[-1]
            
            document.goTo(absPos = match.start(), selectionLength = len(match.group(0)))
            self._searchInFileLastCursorPos = match.start()
            self._widget.setState(self._widget.Good)  # change background acording to result
            core.mainWindow().statusBar().showMessage('Match %d of %d' % \
                                                      (matches.index(match) + 1, len(matches)), 3000)
        else:
            self._widget.setState(self._widget.Bad)

    def _onReplaceFileOne(self, replaceText):
        """Do one replacement in the file
        """
        document = core.workspace().currentDocument()
        regExp = self._widget.getRegExp()

        start, end = document.absSelection()  # pylint: disable=W0612
        if start is None:
            start = 0
        
        match = regExp.search(document.text(), start)
        
        if match is None:
            match = regExp.search(document.text(), 0)
        
        if match is not None:
            document.goTo(absPos = match.start(), selectionLength = len(match.group(0)))
            try:
                replaceTextSubed = regExp.sub(replaceText, match.group(0))
            except re.error, ex:
                message = unicode(ex.message, 'utf_8')
                message += r'. Probably <i>\group_index</i> used in replacement string, but such group not found. '\
                           r'Try to escape it: <i>\\group_index</i>'
                QMessageBox.critical(None, "Invalid replace string", message)
                # TODO link to replace help
                return
            document.replaceSelectedText(replaceTextSubed)
            document.goTo(absPos = match.start() + len(replaceTextSubed))
            self._searchFile( True, False )  # move selection to the next item
        else:
            self._widget.setState(self._widget.Bad)

    def _onReplaceFileAll(self, replaceText):
        """Do all replacements in the file
        """
        document = core.workspace().currentDocument()
        regExp = self._widget.getRegExp()

        oldPos = document.absCursorPosition()
        
        document.beginUndoAction()
        
        pos = 0
        count = 0
        match = regExp.search(document.text(), pos)
        while match is not None:
            document.goTo(absPos = match.start(), selectionLength = len(match.group(0)))
            replaceTextSubed = regExp.sub(replaceText, match.group(0))
            document.replaceSelectedText(replaceTextSubed)
            
            count += 1
            
            pos = match.start() + len(replaceTextSubed)
            
            if not match.group(0) and not replText:  # avoid freeze when replacing empty with empty
                pos  += 1
            if pos < len(document.text()):
                match = regExp.search(document.text(), pos)
            else:
                match = None

        document.endUndoAction()
        
        if oldPos is not None:
            document.setCursorPosition(absPos = oldPos) # restore cursor position
        core.mainWindow().statusBar().showMessage( self.tr( "%d match(es) replaced." % count ), 3000 )
    
    #
    # Search in directory (with thread)
    #

    def _onSearchInDirectoryStartPressed(self, regExp, mask, path):
        """Handler for 'search in directory' action
        """ 
        if self._dock is None:
            self._createDockWidget()
        
        from threads import SearchThread
        self._searchThread = SearchThread()
        self._searchThread.progressChanged.connect(self._widget.onSearchProgressChanged)
        self._searchThread.resultsAvailable.connect(self._dock.appendResults)
        self._searchThread.finished.connect(self._onSearchThreadFinished)
        
        inOpenedFiles = self._mode in (ModeSearchOpenedFiles, ModeReplaceOpenedFiles,)
        
        self._widget.setSearchInProgress(True)
        self._dock.clear()
        self._searchThread.search( regExp,
                                   mask,
                                   inOpenedFiles,
                                   path)

    def _onSearchInDirectoryStopPressed(self):
        """Handler for 'search in directory' action
        """
        if self._searchThread is not None:
            self._searchThread.stop()

    def _onSearchThreadFinished(self):
        """Handler for search in directory finished signal
        """
        self._widget.setSearchInProgress(False)
        matchesCount = self._dock.matchesCount()
        if matchesCount:
            core.mainWindow().statusBar().showMessage('%d matches ' % matchesCount, 3000)
        else:
            core.mainWindow().statusBar().showMessage('Nothing found', 3000)
    
    #
    # Replace in directory (with thread)
    #

    def _onReplaceCheckedStartPressed(self, replaceText):
        """Handler for 'replace checked' action
        """
        if self._dock is None:  # no any results
            return

        from threads import ReplaceThread 
        self._replaceThread = ReplaceThread()
        self._replaceThread.resultsHandled.connect(self._dock.onResultsHandledByReplaceThread)
        self._replaceThread.openedFileHandled.connect(self._onReplaceThreadOpenedFileHandled)
        self._replaceThread.error.connect(self._onReplaceThreadError)
        self._replaceThread.finalStatus.connect(self._onReplaceThreadFinalStatus)

        self._replaceThread.replace( self._dock.getCheckedItems(),
                                     replaceText)

    def _onReplaceCheckedStopPressed(self):
        """Handler for 'stop replacing checked' action
        """
        if self._replaceThread is not None:
            self._replaceThread.stop()

    def _onReplaceThreadError(self, error ):
        """Error message from the replace thread
        """
        core.mainWindow().appendMessage( error )

    def _onReplaceThreadOpenedFileHandled(self, fileName, content):
        """Replace thread processed currently opened file,
        need update text in the editor
        """
        document = core.workspace().openFile(fileName)
        document.replace(content, startAbsPos=0, endAbsPos=len(document.text()))
    
    def _onReplaceThreadFinished(self):
        """Handler for replace in directory finished event
        """
        self._widget.setReplaceInProgress(False)

    def _onReplaceThreadFinalStatus(self, message):
        """Show replace thread status on status bar
        """
        core.mainWindow().statusBar().showMessage(message, 3000)
