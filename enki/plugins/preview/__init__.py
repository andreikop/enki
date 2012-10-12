"""
preview --- HTML, Markdown preview
==================================
"""

from PyQt4.QtCore import QObject, Qt

from enki.core.core import core


def _isRestFile(document):
    """Check if document is a ReST file
    Currently, there are no highlighting language for ReST
    """
    return document is not None and \
           document.fileName() is not None and \
           document.fileName().endswith('.rst')


class Plugin(QObject):
    """Plugin interface implementation
    """
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        self._dock = None
        self._dockInstalled = False
        self._wasVisible = None
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().languageChanged.connect(self._onDocumentChanged)

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
        
        if document.language() is not None and \
           document.language() in ('HTML', 'Markdown'):
            return True
        
        if _isRestFile(document):
            return True
        
        return False

    def _createDock(self):
        """Install dock
        """
        # create dock
        if self._dock is None:
            from enki.plugins.preview.preview import PreviewDock
            self._dock = PreviewDock()
        # add dock to dock toolbar entry
        core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)
        core.actionManager().addAction("mView/aPreview", self._dock.showAction())
        self._dockInstalled = True
        if self._wasVisible is not None and self._wasVisible:
            self._dock.show()
    
    def _removeDock(self):
        """Remove dock from GUI
        """
        self._wasVisible = self._dock.isVisible()
        core.actionManager().removeAction("mView/aPreview")
        core.mainWindow().removeDockWidget(self._dock)
        self._dockInstalled = False
    
    def del_(self):
        """Uninstall the plugin
        """
        if self._dockInstalled:
            self._removeDock()
        
        if self._dock is not None:
            self._dock.del_()
