"""
repl --- MIT Scheme and SML REPL
================================

File contains integration with the core
"""

from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QIcon

from enki.core.core import core
from enki.core.uisettings import ChoiseOption, TextOption

class _AbstractReplPlugin(QObject):
    """Base class for language-specific REPL sub-plugins
    """
    _LANGUAGE = None
    _FULL_NAME = None
    _MENU_PATH = None
    _DOCK_TITLE = None
    
    def __init__(self):
        QObject.__init__(self)
        
        self._installed = False
        self._evalAction = None
        self._activeInterpreterPath = None

        # TODO handle situation, when lexer changed for current document
        core.workspace().documentOpened.connect(self._installOrUninstallIfNecessary)
        core.workspace().documentClosed.connect(self._installOrUninstallIfNecessary)
        core.workspace().currentDocumentChanged.connect(self._installOrUninstallIfNecessary)
        core.workspace().currentDocumentChanged.connect(self._updateEvalActionEnabledState)
        core.workspace().languageChanged.connect(self._installOrUninstallIfNecessary)
        core.workspace().languageChanged.connect(self._updateEvalActionEnabledState)
        core.uiSettingsManager().dialogAccepted.connect(self._applySettings)
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)
        
        self._installOrUninstallIfNecessary()

    def _icon(self):
        """Settings widget icon
        """
        raise NotImplementedError()

    def _createInterpreter(self):
        """Create interpreter instance
        """
        raise NotImplementedError()

    def __del__(self):
        self.del_()
    
    def del_(self):
        """Terminate the plugin. Method called by core, when closing Enki, and sometimes by plugin itself
        """
        if not self._installed:
            return
        self._interpreter.stop()
        core.actionManager().removeAction(self._evalAction)
        self._evalAction = None
        core.actionManager().removeAction(self._breakAction)
        self._breakAction = None
        core.actionManager().removeMenu(self._MENU_PATH)
        core.mainWindow().removeDockWidget(self._dock)
        self._dock.del_()
        del self._dock
        self._installed = False

    def _isSupportedFile(self, document):
        """Check if document is highlighted as Scheme
        """
        return document is not None and \
               document.qutepart.language() == self._LANGUAGE

    def _applySettings(self):
        """Apply settings. Called by configurator class
        """
        # if path has been changed - restart the interpreter
        if self._installed and \
           self._activeInterpreterPath != self._settingsGroup()["InterpreterPath"]:
            self.del_()
        
        self._installOrUninstallIfNecessary()
    
    def _supportedDocumentIsOpened(self):
        """Check if at least one Scheme document is opened
        """
        schemeDocs = filter(self._isSupportedFile, core.workspace().documents())
        return len(schemeDocs) > 0

    def _updateEvalActionEnabledState(self):
        """Update action enabled state
        """
        if self._evalAction is None:
            return

        currDoc = core.workspace().currentDocument()
        self._evalAction.setEnabled(currDoc is not None and self._isSupportedFile(currDoc))

    def _settingsGroup(self):
        """Get own settings group
        """
        return core.config().get("Modes/%s" % self._LANGUAGE)

    def _installOrUninstallIfNecessary(self):
        """Install or uninstall according to settings and availability of opened Scheme files
        """
        enabled = self._settingsGroup()["Enabled"]
        if enabled == 'always':
            if not self._installed:
                self._install()
        elif enabled == 'never':
            if self._installed:
                self.del_()
        else:
            assert enabled == 'whenOpened'
            if self._supportedDocumentIsOpened():
                self._install()
            else:
                self.del_()

    def _onEvalTriggered(self):
        """Eval action triggered. Evaluate file or expression
        """
        document = core.workspace().currentDocument()
        if document is None:
            return
        
        selection = document.qutepart.selectedText
        if selection:
            self._interpreter.execCommand(selection)
            self._dock.show()
        else:
            if document.isModified():
                document.saveFile()
            if document.filePath():  # user may cancel saving document
                self._interpreter.loadFile(document.filePath())
                self._dock.show()
    
    def _onBreakTriggered(self):
        """Break has been triggered. Stop the interpreter
        """
        self._interpreter.stop()

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        from repl import SettingsWidget
        widget = SettingsWidget(dialog)

        dialog.appendPage(u"Modes/%s" % self._FULL_NAME, widget, self._icon())

        # Options
        dialog.appendOption(ChoiseOption(dialog, core.config(), "Modes/%s/Enabled" % self._LANGUAGE,
                                       {widget.rbWhenOpened: "whenOpened",
                                        widget.rbNever: "never",
                                        widget.rbAlways: "always"}))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Modes/%s/InterpreterPath" % self._LANGUAGE, widget.leInterpreterPath))

    def _install(self):
        """Install the plugin to the core
        """
        if self._installed:
            return

        self._schemeMenu = core.actionManager().addMenu(self._MENU_PATH, self._FULL_NAME)
        self._evalAction = core.actionManager().addAction("%s/aEval" % self._MENU_PATH,
                                                          "Eval. selection/Save and eval.")
        self._evalAction.setStatusTip("Evaluate selection. If nothing is selected - save and evaluate whole file")
        self._evalAction.setShortcut("Ctrl+E")
        self._evalAction.triggered.connect(self._onEvalTriggered)
        self._breakAction = core.actionManager().addAction("%s/aBreak" % self._MENU_PATH, "Stop the interpreter")
        self._breakAction.setStatusTip("Use it as a restart action.")
        self._breakAction.setShortcut("Pause")
        self._breakAction.triggered.connect(self._onBreakTriggered)
        self._breakAction.setEnabled(False)

        self._activeInterpreterPath = self._settingsGroup()["InterpreterPath"]
        
        self._interpreter = self._createInterpreter()
        
        self._interpreter.processIsRunningChanged.connect(lambda isRunning: self._breakAction.setEnabled(isRunning))
        
        from repl import ReplDock
        self._dock = ReplDock(self._interpreter.widget(), self._LANGUAGE, self._DOCK_TITLE, self._icon())

        core.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self._dock)
        self._dock.hide()

        self._installed = True


