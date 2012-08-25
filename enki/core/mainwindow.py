"""
mainwindow --- Main window of the UI. Fills main menu.
======================================================


Module contains :class:`enki.core.mainwindow.MainWindow` implementation
"""

import sys
import os.path
import json

from PyQt4.QtCore import pyqtSignal, QSize, Qt, QTimer
from PyQt4.QtGui import QHBoxLayout, QIcon, QLabel, QMessageBox, \
                        QPalette, QSizePolicy, QStatusBar, QToolBar, QVBoxLayout, QWidget

from PyQt4.QtGui import QMainWindow

from enki.widgets.dockwidget import DockWidget
from enki.core.actionmanager import ActionMenuBar

from enki.core.core import core
import enki.core.defines

class _StatusBar(QStatusBar):
    """Extended status bar. Supports HTML messages
    """
    def __init__(self, *args):
        QStatusBar.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizeGripEnabled(False)
        self.setStyleSheet("QStatusBar {border: 0} QStatusBar::item {border: 0}")
        self._label = QLabel(self)
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self._label.setStyleSheet("color: red")
        self.addWidget(self._label)
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.clearMessage)
    
    def showMessage(self, text, timeout=0):
        """QStatusBar.showMessage()
        """
        self._label.setText(text)
        self._timer.stop()
        if timeout > 0:
            self._timer.start(timeout)
    
    def clearMessage(self):
        """QStatusBar.clearMessage()
        """
        self._label.clear()

