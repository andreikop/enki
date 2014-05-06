# **********************************************************
# __init__.py - The HTML, Markdown, and reST preview package
# **********************************************************
# The Preview plugin provides an HTML-based rendering of the
# file currently being edited. This file implements the
# Plugin interface; other modules are given below.
#
# .. toctree::
#   :maxdepth: 2
#
#   preview.py
#   ApproxMatch.py

import os.path
from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QWidget
from PyQt4 import uic

from enki.core.core import core
from enki.core.uisettings import CheckableOption

try:
    import CodeChat
except ImportError:
    CodeChat = None

def isHtmlFile(document):
    return document is not None and  \
           document.qutepart.language() is not None and \
           'html' in document.qutepart.language().lower()  # 'Django HTML Template'

class SettingsWidget(QWidget):
    """Insert preview plugin as a page to UISetting
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        if CodeChat is None:
            self.cbEnable.setEnabled(False)
            self.cbEnable.setChecked(False)
            return
        else:
            self.cbEnable.clicked.connect(self._oncbEnableCodeChatClicked)
            self.cbEnable.setChecked(core.config()['CodeChat']['Enabled'])

    def _oncbEnableCodeChatClicked(self):
        if self.cbEnable.isChecked():
            core.config()['CodeChat']['Enabled'] = True
        else:
            core.config()['CodeChat']['Enabled'] = False
        core.config().flush()


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

        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)
        # Toggle preview dock when codechat enable checkbox toggles
        core.uiSettingsManager().dialogAccepted.connect(self._onDocumentChanged)

        # If user's config .json file is older then populate the new codechat
        # default config key.
        if not 'CodeChat' in core.config():
            core.config()['CodeChat'] = {}
            core.config()['CodeChat']['Enabled'] = False
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
            self._saveAction.triggered.connect(self._dock.onSave)

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
        """UI settings dialogue is about to execute.
        Add own options
        """
        widget = SettingsWidget(dialog)

        dialog.appendPage(u"CodeChat", widget)

        # Options
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "CodeChat/Enabled",
                                            widget.cbEnable))
