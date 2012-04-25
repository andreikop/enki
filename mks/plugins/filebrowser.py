"""
filebrowser --- Dock with file system tree
==========================================
"""
import sys
import os
import os.path
import operator
import logging

from PyQt4.QtCore import QDir, QRect, QEvent, QModelIndex, QObject, Qt, \
                         pyqtSignal, pyqtSlot
from PyQt4.QtGui import QAction, QCompleter, QDirModel, \
                        QFrame, QFileSystemModel, \
                        QIcon, QItemSelectionModel, QKeySequence, QComboBox, \
                        QPainter, \
                        QShortcut, QSortFilterProxyModel, QToolButton, QTreeView, QVBoxLayout, QWidget

from mks.fresh.dockwidget.pDockWidget import pDockWidget

from mks.core.core import core

def _getCurDir():
    """Get process current directory
    """
    try:
        return os.path.abspath(unicode(os.curdir))
    except OSError:
        return ''

class Plugin(QObject):
    """File system tree.
    
    Allows to open files quickly
    """

    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        # create dock
        self.dock = DockFileBrowser(core.mainWindow())
        self.dock.hide()
        # add dock to dock toolbar entry
        core.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self.dock)
    
    def del_(self):
        """Uninstall the plugin
        """
        self.dock.del_()


class FileBrowserFilteredModel(QSortFilterProxyModel):
    """Model filters out files using negative filter.
    i.e. does not show .o .pyc and other temporary files
    """
    def __init__(self, parent):
        QSortFilterProxyModel.__init__(self, parent)
        core.fileFilter().regExpChanged.connect(self.invalidate)
    
    def columnCount(self, parent = QModelIndex()):  # pylint: disable=W0613
        """Column count for the model
        """
        return 1
    
    def hasChildren(self, parent = QModelIndex()):
        """Check if node has children. QAbstractItemModel standard method
        """
        return self.sourceModel().hasChildren( self.mapToSource( parent ) )
        
    def filterAcceptsRow(self, source_row, source_parent):
        """ Main method. Check if file matches filter
        """
        if  source_parent == QModelIndex():
            return True
        return not core.fileFilter().regExp().match(source_parent.child( source_row, 0 ).data().toString() )


class SmartRecents(QObject):
    """Class stores File Browser recent directories and provides variants for combo box.
    
    
    "Active directory" in this class means the last directory, where one or more files has been opened
    """
    MAX_RECENTS_SIZE = 8
    
    STATISTICS_SIZE = 10.
    BONUS_FOR_OPENING = 1.
    MAX_POINTS_COUNT = 100.
    
    _recentsChanged = pyqtSignal(list)

    def __init__(self, fileBrowser):
        QObject.__init__(self)
        self._currDir = None
        self._currIsActive = False
        self._popularDirs = None
        self._loadPopularDirs()
        core.workspace().currentDocumentChanged.connect(self._updateRecents)
        
        # incoming connections
        fileBrowser.rootChanged.connect(self._onRootChanged)
        fileBrowser.fileActivated.connect(self._onFileActivated)
        # outgoing connections
        self._recentsChanged.connect(fileBrowser.updateComboItems)

    def _loadPopularDirs(self):
        """Load popular directories from the config
        """
        self._popularDirs = core.config()["FileBrowser"]["PopularDirs"]  # Directory: popularity points
        for k in self._popularDirs.iterkeys():
            try:
                self._popularDirs[k] = float(self._popularDirs[k])
            except ValueError as ex:
                logging.error('Invalid PopularDirs value: ' + unicode(ex))
                self._popularDirs[k] = 0.0

    def _dirsByPopularity(self):
        """Return list of dirrectories, sorted by popularity
        """
        if not self._popularDirs:
            return ()
        
        dirAndPopularity = sorted(self._popularDirs.iteritems(), key=operator.itemgetter(1), reverse=True)
        dirs = [dp[0] for dp in dirAndPopularity]  # take only first elements
        return dirs
    
    def _dirsByPath(self):
        """Return list of dirrectories, sorted by popularity
        """
        if not self._popularDirs:
            return ()
        
        dirAndPopularity = sorted(self._popularDirs.iteritems(), key=operator.itemgetter(0))
        dirs = [dp[0] for dp in dirAndPopularity]  # take only first elements
        return dirs

    def _onFileActivated(self):
        """FileBrowserDock notifies SmartRecents that file has been activated
        """
        if self._currIsActive:  # statistics already has been updated
            return
        
        self._currIsActive = True

        # Replace the least popular
        if self._currDir not in self._popularDirs:
            if len(self._popularDirs) == self.STATISTICS_SIZE:
                leastPopular = self._dirsByPopularity()[-1]
                del self._popularDirs[leastPopular]
            self._popularDirs[self._currDir] = 0

        self._popularDirs[self._currDir] += self.BONUS_FOR_OPENING

        # Normalization
        pointsSum = sum(self._popularDirs.itervalues())
        multiplier = self.MAX_POINTS_COUNT / pointsSum
        if multiplier < 1:
            for k in self._popularDirs.iterkeys():
                self._popularDirs[k] *= multiplier
        
        core.config()["FileBrowser"]["PopularDirs"] = self._popularDirs
        core.config().flush()
        
        # History update is not scheduled here, because it will be scheduled when workspace changes current file

    def _onRootChanged(self, newCurrDir):
        """FileBrowserDock notifies SmartRecents that user changed current directory
        """
        self._currDir = newCurrDir
        self._currIsActive = False
        self._updateRecents()

    def _updateRecents(self):
        """Generate new list of directories, which will be shown in the combo box.
        Emit this list
        """
        history = []
        includedDirs = set()
        if self._currDir is not None:
            history.append((self._currDir, self._currDir, None))
            includedDirs.add(self._currDir)
        # Separator
        if len(history) > 1:
            history.insert(1, None)  # separator
        # Popular directories
        firstPopularDir = True
        popularDirs = self._dirsByPath()
        for directory in popularDirs:
            if not directory in includedDirs:
                if firstPopularDir:
                    history.append(None)  # separator
                    firstPopularDir = False
                history.append( (directory, directory, ':mksicons/bookmark.png') )
                includedDirs.add(directory)
            if len(history) >= self.MAX_RECENTS_SIZE:
                break
        
        self._recentsChanged.emit(history)

