# **********************************************************
# __init__.py - The HTML, Markdown, and reST preview package
# **********************************************************
# The Preview plugin provides an HTML-based rendering of the
# file currently being edited. This file implements the
# Plugin interface; other modules are given below.

import os.path
from PyQt4.QtCore import QObject, Qt, pyqtSlot
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QWidget, QFileDialog, \
    QMessageBox
from PyQt4 import uic

from enki.core.core import core
from enki.core.uisettings import CheckableOption, TextOption

# Import CodeChat if possible; otherwise, indicate it wasn't available.
try:
    import CodeChat
    import CodeChat.LanguageSpecificOptions as LSO
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

        # Clicking on advanced mode label triggers either advanced mode or
        # normal mode.
        self.lbSphinxEnableAdvMode.mousePressEvent = self.on_ToggleSphinxSettingModeClicked

        # Update misc pieces of the GUI that can't be stored in the .ui file.
        self.cmbSphinxOutputExtension.addItem("html")
        self.cmbSphinxOutputExtension.addItem("htm")
        self._updateSphinxSettingMode()

    def on_cbSphinxEnable_stateChanged(self, layout=None):
        """Recursively set everything in the layout argument to enabled/disabled
        based on the state of the Sphinx enable checkbox, including any child
        of ``layout``.
        """
        if isinstance(layout, int):
            # on_cbSphinxEnable_stateChanged is called by cbSphinxEnable.stateChanged,
            # which will pass an unnecessary integer argument. Replace it with
            # the default layout.
            layout = self.loSphinxProject
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.layout():
                self.on_cbSphinxEnable_stateChanged(item.layout())
            # Don't hide the Sphinx enable or Sphinx description text.
            if (item.widget() and
              (item.widget() not in (self.cbSphinxEnable, self.labelSphinxIntro)) ):
                item.widget().setEnabled(self.cbSphinxEnable.isChecked())

    @pyqtSlot()
    def on_pbSphinxProjectPath_clicked(self):
        """Provide a directory chooser for the user to select a project path.
        """
        path = QFileDialog.getExistingDirectory(core.mainWindow(), 'Project path')
        if path:
            self.leSphinxProjectPath.setText(path)
            # Automatically set the builder output path to '_build\\html' under
            # builder root path.
            #
            # .. note::
            #    TODO: Pan: since we (I think) support relative paths, only set this
            #    if the path was absolute (and therefore presumabely wrong). If
            #    it's a relative path such as ``_build\html``, then it's probably
            #    OK without changing. Would you add tests/code for this?
            self.leSphinxOutputPath.setText(os.path.join(path, '_build', 'html'))

    # TODO: Pan: for the output path, how about defaulting to "_build\html" (a relative
    # path), instead of using an absolute path by default?
    @pyqtSlot()
    def on_pbSphinxOutputPath_clicked(self):
        """Proivde a directory chooser for the user to select an output path.
        """
        path = QFileDialog.getExistingDirectory(core.mainWindow(), 'Output path')
        if path:
            self.leSphinxOutputPath.setText(path)

    # The Sphinx executable can be selected by the user. A filter is needed
    # such that non-executable files will not be selected by the user.
    @pyqtSlot()
    def on_pbSphinxExecutable_clicked(self):
        path = QFileDialog.getOpenFileName(self,
                                           "Select Sphinx executable",
                                           # .. note::
                                           #    TODO: Pan: What's the Unix equivalent of sphinx-build.exe? Sphinx-build.py?
                                           #    Would you add code to put that in depending on OS?
                                           filter="sphinx-build.exe;; All Files (*.*)");
        if path:
            self.leSphinxExecutable.setText(path)

    def on_ToggleSphinxSettingModeClicked(self, *args):
        core.config()['Sphinx']['AdvancedMode'] = not core.config()['Sphinx']['AdvancedMode']
        core.config().flush()
        self._updateSphinxSettingMode()

    # Cleanup user input paths by calling os.path.normpath such that path
    # separator is consistent, upper level references can be precalculated,
    # unnecessary dots can be removed.
    def on_leSphinxProjectPath_editingFinished(self):
        self.leSphinxProjectPath.setText(os.path.normpath(self.leSphinxProjectPath.text()))

    def on_leSphinxOutputPath_editingFinished(self):
        self.leSphinxOutputPath.setText(os.path.normpath(self.leSphinxOutputPath.text()))

    def on_leSphinxExecutable_editingFinished(self):
        self.leSphinxExecutable.setText(os.path.normpath(self.leSphinxExecutable.text()))

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
        # config key and Sphinx's default config key.
        if not 'CodeChat' in core.config():
            core.config()['CodeChat'] = {}
            core.config()['CodeChat']['Enabled'] = False
            core.config().flush()
        if not 'Sphinx' in core.config():
            core.config()['Sphinx'] = {}
            core.config()['Sphinx']['Enabled'] = False
            core.config()['Sphinx']['Executable'] = u'sphinx-build'
            core.config()['Sphinx']['ProjectPath'] = u''
            core.config()['Sphinx']['BuildOnSave'] = False
            core.config()['Sphinx']['OutputPath'] = os.path.join('_build', 'html')
            core.config()['Sphinx']['OutputExtension'] = u'html'
            core.config()['Sphinx']['AdvancedMode'] = False
            core.config()['Sphinx']['Cmdline'] = u'sphinx-build -d ' + os.path.join('_build','doctrees')  \
                                                 + ' . ' + os.path.join('_build','html')
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
        if self._canPreview(core.workspace().currentDocument()):
            if not self._dockInstalled:
                self._createDock()
        else:
            if self._dockInstalled:
                self._removeDock()

    def _canPreview(self, document):
        """Check if the given document can be shown in the Preview dock.
        """
        if document is None:
            return False

        if document.qutepart.language() in ('Markdown', 'Restructured Text') or \
           isHtmlFile(document):
            return True

        # CodeChat can preview a file if it's enabled and if that file's
        # extension is supported.
        if ( CodeChat is not None and core.config()['CodeChat']['Enabled'] 
             and document.filePath()):
            lso = LSO.LanguageSpecificOptions()
            fileExtension = os.path.splitext(document.filePath())[1]
            if fileExtension in lso.extension_to_options.keys():
                return True
        # TODO: When to really show the preview dock with Sphinx? That is, how
        # can we tell if Sphinx will produce a .html file based on the currently
        # open file in the editor? Just checking for a .html file doesn't work;
        # perhaps Sphinx hasn't been run or the output files were removed, but
        # a run of Sphinx will generate them. Or perhaps Sphinx won't process
        # this file (it's excluded, wrong extension, etc.)
        if core.config()['Sphinx']['Enabled'] and document.filePath():
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
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "Sphinx/BuildOnSave",
                                            widget.cbBuildOnSaveEnable))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/ProjectPath",
                                       widget.leSphinxProjectPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/OutputPath",
                                       widget.leSphinxOutputPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/OutputExtension",
                                       widget.cmbSphinxOutputExtension.lineEdit()))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/Executable",
                                       widget.leSphinxExecutable))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/Cmdline",
                                       widget.leSphinxCmdline))
        # TODO: Emit a signal from here to the preview class. Force preview
        # window to refresh on setting change.
