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
from PyQt4.QtGui import QAction, QCompleter, QColor, QDirModel, QFileDialog,  \
                        QFrame, QFileDialog, QHBoxLayout, QIcon, \
                        QPainter,  \
                        QProgressBar, QToolButton, QTreeView, QWidget
from PyQt4.fresh import pDockWidget

from mks.core.core import core, DATA_FILES_PATH

def isBinary(fileObject):
    """Expects, that file position is 0, when exits, file position is 0
    """
    binary = '\0' in fileObject.read( 4096 )
    fileObject.seek(0)
    return binary


class Plugin(QObject):  # TODO (Plugin) ?
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

    OptionNo = 0x0
    OptionCaseSensitive = 0x1
    OptionWholeWord = 0x2
    OptionWrap = 0x4
    OptionRegularExpression = 0x8
    
    def __init__(self):
        """Plugin initialisation
        """
        QObject.__init__(self)
        self.widget = None
        model = core.actionModel()
        
        def createAction(path, text, icon, shortcut, tooltip, slot, data, enabled=True):
            actObject = model.addAction( 'mNavigation/mSearchReplace/' + path,
                                         self.tr(text),
                                         QIcon(':/mksicons/' + icon))
            actObject.setShortcut(self.tr(shortcut))
            actObject.setToolTip(self.tr(tooltip))
            if slot:
                actObject.triggered.connect(slot)
            actObject.setData(data)
            actObject.setEnabled(enabled)

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
        ''' TODO
                        ("aSearchProjectFiles", "Search in Project &Files...",
                        "search-replace-project-files.png", "Ctrl+Meta+F",
                        "Search in the current project files..",
                        self.modeSwitchTriggered, self.ModeSearchProjectFiles),
                        ("aReplaceProjectFiles", "Replace in Projec&t Files...",
                        "search-replace-project-files.png", "Ctrl+Meta+R",
                        "Replace in the current project files...",
                        self.modeSwitchTriggered, self.ModeReplaceProjectFiles),
        '''        
    
    def __del__(self):
        """Plugin termination
        """        
        core.actionModel().removeMenu("mNavigation/mSearchReplace")
    
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
        # TODO if  ( document and document.editor() ) or not document :
        if newMode & Plugin.ModeFlagFile:
            # TODO check if editor is a QScintilla
            self.widget.setMode(newMode)
        elif newMode & Plugin.ModeFlagDirectory:
            self.widget.setMode(newMode)
        elif newMode & Plugin.ModeFlagProjectFiles:  # TODO
            pass
        elif newMode & Plugin.ModeFlagOpenedFiles:
            # TODO check if have file based document
            if core.workspace().openedDocuments():
                self.widget.setMode(newMode)
    
    def _createWidgets(self):
        self.widget = SearchWidget( self )
        core.mainWindow().centralLayout().addWidget( self.widget )
        self.widget.setVisible( False )
        
        # FIXME create dock, only when have some search results!!!
        self.dock = SearchResultsDock( self.widget.mSearchThread )
        core.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDockWidget(self.dock)
        self.dock.setVisible( False )

        self.widget.setResultsDock( self.dock )

class SearchContext:
    """Structure holds parameters of search or replace operation in progress
    """
    mask = []
    """TODO
    encoding = ''
    """
    options = 0
    openedFiles = {}
    """TODO
    project = None
    sourcesFiles = ''
    """
    def __init__(self,
                 searchText, \
                 replaceText, \
                 searchPath, \
                 mode, \
                 encoding):
        self.searchText = searchText
        self.replaceText = replaceText
        self.searchPath = searchPath
        self.mode = mode
        self.encoding = encoding
    
    def regExp(self):
        """Compile regular expression object according to search text and
        options
        """
        pattern = self.searchText
        flags = 0
        
        # if not reg exp
        if not self.options & Plugin.OptionRegularExpression:
            pattern = re.escape( pattern )
        
        if self.options & Plugin.OptionWholeWord:  # whole word
            pattern = "\\b" + pattern + "\\b"
        
        # if not case sensetive
        if not self.options & Plugin.OptionCaseSensitive:
            flags = re.IGNORECASE
        
        return re.compile(pattern, flags)
        

