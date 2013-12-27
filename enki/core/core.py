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

from PyQt4.QtGui import QApplication, QIcon, QMessageBox
from PyQt4.QtCore import pyqtSignal, QObject, QTimer

import enki.core.defines
from enki.resources.icons import qInitResources, qCleanupResources

DATA_FILES_PATH = os.path.join(os.path.dirname(__file__), '..')

_DEFAULT_CONFIG_PATH = os.path.join(DATA_FILES_PATH, 'config/enki.default.json')
_CONFIG_PATH = os.path.join(enki.core.defines.CONFIG_DIR, 'enki.json')

_OLD_CONFIG_DIR = os.path.expanduser('~/.enki')


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

    # Add object here to avoid gardadge-collecting it. NOT FOR PLUGINS USE!!!
    _do_not_gargadge_collect_this_objects = []

    def __init__(self):
        QObject.__init__(self)
        self._mainWindow = None
        self._workspace = None
        self._config = None
        self._uiSettingsManager = None
        self._fileFilter = None
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

        profiler.stepDone('Catch SIGINT')

        qInitResources()

        QApplication.instance().setWindowIcon(QIcon(':/enkiicons/logo/32x32/enki.png') )

        self._initConfigDir()

        import enki.core.actionmanager
        self._actionManager = enki.core.actionmanager.ActionManager(self)

        # Imports are here for hack crossimport problem
        import enki.core.mainwindow  # pylint: disable=W0621,W0404
        self._mainWindow = enki.core.mainwindow.MainWindow()

        profiler.stepDone('create main window')

        self._config = self._createConfig()

        profiler.stepDone('create config')

        import enki.core.uisettings  # pylint: disable=W0404
        self._uiSettingsManager = enki.core.uisettings.UISettingsManager()
        profiler.stepDone('Create UISettings')

        import enki.core.workspace
        profiler.stepDone('import workspace')

        self._workspace = enki.core.workspace.Workspace(self._mainWindow)
        self._mainWindow.setWorkspace(self._workspace)
        profiler.stepDone('create workspace')

        import enki.core.filefilter
        self._fileFilter = enki.core.filefilter.FileFilter()
        profiler.stepDone('Create FileFilter')

        import enki.core.locator
        self._locator = enki.core.locator.Locator(self._mainWindow)
        profiler.stepDone('Create Locator')

        # Create plugins
        firstPlugin = True
        pluginsPath = os.path.join(os.path.dirname(__file__), '../plugins')
        for loader, name, isPackage in pkgutil.iter_modules([pluginsPath]):
            if firstPlugin:
                firstPlugin = False
                profiler.stepDone('Search plugins')
            self._loadPlugin(name)

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
        if self._actionManager is not None:
            self._actionManager.del_()
            del self._actionManager

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

    def _loadPlugin(self, name):
        """Load plugin by it's module name
        """
        exec("import enki.plugins.%s as module" % name)  # pylint: disable=W0122
        self._loadedPlugins.append(module.Plugin())  # pylint: disable=E0602

    def _initConfigDir(self):
        """Enki on Linux used to store configs in ~/.enki on Linux.
        Now it stores configs in ~/.config/.enki/.
        Move old configs
        """
        new_path = enki.core.defines.CONFIG_DIR

        if new_path != _OLD_CONFIG_DIR and \
           os.path.isdir(_OLD_CONFIG_DIR) and \
           not os.path.isdir(new_path):
            try:
                shutil.move(_OLD_CONFIG_DIR, new_path)
            except Exception as ex:
                text = 'Failed to move config directory from {} to {}: {}' \
                    .format(_OLD_CONFIG_DIR, new_path, unicode(ex))
                QMessageBox.warning(None, 'Failed to move configs', text)

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
