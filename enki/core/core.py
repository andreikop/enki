"""
core --- Instances of core classes, initialize and terminate the system
=======================================================================

Module initializes system at startup, terminates it, when Enki closed,
and used for get core instances, such as main window, workspace, etc.
"""

import os.path
import shutil
import signal
import pkgutil

from PyQt4.QtGui import QApplication, QIcon
from PyQt4.QtCore import pyqtSignal, QObject, QTimer

import enki.core.defines
from enki.resources.icons import qInitResources, qCleanupResources

DATA_FILES_PATH = os.path.join(os.path.dirname(__file__), '..')

_DEFAULT_CONFIG_PATH = os.path.join(DATA_FILES_PATH, 'config/enki.default.json')
_CONFIG_PATH = os.path.join(enki.core.defines.CONFIG_DIR, 'enki.json')


class Core(QObject):
    """Core object initializes system at startup and terminates when closing.
    
    It creates instances of other core modules and holds references to it
    """
    
    restoreSession = pyqtSignal()
    """
    restoreSession()
    
    **Signal** for session plugin.
    Emitted, when initialization has been finished and all files,
    listed in the command line has been opened.
    Only if user hadn't passed --no-session key
    """  # pylint: disable=W0105

    aboutToTerminate = pyqtSignal()
    """
    aboutToTerminate()
    
    **Signal** emitted, before closing all files and terminating Enki
    """  # pylint: disable=W0105

    settingsDialogAccepted = pyqtSignal()
    """
    settingsDialogAccepted()
    
    **Signal** emitted, when settings dialog had been accepted
    """  # pylint: disable=W0105

    def __init__(self):
        QObject.__init__(self)
        self._mainWindow = None
        self._workspace = None
        self._config = None
        self._uiSettingsManager = None
        self._fileFilter = None
        self._indentHelpers = {}
        self._loadedPlugins = []

    def _prepareToCatchSigInt(self):
        """Catch SIGINT signal to close the application
        """
        signal.signal(signal.SIGINT, lambda signum, frame: QApplication.instance().closeAllWindows())
        self._checkSignalsTimer = QTimer()
        self._checkSignalsTimer.start(500)
        self._checkSignalsTimer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        
    def init(self, profiler):
        """Initialize core.
        
        Called only by main()
        """
        self._prepareToCatchSigInt()

        if profiler is not None:
            profiler.stepDone('Catch SIGINT')

        qInitResources()

        QApplication.instance().setWindowIcon(QIcon(':/enkiicons/enki.png') )

        import enki.core.actionmanager
        self._actionManager = enki.core.actionmanager.ActionManager(self)
        
        # Imports are here for hack crossimport problem
        import enki.core.mainwindow  # pylint: disable=W0621,W0404
        self._mainWindow = enki.core.mainwindow.MainWindow()
        
        if profiler is not None:
            profiler.stepDone('create main window')

        self._config = self._createConfig()

        if profiler is not None:
            profiler.stepDone('create config')

        import enki.core.uisettings  # pylint: disable=W0404
        self._uiSettingsManager = enki.core.uisettings.UISettingsManager()
        if profiler is not None:
            profiler.stepDone('Create UISettings')
        
        import enki.core.workspace
        if profiler is not None:
            profiler.stepDone('import workspace')

        self._workspace = enki.core.workspace.Workspace(self._mainWindow)
        self._mainWindow.setWorkspace(self._workspace)
        if profiler is not None:
            profiler.stepDone('create workspace')

        import enki.core.filefilter
        self._fileFilter = enki.core.filefilter.FileFilter()
        if profiler is not None:
            profiler.stepDone('Create FileFilter')
        
        import enki.core.locator
        self._locator = enki.core.locator.Locator(self._mainWindow)
        if profiler is not None:
            profiler.stepDone('Create Locator')
        
        # Create plugins
        if profiler is not None:
            firstPlugin = True
        pluginsPath = os.path.join(os.path.dirname(__file__), '../plugins')
        for loader, name, isPackage in pkgutil.iter_modules([pluginsPath]):
            if profiler is not None and firstPlugin:
                firstPlugin = False
                profiler.stepDone('Search plugins')
            self._loadPlugin(name)
            
            if profiler is not None:
                profiler.stepDone('  Load %s' % name)

    def term(self):
        """Terminate plugins and core modules
        
        Called only by main()
        """
        while self._loadedPlugins:
            plugin = self._loadedPlugins.pop()
            plugin.del_()

        if self._locator is not None:
            self._locator.del_()
            del self._locator
        if self._fileFilter is not None:
            del self._fileFilter
        if self._uiSettingsManager is not None:
            del self._uiSettingsManager
        if self._workspace is not None:
            self._workspace.del_()
            del self._workspace
        if self._mainWindow is not None:
            self._mainWindow.del_()
            del self._mainWindow
        if self._config is not None:
            del self._config

        qCleanupResources()

    def mainWindow(self):
        """Get :class:`enki.core.mainwindow.MainWindow` instance
        """
        return self._mainWindow

    def actionManager(self):
        """Get main window ::class:`enki.core.actionmanager.ActionManager` instance
        """
        return self._actionManager

    def workspace(self):
        """Get :class:`enki.core.workspace.Workspace` instance
        """
        return self._workspace

    def config(self):
        """Get :class:`enki.core.config.Config` instance
        """
        return self._config
    
    def loadedPlugins(self):
        """Get list of curretly loaded plugins (::class:`enki.core.Plugin` instances)
        """
        return self._loadedPlugins
    
    def setIndentHelper(self, language, indentHelper):
        """Set  ::class:`enki.core.abstractdocument.IndentHelper` for language. Pass None to clear the value
        """
        if indentHelper is not None:
            self._indentHelpers[language] = indentHelper
        else:  # clear
            try:
                del self._indentHelpers[language]
            except KeyError:
                pass
        
    def indentHelper(self, language):
        """Get ::class:`enki.core.abstractdocument.IndentHelper` for the language
        
        Raises KeyError, if not available
        """
        return self._indentHelpers[language]

    def _loadPlugin(self, name):
        """Load plugin by it's module name
        """
        exec("import enki.plugins.%s as module" % name)  # pylint: disable=W0122
        self._loadedPlugins.append(module.Plugin())  # pylint: disable=E0602

    def _createDefaultConfigFile(self):
        """Create default configuration file, if it is not present
        Called only by _createConfig()
        """
        import enki.core.config  # pylint: disable=W0621,W0404
        
        if not os.path.exists(enki.core.defines.CONFIG_DIR):
            try:
                os.makedirs(enki.core.defines.CONFIG_DIR)
            except (OSError, IOError) as ex:
                raise UserWarning(u'Failed to create directory "%s". Error: %s\n' % \
                                  (enki.core.defines.CONFIG_DIR, unicode(str(ex), 'utf8')))
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
        import enki.core.config  # pylint: disable=W0621,W0404
        
        haveFileInHome = os.path.exists(_CONFIG_PATH)
        
        # Create file, if not exists
        if not haveFileInHome:
            try:
                self._createDefaultConfigFile()
                haveFileInHome = True
            except UserWarning as ex:
                self.mainWindow().appendMessage(unicode(ex))
        
        # Try to open
        config = None
        if haveFileInHome:
            try:
                config = enki.core.config.Config(True, _CONFIG_PATH)
            except UserWarning:  # messages are shown by the Config class
                pass
        
        # Open default, if previous step failed
        if config is None:
            config = enki.core.config.Config(False, _DEFAULT_CONFIG_PATH)
        
        return config
    
    def fileFilter(self):
        """Negative file filter
        
        See ::mod:`enki.core.filefilter`
        """
        return self._fileFilter
    
    def locator(self):
        """::class:`enki.core.locator.Locator` instance
        
        Widget, which appears on Ctrl+L. Allows to execute textual commands
        Extendable with new commands
        """
        return self._locator
    
    def uiSettingsManager(self):
        """::class:`enki.core.uisettings.UISettingsManager` instance
        
        Settings dialogue (Edit -> Settings) manager.
        Use it for adding own settings to the dialogue
        """
        return self._uiSettingsManager

core = Core()  # pylint: disable=C0103
"""Core instance. It is accessible as: 

::

    from enki.core.core import core
    core.anyMethod()
"""  # pylint: disable=W0105
