"""
mainwindow --- Main window of the UI. Fills main menu.
======================================================


Module contains :class:`mks.core.mainwindow.MainWindow` implementation
"""

import os.path

from PyQt4.QtCore import pyqtSignal, QSize, Qt
from PyQt4.QtGui import QHBoxLayout, QIcon, QMessageBox, QSizePolicy, QStatusBar, QToolBar, QVBoxLayout, QWidget

from PyQt4.QtGui import QMainWindow

from mks.fresh.dockwidget.pDockWidget import pDockWidget
from mks.fresh.actionmanager.ActionManager import ActionManager
from mks.fresh.actionmanager.pActionsMenuBar import pActionsMenuBar

from mks.core.core import core
import mks.core.defines

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
        self._statusBar = QStatusBar(self)
        self._statusBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        
        def seperator(menu):
            """Subfunction for insert separator to the menu"""
            self._actionManager.action(menu).menu().addSeparator()
        
        # pylint: disable=C0301  
        # enable long lines for menu items
        # Menu or action path                   Name                                Icon            Shortcut        Hint                     Action enabled
        tr = self.tr  # pylint: disable=C0103
        menu  ("mFile",                               tr("File"                  ), ""            )
        action("mFile/aOpen",                         tr("&Open..."              ), "open.png",     "Ctrl+O" ,      tr("Open a file"            ), True )
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
        seperator("mFile")

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
        
        #TODO save session on close
        # save session if needed
        #if  mks.monkeystudio.saveSessionOnClose() :
        #    core.workspace().fileSessionSave_triggered()

        # request close all documents
        if not core.workspace().closeAllDocuments():
            event.ignore()
            return
        
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

#   TODO restore or delete old code
#    urlsDropped = pyqtSignal()
#
#        core.recentsManager().openFileRequested.connect(core.fileManager().openFile)
#        self._actionManager.action( "mFile/mSession/aSave" ).triggered.connect(core.workspace().fileSessionSave_triggered)
#        self._actionManager.action( "mFile/mSession/aRestore" ).triggered.connect(core.workspace().fileSessionRestore_triggered)
#        self._actionManager.action( "mFile/aQuickPrint" ).triggered.connect(core.workspace().fileQuickPrint_triggered)
#        self._actionManager.action( "mFile/aPrint" ).triggered.connect(core.workspace().filePrint_triggered)
#        # edit connection
#        self._actionManager.action( "mEdit/aTranslations" ).triggered.connect(core.workspace().editTranslations_triggered)
#        self._actionManager.action( "mEdit/aExpandAbbreviation" ).triggered.connect(core.workspace().onEditExpandAbbreviation)
#        self._actionManager.action( "mEdit/aPrepareAPIs" ).triggered.connect(core.workspace().editPrepareAPIs_triggered)
#        # view connection
#        agStyles.styleSelected.connect(self.changeStyle)

