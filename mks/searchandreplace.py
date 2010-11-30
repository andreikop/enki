"""Search and Replace plugin. S&R GUI and implementation
"""

import os.path
import threading

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QDir, QEvent, QFile, QIODevice, QModelIndex, \
                        QMutex, QMutexLocker, \
                        QObject, QPoint, QRect, QRegExp, QSize, QString, QStringList, Qt, QTime, \
                        QTextCodec, QThread, QVariant
from PyQt4.QtGui import QAction, QCompleter, QColor, QDirModel, QFileDialog,  \
                        QFrame, QFileDialog, QHBoxLayout, QIcon, QKeyEvent, QLineEdit, QPainter,  \
                        QProgressBar, QToolButton, QTreeView, QWidget
from PyQt4.fresh import *

import mks.monkeycore

def isBinary(file ):
    position = file.pos()
    file.seek( 0 )
    binary = '\0' in file.read( 4096 )
    file.seek( position )
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
                        ("aReplaceFile", "&Replace...", "edit/replace.png", "Ctrl+R", "Replace in the current file...", self.modeSwitchTriggered, self.ModeReplace),
                        ("aSearchPrevious", "Search &Previous", "edit/previous.png", "Shift+F3", "Search previous occurrence", self.widget.on_pbPrevious_clicked, None),
                        ("aSearchNext", "Search &Next", "edit/next.png", "F3", "Search next occurrence", self.widget.on_pbNext_clicked, None))
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
            actObject = mb.action(action[0], self.tr(action[1]), mks.monkeystudio.getIcon(action[2]), self.tr(action[3]), self.tr(action[4]))
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
        self.tbMode.setIcon( mks.monkeystudio.getIcon( "build/misc.png" ) )
        self.tbMode.setPopupMode( QToolButton.InstantPopup )
        self.tbMode.setMenu( mks.monkeycore.menuBar().menu( "mEdit/mSearchReplace" ) )
        self.tbMode.setCursor( Qt.ArrowCursor )
        self.tbMode.installEventFilter( self )
        
        # cd up action
        self.tbCdUp = QToolButton( self.cbPath.lineEdit() )
        self.tbCdUp.setIcon( mks.monkeystudio.getIcon( "listeditor/go-up.png" ) )
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
        slist = QStringList()
        for c in sorted(QTextCodec.availableCodecs()):
            slist.append(QString(c))
        self.cbCodec.addItems(slist)
        
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
        returnself.mMode

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
                codec = self.mProperties.project.temporaryValue( "codec", pMonkeyStudio.defaultCodec() ).toString()
                
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
        self.mProperties.codec = self.cbCodec.currentText()
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
            self.mProperties.openedFiles[document.filePath()] = document.fileBuffer()

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
        document = mks.monkeycore.fileManager().openFile( fileName, codec )
        editor = document.editor()

        assert( editor )

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

    def on_pbSearch_clicked(self):
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

    def on_pbReplaceAll_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.replaceFile( True )

    def on_pbReplaceChecked_clicked(self):
        items = {}
        model = self.mDock.model()

        self.updateComboBoxes()
        self.initializeProperties( False )
        
        if  self.mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not self.mProperties.project :
            mks.monkeycore.messageManager().appendMessage( self.tr( "You can't replace in project files because there is no opened projet." ) )
            return

        for results in model.results():
            for result in results:
                if  result.enabled and result.checkState == Qt.Checked :
                    if not result.fileName in items:
                        items[result.fileName] = []
                    items[ result.fileName ].append(result)
                else:
                    index = model._index( result )
                    self.mDock.model().setData( index, False, SearchResultsModel.EnabledRole )

        self.mReplaceThread.replace( self.mProperties, items )

    def on_pbReplaceCheckedStop_clicked(self):
        self.mReplaceThread.stop()

    def on_pbBrowse_clicked(self):
        path = QFileDialog.getExistingDirectory( self, self.tr( "Search path" ), self.cbPath.currentText() )

        if path:
            self.cbPath.setEditText( path )


