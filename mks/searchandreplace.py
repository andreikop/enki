"""Search and Replace plugin. S&R GUI and implementation
"""

import os.path
import threading
import re
import time
import pkgutil
import encodings

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QDir, QEvent, QIODevice, QModelIndex, \
                        QObject, QRect, QRegExp, QSize, Qt, \
                        QTextCodec, QThread, QVariant
from PyQt4.QtGui import QAction, QCompleter, QColor, QDirModel, QFileDialog,  \
                        QFrame, QFileDialog, QHBoxLayout, QIcon, QKeyEvent, QLineEdit, QPainter,  \
                        QProgressBar, QToolButton, QTreeView, QWidget
from PyQt4.fresh import *

import mks.monkeycore

def isBinary(file ):
    """Expects, that file position is 0, when exits, file position is 0
    """
    binary = '\0' in file.read( 4096 )
    file.seek(0)
    return binary


class SearchAndReplace(QObject):  # TODO (Plugin) ?
    
    ModeFlagSearch = 0x1
    ModeFlagReplace = 0x2
    ModeFlagFile = 0x4
    ModeFlagDirectory = 0x8
    ModeFlagProjectFiles = 0x10
    ModeFlagOpenedFiles = 0x11

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
        self.widget = SearchWidget( self )
        
        # List if search actions. First acition created by MainWindow, so, do not fill text
        self.actions = (("aSearchFile", "", "", "", "", self.modeSwitchTriggered, self.ModeSearch),
                        ("aSearchDirectory", "Search in &Directory...", "search-replace-directory.png", "Ctrl+Shift+F", "Search in directory...", self.modeSwitchTriggered, self.ModeSearchDirectory),
                        ("aReplaceDirectory", "Replace in Director&y...", "search-replace-directory.png", "Ctrl+Shift+R", "Replace in directory...", self.modeSwitchTriggered, self.ModeReplaceDirectory),
                        ("aReplaceFile", "&Replace...", "replace.png", "Ctrl+R", "Replace in the current file...", self.modeSwitchTriggered, self.ModeReplace),
                        ("aSearchPrevious", "Search &Previous", "previous.png", "Shift+F3", "Search previous occurrence", self.widget.on_pbPrevious_clicked, None),
                        ("aSearchNext", "Search &Next", "next.png", "F3", "Search next occurrence", self.widget.on_pbNext_clicked, None))
        """TODO
                        ("aSearchProjectFiles", "Search in Project &Files...", "search-replace-project-files.png", "Ctrl+Meta+F", "Search in the current project files..", self.modeSwitchTriggered, self.ModeSearchProjectFiles),
                        ("aReplaceProjectFiles", "Replace in Projec&t Files...", "search-replace-project-files.png", "Ctrl+Meta+R", "Replace in the current project files...", self.modeSwitchTriggered, self.ModeReplaceProjectFiles),
                        ("aSearchOpenedFiles", "Search in &Opened Files...", "search-replace-opened-files.png", "Ctrl+Alt+Meta+F", "Search in opened files...", self.modeSwitchTriggered, self.ModeSearchOpenedFiles),
                        ("aReplaceOpenedFiles", "Replace in Open&ed Files...", "search-replace-opened-files.png", "Ctrl+Alt+Meta+R", "Replace in opened files...", self.modeSwitchTriggered, self.ModeReplaceOpenedFiles))
        """

        
        mks.monkeycore.workspace().layout().addWidget( self.widget )
        self.widget.setVisible( False )
        
        self.dock = SearchResultsDock( self.widget.searchThread() )
        mks.monkeycore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( self.dock, self.dock.windowTitle(), self.dock.windowIcon() )
        self.dock.setVisible( False )

        self.widget.setResultsDock( self.dock )
        
        mb = mks.monkeycore.menuBar()
        
        mb.beginGroup( "mEdit/mSearchReplace" )
        for action in self.actions:
            actObject = mb.action(action[0], self.tr(action[1]), QIcon(':/mksicons/' + action[2]), self.tr(action[3]), self.tr(action[4]))
            actObject.triggered.connect(action[5])
            actObject.setData(action[6])
        mb.endGroup()

    def __del__(self):
        """Plugin termination
        """
        mb = mks.monkeycore.menuBar()
        
        mb.beginGroup( "mEdit/mSearchReplace" )
        for action in self.actions:
            mb.action( action[0]).deleteLater()
        mb.endGroup()
    
    def modeSwitchTriggered(self):
        newMode = self.sender().data().toInt()[0]
        # TODO if  ( document and document.editor() ) or not document :
        if newMode & SearchAndReplace.ModeFlagFile:
            # TODO check if editor is a QScintilla
            self.widget.setMode(newMode)
        elif newMode & SearchAndReplace.ModeFlagDirectory:
            self.widget.setMode(newMode)
        elif newMode & SearchAndReplace.ModeFlagProjectFiles:  # TODO
            pass
        elif newMode & SearchAndReplace.ModeFlagOpenedFiles:
            if mks.workspace.openedDocuments():  # TODO check if have file based document
                self.widget.setMode(newMode)


