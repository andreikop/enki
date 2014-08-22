# **********************************************************
# __init__.py - The HTML, Markdown, and reST preview package
# **********************************************************
# The Preview plugin provides an HTML-based rendering of the
# file currently being edited. This file implements the
# Plugin interface; other modules are given below.

import os.path
import shutil
from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QWidget, QFileDialog, QMessageBox
from PyQt4 import uic

from enki.core.core import core
from enki.core.uisettings import CheckableOption, TextOption

# Import CodeChat if possible; otherwise, indicate it wasn't available.
try:
    import CodeChat
except ImportError:
    CodeChat = None

def isHtmlFile(document):
    return document is not None and  \
           document.qutepart.language() is not None and \
           'html' in document.qutepart.language().lower()  and \
           (not 'php' in document.qutepart.language().lower())  # Django HTML template but not HTML (PHP)

class SettingsWidget(QWidget):
    """Insert the preview plugin as a page of the UISettings dialog.
    """
    def __init__(self, *args):
        # Initialize the dialog, loading in the literate programming settings GUI.
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)

        if CodeChat is None:
            # If the CodeChat module can't be loaded, then disable the
            # associated checkbox and show the "not installed" message.
            self.cbCodeChatEnable.setEnabled(False)
            self.labelCodeChatNotInstalled.setVisible(True)
        else:
            # Hide the "not installed" message.
            self.labelCodeChatNotInstalled.setVisible(False)

        # When the Sphinx enable checkbox is toggled, enable/disable all Sphinx
        # UI elements.
        self.cbSphinxEnable.stateChanged.connect(self._toggleSphinx)
        # Provide file choosers for the Sphinx UI.
        self.pbSphinxProjectPath.clicked.connect(self._onPbSphinxProjectPathClicked)
        # Pan: for the output path, how about defaulting to "_build\html" (a relative
        # path), instead of using an absolute path by default?
        self.pbSphinxOutputPath.clicked.connect(self._onPbSphinxOutputPathClicked)
        # The Sphinx executable can be selected by the user. A filter is needed
        # such that non-executable files will not be selected by the user.
        self.pbSphinxExecutable.clicked.connect(self._onPbSphinxExecutableClicked)

        # Clicking on advanced mode label triggers either advanced mode or
        # normal mode.
        self.lbSphinxEnableAdvMode.mousePressEvent = self._onToggleSphinxSettingModeClicked

        # Changes to the project path will check that the new path has the
        # necessary project files.
        self.leSphinxProjectPath.textEdited.connect(
          lambda text : self._copySphinxProjectTemplate())

        # Update misc pieces of the GUI that can't be stored in the .ui file.
        self.cmbSphinxOutputExtension.addItem("html")
        self.cmbSphinxOutputExtension.addItem("htm")
        self._updateSphinxSettingMode()

    def _toggleSphinx(self, layout=None):
        """Recursively set everything in the layout argument to enabled/disabled
        based on the state of the Sphinx enable checkbox, including any children
        of ``layout``.
        """
        if layout.__class__ is int:
            # _toggleSphinx is called by cbSphinxEnable.stateChanged, which will
            # pass an unnecessary integer argument. Replaced it with
            # the default layout.
            layout = self.loSphinxProject
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.layout():
                self._toggleSphinx(item.layout())
            # Don't hide the Sphinx enable or Sphinx description text.
            if (item.widget() and
              (item.widget() not in (self.cbSphinxEnable, self.labelSphinxIntro)) ):
                item.widget().setEnabled(self.cbSphinxEnable.isChecked())

    def _onPbSphinxProjectPathClicked(self):
        """Provide a directory chooser for the user to select a project path.
        """
        path = QFileDialog.getExistingDirectory(core.mainWindow(), 'Project path')
        if path:
            self.leSphinxProjectPath.setText(path)
            # Automatically set the builder output path to '_build\\html' under
            # builder root path
            self.leSphinxOutputPath.setText(os.path.join(path, '_build\\html'))

    def _onPbSphinxOutputPathClicked(self):
        """Proivde a directory chooser for the user to select an output path.
        """
        path = QFileDialog.getExistingDirectory(core.mainWindow(), 'Output path')
        if path:
            self.leSphinxOutputPath.setText(path)

    def _onPbSphinxExecutableClicked(self):
        path = QFileDialog.getOpenFileName(self,
                                           "Select Sphinx executable",
                                           filter="sphinx-build.exe;; All Files (*.*)");
        if path:
            self.leSphinxExecutable.setText(path)

    def _onToggleSphinxSettingModeClicked(self, *args):
        core.config()['Sphinx']['AdvancedMode'] = not core.config()['Sphinx']['AdvancedMode']
        core.config().flush()
        self._updateSphinxSettingMode()


    def _updateSphinxSettingMode(self):
        """Update the Sphinx settings mode by hiding/revealing the appropriate
        controls.
        """
        if core.config()['Sphinx']['AdvancedMode']:
            # Switch to advanced setting mode:
            # hide all path setting line edit boxes and buttons.
            for i in range(self.gridLayout.count()):
                self.gridLayout.itemAt(i).widget().setVisible(False)
            # Enable advanced setting mode items
            self.lbSphinxEnableAdvMode.setText('<html><head/><body><p>' +
            '<span style="text-decoration: underline; color:#0000ff;">Switch to Normal Mode' +
            '</span></p></body></html>')
            self.lbSphinxCmdline.setVisible(True)
            self.leSphinxCmdline.setVisible(True)
            self.lbSphinxReference.setVisible(True)
        else:
            # Reenable all path setting line edit boxes and buttons
            for i in range(self.gridLayout.count()):
                self.gridLayout.itemAt(i).widget().setVisible(True)
            # Hide all advanced mode entries.
            self.lbSphinxEnableAdvMode.setText('<html><head/><body><p>' +
              '<span style="text-decoration: underline; color:#0000ff;">Switch to Advanced Mode' +
              '</span></p></body></html>')
            self.lbSphinxCmdline.setVisible(False)
            self.leSphinxCmdline.setVisible(False)
            self.lbSphinxReference.setVisible(False)

