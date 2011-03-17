"""
monkeycore --- Get instances of core classes, initialize and terminate the system
=================================================================================


Module initializes system at startup, terminates it, when mksv3 closed,
and used for get core instances, such as main window, workspace, etc.

"""

"""TODO
import sys
from datetime import datetime
"""
#from PyQt4.QtCore import 
"""TODO
from PyQt4.QtGui import *

import main
"""
import os.path
import shutil

from PyQt4.QtCore import Qt
from PyQt4.QtGui import qApp

from PyQt4.fresh import pSettings

from _3rdparty.configobj import ConfigObj, flatten_errors, ParseError
from _3rdparty.validate import Validator

import mksiconsresource

DATA_FILES_PATH = os.path.dirname(__file__)
_DEFAULT_CONFIG_PATH = os.path.join(DATA_FILES_PATH, 'config/mksv3.default.cfg')
_DEFAULT_CONFIG_SPEC_PATH = os.path.join(DATA_FILES_PATH, 'config/mksv3.spec.cfg')
_CONFIG_PATH = os.path.expanduser('~/.mksv3.cfg')


class Core:
    """Core object initializes system at startup and terminates at close.
    It create instances of other core modules and holds references to it
    """
    def init(self):
        """Initialize core.
        Called only by main()
        """
        # FIXME find good parameters and good place for this code
        pSettings.setDefaultProperties(pSettings.Properties(qApp.applicationName(), \
                                                            "1.0.0",
                                                            pSettings.Normal))
        
        
        # init main window
        #TODO _showMessage( splash, splash.tr( "Initializing Main Window..." ) )
        
        self._mainWindow = mks.mainwindow.MainWindow()
        self._config = None
        self.config()   # create the instance
        self._workspace = mks.workspace.Workspace(self._mainWindow)
        self._mainWindow.setWorkspace(self._workspace)
    
        self._workspace.setTextEditorClass(mks.editor.Editor) 
        # Create editor tool bar
        self._mainWindow.statusBar().addPermanentWidget(mks.editortoolbar.EditorToolBar(self._mainWindow.statusBar()))
        
        # Create searchreplacce and filebrowser plugins
        self._searchreplace = mks.searchandreplace.SearchAndReplace()
        self._fileBrowser = mks.filebrowser.FileBrowser()

    def __term__(self):
        """Terminate plugins and core modules
        """
        del self._searchreplace
        del self._fileBrowser
        mksiconsresource.qCleanupResources()

    def mainWindow(self):
        """Get :class:`mks.mainwindow.MainWindow` instance 
        
        Instance created, if not exists yet
        """
        return self._mainWindow

    def menuBar(self):
        """Get main window menu bar.
        
        Instance created, if not exists yet
        """
        return self._mainWindow.menuBar()

    def workspace(self):
        """Get :class:`mks.workspace.Workspace` instance
        
        Instance created, if not exists yet
        """
        return self._workspace

    def config(self):
        """ConfigObj istance used for read and write settings
        ConfigObj is cool config file reader and writer. Home page and documentation:
            http://www.voidspace.org.uk/python/configobj.html
        """
        if self._config is None:
            # Create config file in the users home
            failed = False
            if not os.path.exists(_CONFIG_PATH):
                try:
                    shutil.copyfile(_DEFAULT_CONFIG_PATH, _CONFIG_PATH)
                except IOError, ex:
                    messageManager().appendMessage('Failed to create configuration file. Error' + 
                                                    unicode(str(ex), 'utf_8') + 
                                                    '\nUsing default configuration')
                    failed = True
            
            # Open config file
            if not failed:
                try:
                    self._config = ConfigObj(_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
                except ParseError, ex:
                    messageManager().appendMessage('Failed to parse configuration file ' + 
                                                    _CONFIG_PATH + 
                                                    '\n Error:' + 
                                                    unicode(str(ex), 'utf_8') + 
                                                    '\n Fix the file or delete it.' + 
                                                    '\nUsing default configuration')
                    failed = True
            
            # Validate config file
            def _validateConfig(config):
                message_string = ''
                validator = Validator()
                errors = self._config.validate(validator, preserve_errors=True)
                if errors:
                    for entry in flatten_errors(config, errors):
                        # each entry is a tuple
                        section_list, key, error = entry
                        if key is not None:
                           section_list.append(key)
                        else:
                            section_list.append('[missing section]')
                        section_string = ', '.join(section_list)
                        if error == False:
                            error = 'Missing value or section.'
                        message_string += (section_string + ' = ' + str(error))
                return message_string

            if not failed:
                message_string = _validateConfig(self._config)
                if message_string:
                    messageManager().appendMessage('Invalid configuration file ' + 
                                                    _CONFIG_PATH + 
                                                    '\n Error:' + 
                                                    message_string + 
                                                    '\n Fix the file or delete it.' + 
                                                    '\nUsing default configuration')
                    failed = True
            
            # Open default, if failed to use config in the users home
            if failed:
                self._config = ConfigObj(_DEFAULT_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
                message_string = _validateConfig(self._config)
                if message_string:
                    print message_string
                    assert not message_string  # default config MUST be valid
        
        return self._config

    def _reloadConfig():
        """TMP functions, probably I should invent something better"""
        self._config.reload()

    def _flushConfig():
        """TMP functions, probably I should invent something better"""
        if self._config.filename != _DEFAULT_CONFIG_PATH:
            self._config.write()
    
    def messageManager():
        """pQueuedMessageToolBar used for show popup messages
        """
        return self._mainWindow.queuedMessageToolBar()

core = Core()
import mks.editor  # imports after core created, hack for fix cross-imports problem
import mks.editortoolbar
import mks.searchandreplace
import mks.filebrowser
import mks.mainwindow


"""TODO
def _isXmas():
    return datetime.now().month in (11, 12, 1,)

def _showMessage(splash, message):
    if _isXmas():
        splash.showMessage(message, Qt.AlignRight | Qt.AlignBottom, Qt.red)
    else:
        splash.showMessage(message, Qt.AlignRight | Qt.AlignBottom, Qt.white)
    # FIXME no update without hide/show
    splash.hide()
    splash.show()
"""
"""TODO
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
"""

"""TODO
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
"""

"""TODO
# init shortcuts editor
_showMessage( splash, splash.tr( "Initializing Actions Manager..." ) )
actionsManager().setSettings( settings() )


# init shell and commands
_showMessage( splash, splash.tr( "Initializing Shell..." ) )
interpreter()

# start console manager
_showMessage( splash, splash.tr( "Initializing Console..." ) )
consoleManager()
"""
"""TODO
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
"""

"""TODO
# restore window state
_showMessage( splash, splash.tr( "Restoring Workspace..." ) )
mainWindow().setSettings( settings() )

# restore session
_showMessage( splash, splash.tr( "Restoring Session..." ) )
if  mks.monkeystudio.restoreSessionOnStartup() :
    workspace().fileSessionRestore_triggered()
"""
# show main window
#TODO mainWindow().menu_Docks_aboutToShow()
# moved to main, after opening files    mainWindow().show()

"""TODO
# ready
_showMessage( splash, splash.tr( "%1 v%2 (%3) Ready" ).arg( mks.config.PACKAGE_NAME, mks.config.PACKAGE_VERSION, mks.config.PACKAGE_VERSION_STR ) )

# finish splashscreen
splash.finish( mainWindow() )

# show settings dialog the first time user start program
if  settings().value( "FirstTimeRunning", True ).toBool() :
    # execute settings dialog
    if  UISettings.instance().exec_() :
        settings().setValue( "FirstTimeRunning", False )

# prepare apis
mks.monkeystudio.prepareAPIs()
"""


"""TODO
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
"""

"""
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