class SearchThread(QThread):
    mMaxTime = 125

    reset = pyqtSignal()
    resultsAvailable = pyqtSignal(QString, list)  # QString filename, list of results
    progressChanged = pyqtSignal(int, int)  # int value, int total

    def __init__(self, parentObject):
        QThread.__init__(self, parentObject)
        self.mReset = False
        self.mExit = False
        self.lock = threading.Lock()
        
        # FIXME what to do with it?
        # qRegisterMetaType(ResultList, "ResultList" )

    def __del__(self):
        self.stop()
        self.wait()

    def search(self, properties ):
        with self.lock:
            self.mProperties = properties
            self.mReset = self.isRunning()
            self.mExit = False

        if  not self.isRunning() :
            self.start()

    def stop(self):
        with self.lock:
            self.mReset = False
            self.mExit = True

    def properties(self):
        with self.lock:
            return self.mProperties

    def getFiles(self, fromDir, filters, recursive ):
        files = []
        
        # TODO replace with python functionality
        for file in fromDir.entryInfoList( QDir.AllEntries | QDir.AllDirs | QDir.NoDotAndDotDot, QDir.DirsFirst | QDir.Name ):
            if  file.isFile() and ( (not filters) or QDir.match( filters, file.fileName() ) ) :
                files.append(file.absoluteFilePath())
            elif  file.isDir() and recursive:
                fromDir.cd( file.filePath() )
                files.extend(self.getFiles( fromDir, filters, recursive ))
                fromDir.cdUp()

                with self.lock:
                    if  self.mReset or self.mExit :
                        return files
        return files
    
    def getFilesToScan(self):
        files = set()
        mode = SearchAndReplace.ModeNo

        with self.lock:
            mode = self.mProperties.mode

        if mode in (SearchAndReplace.ModeNo, SearchAndReplace.ModeSearch, SearchAndReplace.ModeReplace):
            print "Invalid mode used."  # TODO use some logging system?
            assert(0)
        elif mode in (SearchAndReplace.ModeSearchDirectory, SearchAndReplace.ModeReplaceDirectory):
            with self.lock:
                path = self.mProperties.searchPath
                mask = self.mProperties.mask
            files = list(set(self.getFiles( QDir (path), mask, True )))  # list(set()) for clear duplicates
        elif mode in (SearchAndReplace.ModeSearchProjectFiles, SearchAndReplace.ModeReplaceProjectFiles):
            with self.lock:
                sources = self.mProperties.sourcesFiles
                mask = self.mProperties.mask

            for fileName in sources:
                if  QDir.match( mask, fileName ) :
                    files.append(fileName)
                with self.lock:
                    if  self.mReset or self.mExit :
                        return files
        elif mode in (SearchAndReplace.ModeSearchOpenedFiles, SearchAndReplace.ModeReplaceOpenedFiles):
            with self.lock:
                sources = self.mProperties.openedFiles.keys()
                mask = self.mProperties.mask

            for fileName in sources:
                if  QDir.match( mask, fileName ) :
                    files.append(fileName)
                    with self.lock:
                        if  self.mReset or self.mExit :
                            return files
        return files

    def fileContent(self, fileName ):
        codec = 0

        with self.lock:
            codec = QTextCodec.codecForName( self.mProperties.codec.toLocal8Bit() )

            if fileName in self.mProperties.openedFiles:
                return self.mProperties.openedFiles[ fileName ]

        assert( codec )

        file = QFile ( fileName )

        if  not file.open( QIODevice.ReadOnly ) :
            return ''

        if  isBinary( file ) :
            return ''

        return codec.toUnicode( file.readAll() )

    def _search(self, fileName, content ):
        eol = "\n"
        checkable = False
        isRE = False
        rx = QRegExp()
        
        with self.lock:

            isRE = self.mProperties.options & SearchAndReplace.OptionRegularExpression
            isWw = self.mProperties.options & SearchAndReplace.OptionWholeWord
            isCS = self.mProperties.options & SearchAndReplace.OptionCaseSensitive
            if isCS:
                sensitivity = Qt.CaseSensitive
            else:
                sensitivity = Qt.CaseInsensitive
            checkable = self.mProperties.mode & SearchAndReplace.ModeFlagReplace
            if isRE:
                pattern = self.mProperties.searchText
            else:
                pattern = QRegExp.escape( self.mProperties.searchText )

            if  isWw :
                pattern.prepend( "\\b" ).append( "\\b" )

            rx.setMinimal( True )
            rx.setPattern( pattern )
            rx.setCaseSensitivity( sensitivity )

        pos = 0
        lastPos = 0
        eolCount = 0
        results = []
        tracker = QTime()

        tracker.start()
        
        pos = rx.indexIn( content, pos )
        while pos != -1:
            eolStart = content.lastIndexOf( eol, pos )
            eolEnd = content.indexOf( eol, pos )
            capture = content.mid( eolStart + 1, eolEnd -1 -eolStart ).simplified()
            eolCount += content.mid( lastPos, pos -lastPos ).count( eol )
            column = pos - eolStart
            if eolStart != 0:
                column -= 1
            
            result = Result( fileName, capture )
            result.position = QPoint( column, eolCount )
            result.offset = pos
            result.length = rx.matchedLength()
            result.checkable = checkable
            if checkable:
                result.checkState =  Qt.Checked
            else:
                result.checkState =  Qt.Unchecked
            
            if isRE:
                result.capturedTexts =  rx.capturedTexts()
            else:
                result.capturedTexts = []
            
            results.append(result)

            lastPos = pos
            pos += rx.matchedLength()

            if  tracker.elapsed() >= self.mMaxTime :
                self.resultsAvailable.emit( fileName, results )
                results = []
                tracker.restart()

            with self.lock:
                if  self.mReset or self.mExit :
                    return
            pos = rx.indexIn( content, pos )

        if  results:
            self.resultsAvailable.emit( fileName, results )

    def run(self):
        tracker = QTime()

        while True:  # FIXME replace with better loop
            with self.lock:
                self.mReset = False
                self.mExit = False

            self.reset.emit()
            self.progressChanged.emit( -1, 0 )
            tracker.restart()

            files = self.getFilesToScan()
            files.sort()

            with self.lock:
                if  self.mExit :
                    return
                elif  self.mReset :
                    continue
            
            total = len(files)
            value = 0
            
            self.progressChanged.emit( 0, total )

            for fileName in files:
                content = self.fileContent( fileName )
                self._search( fileName, content )
                value += 1
                
                self.progressChanged.emit( value, total )

                with self.lock:
                    if  self.mExit :
                        return
                    elif  self.mReset :
                        break

            with self.lock:
                if  self.mReset :
                    continue
            break

        print "Search finished in ", tracker.elapsed() /1000.0

    def clear(self):
        self.stop()
        self.reset.emit()