class Properties:  # TODO rework it
    searchText = ''
    replaceText = ''
    searchPath = ''
    mode = 0
    mask = []
    codec = ''
    options = 0
    openedFiles = {}
    project = None
    sourcesFiles = ''


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
        QFrame.__init__(self, mks.monkeycore.workspace())
        self.plugin = plugin
        uic.loadUi('mks/SearchWidget.ui', self)
        
        self.mProperties = Properties()
        
        self.cbSearch.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.cbReplace.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.fsModel = QDirModel( self )
        self.fsModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self.cbPath.lineEdit().setCompleter( QCompleter( self.fsModel ) )
        #warning QDirModel is deprecated but QCompleter does not yet handle QFileSystemModel - please update when possible.
        self.cbMask.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.pbSearchStop.setVisible( False )
        self.pbReplaceCheckedStop.setVisible( False )
        
        self.mProgress = QProgressBar( self )
        self.mProgress.setAlignment( Qt.AlignCenter )
        self.mProgress.setToolTip( self.tr( "Search in progress..." ) )
        self.mProgress.setMaximumSize( QSize( 80, 16 ) )
        mks.monkeycore.mainWindow().statusBar().insertPermanentWidget( 0, self.mProgress )
        self.mProgress.setVisible( False )
        
        # threads
        self.mSearchThread = SearchThread( self )
        self.mReplaceThread = ReplaceThread( self )

        self.mDock = 0
        
        # mode actions
        self.tbMode = QToolButton( self.cbSearch.lineEdit() )
        self.tbMode.setIcon( QIcon( ":/mksicons/misc.png" ) )
        self.tbMode.setPopupMode( QToolButton.InstantPopup )
        self.tbMode.setMenu( mks.monkeycore.menuBar().menu( "mEdit/mSearchReplace" ) )
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
        self.mModeActions[ SearchAndReplace.OptionCaseSensitive ] = action
        
        action = QAction( self.cbWholeWord )
        action.setCheckable( True )
        self.cbWholeWord.toggled.connect(action.setChecked)
        self.mModeActions[ SearchAndReplace.OptionWholeWord ] = action
        
        action = QAction( self.cbWrap )
        action.setCheckable( True )
        self.cbWrap.toggled.connect(action.setChecked)
        self.mModeActions[ SearchAndReplace.OptionWrap ] = action
        
        action = QAction( self.cbRegularExpression )
        action.setCheckable( True )
        self.cbRegularExpression.toggled.connect(action.setChecked)
        self.mModeActions[ SearchAndReplace.OptionRegularExpression ] = action
        
        # init default options
        self.cbWrap.setChecked( True )
        
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
        
        """TODO
        # mask tooltip
        languages = pMonkeyStudio.availableLanguages()
        
        for ( i = 0; i < languages.count(); i += 10 )
            languages[ i ].prepend( "\n" )

        
        maskToolTip = self.tr( "Space separated list of wildcards, *.h *.cpp file???.txt\n"
            "You can use language name too so the search will only apply to the language suffixes.\n"
            "Available languages: %1" ).arg( languages.join( ", " ) )
        
        self.cbMask.setToolTip( maskToolTip )
        """
        
        # codecs
        false_positives = set(["aliases"])
        foundCodecs = set(name for imp, name, ispkg in pkgutil.iter_modules(encodings.__path__) if not ispkg)
        foundCodecs.difference_update(false_positives)
        foundCodecs = sorted(list(foundCodecs))

        self.cbCodec.addItems(foundCodecs)
        
        """TODO
        self.cbCodec.setCurrentIndex( self.cbCodec.findText( pMonkeyStudio.defaultCodec() ) )
        """

        # connections
        self.cbSearch.lineEdit().textEdited.connect(self.search_textChanged)
        self.tbCdUp.clicked.connect(self.cdUp_clicked)
        self.mSearchThread.started.connect(self.searchThread_stateChanged)
        self.mSearchThread.finished.connect(self.searchThread_stateChanged)
        self.mSearchThread.progressChanged.connect(self.searchThread_progressChanged)
        self.mReplaceThread.started.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.finished.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.openedFileHandled.connect(self.replaceThread_openedFileHandled)
        self.mReplaceThread.error.connect(self.replaceThread_error)
        self.setMode( SearchAndReplace.ModeSearch )

    def mode(self):  # FIXME remove
        return self.mMode

    def searchThread(self):  # FIXME remove
        return self.mSearchThread

    def setResultsDock(self, dock ):
        if  self.mDock == dock :
            return

        self.mDock = dock

        # connections
        self.mReplaceThread.resultsHandled.connect(self.mDock.model().thread_resultsHandled)

    def setMode(self, mode ):
        self.mSearchThread.stop()
        self.mReplaceThread.stop()
        
        currentDocumentOnly = False
        
        # clear search results if needed.
        if mode & SearchAndReplace.ModeFlagFile:
            currentDocumentOnly = True
        else:
            currentDocumentOnly = False
            self.mSearchThread.clear()
        
        self.mMode = mode
        
        self.initializeProperties( currentDocumentOnly )
        
        if self.mMode & SearchAndReplace.ModeFlagProjectFiles :
            if  self.mProperties.project :
                codec = self.mProperties.project.temporaryValue( "codec", mks.monkeystudio.defaultCodec() ).toString()
                
                self.mProperties.codec = codec
                self.cbCodec.setCurrentIndex( self.cbCodec.findText( codec ) )

        assert( self.mProperties.codec )
        
        document = mks.monkeycore.workspace().currentDocument()
        editor = document.qscintilla  # FIXME
        # TODO editor = document ? document.editor() : 0
        searchPath = os.path.abspath(os.path.curdir)
        if editor:
            searchText = editor.selectedText()
        else:
            searchText = ''
        
        wasVisible = self.isVisible()

        self.setVisible( mode != SearchAndReplace.ModeNo )

        if  self.isVisible() :
            if searchText:
                self.cbSearch.setEditText( searchText )

            if  mode & SearchAndReplace.ModeFlagSearch :
                self.cbSearch.setFocus()
                self.cbSearch.lineEdit().selectAll()
            else:
                self.cbReplace.setFocus()
                self.cbReplace.lineEdit().selectAll()
            
            if  mode & SearchAndReplace.ModeFlagDirectory :
                self.cbPath.setEditText( searchPath )
        
        # hlamer: I'm sory for long lines, but, even workse without it
        # Set widgets visibility flag according to state
        widgets = (self.wSearch, self.pbPrevious, self.pbNext, self.pbSearch, self.wReplace, self.wPath, \
                   self.pbReplace, self.pbReplaceAll, self.pbReplaceChecked, self.wOptions, self.wMask, self.wCodec,)
        #                                                       wSear  pbPrev pbNext pbSear wRepl  wPath  pbRep  pbRAll pbRCHK wOpti wMask wCodec
        visible = {SearchAndReplace.ModeNo     :             (    0,     0,     0,     0,     0,     0,     0,     0,     0,    0,    0,    0,),
                   SearchAndReplace.ModeSearch :             (    1,     1,     1,     0,     0,     0,     0,     1,     1,    1,    0,    0,),
                   SearchAndReplace.ModeReplace:             (    1,     1,     1,     0,     1,     0,     1,     1,     0,    1,    0,    0,),
                   SearchAndReplace.ModeSearchDirectory:     (    1,     0,     0,     1,     0,     1,     0,     0,     0,    1,    1,    1,),
                   SearchAndReplace.ModeReplaceDirectory:    (    1,     0,     0,     1,     1,     1,     0,     0,     1,    1,    1,    1,),
                   SearchAndReplace.ModeSearchProjectFiles:  (    1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
                   SearchAndReplace.ModeSearchProjectFiles:  (    1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
                   SearchAndReplace.ModeReplaceProjectFiles: (    1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    1,),
                   SearchAndReplace.ModeSearchOpenedFiles:   (    1,     0,     0,     1,     1,     0,     0,     0,     0,    1,    1,    0,),
                   SearchAndReplace.ModeReplaceOpenedFiles:  (    1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    0,)}
        
        for i, widget in enumerate(widgets):
            widget.setVisible(visible[mode][i])

        self.updateLabels()
        self.updateWidgets()

    def eventFilter(self, object, event ):
        if  event.type() == QEvent.Paint :
            toolButton = object
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

        return QFrame.eventFilter( self, object, event )


    def keyPressEvent(self, event ):
        if  event.modifiers() == Qt.NoModifier :
            if event.key() == Qt.Key_Escape:
                mks.monkeycore.workspace().focusCurrentDocument()
                self.hide()
            elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if self.mMode == SearchAndReplace.ModeNo:
                    pass
                elif self.mMode == SearchAndReplace.ModeSearch:
                        self.pbNext.click()
                elif self.mMode in (SearchAndReplace.ModeSearchDirectory, \
                                    SearchAndReplace.ModeSearchProjectFiles, \
                                    SearchAndReplace.ModeSearchOpenedFiles):
                    self.pbSearch.click()
                elif self.mMode == SearchAndReplace.ModeReplace:
                    self.pbReplace.click()
                elif self.mMode in (SearchAndReplace.ModeReplaceDirectory, \
                                    SearchAndReplace.ModeReplaceProjectFiles, \
                                    SearchAndReplace.ModeReplaceOpenedFiles):
                    self.pbReplaceChecked.click()

        QFrame.keyPressEvent( self, event )

    def updateLabels(self):
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
    
    def initializeProperties(self, currentDocumentOnly ):
        """TODO
        suffixes = pMonkeyStudio.availableLanguagesSuffixes()
        keys = suffixes.keys()
        """
        self.mProperties.searchText = self.cbSearch.currentText()
        self.mProperties.replaceText = self.cbReplace.currentText()
        self.mProperties.searchPath = self.cbPath.currentText()
        self.mProperties.mode = self.mMode
        self.mProperties.mask = []
        self.mProperties.codec = unicode(self.cbCodec.currentText())
        self.mProperties.options = SearchAndReplace.ModeNo
        self.mProperties.openedFiles = {}
        """TODO
        self.mProperties.project = mks.monkeycore.fileManager().currentProject()
        """
        self.mProperties.sourcesFiles = {}
        
        """TODO
        # update masks
        for part in self.cbMask.currentText().split( " ", QString.SkipEmptyParts ):
            index = keys.index( QRegExp( QRegExp.escape( part ), Qt.CaseInsensitive ) )

            if  index != -1 :
                foreach (  QString& suffixe, suffixes[ keys[index] ] )
                    if  not suffixe in self.mProperties.mask:
                        self.mProperties.mask << suffixe
            else:
                self.mProperties.mask << part
        """

        # set default mask if needed
        if  self.mProperties.mask:
            self.mProperties.mask.append("*")

        # update options
        for option in self.mModeActions.keys():
            if  self.mModeActions[option].isChecked() :
                self.mProperties.options |= option
        
        """TODO
        # update project
        self.mProperties.project = self.mProperties.project.topLevelProject()
        """
        
        if  currentDocumentOnly :
            return

        # update opened files
        for document in mks.monkeycore.workspace().openedDocuments():
            self.mProperties.openedFiles[document.filePath()] = unicode(document.fileBuffer())

        # update sources files
        self.mProperties.sourcesFiles = []
        if self.mProperties.project:
            self.mProperties.sourcesFiles = self.mProperties.project.topLevelProjectSourceFiles()

    def showMessage (self, status ):
        if not status:
            mks.monkeycore.mainWindow().statusBar().clearMessage()
        else:
            mks.monkeycore.mainWindow().statusBar().showMessage( status, 30000 )

    def setState(self, field, state ):
        widget = 0
        color = QColor( Qt.white )
        
        if field == SearchWidget.Search:
            widget = self.cbSearch.lineEdit()
        elif field == SearchWidget.Replace:
            widget = self.cbReplace.lineEdit()
        
        widget= {SearchWidget.Search: self.cbSearch.lineEdit(),
                 SearchWidget.Replace: self.cbReplace.lineEdit()}
        
        color = {SearchWidget.Normal: Qt.white, \
                 SearchWidget.Good: Qt.green, \
                 SearchWidget.Bad: Qt.red}
        
        pal = widget[field].palette()
        pal.setColor( widget[field].backgroundRole(), color[state] )
        widget[field].setPalette( pal )
    
    def searchFile(self, forward, incremental ):
        document = mks.monkeycore.workspace().currentDocument()
        if document:
            editor = document.qscintilla  # FIXME current editor specific, 
        else:
            self.setState( SearchWidget.Search, SearchWidget.Bad )
            self.showMessage( self.tr( "No active editor" ) )
            return False

        # get cursor position
        isRE = self.mProperties.options & SearchAndReplace.OptionRegularExpression
        isCS = self.mProperties.options & SearchAndReplace.OptionCaseSensitive
        isWW = self.mProperties.options & SearchAndReplace.OptionWholeWord
        isWrap = self.mProperties.options & SearchAndReplace.OptionWrap
        
        if  forward :
            if  incremental :
                x, y, temp, temp = editor.getSelection()
            else:
                temp, temp, y, x = editor.getSelection()
        else:
            if  incremental:
                temp, temp, y, x = editor.getSelection()
            else:
                y, x, temp, temp = editor.getSelection()
        
        # search
        found = editor.findFirst( self.mProperties.searchText, isRE, isCS, isWW, isWrap, forward, y, x, True )

        # change background acording to found or not
        if found:
            self.setState( SearchWidget.Search, SearchWidget.Good)
        else:
            self.setState( SearchWidget.Search, SearchWidget.Bad)
        
        # return found state
        return found

    def replaceFile(self, all ):
        document = mks.monkeycore.workspace().currentDocument()
        if document:
            editor = document.qscintilla  # FIXME current version specific
        
        if  not editor :
            self.setState( SearchWidget.Search, SearchWidget.Bad )
            self.showMessage( self.tr( "No active editor" ) )
            return False

        count = 0
        
        if  all :
            isWrap = self.mProperties.options & SearchAndReplace.OptionWrap
            x, y = editor.getCursorPosition(y, x)

            if  isWrap :
                # don't need to give wrap parameter for search as we start at begin of document
                editor.setCursorPosition( 0, 0 )
                self.mProperties.options &= ~SearchAndReplace.OptionWrap

            editor.beginUndoAction()
            
            count = 0
            while ( self.searchFile( True, False ) ): # search next
                editor.replace( self.mProperties.replaceText )
                count += 1

            editor.endUndoAction()
            editor.setCursorPosition( y, x ) # restore cursor position
            
            # restore wrap property if needed
            if  isWrap :
                self.mProperties.options |= SearchAndReplace.OptionWrap

        else:
            y, x, temp, temp = editor.getSelection()
            editor.setCursorPosition( y, x )

            if  self.searchFile( True, False ) :
                editor.beginUndoAction()
                editor.replace( self.mProperties.replaceText )
                editor.endUndoAction()
                count += 1
                self.pbNext.click(); # move selection to next item

        self.showMessage( self.tr( "%d occurrence(s) replaced." % count ))

        return True

    def searchThread_stateChanged(self):
        self.pbSearchStop.setVisible( self.mSearchThread.isRunning() )
        self.updateWidgets()
        self.mProgress.setVisible( self.mSearchThread.isRunning() )

    def searchThread_progressChanged(self, value, total ):
        self.mProgress.setValue( value )
        self.mProgress.setMaximum( total )

    def replaceThread_stateChanged(self):
        self.pbReplaceCheckedStop.setVisible( self.mReplaceThread.isRunning() )
        self.updateWidgets()

    def replaceThread_openedFileHandled(self, fileName, content, codec ):
        document = mks.monkeycore.workspace().openFile(fileName, codec)
        editor = document.qscintilla  # FIXME

        editor.beginUndoAction()
        editor.selectAll()
        editor.removeSelectedText()
        editor.insert( content )
        editor.endUndoAction()


    def replaceThread_error(self, error ):
        mks.monkeycore.messageManager().appendMessage( error )

    def search_textChanged(self):
        self.initializeProperties( True )
        
        # clear search results if needed.
        if self.mMode == SearchAndReplace.ModeSearch:
            self.searchFile( True, True )
        elif self.mMode == SearchAndReplace.ModeReplace:
            self.mSearchThread.clear()

    def cdUp_clicked(self):
        
        if not os.path.exists(self.cbPath.currentText()):
            return

        self.cbPath.setEditText( os.path.abspath(self.cbPath.currentText() + os.path.pardir))

    def on_pbPrevious_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.searchFile( False, False )

    def on_pbNext_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.searchFile( True, False )

    def on_pbSearch_pressed(self):
        self.setState( SearchWidget.Search, SearchWidget.Normal )
        self.updateComboBoxes()
        self.initializeProperties( False )
        
        if not self.mProperties.searchText:
            mks.monkeycore.messageManager().appendMessage( self.tr( "You can't search for NULL text." ) )
            return

        if  self.mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not self.mProperties.project :
            mks.monkeycore.messageManager().appendMessage( self.tr( "You can't search in project files because there is no opened projet." ) )
            return

        self.mSearchThread.search( self.mProperties )

    def on_pbSearchStop_clicked(self):
        self.mSearchThread.stop()

    def on_pbReplace_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.replaceFile( False )

    def on_pbReplaceAll_pressed(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.replaceFile( True )

    def on_pbReplaceChecked_pressed(self):
        items = {}
        model = self.mDock.model()

        self.updateComboBoxes()
        self.initializeProperties( False )
        
        if  self.mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not self.mProperties.project :
            mks.monkeycore.messageManager().appendMessage( self.tr( "You can't replace in project files because there is no opened projet." ) )
            return

        for fileRes in model.fileResults:
            for row, result in enumerate(fileRes.results):
                if result.enabled and result.checkState == Qt.Checked :
                    if not result.fileName in items:
                        items[result.fileName] = []
                    items[ result.fileName ].append(result)
                else:
                    index = model.createIndex(row, 0, result)
                    self.mDock.model().setData( index, False, SearchResultsModel.EnabledRole )

        self.mReplaceThread.replace( self.mProperties, items )

    def on_pbReplaceCheckedStop_clicked(self):
        self.mReplaceThread.stop()

    def on_pbBrowse_clicked(self):
        path = QFileDialog.getExistingDirectory( self, self.tr( "Search path" ), self.cbPath.currentText() )

        if path:
            self.cbPath.setEditText( path )


class SearchThread(QThread):
    RESULTS_EMIT_TIMEOUT = 1.0

    reset = pyqtSignal()
    resultsAvailable = pyqtSignal(list)  # list of SearchResultsModel.FileResults
    progressChanged = pyqtSignal(int, int)  # int value, int total

    def __init__(self, parentObject):
        QThread.__init__(self, parentObject)
        self.mExit = False
    
    def __del__(self):
        self.stop()

    def search(self, properties ):
        self.mProperties = properties
        self.stop()
        self.mExit = False
        self.start()

    def stop(self):
        """Stops thread synchronously
        """
        self.mExit = True
        self.wait()

    def clear(self):
        self.stop()
        self.reset.emit()            

    def _getFiles(self, path, filters):
        retFiles = []
        for root, dirs, files in os.walk(os.path.abspath(unicode(path))):
            if root.startswith('.'):
                continue
            for fileName in files:
                if fileName.startswith('.'):
                    continue
                if not filters or QDir.match(filters, fileName):
                    retFiles.append(root + os.path.sep + fileName)
            if self.mExit :
                break

        return retFiles
    
    def _getFilesToScan(self):
        files = set()

        """
        elif mode in (SearchAndReplace.ModeSearchProjectFiles, SearchAndReplace.ModeReplaceProjectFiles):
            sources = self.mProperties.sourcesFiles
            mask = self.mProperties.mask

            for fileName in sources:
                if  QDir.match( mask, fileName ) :
                    files.append(fileName)
                    if self.mExit :
                        return files
        elif mode in (SearchAndReplace.ModeSearchOpenedFiles, SearchAndReplace.ModeReplaceOpenedFiles):
            sources = self.mProperties.openedFiles.keys()
            mask = self.mProperties.mask

            for fileName in sources:
                if  QDir.match( mask, fileName ) :
                    files.append(fileName)
                    if self.mExit :
                        return files
        """

        if self.mProperties.mode in (SearchAndReplace.ModeSearchDirectory, SearchAndReplace.ModeReplaceDirectory):
            path = self.mProperties.searchPath
            mask = self.mProperties.mask
            return self._getFiles(path, mask)
        else:
            print "Invalid mode used."  # TODO use some logging system?
            assert(0)

    def _fileContent(self, fileName, codec=''):
        if fileName in self.mProperties.openedFiles:
            return self.mProperties.openedFiles[ fileName ]

        try:
            with open(fileName) as f:
                if  isBinary(f):
                    return ''
                return unicode(f.read(), codec, errors = 'ignore')
        except IOError, ex:
            print ex
            return ''

    def run(self):
        startTime = time.clock()
        self.reset.emit()
        self.progressChanged.emit( -1, 0 )

        files = self._getFilesToScan()
        files.sort()

        if  self.mExit :
            return
        
        self.progressChanged.emit( 0, len(files))
        
        # Prepare data for search process
        eol = "\n"
        pattern = unicode(self.mProperties.searchText)
        flags = 0
        
        if not self.mProperties.options & SearchAndReplace.OptionRegularExpression:  # not reg exp
            pattern = re.escape( pattern )
        
        if self.mProperties.options & SearchAndReplace.OptionWholeWord:  # whole word
            pattern.prepend( "\\b" ).append( "\\b" )
        
        if not self.mProperties.options & SearchAndReplace.OptionCaseSensitive:  # not case sensetive
            flags = re.IGNORECASE
        
        lastResultsEmitTime = time.clock()
        notEmittedFileResults = []
        # Search for all files
        for fileIndex, fileName in enumerate(files):
            content = self._fileContent( fileName )

            lastPos = 0
            eolCount = 0
            results = []
            
            # Process result for all occurrences
            for match in re.finditer(pattern, content, flags):
                start = match.start()
                
                eolStart = content.rfind( eol, 0, start)
                eolEnd = content.find( eol, start)
                eolCount += content[lastPos:start].count( eol )
                lastPos = start
                
                capture = content[eolStart + 1:eolEnd - 1].strip()
                column = start - eolStart
                if eolStart != 0:
                    column -= 1
                
                result = SearchResultsModel.Result( fileName = fileName, \
                                 capture = capture, \
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
    
class SearchResultsModel(QAbstractItemModel):

    firstResultsAvailable = pyqtSignal()
    
    EnabledRole = Qt.UserRole
    
    class Result:
        def __init__ (  self, \
                        fileName, \
                        capture, \
                        line, \
                        column, \
                        offset,
                        length):
                self.fileName = fileName;
                self.capture = capture;
                self.line = line;
                self.column = column;
                self.offset = offset;
                self.length = length;
                self.checkState =  Qt.Checked
                self.enabled = True;
        
        def text(self, notUsed):
            return "Line: %d, Column: %d: %s" % ( self.line + 1, self.column, self.capture )
        
        def tooltip(self):
            return self.capture
        
        def hasChildren(self):
            return False

    class FileResults:
        def __init__(self, fileName, results):
            self.fileName = fileName
            self.results = results
            self.checkState = Qt.Checked
        
        def __str__(self):
            return '%s (%d)' % (self.fileName, len(self.results))
        
        def updateCheckState(self):
            if all([res.checkState == Qt.Checked for res in self.results]):  # if all checked
                self.checkState = Qt.Checked
            elif any([res.checkState == Qt.Checked for res in self.results]):  # if any checked
                self.checkState = Qt.PartiallyChecked
            else:
                self.checkState = Qt.Unchecked
        
        def text(self, baseDir):
            return '%s (%d)' % (baseDir.relativeFilePath(self.fileName), len(self.results))
        
        def tooltip(self):
            return self.fileName
        
        def hasChildren(self):
            return 0 != len(self.results)
    
    def __init__(self, searchThread, parent ):
        QAbstractItemModel.__init__(self, parent )
        self.mRowCount = 0
        self.mSearchThread = searchThread
        
        self.fileResults = []  # list of FileResults
        self.mSearchDir = QDir()
        
        # connections
        self.mSearchThread.reset.connect(self.thread_reset)
        self.mSearchThread.resultsAvailable.connect(self.thread_resultsAvailable)

    def index(self, row, column, parent ):
        if  row >= self.rowCount( parent ) or column > self.columnCount(parent):
            return QModelIndex()
        
        if parent.isValid():  # index for result
            result = parent.internalPointer().results[row]
            return self.createIndex( row, column, result )
        else:  # need index for fileRes
            return self.createIndex( row, column, self.fileResults[row])

    def parent(self, index):
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
        # root parents
        if item.isValid():
            return item.internalPointer().hasChildren()
        else:
            return len(self.fileResults) != 0

    def columnCount(self, parent ):
        return 1
    
    def rowCount(self, parent):
        if not parent.isValid():  # root elements
            return len(self.fileResults)
        elif isinstance(parent.internalPointer(), SearchResultsModel.Result):  # result
            return 0
        elif isinstance(parent.internalPointer(), self.FileResults):  # file
            return len(parent.internalPointer().results)
        else:
            assert(0)
    
    def flags(self, index ):
        flags = QAbstractItemModel.flags( self, index )
        properties = self.mSearchThread.mProperties

        if properties.mode & SearchAndReplace.ModeFlagReplace :
            flags |= Qt.ItemIsUserCheckable
        
        if isinstance(index.internalPointer(), SearchResultsModel.Result):
            if not index.internalPointer().enabled :
                flags &= ~Qt.ItemIsEnabled
                flags &= ~Qt.ItemIsSelectable
        
        return flags
    
    def data(self, index, role ):
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
        self.beginRemoveRows(QModelIndex(), 0, len(self.fileResults) - 1)
        self.fileResults = []
        self.endRemoveRows()

    def thread_reset(self):
        self.clear()

    def thread_resultsAvailable(self, fileResultsList ):
        properties = self.mSearchThread.mProperties
        if not self.fileResults:  # appending first
            self.firstResultsAvailable.emit()
            self.mSearchDir.setPath( properties.searchPath )
        self.beginInsertRows( QModelIndex(), \
                              len(self.fileResults), \
                              len(self.fileResults) + len(fileResultsList) - 1)
        self.fileResults.extend(fileResultsList)
        self.endInsertRows()
    
    def thread_resultsHandled(self, fileName, results):
        for index, fileRes in enumerate(self.fileResults):  # try to find FileResults
            if fileRes.fileName == fileName:  # found
                fileResIndex = self.createIndex(index, 0, fileRes)
                for res in results:  # TODO make optimisation - if removing all results - do not remove one by one
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
    
    def __init__(self, searchThread, parent=None):
        pDockWidget.__init__( self, parent )
        assert(searchThread)

        self.mSearchThread = searchThread

        self.setObjectName( self.metaObject().className() )
        self.setWindowTitle( self.tr( "Search Results" ) )
        self.setWindowIcon( QIcon(":/mksicons/SearchAndReplace.png") )
        
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
        
        """TODO
        # mac
        self.pMonkeyStudio.showMacFocusRect( self, False, True )
        pMonkeyStudio.setMacSmallSize( self, True, True )
        """

        # connections
        aClear.triggered.connect(self.mModel.clear)
        self.mModel.firstResultsAvailable.connect(self.show)
        self.mView.activated.connect(self.view_activated)

    def model(self):
        return self.mModel

    def view_activated(self, index ):
        result = index.internalPointer()
        if isinstance(result, SearchResultsModel.Result):
            mks.monkeycore.workspace().goToLine( result.fileName,
                                                 (result.line, result.column,),
                                                 self.mSearchThread.mProperties.codec,
                                                 result.length)  # FIXME check this code result.offset == -1 ? 0 : result.length

class ReplaceThread(QThread):
    resultsHandled = pyqtSignal(unicode, list)
    openedFileHandled = pyqtSignal(unicode, unicode, unicode)
    error = pyqtSignal(unicode)
    
    def __init__(self, parent):
        QThread.__init__(self, parent)

    def __del__(self):
        self.stop()

    def replace(self, properties, results):
        self.stop()
        self.mProperties = properties
        self.mResults = results
        self.mExit = False
        self.start()

    def stop(self):
        self.mExit = True
        self.wait()

    def _saveContent(self, fileName, content, encoding):  # use Python functionality?
        if encoding:
            try:
                content = unicode(content, encoding)
            except UnicodeEncodeError, ex:
                self.error.emit( self.tr( "Failed to encode file to %s: %s" % (codec, str(ex)) ) )
                return
        try:
            with open(fileName, 'w') as f:
                f.write(content)
        except IOError, ex:
            self.error.emit( self.tr( "Error while saving replaced content: %s" % str(ex) ) )

    def _fileContent(self, fileName, encoding=None):
        if fileName in self.mProperties.openedFiles:
            return self.mProperties.openedFiles[ fileName ]

        try:
            with open(fileName) as f:
                content = f.read()
        except IOError, ex:
            self.error.emit( self.tr( "Error opening file: %s" % str(ex) ) )
            return ''
        
        if encoding:
            try:
                content = unicode(content, encoding)
            except UnicodeDecodeError, ex:
                self.error.emit(self.tr( "File %s not read: unicode error '%s'. File may be corrupted" % \
                                (fileName, str(ex) ) ))
                return ''

    def run(self):
        startTime = time.clock()
        pattern = unicode(self.mProperties.searchText)
        flags = 0
        
        if not self.mProperties.options & SearchAndReplace.OptionRegularExpression:  # not reg exp
            pattern = re.escape( pattern )
        
        if self.mProperties.options & SearchAndReplace.OptionWholeWord:  # whole word
            pattern.prepend( "\\b" ).append( "\\b" )
        
        if not self.mProperties.options & SearchAndReplace.OptionCaseSensitive:  # not case sensetive
            flags = re.IGNORECASE
        
        for fileName in self.mResults.keys():
            handledResults = []
            content = self._fileContent( fileName, self.mProperties.codec )
            
            for result in self.mResults[ fileName ][::-1]:  # count from end to begin because we are replacing by offset in content
                
                if self.mProperties.options & SearchAndReplace.OptionRegularExpression:  # replace \number with groups
                    replaceText = re.sub(self.mProperties.searchText, \
                                         self.mProperties.replaceText, \
                                         result.capture)
                else:
                    replaceText = self.mProperties.replaceText
                
                # replace text
                content = content[:result.offset] + replaceText + content[result.offset + result.length:]
                handledResults.append(result)
            
            if fileName in self.mProperties.openedFiles:
                self.openedFileHandled.emit( fileName, content, self.mProperties.codec )
            else:
                self._saveContent( fileName, content, self.mProperties.codec )
            
            self.resultsHandled.emit( fileName, handledResults)

            if  self.mExit :
                break

        print "Replace finished in ", time.clock() - startTime
