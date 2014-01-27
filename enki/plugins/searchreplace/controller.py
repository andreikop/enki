"""
controller --- Main module. Business logic
==========================================

This module implements S&R plugin functionality. It joins together all other modules
"""
import re
import sys

from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QApplication, QAction, QIcon, QMessageBox


from enki.core.core import core
import substitutions

MODE_FLAG_SEARCH = 0x1
MODE_FLAG_REPLACE = 0x2
MODE_FLAG_FILE = 0x4
MODE_FLAG_DIRECTORY = 0x8
MODE_FLAG_FILES = 0x10

MODE_SEARCH = MODE_FLAG_SEARCH | MODE_FLAG_FILE
MODE_REPLACE = MODE_FLAG_REPLACE | MODE_FLAG_FILE
MODE_SEARCH_DIRECTORY = MODE_FLAG_SEARCH | MODE_FLAG_DIRECTORY
MODE_REPLACE_DIRECTORY = MODE_FLAG_REPLACE | MODE_FLAG_DIRECTORY
MODE_SEARCH_OPENED_FILES = MODE_FLAG_SEARCH | MODE_FLAG_FILES
MODE_REPLACE_OPENED_FILES = MODE_FLAG_REPLACE | MODE_FLAG_FILES

# Too many extra se
MAX_EXTRA_SELECTIONS_COUNT = 256


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

        # all matches cache
        self._cachedRegExp = None
        self._cachedText = None
        self._catchedMatches = None

        self._createActions()

        core.workspace().currentDocumentChanged.connect(self._resetSearchInFileStartPoint)
        QApplication.instance().focusChanged.connect(self._resetSearchInFileStartPoint)

    def del_(self):
        """Explicitly called destructor
        """
        if self._searchThread is not None:
            self._searchThread.stop()
        if self._replaceThread is not None:
            self._replaceThread.stop()

        for action in self._createdActions:
            core.actionManager().removeAction(action)
        self._menuSeparator.parent().removeAction(self._menuSeparator)

        if self._dock is not None:
            self._dock.del_()

    def _createActions(self):
        """Create main menu actions
        """
        actManager = core.actionManager()

        self._createdActions = []

        menu = 'mNavigation/mSearchReplace'

        def createAction(path, text, icon, shortcut, tooltip, slot, data, enabled=True):  # pylint: disable=R0913
            """Create action object
            """
            actObject = core.actionManager().addAction( menu + '/' + path,
                                                        self.tr(text),
                                                        QIcon(':/enkiicons/' + icon),
                                                        shortcut)
            actObject.setToolTip(self.tr(tooltip))
            if slot:
                actObject.triggered.connect(slot)
            actObject.setData(data)
            actObject.setEnabled(enabled)
            self._createdActions.append(actObject)

        if sys.platform == 'darwin':
            # Ctrl+, conflicts with "Open preferences"
            searchWordBackwardShortcut, searchWordForwardShortcut = 'Meta+,', 'Meta+.'
        else:
            searchWordBackwardShortcut, searchWordForwardShortcut = 'Ctrl+,', 'Ctrl+.'

        # List if search actions.
        # First acition created by MainWindow, so, do not fill text
        createAction("aSearchFile", "&Search...",
                      "search.png", "Ctrl+F",
                      "Search in the current file...",
                      self._onModeSwitchTriggered, MODE_SEARCH)
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
        createAction("aReplaceFile", "&Replace...",
                      "replace.png", "Ctrl+R",
                      "Replace in the current file...",
                      self._onModeSwitchTriggered, MODE_REPLACE)
        createAction("aSearchWordBackward", "Search word under cursor backward",
                      "less.png", searchWordBackwardShortcut,
                      "",
                      self._onSearchCurrentWordBackward, None)
        createAction("aSearchWordForward", "Search word under cursor forward",
                      "bigger.png", searchWordForwardShortcut,
                      "",
                      self._onSearchCurrentWordForward, None)
        self._menuSeparator = core.actionManager().menu(menu).addSeparator()
        createAction("aSearchDirectory", "Search in &Directory...",
                      "search-replace-directory.png", "Ctrl+Shift+F",
                      "Search in directory...",
                      self._onModeSwitchTriggered, MODE_SEARCH_DIRECTORY)
        createAction("aReplaceDirectory", "Replace in Director&y...",
                      "search-replace-directory.png", "Ctrl+Shift+R",
                      "Replace in directory...",
                      self._onModeSwitchTriggered, MODE_REPLACE_DIRECTORY)
        createAction("aSearchOpenedFiles", "Search in &Opened Files...",
                      "search-replace-opened-files.png",
                      "Ctrl+Alt+Meta+F", "Search in opened files...",
                      self._onModeSwitchTriggered, MODE_SEARCH_OPENED_FILES)
        createAction("aReplaceOpenedFiles", "Replace in Open&ed Files...",
                      "search-replace-opened-files.png", "Ctrl+Alt+Meta+R",
                      "Replace in opened files...",
                      self._onModeSwitchTriggered, MODE_REPLACE_OPENED_FILES)

        am = core.actionManager()
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "/aSearchFile").setEnabled(new is not None))
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "/aReplaceFile").setEnabled(new is not None))
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "/aSearchOpenedFiles").setEnabled(new is not None))
        core.workspace().currentDocumentChanged.connect( \
            lambda old, new: am.action(menu + "/aReplaceOpenedFiles").setEnabled(new is not None))

    def _createSearchWidget(self):
        """ Create search widget. Called only when user requested it first time
        """
        import searchwidget
        self._widget = searchwidget.SearchWidget( self )
        self._widget.searchInDirectoryStartPressed.connect(self._onSearchInDirectoryStartPressed)
        self._widget.searchInDirectoryStopPressed.connect(self._onSearchInDirectoryStopPressed)
        self._widget.replaceCheckedStartPressed.connect(self._onReplaceCheckedStartPressed)
        self._widget.replaceCheckedStopPressed.connect(self._onReplaceCheckedStopPressed)
        self._widget.visibilityChanged.connect(self._updateSearchWidgetFoundItemsHighlighting)

        self._widget.searchRegExpChanged.connect(self._updateFileActionsState)
        self._widget.searchRegExpChanged.connect(self._onRegExpChanged)
        self._widget.searchRegExpChanged.connect(self._updateSearchWidgetFoundItemsHighlighting)

        self._widget.searchNext.connect(self._onSearchNext)
        self._widget.searchPrevious.connect(self._onSearchPrevious)

        self._widget.replaceFileOne.connect(self._onReplaceFileOne)
        self._widget.replaceFileAll.connect(self._onReplaceFileAll)

        core.workspace().currentDocumentChanged.connect(self._updateFileActionsState)  # always disabled, if no widget
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        core.workspace().textChanged.connect(self._updateSearchWidgetFoundItemsHighlighting)

        core.mainWindow().centralLayout().addWidget( self._widget )
        self._widget.setVisible( False )
        self._updateFileActionsState()

    def _createDockWidget(self):
        """Create dock widget, which displays search results.
        Called only when search in direcory process starts
        """
        import searchresultsdock
        self._dock = searchresultsdock.SearchResultsDock(core.mainWindow())

        core.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self._dock)
        self._dock.setVisible( False )
        self._dock.setReplaceMode(self._mode == MODE_REPLACE_DIRECTORY or \
                                  self._mode == MODE_REPLACE_OPENED_FILES)

    def _onModeSwitchTriggered(self):
        """Changing mode, i.e. from "Search file" to "Replace file"
        """
        if not self._widget:
            self._createSearchWidget()

        newMode = self.sender().data()

        if newMode & MODE_FLAG_FILES and \
           not core.workspace().documents():
            return

        self._widget.setMode(newMode)

        if self._searchThread is not None:
            self._searchThread.stop()
        if self._replaceThread is not None:
            self._replaceThread.stop()

        self._mode = newMode

        if self._dock is not None:
            self._dock.setReplaceMode(self._mode == MODE_REPLACE_DIRECTORY or \
                                      self._mode == MODE_REPLACE_OPENED_FILES)

    #
    # Highlight found items with yellow
    #
    def _findAllMatches(self, text, regExp):
        """Find all matces of regExp in text
        This method caches found items for last text and regExp
        """
        if self._cachedText != text or \
           self._cachedRegExp != regExp:
            self._catchedMatches = [match for match in regExp.finditer(text)]
            self._cachedText = text
            self._cachedRegExp = regExp

        return self._catchedMatches

    def _updateSearchWidgetFoundItemsHighlighting(self):
        document = core.workspace().currentDocument()
        if document is None:
            return

        if not self._widget.isVisible() or \
           not self._widget.isSearchRegExpValid()[0] or \
           not self._widget.getRegExp().pattern:
            document.qutepart.setExtraSelections([])
            return

        return self._updateFoundItemsHighlighting(self._widget.getRegExp())

    def _updateFoundItemsHighlighting(self, regExp):
        """(Re)highlight found items with yellow color
        Called by _updateSearchWidgetFoundItemsHighlighting and by word search highlighting
        """
        document = core.workspace().currentDocument()

        matches = self._findAllMatches(document.qutepart.text, regExp)

        if len(matches) <= MAX_EXTRA_SELECTIONS_COUNT:
            selections = [ (match.start(), len(match.group(0))) \
                                for match in matches]
        else:
            selections = []

        document.qutepart.setExtraSelections(selections)

    def _onCurrentDocumentChanged(self, old, new):
        """Current document changed. Clear highlighted items
        """
        if old is not None:
            old.qutepart.setExtraSelections([])

    def _searchInText(self, regExp, text, startPoint, forward):
        """Search in text and return tuple (nearest match, all matches)
        (None, None) if not found
        """
        matches = self._findAllMatches(text, regExp)
        if matches:
            if forward:
                for match in matches:
                    if match.start() >= startPoint:
                        break
                else:  # wrap, search from start
                    match = matches[0]
            else:  # reverse search
                for match in matches[::-1]:
                    if match.start() < startPoint:
                        break
                else:  # wrap, search from end
                    match = matches[-1]
            return match, matches
        else:
            return None, None

    #
    # Search word under cursor
    #
    def _onSearchCurrentWordBackward(self):
        """Search current word backward.
        This search doesn't depend on search widget state, mode and contents
        """
        self._searchWord(forward=False)

    def _onSearchCurrentWordForward(self):
        """Search current word forward.
        This search doesn't depend on search widget state, mode and contents
        """
        self._searchWord(forward=True)

    def _searchWord(self, forward):
        """Do search in file operation. Will select next found item
        if updateWidget is True, search widget line edit will color will be set according to result
        """
        document = core.workspace().currentDocument()

        cursor = document.qutepart.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.WordUnderCursor)
        word = cursor.selectedText()
        wordStartAbsPos = cursor.anchor()
        wordEndAbsPos = cursor.position()

        if not word:
            return

        regExp = re.compile('\\b%s\\b' % re.escape(word))
        text = document.qutepart.text

        # avoid matching word under cursor
        if forward:
            startPoint = wordEndAbsPos
        else:
            startPoint = wordStartAbsPos

        self._updateFoundItemsHighlighting(regExp)

        match, matches = self._searchInText(regExp, document.qutepart.text, startPoint, forward)
        if match is not None:
            document.qutepart.absSelectedPosition = (match.start(), match.start() + len(match.group(0)))
            core.mainWindow().statusBar().showMessage('Match %d of %d' % \
                                                      (matches.index(match) + 1, len(matches)), 3000)
        else:
            core.workspace().currentDocument().qutepart.resetSelection()

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
        valid = valid and len(self._widget.getRegExp().pattern) > 0  # valid and not empty
        searchAvailable = valid

        haveDocument = core.workspace().currentDocument() is not None
        searchInFileAvailable = valid and haveDocument

        self._widget.setSearchInFileActionsEnabled(searchInFileAvailable)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchNext").setEnabled(searchInFileAvailable)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchPrevious").setEnabled(searchInFileAvailable)

        core.actionManager().action("mNavigation/mSearchReplace/aSearchWordBackward").setEnabled(haveDocument)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchWordForward").setEnabled(haveDocument)

    def _onRegExpChanged(self, regExp):
        """Search regExp changed. Do incremental search
        """
        if self._mode in (MODE_SEARCH, MODE_REPLACE) and \
           core.workspace().currentDocument() is not None:
            if regExp.pattern:
                self._searchFile(forward=True, incremental=True )
            else:  # Clear selection
                core.workspace().currentDocument().qutepart.resetSelection()

    def _onSearchNext(self):
        """Search Next clicked
        """
        self._widget.updateComboBoxes()
        self._searchFile(forward=True, incremental=False )

    def _onSearchPrevious(self):
        """Search Previous clicked
        """
        self._widget.updateComboBoxes()
        self._searchFile(forward=False, incremental=False )

    def _searchFile(self, forward=True, incremental=False):
        """Do search in file operation. Will select next found item
        """
        qutepart = core.workspace().currentDocument().qutepart

        regExp = self._widget.getRegExp()

        if qutepart.absCursorPosition != self._searchInFileLastCursorPos:
            self._searchInFileStartPoint = None

        if self._searchInFileStartPoint is None or not incremental:
            # get cursor position
            cursor = qutepart.textCursor()

            if forward:
                if  incremental :
                    self._searchInFileStartPoint = cursor.selectionStart()
                else:
                    self._searchInFileStartPoint = cursor.selectionEnd()
            else:
                self._searchInFileStartPoint = cursor.selectionStart()

        match, matches = self._searchInText(regExp, qutepart.text, self._searchInFileStartPoint, forward)
        if match:
            selectionStart, selectionEnd = match.start(), match.start() + len(match.group(0))
            qutepart.absSelectedPosition = (selectionStart, selectionEnd)
            self._searchInFileLastCursorPos = selectionEnd
            self._widget.setState(self._widget.Good)  # change background acording to result
            core.mainWindow().statusBar().showMessage('Match %d of %d' % \
                                                      (matches.index(match) + 1, len(matches)), 3000)
        else:
            self._widget.setState(self._widget.Bad)
            qutepart.resetSelection()

    def _onReplaceFileOne(self, replaceText):
        """Do one replacement in the file
        """
        self._widget.updateComboBoxes()

        qpart = core.workspace().currentDocument().qutepart
        regExp = self._widget.getRegExp()

        start, end = qpart.absSelectedPosition

        match = regExp.search(qpart.text, start)

        if match is None:
            match = regExp.search(qpart.text, 0)

        if match is not None:
            replaceTextSubed = substitutions.makeSubstitutions(replaceText, match)
            qpart.replaceText(match.start(), len(match.group(0)), replaceTextSubed)
            # move cursor to the end of replaced text
            qpart.absCursorPosition = match.start() + len(replaceTextSubed)
            # move selection to the next item
            self._searchFile(forward=True, incremental=False )
        else:
            self._widget.setState(self._widget.Bad)

    def _onReplaceFileAll(self, replaceText):
        """Do all replacements in the file
        """
        self._widget.updateComboBoxes()

        qpart = core.workspace().currentDocument().qutepart
        regExp = self._widget.getRegExp()

        matches = self._findAllMatches(qpart.text, regExp)
        with qpart:
            for match in matches[::-1]:  # reverse order, because replacement may move indexes
                replaceTextSubed = substitutions.makeSubstitutions(replaceText, match)
                qpart.replaceText(match.start(), len(match.group(0)), replaceTextSubed)

        core.mainWindow().statusBar().showMessage( self.tr( "%d match(es) replaced." % len(matches) ), 3000 )

    #
    # Search in directory (with thread)
    #

    def _onSearchInDirectoryStartPressed(self, regExp, mask, path):
        """Handler for 'search in directory' action
        """
        self._widget.updateComboBoxes()

        if self._dock is None:
            self._createDockWidget()

        from threads import SearchThread
        self._searchThread = SearchThread()
        self._searchThread.progressChanged.connect(self._widget.onSearchProgressChanged)
        self._searchThread.resultsAvailable.connect(self._dock.appendResults)
        self._searchThread.finished.connect(self._onSearchThreadFinished)
        self._searchThread.error.connect(self._onThreadError)

        inOpenedFiles = self._mode in (MODE_SEARCH_OPENED_FILES, MODE_REPLACE_OPENED_FILES,)

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
        self._widget.updateComboBoxes()

        if self._dock is None:  # no any results
            return

        from threads import ReplaceThread
        self._replaceThread = ReplaceThread()
        self._replaceThread.resultsHandled.connect(self._dock.onResultsHandledByReplaceThread)
        self._replaceThread.error.connect(self._onThreadError)
        self._replaceThread.finalStatus.connect(self._onReplaceThreadFinalStatus)

        self._replaceThread.replace( self._dock.getCheckedItems(),
                                     replaceText)

    def _onReplaceCheckedStopPressed(self):
        """Handler for 'stop replacing checked' action
        """
        if self._replaceThread is not None:
            self._replaceThread.stop()

    def _onThreadError(self, error ):
        """Error message from the replace thread
        """
        core.mainWindow().appendMessage( error )

    def _onReplaceThreadFinished(self):
        """Handler for replace in directory finished event
        """
        self._widget.setReplaceInProgress(False)

    def _onReplaceThreadFinalStatus(self, message):
        """Show replace thread status on status bar
        """
        core.mainWindow().statusBar().showMessage(message, 3000)
