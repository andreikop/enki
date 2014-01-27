# ********************************************
# preview.py - HTML, Markdown and ReST preview
# ********************************************

import os.path
import collections
import Queue


from PyQt4.QtCore import pyqtSignal, QSize, Qt, QThread, QTimer, QUrl
from PyQt4.QtGui import QDesktopServices, QFileDialog, QIcon, QMessageBox, QWidget
from PyQt4.QtWebKit import QWebPage
from PyQt4 import QtGui
from PyQt4 import uic
from PyQt4.QtWebKit import QWebPage

from enki.core.core import core

from enki.widgets.dockwidget import DockWidget

from enki.plugins.preview import isMarkdownFile, isHtmlFile

from ApproxMatch import find_approx_text_in_target




class ConverterThread(QThread):
    """Thread converts markdown to HTML
    """
    htmlReady = pyqtSignal(unicode, unicode)

    _Task = collections.namedtuple("Task", ["filePath", "language", "text"])

    def __init__(self):
        QThread.__init__(self)
        self._queue = Queue.Queue()
        self.start(QThread.LowPriority)

    def process(self, filePath, language, text):
        """Convert data and emit result
        """
        self._queue.put(self._Task(filePath, language, text))

    def stop_async(self):
        self._queue.put(None)

    def _getHtml(self, language, text):
        """Get HTML for document
        """
        if language == 'HTML':
            return text
        elif language == 'Markdown':
            return self._convertMarkdown(text)
        elif language == 'reStructuredText':
            htmlAscii = self._convertReST(text)
            return unicode(htmlAscii, 'utf8')
        else:
            return 'No preview for this type of file'

    def _convertMarkdown(self, text):
        """Convert Markdown to HTML
        """
        try:
            import markdown
        except ImportError:
            return 'Markdown preview requires <i>python-markdown</i> package<br/>' \
                   'Install it with your package manager or see ' \
                   '<a href="http://packages.python.org/Markdown/install.html">installation instructions</a>'

        try:
            import mdx_mathjax
        except ImportError:
            pass  #mathjax doesn't require import statement if installed as extension

        extensions = ['fenced_code', 'nl2br']

        # version 2.0 supports only extension names, not instances
        if markdown.version_info[0] > 2 or \
           (markdown.version_info[0] == 2 and markdown.version_info[1] > 0):

            class _StrikeThroughExtension(markdown.Extension):
                """http://achinghead.com/python-markdown-adding-insert-delete.html
                Class is placed here, because depends on imported markdown, and markdown import is lazy
                """
                DEL_RE = r'(~~)(.*?)~~'
                def extendMarkdown(self, md, md_globals):
                    # Create the del pattern
                    delTag = markdown.inlinepatterns.SimpleTagPattern(self.DEL_RE, 'del')
                    # Insert del pattern into markdown parser
                    md.inlinePatterns.add('del', delTag, '>not_strong')

            extensions.append(_StrikeThroughExtension())

        try:
            return markdown.markdown(text,  extensions + ['mathjax'])
        except (ImportError, ValueError):  # markdown raises ValueError or ImportError, depends on version
                                           # it is not clear, how to distinguish missing mathjax from other errors
            return markdown.markdown(text, extensions) #keep going without mathjax

    def _convertReST(self, text):
        """Convert ReST
        """
        try:
            import docutils.core
        except ImportError:
            return 'ReStructuredText preview requires <i>python-docutils</i> package<br/>' \
                   'Install it with your package manager or see ' \
                   '<a href="http://pypi.python.org/pypi/docutils"/>this page</a>'

        return docutils.core.publish_string(text, writer_name='html')

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            # wait task
            task = self._queue.get()
            # take the last task
            while self._queue.qsize():
                task = self._queue.get()

            if task is None:  # None is a quit command
                break

            html = self._getHtml(task.language, task.text)

            if not self._queue.qsize():  # Do not emit results, if having new task
                self.htmlReady.emit(task.filePath, html)


