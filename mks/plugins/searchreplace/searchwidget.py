"""
searchwidget --- Search widget and controler
============================================

Module implements search widget and manages search and replace operations
"""

import os.path
import re

from PyQt4 import uic
from PyQt4.QtCore import qApp, QDir, QEvent, \
                         QRect, QSize, Qt, \
                         pyqtSignal

from PyQt4.QtGui import QCompleter, QDirModel, QFileDialog,  \
                        QFrame, QFileDialog, QIcon, \
                        QMessageBox, \
                        QPainter,  \
                        QPalette, \
                        QProgressBar, QToolButton, QWidget

from mks.core.core import core

from mks.plugins.searchreplace import *
import searchresultsmodel

from controller import *

class SearchWidget(QFrame):
    """Widget, appeared, when Ctrl+F pressed.
    Has different forms for different search modes
    """

    Normal = 'normal'
    Good = 'good'
    Bad = 'bad'
    Incorrect = 'incorrect'

    searchInDirectoryStartPressed = pyqtSignal(type(re.compile('')), list, unicode)
    """
    searchInDirectoryStartPressed(regEx, mask, path)
    
    **Signal** emitted, when 'search in directory' button had been pressed
    """  # pylint: disable=W0105

    searchInDirectoryStopPressed = pyqtSignal()
    """
    searchInDirectoryStopPressed()
    
    **Signal** emitted, when 'stop search in directory' button had been pressed
    """  # pylint: disable=W0105

    replaceCheckedStartPressed = pyqtSignal(unicode)
    """
    replaceCheckedStartPressed(replText)
    
    **Signal** emitted, when 'replace checked' button had been pressed
    """  # pylint: disable=W0105

    replaceCheckedStopPressed = pyqtSignal()
    """
    replaceCheckedStartPressed()
    
    **Signal** emitted, when 'stop replacing checked' button had been pressed
    """  # pylint: disable=W0105


    def __init__(self, plugin):
        QFrame.__init__(self, core.workspace())
        self._mode = None
        self.plugin = plugin
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'SearchWidget.ui'), self)
        
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
        
        # connections
        self.cbSearch.lineEdit().textChanged.connect(self._updateActionsState)
        self.cbRegularExpression.stateChanged.connect(self._updateActionsState)
        self.cbCaseSensitive.stateChanged.connect(self._updateActionsState)
        
        self.cbSearch.lineEdit().textChanged.connect(self._onSearchRegExpChanged)
        self.cbRegularExpression.stateChanged.connect(self._onSearchRegExpChanged)
        self.cbCaseSensitive.stateChanged.connect(self._onSearchRegExpChanged)
        
        core.workspace().currentDocumentChanged.connect(self._updateActionsState)
        
        self.tbCdUp.clicked.connect(self._onCdUpPressed)
        
        core.actionManager().action("mNavigation/mSearchReplace/aSearchNext")\
                                        .triggered.connect(self.on_pbNext_pressed)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchPrevious")\
                                        .triggered.connect(self.on_pbPrevious_pressed)
        
        self._updateActionsState()
        
        core.mainWindow().hideAllWindows.connect(self.hide)

    def setMode(self, mode ):
        """Change search mode.
        i.e. from "Search file" to "Replace directory"
        """
        if self._mode == mode and \
           self.isVisible() and \
           not core.workspace().currentDocument().hasFocus():
            self.cbSearch.lineEdit().selectAll()
            self.cbSearch.setFocus()
            return

        self._mode = mode

        if core.workspace().currentDocument() and \
            searchText = core.workspace().currentDocument().selectedText()
        else:
            searchText = ''

        if searchText:
            self.cbSearch.setEditText( searchText )
            self.cbReplace.setEditText( searchText )
        
        self.cbSearch.setFocus()
        self.cbSearch.lineEdit().selectAll()
            
        if  mode & ModeFlagDirectory :
            try:
                searchPath = os.path.abspath(unicode(os.path.curdir))
                self.cbPath.setEditText( searchPath )
            except OSError:  # current directory might have been deleted
                pass 

        # Set widgets visibility flag according to state
        widgets = (self.wSearch, self.pbPrevious, self.pbNext, self.pbSearch, self.wReplace, self.wPath, \
                   self.pbReplace, self.pbReplaceAll, self.pbReplaceChecked, self.wOptions, self.wMask)
        #                         wSear  pbPrev pbNext pbSear wRepl  wPath  pbRep  pbRAll pbRCHK wOpti wMask 
        visible = \
        {ModeSearch :             (1,     1,     1,     0,     0,     0,     0,     1,     1,    1,    0,),
         ModeReplace:             (1,     1,     1,     0,     1,     0,     1,     1,     0,    1,    0,),
         ModeSearchDirectory:     (1,     0,     0,     1,     0,     1,     0,     0,     0,    1,    1,),
         ModeReplaceDirectory:    (1,     0,     0,     1,     1,     1,     0,     0,     1,    1,    1,),
         ModeSearchOpenedFiles:   (1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,),
         ModeReplaceOpenedFiles:  (1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,)}
        
        for i, widget in enumerate(widgets):
            widget.setVisible(visible[mode][i])

        self.updateLabels()
        self.updateWidgets()

        self.show()

    def eventFilter(self, object_, event ):
        """ Event filter for mode switch tool button
        Draws icons in the search and path lineEdits
        """
        if  event.type() == QEvent.Paint :
            toolButton = object_
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
                if self._mode == ModeSearch:
                    self.pbNext.click()
                elif self._mode in (ModeSearchDirectory, \
                                    ModeSearchOpenedFiles, \
                                    ModeReplaceDirectory, \
                                    ModeReplaceOpenedFiles):
                    if self.pbSearch.isVisible():
                        self.pbSearch.click()
                    else:
                        self.pbSearchStop.click()
                elif self._mode == ModeReplace:
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

    def _getSearchMask(self):
        """Get search mask as list of patterns
        """
        mask = [s.strip() for s in self.cbMask.currentText().split(' ')]
        # remove empty
        mask = filter(None, mask)
        return mask

    def setState(self, state ):
        """Change line edit color according to search result
        """
        widget = self.cbSearch.lineEdit()
        
        color = {SearchWidget.Normal: qApp.palette().color(QPalette.Base), \
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
                pos  += 1
            if pos < len(document.text()):
                match = regExp.search(document.text(), pos)
            else:
                match = None

        document.endUndoAction()
        
        if oldPos is not None:
            document.setCursorPosition(absPos = oldPos) # restore cursor position
        core.mainWindow().statusBar().showMessage( self.tr( "%d occurrence(s) replaced." % count ), 10000 )

    def setSearchInProgress(self, inProgress):
        """Search thread started or stopped
        """
        self.pbSearchStop.setVisible( inProgress )
        self.pbSearch.setVisible( not inProgress )
        self.updateWidgets()
        self._progress.setVisible( inProgress )

    def onSearchProgressChanged(self, value, total ):
        """Signal from the thread, progress changed
        """
        self._progress.setValue( value )
        self._progress.setMaximum( total )

    def setReplaceInProgress(self, inProgress):
        """Replace thread started or stopped
        """
        self.pbReplaceCheckedStop.setVisible( inProgress )
        self.pbReplaceChecked.setVisible( not inProgress )
        self.updateWidgets()
    
    def _updateActionsState(self):
        """Update actions state according to search reg exp valid state
        """
        valid, error = self._isSearchRegExpValid()
        searchAvailable = valid 
        searchInFileAvailable = valid and core.workspace().currentDocument() is not None
        
        for button in (self.pbNext, self.pbPrevious, self.pbReplace, self.pbReplaceAll):
            button.setEnabled(searchInFileAvailable)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchNext").setEnabled(searchInFileAvailable)
        core.actionManager().action("mNavigation/mSearchReplace/aSearchPrevious").setEnabled(searchInFileAvailable)

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
        if self._mode in (ModeSearch, ModeReplace) and \
           core.workspace().currentDocument() is not None:
            self.searchFile( True, True )

    def _onCdUpPressed(self):
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

        self.searchInDirectoryStartPressed.emit(self._getRegExp(),
                                                self._getSearchMask(),
                                                self.cbPath.currentText())

    def on_pbSearchStop_pressed(self):
        """Handler of click on "Stop" button. Stop search thread
        """
        self.searchInDirectoryStopPressed.emit()

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
        self.updateComboBoxes()
        self.replaceCheckedStartPressed.emit(self.cbReplace.currentText())

    def on_pbReplaceCheckedStop_pressed(self):
        """Handler of click on "Stop" button when replacing in directory
        """
        self.replaceCheckedStopPressed.emit()

    def on_pbBrowse_pressed(self):
        """Handler of click on "Browse" button. Explores FS for search directory path
        """
        path = QFileDialog.getExistingDirectory( self, self.tr( "Search path" ), self.cbPath.currentText() )

        if path:
            self.cbPath.setEditText( path )