class SearchWidget(QFrame):
    """Widget, appeared, when Ctrl+F pressed.
    Has different forms for different search modes
    """
    
    Search = 'search'
    Replace = 'replace'
    
    Normal = 'normal'
    Good = 'good'
    Bad = 'bad'
    
    def __init__(self, plugin):
        QFrame.__init__(self, core.workspace())
        self.mMode = None
        self.mSearchContext = None
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
        """TODO QDirModel is deprecated but QCompleter does not yet handle
        QFileSystemModel - please update when possible."""
        self.cbMask.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.pbSearchStop.setVisible( False )
        self.pbReplaceCheckedStop.setVisible( False )
        
        self.mProgress = QProgressBar( self )
        self.mProgress.setAlignment( Qt.AlignCenter )
        self.mProgress.setToolTip( self.tr( "Search in progress..." ) )
        self.mProgress.setMaximumSize( QSize( 80, 16 ) )
        core.mainWindow().statusBar().\
                insertPermanentWidget( 0, self.mProgress )
        self.mProgress.setVisible( False )
        
        # threads
        self.mSearchThread = SearchThread( self )
        self.mReplaceThread = ReplaceThread( self )

        self.mDock = None
        
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

        # options actions
        self.mModeActions = {}
        action = QAction( self.cbCaseSensitive )
        action.setCheckable( True )
        self.cbCaseSensitive.toggled.connect(action.setChecked)
        self.mModeActions[ Plugin.OptionCaseSensitive ] = action
        
        action = QAction( self.cbWholeWord )
        action.setCheckable( True )
        self.cbWholeWord.toggled.connect(action.setChecked)
        self.mModeActions[ Plugin.OptionWholeWord ] = action
        
        action = QAction( self.cbWrap )
        action.setCheckable( True )
        self.cbWrap.toggled.connect(action.setChecked)
        self.mModeActions[ Plugin.OptionWrap ] = action
        
        action = QAction( self.cbRegularExpression )
        action.setCheckable( True )
        self.cbRegularExpression.toggled.connect(action.setChecked)
        self.mModeActions[ Plugin.OptionRegularExpression ] = action
        
        # init default options
        self.cbWrap.setChecked( True )
        
        QWidget.setTabOrder(self.cbSearch, self.cbReplace)
        QWidget.setTabOrder(self.cbReplace, self.cbPath)
        
        """TODO
        # mac
        pMonkeyStudio.showMacFocusRect( self, False, True )
        pMonkeyStudio.setMacSmallSize( self, True, True )
        

    #ifdef Q_OS_MAC
         QSize size( 12, 12 )

        foreach ( QAbstractButton* button, findChildren<QAbstractButton*>() )
            button.setIconSize( size )
            button.setFixedHeight( 24 )


        vlMain.setSpacing( 0 )
    #endif
        """
        
        '''TODO
        # mask tooltip
        languages = pMonkeyStudio.availableLanguages()
        
        for ( i = 0; i < languages.count(); i += 10 )
            languages[ i ].prepend( "\n" )

        
        maskToolTip = self.tr( "Space separated list of wildcards, *.h *.cpp 
        file???.txt\n"
            "You can use language name too so the search will only apply to 
            the language suffixes.\n"
            "Available languages: %1" ).arg( languages.join( ", " ) )
        
        self.cbMask.setToolTip( maskToolTip )
        '''
        
        # codecs
        false_positives = set(["aliases"])
        foundCodecs = set(name for imp, name, ispkg in \
                        pkgutil.iter_modules(encodings.__path__) if not ispkg)
        foundCodecs.difference_update(false_positives)
        foundCodecs = sorted(list(foundCodecs))

        self.cbEncoding.addItems(foundCodecs)
        
        """TODO
        self.cbEncoding.setCurrentIndex( 
            self.cbEncoding.findText( pMonkeyStudio.defaultCodec() ) )
        """

        # connections
        self.cbSearch.lineEdit().textChanged.connect(self.search_textChanged)
        self.cbSearch.lineEdit().textEdited.connect(self.search_textEdited)
        self.tbCdUp.clicked.connect(self.cdUp_pressed)
        self.mSearchThread.started.connect(self.searchThread_stateChanged)
        self.mSearchThread.finished.connect(self.searchThread_stateChanged)
        self.mSearchThread.progressChanged.connect(\
                                        self.searchThread_progressChanged)
        self.mReplaceThread.started.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.finished.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.openedFileHandled.connect(\
                                        self.replaceThread_openedFileHandled)
        self.mReplaceThread.error.connect(self.replaceThread_error)
        
        core.actionModel().action("mNavigation/mSearchReplace/aSearchNext").triggered.connect(self.on_pbNext_pressed)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchPrevious").triggered.connect(self.on_pbPrevious_pressed)
        
        self.pbSearch.setEnabled(False)
        self.pbNext.setEnabled(False)
        self.pbPrevious.setEnabled(False)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchNext").setEnabled(False)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchPrevious").setEnabled(False)
        
        core.mainWindow().hideAllWindows.connect(self.hide)


    def setResultsDock(self, dock ):
        """Set to widget pointer to the search results dock
        """
        self.mDock = dock

        # connections
        self.mReplaceThread.resultsHandled.connect(\
                                    self.mDock.mModel.thread_resultsHandled)

    def setMode(self, mode ):
        """Change search mode.
        i.e. from "Search file" to "Replace directory"
        """
        self.mSearchThread.stop()
        self.mReplaceThread.stop()
        
        currentDocumentOnly = False
        
        # clear search results if needed.
        if mode & Plugin.ModeFlagFile:
            currentDocumentOnly = True
        else:
            currentDocumentOnly = False
            self.mSearchThread.clear()
        
        self.mMode = mode
        
        self.initializeSearchContext( currentDocumentOnly )
        """TODO
        if self.mMode & Plugin.ModeFlagProjectFiles :
            if  self.mSearchContext.project :
                encoding = self.mSearchContext.project.temporaryValue(
                "encoding", mks.monkeystudio.defaultCodec() ).toString()
                
                self.mSearchContext.encoding = encoding
                self.cbEncoding.setCurrentIndex( self.cbEncoding.findText(
                encoding ) )
        """
        assert( self.mSearchContext.encoding )
        
        searchPath = os.path.abspath(os.path.curdir)
        if core.workspace().currentDocument():
            searchText = core.workspace().currentDocument().\
                                                    qscintilla.selectedText()
        else:
            searchText = ''
        
        self.setVisible( mode != Plugin.ModeNo )

        if searchText:
            self.cbSearch.setEditText( searchText )
            self.cbReplace.setEditText( searchText )
            
        if  mode & Plugin.ModeFlagDirectory :
            self.cbPath.setEditText( searchPath )

        self.cbSearch.setFocus()
        self.cbSearch.lineEdit().selectAll()

        # hlamer: I'm sory for long lines, but, even workse without it
        # Set widgets visibility flag according to state
        widgets = (self.wSearch, self.pbPrevious, self.pbNext, self.pbSearch, self.wReplace, self.wPath, \
                   self.pbReplace, self.pbReplaceAll, self.pbReplaceChecked, self.wOptions, self.wMask, self.wEncoding,)
        #                                                       wSear  pbPrev pbNext pbSear wRepl  wPath  pbRep  pbRAll pbRCHK wOpti wMask wEncoding
        visible = {Plugin.ModeNo     :             (    0,     0,     0,     0,     0,     0,     0,     0,     0,    0,    0,    0,),
                   Plugin.ModeSearch :             (    1,     1,     1,     0,     0,     0,     0,     1,     1,    1,    0,    0,),
                   Plugin.ModeReplace:             (    1,     1,     1,     0,     1,     0,     1,     1,     0,    1,    0,    0,),
                   Plugin.ModeSearchDirectory:     (    1,     0,     0,     1,     0,     1,     0,     0,     0,    1,    1,    1,),
                   Plugin.ModeReplaceDirectory:    (    1,     0,     0,     1,     1,     1,     0,     0,     1,    1,    1,    1,),
                   Plugin.ModeSearchProjectFiles:  (    1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
                   Plugin.ModeSearchProjectFiles:  (    1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
                   Plugin.ModeReplaceProjectFiles: (    1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    1,),
                   Plugin.ModeSearchOpenedFiles:   (    1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    0,),
                   Plugin.ModeReplaceOpenedFiles:  (    1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    0,)}
        
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
                if self.mMode == Plugin.ModeNo:
                    pass
                elif self.mMode == Plugin.ModeSearch:
                    self.pbNext.click()
                elif self.mMode in (Plugin.ModeSearchDirectory, \
                                    Plugin.ModeSearchProjectFiles, \
                                    Plugin.ModeSearchOpenedFiles, \
                                    Plugin.ModeReplaceDirectory, \
                                    Plugin.ModeReplaceProjectFiles, \
                                    Plugin.ModeReplaceOpenedFiles):
                    if not self.mSearchThread.isRunning():
                        self.pbSearch.click()
                    else:
                        self.pbSearchStop.click()
                elif self.mMode == Plugin.ModeReplace:
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
    
    def initializeSearchContext(self, currentDocumentOnly ):
        """Fill search context with actual data
        """
        self.mSearchContext = SearchContext(\
            searchText = unicode(self.cbSearch.currentText()), \
            replaceText = unicode(self.cbReplace.currentText()), \
            searchPath = unicode(self.cbPath.currentText()), \
            mode = self.mMode,
            encoding = unicode(self.cbEncoding.currentText()))

        """TODO
        self.mSearchContext.project = 
            core.fileManager().currentProject()
        """
        
        # update masks
        self.mSearchContext.mask = \
            [unicode(s).strip() for s in self.cbMask.currentText().split(' ')]
        # remove empty
        self.mSearchContext.mask = filter(None, self.mSearchContext.mask)
        
        # update options
        for option in self.mModeActions.keys():
            if  self.mModeActions[option].isChecked() :
                self.mSearchContext.options |= option
        
        """TODO
        # update project
        self.mSearchContext.project = \
        self.mSearchContext.project.topLevelProject()
        """
        
        if  currentDocumentOnly :
            return

        # update opened files
        for document in core.workspace().openedDocuments():
            self.mSearchContext.openedFiles[document.filePath()] = \
                                        unicode(document.text())
        """TODO
        # update sources files
        self.mSearchContext.sourcesFiles = []
        if self.mSearchContext.project:
            self.mSearchContext.sourcesFiles = \
                        self.mSearchContext.project.topLevelProjectSourceFiles()
        """

    def showMessage (self, status):
        """Show message on the status bar"""
        if not status:
            core.mainWindow().statusBar().clearMessage()
        else:
            core.mainWindow().statusBar().showMessage( status, 30000 )

    def setState(self, field, state ):
        """Change line edit color according to search result
        """
        widget = 0
        color = QColor( Qt.white )
        
        if field == SearchWidget.Search:
            widget = self.cbSearch.lineEdit()
        elif field == SearchWidget.Replace:
            widget = self.cbReplace.lineEdit()
        
        widget = {SearchWidget.Search: self.cbSearch.lineEdit(),
                  SearchWidget.Replace: self.cbReplace.lineEdit()}
        
        color = {SearchWidget.Normal: Qt.white, \
                 SearchWidget.Good: Qt.green, \
                 SearchWidget.Bad: Qt.red}
        
        pal = widget[field].palette()
        pal.setColor( widget[field].backgroundRole(), color[state] )
        widget[field].setPalette( pal )
    
    def searchFile(self, forward, incremental ):
        """Do search in file operation. Will select next found item
        """
        document = core.workspace().currentDocument()
        if document:
            editor = document.qscintilla  # FIXME current editor specific, 
        else:
            self.setState( SearchWidget.Search, SearchWidget.Bad )
            self.showMessage( self.tr( "No active editor" ) )
            return False

        # get cursor position
        isRE = self.mSearchContext.options & Plugin.OptionRegularExpression
        isCS = self.mSearchContext.options & Plugin.OptionCaseSensitive
        isWW = self.mSearchContext.options & Plugin.OptionWholeWord
        isWrap = self.mSearchContext.options & Plugin.OptionWrap
        
        if  forward :
            if  incremental :
                line, col, temp, temp = editor.getSelection()
            else:
                temp, temp, line, col = editor.getSelection()
        else:
            if  incremental:
                temp, temp, line, col = editor.getSelection()
            else:
                line, col, temp, temp = editor.getSelection()
        
        # search
        found = editor.findFirst( self.mSearchContext.searchText, isRE, isCS, isWW, isWrap, forward, line, col, True )

        # change background acording to found or not
        if found:
            self.setState( SearchWidget.Search, SearchWidget.Good)
        else:
            self.setState( SearchWidget.Search, SearchWidget.Bad)
        
        # return found state
        return found

    def replaceFile(self, replaceAll ):
        """Do one or all replacements in the file
        """
        document = core.workspace().currentDocument()
        if document:
            editor = document.qscintilla  # FIXME current editor specific
        
        if  not editor :
            self.setState( SearchWidget.Search, SearchWidget.Bad )
            self.showMessage( self.tr( "No active editor" ) )
            return False

        count = 0
        
        if  replaceAll:
            isWrap = self.mSearchContext.options & Plugin.OptionWrap
            col, line = editor.getCursorPosition()

            if  isWrap :
                # don't need to give wrap parameter for search as we start at begin of document
                editor.setCursorPosition( 0, 0 )
                self.mSearchContext.options &= ~Plugin.OptionWrap

            editor.beginUndoAction()
            
            count = 0
            while ( self.searchFile( True, False ) ): # search next
                editor.replace( self.mSearchContext.replaceText )
                count += 1

            editor.endUndoAction()
            editor.setCursorPosition(col, line) # restore cursor position
            
            # restore wrap property if needed
            if  isWrap :
                self.mSearchContext.options |= Plugin.OptionWrap
        else:
            line, col, temp, temp = editor.getSelection()
            editor.setCursorPosition( line, col )

            if  self.searchFile( True, False ) :
                editor.beginUndoAction()
                editor.replace( self.mSearchContext.replaceText )
                editor.endUndoAction()
                count += 1
                self.pbNext.click() # move selection to next item

        self.showMessage( self.tr( "%d occurrence(s) replaced." % count ))

        return True

    def searchThread_stateChanged(self):
        """Search thread started or stopped
        """
        self.pbSearchStop.setVisible( self.mSearchThread.isRunning() )
        self.pbSearch.setVisible( not self.mSearchThread.isRunning() )
        self.updateWidgets()
        self.mProgress.setVisible( self.mSearchThread.isRunning() )

    def searchThread_progressChanged(self, value, total ):
        """Signal from the thread, progress changed
        """
        self.mProgress.setValue( value )
        self.mProgress.setMaximum( total )

    def replaceThread_stateChanged(self):
        """Replace thread started or stopped
        """
        self.pbReplaceCheckedStop.setVisible( self.mReplaceThread.isRunning() )
        self.pbReplaceChecked.setVisible( not self.mReplaceThread.isRunning() )
        self.updateWidgets()

    def replaceThread_openedFileHandled(self, fileName, content, encoding ):
        """Replace thread processed currently opened file,
        need update text in the editor
        """
        document = core.workspace().openFile(fileName)
        editor = document.qscintilla  # FIXME current editor specific

        editor.beginUndoAction()
        editor.selectAll()
        editor.removeSelectedText()
        editor.insert( content )
        editor.endUndoAction()


    def replaceThread_error(self, error ):
        """Error message from the replace thread
        """
        core.messageManager().appendMessage( error )

    def search_textChanged(self):
        """Text changed, enable actions, if have text, disable, if haven't
        """
        haveText = bool(self.cbSearch.currentText())
        
        self.pbSearch.setEnabled(haveText)
        self.pbNext.setEnabled(haveText)
        self.pbPrevious.setEnabled(haveText)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchNext").setEnabled(haveText)
        core.actionModel().action("mNavigation/mSearchReplace/aSearchPrevious").setEnabled(haveText)
    
    def search_textEdited(self):
        """User edited search text, do incremental search
        """
        self.initializeSearchContext( True )
            
        # clear search results if needed.
        if self.mMode == Plugin.ModeSearch:
            self.searchFile( True, True )
        elif self.mMode == Plugin.ModeReplace:
            self.mSearchThread.clear()

    def cdUp_pressed(self):
        """User pressed "Up" button, need to remove one level from search path
        """
        if not os.path.exists(self.cbPath.currentText()):
            return

        self.cbPath.setEditText( os.path.abspath(self.cbPath.currentText() + os.path.pardir))

    def on_pbPrevious_pressed(self):
        """Handler of click on "Previous" button
        """
        self.updateComboBoxes()
        self.initializeSearchContext( True )
        self.searchFile( False, False )

    def on_pbNext_pressed(self):
        """Handler of click on "Next" button
        """
        self.updateComboBoxes()
        self.initializeSearchContext( True )
        self.searchFile( True, False )

    def on_pbSearch_pressed(self):
        """Handler of click on "Search" button (for search in directory)
        """
        self.setState( SearchWidget.Search, SearchWidget.Normal )
        self.updateComboBoxes()
        self.initializeSearchContext( False )
        
        assert self.mSearchContext.searchText
        
        """TODO
        if  self.mSearchContext.mMode & Plugin.ModeFlagProjectFiles and not self.mSearchContext.project :
            core.messageManager().appendMessage( \
                                self.tr( "You can't search in project files because there is no opened projet." ) )
            return
        """

        self.mSearchThread.search( self.mSearchContext )

    def on_pbSearchStop_pressed(self):
        """Handler of click on "Stop" button. Stop search thread
        """
        self.mSearchThread.stop()

    def on_pbReplace_pressed(self):
        """Handler of click on "Replace" (in file) button
        """
        self.updateComboBoxes()
        self.initializeSearchContext( True )
        self.replaceFile( False )

    def on_pbReplaceAll_pressed(self):
        """Handler of click on "Replace all" (in file) button
        """
        self.updateComboBoxes()
        self.initializeSearchContext( True )
        self.replaceFile( True )

    def on_pbReplaceChecked_pressed(self):
        """Handler of click on "Replace checked" (in directory) button
        """
        items = {}
        model = self.mDock.mModel

        self.updateComboBoxes()
        self.initializeSearchContext( False )
        """TODO
        if  self.mSearchContext.mode & Plugin.ModeFlagProjectFiles and not self.mSearchContext.project :
            core.messageManager().appendMessage(
                                    self.tr( "You can't replace in project files because there is no opened projet." ) )
            return
        """

        for fileRes in model.fileResults:
            for row, result in enumerate(fileRes.results):
                if result.enabled and result.checkState == Qt.Checked :
                    if not result.fileName in items:
                        items[result.fileName] = []
                    items[ result.fileName ].append(result)
                else:
                    index = model.createIndex(row, 0, result)
                    self.mDock.mModel.setData( index, False, SearchResultsModel.EnabledRole )

        self.mReplaceThread.replace( self.mSearchContext, items )

    def on_pbReplaceCheckedStop_pressed(self):
        """Handler of click on "Stop" button when replacing in directory
        """
        self.mReplaceThread.stop()

    def on_pbBrowse_pressed(self):
        """Handler of click on "Browse" button. Explores FS for search directory path
        """
        path = QFileDialog.getExistingDirectory( self, self.tr( "Search path" ), self.cbPath.currentText() )

        if path:
            self.cbPath.setEditText( path )

    
class SearchResultsModel(QAbstractItemModel):
    """AbstractItemModel used for display search results in 'Search in directory' and 'Replace in directory' mode
    """
    firstResultsAvailable = pyqtSignal()
    
    EnabledRole = Qt.UserRole
    
    class Result:
        """One found by search thread item. Consists coordinates and capture. Used by SearchResultsModel
        """
        def __init__ (  self, \
                        fileName, \
                        capture, \
                        groups,
                        line, \
                        column, \
                        offset,
                        length):
            self.fileName = fileName
            self.capture = capture
            self.groups = groups
            self.line = line
            self.column = column
            self.offset = offset
            self.length = length
            self.checkState =  Qt.Checked
            self.enabled = True
        
        def text(self, notUsed):
            """Displayable text of search result. Shown as line in the search results dock
            notUsed argument added for have same signature, as FileResults.text
            """
            return "Line: %d, Column: %d: %s" % ( self.line + 1, self.column, self.capture )
        
        def tooltip(self):
            """Tooltip of the search result"""
            return self.capture
        
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
        self.mRowCount = 0
        self.mSearchThread = searchThread
        
        self.fileResults = []  # list of FileResults
        self.mSearchDir = QDir()
        
        # connections
        self.mSearchThread.reset.connect(self.clear)
        self.mSearchThread.resultsAvailable.connect(self.thread_resultsAvailable)

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

    def columnCount(self, parent ):
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
        properties = self.mSearchThread.mSearchContext

        if properties.mode & Plugin.ModeFlagReplace :
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
            return self.tr( index.internalPointer().text(self.mSearchDir))
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
        New result is available, need to add it to the model
        """
        properties = self.mSearchThread.mSearchContext
        if not self.fileResults:  # appending first
            self.firstResultsAvailable.emit()
            self.mSearchDir.setPath( properties.searchPath )
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

        self.mSearchThread = searchThread

        self.setObjectName( self.metaObject().className() )
        self.setWindowTitle( self.tr( "Search Results" ) )
        self.setWindowIcon( QIcon(":/mksicons/search.png") )
        
        # actions
        # clear action
        aClear = QAction( self.tr( "Clear results list" ), self )
        aClear.setIcon( QIcon(":/mksicons/clear-list.png"))
        aClear.setToolTip( aClear.text() )
        self.titleBar().addAction( aClear, 0 )
        
        # add separator
        self.titleBar().addSeparator( 1 )

        widget = QWidget( self )
        self.mModel = SearchResultsModel( searchThread, self )
        self.mView = QTreeView( self )
        self.mView.setHeaderHidden( True )
        self.mView.setUniformRowHeights( True )
        self.mView.setModel( self.mModel )
        self.mLayout = QHBoxLayout( widget )
        self.mLayout.setMargin( 5 )
        self.mLayout.setSpacing( 5 )
        self.mLayout.addWidget( self.mView )

        self.setWidget( widget )
        self.setFocusProxy(self.mView)
        
        """TODO
        # mac
        self.pMonkeyStudio.showMacFocusRect( self, False, True )
        pMonkeyStudio.setMacSmallSize( self, True, True )
        """

        # connections
        aClear.triggered.connect(self.mModel.clear)
        self.mModel.firstResultsAvailable.connect(self.show)
        self.mView.activated.connect(self.view_activated)
        
        self.showAction().setShortcut("F10")
        core.actionModel().addAction("mDocks/aSearchResults", self.showAction())

    def __term__(self):
        core.actionModel().removeAction("mDocks/aSearchResults")

    def view_activated(self, index ):
        """Item doubleclicked in the model, opening file
        """
        result = index.internalPointer()
        if isinstance(result, SearchResultsModel.Result):
            core.workspace().goToLine( result.fileName,
                                       result.line,
                                       result.column,
                                       result.length)

class StopableThread(QThread):
    """Stoppable thread class. Used as base for search and replace thread.
    """
    mExit = False
    
    def __init__(self, parentObject):
        QThread.__init__(self, parentObject)
    
    def __del__(self):
        self.stop()

    def stop(self):
        """Stop thread synchronously
        """
        self.mExit = True
        self.wait()
    
    def start(self):
        """Ensure thread is stopped, and start it
        """
        self.stop()
        self.mExit = False
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
        self.mSearchContext = context
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
        for root, dirs, files in os.walk(os.path.abspath(unicode(path))):
            if root.startswith('.') or (os.path.sep + '.') in root:
                continue
            for fileName in files:
                if fileName.startswith('.'):
                    continue
                if not maskRegExp or maskRegExp.match(fileName):
                    retFiles.append(root + os.path.sep + fileName)
            if self.mExit :
                break

        return retFiles
    
    def _getFilesToScan(self):
        """Get list of files for search.
        """
        files = set()

        """
        elif mode in (Plugin.ModeSearchProjectFiles, Plugin.ModeReplaceProjectFiles):
            sources = self.mSearchContext.sourcesFiles
            mask = self.mSearchContext.mask

            for fileName in sources:
                if  QDir.match( mask, fileName ) :
                    files.append(fileName)
                    if self.mExit :
                        return files
        """
        if self.mSearchContext.mask:
            regExPatterns = map(fnmatch.translate, self.mSearchContext.mask)
            maskRegExpPattern = '(' + ')|('.join(regExPatterns) + ')'
            maskRegExp = re.compile(maskRegExpPattern)
        else:
            maskRegExp = None

        if self.mSearchContext.mode in (Plugin.ModeSearchDirectory, Plugin.ModeReplaceDirectory):
            path = self.mSearchContext.searchPath
            return self._getFiles(path, maskRegExp)
        elif self.mSearchContext.mode in \
                                (Plugin.ModeSearchOpenedFiles, Plugin.ModeReplaceOpenedFiles):
            files = self.mSearchContext.openedFiles.keys()
            if maskRegExp:
                files = filter(maskRegExp.match, map(os.path.basename, files))
            return files
        else:
            assert(0)

    def _fileContent(self, fileName, encoding='utf_8'):
        """Read text from file
        """
        if fileName in self.mSearchContext.openedFiles:
            return self.mSearchContext.openedFiles[ fileName ]

        try:
            with open(fileName) as openedFile:
                if  isBinary(openedFile):
                    return ''
                return unicode(openedFile.read(), encoding, errors = 'ignore')
        except IOError, ex:
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

        if  self.mExit :
            return
        
        self.progressChanged.emit( 0, len(files))
        
        # Prepare data for search process
        eol = "\n"
        
        regExp = self.mSearchContext.regExp()
        
        lastResultsEmitTime = time.clock()
        notEmittedFileResults = []
        # Search for all files
        for fileIndex, fileName in enumerate(files):
            content = self._fileContent( fileName )

            lastPos = 0
            eolCount = 0
            results = []
            
            # Process result for all occurrences
            for match in regExp.finditer(content):
                start = match.start()
                
                eolStart = content.rfind( eol, 0, start)
                eolEnd = content.find( eol, start)
                eolCount += content[lastPos:start].count( eol )
                lastPos = start
                
                capture = content[eolStart + 1:eolEnd].strip()
                column = start - eolStart
                if eolStart != 0:
                    column -= 1
                
                result = SearchResultsModel.Result( fileName = fileName, \
                                 capture = capture, \
                                 groups = match.groups(), \
                                 line = eolCount, \
                                 column = column, \
                                 offset = start, \
                                 length = match.end() - start)
                
                results.append(result)

                if self.mExit:
                    break

            if  results:
                notEmittedFileResults.append(SearchResultsModel.FileResults(fileName, results))

            if notEmittedFileResults and \
               (time.clock() - lastResultsEmitTime) > self.RESULTS_EMIT_TIMEOUT:
                self.progressChanged.emit( fileIndex, len(files))
                self.resultsAvailable.emit(notEmittedFileResults)
                notEmittedFileResults = []
                lastResultsEmitTime = time.clock()

            if  self.mExit :
                self.progressChanged.emit( fileIndex, len(files))
                break
        
        if notEmittedFileResults:
            self.resultsAvailable.emit(notEmittedFileResults)
        
        print "Search finished in ", time.clock() - startTime        


class ReplaceThread(StopableThread):
    """Thread does replacements in the directory according to checked items
    """
    resultsHandled = pyqtSignal(unicode, list)
    openedFileHandled = pyqtSignal(unicode, unicode, unicode)
    error = pyqtSignal(unicode)
    
    def replace(self, context, results):
        """Run replace process
        """
        self.stop()
        self.mSearchContext = context
        self.mResults = results
        self.start()

    def _saveContent(self, fileName, content, encoding):
        """Write text to the file
        """
        if encoding:
            try:
                content = content.encode(encoding)
            except UnicodeEncodeError, ex:
                pattern = unicode(self.tr("Failed to encode file to %s: %s"), 'utf_8')
                text = unicode(str(ex), 'utf_8')
                self.error.emit(pattern % (encoding, text))
                return
        try:
            with open(fileName, 'w') as openFile:
                openFile.write(content)
        except IOError, ex:
            pattern = unicode(self.tr("Error while saving replaced content: %s"), 'utf_8')
            text = unicode(str(ex), 'utf_8')
            self.error.emit(pattern % text)

    def _fileContent(self, fileName, encoding=None):
        """Read file
        """
        if fileName in self.mSearchContext.openedFiles:
            return self.mSearchContext.openedFiles[ fileName ]
        else:
            try:
                with open(fileName) as openFile:
                    content = openFile.read()
            except IOError, ex:
                self.error.emit( self.tr( "Error opening file: %s" % str(ex) ) )
                return ''
            
            if encoding:
                try:
                    return unicode(content, encoding)
                except UnicodeDecodeError, ex:
                    self.error.emit(self.tr( "File %s not read: unicode error '%s'. File may be corrupted" % \
                                    (fileName, str(ex) ) ))
                    return ''
            else:
                return content

    def run(self):
        """Start point of the code, running i thread
        Does thread job
        """
        startTime = time.clock()
        
        subMatchRex = re.compile( r"\\(\d+)" )
        
        for fileName in self.mResults.keys():
            handledResults = []
            content = self._fileContent( fileName, self.mSearchContext.encoding )
            
            # count from end to begin because we are replacing by offset in content
            for result in self.mResults[ fileName ][::-1]:
                replaceText = self.mSearchContext.replaceText
                # replace \number with groups
                if self.mSearchContext.options & Plugin.OptionRegularExpression:
                    replaceText = self.mSearchContext.replaceText
                    pos = 0
                    match = subMatchRex.search(replaceText)
                    while match:
                        index = int(match.group(1))
                        if index in range(1, len(result.groups) + 1):
                            replaceText = replaceText[:pos + match.start()] + \
                                          result.groups[index - 1] + \
                                          replaceText[pos + match.start() + len(match.group(0)):]
                        pos += (match.start() + len(result.groups[index - 1]))
                        match = subMatchRex.search(replaceText[pos:])
                
                # replace text
                content = content[:result.offset] + replaceText + content[result.offset + result.length:]
                handledResults.append(result)
            
            if fileName in self.mSearchContext.openedFiles:
                self.openedFileHandled.emit( fileName, content, self.mSearchContext.encoding )
            else:
                self._saveContent( fileName, content, self.mSearchContext.encoding )
            
            self.resultsHandled.emit( fileName, handledResults)

            if  self.mExit :
                break

        print "Replace finished in ", time.clock() - startTime