class SmartHistory(QObject):
    """Class remembers file browser history and manages Back and Forward buttons
    """
    def __init__(self, fileBrowser):
        QObject.__init__(self)
        self._fileBrowser = fileBrowser
        self._currDir = None
        self._currIsActive = False
        self._history = []
        self._historyIndex = -1

        self._aBack = QAction(  QIcon(':mksicons/previous.png'),
                                self.tr("Back"),
                                self)
        self._aBack.setShortcut('Alt+Left')
        fileBrowser.titleBar().addAction(self._aBack, 0)
        core.actionManager().addAction("mNavigation/mFileBrowser/aBack", self._aBack)
        self._aBack.triggered.connect(self._onTbBackTriggered)

        self._aForward = QAction(   QIcon(':mksicons/next.png'),
                                    self.tr("Forward"),
                                    self)
        self._aForward.setShortcut('Alt+Right')
        fileBrowser.titleBar().addAction(self._aForward, 1)
        core.actionManager().addAction("mNavigation/mFileBrowser/aForward", self._aForward)
        self._aForward.triggered.connect(self._onTbForwardTriggered)
        
        fileBrowser.titleBar().addSeparator(2)
        
        # incoming connections
        fileBrowser.rootChanged.connect(self._onRootChanged)
        fileBrowser.fileActivated.connect(self._onFileActivated)
    
    def del_(self):
        """Explicitly called destructor
        """
        core.actionManager().removeAction("mNavigation/mFileBrowser/aBack")
        core.actionManager().removeAction("mNavigation/mFileBrowser/aForward")

    def _onRootChanged(self, newCurrDir):
        """FileBrowserDock notifies SmartHistory that root has been changed
        """
        self._currDir = newCurrDir
        self._currIsActive = False
        self._updateActions()

    def _onFileActivated(self):
        """FileBrowserDock notifies SmartHistory that file has been activated
        """
        if self._currIsActive:
            return
        self._currIsActive = True
        self._updateHistory()

    def _updateHistory(self):
        """Directory has been activated. Update history
        """
        if  self._history and \
                self._history[self._historyIndex] == self._currDir:
            return # Do nothing, if moved back or forward

        if (self._historyIndex + 1) < len(self._history):  # not on the top of the stack
            # Cut history
            self._history = self._history[:self._historyIndex + 1]
        
        # Append new root to the history
        self._history.append(self._currDir)
        self._historyIndex += 1
        
        self._updateActions()
        
    def _onTbBackTriggered(self):
        """Back action handler
        """
        if not self._currIsActive:
            self._updateHistory()
        
        self._historyIndex -= 1
        self._fileBrowser.setCurrentPath(self._history[self._historyIndex])
    
    def _onTbForwardTriggered(self):
        """Forward action handler
        """
        self._historyIndex += 1
        self._fileBrowser.setCurrentPath(self._history[self._historyIndex])

    def _updateActions(self):
        """Update actions enabled state
        """
        if self._history and self._currDir != self._history[self._historyIndex]:
            self._aBack.setEnabled(True)
            self._aBack.setStatusTip(self._history[-1])
            self._aBack.setToolTip(self._history[-1])
        elif self._history and self._historyIndex > 0:
            self._aBack.setEnabled(True)
            self._aBack.setStatusTip(self._history[self._historyIndex - 1])
            self._aBack.setToolTip(self._history[self._historyIndex - 1])
        else:
            self._aBack.setEnabled(False)
            self._aBack.setStatusTip(self.tr("Back"))
            self._aBack.setToolTip(self.tr("Back"))
        
        if (self._historyIndex + 1) < len(self._history):
            self._aForward.setEnabled(True)
            self._aForward.setStatusTip(self._history[self._historyIndex + 1])
            self._aForward.setToolTip(self._history[self._historyIndex + 1])
        else:
            self._aForward.setEnabled(False)
            self._aForward.setStatusTip(self.tr("Forward"))
            self._aForward.setToolTip(self.tr("Forward"))