class Result:
    def __init__ (  self, \
                    _fileName = '', \
                    _capture = '', \
                    _position = QPoint(), \
                    _offset = -1, \
                    _length = 0, \
                    _checkable = False, \
                    _checkState = Qt.Unchecked, \
                    _enabled = True, \
                    _capturedTexts = []):
            self.fileName = _fileName;
            self.capture = _capture;
            self.position = _position;
            self.offset = _offset;
            self.length = _length;
            self.checkable = _checkable;
            self.checkState = _checkState;
            self.enabled = _enabled;
            self.capturedTexts = _capturedTexts;

class SearchResultsModel(QAbstractItemModel):

    firstResultsAvailable = pyqtSignal()
    
    EnabledRole = Qt.UserRole
    
    def __init__(self, searchThread, parent ):
        QAbstractItemModel.__init__(self, parent )
        self.mRowCount = 0
        self.mSearchThread = searchThread
        
        self.mResults = []
        self.mParents = {}
        self.mParentsList = []
        self.mRowCount = 0
        self.mSearchDir = QDir()
        
        # connections
        self.mSearchThread.reset.connect(self.thread_reset)
        self.mSearchThread.resultsAvailable.connect(self.thread_resultsAvailable)

    def columnCount(self, parent ):
        return 1

    def data(self, index, role ):
        if  not index.isValid() :
            return QVariant()

        result = self.result( index )
        assert(result)

        if role == Qt.DisplayRole:
            # index is a root parent
            if result in self.mParentsList:
                count = self.rowCount( index )
                text = self.mSearchDir.relativeFilePath( result.fileName )
                text.append(" (%d)"  % count)
            else:  # index is a root parent child
                text = self.tr( "Line: %d, Column: %d: %s" % ( result.position.y() +1, result.position.x(), result.capture ))
            return text
        elif role == Qt.ToolTipRole:
            return result.capture
        elif role == Qt.CheckStateRole:
            if  self.flags( index ) & Qt.ItemIsUserCheckable :
                return result.checkState

        return QVariant()

    def index(self, row, column, parent ):
        if  row >= self.rowCount( parent ) or column >= self.columnCount( parent ) :
            return QModelIndex()

        result = self.result( parent )

        # parent is a root parent
        if  result and self.mParentsList[parent.row()] == result :
            result = self.mResults[parent.row()][row]
            return self.createIndex( row, column, result )

        assert (not parent.isValid())

        # parent is invalid
        return self.createIndex( row, column, self.mParentsList[ row ] )

    def parent(self, index ):
        if not index.isValid() :
            return QModelIndex()

        result = self.result( index )
        assert(result)

        # index is a root parent
        if result in self.mParentsList:
            return QModelIndex()

        assert( index.isValid() )

        result = self.mParents[ result.fileName ]
        row = self.mParentsList.index( result )

        # index is a root parent child
        return self.createIndex( row, index.column(), result )

    def rowCount(self, parent ):
        # root parents
        if  not parent.isValid() :
            return self.mRowCount
        
        if parent.parent().isValid():
            return 0
        else:
            if parent.row() < len (self.mResults):
                return len(self.mResults[parent.row()])
            else:
                return 0

    def flags(self, index ):
        flags = QAbstractItemModel.flags( self, index )
        properties = self.mSearchThread.properties()

        if  properties.mode & SearchAndReplace.ModeFlagReplace :
            flags |= Qt.ItemIsUserCheckable

        result = self.result( index )

        if  result :
            if  not result.enabled :
                flags &= ~Qt.ItemIsEnabled
                flags &= ~Qt.ItemIsSelectable

        return flags

    def hasChildren(self, parent ):
        # root parents
        if  not parent.isValid() :
            return self.mRowCount != 0
        
        if parent.parent().isValid():
           return False
        else:
            if parent.row() < len(self.mResults):
                return bool(self.mResults[parent.row()])
            else:
                return False

    def setData(self, index, value, role ):
        result = self.result( index )

        if role == Qt.CheckStateRole:
            ok = True
        elif role == SearchResultsModel.EnabledRole:
            result.enabled = value
            ok = True
        else:
            ok = False

        if  role != Qt.CheckStateRole :
            if  ok :
                self.dataChanged.emit( index, index )

            return ok

        state = Qt.CheckState( value.toInt()[0] )
        pIndex = index.parent()
        isParent = not pIndex.isValid()
        pResult = self.result( pIndex )

        assert( result )

        if  isParent :
            pRow = self.mParentsList.index( result )
            checkedCount = 0

            # update all children to same state as parent
            for r in self.mResults[pRow]:
                if  r.enabled :
                    r.checkState = state
                    checkedCount += 1

            left = index.child( 0, 0 )
            right = index.child( self.rowCount( index ) -1, self.columnCount( index ) -1 )
            # update root parent children
            self.dataChanged.emit( left, right )

            if  state == Qt.Unchecked :
                checkedCount = 0

            if  ( checkedCount == 0 and state == Qt.Checked ) or result.checkState == state :
                ok = False

            if  ok :
                result.checkState = state
        else:
            pRow = self.mParentsList.index( pResult )
            count = 0
            checkedCount = 0

            for r in self.mResults[pRow]:
                count += 1

                if  r.checkState == Qt.Checked :
                    checkedCount += 1
            
            if  state == Qt.Checked :
                checkedCount += 1
            else:
                checkedCount -= 1

            result.checkState = state

            # update parent
            if  checkedCount == 0 :
                pResult.checkState = Qt.Unchecked
            elif  checkedCount == count :
                pResult.checkState = Qt.Checked
            else:
                pResult.checkState = Qt.PartiallyChecked

            # update root parent index
            self.dataChanged.emit( pIndex, pIndex )

        # update clicked index
        self.dataChanged.emit( index, index )

        return ok

    def _index(self, result ):
        if result in self.mParentsList:
            row = self.mParentsList.index(  )
            return self.createIndex( row, 0, result )
        elif  result :
            pResult = self.mParents[result.fileName]

            if  pResult :
                row = self.mParentsList.index( pResult )

                if  row != -1 :
                    row = self.mResults[row].index( result )
                    return self.createIndex( row, 0, result )

        return QModelIndex
    
    def result(self, index ):
        if index.isValid():
            return index.internalPointer()
        else:
            return None
    
    def results(self):
        return self.mResults

    def clear(self):
        if  self.mRowCount == 0 :
            return

        self.beginRemoveRows( QModelIndex(), 0, self.mRowCount -1 )
        
        self.mResults = []  # clear
        self.mParents = {}
        self.mParentsList = []
        self.mRowCount = 0
        
        self.endRemoveRows()

    def thread_reset(self):
        self.clear()

    def thread_resultsAvailable(self, fileName, results ):
        if  self.mRowCount == 0 :
            self.firstResultsAvailable.emit()
        
        properties = self.mSearchThread.properties()
        
        if  self.mRowCount == 0 :
            self.mSearchDir.setPath( properties.searchPath )

        if not fileName in self.mParents:
            result = Result( fileName )
            result.checkable = properties.mode & SearchAndReplace.ModeFlagReplace
            if result.checkable:
                result.checkState = Qt.Checked
            else:
                result.checkState = Qt.Unchecked
            self.beginInsertRows( QModelIndex(), self.mRowCount, self.mRowCount )
            self.mParents[ fileName ] = result
            self.mParentsList.append(result)
            self.mRowCount += 1
            self.mResults.append(results)
            self.endInsertRows()
        else:
            result = self.mParents[ fileName ]
            pRow = self.mParentsList.index( result )
            count = len(self.mResults[pRow])
            index = self.createIndex( pRow, 0, result )

            self.beginInsertRows( index, count, count +results.count() -1 )
            self.mResults[ pRow ].append(results)
            self.endInsertRows()

            self.dataChanged.emit( index, index )

    def thread_resultsHandled(self, fileName, results ):
        pResult = self.mParents[fileName]
        assert( pResult )

        pRow = self.mParentsList.index( pResult )
        children = self.mResults[ pRow ]
        pIndex = self.createIndex( pRow, 0, pResult )

        # remove root parent children
        for result in results:
            index = children.index( result )
            self.beginRemoveRows( pIndex, index, index )
            children.pop( index )
            self.endRemoveRows()

        # remove root parent
        if not children:
            self.beginRemoveRows( QModelIndex(), pRow, pRow )
            self.mResults.pop( pRow )
            self.mParentsList.pop( pRow )
            self.mRowCount -= 1
            self.endRemoveRows()
        else:
            pResult.checkState = Qt.Unchecked
            self.dataChanged.emit( pIndex, pIndex )

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
        mks.monkeycore.workspace().goToLine( result.fileName,
                                         result.position,
                                         self.mSearchThread.properties().codec,
                                         result.length )  # FIXME check this code result.offset == -1 ? 0 : result.length

