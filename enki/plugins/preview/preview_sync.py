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
# Library imports
# ---------------
from enum import Enum
#
# Third-party
# -----------
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QObject, QThread, \
    QFile, QIODevice, QEventLoop
from PyQt5 import QtGui
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineScript
import sip
#
# Local
# -----
from enki.core.core import core
from enki.lib.future import RunLatest

# If regex isn't installed or is too old, this import will fail. In this case,
# disable the sync feature.
try:
    pass
    # Approx matching is disabled because of issue #460
    # from .approx_match import findApproxTextInTarget
    findApproxTextInTarget = None
except ImportError as e:
    findApproxTextInTarget = None
#
# CallbackManager
# ===============
# Callbacks are a painful additon when porting from QWebKit to QWebEngine. Some operations, just as getting the HTML content of the page, return their value via a callback. Effectively, this is somewhat like a threaded (or, more correctly a multi-process) operation: Qt sends a request to the web engine process, which replies with the requested data. In the meantime, other code runs. When the requested data arrives, Qt invokes the callback. (Why didn't they use signals?) This leads to some challenges:
#
# #. The data the callback operates on may no longer be needed or relevant; for example, if a document was closed, a callback expecting to use the HTML text to synchronize with text in the current document will fail.
# #. When terminating a class, there's no way to know if any callbacks are pending. If they're called after the class terminates, failures will occur. Likewise, there's not way to wait until all callbacks have completed.
#
# As a solution, this class provides future-like behavior for callbacks: a CallbackFuture can be skipped (so that the callback it wraps won't be invoked, providing a way to deal with problem 1 above -- don't invoke callbacks that depend on out-of-date state) or waiting for (to avoid termination errors in problem 2 above). The CallbackManager keeps track of all pending callbacks.
#
# Example use:
#
# .. code:: Python
#   :number-lines:
#
#   def __init__(self):
#       self.cm = CallbackManager()
#
#   # This demonstrates wrapping a callback in a CallbackFuture.
#   def getPlainText(self):
#       # The parameter to ``toPlainText`` is a callback.
#       self.webEngineView.page().toPlainText(cm.callback(self.havePlainText))
#
#   def havePlainText(self, txt):
#       # Do something with txt.
#
#   def setNewHtml(self, html):
#       # Cancel any pending callbacks -- with new HTML, the plain text isn't correct.
#       self.cm.skipAllCallbacks()
#       self.webEngineView.page().setHtml(html)
#       # Run it again on the new HTML.
#       self.getPlainText()
#
#   def terminate(self):
#       # Cancel then wait for all callbacks to complete before terminating.
#       self.cm.skipAllCallbacks()
#       self.cm.waitAllCallbacks()
#
#
class CallbackFutureState(Enum):
    READY = 0
    WAITING = 1
    COMPLETE = 2
#
# CallbackFuture
# --------------
# A CallbackFuture keeps track of its state (if it's waiting for a callback; if the callback should be skipped).
#
# **Important**: This class is NOT thread-safe. Invoke all of its methods from a single thread.
class CallbackFuture:
    def __init__(self,
      # A CallbackManager instance to register with.
      callbackManager,
      # _`callbackToWrap`: The callback function to (optionally) invoke, which this future will wrap.
      callbackToWrap):

        self.callbackManager = callbackManager
        self._callbackToWrap = callbackToWrap
        self._state = CallbackFutureState.READY
        self._shouldInvokeCallback = True
        self._qEventLoop = None

    # Return the callback wrapper for this future and mark it as waiting.
    def callback(self):
        assert self._state == CallbackFutureState.READY, 'A callback may only be obtained once.'
        self._state = CallbackFutureState.WAITING
        self.callbackManager.add(self)
        return self._callbackWrapper

    # The callback wrapper. Update state, then invoke the wrapped callback.
    def _callbackWrapper(self, *args, **kwargs):
        assert self._state == CallbackFutureState.WAITING
        self._state = CallbackFutureState.COMPLETE
        self.callbackManager.remove(self)
        # If waiting for the callback, stop!
        if self._qEventLoop:
            self._qEventLoop.quit()
        if self._shouldInvokeCallback:
            self._callbackToWrap(*args, **kwargs)

    def skipCallback(self):
        assert self._state == CallbackFutureState.WAITING, 'Only callbacks being waited for may be skipped.'
        self._shouldInvokeCallback = False

    # Wait until the wrapped callback is completed (invoked or skipped).
    def waitForCallback(self):
        assert self._state == CallbackFutureState.WAITING, 'Only callbacks being waited for may be skipped.'
        # Run events until the callback is invoked.
        self._qEventLoop = QEventLoop()
        self._qEventLoop.exec_()
        self._qEventLoop = None
        assert self._state == CallbackFutureState.COMPLETE