class JumpToCurent(QObject):
    """Class implements 'Jump to current' functionality
    It creates the action and handles it
    """
    def __init__(self, fileBrowser):
        QObject.__init__(self)
        self._fileBrowser = fileBrowser
        
        self._action = QAction(QIcon(':mksicons/text.png'),
                               self.tr("Jump to current file path"),
                               self)
        self._action.setShortcut('Shift+Ctrl+J')
        self._action.triggered.connect(self._onTriggered)

        fileBrowser.titleBar().addAction(self._action, 0)
        fileBrowser.titleBar().addSeparator(1)
        core.actionManager().addAction("mNavigation/mFileBrowser/aJumpToCurrent", self._action)

        fileBrowser.rootChanged.connect(self._updateAction)
        core.workspace().currentDocumentChanged.connect(self._updateAction)

    def del_(self):
        """Explicitly called destructor
        """
        core.actionManager().removeAction(self._action)

    def _updateAction(self):
        """Update action enabled state after current file or current directory changed
        """
        self._action.setEnabled(_getCurDir() != self._fileBrowser.currentPath())
        try:
            self._action.setEnabled(_getCurDir() != self._fileBrowser.currentPath())
        except OSError:  # probably current dir has been deleted
            self._action.setEnabled(False)

    def _onTriggered(self):
        """Jump to directory of current file
        """
        self._fileBrowser.setCurrentPath(_getCurDir())

