"""
core --- Instances of core classes, initialize and terminate the system
=======================================================================

Module initializes system at startup, terminates it, when mksv3 closed,
and used for get core instances, such as main window, workspace, etc.

"""

import os.path

from PyQt4.QtGui import qApp

from PyQt4.fresh import pSettings

import mks.resources.icons

DATA_FILES_PATH = os.path.join(os.path.dirname(__file__), '..')

class Core:
    """Core object initializes system at startup and terminates at close.
    
    It creates instances of other core modules and holds references to it
    """
    def init(self):
        """Initialize core.
        
        Called only by main()
        """
        pSettings.setDefaultProperties(pSettings.Properties(qApp.applicationName(), \
                                                            "1.0.0",
                                                            pSettings.Normal))
        self._mainWindow = mks.core.mainwindow.MainWindow()
        self._config = mks.core.config.createConfig()
        self._workspace = mks.core.workspace.Workspace(self._mainWindow)
        self._mainWindow.setWorkspace(self._workspace)
        self._workspace.setTextEditorClass(mks.plugins.editor.Editor) 
        
        self._mainWindow.statusBar().addPermanentWidget(mks.plugins.editortoolbar.EditorToolBar(self._mainWindow.statusBar()))
        
        # Create plugins
        self._appShortcuts = mks.plugins.appshortcuts.AppShortcuts()
        self._searchreplace = mks.plugins.searchreplace.SearchReplace()
        self._fileBrowser = mks.plugins.filebrowser.FileBrowser()
        self._editorShortcuts = mks.plugins.editorshortcuts.EditorShortcutsDialog().exec_()

    def term(self):
        """Terminate plugins and core modules
        
        Called only by main()
        """
        del self._searchreplace
        del self._fileBrowser
        del self._appShortcuts
        mks.resources.icons.qCleanupResources()

    def mainWindow(self):
        """Get :class:`mks.core.mainwindow.MainWindow` instance
        """
        return self._mainWindow

    def menuBar(self):
        """Get main window `menu bar <http://api.monkeystudio.org/fresh/classp_actions_node_menu_bar.html>`_ instance
        """
        return self._mainWindow.menuBar()

    def workspace(self):
        """Get :class:`mks.core.workspace.Workspace` instance
        """
        return self._workspace

    def config(self):
        """Get :class:`mks.core.config.Config` instance
        """
        return self._config
        
    def messageManager(self):
        """Get `queued message bar <http://api.monkeystudio.org/fresh/classp_queued_message_tool_bar.html>`_ instance
        """
        return self._mainWindow.queuedMessageToolBar()

core = Core()
import mks.core.mainwindow # imports after core has been created, hack for fix cross-imports problem
import mks.core.config
# Plugins
import mks.plugins.editor
import mks.plugins.editortoolbar
import mks.plugins.searchreplace
import mks.plugins.filebrowser
import mks.plugins.appshortcuts
import mks.plugins.editorshortcuts