#        # project connection
#        core.recentsManager().openProjectRequested.connect(core.projectsManager().openProject)
#        core.projectsManager().fileDoubleClicked.connect(core.workspace().openFile)
#        # plugins menu
#        # window menu
#        self._actionManager.action( "mWindow/aTile" ).triggered.connect(core.workspace().tile)
#        self._actionManager.action( "mWindow/aCascase" ).triggered.connect(core.workspace().cascade)
#        self._actionManager.action( "mWindow/aMinimize" ).triggered.connect(core.workspace().minimize)
#        self._actionManager.action( "mWindow/aRestore" ).triggered.connect(core.workspace().restore)
#
#   TODO can't configure pylint to ignore long lines in the commented code
#        mb.menu( "mRecents", tr("&Recents" ), QIcon(":/mksicons/recents.png" ) )
#        mb.action( "mRecents/aClear", tr("&Clear" ), QIcon(":/mksicons/clear.png" ), '', tr("Clear the recents file list" ) )
#        mb.action( "mRecents/aSeparator1" )
#        mb.action( "aSeparator1" )
#        mb.menu( "mSession", tr("Session" ), QIcon(":/mksicons/session.png" ) )
#        mb.action( "mSession/aSave", tr("Save" ), QIcon(":/mksicons/save.png" ), '', tr("Save the current session file list" ) )
#        mb.action( "mSession/aRestore", tr("Restore" ), QIcon(":/mksicons/restore.png" ), '', tr("Restore the current session file list" ) )
#        mb.action( "aSeparator4" )
#        mb.action( "aQuickPrint", tr("Quic&k Print" ), QIcon(":/mksicons/quickprint.png" ), '', tr("Quick print the current file" ) ).setEnabled( False )
#        mb.action( "aPrint", tr("&Print..." ), QIcon(":/mksicons/print.png" ), "Ctrl+P", tr("Print the current file" ) ).setEnabled( False )
#        mb.action( "aSeparator5" )
#        mb.action( "aSettings", tr("Settings..." ), QIcon( ":/mksicons/settings.png" ), "", tr("Edit the application settings" ) )
#        mb.action( "aTranslations", tr("Translations..." ), QIcon( ":/mksicons/translations.png" ), "Ctrl+T", tr("Change the application translations files" ) )
#        mb.action( "aSeparator1" )
#        mb.action( "aSeparator3" )
#        mb.menu( "mAllCommands", tr("&All Commands" ), QIcon( ":/mksicons/commands.png" ) )
#        
#        mb.action( "aSeparator5" )
#        mb.action( "aExpandAbbreviation", tr("Expand Abbreviation" ), QIcon( ":/mksicons/abbreviation.png" ), "Ctrl+E", tr("Expand Abbreviation" ) ).setEnabled( False )
#        mb.action( "aPrepareAPIs", tr("Prepare APIs" ), QIcon( ":/mksicons/prepareapis.png" ), "Ctrl+Alt+P", tr("Prepare the APIs files for auto completion / calltips" ) )
#        mb.menu( "mStyle", tr("&Style" ), QIcon( ":/mksicons/style.png" ) )
#        mb.menu( "mProject", tr("Project" ) )
#        mb.beginGroup( "mProject" )
#        
#        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atNew ) )
#        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atOpen ) )
#        mb.action( "aSeparator1" )
#        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atClose ) )
#        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atCloseAll ) )
#        mb.action( "aSeparator2" )
#        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atEdit ) )
#        mb.action( "aSeparator3" )
#        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atAddFiles ) )
#        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atRemoveFiles ) )
#        mb.action( "aSeparator4" )
#        
#        mb.menu( "mRecents", tr("&Recents" ), QIcon( ":/mksicons/recents.png" ) )
#        mb.action( "mRecents/aClear", tr("&Clear" ), QIcon( ":/mksicons/clear.png" ), '', tr("Clear the recents projects list" ) )
#        mb.action( "mRecents/aSeparator1" )
#        mb.endGroup()
#        
#        mb.menu( "mBuilder", tr("Build" ) ).menuAction().setEnabled( False )
#        mb.menu( "mBuilder" ).menuAction().setVisible( False )
#        
#        mb.beginGroup( "mBuilder" )
#        mb.menu( "mBuild", tr("&Build" ), QIcon( ":/mksicons/build.png" ) )
#        mb.menu( "mRebuild", tr("&Rebuild" ), QIcon( ":/mksicons/rebuild.png" ) )
#        mb.menu( "mClean", tr("&Clean" ), QIcon( ":/mksicons/clean.png" ) )
#        mb.menu( "mExecute", tr("&Execute" ), QIcon( ":/mksicons/execute.png" ) )
#        mb.menu( "mUserCommands", tr("&User Commands" ), QIcon( ":/mksicons/misc.png" ) )
#        mb.action( "aSeparator1" )
#        mb.endGroup()
#        
#        mb.menu( "mDebugger", tr("Debugger" ) ).menuAction().setEnabled( False )
#        mb.menu( "mDebugger" ).menuAction().setVisible( False )
#        mb.menu( "mInterpreter", tr("Interpreter" ) ).menuAction().setEnabled( False )
#        mb.menu( "mInterpreter" ).menuAction().setVisible( False )
#        mb.menu( "mPlugins", tr("Plugins" ) )
#        
#        mb.beginGroup( "mPlugins" )
#        mb.action( "aSeparator1" )
#        mb.endGroup()
#        
#        mb.menu( "mWindow", tr("Window" ) )

#        mb.beginGroup( "mWindow" )
#        mb.action( "aCascase", tr("&Cascade" ), QIcon( "" ), '', tr("Cascade" ) )
#        mb.action( "aTile", tr("&Tile" ), QIcon( "" ), '', tr("Tile" ) )
#        mb.action( "aMinimize", tr("&Minimize" ), QIcon( "" ), '', tr("Minimize" ) )
#        mb.action( "aRestore", tr("&Restore" ), QIcon( "" ), '', tr("Restore normal size" ) )
#        mb.endGroup()
#        
#        mb.action( "aAbout", tr("&About..." ), QIcon( ":/mksicons/monkey2.png" ), '', tr("About application..." ) )
#        # create action for styles
#        agStyles = pStylesActionGroup( tr("Use %1 style" ), mb.menu( "mNavigation/mStyle" ) )
#        agStyles.setCurrentStyle( core.settings().value( "MainWindow/Style" ).toString() )
#        mb.menu( "mNavigation/mStyle" ).addActions( agStyles.actions() )
#        
#        # create plugins actions
#        core.pluginsManager().menuHandler().setMenu( mb.menu( "mPlugins" ) )        

#    def dragEnterEvent( self, event ):
#        # if correct mime and same tabbar
#        if  event.mimeData().hasUrls() :
#            # accept drag
#            event.acceptProposedAction()
#        
#        # default event
#        pMainWindow.dragEnterEvent( self, event )
#    
#    def dropEvent( self, event ):
#        if  event.mimeData().hasUrls() :
#            self.urlsDropped.emit( event.mimeData().urls () )
#        
#        # default event
#        pMainWindow.dropEvent( self, event )
#    
#def updateMenuVisibility( self, menu ):
#        menuAction = menu.menuAction()
#        
#        menuVisible = False

#        for action in menu.actions():
#            if  action.isSeparator() :
#                continue
#            
#            subMenu = action.menu()

#            if  subMenu :
#                if  self.updateMenuVisibility( subMenu ) :
#                    menuVisible = True
#            else:
#                menuVisible = True
#        
#        menuAction.setVisible( menuVisible )
#        menuAction.setEnabled( menuVisible )
#        
#        return menuVisible    