class CallbackManager(set):
    def skipAllCallbacks(self):
        for item in self:
            item.skipCallback()

    def waitForAllCallbacks(self):
        while self:
            # Note: we can't iterate over items in the set, since removal of an item (such as a completed CallbackFuture) rasies ``RuntimeError: Set changed size during iteration``. Instead, wait one item in the set. (Don't wait on the rest, since they may no longer belong to the set). The following two lines gets one item from the set.
            for item in self:
                break
            # Wait on it.
            item.waitForCallback()

    # A convenience method: wrap a callback and return the wrapper.
    def callback(self,
      # See callbackToWrap_.
      callbackToInvoke):

        return CallbackFuture(self, callbackToInvoke).callback()
#
# PreviewSync
# ===========
class PreviewSync(QObject):
    """This class synchronizes the contents of the web and text views and aligns
       them vertically.
    """
    textToPreviewSynced = pyqtSignal()

    # Setup / cleanup
    # ===============
    def __init__(self,
      # The preview dock involved in synchronization.
      previewDock):

        QObject.__init__(self)
        # Only set up sync if fuzzy matching is available.
        if not findApproxTextInTarget:
            return

        # Gather into one variable all the JavaScript needed for PreviewSync.
        self._jsPreviewSync = self._jsOnClick + self._jsWebCursorCoords

        self._dock = previewDock
        self._callbackManager = CallbackManager()
        self._initPreviewToTextSync()
        self._initTextToPreviewSync()
        self._unitTest = False

    def terminate(self):
        # Uninstall the text-to-web sync only if it was installed in the first
        # place (it depends on TRE).
        if findApproxTextInTarget:
            self._cursorMovementTimer.stop()
            # Shut down the background sync. If a sync was already in progress,
            # then discard its output.
            self._runLatest.future.cancel(True)
            self._runLatest.terminate()
            # End all callbacks.
            self._callbackManager.skipAllCallbacks()
            self._callbackManager.waitForAllCallbacks()
            # Bug: DON'T de-register the QWebChannel. This casues the error message ``onmessage is not a callable property of qt.webChannelTransport. Some things might not work as expected.`` to be displayed. I see this in https://code.woboq.org/qt5/qtwebengine/src/core/renderer/web_channel_ipc_transport.cpp.html#221; I assume it's a result of attempting to send a signal to the web page, where the web page doesn't have qwebchannel.js running.
            #self.channel.deregisterObject(self)
            # Delete it. Note that the channel is `NOT owned by the page <http://doc.qt.io/qt-5/qwebenginepage.html#setWebChannel>`.
            sip.delete(self.channel)
            # Disconnect all signals.
            sip.delete(self)
    #
    # Vertical synchronization
    ##========================
    # These routines perform vertical synchronization.
    #
    # This function computes the distance, in pixels, measured from the target
    # cursor location to the source cursor location, as shown in part (a) of the
    # figure below: delta = source - target, so that source = target + delta.
    # This distance is limited by a constraint: the resulting target cursor
    # location must be kept a padding pixels amount away from the boundaries of
    # the target widget. Part (b) of the figure shows show this distance is
    # limited when the source lies above the target widget; the same constraint
    # applies when the source lies below the target widget.
    #
    # .. image:: sync_delta.png
    #
    # Ideally, this would instead operate on the baseline of the text, rather
    # than the bottom, but getting this is harder.
    def _alignScrollAmount(self,
      # The top (y) coordinate of the source widget in a global coordinate frame,
      # such as screen coordinates. In pixels.
      sourceGlobalTop,
      # The bottom coordinate of the cursor in the source widget, measured from the
      # top of the widget, NOT the top of the viewport. In pixels.
      sourceCursorBottom,

      # The top (y) coordinate of the target widget in a global coordinate frame,
      # such as screen coordinates. In pixels.
      targetGlobalTop,
      # The bottom coordinate of the cursor in the target widget, measured from the
      # top of the widget, NOT the top of the viewport. In pixels.
      targetCursorBottom,
      # The height of the target widget. In pixels.
      targetHeight,
      # The height of the cursor in the target widget. In pixels.
      targetCursorHeight,
      # The minimum allowable distance between target + delta and the top or
      # bottom of the target widget.
      padding):

        # Compute the raw delta between the source and target widgets.
        #
        # .. image:: dtop_initial_diagram.png
        delta = (
          # Global coords of the source cursor top.
          (sourceGlobalTop + sourceCursorBottom) -
          # Global coords of the target cursor top. The difference
          # gives the number of pixels separating them.
          (targetGlobalTop + targetCursorBottom) );

        # Constrain the resulting delta so that the stays padding pixels from
        # the top of the target widget.
        delta = max(-targetCursorBottom + targetCursorHeight + padding, delta)
        # Likewise, constrain the bottom.
        delta = min(targetHeight - targetCursorBottom - padding, delta)

        return delta

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
            'var rangeAtFocus = document.createRange();'
            'rangeAtFocus.setStart(selection.focusNode, selection.focusOffset);'

            # Insert a measurable element (a span) at the selection's
            # focus.
            'var span = document.createElement("span");'
            'rangeAtFocus.insertNode(span);'

            # Measure coordinates at this span, then remove it.
            'var [left, top] = findPos(span);'
            'var height = span.offsetHeight;'
            'span.remove();'

            'return [left, top, height];'
        '}'

        # Clear the current selection, if it exists.
        'function clearSelection() {'
            'if (window.getSelection()) {'
                'window.getSelection().empty();'
            '}'
        '}'

        # Given text to find, place a highlight on the last line containing the
        # text.
        'function highlightFind('
          # The text to find, typically consisting of all text in the web page
          # from its beginning to the point to be found.
          'txt) {'

            # Clear the current selection, so that a find will start at the
            # beginning of the page.
            'clearSelection();'
            # Find or create a ``div`` used as a highlighter.
            'var highlighter = getHighlight();'
            'if (!highlighter) {'
                'highlighter = document.createElement("div");'
                'document.body.appendChild(highlighter);'
                'highlighter.style.zIndex = 100;'
                'highlighter.style.width = "100%";'
                'highlighter.style.position = "absolute";'
                # Pass any click on the highlight on to the webpage underneath.
                # See https://developer.mozilla.org/en-US/docs/Web/CSS/pointer-events.
                'highlighter.style.pointerEvents = "none";'
                'highlighter.style.backgroundColor = "rgba(255, 255, 0, 0.4)";'
                'highlighter.id = "highlighter";'
            '}'
            # See https://developer.mozilla.org/en-US/docs/Web/API/Window/find.
            ##                       aString, aCaseSensitive, aBackwards, aWrapAround, aWholeWord, aSearchInFrames, aShowDialog)
            'var found = window.find(txt,     true,           false,     false,        false,      true,            false);'
            # If the text was found, or the search string was empty, highlight a line.
            'if (found || txt === "") {'
                # Determine the coordiantes of the end of the selection.
                'var res = selectionAnchorCoords();'
                'if (res) {'
                    # Unpack the coordinates obtained.
                    'var [left, top, height] = res;'
                    # Position it based on the coordinates.
                    'highlighter.style.height = height + "px";'
                    'highlighter.style.top = (window.scrollY + top) + "px";'
                '}'
                'return true;'
            '}'
            # Remove the highlight if we can't find the text.
            'clearHighlight();'
            # Clear the selection, since we won't use it later.
            'clearSelection();'
            'return false;'
        '}'

        # Return the ``div`` used to produce a highlight, or None if it doesn't exist.
        'function getHighlight() {'
            'return document.getElementById("highlighter");'
        '}'

        # Delete the element used to produce a highlight.
        'function clearHighlight() {'
            'var highlighter = getHighlight();'
            'if (highlighter) {'
                'highlighter.remove();'
            '}'
        '}')

    # Scroll the web view to align its cursor with the qutepart cursor or vice
    # versa.
    def _scrollSync(self,
      # None to scroll the text view to the y coordinate of the web view's
      # cursor. True or False to do the opposite: scroll the web view so that
      # its cursor aligns vertically with the y coordinate of the text view. In
      # this case, True will use the tolerance to scroll only if the amount to
      # scroll exceeds that tolerance; False will scroll irregardless of the
      # tolerance.
      alreadyScrolling=None,
      # Ignored if ``alreadyScrolling == None``. Used as both a padding value and a
      # scroll tolerance, as described in alreadyScrolling.
      tolerance=50):

        # Per the `window geometry
        # <http://qt-project.org/doc/qt-4.8/application-windows.html#window-geometry>`_,
        # `geometry() <http://qt-project.org/doc/qt-4.8/qwidget.html#geometry-prop>`_
        # is relative to the parent frame. Then, use `mapToGlobal
        # <http://qt-project.org/doc/qt-4.8/qwidget.html#mapToGlobal>`_ to
        # put this in global coordinates. This works for `QWebEngineView
        # <http://doc.qt.io/qt-5/qwebengineview.html>`_, since it
        # inherits from QWidget.
        wv = self._dock._widget.webEngineView
        qp = core.workspace().currentDocument().qutepart
        qpGlobalTop = qp.mapToGlobal(qp.geometry().topLeft()).y()
        wvGlobalTop = wv.mapToGlobal(wv.geometry().topLeft()).y()

        # `qutepart.cursorRect()
        # <http://qt-project.org/doc/qt-4.8/qplaintextedit.html#cursorRect-2>`_
        # gives a value in viewport == widget coordinates. Use that directly.
        cr = qp.cursorRect()
        qpCursorHeight = cr.height()
        qpCursorBottom = cr.top() + qpCursorHeight

        # Widget height includes the scrollbars. Subtract that off to get a
        # viewable height for qutepart.
        qpHeight = qp.geometry().height()
        hsb = qp.horizontalScrollBar()
        # The scrollbar height is a constant, even if it's hidden. So, only
        # include it in calculations if it's visible.
        if hsb.isVisible():
            qpHeight -= qp.horizontalScrollBar().height()
        page = wv.page()
        wvHeight = wv.geometry().height()

        # JavaScript callback to determine the coordinates and height of the
        # anchor of the selection in the web view. It expects a 3-element tuple
        # of (left, top, height), or None if there was no selection, where:
        # top is the coordinate (in pixels) of the top of the selection, measured from the web page's origin;
        # left is the coordinate (in pixels) of the left of the selection, measured from the web page's origin.
        def callback(res):
            # See if a 3-element tuple is returned. Exit if the selection was empty.
            if not res:
                return

            _, wvCursorTop, wvCursorHeight = res
            wvCursorBottom = wvCursorTop + wvCursorHeight

            if alreadyScrolling is not None:
                deltaY = self._alignScrollAmount(qpGlobalTop, qpCursorBottom,
                  wvGlobalTop, wvCursorBottom, wvHeight, wvCursorHeight, tolerance)
                # Uncomment for helpful debug info.
                ##print(("qpGlobalTop = %d, qpCursorBottom = %d, qpHeight = %d, deltaY = %d, tol = %d\n" +
                ##  "  wvGlobalTop = %d, wvCursorBottom = %d, wvHeight = %d, wvCursorHeight = %d") %
                ##  (qpGlobalTop, qpCursorBottom, qpHeight, deltaY, tolerance,
                ##  wvGlobalTop, wvCursorBottom, wvHeight, wvCursorHeight))

                # Only scroll if we've outside the tolerance.
                if alreadyScrolling or (abs(deltaY) > tolerance):
                    # Note that scroll bars are backwards: to make the text go up, you must
                    # move the bars down (a positive delta) and vice versa. Hence, the
                    # subtration, rather than addition, below.
                    page.runJavaScript('window.scrollTo(0, window.scrollY - {});'.format(deltaY))
                # Clear the selection, whether we scrolled or not.
                self.clearSelection()
            else:
                deltaY = self._alignScrollAmount(wvGlobalTop, wvCursorBottom,
                  qpGlobalTop, qpCursorBottom, qpHeight, qpCursorHeight, 0)
                vsb = qp.verticalScrollBar()
                # The units for the vertical scroll bar is pixels, not lines. So, do
                # a kludgy conversion by assuming that all line heights are the
                # same.
                vsb.setValue(vsb.value() - round(deltaY/qpCursorHeight))

        self._dock._afterLoaded.afterLoaded(lambda: page.runJavaScript('selectionAnchorCoords();', QWebEngineScript.ApplicationWorld, self._callbackManager.callback(callback)))

    # Clear the current selection in the web view.
    def clearSelection(self):
        if not self._unitTest:
            self._dock._afterLoaded.afterLoaded(self._dock._widget.webEngineView.page().runJavaScript, 'clearSelection();', QWebEngineScript.ApplicationWorld)
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
    # * `QWebEngineView`_ is the top-level widget used to embed a Web page in a Qt
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
    #
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
        'function window_onclick() {'

            # Clear the current highlight -- it doesn't make sense to have other
            # text highlighted after a click.
            'clearHighlight();'

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
             # Call Python with the document's text and that index.
            'window.previewSync._onWebviewClick(document.body.textContent.toString(), rStr.length);'
        '}')

    _qtJsInit = (
        # _`Bug 1`: I can't seem to avoid the error message ``js: Uncaught TypeError: channel.execCallbacks[message.id] is not a function``. It seems like this occurs  when a new page is loaded, but the QWebChannel on the Python side sends a message intended for a previously-loaded page. Adding delays / waiting until all JS init finishes / wiating until the event queue is empty helps, but doesn't fix it. Even with these, enough busyness (constant CPU use), this still happends -- perhaps the Python/Qt network backend doesn't send these messages until the CPU is idle? As a workaround, don't define the channel until is needed, making it less likely this will happen.
        #
        # _`Bug 2`: Since ``qt`` may not be defined (Qt 5.7.0 doesn't provide the
        # ``qt`` object to JavaScript when loading per https://bugreports.qt.io/browse/QTBUG-53411),
        # wrap it in a try/except block.
        'function init_qwebchannel() {'
            # Switch event listeners, part 1/2 -- now that this init is done, don't call it again.
            'window.removeEventListener("click", init_qwebchannel);'
            'try {'
                'new QWebChannel(qt.webChannelTransport, function(channel) {'
                    # Save a reference to the previewSync object.
                    'window.previewSync = channel.objects.previewSync;'
                    # Switch event listeners, part 2/2 -- Invoke the usual onclick handler. This will only be run if the QWebChannel init succeeds.
                    'window.addEventListener("click", window_onclick);'
                    # Now that the QWebChannel is ready, use it to handle the click.
                    'window_onclick();'
                '});'
            '} catch (err) {'
                # Re-throw unrecognized errors. When ``qt`` isn't defined,
                # JavaScript reports ``js: Uncaught ReferenceError: qt is not
                # defined``; this works around `bug 2`_.
                'throw err;' #if (!(err instanceof ReferenceError)) throw err;'
            '}'
        '}'
        # Set up the sync system after a click. This works around `bug 1`_. See https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener.
        'window.addEventListener("click", init_qwebchannel);'
    )

    def _initPreviewToTextSync(self):
        """Initialize the system per items 1, 2, and 4 above."""
        # When a web page finishes loading, reinsert our JavaScript.
        page = self._dock._widget.webEngineView.page()

        # Insert our scripts into every loaded page.
        qwebchannel_js = QFile(':/qtwebchannel/qwebchannel.js')
        if not qwebchannel_js.open(QIODevice.ReadOnly):
            raise SystemExit(
                'Failed to load qwebchannel.js with error: %s' %
                qwebchannel_js.errorString())
        qwebchannel_js = bytes(qwebchannel_js.readAll()).decode('utf-8')

        # Set up the QWebChannel. See http://doc.qt.io/qt-5/qtwebchannel-javascript.html.
        # Run the script containing QWebChannel.js first.
        beforeScript = QWebEngineScript()
        beforeScript.setSourceCode(qwebchannel_js + self._jsPreviewSync + self._qtJsInit)
        beforeScript.setName('qwebchannel.js, previewSync')
        # Run this JavaScript separated from any JavaScript present in the loaded web page. This provides better security (rogue pages can't access the QWebChannel) and better isolation (handlers, etc. won't conflict, I hope).
        beforeScript.setWorldId(QWebEngineScript.ApplicationWorld)
        beforeScript.setInjectionPoint(QWebEngineScript.DocumentCreation)
        # Per `setWebChannel <http://doc.qt.io/qt-5/qwebenginepage.html#setWebChannel>`_, only one channel is allowed per page. So, don't run this on sub-frames, since it will attempt the creation of more channels for each subframe.
        beforeScript.setRunsOnSubFrames(False)
        page.scripts().insert(beforeScript)

        # Set up the web channel. See https://riverbankcomputing.com/pipermail/pyqt/2015-August/036346.html
        # and http://stackoverflow.com/questions/28565254/how-to-use-qt-webengine-and-qwebchannel.
        # For debug, ``set QTWEBENGINE_REMOTE_DEBUGGING=port`` then browse to
        # http://127.0.0.1:port, where port=60000 works for me. See https://riverbankcomputing.com/pipermail/pyqt/2015-August/036346.html.
        self.channel = QWebChannel(page)
        self.channel.registerObject("previewSync", self)
        # Expose the ``qt.webChannelTransport`` object in the world where these scripts live.
        page.setWebChannel(self.channel, QWebEngineScript.ApplicationWorld)

    @pyqtSlot(str, int)
    def _onWebviewClick(self, tc, webIndex):
        self._onWebviewClick_(tc, webIndex)
        # Get the qutepart text.
        qp = core.workspace().currentDocument().qutepart
        # Perform an approximate match between the clicked webpage text and the
        # qutepart text.
        textIndex = findApproxTextInTarget(tc, webIndex, qp.text)
        # Move the cursor to textIndex in qutepart, assuming corresponding text
        # was found.
        if textIndex >= 0:
            self._moveTextPaneToIndex(textIndex)

    # Used for testing -- this will be replaced by a mock. Does nothing.
    def _onWebviewClick_(self, tc, webIndex):
        pass

    def _moveTextPaneToIndex(self, textIndex, noWebSync=True):
        """Given an index into the text pane, move the cursor to that index.

        Params:

        - textIndex - The index into the text pane at which to place the cursor.
        - noWebSync - True to prevent the web-to-text sync from running as a
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
        self._scrollSync()
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
        self._runLatest = RunLatest('QThread', self)
        self._runLatest.ac.defaultPriority = QThread.LowPriority
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)

    def _onDocumentChanged(self, old, new):
        self._runLatest.future.cancel(True)
        self._callbackManager.skipAllCallbacks()
        self._cursorMovementTimer.stop()

    def _onCursorPositionChanged(self):
        """Called when the cursor position in the text pane changes. It (re)schedules
        a text to web sync per item 2 above. Note that the signal connected to
        this slot must be updated when the current document changes, since we only
        want cursor movement notification from the active text document. This is
        handled in _onDocumentChanged.
        """
        # Ignore this callback if a preview to text sync caused it or if the
        # preview dock is closed.
        if not self._previewToTextSyncRunning and self._dock.isVisible():
            self._cursorMovementTimer.stop()
            self._cursorMovementTimer.start()

    def syncTextToPreview(self):
        """When the timer above expires, this is called to sync text to preview
        per item 3 above. It can also be called when a sync is needed (when
        switching windows, for example).
        """
        # Only run this if we TRE is installed.
        if not findApproxTextInTarget:
            return
        # Stop the timer; the next cursor movement will restart it.
        self._cursorMovementTimer.stop()
        # Get a plain text rendering of the web view. Continue execution in a callback.
        qp = core.workspace().currentDocument().qutepart
        qp_text = qp.text
        self._dock._widget.webEngineView.page().toPlainText(
            self._callbackManager.callback(self._havePlainText))

    # Perform an approximate match in a separate thread, then update
    # the cursor based on the match results.
    def _havePlainText(self, html_text):
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
        qp = core.workspace().currentDocument().qutepart
        qp_text = qp.text
        qp_position = qp.textCursor().position()
        self._runLatest.start(self._movePreviewPaneToIndex,
            # Call findApproxTextInTarget, returning the index and the HTML text searched.
            lambda: (findApproxTextInTarget(qp_text, qp_position, html_text), html_text))

    def _movePreviewPaneToIndex(self, future):
        """Highlights webIndex in the preview pane, per item 4 above.

        Params:

        - webIndex - The index to move the cursor / highlight to in the preview
          pane.
        - txt - The text of the webpage, returned by mainFrame.toPlainText().
        """
        # Retrieve the return value from findApproxTextInTarget.
        webIndex, txt = future.result

        view = self._dock._widget.webEngineView
        page = view.page()
        ft = txt[:webIndex]

        def callback(found):
            if found:
                # Sync the cursors.
                self._scrollSync(False)
                self.textToPreviewSynced.emit()

        if webIndex >= 0:
            self._dock._afterLoaded.afterLoaded(lambda: page.runJavaScript('highlightFind({});'.format(repr(ft)), QWebEngineScript.ApplicationWorld, self._callbackManager.callback(callback)))
        else:
            self.clearHighlight()

    def clearHighlight(self):
        self._dock._afterLoaded.afterLoaded(self._dock._widget.webEngineView.page().runJavaScript, 'clearHighlight();', QWebEngineScript.ApplicationWorld)