class MainWindow(QMainWindow):
    """
    Main UI window
    
    Class creates window elements, fills main menu with items.
    
    If you need to access to some existing menu items - check action path 
    in the class constructor, than use next code: ::
        
        core.actionManager().action( "mFile/aOpen" ).setEnabled(True)
        core.actionManager().action( "mFile/aOpen" ).triggered.connect(self.myCoolMethod)
    
    MainWindow instance is accessible as: ::
    
        from enki.core.core import core
        core.mainwindow()
    
    Created by the core
    """
    
    hideAllWindows = pyqtSignal()
    """
    hideAllWindows()
    
    **Signal** emitted, when user toggled "Hide all" .
    Dock widgets are closed automatically, but other widgets, i.e. search widget, must catch this signal and close
    themselves.
    """  # pylint: disable=W0105
    
    directoryDropt = pyqtSignal(unicode)
    """
    directoryDropt()
    
    **Signal** emitted, when user drag-n-dropt directory to main windowd.
    FileBrowser shows directory
    """  # pylint: disable=W0105
    
    _STATE_FILE = os.path.join(enki.core.defines.CONFIG_DIR, "main_window_state.bin")
    _GEOMETRY_FILE = os.path.join(enki.core.defines.CONFIG_DIR, "main_window_geometry.json")
    
    def __init__(self):
        QMainWindow.__init__(self)
        
        self._queuedMessageToolBar = None
        self._createdMenuPathes = []
        self._createdActions = []

        self.setUnifiedTitleAndToolBarOnMac( True )
        self.setIconSize( QSize( 16, 16 ) )
        self.setAcceptDrops( True )
        
        # Set corner settings for dock widgets
        self.setCorner( Qt.TopLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.TopRightCorner, Qt.RightDockWidgetArea )
        self.setCorner( Qt.BottomLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.BottomRightCorner, Qt.RightDockWidgetArea )
        
        self.setWindowTitle(self.defaultTitle())  # overwriten by workspace when file or it's modified state changes
        self.setWindowIcon( QIcon(':/enkiicons/logo/32x32/enki.png') )

        # Create top tool bar
        self._topToolBar = QToolBar("topToolBar")
        self._topToolBar.setObjectName("topToolBar")
        self._topToolBar.setMovable(False)
        self._topToolBar.setIconSize(QSize(16, 16))

        # Create menu bar
        self._menuBar = ActionMenuBar(self, core.actionManager())

        self._initMenubarAndStatusBarLayout()
        
        self._createMenuStructure()
        
        # create central layout
        widget = QWidget(self)
        self._centralLayout = QVBoxLayout(widget)
        self._centralLayout.setMargin(0)
        self.setCentralWidget(widget)
        
        core.actionManager().action("mFile/aQuit").triggered.connect(self.close)

    def del_(self):
        """Explicitly called destructor
        """
        if self._queuedMessageToolBar:
            self.removeToolBar(self._queuedMessageToolBar)
            del self._queuedMessageToolBar

        for act in self._createdActions:
            core.actionManager().removeAction(act, False)
        for menuPath in self._createdMenuPathes[::-1]:
            core.actionManager().removeMenu(menuPath)
    
    @staticmethod
    def _isMenuEmbeddedToTaskBar():
        """On Unity (Ubuntu) and MacOS menu bar is embedded to task bar
        """
        return 'UBUNTU_MENUPROXY' in os.environ or \
               'darwin' == sys.platform
    
    def _initMenubarAndStatusBarLayout(self):
        """Create top widget and put it on its place
        """
        if not 'darwin' == sys.platform:
            # on Ubuntu toolbar, docs and editor area look as one widget. Ugly
            # Therefore it is separated with line. On Mac seems OK
            # I can't predict, how it will look on other platforms, therefore line is used for all, except Mac
            toolBarStyleSheet = "QToolBar {border: 0; border-bottom-width: 1; border-bottom-style: solid}"""
            self._topToolBar.setStyleSheet(toolBarStyleSheet)

        if self._isMenuEmbeddedToTaskBar():  # separate menu bar
            self.addToolBar(self._topToolBar)
            self.setMenuBar(self._menuBar)
        else:  # menubar, statusbar and editor tool bar on one line
            self._menuBar.setAutoFillBackground(False)
            menuBarStyleSheet = """
            QMenuBar {background-color: transparent;
                      color: %s}
            QMenuBar::item:!selected {background: transparent;}
            """ % self.palette().color(QPalette.WindowText).name()
            self._menuBar.setStyleSheet(menuBarStyleSheet)
            self._menuBar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

            self.addToolBar(self._topToolBar)
            self._topToolBar.addWidget(self._menuBar)
            
        # Create status bar
        self._statusBar = _StatusBar(self)
        self._topToolBar.addWidget(self._statusBar)
        
    def _createMenuStructure(self):
        """Fill menu bar with items. The majority of items are not connected to the slots,
        Connections made by module, which implements menu item functionality, but, all items are in one place,
        because it's easier to create clear menu layout
        """
        # create menubar menus and actions
        
        def menu(path, name, icon):
            """Subfunction for create a menu in the main menu"""
            menuObject = core.actionManager().addMenu(path, name)
            if icon:
                menuObject.setIcon(QIcon(':/enkiicons/' + icon))
            self._createdMenuPathes.append(path)
            
        def action(path, name, icon, shortcut, tooltip, enabled):  # pylint: disable=R0913
            """Subfunction for create an action in the main menu"""
            if icon:  # has icon
                actObject = core.actionManager().addAction(path, name, QIcon(':/enkiicons/' + icon), shortcut)
            else:
                actObject = core.actionManager().addAction(path, name, shortcut=shortcut)
            actObject.setStatusTip(tooltip)
            actObject.setEnabled(enabled)
            self._createdActions.append(actObject)
        
        def separator(menu):
            """Subfunction for insert separator to the menu"""
            core.actionManager().action(menu).menu().addSeparator()
        
        # pylint: disable=C0301  
        # enable long lines for menu items
        # Menu or action path                          Name                     Icon            Shortcut        Hint                     Action enabled
        tr = self.tr  # pylint: disable=C0103
        menu  ("mFile",                               "File"                  , ""            )
        menu  ("mFile/mUndoClose",                    "Undo Close"            , "recents.png" )
        separator("mFile")
        action("mFile/aNew",                          "&New file..."          , "new.png",      'Ctrl+N',       "New file"               , True )
        action("mFile/aOpen",                         "&Open..."              , "open.png",     "Ctrl+O" ,      "Open a file"            , True )
        menu  ("mFile/mSave",                         "&Save"                 , "save.png"    )
        action("mFile/mSave/aCurrent",                "&Save"                 , "save.png" ,    "Ctrl+S" ,      "Save the current file"  , False)
        action("mFile/mSave/aSaveAs",                 "Save As..."            , "save.png" ,    "Ctrl+Alt+S" ,  ""                           , False)
        action("mFile/mSave/aAll",                    "Save &All"             , "saveall.png",  'Shift+Ctrl+S', "Save all files"         , False)
        menu  ("mFile/mReload",                       "&Reload"               , "reload.png"    )
        action("mFile/mReload/aCurrent",              "Reload"                , "reload.png"  , 'F5',           "Reload the current file", False)
        action("mFile/mReload/aAll",                  "Reload All"            , "reload.png"  , 'Shift+F5',     "Reload all files"       , True)
        action("mFile/aPrint",                        "&Print..."             , "print.png"   , "Ctrl+P",       "Print the current file" , False)
        menu  ("mFile/mClose",                        "&Close"                , "close.png"   )
        action("mFile/mClose/aCurrent",               "&Close"                , "close.png",    "Ctrl+W",       "Close the current file" , False)
        action("mFile/mClose/aAll",                   "Close &All"            , "closeall.png", 'Shift+Ctrl+W', "Close all files"        , False)
        separator("mFile")
        action("mFile/aQuit",                         "&Quit"                 , "quit.png"    , ""            , "Quit"                   , True)

        menu  ("mView",                               "View"                  , ""            )
        menu  ("mView/mZoom",                         "&Zoom"                 , "search.png"  )
        menu  ("mView/mHighlighting",                 "Highlighting"          , ""            )
        separator("mView")
        action("mView/aHideAll",                      "Hide all widgets"      , "",             "Shift+Esc",    "Hide all widgets"          , True)

        menu  ("mEdit",                               "Edit"                  , ""            )

        menu  ("mNavigation",                          "Navigation"            , ""           ) 
        action("mNavigation/aFocusCurrentDocument",   "Focus to editor"       , "text.png",     "Ctrl+Return",  "Focus current document" , False)

        menu  ("mNavigation/mSearchReplace",           "&Search && Replace"    , "search-replace-directory.png")
        menu  ("mNavigation/mBookmarks",               "&Bookmarks"            , "bookmark.png")

        action("mNavigation/aNext",                   "&Next file"            , "next.png",     "Ctrl+PgDown",    "Next file"              , False)
        action("mNavigation/aPrevious",               "&Previous file"        , "previous.png", "Ctrl+PgUp",     "Previous file"          , False)
        action("mNavigation/aGoto",                   "Go go line..."         , "goto.png",     "Ctrl+G",       "Go to line..."          , False)
        menu  ("mNavigation/mFileBrowser",            "File browser"          , ':/enkiicons/open.png')

        menu  ("mSettings",                           "Settings"              , ""            )

        menu  ("mHelp",                               "Help"                  , ""            )
        
        # docks
        core.actionManager().action( "mView/aHideAll" ).triggered.connect(self._onHideAllWindows)
    
    def menuBar(self):
        """Reference to menuBar
        """
        return self._menuBar

    def topToolBar(self):
        """Top tool bar. Contains main menu, position indicator, etc
        """
        return self._topToolBar
    
    def statusBar(self):
        """Return main window status bar.
        It is located on the top tool bar
        """
        return self._statusBar

    def setWorkspace(self, workspace):
        """Set central widget of the main window.
        Normally called only by core when initializing system
        """
        self._centralLayout.addWidget(workspace)
        self.setFocusProxy(workspace)
    
    def defaultTitle(self):
        """Default title. Contains  name and version
        """
        return "%s v.%s" % (enki.core.defines.PACKAGE_NAME, enki.core.defines.PACKAGE_VERSION)
    
    def centralLayout(self):
        """Layout of the central widget. Contains Workspace and search widget
        """
        return self._centralLayout
    
    def appendMessage(self, text, timeoutMs=10000):
        """Append message to the queue. It will be shown as non-modal at the bottom of the window.
        Use such notifications, which are too long or too important for status bar
        but, not so important, to interrupt an user with QMessageBox
        """
        if self._queuedMessageToolBar is None:
            from enki.core.QueuedMessageToolBar import QueuedMessageToolBar
            
            self._queuedMessageToolBar = QueuedMessageToolBar(self)
            self.addToolBar(Qt.BottomToolBarArea, self._queuedMessageToolBar)
            self._queuedMessageToolBar.setVisible( False )
        
        self._queuedMessageToolBar.appendMessage(text, timeoutMs)
    
    def closeEvent( self, event ):
        """NOT A PUBLIC API
        Close event handler.
        Shows save files dialog. Cancels close, if dialog was rejected
        """
        # request close all documents
        if not core.workspace().askToCloseAll():
            event.ignore()
            return

        core.aboutToTerminate.emit()
        self.hide()

        core.workspace().forceCloseAllDocuments()

        self._saveState()
        self._saveGeometry()

        return QMainWindow.closeEvent(self, event)
    
    def _onHideAllWindows(self):
        """Close all visible windows for get as much space on the screen, as possible
        """
        self.hideAllWindows.emit()
        for dock in self.findChildren(DockWidget):
            dock.hide()

    def _saveState(self):
        """Save window state to main_window_state.bin file in the config directory
        """
        state = self.saveState()
        try:
            with open(self._STATE_FILE, 'w') as f:
                f.write(state)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            QMessageBox.critical(None,
                                self.tr("Cannot save main window state"),
                                self.tr( "Cannot create file '%s'\nError: %s" % (path, error)))
            return
    
    def loadState(self):
        """Restore window state from main_window_state.bin and config.
        Called by the core after all plugins had been initialized
        """
        self._restoreGeometry()

        state = None
        if os.path.exists(self._STATE_FILE):
            try:
                with open(self._STATE_FILE, 'r') as f:
                    state = f.read()
            except (OSError, IOError), ex:
                error = unicode(str(ex), 'utf8')
                QMessageBox.critical(None,
                                    self.tr("Cannot restore main window state"),
                                    self.tr( "Cannot read file '%s'\nError: %s" % (path, error)))
        
        if state is not None:
            self.restoreState(state)
        else:  # not state, first start
            self.showMaximized()
            for dock in self.findChildren(DockWidget):
                dock.show()
        
    def _saveGeometry(self):
        """Save window geometry to the config file
        """
        geometry = {}
        geometry["X"], geometry["Y"], geometry["Width"], geometry["Height"] = self.geometry().getRect()
        geometry["Maximized"] = self.isMaximized()
        
        try:
            with open(self._GEOMETRY_FILE, 'w') as f:
                json.dump(geometry, f, sort_keys=True, indent=4)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            text = "Failed to save popular directories to '%s': %s" % (self._GEOMETRY_FILE, error)
            print >> sys.stderr, error

    def _restoreGeometry(self):
        """Restore window geometry to the config file
        """
        if os.path.exists(self._GEOMETRY_FILE):
            try:
                with open(self._GEOMETRY_FILE, 'r') as f:
                    geometry = json.load(f)
            except (OSError, IOError, ValueError), ex:
                error = unicode(str(ex), 'utf8')
                text = "Failed to load main window geometry from '%s': %s" % (self._GEOMETRY_FILE, error)
                self.appendMessage(text)
            
            self.setGeometry(geometry["X"], geometry["Y"], geometry["Width"], geometry["Height"])
            if geometry["Maximized"]:
               self.showMaximized()

    def dragEnterEvent( self, event):
        """QMainWindow method reimplementation.
        Say, that we are ready to accept dragged urls
        """
        if  event.mimeData().hasUrls() :
            # accept drag
            event.acceptProposedAction()
        
        # default handler
        QMainWindow.dragEnterEvent(self, event)
    
    def dropEvent( self, event ):
        """QMainWindow method reimplementation.
        Open dropt files
        """
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                localFile = url.toLocalFile()
                if os.path.isfile(localFile):
                    core.workspace().openFile(localFile)
                elif os.path.isdir(localFile):
                    self.directoryDropt.emit(localFile)
        
        # default handler
        QMainWindow.dropEvent(self, event)