# Pan: Let's put this code in preview.py, in scheduleDocumentProcessing -- have
# it pop us a dialog box saying something like "missing files needed for Sphinx,
# copy now?"
def copySphinxProjectTemplate():
    """If Sphinx directory is valid and Sphinx is enabled, then add conf.py
       and default.css to the project directory."""
    if (core.config()['Sphinx']['Enabled'] and
      os.path.exists(core.config()['Sphinx']['ProjectPath'])):
        # Check whether conf.py or default.css already exist; if so,
        # they do not need to be copied.
        if (os.path.exists(os.path.join(core.config()['Sphinx']['ProjectPath'], 'conf.py')) or
          os.path.exists(os.path.join(core.config()['Sphinx']['ProjectPath'], 'default.css'))):
            return

        # Copy template files to sphinx project directory.
        codeChatPath = os.path.dirname(os.path.realpath(CodeChat.__file__))
        cssPath = os.path.join(codeChatPath, 'template/default.css')
        shutil.copy(cssPath, core.config()['Sphinx']['ProjectPath'])
        # Choose what conf.py file to copy based whether CodeChat is enabled.
        if core.config()['CodeChat']['Enabled']:
            # If CodeChat is also enabled, enable this in conf.py too.
            confCodeChatPath = os.path.join(codeChatPath, 'template/conf_codechat.py')
            shutil.copy(confCodeChatPath, os.path.join(core.config()['Sphinx']['ProjectPath'], 'conf.py'))
        else:
            # else simple copy the default conf.py to sphinx target directory
            confPath = os.path.join(codeChatPath, 'template/conf.py')
            shutil.copy(confPath, core.config()['Sphinx']['ProjectPath'])

