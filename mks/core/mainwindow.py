"""
mainwindow --- Main window of the UI. Fills main menu.
======================================================


Module contains :class:`mks.core.mainwindow.MainWindow` implementation
"""

import os.path

from PyQt4.QtCore import pyqtSignal, QSize, Qt, QTimer
from PyQt4.QtGui import QHBoxLayout, QIcon, QLabel, QMessageBox, \
                        QSizePolicy, QStatusBar, QToolBar, QVBoxLayout, QWidget

from PyQt4.QtGui import QMainWindow

from mks.fresh.dockwidget.pDockWidget import pDockWidget
from mks.fresh.actionmanager.ActionManager import ActionManager
from mks.fresh.actionmanager.pActionsMenuBar import pActionsMenuBar

from mks.core.core import core
import mks.core.defines

class _StatusBar(QStatusBar):
    """Extended status bar. Supports HTML messages
    """
    def __init__(self, *args):
        QStatusBar.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        
        self._actionManager.action( "mFile/aOpen" ).setEnabled(True)
        self._actionManager.action( "mFile/aOpen" ).triggered.connect(self.myCoolMethod)
    
    MainWindow instance is accessible as: ::
    
        from mks.core.core import core
        core.mainwindow()
    
    Created by monkeycore
    """
    
    hideAllWindows = pyqtSignal()
    """
    hideAllWindows()
    
    **Signal** emitted, when user toggled "Hide all" .
    Dock widgets are closed automatically, but other widgets, i.e. search widget, must catch this signal and close
    themselves.
    """  # pylint: disable=W0105
    
    def __init__(self):
        QMainWindow.__init__(self)
        
        self._queuedMessageToolBar = None
        self._actionManager = None
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
        self.setWindowIcon( QIcon(':/mksicons/monkey2.png') )
        
        self.setStyleSheet("QTreeView:focus {border: 1px solid red}")

        # Create top tool bar
        self._topToolBar = self.addToolBar("topToolBar")
        self._topToolBar.setObjectName("topToolBar")
        self._topToolBar.setMovable(False)
        self._topToolBar.setIconSize(QSize(16, 16))
        toolBarStyleSheet = "QToolBar {border: 0; border-bottom-width: 0.5; border-bottom-style: solid}"""
        self._topToolBar.setStyleSheet(toolBarStyleSheet)

        # Create menu bar
        self._menuBar = pActionsMenuBar(self)
        self._menuBar.setAutoFillBackground(False)
        menuBarStyleSheet = """
        QMenuBar {background-color: transparent;}
        QMenuBar::item:!selected {background: transparent;}
        """
        self._menuBar.setStyleSheet(menuBarStyleSheet)
        self._menuBar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._actionManager = ActionManager(self._menuBar)
        self._menuBar.setModel(self._actionManager)
        self._topToolBar.addWidget(self._menuBar)
        self._topToolBar.addSeparator()

        # Create status bar
        self._statusBar = _StatusBar(self)
        self._topToolBar.addWidget(self._statusBar)
        
        self._createMenuStructure()
        
        # create central layout
        widget = QWidget(self)
        self._centralLayout = QVBoxLayout(widget)
        self._centralLayout.setMargin(0)
        self.setCentralWidget(widget)
        
    def del_(self):
        """Explicitly called destructor
        """
        if self._queuedMessageToolBar:
            self.removeToolBar(self._queuedMessageToolBar)
            del self._queuedMessageToolBar

        for act in self._createdActions:
            self._actionManager.removeAction(act, False)
        for menuPath in self._createdMenuPathes[::-1]:
            self._actionManager.removeMenu(menuPath)
        
        self.menuBar().setModel( None )
        # FIXME self.settings().sync()  # write window and docs geometry

    def _initTopWidget(self):
        """Create top widget and put it on its place
        """
        
    def _createMenuStructure(self):
        """Fill menu bar with items. The majority of items are not connected to the slots,
        Connections made by module, which implements menu item functionality, but, all items are in one place,
        because it's easier to create clear menu layout
        """
        # create menubar menus and actions
        
        def menu(path, name, icon):
            """Subfunction for create a menu in the main menu"""
            menuObject = self._actionManager.addMenu(path, name)
            if icon:
                menuObject.setIcon(QIcon(':/mksicons/' + icon))
            self._createdMenuPathes.append(path)
            
        def action(path, name, icon, shortcut, tooltip, enabled):  # pylint: disable=R0913
            """Subfunction for create an action in the main menu"""
            if icon:  # has icon
                actObject = self._actionManager.addAction(path, name, QIcon(':/mksicons/' + icon), shortcut)
            else:
                actObject = self._actionManager.addAction(path, name, shortcut=shortcut)
            actObject.setStatusTip(tooltip)
            actObject.setEnabled(enabled)
            self._createdActions.append(actObject)
        
        def separator(menu):
            """Subfunction for insert separator to the menu"""
            self._actionManager.action(menu).menu().addSeparator()
        
        # pylint: disable=C0301  
        # enable long lines for menu items
        # Menu or action path                   Name                                Icon            Shortcut        Hint                     Action enabled
        tr = self.tr  # pylint: disable=C0103
        menu  ("mFile",                               tr("File"                  ), ""            )
        action("mFile/aOpen",                         tr("&Open..."              ), "open.png",     "Ctrl+O" ,      tr("Open a file"            ), True )
        menu  ("mFile/mUndoClose",                    tr("Undo Close"            ), "recents.png" )
        menu  ("mFile/mSave",                         tr("&Save"                 ), "save.png"    )
        action("mFile/mSave/aCurrent",                tr("&Save"                 ), "save.png" ,    "Ctrl+S" ,      tr("Save the current file"  ), False)
        action("mFile/mSave/aSaveAs",                 tr("Save As..."            ), "save.png" ,    "Ctrl+Alt+S" ,  ""                           , False)
        action("mFile/mSave/aAll",                    tr("Save &All"             ), "saveall.png",  'Shift+Ctrl+S', tr("Save all files"         ), False)
        menu  ("mFile/mReload",                       tr("&Reload"               ), "reload.png"    )
        action("mFile/mReload/aCurrent",              tr("Reload"                ), "reload.png"  , 'F5',           tr("Reload the current file"), False)
        action("mFile/mReload/aAll",                  tr("Reload All"            ), "reload.png"  , 'Alt+Shift+F5', tr("Reload all files"       ), True)
        action("mFile/aNew",                          tr("&New file..."          ), "new.png",      'Ctrl+N',       tr("New file"               ), True )
        menu  ("mFile/mClose",                        tr("&Close"                ), "close.png"   )
        action("mFile/mClose/aCurrent",               tr("&Close"                ), "close.png",    "Ctrl+W",       tr("Close the current file" ), False)
        action("mFile/mClose/aAll",                   tr("Close &All"            ), "closeall.png", 'Shift+Ctrl+W', tr("Close all files"        ), False)
        action("mFile/aPrint",                        tr("&Print..."             ), "print.png" ,   "Ctrl+P",       tr("Print the current file" ), False)

        menu  ("mView",                               tr("View"                  ), ""            )
        menu  ("mView/mZoom",                         tr("&Zoom"                 ), "search.png"  )

        menu  ("mEdit",                               tr("Edit"                  ), ""            )

        menu  ("mNavigation",                          tr("Navigation"            ), ""           ) 
        menu  ("mNavigation/mSearchReplace",           tr("&Search && Replace"    ), "search-replace-directory.png")
        menu  ("mNavigation/mBookmarks",               tr("&Bookmarks"            ), "bookmark.png")

        action("mNavigation/aNext",                   tr("&Next file"            ), "next.png",     "Ctrl+PgDown",    tr("Next file"              ), False)
        action("mNavigation/aPrevious",               tr("&Previous file"        ), "previous.png", "Ctrl+PgUp",     tr("Previous file"          ), False)
        action("mNavigation/aFocusCurrentDocument",   tr("Focus to editor"       ), "text.png",     "Ctrl+Return",  tr("Focus current document" ), False)
        action("mNavigation/aGoto",                   tr("Go go line..."         ), "goto.png",     "Ctrl+G",       tr("Go to line..."          ), False)
        menu  ("mNavigation/mFileBrowser",            tr("File browser"          ), ':/mksicons/open.png')

        menu  ("mSettings",                           tr("Settings"              ), ""            )

        menu  ("mDocks",                              tr("Docks"                 ), ""            )
        action("mDocks/aHideAll",                     tr("Hide all"              ), "",             "Shift+Esc",    tr("Hide all"               ), True)

        menu  ("mHelp",                               tr("Help"                  ), ""            )
        
        # docks
        self._actionManager.action( "mDocks/aHideAll" ).triggered.connect(self._onHideAllWindows)
    
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
        """Default title. Contains MkS name and version
        """
        return "%s v.%s" % (mks.core.defines.PACKAGE_NAME, mks.core.defines.PACKAGE_VERSION)
    
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
            from mks.fresh.queuedmessage.pQueuedMessageToolBar import pQueuedMessageToolBar
            from PyQt4.QtCore import Qt
            
            self._queuedMessageToolBar = pQueuedMessageToolBar(self)
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
        for dock in self.findChildren(pDockWidget):
            dock.hide()

    def _saveState(self):
        """Save window state to main_window_state.bin file in the config directory
        """
        path = os.path.join(mks.core.defines.CONFIG_DIR, "main_window_state.bin")
        state = self.saveState()
        try:
            with open(path, 'w') as f:
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

        path = os.path.join(mks.core.defines.CONFIG_DIR, "main_window_state.bin")
        state = None
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    state = f.read()
            except (OSError, IOError), ex:
                error = unicode(str(ex), 'utf8')
                QMessageBox.critical(None,
                                    self.tr("Cannot restore main window state"),
                                    self.tr( "Cannot read file '%s'\nError: %s" % (path, error)))
        
        if state is not None:
            self.restoreState(state)
        
    def _saveGeometry(self):
        """Save window geometry to the config file
        """
        section = core.config()["MainWindow"]
        section["X"], section["Y"], section["Width"], section["Height"] = self.geometry().getRect()
        section["Maximized"] = self.isMaximized()
        core.config().flush()
    
    def _restoreGeometry(self):
        """Restore window geometry to the config file
        """
        section = core.config()["MainWindow"]
        self.setGeometry(section["X"], section["Y"], section["Width"], section["Height"])
        if section["Maximized"]:
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
        
        # default handler
        QMainWindow.dropEvent(self, event)


#   TODO restore or delete old code
#        # edit connection
#        self._actionManager.action( "mEdit/aExpandAbbreviation" ).triggered.connect(core.workspace().onEditExpandAbbreviation)
#        self._actionManager.action( "mEdit/aPrepareAPIs" ).triggered.connect(core.workspace().editPrepareAPIs_triggered)

#        # project connection
#        core.recentsManager().openProjectRequested.connect(core.projectsManager().openProject)
#
#        mb.action( "aExpandAbbreviation", tr("Expand Abbreviation" ), QIcon( ":/mksicons/abbreviation.png" ), "Ctrl+E", tr("Expand Abbreviation" ) ).setEnabled( False )
#        mb.action( "aPrepareAPIs", tr("Prepare APIs" ), QIcon( ":/mksicons/prepareapis.png" ), "Ctrl+Alt+P", tr("Prepare the APIs files for auto completion / calltips" ) )
#        