"""TODO restore or delete old code
def _isXmas():
    return datetime.now().month in (11, 12, 1,)

def _showMessage(splash, message):
    if _isXmas():
        splash.showMessage(message, Qt.AlignRight | Qt.AlignBottom, Qt.red)
    else:
        splash.showMessage(message, Qt.AlignRight | Qt.AlignBottom, Qt.white)
    # no update without hide/show
    splash.hide()
    splash.show()

# create splashscreen
if _isXmas():
    pixmap = "splashscreen_christmas.png"
else:
    pixmap = "splashscreen.png"

splash = QSplashScreen (QIcon(':/mksicons/pixmap.png'))

ft = QFont( splash.font() )
if sys.platform.startswith('win'): # Windows platform
    ft.setPointSize( ft.pointSize() -2 )
ft.setBold( True )
splash.setFont( ft )
splash.show()

# restore application style
_showMessage( splash, splash.tr( 'Initializing Style...' ) )
qApp.setStyle(settings().value('MainWindow/Style', 'system').toString())

# set default settings if first time running
if  settings().value( "FirstTimeRunning", True ) :
    settings().setDefaultSettings()

# initialize locales
_showMessage( splash, splash.tr( "Initializing locales..." ) )
translationsManager().setFakeCLocaleEnabled( True )
translationsManager().addTranslationsMask( "qt*.qm" )
translationsManager().addTranslationsMask( "assistant*.qm" )
translationsManager().addTranslationsMask( "designer*.qm" )
translationsManager().addTranslationsMask( "monkeystudio*.qm" )
translationsManager().addForbiddenTranslationsMask( "assistant_adp*.qm" )
translationsManager().setTranslationsPaths( settings().storagePaths( Settings.SP_TRANSLATIONS ) )

# init translations
_showMessage( splash, splash.tr( "Initializing Translations..." ) )
if  not settings().value( "Translations/Accepted" ).toBool() :
    locale = TranslationDialog.getLocale( translationManager )

    if  not locale.isEmpty() :
        settings().setValue( "Translations/Locale", locale )
        settings().setValue( "Translations/Accepted", True )
        translationManager.setCurrentLocale( locale )
        translationManager.reloadTranslations()


translationManager.setCurrentLocale( settings().value( "Translations/Locale" ).toString() )
translationManager.reloadTranslations()

# init shortcuts editor
_showMessage( splash, splash.tr( "Initializing Actions Manager..." ) )
actionsManager().setSettings( settings() )


# init shell and commands
_showMessage( splash, splash.tr( "Initializing Shell..." ) )
interpreter()

# start console manager
_showMessage( splash, splash.tr( "Initializing Console..." ) )
consoleManager()

# init abbreviations manager
_showMessage( splash, splash.tr( "Initializing abbreviations manager..." ) )
abbreviationsManager()

# init file manager
_showMessage( splash, splash.tr( "Initializing file manager..." ) )
fileManager()

# load mks scripts
_showMessage( splash, splash.tr( "Executing scripts..." ) )
interpreter().loadHomeScripts()

# init pluginsmanager
_showMessage( splash, splash.tr( "Initializing Plugins..." ) )
pluginsManager().loadsPlugins()

# restore session
_showMessage( splash, splash.tr( "Restoring Session..." ) )
if  mks.monkeystudio.restoreSessionOnStartup() :
    workspace().fileSessionRestore_triggered()


# ready
_showMessage( splash, splash.tr( "%1 v%2 (%3) Ready" ).arg( 
mks.core.config.PACKAGE_NAME, mks.core.config.PACKAGE_VERSION, mks.core.config.PACKAGE_VERSION_STR ) )

# finish splashscreen
splash.finish( mainWindow() )

# show settings dialog the first time user start program
if  settings().value( "FirstTimeRunning", True ).toBool() :
    # execute settings dialog
    if  UISettings.instance().exec_() :
        settings().setValue( "FirstTimeRunning", False )

# prepare apis
mks.monkeystudio.prepareAPIs()

def pluginsManager():
    global _pluginsManager
    if _pluginsManager:
        _pluginsManager = PluginsManager( mainWindow() )
    return _pluginsManager

def actionsManager():
    return menuBar().actionsManager()

def recentsManager():
    global _recentsManager
    if _recentsManager is None:
        _recentsManager = pRecentsManager( mainWindow() )
    return _recentsManager

def projectsManager():
    global _projectsManager
    if _projectsManager is None:
        _projectsManager = XUPProjectManager( mainWindow() )
    return _projectsManager

def fileManager():
    global _fileManager
    if _fileManager is None:
        _fileManager = pFileManager( mainWindow() )
    return _fileManager


def consoleManager():
    global _consoleManager
    if _consoleManager is None:
        _consoleManager = pConsoleManager( mainWindow() )
    return _consoleManager

def interpreter():
    global _interpreter
    if _interpreter is None:
        _interpreter = MkSShellInterpreter.instance( mainWindow() )
    return _interpreter

def abbreviationsManager():
    global _abbreviationsManager
    if _abbreviationsManager is None:
        _abbreviationsManager = pAbbreviationsManager( mainWindow() )
    return _abbreviationsManager

def multiToolBar():
    global _multiToolBar
    if _multiToolBar is None:
        _multiToolBar = pMultiToolBar( mainWindow() )
    return _multiToolBar

def translationsManager():
    global _translationManager
    if _translationManager is None:
        _translationManager = TranslationManager( mainWindow() )
    return _translationManager
"""