class PreviewDock(DockWidget):
    """GUI and implementation
    """
    closed = pyqtSignal()

    def __init__(self):
        DockWidget.__init__(self, core.mainWindow(), "&Preview", QIcon(':/enkiicons/internet.png'), "Alt+P")
        self._widget = QWidget(self)

        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Preview.ui'), self._widget)

        self._loadTemplates()

        self._widget.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self._widget.webView.page().linkClicked.connect(self._onLinkClicked)

        self._widget.webView.page().mainFrame().titleChanged.connect(self._updateTitle)
        self.setWidget(self._widget)
        self.setFocusProxy(self._widget.webView )

        self._widget.cbEnableJavascript.clicked.connect(self._onJavaScriptEnabledCheckbox)

        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)

        self._scrollPos = {}
        self._vAtEnd = {}
        self._hAtEnd = {}

        self._thread = ConverterThread()
        self._thread.htmlReady.connect(self._setHtml)

        self._visiblePath = None

        # If we update Preview on every key pressing, freezes are sensible (GUI thread draws preview too slowly
        # This timer is used for drawing Preview 300 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(300)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self._widget.cbTemplate.currentIndexChanged.connect(self._onCurrentTemplateChanged)

        self._scheduleDocumentProcessing()
        self._applyJavaScriptEnabled(self._isJavaScriptEnabled())

        self._widget.tbSave.clicked.connect(self.onSave)

        self.initPreviewToTextSync()
        self.initTextToPreviewSync()

# Synchronizing between the text pane and the preview pane
# ========================================================
# A single click in the preview pane should move the text pane's cursor to the corresponding location. Likewise, movement of the text pane's cursor should select the corresponding text in the preview pane. To do so, an approximate search for text surrounding the current cursor or click location perfomed on text in the other pane provides the corresponding location in the other pane to highlight.
#
# Preview-to-text sync
# --------------------
# For this sync, the first step is to find the single click's location in a plain text rendering of the preview's web content. This is implemented in JavaScript, which emits a Qt signal with the location on a click. A slot connected to this signal then performs the approximate match and updates the text pane's cursor. To do this:
#
# #. ``js_click``, a PyQt signal with a single numeric argument (the index into a string containing the plain text rendering of the web page) is defined. This signal is :ref:`connected <onJavaScriptCleared.connect>` to the ``onWebviewClick`` slot.
# #. The ``onJavaScriptCleared`` method inserts the JavaScript to listen for a click and then emit a signal giving the click's location.
# #. The ``onWebviewClick`` method then performs the approximate match and updates the text pane's cursor location.
# #. When a new web page is loaded, all JavaScript is lost and must be reinserted. The ``onJavaScriptCleared`` slot, connected to the ``javaScriptWindowObjectCleared`` signal, does this.

    # A signal emitted by clicks in the web view, per 1 above.
    js_click = pyqtSignal(int)
                          # int: The index of the click character in a text rendering of the web page.

    # Initialize the system per items 1, 2, and 4 above.
    def initPreviewToTextSync(self):
        # Insert our onClick JavaScript.
        self.onJavaScriptCleared()
        # Connect the signal emitted by the JavaScript onClick handler to onWebviewClick.
        self.js_click.connect(self.onWebviewClick)
        # Qt emits the `javaScriptWindowObjectCleared <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#javaScriptWindowObjectCleared.>`_ signal when a web page is loaded. When this happens, reinsert our onClick JavaScript. 
        self._widget.webView.page().mainFrame().javaScriptWindowObjectCleared.connect(self.onJavaScriptCleared)

    # This is called before starting a new load of a web page, per item 2 above.
    def onJavaScriptCleared(self):
        mf = self._widget.webView.page().mainFrame()
        # Use `addToJavaScriptWindowObject <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#addToJavaScriptWindowObject>`_ to make this PreviewDock object known to JavaScript, so that JavaScript can emit the ``js_click`` signal defined by PreviewDock.
        mf.addToJavaScriptWindowObject("PyPreviewDock", self)
        # Use `evaluateJavaScript <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#evaluateJavaScript>`_ to insert our ``onclick()`` handler. The job of this handler is to translate a mouse click into an index into the text rendering of the webpage. To do this, we must:
        #
        # #. Get the current selection made by the mouse click, which is typically an empty range. (I assume a click and drag will produce a non-empty range).
        # #. Extend a copy of this range so that it begins at the start of the webpage and, of course, ends at the character nearest the latest mouse click.
        # #. Get a string rendering of this range.
        # #. Emit a signal with the length of this string.
        res = mf.evaluateJavaScript(
            'window.onclick = function () {' +
            # The `window.onclick <https://developer.mozilla.org/en-US/docs/Web/API/Window.onclick>`_ event is "called when the user clicks the mouse button while the cursor is in the window." Although the docs claim that "this event is fired for any mouse button pressed", I found experimentally that it on fires on a left-click release; middle and right clicks had no effect.

            '    var r = window.getSelection().getRangeAt(0).cloneRange();' +
                 # This performs step 1 above. In particular:
                 #
                 # - `window.getSelection <https://developer.mozilla.org/en-US/docs/Web/API/Window.getSelection>`_ "returns a `Selection <https://developer.mozilla.org/en-US/docs/Web/API/Selection>`_ object representing the range of text selected by the user." Since this is only called after a click, I assume the Selection object is non-null.
                 # - The Selection.\ `getRangeAt <https://developer.mozilla.org/en-US/docs/Web/API/Selection.getRangeAt>`_ method "returns a range object representing one of the ranges currently selected." Per the Selection `glossary <https://developer.mozilla.org/en-US/docs/Web/API/Selection#Glossary>`_, "A user will normally only select a single range at a time..." The index for retrieving a single-selection range is of course 0.
                 # - "The `Range <https://developer.mozilla.org/en-US/docs/Web/API/range>`_ interface represents a fragment of a document that can contain nodes and parts of text nodes in a given document." We clone it to avoid modifying the user's existing selection using `cloneRange <https://developer.mozilla.org/en-US/docs/Web/API/Range.cloneRange>`_.

            '    r.setStartBefore(document.body);' +
                 # This performs step 2 above: the cloned range is now changed to contain the web page from its beginning to the point where the user click by calling `setStartBefore <https://developer.mozilla.org/en-US/docs/Web/API/Range.setStartBefore>`_ on `document.body <https://developer.mozilla.org/en-US/docs/Web/API/document.body>`_.

            '    var r_str = r.cloneContents().textContent.toString();' +
                 # Step 3:
                 #
                 # - `cloneContents <https://developer.mozilla.org/en-US/docs/Web/API/Range.cloneContents>`_ "Returns a `DocumentFragment <https://developer.mozilla.org/en-US/docs/Web/API/DocumentFragment>`_ copying the nodes of a Range."
                 # - DocumentFragment's parent `Node <a DOMString representing the textual content of an element and all its descendants.>`_ provides a `textContent <https://developer.mozilla.org/en-US/docs/Web/API/Node.textContent>`_ property which gives "a DOMString representing the textual content of an element and all its descendants." This therefore contains a text rendering of the webpage from the beginning of the page to the point where the user clicked.

            '    PyPreviewDock.js_click(r_str.length);' +
                 # Step 4: the length of the string gives the index of the click into a string containinga text rendering of the webpage. Emit a signal with that information.
            '};')

        # Make sure no errors were returned; the result should be empty.
        assert not res.toString()
    
    # Per item 3 above, this is called when the user clicks in the web view. It finds the matching location in the text pane then moves the text pane cursor.
    def onWebviewClick(self,
                       web_index):
                       # The index of the click character in a text rendering of the web page.
        # Perform an approximate match between the clicked webpage text and the text pane text.
        mf = self._widget.webView.page().mainFrame()
        qp = core.workspace().currentDocument().qutepart
        text_index = find_approx_text_in_target(mf.toPlainText(), web_index, qp.text)
        # Move the cursor to text_index in qutepart, assuming corresponding text was found.
        if text_index >= 0:
            self.moveTextPaneToIndex(text_index)

    # Given an index into the text pane, move the cursor to that index.
    def moveTextPaneToIndex(self,
                            text_index):
                            # The index into the text pane at which to place the cursor.
        # Move the cursor to text_index.
        qp = core.workspace().currentDocument().qutepart
        cursor = qp.textCursor()
        # Tell the text to preview sync to ignore this cursor position change.
        cursor.setPosition(text_index, QtGui.QTextCursor.MoveAnchor)
        self._previewToTextSyncRunning = True
        qp.setTextCursor(cursor)
        self._previewToTextSyncRunning = False
        # Scroll the document to make sure the cursor is visible.
        qp.ensureCursorVisible()
        # Focus on the editor so the cursor will be shown and ready for typing.
        core.workspace().focusCurrentDocument()
