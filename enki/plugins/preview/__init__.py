# **********************************************************
# __init__.py - The HTML, Markdown, and reST preview package
# **********************************************************
# The Preview plugin provides an HTML-based rendering of the
# file currently being edited. This file implements the
# Plugin interface; other modules are given below.

import os.path
from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QWidget, QFileDialog
from PyQt4 import uic

from enki.core.core import core
from enki.core.uisettings import CheckableOption, TextOption

try:
    import CodeChat
except ImportError:
    CodeChat = None

try:
    import sphinx
except ImportError:
    sphinx = None

def isHtmlFile(document):
    return document is not None and  \
           document.qutepart.language() is not None and \
           'html' in document.qutepart.language().lower()  and \
           (not 'php' in document.qutepart.language().lower())  # Django HTML template but not HTML (PHP)

class SettingsWidget(QWidget):
    """Insert the preview plugin as a page of the UISettings dialog.
    """
    def __init__(self, *args):
        # Initialize the dialog, loading in Literate programming setting GUI.
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

        if sphinx is None:
            # If the sphinx module can't be loaded, then disable the
            # associated checkboxes, path selection line edits and output
            # extension line edits.
            self.cbSphinxEnable.setChecked(False)
            self.cbSphinxEnable.setEnabled(False)
            self.leSphinxProjectPath.setEnabled(False)
            self.pbSphinxProjectPath.setEnabled(False)
            self.leSphinxOutputPath.setEnabled(False)
            self.pbSphinxOutputPath.setEnabled(False)
            self.leSphinxOutputExtension.setEnabled(False)
            # disable build on save checkbox
            self.cbBuildOnSaveEnable.setEnabled(False)
            # show the "not installed" message
            self.labelSphinxNotInstalled.setVisible(True)
        else:
            # If sphinx is available, then set all path selection buttons to
            # work, along with build on save pushbutton.
            self.pbSphinxProjectPath.clicked.connect(self._onPbSphinxProjectPathClicked)
            self.pbSphinxOutputPath.clicked.connect(self._onPbSphinxOutputPathClicked)
            # set default output format to html
            self.leSphinxOutputExtension.setText('html')
            # Use sphinx if sphinx installed
            self.cbSphinxEnable.setChecked(True)
            # disable build only on save function
            self.cbBuildOnSaveEnable.setChecked(False)
            # Hide the "not installed" message.
            self.labelSphinxNotInstalled.setVisible(False)

    def _onPbSphinxProjectPathClicked(self):
        path = QFileDialog.getExistingDirectory(core.mainWindow(), 'Project path')
        if path:
            self.leSphinxProjectPath.setText(path)

    def _onPbSphinxOutputPathClicked(self):
        path = QFileDialog.getExistingDirectory(core.mainWindow(), 'Output path')
        if path:
            self.leSphinxOutputPath.setText(path)

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
        if not 'sphinx' in core.config():
        # TODO: if user updates from an old Enki version, certain entries might
        # not be available, while core.config()['sphinx'] is available, causing
        # the newly added settings fail to get initialized correctly.
            core.config()['sphinx'] = {}
            core.config()['sphinx']['Enabled'] = False
            core.config()['sphinx']['ProjectPath'] = u''
            core.config()['sphinx']['BuildOnSave'] = False
            core.config()['sphinx']['OutputPath'] = u''
            core.config()['sphinx']['OutputExtension'] = u'html'
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
        if CodeChat is not None and core.config()['CodeChat']['Enabled'] is True:
            return True
        # Sphinx does not depend on codechat
        if sphinx is not None and core.config()['sphinx']['Enabled'] is True:
            return True

        # TODO: Only if using an HTML builder should this be true; otherwise, false.
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
                                            "sphinx/Enabled",
                                            widget.cbSphinxEnable))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "sphinx/ProjectPath",
                                       widget.leSphinxProjectPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "sphinx/OutputPath",
                                       widget.leSphinxOutputPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "sphinx/OutputExtension",
                                       widget.leSphinxOutputExtension))
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "sphinx/BuildOnSave",
                                            widget.cbBuildOnSaveEnable))