class Tree(QTreeView):
    """File system tree
    """
    
    _fileActivated = pyqtSignal()
    
    def __init__(self, fileBrowser):
        QTreeView.__init__(self, fileBrowser)
        
        self._fileBrowser = fileBrowser
        
        self.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.setAttribute( Qt.WA_MacSmallSize )
        self.setContextMenuPolicy( Qt.ActionsContextMenu )
        self.setHeaderHidden( True )
        self.setUniformRowHeights( True )
        self.setTextElideMode(Qt.ElideMiddle)
        
        # dir model
        self._dirsModel = QFileSystemModel( self )
        self._dirsModel.setNameFilterDisables( False )
        self._dirsModel.setFilter( QDir.AllDirs | QDir.AllEntries | QDir.CaseSensitive | QDir.NoDotAndDotDot )
        # self._dirsModel.directoryLoaded.connect(self.setFocus)  TODO don't have this signal in my Qt version
        
        # create proxy model
        self._filteredModel = FileBrowserFilteredModel( self )
        self._filteredModel.setSourceModel( self._dirsModel )

        self.setModel( self._filteredModel)
        
        if not sys.platform.startswith('win'):
            self._dirsModel.setRootPath( "/" )
        else:
            self._dirsModel.setRootPath('')
        
        # shortcut accessible only when self._tree has focus
        self._upShortcut = QShortcut( QKeySequence( "BackSpace" ), self )
        self._upShortcut.setContext( Qt.WidgetShortcut )
        self._upShortcut.activated.connect(self.moveUp)
        
        self.activated.connect(self._onActivated)
        self._fileActivated.connect(fileBrowser.fileActivated)

    def _onActivated(self, idx ):
        """File or directory doubleClicked
        """
        index = self._filteredModel.mapToSource( idx )
        path = self._dirsModel.filePath( index )
        
        if  os.path.isdir( path ) :
            self._fileBrowser.setCurrentPath(path)
        else:
            self._fileActivated.emit()
            core.workspace().openFile(path)
    
    def moveUp(self):
        """User pressed Up key or button. Move focus and root up
        """
        current = self.currentIndex()
        if not current.isValid():
            current = self.rootIndex().child(0, 0)
            self.setCurrentIndex(current)
        
        # move tree root up, if necessary
        if current.parent() == self.rootIndex() or \
           current == self.rootIndex():  # need to move root up
            if self.rootIndex().parent().isValid():  # not reached root of the FS tree
                self._fileBrowser.setCurrentPath( self._filteredModelIndexToPath(self.rootIndex().parent()))
        
        parentOfCurrent = self.currentIndex().parent()
        if parentOfCurrent != self.rootIndex():  # if not reached top
            self.setCurrentIndex(parentOfCurrent)  # move selection up

    def _filteredModelIndexToPath(self, index):
        """Map index to file path
        """
        srcIndex = self._filteredModel.mapToSource( index )
        return self._dirsModel.filePath( srcIndex )

    def setFocus(self):
        """Moves focus and selection to the first item, if nothing focused
        """
        rootIndex = self.rootIndex()
        
        selected =  self.selectionModel().selectedIndexes()
        for index in selected:
            if index.parent() == rootIndex:   # Already having selected item
                return
        
        firstChild = self._filteredModel.index(0, 0, rootIndex)
        if firstChild.isValid():  # There may be no rows, if directory is empty, or not loaded yet
            self.selectionModel().select(firstChild, QItemSelectionModel.SelectCurrent)
        QTreeView.setFocus(self)

    def currentPath(self):
        """Get current path (root of the tree)
        """
        index = self.rootIndex()
        index = self._filteredModel.mapToSource( index )
        return self._dirsModel.filePath( index )

    def _isDescendant(self, child, parent):
        """Check if child is descendant of parent
        """
        childsParent = child.parent()
        while childsParent.isValid():
            if childsParent == parent:
                return True
            childsParent = childsParent.parent()
        
        return False

    def setCurrentPath(self, path):
        """Set current path (root of the tree)
        """
        # get index
        index = self._dirsModel.index(path)
        
        # set current path
        self._filteredModel.invalidate()
        newRoot = self._filteredModel.mapFromSource( index )
        self.setRootIndex(newRoot)
        if not self._isDescendant(self.currentIndex(), newRoot):
            self.setCurrentIndex(QModelIndex())

class ComboBox(QComboBox):
    """File browser combo box.
    Widget and functionality
    """
    def __init__(self, fileBrowser):
        QComboBox.__init__(self, fileBrowser)
        
        self._fileBrowser = fileBrowser

        self.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.setAttribute( Qt.WA_MacSmallSize )
        self.setEditable(True)
        self.setMinimumContentsLength(1)
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.lineEdit().setReadOnly( False )
        self._completionModel = QDirModel(self.lineEdit())
        self._completionModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self.lineEdit().setCompleter(QCompleter(self._completionModel,
                                               self.lineEdit()))
        #TODO QDirModel is deprecated but QCompleter does not yet handle
        #QFileSystemModel - please update when possible.
        self._count = 0

        # Show popup action
        self._showPopupAction = QAction(QIcon(':mksicons/filtered.png'), "File browser history", self)
        self._showPopupAction.setShortcut('Ctrl+H')
        core.actionManager().addAction("mNavigation/mFileBrowser/aMenuShow", self._showPopupAction)
        showPopupSlot = lambda triggered: self.showPopup()
        self._showPopupAction.triggered.connect(showPopupSlot)
        
        # cd up button
        self._tbCdUp = QToolButton( self.lineEdit() )
        self._tbCdUp.setIcon( QIcon( ":/mksicons/go-up.png" ) )
        self._tbCdUp.setCursor( Qt.ArrowCursor )
        self._tbCdUp.installEventFilter( self )
        self._tbCdUp.clicked.connect(self._fileBrowser.moveUp)
        
        # reconnected in self.updateComboItems()
        self.currentIndexChanged[int].connect(self._onItemSelected)

    def del_(self):
        """Explicitly called destructor
        """
        core.actionManager().removeAction(self._showPopupAction)

    def eventFilter(self, object_, event ):
        """ Event filter for mode switch tool button
        Draws icons in the search and path lineEdits
        """
        if  event.type() == QEvent.Paint:
            toolButton = object_
            lineEdit = self.lineEdit()
            height = lineEdit.height()
            lineEdit.setContentsMargins( height, 0, 0, 0 )
            
            availableRect = QRect( 0, 0, height, height )
            toolButton.setGeometry( availableRect )
            
            painter = QPainter ( toolButton )
            toolButton.icon().paint( painter, availableRect )
            
            return True

        return QComboBox.eventFilter( self, object_, event )

    @pyqtSlot(int)
    def _onItemSelected(self, index):
        """Handler of item selection in the combo box
        """
        if self.count() > self._count:  # It is user input
            path = self.itemText(index)
            if os.path.isdir(path):
                self._fileBrowser.setCurrentPath(path)
        else:
            path = self.itemData(index).toString()
            self._fileBrowser.setCurrentPath(path)

    def updateItems(self, items):
        """Update items in the combo box according to current history
        """
        self.currentIndexChanged[int].disconnect()
        self.clear()
        for index, item in enumerate(items):
            if item is not None:
                text, path, icon = item
                self.addItem(text)  #  text
                self.setItemData(index, path)  # path
                if item[2] is not None:
                    self.setItemIcon(index, QIcon(icon))
            else:
                self.insertSeparator(self.count())
        self._count = self.count()
        self.currentIndexChanged[int].connect(self._onItemSelected)