#
# Text-to-preview sync
# --------------------
# The opposite direction is easier, since all the work can be done in Python. When the cursor moves in the text pane, find its matching location in the preview pane using an approximate match. Select several characters before and after the matching point to make the location more visible, since the preview pane lacks a cursor. Specifically:
#
# #. initTextToPreviewSync sets up a timer and connects the _onCursorPositionChanged  method.
# #. _onCursorPositionChanged is called each time the cursor moves. It starts or resets a short timer. The timer's expiration calls:
# #. syncTextToWeb performs the approximate match, then calls moveWebPaneToIndex to sync the web pane with the text pane.
# #. moveWebToPane uses QWebFrame.find to search for the text under the anchor then select (or highlight) it.
#
    # Called when constructing the PreviewDoc. It performs item 1 above.
    def initTextToPreviewSync(self):
        # Create a timer which will sync the preview with the text cursor a short time after cursor movement stops.
        self._cursorMovementTimer = QTimer()
        self._cursorMovementTimer.setInterval(300)
        self._cursorMovementTimer.timeout.connect(self._syncTextToPreview)
        # Restart this timer every time the cursor moves.
        core.workspace().currentDocument().qutepart.cursorPositionChanged.connect(self._onCursorPositionChanged)
        # Set up a variable to tell us when the preview to text sync just fired, disabling this sync. Otherwise, that sync would trigger this sync, which is unnecessary.
        self._previewToTextSyncRunning = False
    
    # Called when the cursor position in the text pane changes. It (re)schedules a text to web sync per item 2 above.
    def _onCursorPositionChanged(self):
        # Ignore this callback if a preview to text sync caused it.
        if not self._previewToTextSyncRunning:
            self._cursorMovementTimer.stop()
            self._cursorMovementTimer.start()
        
    # When the timer above expires, this is called to sync text to preview per item 3 above.
    def _syncTextToPreview(self):
        # Stop the timer; the next cursor movement will restart it.
        self._cursorMovementTimer.stop()
        # Perform an approximate match.
        mf = self._widget.webView.page().mainFrame()
        qp = core.workspace().currentDocument().qutepart
        web_index = find_approx_text_in_target(qp.text, qp.textCursor().position(), mf.toPlainText())
        # Move the cursor to web_index in the preview pane, assuming corresponding text was found.
        if web_index >= 0:
            self.movePreviewPaneToIndex(web_index)
    
    # Highlights web_index in the preview pane, per item 4 above.
    def movePreviewPaneToIndex(self,
            web_index,
            # The index to move the cursor / highlight to in the preview pane.
            select_radius=5):
            # The number of characters to highlight before and after web_index.
        #
        # Implementation: there's no direct way I know of to move the cursor in a web page. However, the find operation is fairly common. So, simply search from the beginning of the page for a substring of the web page's text rendering  from the beginning to a few characters before web_index. Then do a second search, starting at the character following the first search (a few characters before the web_index) to a few characters after the web_index.
        pg = self._widget.webView.page()
        mf = pg.mainFrame()
        txt = mf.toPlainText()
        # Hopefully, start the search location at the beginning of the document by clearing the previous selection using `removeAllRanges <https://developer.mozilla.org/en-US/docs/Web/API/Selection.removeAllRanges>`_.
        res = mf.evaluateJavaScript('window.getSelection().removeAllRanges();')
        assert not res.toString()
        # Determine the index a few characters before web_index then find it using `findText <http://qt-project.org/doc/qt-4.8/qwebpage.html#findText>`_, assuming the string isn't empty.
        before_web_index = max(0, web_index - select_radius)
        if before_web_index > 0:
            found = pg.findText(txt[:before_web_index], QWebPage.FindCaseSensitively)
            assert found
        # Determine the index a few characters after web_index and find it, highlighting this text.
        after_web_index = min(len(txt) - 1, web_index + select_radius)
        assert after_web_index > before_web_index
        found = pg.findText(txt[before_web_index:after_web_index], QWebPage.FindCaseSensitively)
        assert found
    
