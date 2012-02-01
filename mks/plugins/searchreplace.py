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
from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QDir, QEvent, \
                         QModelIndex, \
                         QObject, QRect, QSize, Qt, \
                         QThread, QVariant
from PyQt4.QtGui import QAction, QCompleter, QDirModel, QFileDialog,  \
                        QFrame, QFileDialog, QHBoxLayout, QIcon, \
                        QMessageBox, \
                        QPainter,  \
                        QPalette, \
                        QProgressBar, QToolButton, QTreeView, QWidget
from mks.fresh.dockwidget.pDockWidget import pDockWidget

from mks.core.core import core, DATA_FILES_PATH

def _isBinary(fileObject):
    """Expects, that file position is 0, when exits, file position is 0
    """
    binary = '\0' in fileObject.read( 4096 )
    fileObject.seek(0)
    return binary


class Plugin(QObject):
    """Main class of the plugin. Installs and uninstalls plugin to the system
    """
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
    
    def __init__(self):
        """Plugin initialisation
        """
        QObject.__init__(self)
        self.widget = None
        self.dock = None
        model = core.actionModel()
        
        self._createdActions = []
        
        def createAction(path, text, icon, shortcut, tooltip, slot, data, enabled=True):  # pylint: disable=R0913
            """Create action object
            """
            actObject = model.addAction( 'mNavigation/mSearchReplace/' + path,
                                         self.tr(text),
                                         QIcon(':/mksicons/' + icon))
            actObject.setShortcut(self.tr(shortcut))
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
                      self._modeSwitchTriggered, self.ModeSearch)
        createAction("aSearchDirectory", "Search in &Directory...", 
                      "search-replace-directory.png", "Ctrl+Shift+F", 
                      "Search in directory...",
                      self._modeSwitchTriggered, self.ModeSearchDirectory)
        createAction("aReplaceDirectory", "Replace in Director&y...",
                      "search-replace-directory.png", "Ctrl+Shift+R",
                      "Replace in directory...",
                      self._modeSwitchTriggered, self.ModeReplaceDirectory)
        createAction("aReplaceFile", "&Replace...",
                      "replace.png", "Ctrl+R",
                      "Replace in the current file...",
                      self._modeSwitchTriggered, self.ModeReplace)
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
                      self._modeSwitchTriggered, self.ModeSearchOpenedFiles)
        createAction("aReplaceOpenedFiles", "Replace in Open&ed Files...",
                      "search-replace-opened-files.png", "Ctrl+Alt+Meta+R",
                      "Replace in opened files...",
                      self._modeSwitchTriggered, self.ModeReplaceOpenedFiles)
        #TODO search in project
        #                ("aSearchProjectFiles", "Search in Project &Files...",
        #                "search-replace-project-files.png", "Ctrl+Meta+F",
        #                "Search in the current project files..",
        #                self.modeSwitchTriggered, self.ModeSearchProjectFiles),
        #                ("aReplaceProjectFiles", "Replace in Projec&t Files...",
        #                "search-replace-project-files.png", "Ctrl+Meta+R",
        #                "Replace in the current project files...",
        #                self.modeSwitchTriggered, self.ModeReplaceProjectFiles),
    
    def del_(self):
        """Plugin termination
        """
        for action in self._createdActions:
            core.actionModel().removeAction(action)
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
        if newMode & Plugin.ModeFlagFile:
            self.widget.setMode(newMode)
        elif newMode & Plugin.ModeFlagDirectory:
            self.widget.setMode(newMode)
        elif newMode & Plugin.ModeFlagProjectFiles:
            pass  # TODO search in project support
        elif newMode & Plugin.ModeFlagOpenedFiles:
            # TODO check if have file based document
            if core.workspace().openedDocuments():
                self.widget.setMode(newMode)
    
    def _createWidgets(self):
        """ Create search widget and dock. Called only when user requested it first time
        """
        self.widget = SearchWidget( self )
        core.mainWindow().centralLayout().addWidget( self.widget )
        self.widget.setVisible( False )
        
        # FIXME create dock, only when have some search results!!!
        self.dock = SearchResultsDock( self.widget.searchThread )
        core.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self.dock)
        self.dock.setVisible( False )

        self.widget.setResultsDock( self.dock )

class SearchContext:
    """Structure holds parameters of search or replace operation in progress
    """    
    def __init__(self, regExp, replaceText, searchPath, mode, encoding):  # pylint: disable=R0913
        self.mask = []
        self.openedFiles = {}
        self.regExp = regExp
        self.replaceText = replaceText
        self.searchPath = searchPath
        self.mode = mode
        self.encoding = encoding


