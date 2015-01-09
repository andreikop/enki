# .. -*- coding: utf-8 -*-
#
# **********************************************************************
# preview_sync.py - Synchronize between text and web views of a document
# **********************************************************************
# With this module, cursor movement and mouse clicks in either view scroll to
# and highlight the corresponding text in the other view. In addition, the text
# is vertically synchronized: the y coordinate at which the last cursor movement
# or mouse click occurred will show the same text in both views.
#
# Imports
# =======
# Comment out one of the two following lines to enable or disable profiling
# of text to web sync.
#from time import time
#import cProfile
cProfile = None
# Third-party
# -----------
from PyQt4.QtCore import pyqtSignal, QPoint, Qt, QTimer, QObject, QThread
from PyQt4 import QtGui
from PyQt4.QtWebKit import QWebPage
from PyQt4.QtTest import QTest

# Local
# -----
from enki.core.core import core
from enki.lib.future import AsyncController

# If TRE isn't installed, this import will fail. In this case, disable the sync
# feature.
try:
    from approx_match import findApproxTextInTarget
except ImportError as e:
    findApproxTextInTarget = None

# PreviewSync
# ===========
class PreviewSync(QObject):
    """This class synchronizes the contents of the web and text views and aligns
       them vertically.
    """
    textToPreviewSynced = pyqtSignal()
    # Setup / cleanup
    ##===============
    def __init__(self,
      # The web view involved in synchronization
      webView):

        QObject.__init__(self)
        # Only set up sync if TRE is installed.
        if not findApproxTextInTarget:
            return

        # Gather into one variable all the JavaScript needed for PreviewSync.
        self._jsPreviewSync = self._jsOnClick + self._jsWebCursorCoords

        self.webView = webView
        self._initPreviewToTextSync()
        self._initTextToPreviewSync()
        if cProfile:
            self._pr = cProfile.Profile()

    def _onJavaScriptCleared(self):
        """This is called before starting a new load of a web page, to inject the
           JavaScript needed for PreviewSync."""
        mf = self.webView.page().mainFrame()
        # Use `addToJavaScriptWindowObject
        # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#addToJavaScriptWindowObject>`_
        # to make this PreviewDock object known to JavaScript, so that
        # JavaScript can emit the ``jsClick`` signal defined by PreviewDock.
        mf.addToJavaScriptWindowObject("PyPreviewDock", self)
        # Use `evaluateJavaScript
        # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebframe.html#evaluateJavaScript>`_
        # to insert JavaScript needed by PreviewSync.
        res = mf.evaluateJavaScript(self._jsPreviewSync)
        # Make sure no errors were returned; the result should be empty.
        assert not res

    def del_(self):
        # Uninstall the text-to-web sync only if it was installed in the first
        # place (it depends on TRE).
        if cProfile:
            self._pr.print_stats('cumtime')
        if findApproxTextInTarget:
            self._cursorMovementTimer.stop()
            core.workspace().cursorPositionChanged.disconnect(
              self._onCursorPositionChanged)
            core.workspace().currentDocumentChanged.disconnect(
              self._onDocumentChanged)
            # Shut down the background sync. If a sync was already in progress,
            # then discard its output, since that output might not come until
            # after this routine finishes and this class is not usable. Adding
            # the True guarentees that _movePreviewPaneToIndex will not be
            # invoked after this line.
            self._future.cancel(True)
            self._ac.del_()

    # Vertical synchronization
    ##========================
    # These routines perform vertical synchronization.
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

    # This string contains JavaScript code to determine the coordinates and height of the
    # anchor of the selection in the web view.
    _jsWebCursorCoords = (
        # This function returns the [top, left] position in pixels of ``obj``
        # relative to the screen, not to the viewport. This introduces one
        # potential problem: if obj is not visible when this is called, it
        # returns coordinates outside the screen (such that top or left is
        # negative or greater than the screen's height or width.
        #
        # It was slightly modified from http://www.quirksmode.org/js/findpos.html,
        #  which reproduces jQuery's offset method (https://api.jquery.com/offset/).
        'function findPos(obj) {'
            'var curLeft = 0;'
            'var curTop = 0;'
             # element.offsetLeft and element.offsetTop measure relative to
             # the object's parent. Walk the tree of parents, summing each
             # offset to determine the offset from the origin of the web page.
            'do {'
                'curLeft += obj.offsetLeft;'
                'curTop += obj.offsetTop;'
            '} while (obj = obj.offsetParent);'
            # See `element.getBoundingClientRect
            # <https://developer.mozilla.org/en-US/docs/Web/API/element.getBoundingClientRect>`_
            # for converting viewport coords to screen coords.
            'return [curLeft - window.scrollX, curTop - window.scrollY];'
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
        'function selectionAnchorCoords() {'
            # Using ``window.getSelection()``
            # Make sure a `selection <https://developer.mozilla.org/en-US/docs/Web/API/Selection>`_ exists.
            'var selection = window.getSelection();'
            'if (selection.rangeCount == 0) return 0;'

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
            'rangeAtFocus = document.createRange();'
            'rangeAtFocus.setStart(selection.focusNode, selection.focusOffset);'

            # Insert a measurable element (a span) at the selection's
            # focus.
            'var span = document.createElement("span");'
            'rangeAtFocus.insertNode(span);'

            # Measure coordinates at this span, then remove it. Note:
            # span.remove() isn't supported in the PyQt 4 I'm running, hence
            # the longer syntax below.
            'ret = findPos(span);'
            'height = span.offsetHeight;'
            'span.parentNode.removeChild(span);'

            ## Return      top,   left, height.
            'return    [ret[0], ret[1], height];'
        '}')

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
        res = self.webView.page().mainFrame(). \
          evaluateJavaScript('selectionAnchorCoords();')
        # See if a 3-element tuple is returned. Null is returned if the
        # selection is empty.
        if not res:
            return None
        left, top, height = res
        return top, height

    # Scroll the web view to align its cursor with the qutepart cursor or vice
    # versa.
    def _scrollSync(self,
      # True to scroll the web view so that its cursor aligns vertically with
      # the y coordinate of the text view. False to do the opposite: scroll the
      # text view to the y coordinate of the web view's cursor.
      doTextToWebSync):

        # Per the `window geometry
        # <http://qt-project.org/doc/qt-4.8/application-windows.html#window-geometry>`_,
        # `geometry() <http://qt-project.org/doc/qt-4.8/qwidget.html#geometry-prop>`_
        # is relative to the parent frame. Then, use `mapToGlobal
        # <http://qt-project.org/doc/qt-4.8/qwidget.html#mapToGlobal>`_ to
        # put this in global coordinates. This works for `QWebView
        # <http://qt-project.org/doc/qt-5.0/qtwebkit/qwebview.html>`_, since it
        # inherits from QWidget.
        wv = self.webView
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
    #    This signal is `connected <onJavaScriptCleared.connect>`_ to the
    #    ``onWebviewClick`` slot.
    # #. The ``onJavaScriptCleared`` method inserts the JavaScript to listen for a
    #    click and then emit a signal giving the click's location.
    # #. The ``onWebviewClick`` method then performs the approximate match and
    #    updates the text pane's cursor location.
    # #. When a new web page is loaded, all JavaScript is lost and must be reinserted.
    #    The ``onJavaScriptCleared`` slot, connected to the
    #    ``javaScriptWindowObjectCleared`` signal, does this.

    # The job of this JavaScript handler is to
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
    _jsOnClick = (
        # The `window.onclick
        # <https://developer.mozilla.org/en-US/docs/Web/API/Window.onclick>`_
        # event is "called when the user clicks the mouse button while the
        # cursor is in the window." Although the docs claim that "this event
        # is fired for any mouse button pressed", I found experimentally
        # that it on fires on a left-click release; middle and right clicks
        # had no effect.
        'window.onclick = function () {'

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
            'var r = window.getSelection().getRangeAt(0).cloneRange();'

             # This performs step 2 above: the cloned range is now changed
             # to contain the web page from its beginning to the point where
             # the user clicked by calling `setStartBefore
             # <https://developer.mozilla.org/en-US/docs/Web/API/Range.setStartBefore>`_
             # on `document.body
             # <https://developer.mozilla.org/en-US/docs/Web/API/document.body>`_.
            'r.setStartBefore(document.body);'

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
             'var rStr = r.cloneContents().textContent.toString();'

             # Step 4: the length of the string gives the index of the click
             # into a string containing a text rendering of the webpage.
             # Emit a signal with that information.
            'PyPreviewDock.jsClick(rStr.length);'
        '};')

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
        self.webView.page().mainFrame(). \
          javaScriptWindowObjectCleared.connect(self._onJavaScriptCleared)

    def _webTextContent(self):
        """Return the ``textContent`` of the entire web page. This differs from
        ``mainFrame().toPlainText()``, which uses ``innerText`` and therefore
        produces a slightly differnt result. Since the JavaScript signal's index
        is computed based on textContent, that must be used for all web to text
        sync operations.
        """
        return (self.webView.page().mainFrame().
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
        self._cursorMovementTimer.timeout.connect(self.syncTextToPreview)
        # Restart this timer every time the cursor moves.
        core.workspace().cursorPositionChanged.connect(self._onCursorPositionChanged)
        # Set up a variable to tell us when the preview to text sync just fired,
        # disabling this sync. Otherwise, that sync would trigger this sync,
        # which is unnecessary.
        self._previewToTextSyncRunning = False
        # Run the approximate match in a separate thread. Cancel it if the
        # document changes.
        self._ac = AsyncController('QThread')
        self._ac.defaultPriority = QThread.LowPriority
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        # Create a dummy future object for use in canceling pending sync jobs
        # when a new sync needs to be run.
        self._future = self._ac.start(lambda future: None, lambda: None)

    def _onDocumentChanged(self, old, new):
        self._future.cancel(True)

    def _onCursorPositionChanged(self):
        """Called when the cursor position in the text pane changes. It (re)schedules
        a text to web sync per item 2 above. Note that the signal connected to
        this slot must be updated when the current document changes, since we only
        want cursor movement notification from the active text document. This is
        handled in _onDocumentChanged.
        """
        # Ignore this callback if a preview to text sync caused it or if the
        # preview dock is closed.
        if (not self._previewToTextSyncRunning and
          core.config()['Preview']['Enabled']):
            self._cursorMovementTimer.stop()
            self._cursorMovementTimer.start()

    def syncTextToPreview(self):
        """When the timer above expires, this is called to sync text to preview
        per item 3 above. It can also be called when a sync is needed (when
        switching windows, for example).
        """
        if cProfile:
            self._pr.enable()
            self._startTime = time()
        # Only run this if we TRE is installed.
        if not findApproxTextInTarget:
            return
        # Stop the timer; the next cursor movement will restart it.
        self._cursorMovementTimer.stop()
        # Perform an approximate match in a separate thread, then update
        # the cursor based on the match results.
        mf = self.webView.page().mainFrame()
        qp = core.workspace().currentDocument().qutepart
        txt = mf.toPlainText()
        # Before starting a new sync job, cancel pending ones.
        self._future.cancel(True)
        # Performance notes: findApproxTextInTarget is REALLY slow. Scrolling
        # through preview.py with profiling enabled produced::
        #
        #  Output from Enki:
        #         41130 function calls in 3.642 seconds
        #
        #   Ordered by: standard name
        #
        #   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        #       13    0.000    0.000    0.000    0.000 __init__.py:406(text)
        #       13    0.000    0.000    3.398    0.261 approx_match.py:138(findApproxText)
        #       13    0.000    0.000    3.432    0.264 approx_match.py:175(findApproxTextInTarget)
        #       13    0.029    0.002    0.034    0.003 approx_match.py:252(refineSearchResult)
        #       26    0.000    0.000    0.000    0.000 core.py:177(workspace)
        #       ...snip lots more 0.000 or very small times...
        #
        # Therefore, finding ways to make this faster or run it in another
        # thread should significantly improve the GUI's responsiveness.
        self._future = self._ac.start(self._movePreviewPaneToIndex,
                       findApproxTextInTarget, qp.text,
                       qp.textCursor().position(), txt)
        if cProfile:
            print('Time before: ' + str(time() - self._startTime))

    def _movePreviewPaneToIndex(self, future):
        """Highlights webIndex in the preview pane, per item 4 above.

        Params:
        webIndex - The index to move the cursor / highlight to in the preview
          pane.
        txt - The text of the webpage, returned by mainFrame.toPlainText().
        """
        if cProfile:
            print('Time between: ' + str(time() - self._startTime))
            self._startTime = time()
        # Retrieve the return value from findApproxTextInTarget.
        webIndex = future.result
        # Only move the cursor to webIndex in the preview pane if
        # corresponding text was found.
        if webIndex < 0:
            return

        # Implementation: there's no direct way I know of to move the cursor in
        # a web page. However, the find operation is fairly common. So, simply
        # search from the beginning of the page for a substring of the web
        # page's text rendering from the beginning to webIndex. Then press home
        # followed by shift+end to select the line the cursor is on. (This
        # relies on the page being editable, which is set in
        # _initTextToPreviewSync).
        pg = self.webView.page()
        # Start the search location at the beginning of the document by clearing
        # the previous selection using `findText
        # <http://qt-project.org/doc/qt-4.8/qwebpage.html#findText>`_ with an
        # empty search string.
        pg.findText('')
        # Find the index with findText_.
        txt = pg.mainFrame().toPlainText()
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
            # #. The same idea, but done in JavaScript. Playing with this produced
            #    a set of failures -- in a ``conteneditable`` area, I couldn't
            #    perform any edits by sending keypresses. The best reference I
            #    found for injecting keypresses was `this jsbin demo
            #    <http://stackoverflow.com/questions/10455626/keydown-simulation-in-chrome-fires-normally-but-not-the-correct-key/12522769#12522769>`_.
            ice = pg.isContentEditable()
            pg.setContentEditable(True)
            # If the find text ends with a newline, findText doesn't include
            # the newline. Manaully move one char forward in this case to get it.
            # This is tested in test_preview.py:test_sync10, test_sync11.
            if ft and ft[-1] == '\n':
                QTest.keyClick(self.webView, Qt.Key_Right, Qt.ShiftModifier)
            QTest.keyClick(self.webView, Qt.Key_Home)
            QTest.keyClick(self.webView, Qt.Key_End, Qt.ShiftModifier)
            pg.setContentEditable(ice)

            # Sync the cursors.
            self._scrollSync(True)
            self.textToPreviewSynced.emit()
            if cProfile:
                self._pr.disable()
                print('Time after: ' + str(time() - self._startTime))