# Other handlers
# ==============
    def del_(self):
        """Uninstall themselves
        """
        self._typingTimer.stop()
        self._thread.htmlReady.disconnect(self._setHtml)
        self._thread.stop_async()
        self._thread.wait()

    def closeEvent(self, event):
        """Widget is closed. Clear it
        """
        self._clear()
        return DockWidget.closeEvent(self, event)

    def _onLinkClicked(self, url):
        res = QDesktopServices.openUrl(url)
        if res:
            core.mainWindow().statusBar().showMessage("{} opened in a browser".format(url.toString()), 2000)
        else:
            core.mainWindow().statusBar().showMessage("Failed to open {}".format(url.toString()), 2000)

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
        frame = self._widget.webView .page().mainFrame()
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
            self._widget.webView .page().mainFrame().contentsSizeChanged.disconnect(self._restoreScrollPos)
        except TypeError:  # already has been disconnected
            pass

        if not self._visiblePath in self._scrollPos:
            return  # no data for this document

        frame = self._widget.webView .page().mainFrame()

        frame.setScrollPosition(self._scrollPos[self._visiblePath])

        if self._hAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Horizontal, frame.scrollBarMaximum(Qt.Horizontal))

        if self._vAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Vertical, frame.scrollBarMaximum(Qt.Vertical))

    def _onDocumentChanged(self, old, new):
        """Current document changed, update preview
        """
        if new is not None:
            if isMarkdownFile(new):
                self._widget.cbTemplate.show()
                self._widget.lTemplate.show()
            else:
                self._widget.cbTemplate.hide()
                self._widget.lTemplate.hide()

        if new is not None and core.config()['Preview']['Enabled']:
            self._scheduleDocumentProcessing()
        else:
            self._clear()

    _CUSTOM_TEMPLATE_PATH = '<custom template>'
    def _loadTemplates(self):
        for path in [os.path.join(os.path.dirname(__file__), 'templates'),
                     os.path.expanduser('~/.enki/markdown-templates')]:
            if os.path.isdir(path):
                for fileName in os.listdir(path):
                    fullPath = os.path.join(path, fileName)
                    if os.path.isfile(fullPath):
                        self._widget.cbTemplate.addItem(fileName, fullPath)

        self._widget.cbTemplate.addItem('Custom...', self._CUSTOM_TEMPLATE_PATH)

        self._restorePreviousTemplate()

    def _restorePreviousTemplate(self):
        # restore previous template
        index = self._widget.cbTemplate.findText(core.config()['Preview']['Template'])
        if index != -1:
            self._widget.cbTemplate.setCurrentIndex(index)

    def _getCurrentTemplatePath(self):
        index = self._widget.cbTemplate.currentIndex()
        if index == -1:  # empty combo
            return ''

        return unicode(self._widget.cbTemplate.itemData(index))

    def _getCurrentTemplate(self):
        path = self._getCurrentTemplatePath()
        if not path:
            return ''

        try:
            with open(path) as file:
                text = file.read()
        except Exception as ex:
            text = 'Failed to load template {}: {}'.format(path, ex)
            core.mainWindow().statusBar().showMessage(text)
            return ''
        else:
            return text

    def _onCurrentTemplateChanged(self):
        """Update text or show message to the user"""
        if self._getCurrentTemplatePath() == self._CUSTOM_TEMPLATE_PATH:
            QMessageBox.information(core.mainWindow(),
                                   'Custom templaes help',
                                   '<html>See <a href="https://github.com/hlamer/enki/wiki/Markdown-preview-templates">'
                                   'this</a> wiki page for information about custom templates')
            self._restorePreviousTemplate()

        core.config()['Preview']['Template'] = self._widget.cbTemplate.currentText()
        core.config().flush()
        self._scheduleDocumentProcessing()

    def _onTextChanged(self, document):
        """Text changed, update preview
        """
        if core.config()['Preview']['Enabled']:
            self._typingTimer.stop()
            self._typingTimer.start()

    def show(self):
        """When shown, update document, if posible
        """
        DockWidget.show(self)
        self._scheduleDocumentProcessing()

    def _scheduleDocumentProcessing(self):
        """Start document processing with the thread.
        """
        self._typingTimer.stop()

        document = core.workspace().currentDocument()
        if document is not None:
            language = document.qutepart.language()
            text = document.qutepart.text
            if isMarkdownFile(document):
                language = 'Markdown'
                text = self._getCurrentTemplate() + text
            elif isHtmlFile(document):
                language = 'HTML'
            # for rest language is already correct
            self._thread.process(document.filePath(), language, text)

    def _setHtml(self, filePath, html):
        """Set HTML to the view and restore scroll bars position.
        Called by the thread
        """
        self._saveScrollPos()
        self._visiblePath = filePath
        self._widget.webView.page().mainFrame().contentsSizeChanged.connect(self._restoreScrollPos)
        self._widget.webView.setHtml(html,baseUrl=QUrl.fromLocalFile(filePath))

    def _clear(self):
        """Clear themselves.
        Might be necesssary for stop executing JS and loading data
        """
        self._setHtml('', '')

    def _isJavaScriptEnabled(self):
        """Check if JS is enabled in the settings
        """
        return core.config()['Preview']['JavaScriptEnabled']

    def _onJavaScriptEnabledCheckbox(self, enabled):
        """Checkbox clicked, save and apply settings
        """
        core.config()['Preview']['JavaScriptEnabled'] = enabled;
        core.config().flush()

        self._applyJavaScriptEnabled(enabled)

    def _applyJavaScriptEnabled(self, enabled):
        """Update QWebView settings and QCheckBox state
        """
        self._widget.cbEnableJavascript.setChecked(enabled)

        settings = self._widget.webView.settings()
        settings.setAttribute(settings.JavascriptEnabled, enabled)

        self._scheduleDocumentProcessing()

    def onSave(self):
        """Save contents of the preview"""
        path = QFileDialog.getSaveFileName(self, 'Save Preview as HTML', filter='HTML (*.html)')
        if path:
            try:
                with open(path, 'w') as openedFile:
                    openedFile.write(self._widget.webView.page().mainFrame().toHtml())
            except (OSError, IOError) as ex:
                QMessageBox.critical(self, "Failed to save HTML", unicode(str(ex), 'utf8'))