class SearchWidget(QFrame):
    """Widget, appeared, when Ctrl+F pressed.
    Has different forms for different search modes
    """

    Normal = 'normal'
    Good = 'good'
    Bad = 'bad'
    Incorrect = 'incorrect'

    def __init__(self, plugin):
        QFrame.__init__(self, core.workspace())
        self._mode = None
        self.plugin = plugin
        uic.loadUi(os.path.join(DATA_FILES_PATH,
                   'ui/SearchWidget.ui'),
                   self)
        
        self.cbSearch.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.cbReplace.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.fsModel = QDirModel(self.cbPath.lineEdit())
        self.fsModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self.cbPath.lineEdit().setCompleter(QCompleter(self.fsModel,
                                                       self.cbPath.lineEdit() ))
        # TODO QDirModel is deprecated but QCompleter does not yet handle
        # QFileSystemodel - please update when possible."""
        self.cbMask.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.pbSearchStop.setVisible( False )
        self.pbReplaceCheckedStop.setVisible( False )
        
        self._progress = QProgressBar( self )
        self._progress.setAlignment( Qt.AlignCenter )
        self._progress.setToolTip( self.tr( "Search in progress..." ) )
        self._progress.setMaximumSize( QSize( 80, 16 ) )
        core.mainWindow().statusBar().insertPermanentWidget( 0, self._progress )
        self._progress.setVisible( False )
        
        # threads
        self.searchThread = SearchThread()
        self._replaceThread = ReplaceThread()

        self._dock = None
        
        # mode actions
        self.tbMode = QToolButton( self.cbSearch.lineEdit() )
        self.tbMode.setIcon( QIcon( ":/mksicons/misc.png" ) )
        self.tbMode.setPopupMode( QToolButton.InstantPopup )
        self.tbMode.setMenu( core.actionModel().\
                action( "mNavigation/mSearchReplace" ).menu() )
        self.tbMode.setCursor( Qt.ArrowCursor )
        self.tbMode.installEventFilter( self )
        
        # cd up action
        self.tbCdUp = QToolButton( self.cbPath.lineEdit() )
        self.tbCdUp.setIcon( QIcon( ":/mksicons/go-up.png" ) )
        self.tbCdUp.setCursor( Qt.ArrowCursor )
        self.tbCdUp.installEventFilter( self )

        QWidget.setTabOrder(self.cbSearch, self.cbReplace)
        QWidget.setTabOrder(self.cbReplace, self.cbPath)
        
        #TODO PasNox, check if we need this on Mac
        # mac
        #pMonkeyStudio.showMacFocusRect( self, False, True )
        #pMonkeyStudio.setMacSmallSize( self, True, True )
        #ifdef Q_OS_MAC
        # QSize size( 12, 12 )
        #
        #foreach ( QAbstractButton* button, findChildren<QAbstractButton*>() )
        #    button.setIconSize( size )
        #    button.setFixedHeight( 24 )
        #vlMain.setSpacing( 0 )
        #endif
        
        # TODO mask tooltip
        #languages = pMonkeyStudio.availableLanguages()
        #
        #for ( i = 0; i < languages.count(); i += 10 )
        #    languages[ i ].prepend( "\n" )
        #maskToolTip = self.tr( "Space separated list of wildcards, *.h *.cpp 
        #file???.txt\n"
        #"You can use language name too so the search will only apply to 
        #the language suffixes.\n"
        #"Available languages: %1" ).arg( languages.join( ", " ) )
        # self.cbMask.setToolTip( maskToolTip )
        
        
        #TODO support encodings
        #falsePositives = set(["aliases"])
        #foundCodecs = set(name for imp, name, ispkg in \
        #                pkgutil.iter_modules(encodings.__path__) if not ispkg)
        #foundCodecs.difference_update(falsePositives)
        #foundCodecs = sorted(list(foundCodecs))
        #self.cbEncoding.addItems(foundCodecs)
        #self.cbEncoding.setCurrentIndex(foundCodecs.index('utf_8'))
        #self.cbEncoding.setCurrentIndex( 
        #    self.cbEncoding.findText( pMonkeyStudio.defaultCodec() ) )

        # connections
        self.cbSearch.lineEdit().textChanged.connect(self._updateActionsState)
        self.cbRegularExpression.stateChanged.connect(self._updateActionsState)
        self.cbCaseSensitive.stateChanged.connect(self._updateActionsState)
        
        self.cbSearch.lineEdit().textChanged.connect(self._onSearchRegExpChanged)
        self.cbRegularExpression.stateChanged.connect(self._onSearchRegExpChanged)
        self.cbCaseSensitive.stateChanged.connect(self._onSearchRegExpChanged)
        
        core.workspace().currentDocumentChanged.connect(self._updateActionsState)
        
        self.tbCdUp.clicked.connect(self.cdUp_pressed)
        self.searchThread.started.connect(self.searchThread_stateChanged)
        self.searchThread.finished.connect(self.searchThread_stateChanged)
        self.searchThread.progressChanged.connect(\
                                        self.searchThread_progressChanged)
        self._replaceThread.started.connect(self.replaceThread_stateChanged)
        self._replaceThread.finished.connect(self.replaceThread_stateChanged)
        self._replaceThread.openedFileHandled.connect(\
                                        self.replaceThread_openedFileHandled)
        self._replaceThread.error.connect(self.replaceThread_error)
        
        core.actionModel().action("mNavigation/mSearchReplace/aSearchNext")\
                                        .triggered.connect(self.on_pbNext_pressed)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchPrevious")\
                                        .triggered.connect(self.on_pbPrevious_pressed)
        
        self._updateActionsState()
        
        core.mainWindow().hideAllWindows.connect(self.hide)

        self._defaultBackgroundColor = self.cbSearch.palette().color(QPalette.Base)


    def setResultsDock(self, dock ):
        """Set to widget pointer to the search results dock
        """
        self._dock = dock

        # connections
        self._replaceThread.resultsHandled.connect(\
                                    self._dock.model.thread_resultsHandled)

    def setMode(self, mode ):
        """Change search mode.
        i.e. from "Search file" to "Replace directory"
        """
        self.searchThread.stop()
        self._replaceThread.stop()
        
        currentDocumentOnly = False
        
        # clear search results if needed.
        if mode & Plugin.ModeFlagFile:
            currentDocumentOnly = True
        else:
            currentDocumentOnly = False
            self.searchThread.clear()
        
        self._mode = mode
        
        # TODO support search in project
        #if self._mode & Plugin.ModeFlagProjectFiles :
        #    if  self.searchContext.project :
        #        encoding = self.searchContext.project.temporaryValue(
        #        "encoding", mks.monkeystudio.defaultCodec() ).toString()
        #        self.searchContext.encoding = encoding
        #        self.cbEncoding.setCurrentIndex( self.cbEncoding.findText(
        #        encoding ) )
        #assert( self.searchContext.encoding )
        
        if core.workspace().currentDocument():
            searchText = core.workspace().currentDocument().selectedText()
        else:
            searchText = ''
        
        self.setVisible( mode != Plugin.ModeNo )

        if searchText:
            self.cbSearch.setEditText( searchText )
            self.cbReplace.setEditText( searchText )
            
        if  mode & Plugin.ModeFlagDirectory :
            try:
                searchPath = os.path.abspath(unicode(os.path.curdir))
                self.cbPath.setEditText( searchPath )
            except OSError:  # current directory might be deleted
                pass 

        self.cbSearch.setFocus()
        self.cbSearch.lineEdit().selectAll()

        # hlamer: I'm sory for long lines, but, even workse without it
        # Set widgets visibility flag according to state
        widgets = (self.wSearch, self.pbPrevious, self.pbNext, self.pbSearch, self.wReplace, self.wPath, \
                   self.pbReplace, self.pbReplaceAll, self.pbReplaceChecked, self.wOptions, self.wMask, self.wEncoding,)
        #                             wSear  pbPrev pbNext pbSear wRepl  wPath  pbRep  pbRAll pbRCHK wOpti wMask wEnc
        visible = \
        {Plugin.ModeNo     :             (0,     0,     0,     0,     0,     0,     0,     0,     0,    0,    0,    0,),
         Plugin.ModeSearch :             (1,     1,     1,     0,     0,     0,     0,     1,     1,    1,    0,    0,),
         Plugin.ModeReplace:             (1,     1,     1,     0,     1,     0,     1,     1,     0,    1,    0,    0,),
         Plugin.ModeSearchDirectory:     (1,     0,     0,     1,     0,     1,     0,     0,     0,    1,    1,    1,),
         Plugin.ModeReplaceDirectory:    (1,     0,     0,     1,     1,     1,     0,     0,     1,    1,    1,    1,),
         Plugin.ModeSearchProjectFiles:  (1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
         Plugin.ModeSearchProjectFiles:  (1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
         Plugin.ModeReplaceProjectFiles: (1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    1,),
         Plugin.ModeSearchOpenedFiles:   (1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    0,),
         Plugin.ModeReplaceOpenedFiles:  (1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    0,)}
        
        for i, widget in enumerate(widgets):
            widget.setVisible(visible[mode][i])

        self.updateLabels()
        self.updateWidgets()

    def eventFilter(self, object_, event ):
        """ Event filter for mode switch tool button
        Draws icons in the search and path lineEdits
        """
        if  event.type() == QEvent.Paint :
            toolButton = object_
            if toolButton == self.tbMode:
                lineEdit = self.cbSearch.lineEdit()
            else:
                lineEdit = self.cbPath.lineEdit()
            lineEdit.setContentsMargins( lineEdit.height(), 0, 0, 0 )
            
            height = lineEdit.height()
            availableRect = QRect( 0, 0, height, height )
            
            if  toolButton.rect() != availableRect :
                toolButton.setGeometry( availableRect )
            
            painter = QPainter ( toolButton )
            toolButton.icon().paint( painter, availableRect )
            
            return True

        return QFrame.eventFilter( self, object_, event )

    def keyPressEvent(self, event ):
        """Handles ESC and ENTER pressings on widget for hide widget or start action"""
        if  event.modifiers() == Qt.NoModifier :
            if event.key() == Qt.Key_Escape:
                core.workspace().focusCurrentDocument()
                self.hide()
            elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if self._mode == Plugin.ModeNo:
                    pass
                elif self._mode == Plugin.ModeSearch:
                    self.pbNext.click()
                elif self._mode in (Plugin.ModeSearchDirectory, \
                                    Plugin.ModeSearchProjectFiles, \
                                    Plugin.ModeSearchOpenedFiles, \
                                    Plugin.ModeReplaceDirectory, \
                                    Plugin.ModeReplaceProjectFiles, \
                                    Plugin.ModeReplaceOpenedFiles):
                    if not self.searchThread.isRunning():
                        self.pbSearch.click()
                    else:
                        self.pbSearchStop.click()
                elif self._mode == Plugin.ModeReplace:
                    self.pbReplace.click()

        QFrame.keyPressEvent( self, event )

    def updateLabels(self):
        """Update 'Search' 'Replace' 'Path' labels geometry
        """
        width = 0

        if  self.lSearch.isVisible() :
            width = max( width, self.lSearch.minimumSizeHint().width() )

        if   self.lReplace.isVisible() :
            width = max( width,  self.lReplace.minimumSizeHint().width() )

        if  self.lPath.isVisible() :
            width = max( width, self.lPath.minimumSizeHint().width() )

        self.lSearch.setMinimumWidth( width )
        self.lReplace.setMinimumWidth( width )
        self.lPath.setMinimumWidth( width )


    def updateWidgets(self):
        """Update geometry of widgets with buttons
        """
        width = 0

        if  self.wSearchRight.isVisible() :
            width = max( width, self.wSearchRight.minimumSizeHint().width() )

        if  self.wReplaceRight.isVisible() :
            width = max( width, self.wReplaceRight.minimumSizeHint().width() )

        if  self.wPathRight.isVisible() :
            width = max( width, self.wPathRight.minimumSizeHint().width() )

        self.wSearchRight.setMinimumWidth( width )
        self.wReplaceRight.setMinimumWidth( width )
        self.wPathRight.setMinimumWidth( width )

    def updateComboBoxes(self):
        """Update comboboxes with last used texts
        """
        searchText = self.cbSearch.currentText()
        replaceText = self.cbReplace.currentText()
        maskText = self.cbMask.currentText()
        
        # search
        if searchText:
            index = self.cbSearch.findText( searchText )
            
            if  index == -1 :
                self.cbSearch.addItem( searchText )
        
        # replace
        if replaceText:
            index = self.cbReplace.findText( replaceText )
            
            if  index == -1 :
                self.cbReplace.addItem( replaceText )

        # mask
        if maskText:
            index = self.cbMask.findText( maskText )
            
            if  index == -1 :
                self.cbMask.addItem( maskText )
    
    def _searchPatternTextAndFlags(self):
        """Get search pattern and flags
        """
        pattern = self.cbSearch.currentText()
        if not self.cbRegularExpression.checkState() == Qt.Checked:
            pattern = re.escape(pattern)
        flags = 0
        if not self.cbCaseSensitive.checkState() == Qt.Checked:
            flags = re.IGNORECASE
        return pattern, flags

    def _getRegExp(self):
        """Read search parameters from controls and present it as a regular expression
        """
        pattern, flags = self._searchPatternTextAndFlags()
        return re.compile(pattern, flags)
    
    def _isSearchRegExpValid(self):
        """Try to compile search pattern to check if it is valid
        Returns bool result and text error
        """
        pattern, flags = self._searchPatternTextAndFlags()
        try:
            re.compile(pattern, flags)
        except re.error, ex:
            return False, unicode(ex)
        
        return True, None

    def _makeSearchContext(self):
        """Fill search context with actual data
        """

        searchContext = SearchContext(  self._getRegExp(), \
                                        replaceText = self.cbReplace.currentText(), \
                                        searchPath = self.cbPath.currentText(), \
                                        mode = self._mode,
                                        encoding = self.cbEncoding.currentText())

        # TODO search in project
        #self.searchContext.project = core.fileManager().currentProject()
        
        # update masks
        searchContext.mask = \
            [s.strip() for s in self.cbMask.currentText().split(' ')]
        # remove empty
        searchContext.mask = [m for m in searchContext.mask if m]
        
        # TODO update project
        #self.searchContext.project = self.searchContext.project.topLevelProject()

        # update opened files
        for document in core.workspace().openedDocuments():
            searchContext.openedFiles[document.filePath()] = document.text()
        
        # TODO support project
        # update sources files
        #self.searchContext.sourcesFiles = []
        #if self.searchContext.project:
        #    self.searchContext.sourcesFiles = \
        #                self.searchContext.project.topLevelProjectSourceFiles()
        
        return searchContext

    def showMessage (self, status):
        """Show message on the status bar"""
        if not status:
            core.mainWindow().statusBar().clearMessage()
        else:
            core.mainWindow().statusBar().showMessage( status, 30000 )

    def setState(self, state ):
        """Change line edit color according to search result
        """
        widget = self.cbSearch.lineEdit()
        
        color = {SearchWidget.Normal: self._defaultBackgroundColor, \
                 SearchWidget.Good: Qt.green, \
                 SearchWidget.Bad: Qt.red,
                 SearchWidget.Incorrect: Qt.darkYellow}
        
        pal = widget.palette()
        pal.setColor( widget.backgroundRole(), color[state] )
        widget.setPalette( pal )
    
    def searchFile(self, forward, incremental = False):
        """Do search in file operation. Will select next found item
        """
        document = core.workspace().currentDocument()
        regExp = self._getRegExp()

        # get cursor position        
        start, end = document.absSelection()

        if start is None:
            start = 0
            end = 0
        
        if forward:
            if  incremental :
                point = start
            else:
                point = end

            match = regExp.search(document.text(), point)
            if match is None:  # wrap
                match = regExp.search(document.text(), 0)
        else:  # reverse search
            prevMatch = None
            for match in regExp.finditer(document.text()):
                if match.start() >= start:
                    break
                prevMatch = match
            match = prevMatch
            if match is None:  # wrap
                matches = [match for match in regExp.finditer(document.text())]
                if matches:
                    match = matches[-1]
        
        if match is not None:
            document.goTo(absPos = match.start(), selectionLength = len(match.group(0)))
            self.setState(SearchWidget.Good)  # change background acording to result
        else:
            self.setState(SearchWidget.Bad)
        
        # return found state
        return match is not None

    def replaceFile(self):
        """Do one replacement in the file
        """
        document = core.workspace().currentDocument()
        regExp = self._getRegExp()

        start, end = document.absSelection()  # pylint: disable=W0612
        if start is None:
            start = 0
        
        match = regExp.search(document.text(), start)
        
        if match is None:
            match = regExp.search(document.text(), 0)
        
        if match is not None:
            document.goTo(absPos = match.start(), selectionLength = len(match.group(0)))
            replaceText = self.cbReplace.currentText()
            try:
                replaceText = regExp.sub(replaceText, match.group(0))
            except re.error, ex:
                message = unicode(ex.message, 'utf_8')
                message += r'. Probably <i>\group_index</i> used in replacement string, but such group not found. '\
                           r'Try to escape it: <i>\\group_index</i>'
                QMessageBox.critical(None, "Invalid replace string", message)
                # TODO link to replace help
                return
            document.replaceSelectedText(replaceText)
            document.goTo(absPos = match.start() + len(replaceText))
            self.pbNext.click() # move selection to next item
        else:
            self.setState(SearchWidget.Bad)

    def replaceFileAll(self):
        """Do all replacements in the file
        """
        document = core.workspace().currentDocument()
        regExp = self._getRegExp()
        replaceText = self.cbReplace.currentText()

        oldPos = document.absCursorPosition()
        
        document.beginUndoAction()
        
        pos = 0
        count = 0
        match = regExp.search(document.text(), pos)
        while match is not None:
            document.goTo(absPos = match.start(), selectionLength = len(match.group(0)))
            replText = regExp.sub(replaceText, match.group(0))
            document.replaceSelectedText(replText)
            
            count += 1
            
            pos = match.start() + len(replText)
            
            if not match.group(0) and not replText:  # avoid freeze when replacing empty with empty
                pos += 1
            if pos < len(document.text()):
                match = regExp.search(document.text(), pos)
            else:
                match = None

        document.endUndoAction()
        
        if oldPos is not None:
            document.setCursorPosition(absPos = oldPos) # restore cursor position
        self.showMessage( self.tr( "%d occurrence(s) replaced." % count ))

    def searchThread_stateChanged(self):
        """Search thread started or stopped
        """
        self.pbSearchStop.setVisible( self.searchThread.isRunning() )
        self.pbSearch.setVisible( not self.searchThread.isRunning() )
        self.updateWidgets()
        self._progress.setVisible( self.searchThread.isRunning() )

    def searchThread_progressChanged(self, value, total ):
        """Signal from the thread, progress changed
        """
        self._progress.setValue( value )
        self._progress.setMaximum( total )

    def replaceThread_stateChanged(self):
        """Replace thread started or stopped
        """
        self.pbReplaceCheckedStop.setVisible( self._replaceThread.isRunning() )
        self.pbReplaceChecked.setVisible( not self._replaceThread.isRunning() )
        self.updateWidgets()

    def replaceThread_openedFileHandled(self, fileName, content):
        """Replace thread processed currently opened file,
        need update text in the editor
        """
        document = core.workspace().openFile(fileName)
        document.replace(content, startAbsPos=0, endAbsPos=len(document.text()))

    def replaceThread_error(self, error ):
        """Error message from the replace thread
        """
        core.messageToolBar().appendMessage( error )
    
    def _updateActionsState(self):
        """Update actions state according to search context valid state
        """
        valid, error = self._isSearchRegExpValid()
        searchAvailable = valid 
        searchInFileAvailable = valid and core.workspace().currentDocument() is not None
        
        for button in (self.pbNext, self.pbPrevious, self.pbReplace, self.pbReplaceAll):
            button.setEnabled(searchInFileAvailable)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchNext").setEnabled(searchInFileAvailable)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchPrevious").setEnabled(searchInFileAvailable)

        self.pbSearch.setEnabled(searchAvailable)
    
    def _onSearchRegExpChanged(self):
        """User edited search text or checked/unchecked checkboxes
        """
        valid, error = self._isSearchRegExpValid()
        if valid:
            self.setState(self.Normal)
        else:
            core.mainWindow().statusBar().showMessage(error, 5000)
            self.setState(self.Incorrect)
            return
        
        # clear search results if needed.
        if self._mode in (Plugin.ModeSearch, Plugin.ModeReplace) and \
           core.workspace().currentDocument() is not None:
            self.searchFile( True, True )

    def cdUp_pressed(self):
        """User pressed "Up" button, need to remove one level from search path
        """
        text = self.cbPath.currentText()
        if not os.path.exists(text):
            return
        self.cbPath.setEditText( os.path.abspath(text + '/' + os.path.pardir))

    def on_pbPrevious_pressed(self):
        """Handler of click on "Previous" button
        """
        self.updateComboBoxes()
        self.searchFile( False )

    def on_pbNext_pressed(self):
        """Handler of click on "Next" button
        """
        self.updateComboBoxes()
        self.searchFile( True, False )

    def on_pbSearch_pressed(self):
        """Handler of click on "Search" button (for search in directory)
        """
        self.setState(SearchWidget.Normal )
        self.updateComboBoxes()
        
        # TODO support project
        #if  self.searchContext._mode & Plugin.ModeFlagProjectFiles and not self.searchContext.project :
        #    core.messageToolBar().appendMessage( \
        #                        self.tr( "You can't search in project files because there is no opened projet." ) )
        #    return

        self.searchThread.search( self._makeSearchContext() )

    def on_pbSearchStop_pressed(self):
        """Handler of click on "Stop" button. Stop search thread
        """
        self.searchThread.stop()

    def on_pbReplace_pressed(self):
        """Handler of click on "Replace" (in file) button
        """
        self.updateComboBoxes()
        self.replaceFile()

    def on_pbReplaceAll_pressed(self):
        """Handler of click on "Replace all" (in file) button
        """
        self.updateComboBoxes()
        self.replaceFileAll()

    def on_pbReplaceChecked_pressed(self):
        """Handler of click on "Replace checked" (in directory) button
        """
        items = {}
        model = self._dock.model

        self.updateComboBoxes()
        
        # TODO support project
        # TODO disable action, don't show the message!
        #if  self.searchContext.mode & Plugin.ModeFlagProjectFiles and not self.searchContext.project :
        #    core.messageToolBar().appendMessage(
        #         self.tr( "You can't replace in project files because there is no opened projet." ) )
        #    return

        for fileRes in model.fileResults:
            for row, result in enumerate(fileRes.results):
                if result.enabled and result.checkState == Qt.Checked :
                    if not result.fileName in items:
                        items[result.fileName] = []
                    items[ result.fileName ].append(result)
                else:
                    index = model.createIndex(row, 0, result)
                    self._dock.model.setData( index, False, SearchResultsModel.EnabledRole )

        self._replaceThread.replace( self._makeSearchContext(), items )

    def on_pbReplaceCheckedStop_pressed(self):
        """Handler of click on "Stop" button when replacing in directory
        """
        self._replaceThread.stop()

    def on_pbBrowse_pressed(self):
        """Handler of click on "Browse" button. Explores FS for search directory path
        """
        path = QFileDialog.getExistingDirectory( self, self.tr( "Search path" ), self.cbPath.currentText() )

        if path:
            self.cbPath.setEditText( path )

    
class SearchResultsModel(QAbstractItemModel):
    """AbstractItemodel used for display search results in 'Search in directory' and 'Replace in directory' mode
    """
    firstResultsAvailable = pyqtSignal()
    
    EnabledRole = Qt.UserRole
    
    class Result:  # pylint: disable=R0902
        """One found by search thread item. Consists coordinates and capture. Used by SearchResultsModel
        """
        def __init__ (  self, fileName, wholeLine, line, column, match):  # pylint: disable=R0913
            self.fileName = fileName
            self.wholeLine = wholeLine
            self.line = line
            self.column = column
            self.match = match
            self.checkState =  Qt.Checked
            self.enabled = True
        
        def text(self, notUsed):  # pylint: disable=W0613
            """Displayable text of search result. Shown as line in the search results dock
            notUsed argument added for have same signature, as FileResults.text
            """
            return "Line: %d, Column: %d: %s" % ( self.line + 1, self.column, self.wholeLine )
        
        def tooltip(self):
            """Tooltip of the search result"""
            return self.wholeLine
        
        def hasChildren(self):
            """Check if QAbstractItem has children"""
            return False

    class FileResults:
        """Object stores all items, found in the file
        """
        def __init__(self, fileName, results):
            self.fileName = fileName
            self.results = results
            self.checkState = Qt.Checked
        
        def __str__(self):
            """Convertor to string. Used for debugging
            """
            return '%s (%d)' % (self.fileName, len(self.results))
        
        def updateCheckState(self):
            """Update own checked state after checked state of child result changed or
            child result removed
            """
            if all([res.checkState == Qt.Checked for res in self.results]):  # if all checked
                self.checkState = Qt.Checked
            elif any([res.checkState == Qt.Checked for res in self.results]):  # if any checked
                self.checkState = Qt.PartiallyChecked
            else:
                self.checkState = Qt.Unchecked
        
        def text(self, baseDir):
            """Displayable text of the file results. Shown as line in the search results dock
            baseDir is base directory of current search operation
            """
            return '%s (%d)' % (baseDir.relativeFilePath(self.fileName), len(self.results))
        
        def tooltip(self):
            """Tooltip of the item in the results dock
            """
            return self.fileName
        
        def hasChildren(self):
            """Check if item has children
            """
            return 0 != len(self.results)
    
    def __init__(self, searchThread, parent ):
        """Constructor of SearchResultsModel class
        """
        QAbstractItemModel.__init__(self, parent )
        self._rowCount = 0
        self.searchThread = searchThread
        
        self.fileResults = []  # list of FileResults
        self._searchDir = QDir()
        
        # connections
        self.searchThread.reset.connect(self.clear)
        self.searchThread.resultsAvailable.connect(self.thread_resultsAvailable)

    def index(self, row, column, parent ):
        """See QAbstractItemModel docs
        """
        if  row >= self.rowCount( parent ) or column > self.columnCount(parent):
            return QModelIndex()
        
        if parent.isValid():  # index for result
            result = parent.internalPointer().results[row]
            return self.createIndex( row, column, result )
        else:  # need index for fileRes
            return self.createIndex( row, column, self.fileResults[row])

    def parent(self, index):
        """See QAbstractItemModel docs
        """
        if not index.isValid() :
            return QModelIndex()
        
        if not isinstance(index.internalPointer(), SearchResultsModel.Result):  # it is an top level item
            return QModelIndex()
        
        result = index.internalPointer()
        for row, fileRes in enumerate(self.fileResults):
            if fileRes.fileName == result.fileName:
                return self.createIndex(row, 0, fileRes)
        else:
            assert(0)

    def hasChildren(self, item):
        """See QAbstractItemModel docs
        """
        # root parents
        if item.isValid():
            return item.internalPointer().hasChildren()
        else:
            return len(self.fileResults) != 0

    def columnCount(self, parent ):  # pylint: disable=W0613
        """See QAbstractItemModel docs
        """
        return 1
    
    def rowCount(self, parent):
        """See QAbstractItemModel docs
        """
        if not parent.isValid():  # root elements
            return len(self.fileResults)
        elif isinstance(parent.internalPointer(), SearchResultsModel.Result):  # result
            return 0
        elif isinstance(parent.internalPointer(), self.FileResults):  # file
            return len(parent.internalPointer().results)
        else:
            assert(0)
    
    def flags(self, index ):
        """See QAbstractItemModel docs
        """
        flags = QAbstractItemModel.flags( self, index )
        context = self.searchThread.searchContext

        if context.mode & Plugin.ModeFlagReplace :
            flags |= Qt.ItemIsUserCheckable
        
        if isinstance(index.internalPointer(), SearchResultsModel.Result):
            if not index.internalPointer().enabled :
                flags &= ~Qt.ItemIsEnabled
                flags &= ~Qt.ItemIsSelectable
        
        return flags
    
    def data(self, index, role ):
        """See QAbstractItemModel docs
        """
        if not index.isValid() :
            return QVariant()
        
        # Common code for file and result
        if role == Qt.DisplayRole:
            return self.tr( index.internalPointer().text(self._searchDir))
        elif role == Qt.ToolTipRole:
            return index.internalPointer().tooltip()
        elif role == Qt.CheckStateRole:
            if  self.flags( index ) & Qt.ItemIsUserCheckable:
                return index.internalPointer().checkState
        
        return QVariant()
    
    def setData(self, index, value, role ):
        """See QAbstractItemModel docs
        This method changes checked state of the item.
        If file unchecked - we need uncheck all items,
        if item unchecked...
        """
        if isinstance(index.internalPointer(), SearchResultsModel.Result):  # it is a Result
            if role == Qt.CheckStateRole:
                # update own state
                index.internalPointer().checkState = value.toInt()[0]
                self.dataChanged.emit( index, index )  # own checked state changed
                # update parent state
                fileRes = index.parent().internalPointer()
                assert(isinstance(fileRes, self.FileResults))
                fileRes.updateCheckState()
                self.dataChanged.emit(index.parent(), index.parent())  # parent checked state might be changed
        elif isinstance(index.internalPointer(), self.FileResults):  # it is a FileResults
            if role == Qt.CheckStateRole:
                fileRes = index.internalPointer()
                fileRes.checkState = value.toInt()[0]
                for res in fileRes.results:
                    res.checkState = value.toInt()[0]
                firstChildIndex = self.index(0, 0, index)
                lastChildIndex = self.index(len(fileRes.results) - 1, 0, index)
                self.dataChanged.emit(firstChildIndex, lastChildIndex)
        else:
            assert(0)
        return True
    
    def clear(self):
        """Clear all results
        """
        self.beginRemoveRows(QModelIndex(), 0, len(self.fileResults) - 1)
        self.fileResults = []
        self.endRemoveRows()

    def thread_resultsAvailable(self, fileResultsList ):
        """Handler of signal from the search thread.
        New result is available, add it to the model
        """
        context = self.searchThread.searchContext
        if not self.fileResults:  # appending first
            self.firstResultsAvailable.emit()
            self._searchDir.setPath( context.searchPath )
        self.beginInsertRows( QModelIndex(), \
                              len(self.fileResults), \
                              len(self.fileResults) + len(fileResultsList) - 1)
        self.fileResults.extend(fileResultsList)
        self.endInsertRows()
    
    def thread_resultsHandled(self, fileName, results):
        """Replace thread processed result, need to remove it from the model
        """
        for index, fileRes in enumerate(self.fileResults):  # try to find FileResults
            if fileRes.fileName == fileName:  # found
                fileResIndex = self.createIndex(index, 0, fileRes)
                if len(results) == len(fileRes.results):  # removing all
                    self.beginRemoveRows(QModelIndex(), index, index)
                    self.fileResults.pop(index)
                    self.endRemoveRows()                    
                else:
                    for res in results:
                        resIndex = fileRes.results.index(res)
                        self.beginRemoveRows(fileResIndex, resIndex, resIndex)
                        fileRes.results.pop(resIndex)
                        self.endRemoveRows()
                    if not fileRes.results:  # no results left
                        self.beginRemoveRows(QModelIndex(), index, index)
                        self.fileResults.pop(index)
                        self.endRemoveRows()
                    else:
                        fileRes.updateCheckState()
                return
        else:  # not found
            assert(0)

class SearchResultsDock(pDockWidget):
    """Dock with search results
    """
    def __init__(self, searchThread, parent=None):
        pDockWidget.__init__( self, parent )
        self.setObjectName("SearchResultsDock")
        assert(searchThread)

        self.searchThread = searchThread

        self.setObjectName( self.metaObject().className() )
        self.setWindowTitle( self.tr( "Search Results" ) )
        self.setWindowIcon( QIcon(":/mksicons/search.png") )
        
        # actions
        widget = QWidget( self )
        self.model = SearchResultsModel( searchThread, self )
        self._view = QTreeView( self )
        self._view.setHeaderHidden( True )
        self._view.setUniformRowHeights( True )
        self._view.setModel( self.model )
        self._layout = QHBoxLayout( widget )
        self._layout.setMargin( 5 )
        self._layout.setSpacing( 5 )
        self._layout.addWidget( self._view )

        self.setWidget( widget )
        self.setFocusProxy(self._view)
        
        # TODO PasNox, check if we need it on mac
        # mac
        #self.pMonkeyStudio.showMacFocusRect( self, False, True )
        #pMonkeyStudio.setMacSmallSize( self, True, True )

        # connections
        self.model.firstResultsAvailable.connect(self.show)
        self._view.activated.connect(self.view_activated)
        
        self.showAction().setShortcut("F10")
        core.actionModel().addAction("mDocks/aSearchResults", self.showAction())

    def del_(self):
        core.actionModel().removeAction("mDocks/aSearchResults")

    def view_activated(self, index ):
        """Item doubleclicked in the model, opening file
        """
        result = index.internalPointer()
        if isinstance(result, SearchResultsModel.Result):
            core.workspace().goToLine( result.fileName,
                                       result.line + 1,
                                       result.column,
                                       len(result.match.group(0)))

class StopableThread(QThread):
    """Stoppable thread class. Used as base for search and replace thread.
    """
    _exit = False
    
    def __init__(self):
        QThread.__init__(self)
    
    def __del__(self):
        self.stop()

    def stop(self):
        """Stop thread synchronously
        """
        self._exit = True
        self.wait()
    
    def start(self):
        """Ensure thread is stopped, and start it
        """
        self.stop()
        self._exit = False
        QThread.start(self)

class SearchThread(StopableThread):
    """Thread builds list of files for search and than searches in this files.append
    """
    RESULTS_EMIT_TIMEOUT = 1.0

    reset = pyqtSignal()
    resultsAvailable = pyqtSignal(list)  # list of SearchResultsModel.FileResults
    progressChanged = pyqtSignal(int, int)  # int value, int total

    def search(self, context ):
        """Start search process.
        context stores search text, directory and other parameters
        """
        self.stop()
        self.searchContext = context
        self.start()

    def clear(self):
        """Stop thread and clear search results
        """
        self.stop()
        self.reset.emit()            

    def _getFiles(self, path, maskRegExp):
        """Get recursive list of files from directory.
        maskRegExp is regExp object for check if file matches mask
        """
        retFiles = []
        for root, dirs, files in os.walk(os.path.abspath(path)):  # pylint: disable=W0612
            if root.startswith('.') or (os.path.sep + '.') in root:
                continue
            for fileName in files:
                if fileName.startswith('.'):
                    continue
                if maskRegExp and not maskRegExp.match(fileName):
                    continue
                fullPath = os.path.join(root, fileName)
                if not os.path.isfile(fullPath):
                    continue
                retFiles.append(root + os.path.sep + fileName)

            if self._exit :
                break

        return retFiles
    
    def _getFilesToScan(self):
        """Get list of files for search.
        """
        files = set()

        # TODO search in project
        #elif mode in (Plugin.ModeSearchProjectFiles, Plugin.ModeReplaceProjectFiles):
        #    sources = self.searchContext.sourcesFiles
        #    mask = self.searchContext.mask
        #    for fileName in sources:
        #        if  QDir.match( mask, fileName ) :
        #            files.append(fileName)
        
        if self.searchContext.mask:
            regExPatterns = [fnmatch.translate(pat) for pat in self.searchContext.mask]
            maskRegExpPattern = '(' + ')|('.join(regExPatterns) + ')'
            maskRegExp = re.compile(maskRegExpPattern)
        else:
            maskRegExp = None

        if self.searchContext.mode in (Plugin.ModeSearchDirectory, Plugin.ModeReplaceDirectory):
            path = self.searchContext.searchPath
            return self._getFiles(path, maskRegExp)
        elif self.searchContext.mode in \
                                (Plugin.ModeSearchOpenedFiles, Plugin.ModeReplaceOpenedFiles):
            files = self.searchContext.openedFiles.keys()
            if maskRegExp:
                basenames = [os.path.basename(f) for f in files]
                files = [f for f in basenames if maskRegExp.match(f)]
            return files
        else:
            assert(0)

    def _fileContent(self, fileName, encoding='utf_8'):
        """Read text from file
        """
        if fileName in self.searchContext.openedFiles:
            return self.searchContext.openedFiles[ fileName ]

        try:
            with open(fileName) as openedFile:
                if _isBinary(openedFile):
                    return ''
                return unicode(openedFile.read(), encoding, errors = 'ignore')
        except IOError as ex:
            print ex
            return ''

    def run(self):
        """Start point of the code, running in thread.
        Build list of files for search, than do search
        """
        startTime = time.clock()
        self.reset.emit()
        self.progressChanged.emit( -1, 0 )

        files = sorted(self._getFilesToScan())

        if  self._exit :
            return
        
        self.progressChanged.emit( 0, len(files))
        
        # Prepare data for search process        
        lastResultsEmitTime = time.clock()
        notEmittedFileResults = []
        # Search for all files
        for fileIndex, fileName in enumerate(files):
            results = self._searchInFile(fileName)
            if  results:
                notEmittedFileResults.append(SearchResultsModel.FileResults(fileName, results))

            if notEmittedFileResults and \
               (time.clock() - lastResultsEmitTime) > self.RESULTS_EMIT_TIMEOUT:
                self.progressChanged.emit( fileIndex, len(files))
                self.resultsAvailable.emit(notEmittedFileResults)
                notEmittedFileResults = []
                lastResultsEmitTime = time.clock()

            if  self._exit :
                self.progressChanged.emit( fileIndex, len(files))
                break
        
        if notEmittedFileResults:
            self.resultsAvailable.emit(notEmittedFileResults)

    def _searchInFile(self, fileName):
        """Search in the file and return SearchResultsModel.Result s
        """
        lastPos = 0
        eolCount = 0
        results = []
        eol = "\n"
        
        content = self._fileContent( fileName )
        
        # Process result for all occurrences
        for match in self.searchContext.regExp.finditer(content):
            start = match.start()
            
            eolStart = content.rfind( eol, 0, start)
            eolEnd = content.find( eol, start)
            eolCount += content[lastPos:start].count( eol )
            lastPos = start
            
            wholeLine = content[eolStart + 1:eolEnd].strip()
            column = start - eolStart
            if eolStart != 0:
                column -= 1
            
            result = SearchResultsModel.Result( fileName = fileName, \
                             wholeLine = wholeLine, \
                             line = eolCount, \
                             column = column, \
                             match=match)
            results.append(result)

            if self._exit:
                break
        return results

class ReplaceThread(StopableThread):
    """Thread does replacements in the directory according to checked items
    """
    resultsHandled = pyqtSignal(unicode, list)
    openedFileHandled = pyqtSignal(unicode, unicode)
    error = pyqtSignal(unicode)

    def replace(self, context, results):
        """Run replace process
        """
        self.stop()
        self.searchContext = context
        self._results = results
        self.start()

    def _saveContent(self, fileName, content, encoding):
        """Write text to the file
        """
        if encoding:
            try:
                content = content.encode(encoding)
            except UnicodeEncodeError as ex:
                pattern = self.tr("Failed to encode file to %s: %s")
                text = unicode(str(ex), 'utf_8')
                self.error.emit(pattern % (encoding, text))
                return
        try:
            with open(fileName, 'w') as openFile:
                openFile.write(content)
        except IOError as ex:
            pattern = self.tr("Error while saving replaced content: %s")
            text = unicode(str(ex), 'utf_8')
            self.error.emit(pattern % text)

    def _fileContent(self, fileName, encoding='utf_8'):
        """Read file
        """
        if fileName in self.searchContext.openedFiles:
            return self.searchContext.openedFiles[ fileName ]
        else:
            try:
                with open(fileName) as openFile:
                    content = openFile.read()
            except IOError as ex:
                self.error.emit( self.tr( "Error opening file: %s" % str(ex) ) )
                return ''
            
            if encoding:
                try:
                    return unicode(content, encoding)
                except UnicodeDecodeError as ex:
                    self.error.emit(self.tr( "File %s not read: unicode error '%s'. File may be corrupted" % \
                                    (fileName, str(ex) ) ))
                    return None
            else:
                return content

    def run(self):
        """Start point of the code, running i thread
        Does thread job
        """
        startTime = time.clock()
        
        for fileName in self._results.keys():
            handledResults = []
            content = self._fileContent( fileName, self.searchContext.encoding )
            if content is None:  # if failed to read file
                continue
            
            # count from end to begin because we are replacing by offset in content
            for result in self._results[ fileName ][::-1]:
                try:
                    replaceTextWithMatches = self.searchContext.regExp.sub(self.searchContext.replaceText, result.match.group(0))
                except re.error, ex:
                    message = unicode(ex.message, 'utf_8')
                    message += r'. Probably <i>\group_index</i> used in replacement string, but such group not found. '\
                               r'Try to escape it: <i>\\group_index</i>'
                    self.error.emit(message)
                    return
                content = content[:result.match.start()] + replaceTextWithMatches + content[result.match.end():]
                handledResults.append(result)
            
            if fileName in self.searchContext.openedFiles:
                # TODO encode content with self.searchContext.encoding 
                self.openedFileHandled.emit( fileName, content)
            else:
                self._saveContent( fileName, content, self.searchContext.encoding )
            
            self.resultsHandled.emit( fileName, handledResults)

            if  self._exit :
                break

        print "Replace finished in ", time.clock() - startTime