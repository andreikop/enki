"""
core --- Instances of core classes, initialize and terminate the system
=======================================================================

Module initializes system at startup, terminates it, when mksv3 closed,
and used for get core instances, such as main window, workspace, etc.
"""

import os.path
import shutil
import signal

from PyQt4.QtGui import qApp, QIcon
from PyQt4.QtCore import QTimer

import mks.core.defines
import mks.resources.icons # pylint: disable=W0404

DATA_FILES_PATH = os.path.join(os.path.dirname(__file__), '..')

_DEFAULT_CONFIG_PATH = os.path.join(DATA_FILES_PATH, 'config/mksv3.default.cfg')
_DEFAULT_CONFIG_SPEC_PATH = os.path.join(DATA_FILES_PATH, 'config/mksv3.spec.cfg')
_CONFIG_PATH = os.path.join(mks.core.defines.CONFIG_DIR, 'core.cfg')


class Core:
    """Core object initializes system at startup and terminates when closing.
    
    It creates instances of other core modules and holds references to it
    """
    def __init__(self):
        self._queuedMessageToolBar = None
        self._mainWindow = None
        self._workspace = None
        self._config = None
        self._uiSettingsManager = None
        self._indentHelpers = {}

        # List of core configurators. To be filled ONLY by other core modules. Readed ONLY by core.uisettings
        # Use direct access to the list, no methods are provided
        self.moduleConfiguratorClasses = []

        self._loadedPlugins = []

    def _prepareToCatchSigInt(self):
        """Catch SIGINT signal to close the application
        """
        signal.signal(signal.SIGINT, lambda signum, frame: qApp.closeAllWindows())
        # Let the interpreter to run every .5 sec. to catch signal
        self._checkSignalsTimer = QTimer()
        self._checkSignalsTimer.start(500)  # You may change this if you wish.
        self._checkSignalsTimer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        
    def init(self):
        """Initialize core.
        
        Called only by main()
        """
        self._prepareToCatchSigInt()
        
        qApp.setWindowIcon(QIcon(':/mksicons/monkey2.png') )

        # Imports are here for hack crossimport problem
        import mks.core.mainwindow  # pylint: disable=W0621,W0404
        self._mainWindow = mks.core.mainwindow.MainWindow()
        
        self._config = self._createConfig()

        import mks.core.workspace
        self._workspace = mks.core.workspace.Workspace(self._mainWindow)
        self._mainWindow.setWorkspace(self._workspace)
        
        import mks.core.uisettings  # pylint: disable=W0404
        self._uiSettingsManager = mks.core.uisettings.UISettingsManager()
        
        # Create plugins
        self._loadPlugin('editor')
        self._loadPlugin('editortoolbar')
        self._loadPlugin('searchreplace')
        self._loadPlugin('filebrowser')
        self._loadPlugin('appshortcuts')
        self._loadPlugin('editorshortcuts')
        self._loadPlugin('helpmenu')
        self._loadPlugin('associations')
        self._loadPlugin('mitscheme')
        self._loadPlugin('schemeindenthelper')
        self.messageToolBar().appendMessage("hi")

        self._mainWindow.loadState()

    def term(self):
        """Terminate plugins and core modules
        
        Called only by main()
        """
        while self._loadedPlugins:
            plugin = self._loadedPlugins.pop()
            if hasattr(plugin, 'uninstall'):  # TODO make plugin absract interface
                plugin.uninstall()
            del plugin
        
        if self._queuedMessageToolBar:
            self._mainWindow.removeToolBar(self._queuedMessageToolBar)
            del self._queuedMessageToolBar
        if self._mainWindow is not None:
            del self._mainWindow
        if self._workspace is not None:
            del self._workspace
        if self._config is not None:
            del self._config
        if self._uiSettingsManager is not None:
            del self._uiSettingsManager

        mks.resources.icons.qCleanupResources()

    def mainWindow(self):
        """Get :class:`mks.core.mainwindow.MainWindow` instance
        """
        return self._mainWindow

    def actionModel(self):
        """Get main window `action model <http://api.monkeystudio.org/fresh/classp_actions_node_model.html>`_ instance
        """
        return self._mainWindow.menuBar().model()

    def workspace(self):
        """Get :class:`mks.core.workspace.Workspace` instance
        """
        return self._workspace

    def config(self):
        """Get :class:`mks.core.config.Config` instance
        """
        return self._config
        
    def messageToolBar(self):
        """Get `queued message bar <http://api.monkeystudio.org/fresh/classp_queued_message_tool_bar.html>`_ instance
        """
        if self._queuedMessageToolBar is None:
            from mks.fresh.queuedmessage.pQueuedMessageToolBar import pQueuedMessageToolBar
            from PyQt4.QtCore import Qt
            
            self._queuedMessageToolBar = pQueuedMessageToolBar(self._mainWindow)
            self._mainWindow.addToolBar(Qt.BottomToolBarArea, self._queuedMessageToolBar)
            self._queuedMessageToolBar.setVisible( False )
        
        return self._queuedMessageToolBar
    
    def loadedPlugins(self):
        """Get list of curretly loaded plugins (::class:`mks.core.Plugin` instances)
        """
        return self._loadedPlugins
    
    def setIndentHelper(self, language, indentHelper):
        """Set  ::class:`mks.core.abstractdocument.IndentHelper` for language. Pass None to clear the value
        """
        if indentHelper is not None:
            self._indentHelpers[language] = indentHelper
        else:  # clear
            try:
                del self._indentHelpers[language]
            except KeyError:
                pass
        
    def indentHelper(self, language):
        """Get ::class:`mks.core.abstractdocument.IndentHelper` for the language
        
        Raises KeyError, if not available
        """
        return self._indentHelpers[language]

    def _loadPlugin(self, name):
        """Load plugin by it's module name
        """
        exec("import mks.plugins.%s as module" % name)  # pylint: disable=W0122
        self._loadedPlugins.append(module.Plugin())  # pylint: disable=E0602

    def _createDefaultConfigFile(self):
        """Create default configuration file, if it is not present
        Called only by _createConfig()
        """
        import mks.core.config  # pylint: disable=W0621,W0404
        
        if not os.path.exists(mks.core.defines.CONFIG_DIR):
            try:
                os.makedirs(mks.core.defines.CONFIG_DIR)
            except (OSError, IOError) as ex:
                raise UserWarning(u'Failed to create directory "%s". Error: %s\n' % \
                                  (mks.core.defines.CONFIG_DIR, unicode(str(ex), 'utf8')))
        try:
            shutil.copyfile(_DEFAULT_CONFIG_PATH, _CONFIG_PATH)
        except (OSError, IOError) as ex:
            raise UserWarning(u'Failed to create configuration file "%s". Error:\n%s' % \
                              (_CONFIG_PATH, unicode(str(ex), 'utf8')))
    
    def _createConfig(self):
        """Open main config file and return Config instance
         
        Function creates config file in user's home directory, if necessary,
        validates and opens it.
        """
        import mks.core.config  # pylint: disable=W0621,W0404
        
        haveFileInHome = os.path.exists(_CONFIG_PATH)
        
        # Create file, if not exists
        if not haveFileInHome:
            try:
                self._createDefaultConfigFile()
                haveFileInHome = True
            except UserWarning as ex:
                self.messageToolBar().appendMessage(unicode(ex))
        
        # Try to open
        if haveFileInHome:
            try:
                config = mks.core.config.Config(True, _CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
            except UserWarning as ex:
                messageString = unicode(ex) + '\n' + 'Using default configuration'
                self.messageToolBar().appendMessage(messageString)
                config = None
        else:
            config = None
        
        # Open default, if previous step failed
        if config is None:
            config = mks.core.config.Config(False, _DEFAULT_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
        
        return config

core = Core()  # pylint: disable=C0103
"""Core instance. It is accessible as: ::

    from mks.core.core import core
    core.anyMethod()
"""  # pylint: disable=W0105


"""
TODO restore or delete old code
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
"""  # pylint: disable=W0105