class _SchemeReplPlugin(_AbstractReplPlugin):
    """Scheme REPL plugin
    """
    instance = None

    _LANGUAGE = "Scheme"
    _FULL_NAME = "MIT Scheme"
    _MENU_PATH = "mScheme"
    _DOCK_TITLE = "&MIT Scheme"
    
    def _icon(self):
        """Settings widget icon
        """
        return QIcon(':/enkiicons/languages/scheme.png')

    def _createInterpreter(self):
        """Create interpreter instance
        """
        from repl import MitSchemeInterpreter
        return MitSchemeInterpreter(self._LANGUAGE, self._FULL_NAME, self._activeInterpreterPath)


class _SmlReplPlugin(_AbstractReplPlugin):
    """Standard ML REPL sub-plugin
    """
    instance = None

    _LANGUAGE = "SML"
    _FULL_NAME = "Standard ML"
    _MENU_PATH = "mSml"
    _DOCK_TITLE = "Standard &ML"

    def __init__(self):
        if not 'SML' in core.config()['Modes']: # if config file is old, add own settings
            core.config()['Modes']['SML'] = {'Enabled': 'whenOpened', 'InterpreterPath': 'sml'}
        
        _AbstractReplPlugin.__init__(self)

    def _icon(self):
        """Settings widget icon
        """
        return QIcon()

    def _createInterpreter(self):
        """Create interpreter instance
        """
        from repl import SmlInterpreter
        return SmlInterpreter(self._LANGUAGE, self._FULL_NAME, self._activeInterpreterPath)


class Plugin:
    """Module implementation
    """
    def __init__(self):
        self._schemeSubPlugin = _SchemeReplPlugin()
        self._smlSubPlugin = _SmlReplPlugin()

    def del_(self):
        self._schemeSubPlugin.del_()
        self._smlSubPlugin.del_()