class Plugin(QObject):
    """Plugin interface implementation
    """
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)

        self._dock = None
        self._saveAction = None
        self._dockInstalled = False
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().languageChanged.connect(self._onDocumentChanged)

        # Install our CodeChat page into the settings dialog.
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)
        # Update preview dock when the settings dialog (which contains the CodeChat
        # enable checkbox) is changed.
        core.uiSettingsManager().dialogAccepted.connect(self._onDocumentChanged)

        # If user's config .json file lacks it, populate CodeChat's default
        # config key and sphinx' default config key.
        if not 'CodeChat' in core.config():
            core.config()['CodeChat'] = {}
            core.config()['CodeChat']['Enabled'] = False
            core.config().flush()
        if not 'Sphinx' in core.config():
            core.config()['Sphinx'] = {}
            core.config()['Sphinx']['Enabled'] = False
            core.config()['Sphinx']['Executable'] = u''
            core.config()['Sphinx']['ProjectPath'] = u''
            core.config()['Sphinx']['BuildOnSave'] = False
            core.config()['Sphinx']['OutputPath'] = u''
            core.config()['Sphinx']['OutputExtension'] = u''
            core.config()['Sphinx']['AdvancedMode'] = False
            core.config()['Sphinx']['Cmdline'] = u''
            core.config().flush()

    def del_(self):
        """Uninstall the plugin
        """
        if self._dockInstalled:
            self._removeDock()

        if self._dock is not None:
            self._dock.del_()

    def _onDocumentChanged(self):
        """Document or Language changed.
        Create dock, if necessary
        """
        if self._canHighlight(core.workspace().currentDocument()):
            if not self._dockInstalled:
                self._createDock()
        else:
            if self._dockInstalled:
                self._removeDock()

    def _canHighlight(self, document):
        """Check if can highlight document
        """
        if document is None:
            return False

        if document.qutepart.language() in ('Markdown', 'Restructured Text') or \
           isHtmlFile(document):
            return True
        # TODO: Check to see if CodeChat supports the language inferred from the
        # file extension; if so, return true.
        if CodeChat is not None and core.config()['CodeChat']['Enabled'] is True:
            return True
        # TODO: When to really show the preview dock with Sphinx? That is, how
        # can we tell if Sphinx will produce a .html file based on the currently
        # open file in the editor? Just checking for a .html file doesn't work;
        # perhaps Sphinx hasn't been run or the output files were removed, but
        # a run of Sphinx will generate them. Or perhaps Sphinx won't process
        # this file (it's excluded, wrong extension, etc.)
        if core.config()['Sphinx']['Enabled'] is True:
            return True

        return False

    def _createDock(self):
        """Install dock
        """
        # create dock
        if self._dock is None:
            from enki.plugins.preview.preview import PreviewDock
            self._dock = PreviewDock()
            self._dock.closed.connect(self._onDockClosed)
            self._dock.shown.connect(self._onDockShown)
            self._saveAction = QAction(QIcon(':enkiicons/save.png'), 'Save Preview as HTML', self._dock)
            self._saveAction.setShortcut(QKeySequence("Alt+Shift+P"))
            self._saveAction.triggered.connect(self._dock.onPreviewSave)

        core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)

        core.actionManager().addAction("mView/aPreview", self._dock.showAction())
        core.actionManager().addAction("mFile/aSavePreview", self._saveAction)
        self._dockInstalled = True
        if core.config()['Preview']['Enabled']:
            self._dock.show()

    def _onDockClosed(self):
        """Dock has been closed by user. Change Enabled option
        """
        if core.config()['Preview']['Enabled']:
            core.config()['Preview']['Enabled'] = False
            core.config().flush()

    def _onDockShown(self):
        """Dock has been shown by user. Change Enabled option
        """
        if not core.config()['Preview']['Enabled']:
            core.config()['Preview']['Enabled'] = True
            core.config().flush()

    def _removeDock(self):
        """Remove dock from GUI
        """
        core.actionManager().removeAction("mView/aPreview")
        core.actionManager().removeAction("mFile/aSavePreview")
        core.mainWindow().removeDockWidget(self._dock)
        self._dockInstalled = False

    def _onSettingsDialogAboutToExecute(self, dialog):
        """The UI settings dialog is about to execute. Install CodeChat-related
           settings."""
        # First, append the CodeChat settings page to the settings dialog.
        widget = SettingsWidget(dialog)
        dialog.appendPage(u"CodeChat", widget)
        # Next, have the setting UI auto-update the corresponding CodeChat and
        # config entries.
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "CodeChat/Enabled",
                                            widget.cbCodeChatEnable))
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "Sphinx/Enabled",
                                            widget.cbSphinxEnable))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/ProjectPath",
                                       widget.leSphinxProjectPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/OutputPath",
                                       widget.leSphinxOutputPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/OutputExtension",
                                       widget.cmbSphinxOutputExtension.lineEdit()))
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "Sphinx/BuildOnSave",
                                            widget.cbBuildOnSaveEnable))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/Executable",
                                       widget.leSphinxExecutable))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/Cmdline",
                                       widget.leSphinxCmdline))
        # Ensure the Sphinx project has the necessary templates.
        copySphinxProjectTemplate()
