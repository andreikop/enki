# ********************************************
# preview.py - HTML, Markdown and ReST preview
# ********************************************

import os.path
import collections
import Queue


from PyQt4.QtCore import pyqtSignal, QSize, Qt, QThread, QTimer, QUrl, QPoint
from PyQt4.QtGui import QDesktopServices, QFileDialog, QIcon, QMessageBox, QWidget
from PyQt4.QtWebKit import QWebPage
from PyQt4 import QtGui
from PyQt4 import uic
from PyQt4.QtWebKit import QWebPage
from PyQt4.QtTest import QTest

from enki.core.core import core

from enki.widgets.dockwidget import DockWidget

from enki.plugins.preview import isHtmlFile

# If TRE isn't installed, this import will fail. In this case, disable the sync
# feature.
try:
    from approx_match import findApproxTextInTarget
except ImportError as e:
    findApproxTextInTarget = None




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
        elif language == 'Restructured Text':
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
            return 'Restructured Text preview requires <i>python-docutils</i> package<br/>' \
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

        # Only set up sync if TRE is installed.
        if findApproxTextInTarget:
            self._initPreviewToTextSync()
            self._initTextToPreviewSync()

    # Synchronizing between the text pane and the preview pane
    ##========================================================
    # A single click in the preview pane should move the text pane's cursor to the
    # corresponding location. Likewise, movement of the text pane's cursor should
    # select the corresponding text in the preview pane. To do so, an approximate
    # search for text surrounding the current cursor or click location perfomed on
    # text in the other pane provides the corresponding location in the other pane
    # to highlight.
    #
    # Bugs / to-do items
    ##------------------
    # #. I call ``toPlainText()`` several times. In the past, this was quite slow
    #    in a ``QTextEdit``. Check performance and possibly cache this value; it
    #    should be easy to update by adding a few lines to _setHtml().
    #
    # This function returns a delta vertical scroll amount, in pixels, in order to
    # align the top (y) coordinate of the cursor in the target widget with the cursor
    # in the source widget. If the the two widgets don't intersect vertically,
    # then the target cursor is scrolled to be as close to the source
    # widget as possible: if the source widget is above the target, the target
    # widget will scroll to place the cursor at the top of the widget; if the
    # source widget is below the target, the target widget will scroll to place
    # the cursor at the bottom of the widget.
    #
    # Ideally, this would instead operate on the baseline of the text, rather
    # than the top (or bottom), but getting this is much harder.
    #
    # TODO: diagram.
    #
    def _alignScrollAmount(self,
      # The top (y) coordinate of the source widget in a global coordinate frame,
      # such as screen coordinates. In pixels.
      sourceGlobalTop,
      # The top coordinate of the cursor in the source widget, measured from the
      # top of the widget, NOT the top of the viewport. In pixels.
      sourceCursorTop,

      # The top (y) coordinate of the target widget in a global coordinate frame,
      # such as screen coordinates. In pixels.
      targetGlobalTop,
      # The top coordinate of the cursor in the target widget, measured from the
      # top of the widget, NOT the top of the viewport. In pixels.
      targetCursorTop,
      # The height of the target widget. In pixels.
      targetHeight,
      # The height of the cursor in the target widget. In pixels.
      targetCursorHeight):

        # Compute the raw delta between the source and target widgets.
        dTop = (
          # Global coords of the source cursor top.
          (sourceGlobalTop + sourceCursorTop) -
          # Global coords of the target cursor top. The difference
          # gives the number of pixels separating them.
          (targetGlobalTop + targetCursorTop) );

        # Clip the resulting delta so that the target cursor remains visible.
        dTop = min(max(-targetCursorTop, dTop),
          targetHeight - targetCursorHeight - targetCursorTop)

        return dTop

    # Run JavaScript to determine the coordinates and height of the
    # anchor of the selection in the web view.
    #
    # Return values:
    #
    # None if the selection is empty, or (top, left) where:
    #
    #   top - Top of the selection, measured from the web page's origin. In pixels.
    #
    #   left - Left of the selection, measured from the web page's origin. In pixels.
    def _webCursorCoords(self):
        res = self._widget.webView.page().mainFrame(). \
          evaluateJavaScript('selectionAnchorCoords();')
        # See if a 3-element tuple is returned. Null is returned if the
        # selection is empty.
        if not res:
            return None
        left, top, height = res
        return top, height

    # Scroll the web view to align its cursor with the qutepart cursor or vice
    # versa.
    def _scrollSync(self, doTextToWebSync):
        # Per the `window geometry
        # <http://qt-project.org/doc/qt-4.8/application-windows.html#window-geometry>`_,
        # `geometry() <http://qt-project.org/doc/qt-4.8/qwidget.html#geometry-prop>`_
        # is relative to the parent frame. Then, use `mapToGlobal
        # <http://qt-project.org/doc/qt-4.8/qwidget.html#mapToGlobal>`_ to
        # put this in global coordinates. This works for `QWebView
        # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebview.html>`_, since it
        # inherits from QWidget.
        wv = self._widget.webView
        qp = core.workspace().currentDocument().qutepart
        qpGlobalTop = qp.mapToGlobal(qp.geometry().topLeft()).y()
        wvGlobalTop = wv.mapToGlobal(wv.geometry().topLeft()).y() - 10

        # `qutepart.cursorRect()
        # <http://qt-project.org/doc/qt-4.8/qplaintextedit.html#cursorRect-2>`_
        # gives a value in viewport == widget coordinates. Use that directly.
        cr = qp.cursorRect()
        qpCursorTop = cr.top()
        qpCursorHeight = cr.height()

        # Widget height includes the scrollbars. Subtract that off to get a
        # viewable height for qutepart.
        qpHeight = qp.geometry().height()
        hsb = qp.horizontalScrollBar()
        # The scrollbar height is a constant, even if it's hidden. So, only
        # include it in calculations if it's visible.
        if hsb.isVisible():
            qpHeight -= qp.horizontalScrollBar().height()
        mf = wv.page().mainFrame()
        # Since `scrollBarGeometry <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#scrollBarGeometry>`_
        # returns an empty rect if the scroll bar doesn't exist, just subtract
        # its height.
        wvHeight = wv.geometry().height() - mf.scrollBarGeometry(Qt.Horizontal).height()

        # Use JavaScript to determine web view cursor height top and height.
        # There's no nice Qt way that I'm aware of, since Qt doesn't know about
        # these details inside a web view. If JavaScript can't determine this, then
        # silently abort the sync.
        ret = self._webCursorCoords()
        if not ret:
            return
        wvCursorTop, wvCursorHeight = ret

        if doTextToWebSync:
            deltaY = self._alignScrollAmount(qpGlobalTop, qpCursorTop,
              wvGlobalTop, wvCursorTop, wvHeight, wvCursorHeight)
            # Uncomment for helpful debug info.
            ##print(("qpGlobalTop = %d, qpCursorTop = %d, qpHeight = %d, deltaY = %d\n" +
            ##  "  wvGlobalTop = %d, wvCursorTop = %d, wvHeight = %d, wvCursorHeight = %d)") %
            ##  (qpGlobalTop, qpCursorTop, qpHeight, deltaY,
            ##  wvGlobalTop, wvCursorTop, wvHeight, wvCursorHeight))

            # Scroll based on this info using `setScrollPosition
            # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#scrollPosition-prop>`_.
            #
            # Note that scroll bars are backwards: to make the text go up, you must
            # move the bars down (a positive delta) and vice versa. Hence, the
            # subtration, rather than addition, below.
            mf.setScrollPosition(mf.scrollPosition() - QPoint(0, deltaY))
        else:
            deltaY = self._alignScrollAmount(wvGlobalTop, wvCursorTop,
              qpGlobalTop, qpCursorTop, qpHeight, qpCursorHeight)
            vsb = qp.verticalScrollBar()
            # The units for the vertical scroll bar is pixels not lines. So, do
            # a kludgy conversion by assuming that all line heights are the
            # same.
            vsb.setValue(vsb.value() - round(deltaY/qpCursorHeight))
    #
    #
    # Preview-to-text sync
    ##--------------------
    # This functionaliy relies heavily on the Web to Qt bridge. Some helpful
    # references:
    #
    # * `The QtWebKit Bridge <http://qt-project.org/doc/qt-4.8/qtwebkit-bridge.html>`_
    #   gives a helpful overview.
    # * `QWebView`_ is the top-level widget used to embed a Web page in a Qt
    #   application.
    #
    # For this sync, the first step is to find the single click's location in a
    # plain text rendering of the preview's web content. This is implemented in
    # JavaScript, which emits a Qt signal with the location on a click. A slot
    # connected to this signal then performs the approximate match and updates the
    # text pane's cursor. To do this:
    #
    # #. ``jsClick``, a PyQt signal with a single numeric argument (the index into
    #    a string containing the plain text rendering of the web page) is defined.
    #    This signal is :ref:`connected <onJavaScriptCleared.connect>` to the
    #    ``onWebviewClick`` slot.
    # #. The ``onJavaScriptCleared`` method inserts the JavaScript to listen for a
    #    click and then emit a signal giving the click's location.
    # #. The ``onWebviewClick`` method then performs the approximate match and
    #    updates the text pane's cursor location.
    # #. When a new web page is loaded, all JavaScript is lost and must be reinserted.
    #    The ``onJavaScriptCleared`` slot, connected to the
    #    ``javaScriptWindowObjectCleared`` signal, does this.

    # A signal emitted by clicks in the web view, per 1 above.
    jsClick = pyqtSignal(
      # The index of the clicked character in a text rendering
      # of the web page.
      int)

    def _initPreviewToTextSync(self):
        """Initialize the system per items 1, 2, and 4 above."""
        # Insert our on-click JavaScript.
        self._onJavaScriptCleared()
        # .. _onJavaScriptCleared.connect:
        #
        # Connect the signal emitted by the JavaScript onclick handler to
        # ``onWebviewClick``.
        self.jsClick.connect(self._onWebviewClick)
        # Qt emits the `javaScriptWindowObjectCleared
        # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#javaScriptWindowObjectCleared.>`_
        # signal when a web page is loaded. When this happens, reinsert our
        # onclick JavaScript.
        self._widget.webView.page().mainFrame(). \
          javaScriptWindowObjectCleared.connect(self._onJavaScriptCleared)

    def _onJavaScriptCleared(self):
        """This is called before starting a new load of a web page, per item 2 above."""
        mf = self._widget.webView.page().mainFrame()
        # Use `addToJavaScriptWindowObject
        # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#addToJavaScriptWindowObject>`_
        # to make this PreviewDock object known to JavaScript, so that
        # JavaScript can emit the ``jsClick`` signal defined by PreviewDock.
        mf.addToJavaScriptWindowObject("PyPreviewDock", self)
        # Use `evaluateJavaScript
        # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#evaluateJavaScript>`_
        # to insert our ``onclick()`` handler. The job of this handler is to
        # translate a mouse click into an index into the text rendering of the
        # webpage. To do this, we must:
        #
        # #. Get the current selection made by the mouse click, which is typically
        #    an empty range. (I assume a click and drag will produce a non-empty
        #    range; however this code still works).
        # #. Extend a copy of this range so that it begins at the start of the
        #    webpage and, of course, ends at the character nearest the mouse
        #    click.
        # #. Get a string rendering of this range.
        # #. Emit a signal with the length of this string.
        #
        # Note: A JavaScript development environment with this code is available
        # at http://jsfiddle.net/hgDwx/110/.
        res = mf.evaluateJavaScript(
            # The `window.onclick
            # <https://developer.mozilla.org/en-US/docs/Web/API/Window.onclick>`_
            # event is "called when the user clicks the mouse button while the
            # cursor is in the window." Although the docs claim that "this event
            # is fired for any mouse button pressed", I found experimentally
            # that it on fires on a left-click release; middle and right clicks
            # had no effect.
            'window.onclick = function () {' +

                 # This performs step 1 above. In particular:
                 #
                 # - `window.getSelection <https://developer.mozilla.org/en-US/docs/Web/API/Window.getSelection>`_
                 #   "returns a `Selection
                 #   <https://developer.mozilla.org/en-US/docs/Web/API/Selection>`_
                 #   object representing the range of text selected by the
                 #   user." Since this is only called after a click, I assume
                 #   the Selection object is non-null.
                 # - The Selection.\ `getRangeAt <https://developer.mozilla.org/en-US/docs/Web/API/Selection.getRangeAt>`_
                 #   method "returns a range object representing one of the
                 #   ranges currently selected." Per the Selection `glossary
                 #   <https://developer.mozilla.org/en-US/docs/Web/API/Selection#Glossary>`_,
                 #   "A user will normally only select a single range at a
                 #   time..." The index for retrieving a single-selection range
                 #   is of course 0.
                 # - "The `Range <https://developer.mozilla.org/en-US/docs/Web/API/range>`_
                 #   interface represents a fragment of a document that can
                 #   contain nodes and parts of text nodes in a given document."
                 #   We clone it to avoid modifying the user's existing
                 #   selection using `cloneRange
                 #   <https://developer.mozilla.org/en-US/docs/Web/API/Range.cloneRange>`_.
                'var r = window.getSelection().getRangeAt(0).cloneRange();' +

                 # This performs step 2 above: the cloned range is now changed
                 # to contain the web page from its beginning to the point where
                 # the user clicked by calling `setStartBefore
                 # <https://developer.mozilla.org/en-US/docs/Web/API/Range.setStartBefore>`_
                 # on `document.body
                 # <https://developer.mozilla.org/en-US/docs/Web/API/document.body>`_.
                'r.setStartBefore(document.body);' +

                 # Step 3:
                 #
                 # - `cloneContents <https://developer.mozilla.org/en-US/docs/Web/API/Range.cloneContents>`_
                 #   "Returns a `DocumentFragment
                 #   <https://developer.mozilla.org/en-US/docs/Web/API/DocumentFragment>`_
                 #   copying the nodes of a Range."
                 # - DocumentFragment's parent `Node <https://developer.mozilla.org/en-US/docs/Web/API/Node>`_
                 #   provides a `textContent
                 #   <https://developer.mozilla.org/en-US/docs/Web/API/Node.textContent>`_
                 #   property which gives "a DOMString representing the textual
                 #   content of an element and all its descendants." This therefore
                 #   contains a text rendering of the webpage from the beginning of the
                 #   page to the point where the user clicked.
                 'var rStr = r.cloneContents().textContent.toString();' +

                 # Step 4: the length of the string gives the index of the click
                 # into a string containing a text rendering of the webpage.
                 # Emit a signal with that information.
                'PyPreviewDock.jsClick(rStr.length);' +
            '};' +

            # This function returns the [top, left] position in pixels of ``obj``
            # relative to the screen, not to the viewport. This introduces one
            # potential problem: if obj is not visible when this is called, it
            # returns coordinates outside the screen (such that top or left is
            # negative or greater than the screen's height or width.
            #
            # It was slightly modified from http://www.quirksmode.org/js/findpos.html,
            #  which reproduces jQuery's offset method (https://api.jquery.com/offset/).
            'function findPos(obj) {' +
                'var curLeft = 0;' +
                'var curTop = 0;' +
                 # element.offsetLeft and element.offsetTop measure relative to
                 # the object's parent. Walk the tree of parents, summing each
                 # offset to determine the offset from the origin of the web page.
                'do {' +
                    'curLeft += obj.offsetLeft;' +
                    'curTop += obj.offsetTop;' +
                '} while (obj = obj.offsetParent);' +
                # See `element.getBoundingClientRect
                # <https://developer.mozilla.org/en-US/docs/Web/API/element.getBoundingClientRect>`_
                # for converting viewport coords to screen coords.
                'return [curLeft - window.scrollX, curTop - window.scrollY];' +
            '}' +

            # This function returns [top, left, width], of the current
            # selection, where:
            #
            #   top, left - coordinates of the anchor of the
            #     selection relative to the screen, in pixels.
            #
            #   height - height at the beginning of the selection, in pixels.
            #
            # Adapted from http://stackoverflow.com/questions/2031518/javascript-selection-range-coordinates.
            # Changes:
            #
            # - jQuery usage eliminated for all but debug prints.
            # - The original code used ``range.endOffset`` instead of
            #   ``selection.focusOffset``. This caused occasional errors when
            #   dragging selections.
            'function selectionAnchorCoords() {' +
                # Using ``window.getSelection()``
                # Make sure a `selection <https://developer.mozilla.org/en-US/docs/Web/API/Selection>`_ exists.
                'var selection = window.getSelection();' +
                'if (selection.rangeCount == 0) return 0;' +

                # The selection can contain not just a point (from a
                # single mouse click) but a range (from a mouse drag or
                # shift+arrow keys).
                # We're looking for the coordinates of the focus node
                # (the place where the mouse ends up after making the selection).
                # However, the range returned by ``selection.getRangeAt(0)``
                # begins earlier in the document and ends later, regardless
                # how the mouse was dragged. So, create a new range containing
                # just the point at the focus node, so we actually get
                # a range pointing to where the mouse is.
                # Ref: `focus <https://developer.mozilla.org/en-US/docs/Web/API/Selection.focusNode>`_ of the selection.
                # `Range <https://developer.mozilla.org/en-US/docs/Web/API/range>`_
                'rangeAtFocus = document.createRange();' +
                'rangeAtFocus.setStart(selection.focusNode, selection.focusOffset);' +

                # Insert a measurable element (a span) at the selection's
                # focus.
                'var span = document.createElement("span");' +
                'rangeAtFocus.insertNode(span);' +

                # Measure coordinates at this span, then remove it. Note:
                # span.remove() isn't supported in the PyQt 4 I'm running, hence
                # the longer syntax below.
                'ret = findPos(span);' +
                'height = span.offsetHeight;' +
                'span.parentNode.removeChild(span);' +

                ## Return      top,   left, height.
                'return    [ret[0], ret[1], height];'
            '}')

        # Make sure no errors were returned; the result should be empty.
        assert not res

    def _webTextContent(self):
        """Return the ``textContent`` of the entire web page. This differs from
        ``mainFrame().toPlainText()``, which uses ``innerText`` and therefore
        produces a slightly differnt result. Since the JavaScript signal's index
        is computed based on textContent, that must be used for all web to text
        sync operations.
        """
        return (self._widget.webView.page().mainFrame().
          evaluateJavaScript('document.body.textContent.toString()'))

    def _onWebviewClick(self, webIndex):
        """Per item 3 above, this is called when the user clicks in the web view. It
        finds the matching location in the text pane then moves the text pane
        cursor.

        Params:
        webIndex - The index of the clicked character in a text rendering
            of the web page.
        """
        # Retrieve the web page text and the qutepart text.
        tc = self._webTextContent()
        qp = core.workspace().currentDocument().qutepart
        # Perform an approximate match between the clicked webpage text and the
        # qutepart text.
        textIndex = findApproxTextInTarget(tc, webIndex, qp.text)
        # Move the cursor to textIndex in qutepart, assuming corresponding text
        # was found.
        if textIndex >= 0:
            self._moveTextPaneToIndex(textIndex)

    def _moveTextPaneToIndex(self, textIndex, noWebSync=True):
        """Given an index into the text pane, move the cursor to that index.

        Params:
        textIndex - The index into the text pane at which to place the cursor.
        noWebSync - True to prevent the web-to-text sync from running as a
            result of calling this routine.
        """
        # Move the cursor to textIndex.
        qp = core.workspace().currentDocument().qutepart
        cursor = qp.textCursor()
        # Tell the text to preview sync to ignore this cursor position change.
        cursor.setPosition(textIndex, QtGui.QTextCursor.MoveAnchor)
        self._previewToTextSyncRunning = noWebSync
        qp.setTextCursor(cursor)
        self._previewToTextSyncRunning = False
        # Scroll the document to make sure the cursor is visible.
        qp.ensureCursorVisible()
        # Sync the cursors.
        self._scrollSync(False)
        # Focus on the editor so the cursor will be shown and ready for typing.
        core.workspace().focusCurrentDocument()

    # Text-to-preview sync
    ##--------------------
    # The opposite direction is easier, since all the work can be done in Python.
    # When the cursor moves in the text pane, find its matching location in the
    # preview pane using an approximate match. Select several characters before and
    # after the matching point to make the location more visible, since the preview
    # pane lacks a cursor. Specifically:
    #
    # #. initTextToPreviewSync sets up a timer and connects the _onCursorPositionChanged method.
    # #. _onCursorPositionChanged is called each time the cursor moves. It starts or
    #    resets a short timer. The timer's expiration calls syncTextToWeb.
    # #. syncTextToWeb performs the approximate match, then calls moveWebPaneToIndex
    #    to sync the web pane with the text pane.
    # #. moveWebToPane uses QWebFrame.find to search for the text under the anchor
    #    then select (or highlight) it.

    def _initTextToPreviewSync(self):
        """Called when constructing the PreviewDoc. It performs item 1 above."""
        # Create a timer which will sync the preview with the text cursor a
        # short time after cursor movement stops.
        self._cursorMovementTimer = QTimer()
        self._cursorMovementTimer.setInterval(300)
        self._cursorMovementTimer.timeout.connect(self._syncTextToPreview)
        # Restart this timer every time the cursor moves.
        self.currentCursorPositionChanged = core.workspace().currentDocument().qutepart.cursorPositionChanged
        self.currentCursorPositionChanged.connect(self._onCursorPositionChanged)
        # Set up a variable to tell us when the preview to text sync just fired,
        # disabling this sync. Otherwise, that sync would trigger this sync,
        # which is unnecessary.
        self._previewToTextSyncRunning = False
        # Make the page's content editable, to provide for single-line selection
        # performed in _movePreviewPaneToIndex(). The other option: make it
        # editable for just a moment, perform the action, then make it
        # uneditable. Since this *might* be slower, and since clicks to the web
        # page move the focus immediately back to the text editor, I don't think
        # it's possible for a user to edit the page, so I put it here.
        self._widget.webView.page().setContentEditable(True)

    def _onCursorPositionChanged(self):
        """Called when the cursor position in the text pane changes. It (re)schedules
        a text to web sync per item 2 above. Note that the signal connected to
        this slot must be updated when the current document changes, since we only
        want cursor movement notification from the active text document. This is
        handled in _onDocumentChanged.
        """
        # Ignore this callback if a preview to text sync caused it.
        if not self._previewToTextSyncRunning:
            self._cursorMovementTimer.stop()
            self._cursorMovementTimer.start()

    def _syncTextToPreview(self):
        """When the timer above expires, this is called to sync text to preview
        per item 3 above.
        """
        # Stop the timer; the next cursor movement will restart it.
        self._cursorMovementTimer.stop()
        # Perform an approximate match.
        mf = self._widget.webView.page().mainFrame()
        qp = core.workspace().currentDocument().qutepart
        webIndex = findApproxTextInTarget(qp.text, qp.textCursor().position(), mf.toPlainText())
        # Move the cursor to webIndex in the preview pane, assuming
        # corresponding text was found.
        if webIndex >= 0:
            self._movePreviewPaneToIndex(webIndex)

    def _movePreviewPaneToIndex(self, webIndex):
        """Highlights webIndex in the preview pane, per item 4 above.

        Params:
        webIndex - The index to move the cursor / highlight to in the preview pane.
        """
        # Implementation: there's no direct way I know of to move the cursor in
        # a web page. However, the find operation is fairly common. So, simply
        # search from the beginning of the page for a substring of the web
        # page's text rendering from the beginning to webIndex. Then press home
        # followed by shift+end to select the line the cursor is on. (This
        # relies on the page being editable, which is set in
        # _initTextToPreviewSync).
        pg = self._widget.webView.page()
        mf = pg.mainFrame()
        txt = mf.toPlainText()
        # Start the search location at the beginning of the document by clearing
        # the previous selection using `findText
        # <http://qt-project.org/doc/qt-4.8/qwebpage.html#findText>`_ with an
        # empty search string.
        pg.findText('')
        # Find the index with findText_.
        ft = txt[:webIndex]
        found = pg.findText(ft, QWebPage.FindCaseSensitively)

        # Before highlighting a line, make sure the text was found. If the
        # search string was empty, it still counts (found is false, but
        # highlighting will still work).
        if found or (webIndex == 0):
            # Select the entire line containing the anchor: make the page
            # temporarily editable, then press home then shift+end using `keyClick
            # <http://qt-project.org/doc/qt-4.8/qtest.html#keyClick>`_. Other ideas
            # on how to do this:
            #
            # #. The same idea, but done in Javascript. Playing with this produced
            #    a set of failures -- in a ``conteneditable`` area, I couldn't
            #    perform any edits by sending keypresses. The best reference I
            #    found for injecting keypresses was `this jsbin demo
            #    <http://stackoverflow.com/questions/10455626/keydown-simulation-in-chrome-fires-normally-but-not-the-correct-key/12522769#12522769>`_.
            oce = self._widget.webView.page().isContentEditable()
            self._widget.webView.page().setContentEditable(True)
            # If the find text ends with a newline, findText doesn't include
            # the newline. Manaully move one char forward in this case to get it.
            # This is tested in test_preview.py:test_sync10, test_sync11.
            if ft and ft[-1] == '\n':
                QTest.keyClick(self._widget.webView, Qt.Key_Right, Qt.ShiftModifier)
            QTest.keyClick(self._widget.webView, Qt.Key_Home)
            QTest.keyClick(self._widget.webView, Qt.Key_End, Qt.ShiftModifier)
            self._widget.webView.page().setContentEditable(oce)

            # Sync the cursors.
            self._scrollSync(True)

    # Other handlers
    ##==============
    def del_(self):
        """Uninstall themselves
        """
        # Uninstall the text-to-web sync only if it was installed in the first
        # place (it depends on TRE).
        if findApproxTextInTarget:
            self._cursorMovementTimer.stop()
        self._typingTimer.stop()
        self._thread.htmlReady.disconnect(self._setHtml)
        self._thread.stop_async()
        self._thread.wait()

    def closeEvent(self, event):
        """Widget is closed. Clear it
        """
        self.closed.emit()
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
            
        # Re-sync the re-loaded text.
        if findApproxTextInTarget:
            self._syncTextToPreview()

    def _onDocumentChanged(self, old, new):
        """Current document changed, update preview
        """
        if findApproxTextInTarget:
            # Switch connections to the current document.
            if old is not None:
                self.currentCursorPositionChanged.disconnect(self._onCursorPositionChanged)
            if new is not None:
                self.currentCursorPositionChanged = core.workspace().currentDocument().qutepart.cursorPositionChanged
                self.currentCursorPositionChanged.connect(self._onCursorPositionChanged)

        if new is not None:
            if new.qutepart.language() == 'Markdown':
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
            if language == 'Markdown':
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