class ReplaceThread(QThread):
    mMaxTime = 125
    
    resultsHandled = pyqtSignal(QString, list)
    openedFileHandled = pyqtSignal(QString, QString, QString)
    error = pyqtSignal(QString)
    
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.mReset = False
        self.mExit = False
        self.mProperties = Properties()
        self.mResults = {}
        self.lock = threading.Lock()

    def __del__():  # check if it is not done by QThread
        self.stop()
        self.wait()

    def replace(self, properties, results):
        with self.lock:
            self.mProperties = properties
            self.mResults = results
            self.mReset = self.isRunning()
            self.mExit = False

        if  not self.isRunning() :
            self.start()

    def stop(self):
        with self.lock:
            self.mReset = False
            self.mExit = True

    def saveContent(self, fileName, content, codec ):  # use Python functionality?
        file = QFile( fileName )

        if not file.open( QIODevice.WriteOnly ) :
            self.error.emit( self.tr( "Error while saving replaced content: %s" % file.errorString() ) )
            return

        file.resize( 0 )

        textCodec = QTextCodec.codecForName( codec.toLocal8Bit() )

        assert( textCodec )

        if  file.write( textCodec.fromUnicode( content ) ) == -1 :
            self.error.emit( self.tr( "Error while saving replaced content: %s") % file.errorString() )
            return

        file.close()

    def fileContent(self, fileName ):
        codec = 0

        with self.lock:
            codec = QTextCodec.codecForName( self.mProperties.codec.toLocal8Bit() )
            if fileName in self.mProperties.openedFiles:
                return self.mProperties.openedFiles[ fileName ]

        assert( codec )

        file = QFile (fileName)

        if  not file.open( QIODevice.ReadOnly ) :
            return QString.null

        if  isBinary( file ) :
            return QString.null

        return codec.toUnicode( file.readAll() )

    def replace_(self, fileName, content ):
        handledResults = []
        
        with self.lock:
            replaceText = self.mProperties.replaceText
            codec = self.mProperties.codec
            results = self.mResults[ fileName ]
            isOpenedFile = fileName in self.mProperties.openedFiles
            isRE = self.mProperties.options & SearchAndReplace.OptionRegularExpression

        '''
            QTime tracker
            tracker.start()
        '''
        
        rx = QRegExp ( "\\$(\\d+)" )
        rx.setMinimal( True )

        for result in results[::-1]:  # count from end to begin because we are replacing by offset in content
            searchLength = result.length
            captures = result.capturedTexts
        
            # compute replace text
            if isRE and captures.count() > 1 :
                pos = 0
                
                pos = rx.indexIn( replaceText, pos )
                while  pos != -1:
                    id = rx.cap( 1 ).toInt()
                    
                    if  id < 0 or id >= captures.count() :
                        pos += rx.matchedLength()
                        continue
                    
                    # update replace text with partial occurrences
                    replaceText.replace( pos, rx.matchedLength(), captures[id] )
                    
                    # next
                    pos += captures[id].length()
                    
                    pos = rx.indexIn( replaceText, pos )

            # replace text
            content.replace( result.offset, searchLength, replaceText )

            handledResults.append(result)
            '''
                    if  tracker.elapsed() >= self.mMaxTime :
                        if handledResults:
                            if  not isOpenedFile :
                                saveContent( fileName, content, codec )


                            resultsHandled.emit( fileName, handledResults )


                        if  isOpenedFile :
                            openedFileHandled.emit( fileName, content, codec )


                        handledResults.clear()
                        tracker.restart()

            '''
            with self.lock:
                if  self.mExit :
                    return
                elif  self.mReset :
                    break

        if handledResults:
            if not isOpenedFile :
                self.saveContent( fileName, content, codec )

            self.resultsHandled.emit( fileName, handledResults )

        if  isOpenedFile :
            self.openedFileHandled.emit( fileName, content, codec )


    def run(self):
        tracker = QTime()

        while True:
            with self.lock:
                self.mReset = False
                self.mExit = False

            tracker.restart()

            keys = []

            with self.lock:
                keys = self.mResults.keys()

            for fileName in keys:
                content = self.fileContent( fileName )

                self.replace_( fileName, content )

                with self.lock:
                    if  self.mExit :
                        return
                    elif  self.mReset :
                        break

            with self.lock:
                if  self.mExit :
                    return
                elif  self.mReset :
                    continue
            break

        print "Replace finished in ", tracker.elapsed() /1000.0