class DockFileBrowser(pDockWidget):
    """UI interface of FileBrowser plugin. 
        
    Dock with file system tree, Box, navigation in a file system
    tree, for moving root of tree to currently selected directory and
    up (relatively for current directory)
    """
    rootChanged = pyqtSignal(unicode)
    """
    rootChanged(path)
    
    **Signal** emitted, when tree root has been changed
    """  # pylint: disable=W0105
    
    fileActivated = pyqtSignal()
    """
    rootChanged(path)
    
    **Signal** emitted, when file has been activated
    """  # pylint: disable=W0105
    
    def __init__(self, parent):
        pDockWidget.__init__(self, parent)
        
        self._comboBox = None
        self._tree = None
        self._smartRecents = None
        self._smartHistory = None
        self._jumpToCurrent = None
        
        self.setObjectName("FileBrowserDock")
        self.setWindowTitle(self.tr( "&File Browser" ))
        self.setWindowIcon(QIcon(':/mksicons/open.png'))
        # restrict areas
        self.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        
        self.showAction().setShortcut("Alt+F")
        core.actionManager().addAction("mDocks/aFileBrowser", self.showAction())
        
        self.visibilityChanged.connect(self._onVisibilityChanged)
    
    def del_(self):
        """Explicitly called destructor
        """
        if self._smartHistory is not None:
            self._smartHistory.del_()
        if self._jumpToCurrent is not None:
            self._jumpToCurrent.del_()
        if self._comboBox is not None:
            self._comboBox.del_()
        core.actionManager().removeAction("mDocks/aFileBrowser")

    def _onVisibilityChanged(self, visible):
        """Postnoted widget initialization.
        Create element, when widget appears first timer
        """
        if visible:
            self._initialize()
            self.visibilityChanged.disconnect(self._onVisibilityChanged)
    
    def _initialize(self):
        """Delayed initialization of the widget for quicker start of application
        """
        # central widget
        wdg = QWidget( self )
        self.setWidget( wdg )
        
        # vertical layout
        vertLayout = QVBoxLayout( wdg )
        vertLayout.setMargin( 5 )
        vertLayout.setSpacing( 3 )
        
        # combo
        self._comboBox = ComboBox(self)
        vertLayout.addWidget( self._comboBox )
        
        # hline
        hline = QFrame( self )
        hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )
        vertLayout.addWidget( hline )
        
        # files view
        self._tree = Tree(self)
        vertLayout.addWidget( self._tree )
        
        # redirirect focus proxy
        self.setFocusProxy( self._tree )
        
        self._smartRecents = SmartRecents(self)
        self._smartHistory = SmartHistory(self)
        self._jumpToCurrent = JumpToCurent(self)
        
        self.setCurrentPath(_getCurDir())
    
    @pyqtSlot(list)
    def updateComboItems(self, items):
        """Update items in the combo box according to current history
        """
        self._comboBox.updateItems(items)
    
    def currentPath(self):
        """Get current path (root of the tree)
        """
        return self._tree.currentPath()

    def setCurrentPath(self, path):
        """Set current path (root of the tree)
        If there are no documents on workspace, also changes process current directory
        """
        self._tree.setCurrentPath(path)
        
        # set lineedit path
        self._comboBox.setToolTip(path)
        
        # notify SmartRecents and own slots
        self.rootChanged.emit(path)
        self._tree.setFocus()
        
        # cd if no files with known path
        if not any([doc for doc in core.workspace().documents() \
                        if doc.filePath() is not None]):
            os.chdir(path)

    def moveUp(self):
        """Move tree root up, or only move focus"""
        self.setCurrentPath(os.path.dirname(self._tree.currentPath()))
