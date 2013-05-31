"""
preview --- HTML, Markdown preview
==================================
"""

from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QAction, QIcon, QKeySequence

from enki.core.core import core


def isMarkdownFile(document):
    """Check if document is a ReST file
    Currently, there are no highlighting language for ReST
    """
    return document is not None and \
           document.fileName() is not None and \
           (document.fileName().endswith('.md') or \
            document.fileName().endswith('.markdown'))

def isHtmlFile(document):
    return document is not None and  \
           document.qutepart.language() is not None and \
           'html' in document.qutepart.language().lower()  # 'Django HTML Template'    

class Plugin(QObject):
    """Plugin interface implementation
    """
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        
        if not 'Preview' in core.config():  # migration from old configs versions
            core.config()['Preview'] = {'Enabled': True,
                                        'JavaScriptEnabled' : True}

        self._dock = None
        self._saveAction = None
        self._dockInstalled = False
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().languageChanged.connect(self._onDocumentChanged)
        core.mainWindow().stateRestored.connect(self._onMainWindowStateRestored)
    
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
    
    def _onMainWindowStateRestored(self):
        """When main window state is restored - dock is made visible, even if should not. Qt bug?
        Hide dock, if can't view current document
        """
        if (not self._canHighlight(core.workspace().currentDocument())) and \
           self._dock is not None:
               self._dock.hide()
    
    def _canHighlight(self, document):
        """Check if can highlight document
        """
        if document is None:
            return False
        
        if document.qutepart.language() == 'reStructuredText' or \
           isHtmlFile(document):
            return True
        
        if isMarkdownFile(document):
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
            self._dock.showAction().triggered.connect(self._onDockShown)
            self._saveAction = QAction(QIcon(':enkiicons/save.png'), 'Save Preview as HTML', self._dock)
            self._saveAction.setShortcut(QKeySequence("Alt+Ctrl+P"))
            self._saveAction.triggered.connect(self._dock.onSave)
        
        # add dock to dock toolbar entry
        core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)
        core.actionManager().addAction("mView/aPreview", self._dock.showAction())
        core.actionManager().addAction("mFile/aSavePreview", self._saveAction)
        self._dockInstalled = True
        if core.config()['Preview']['Enabled']:
            self._dock.show()
    
    def _onDockClosed(self):
        """Dock has been closed by user. Change Enabled option
        """
        core.config()['Preview']['Enabled'] = False
        core.config().flush()
    
    def _onDockShown(self):
        """Dock has been shown by user. Change Enabled option
        """
        core.config()['Preview']['Enabled'] = True
        core.config().flush()
    
    def _removeDock(self):
        """Remove dock from GUI
        """
        core.actionManager().removeAction("mView/aPreview")
        core.actionManager().removeAction("mFile/aSavePreview")
        core.mainWindow().removeDockWidget(self._dock)
        self._dockInstalled = False
