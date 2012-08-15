"""
preview --- HTML, Markdown preview
==================================
"""

from PyQt4.QtCore import pyqtSignal, QObject, QSize, Qt, QThread, QUrl
from PyQt4.QtGui import QIcon

from enki.core.core import core

from enki.widgets.dockwidget import DockWidget

from threading import Lock

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
        return document is not None and \
           document.language() is not None and \
           document.language() in ('HTML', 'Markdown')

    def _createDock(self):
        """Install dock
        """
        # create dock
        if self._dock is None:
            self._dock = PreviewDock(core.mainWindow())
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

class ConverterThread(QThread):
    """Thread converts markdown to HTML
    """
    htmlReady = pyqtSignal(unicode, unicode)
    
    def __init__(self):
        QThread.__init__(self)
        self._lock = Lock()
    
    def process(self, filePath, language, text):
        """Convert data and emit result
        """
        with self._lock:
            self._filePath = filePath
            self._haveData = True
            self._language = language
            self._text = text
            if not self.isRunning():
                self.start(QThread.LowPriority)
    
    def _getHtml(self, language, text):
        """Get HTML for document
        """
        if language == 'HTML':
            return text
        elif language == 'Markdown':
            return self._convertMarkdown(text)
        else:
            return 'No preview for this type of file'

    def _convertMarkdown(self, text):
        """Convert Markdown to HTML
        """
        try:
            import markdown
        except ImportError:
            return "Markdown preview requires <i>python-markdown</i> package<br/>" \
                   "Install it with your package manager or see " \
                   "<a href=http://packages.python.org/Markdown/install.html>installation instructions</a>"
        
        try: import mdx_mathjax
        except: pass  #mathjax doesn't require import statement if installed as extension
        try:
            return markdown.markdown(text, ['fenced_code', 'nl2br', 'mathjax'])
        except:
            return markdown.markdown(text, ['fenced_code', 'nl2br']) #keep going without mathjax

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            with self._lock:
                filePath = self._filePath
                language = self._language
                text = self._text
                self._haveData = False
            
            html = self._getHtml(self._language, self._text)
            
            with self._lock:
                if not self._haveData:
                    self.htmlReady.emit(filePath, html)
                    break
                # else - next iteration


class PreviewDock(DockWidget):
    """GUI and implementation
    """
    def __init__(self, *args):
        DockWidget.__init__(self, *args)

        self.setObjectName("PreviewDock")
        self.setWindowTitle(self.tr( "&Preview" ))
        self.setWindowIcon(QIcon(':/enkiicons/internet.png'))
        self.showAction().setShortcut("Alt+P")

        from PyQt4.QtWebKit import QWebView  # delayed import, startup performance optimization
        self._view = QWebView(self)
        self._view.page().mainFrame().titleChanged.connect(self._updateTitle)
        self.setWidget(self._view)
        self.setFocusProxy(self._view)
        
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)
        
        self._scrollPos = {}
        self._vAtEnd = {}
        self._hAtEnd = {}
        
        self._thread = ConverterThread()
        self._thread.htmlReady.connect(self._setHtml)

        self._visiblePath = None
        self._onDocumentChanged(None, core.workspace().currentDocument())

    def del_(self):
        """Uninstall themselves
        """
        self._thread.wait()
    
    def _updateTitle(self, pageTitle):
        """Web page title changed. Update own title
        """
        if pageTitle:
            self.setWindowTitle("&Preview - " + pageTitle)
        else:
            self.setWindowTitle("&Preview")
    
    def _saveScrollPos(self):
        """Save scroll bar position for document
        """
        frame = self._view.page().mainFrame()
        if frame.contentsSize() == QSize(0, 0):
            return # no valida data, nothing to save
        
        pos = frame.scrollPosition()
        self._scrollPos[self._visiblePath] = pos
        self._hAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Horizontal) == pos.x()
        self._vAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Vertical) == pos.y()

    def _restoreScrollPos(self):
        """Restore scroll bar position for document
        """
        try:
            self._view.page().mainFrame().contentsSizeChanged.disconnect(self._restoreScrollPos)
        except TypeError:  # already has been disconnected
            pass
        
        if not self._visiblePath in self._scrollPos:
            return  # no data for this document
        
        frame = self._view.page().mainFrame()

        frame.setScrollPosition(self._scrollPos[self._visiblePath])
        
        if self._hAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Horizontal, frame.scrollBarMaximum(Qt.Horizontal))
        
        if self._vAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Vertical, frame.scrollBarMaximum(Qt.Vertical))

    def _onDocumentChanged(self, old, new):
        """Current document changed, update preview
        """
        if new is not None:
            self._thread.process(new.filePath(), new.language(), new.text())

    def _onTextChanged(self, document):
        """Text changed, update preview
        """
        self._thread.process(document.filePath(), document.language(), document.text())

    def _setHtml(self, filePath, html):
        """Set HTML to the view and restore scroll bars position.
        Called by the thread
        """
        self._saveScrollPos()
        self._visiblePath = filePath
        self._view.page().mainFrame().contentsSizeChanged.connect(self._restoreScrollPos)
        self._view.setHtml(html,baseUrl=QUrl.fromLocalFile(filePath))
