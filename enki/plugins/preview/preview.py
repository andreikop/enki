# ********************************************
# preview.py - HTML, Markdown and ReST preview
# ********************************************
#
# Imports
# =======
# Library imports
# ---------------
import os.path
import io
import re
import shutil
import html
import sys
import shlex
import codecs
from queue import Queue
#
# Third-party imports
# -------------------
from PyQt5.QtCore import (pyqtSignal, Qt, QThread, QTimer, QUrl,
                          QEventLoop, QObject)
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt5.QtGui import QDesktopServices, QIcon, QPalette, QWheelEvent
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5 import uic
import sip
#
# Local imports
# -------------
from enki.core.core import core
from enki.widgets.dockwidget import DockWidget
from enki.plugins.preview import isHtmlFile, canUseCodeChat, \
    sphinxEnabledForFile
from .preview_sync import PreviewSync
from enki.lib.get_console_output import open_console_output
from enki.lib.future import AsyncController, RunLatest


# Attempt importing CodeChat; failing that, disable the CodeChat
# feature.
try:
    # Needed to access CodeChat.__file__; not importing this, but using the
    # other CodeChat.* imports below, doesn't define this.
    import CodeChat
except ImportError:
    CodeChat = None
    CodeToRest = None
else:
    import CodeChat.CodeToRest as CodeToRest


# Global functions
# ================
def copyTemplateFile(errors, source, templateFileName, dest, newName=None):
    """For each sphinx project, two files are needed: ``index.rst`` as master
    document, and ``conf.py`` as sphinx configuration file. Given a file with
    ``templateFileName``, it will be copied to destination directory ``dest``.
    If any error occurs during copy operation, error information will
    be appended to ``errors``.
    """
    if not source or not dest:
        raise OSError(2, "Input or output directory cannot be None", None)
    if not newName:
        newName = templateFileName
    if not os.path.exists(os.path.join(dest, newName)):
        sourcePath = os.path.join(source, templateFileName)
        try:
            shutil.copy(sourcePath, os.path.join(dest, newName))
        except (IOError, OSError) as why:
            errors.append((sourcePath, dest, str(why)))


def _checkModificationTime(sourceFile, outputFile, s):
    """Make sure the outputFile is newer than the sourceFile.
    Otherwise, return an error."""
    # Recall that time is measured in seconds since the epoch,
    # so that larger = newer.
    try:
        if os.path.getmtime(outputFile) > os.path.getmtime(sourceFile):
            return sourceFile, '', s, QUrl.fromLocalFile(outputFile)
        else:
            return (sourceFile, 'The file {} is older than the source file {}.'
                    .format(outputFile, sourceFile), s, QUrl())
    except OSError as e:
        return (sourceFile, 'Error checking modification time: {}'.format(str(e)),
                s, QUrl())
#
#
# Threaded members
# ----------------
# These functions and classes convert their input to HTML. They are executed in
# a separate thread.
def _convertMarkdown(text):
    """Convert Markdown to HTML
    """
    try:
        import markdown
    except ImportError:
        return 'Markdown preview requires <i>python3-markdown</i> package<br/>' \
               'Install it with your package manager or see ' \
               '<a href="http://packages.python.org/Markdown/install.html">installation instructions</a>'

    extensions = ['fenced_code', 'nl2br', 'tables', 'enki.plugins.preview.mdx_math']

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

    return markdown.markdown(text, extensions)


def _convertReST(text):
    try:
        import docutils.core
        import docutils.writers.html4css1
    except ImportError:
        return 'Restructured Text preview requires the <i>python-docutils</i> package.<br/>' \
               'Install it with your package manager or see ' \
               '<a href="http://pypi.python.org/pypi/docutils"/>this page.</a>', None

    errStream = io.StringIO()
    docutilsHtmlWriterPath = os.path.abspath(os.path.dirname(
      docutils.writers.html4css1.__file__))
    settingsDict = {
      # Make sure to use Unicode everywhere. This name comes from
      # ``docutils.core.publish_string`` version 0.12, lines 392 and following.
      'output_encoding': 'unicode',
      # While ``unicode`` **should** work for ``input_encoding``, it doesn't if
      # there's an ``.. include`` directive, since this encoding gets passed to
      # ``docutils.io.FileInput.__init__``, in which line 236 of version 0.12
      # tries to pass the ``unicode`` encoding to ``open``, producing:
      #
      # .. code:: python3
      #    :number-lines:
      #
      #    File "...\python-3.4.4\lib\site-packages\docutils\io.py", line 236, in __init__
      #      self.source = open(source_path, mode, **kwargs)
      #    LookupError: unknown encoding: unicode
      #
      # So, use UTF-8 and encode the string first. Ugh.
      'input_encoding' : 'utf-8',
      # Don't stop processing, no matter what.
      'halt_level'     : 5,
      # Capture errors to a string and return it.
      'warning_stream' : errStream,
      # On some Windows PC, docutils will complain that it can't find its
      # template or stylesheet. On other Windows PCs with the same setup, it
      # works fine. ??? So, specify a path to both here.
      'template': (
        os.path.join(docutilsHtmlWriterPath,
                     docutils.writers.html4css1.Writer.default_template) ),
      'stylesheet_dirs' : (
        docutilsHtmlWriterPath,
        os.path.join(os.path.abspath(os.path.dirname(
          os.path.realpath(__file__))), 'rst_templates')),
      'stylesheet_path' : 'default.css',
      }
    htmlString = docutils.core.publish_string(bytes(text, encoding='utf-8'),
      writer_name='html', settings_overrides=settingsDict)
    errString = errStream.getvalue()
    errStream.close()
    return htmlString, errString


def _convertCodeChat(text, filePath):
    # Use StringIO to pass CodeChat compilation information back to
    # the UI.
    errStream = io.StringIO()
    try:
        htmlString = CodeToRest.code_to_html_string(text, errStream,
                                                    filename=filePath)
    except KeyError:
        # Although the file extension may be in the list of supported
        # extensions, CodeChat may not support the lexer chosen by Pygments.
        # For example, a ``.v`` file may be Verilog (supported by CodeChat)
        # or Coq (not supported). In this case, provide an error messsage
        errStream.write('Error: this file is not supported by CodeChat.')
        htmlString = ''
    errString = errStream.getvalue()
    errStream.close()
    return filePath, htmlString, errString, QUrl()


class SphinxConverter(QObject):
    """This class converts Sphinx input to HTML. It is run in a separate
    thread.
    """
    # This signal clears the context of the log window.
    logWindowClear = pyqtSignal()

    # This signal emits messages for the log window.
    logWindowText = pyqtSignal(
      # A string to append to the log window.
      str)

    def __init__(self, parent):
        super().__init__(parent)
        # Use an additional thread to process Sphinx output.
        self._ac = AsyncController('QThread', self)
        self._ac.defaultPriority = QThread.LowPriority
        self._SphinxInvocationCount = 1

    def terminate(self):
        # Free resources.
        self._ac.terminate()

    def convert(self, filePath):
        # Run the builder.
        errString = self._runHtmlBuilder()

        # Look for the HTML output.
        #
        sourcePath = core.config()['Sphinx']['SourcePath']
        outputPath = core.config()['Sphinx']['OutputPath']
        projectPath = core.config()['Sphinx']['ProjectPath']
        # Get an absolute path to the output path and source path, which could be relative.
        if not os.path.isabs(sourcePath):
            sourcePath = os.path.join(projectPath, sourcePath)
        if not os.path.isabs(outputPath):
            outputPath = os.path.join(projectPath, outputPath)
        # Given ``filePath = sourcePath / path to source file``, we want to compute ``htmlPath = outputPath / path to source file``.
        htmlPath = os.path.join(outputPath, os.path.relpath(filePath, sourcePath))
        html_file_suffix = '.html'
        try:
            with codecs.open(os.path.join(projectPath, 'sphinx-enki-info.txt')) as f:
                hfs = f.read()
                # If the file is empty, then html_file_suffix wasn't defined
                # or is None. In this case, use the default extension.
                # Otherwise, use the extension read from the file.
                if hfs:
                    html_file_suffix = hfs
        except:
            errString = "Warning: assuming .html extension. Use " + \
                "the conf.py template to set the extension.\n" + errString
            pass
        # First place to look: file.html. For example, look for foo.py
        # in foo.py.html.
        htmlFile = htmlPath + html_file_suffix
        # Second place to look: file without extension.html. For
        # example, look for foo.html for foo.rst.
        htmlFileAlter = os.path.splitext(htmlPath)[0] + html_file_suffix
        # Check that the output file produced by Sphinx is newer than
        # the source file it was built from.
        if os.path.exists(htmlFile):
            return _checkModificationTime(filePath, htmlFile, errString)
        elif os.path.exists(htmlFileAlter):
            return _checkModificationTime(filePath, htmlFileAlter, errString)
        else:
            return (filePath, 'No preview for this type of file.<br>Expected ' +
                    htmlFile + " or " + htmlFileAlter, errString, QUrl())

    def _runHtmlBuilder(self):
        # Build the commond line for Sphinx.
        if core.config()['Sphinx']['AdvancedMode']:
            htmlBuilderCommandLine = core.config()['Sphinx']['Cmdline']
            if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
                # If Linux is used, then subprocess cannot take the whole
                # commandline as the name of an executable file. Module shlex
                # has to be used to parse commandline.
                htmlBuilderCommandLine = shlex.split(htmlBuilderCommandLine)
        else:
            # For available builder options, refer to: http://sphinx-doc.org/builders.html
            htmlBuilderCommandLine = [core.config()['Sphinx']['Executable'],
              # Place doctrees in the ``_build`` directory; by default, Sphinx
              # places this in _build/html/.doctrees.
              '-d', os.path.join('_build', 'doctrees'),
              # Source directory -- the current directory, since we'll chdir to
              # the project directory before executing this.
              core.config()['Sphinx']['SourcePath'],
              # Build directory
              core.config()['Sphinx']['OutputPath']]

        # Invoke it.
        try:
            # Clear the log at the beginning of a Sphinx build.
            self.logWindowClear.emit()

            cwd = core.config()['Sphinx']['ProjectPath']
            # If the command line is already a string (advanced mode), just print it.
            # Otherwise, it's a list that should be transformed to a string.
            if isinstance(htmlBuilderCommandLine, str):
                htmlBuilderCommandLineStr = htmlBuilderCommandLine
            else:
                htmlBuilderCommandLineStr = ' '.join(htmlBuilderCommandLine)
            self.logWindowText.emit('{} : {}\n\n'.format(cwd,
                                                         htmlBuilderCommandLineStr))

            # Sphinx will output just a carriage return (0x0D) to simulate a
            # single line being updated by build status and the build
            # progresses. Without universal newline support here, we'll wait
            # until the build is complete (with a \n\r) to report any build
            # progress! So, enable universal newlines, so that each \r will be
            # treated as a separate line, providing immediate feedback on build
            # progress.
            popen = open_console_output(htmlBuilderCommandLine, cwd=cwd,
                                        universal_newlines=True)
            # Read are blocking; we can't read from both stdout and stderr in the
            # same thread without possible buffer overflows. So, use this thread to
            # read from and immediately report progress from stdout. In another
            # thread, read all stderr and report that after the build finishes.
            q = Queue()
            self._ac.start(None, self._stderr_read, popen.stderr, q)
            self._popen_read(popen.stdout)
            # Wait until stderr has completed (stdout is already done).
            stderr_out = q.get()
        except OSError as ex:
            return (
                'Failed to execute HTML builder:\n'
                '{}\n'.format(str(ex)) +
                'Go to Settings -> Settings -> Sphinx to set HTML'
                ' builder configurations.')

        return stderr_out

    # Read from stdout (in this thread) and stderr (in another thread),
    # so that the user sees output as the build progresses, rather than only
    # producing output after the build is complete.
    def _popen_read(self, stdout):
        # Read a line of stdout then report it to the user immediately.
        s = stdout.readline()
        while s:
            self.logWindowText.emit(s.rstrip('\n'))
            s = stdout.readline()
        self._SphinxInvocationCount += 1
        # I would expect the following code to do the same thing. It doesn't:
        # instead, it waits until Sphinx completes before returning anything.
        # ???
        #
        # .. code-block: python
        #    :linenos:
        #
        #    for s in stdout:
        #        self.logWindowText.emit(s)

    # Runs in a separate thread to read stdout. It then exits the QEventLoop as
    # a way to signal that stderr reads have completed.
    def _stderr_read(self, stderr, q):
        q.put(stderr.read())
#
# QWebEngineView tweak
# ====================
# This class opens links in an external browser, instead of in the built-in browser.
class QWebEnginePageExtLink(QWebEnginePage):
    def acceptNavigationRequest(self, url, navigationType, isMainFrame):
        # Only open a link externally if the user clicked on it.
        #
        # The following HTML produces navigationType == 0 (link clicked) and
        # isMainFrame == False. (This makes no sense to me). So, only open main frame clicks  in an external browser.
        ## <a class="reference external image-reference" href="https://pypi.python.org/pypi/PyInstaller"><object data="https://img.shields.io/pypi/v/PyInstaller.svg" type="image/svg+xml">https://img.shields.io/pypi/v/PyInstaller.svg</object></a>
        if (navigationType == QWebEnginePage.NavigationTypeLinkClicked and isMainFrame):
            res = QDesktopServices.openUrl(url)
            if res:
                core.mainWindow().statusBar().showMessage("{} opened in a browser".format(url.toString()), 2000)
            else:
                core.mainWindow().statusBar().showMessage("Failed to open {}".format(url.toString()), 2000)

            # Tell the built-in browser not to handle this.
            return False
        else:
            # Handle this in the built-in browser.
            return True
#
# AfterLoaded
# ===========
# Run functions after the web page is loaded. This avoids errors such as  ``js: Uncaught ReferenceError: clearHighlight is not defined``, which (I think) occurs when JavaScript is run before the PreviewSync window is able to inject its JavaScript.
class AfterLoaded(QObject):
    def __init__(self,
      # The QWebEnginePage to watch for loading/load complete.
      webEnginePage):

        super().__init__()
        self._runList = []
        self._isLoading = False
        webEnginePage.loadStarted.connect(self.onLoadStarted)
        webEnginePage.loadFinished.connect(self.onLoadFinished)

    def terminate(self):
        self.clearAll()
        # Ensure that all signals are disconnected, so that waiting callbacks won't be invoked after this class is terminated.
        sip.delete(self)

    def onLoadStarted(self):
        self._isLoading = True

    def onLoadFinished(self, ok):
        self._isLoading = False
        self._runAll()

    # Schedule a funtion to be executed after the web page is finished loading. If the web page has already been loaded, it will execute immediately. Use: ``al.afterLoaded(func_name, param1, param2, ..., kwarg1=kwval1, kwarg2=kwval2, ...)`` will invoke ``func_name(param1, param2, ..., kwarg1=kwval1, kwarg2=kwval2, ...)``. Note that the return values of the functions are discarded.
    def afterLoaded(self, *args, **kwargs):
        self._runList.append([kwargs, *args])
        if not self._isLoading:
            self._runAll()

    def _runAll(self):
        while self._runList:
            kwargs, func, *args = self._runList.pop(0)
            func(*args, **kwargs)

    # Unschedule all functions scheduled to run, but not yet run.
    def clearAll(self):
        self._runList.clear()
#
# Core class
# ==========
class PreviewDock(DockWidget):
    """GUI and implementation
    """
    # Emitted when this window is closed.
    closed = pyqtSignal()

    def __init__(self):
        DockWidget.__init__(self, core.mainWindow(), "Previe&w", QIcon(':/enkiicons/internet.png'), "Alt+W")

        self._widget = self._createWidget()
        # Don't need to schedule document processing; a call to show() does.

        self._afterLoaded = AfterLoaded(self._widget.webEngineView.page())

        self._loadTemplates()
        self._widget.cbTemplate.currentIndexChanged.connect(
            self._onCurrentTemplateChanged)

        # When quitting this program, don't rebuild when closing all open
        # documents. This can take a long time, particularly if a some of the
        # documents are associated with a Sphinx project.
        self._programRunning = True
        core.aboutToTerminate.connect(self._quitingApplication)

        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)

        # If the user presses the accept button in the setting dialog, Enki
        # will force a rebuild of the whole project.
        #
        # TODO: only build if preview settings have been changed.
        #
        # In order to make this happen, let ``_onSettingsDialogAboutToExecute`` emit
        # a signal indicating that the CodeChat setting dialog has been opened. Save
        # core.config()['Sphinx'] and core.config()['CodeChat']. After dialogAccepted
        # is detected, compare current settings with the old one. Build if necessary.
        core.uiSettingsManager().dialogAccepted.connect(
            self._scheduleDocumentProcessing)

        core.workspace().modificationChanged.connect(
            self._onDocumentModificationChanged)

        self._scrollPos = {}
        self._vAtEnd = {}
        self._hAtEnd = {}

        # Keep track of which Sphinx template copies we've already asked the user about.
        self._sphinxTemplateCheckIgnoreList = []

        self._sphinxConverter = SphinxConverter(self)  # stopped
        self._runLatest = RunLatest('QThread', parent=self)

        self._visiblePath = None

        # If we update Preview on every key press, freezes are noticable (the
        # GUI thread draws the preview too slowly).
        # This timer is used for drawing Preview 800 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(800)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self.previewSync = PreviewSync(self)

        self._applyJavaScriptEnabled(self._isJavaScriptEnabled())

        # Clear flags used to temporarily disable signals during
        # ``_scheduleDocumentProcessing.``.
        self._ignoreDocumentChanged = False
        self._ignoreTextChanges = False

        # Provide an inital value for the rebuild needed flag.
        self._rebuildNeeded = False

        # Save the initial font, then restore it after a ``clear``. Note that
        # ``clear()`` doesn't reset the `currentCharFormat
        # <http://doc.qt.io/qt-4.8/qplaintextedit.html#currentCharFormat>`_. In
        # fact, clicking in red (error/warning) message in the log window
        # changes the current font to red! So, save it here so that it will be
        # restored correctly on a ``_clear_log``.
        self._defaultLogFont = self._widget.teLog.currentCharFormat()
        # The logWindowClear signal clears the log window.
        self._sphinxConverter.logWindowClear.connect(self._clear_log)
        # The logWindowText signal simply appends text to the log window.
        self._sphinxConverter.logWindowText.connect(lambda s:
                                           self._widget.teLog.appendPlainText(s))

    def _createWidget(self):
        widget = QWidget(self)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Preview.ui'), widget)
        widget.layout().setContentsMargins(0, 0, 0, 0)
        # The Qt Designer doesn't support a QWebEngineView. Also, we need to
        # add a subclass, which also isn't supported. Add it manually.
        widget.webEngineView = QWebEngineView(widget)
        widget.webView.layout().addWidget(widget.webEngineView)
        # Use our custom subclass for the web page; use the web view as its
        # parent.
        webEnginePage = QWebEnginePageExtLink(widget.webEngineView)
        widget.webEngineView.setPage(webEnginePage)
        # Fix preview palette. See https://github.com/bjones1/enki/issues/34
        webEngineViewPalette = widget.webEngineView.palette()
        webEngineViewPalette.setColor(QPalette.Inactive, QPalette.HighlightedText,
                                webEngineViewPalette.color(QPalette.Text))
        widget.webEngineView.setPalette(webEngineViewPalette)

        widget.webEngineView.page().titleChanged.connect(
            self._updateTitle)
        widget.cbEnableJavascript.clicked.connect(
            self._onJavaScriptEnabledCheckbox)
        widget.webEngineView.installEventFilter(self)

        self.setWidget(widget)
        self.setFocusProxy(widget.webEngineView)

        widget.tbSave.clicked.connect(self.onPreviewSave)
        # Add an attribute to ``widget`` denoting the splitter location.
        # This value will be overwritten when the user changes splitter location.
        widget.splitterErrorStateSize = (199, 50)
        widget.splitterNormStateSize = (1, 0)
        widget.splitterNormState = True
        widget.splitter.setSizes(widget.splitterNormStateSize)
        widget.splitter.splitterMoved.connect(self.on_splitterMoved)

        return widget

    def _quitingApplication(self):
        self._programRunning = False

    def on_splitterMoved(self, pos, index):
        if self._widget.splitterNormState:
            self._widget.splitterNormStateSize = self._widget.splitter.sizes()
        else:
            self._widget.splitterErrorStateSize = self._widget.splitter.sizes()

    def terminate(self):
        """Uninstall themselves
        """
        self._typingTimer.stop()
        self.previewSync.terminate()
        self._sphinxConverter.terminate()
        self._runLatest.terminate()
        self._afterLoaded.terminate()
        sip.delete(self)

    def closeEvent(self, event):
        """Widget is closed. Clear it
        """
        self.closed.emit()
        self._clear()
        return DockWidget.closeEvent(self, event)

    def _clear_log(self):
        """Clear the log window and reset the default font."""
        self._widget.teLog.clear()
        self._widget.teLog.setCurrentCharFormat(self._defaultLogFont)

    def eventFilter(self, obj, ev):
        """Event filter for the web view
        Zooms the web view
        """
        if isinstance(ev, QWheelEvent) and \
           ev.modifiers() == Qt.ControlModifier:
            multiplier = 1 + (0.1 * (ev.angleDelta().y() / 120.))
            view = self._widget.webEngineView
            view.setZoomFactor(view.zoomFactor() * multiplier)
            return True
        else:
            return DockWidget.eventFilter(self, obj, ev)

    def _onDocumentModificationChanged(self, document, modified):
        if not modified:  # probably has been saved just now
            if not self._ignoreDocumentChanged:
                self._scheduleDocumentProcessing()

    def _updateTitle(self, pageTitle):
        """Web page title changed. Update own title.
        """
        if pageTitle:
            self.setWindowTitle("Previe&w - " + pageTitle)
        else:
            self.setWindowTitle("Previe&w")

    def _saveScrollPos(self):
        """Save scroll bar position for document
        """
        page = self._widget.webEngineView.page()
        self._scrollPos[self._visiblePath] = page.scrollPosition()

    def _restoreScrollPos(self, ok):
        """Restore scroll bar position for document
        """
        try:
            self._widget.webEngineView.page().loadFinished.disconnect(self._restoreScrollPos)
        except TypeError:  # already has been disconnected
            pass

        if core.workspace().currentDocument() is None:
            return  # nothing to restore if don't have document

        if not self._visiblePath in self._scrollPos:
            return  # no data for this document

        # Don't restore the scroll position if the window is hidden. This can
        # happen when the current document is changed, which invokes _clear,
        # which calls setHtml, which calls _saveScrollPos and then this routine
        # when the HTML is loaded.
        if not self.isVisible():
            return

        page = self._widget.webEngineView.page()
        pos = self._scrollPos[self._visiblePath]
        # Odd: this works, too. Evidently, the load finishing doesn't mean the
        # render is finished. But, the JavaScript below won't be run until the
        # render finishes. However, since this might lead to a race condition
        # (what if the render finishes before this code runs), avoid this
        # shortcut.
        ##pos = page.scrollPosition()
        # We can't use view.scroll because it doesn't affect the web view's
        # scroll bars -- instead, it will move the widget around, which isn't
        # helpful.
        page.runJavaScript('window.scrollTo({}, {});'.format(pos.x(), pos.y()))

        # Re-sync the re-loaded text.
        self.previewSync.syncTextToPreview()

    def _onDocumentChanged(self, old, new):
        """Current document changed, update preview
        """
        self._typingTimer.stop()
        if new is not None:
            if new.qutepart.language() == 'Markdown':
                self._widget.cbTemplate.show()
                self._widget.lTemplate.show()
            else:
                self._widget.cbTemplate.hide()
                self._widget.lTemplate.hide()

            # We can't rely on ``self.isVisible()`` here: on startup, it returns False even though the widget is visible, probably because the widget hasn't yet been painted.
            if core.config()['Preview']['Enabled']:
                self._clear()
                self._scheduleDocumentProcessing()

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

        return str(self._widget.cbTemplate.itemData(index))

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
            QMessageBox.information(
                core.mainWindow(),
                'Custom templaes help',
                '<html>See <a href="https://github.com/andreikop/enki/wiki/Markdown-preview-templates">'
                'this</a> wiki page for information about custom templates')
            self._restorePreviousTemplate()

        core.config()['Preview']['Template'] = self._widget.cbTemplate.currentText()
        core.config().flush()
        self._scheduleDocumentProcessing()

    def _onTextChanged(self, document):
        """Text changed, update preview
        """
        if self.isVisible() and not self._ignoreTextChanges:
            self._typingTimer.stop()
            self._typingTimer.start()

    def show(self):
        """When shown, update document, if possible.
        """
        DockWidget.show(self)
        self._scheduleDocumentProcessing()

    def _clear(self):
        """Clear the preview dock contents.
        Might be necesssary to stop executing JS and loading data.
        """
        self._setHtml('', '', None, QUrl())

    def _isJavaScriptEnabled(self):
        """Check if JS is enabled in the settings.
        """
        return core.config()['Preview']['JavaScriptEnabled']

    def _onJavaScriptEnabledCheckbox(self, enabled):
        """Checkbox clicked, save and apply settings
        """
        core.config()['Preview']['JavaScriptEnabled'] = enabled
        core.config().flush()

        self._applyJavaScriptEnabled(enabled)

    def _applyJavaScriptEnabled(self, enabled):
        """Update QwebEngineView settings and QCheckBox state
        """
        self._widget.cbEnableJavascript.setChecked(enabled)

        settings = self._widget.webEngineView.settings()
        settings.setAttribute(settings.JavascriptEnabled, enabled)

    def onPreviewSave(self):
        """Save contents of the preview pane to a user-specified file."""
        path, _ = QFileDialog.getSaveFileName(self, 'Save Preview as HTML', filter='HTML (*.html)')

        if path:
            self._previewSave(path)

    def _previewSave(self, path):
        qe = QEventLoop()

        def callback(text):
            try:
                with open(path, 'w', encoding='utf-8') as openedFile:
                    openedFile.write(text)
            except (OSError, IOError) as ex:
                QMessageBox.critical(self, "Failed to save HTML", str(ex))
            qe.quit()

        # The preview selection is an extra ``div`` inserted by the sync code.
        # Remove it before saving the file.
        self.previewSync.clearHighlight()
        self._afterLoaded.afterLoaded(self._widget.webEngineView.page().toHtml, callback)
        # Wait for the callback to complete.
        qe.exec_()

    # HTML generation
    #----------------
    # The following methods all support generation of HTML from text in the
    # Qutepart window in a separate thread.
    def _scheduleDocumentProcessing(self):
        """Start document processing with the thread.
        """
        if not self._programRunning:
            return

        if self.isHidden():
            return

        self._typingTimer.stop()

        document = core.workspace().currentDocument()
        if document is not None:
            if sphinxEnabledForFile(document.filePath()):
                self._copySphinxProjectTemplate(document.filePath())
            qp = document.qutepart
            language = qp.language()
            text = qp.text
            sphinxCanProcess = sphinxEnabledForFile(document.filePath())
            # Determine if we're in the middle of a build.
            currentlyBuilding = self._widget.prgStatus.text() == 'Building...'

            if language == 'Markdown':
                text = self._getCurrentTemplate() + text
                # Hide the progress bar, since processing is usually short and
                # Markdown produces no errors or warnings to display in the
                # progress bar. See https://github.com/bjones1/enki/issues/36.
                self._widget.prgStatus.setVisible(False)
                # Hide the error log, since Markdown never generates errors or
                # warnings.
                self._widget.teLog.setVisible(False)
            elif isHtmlFile(document):
                # No processing needed -- just display it.
                self._setHtml(document.filePath(), text, None, QUrl())
                # Hide the progress bar, since no processing is necessary.
                self._widget.prgStatus.setVisible(False)
                # Hide the error log, since we do not HTML checking.
                self._widget.teLog.setVisible(False)
                return
            elif ((language == 'reStructuredText') or sphinxCanProcess or
                  canUseCodeChat(document.filePath())):
                # Show the progress bar and error log for reST, CodeChat, or
                # Sphinx builds. It will display progress (Sphinx only) and
                # errors/warnings (for all three).
                self._widget.prgStatus.setVisible(True)
                self._widget.teLog.setVisible(True)
                self._setHtmlProgress('Building...')

            # Determine whether to initiate a build or not. The underlying
            # logic:
            #
            # - If Sphinx can't process this file, just build it.
            # - If Sphinx can process this file:
            #
            #   - If the document isn't internally modified, we're here because
            #     the file was saved or the refresh button was pressed. Build it.
            #   - If the document was internally modified and "insta-build" is
            #     enabled (i.e. build only on save is disabled):
            #
            #     - If the document was not externally modified, then save and
            #       build.
            #     - If the document was externally modified, DANGER! The user
            #       needs to decide which file wins (external changes or
            #       internal changes). Don't save and build, since this would
            #       overwrite external modifications without the user realizing
            #       what happened. Instead, warn the user.
            #
            # As a table, see below. Build, Save, and Warn are the outputs; all
            # others are inputs.
            #
            # ==================  ===================  ===================  =============  =====  ====  ====
            # Sphinx can process  Internally modified  Externally modified  Build on Save  Build  Save  Warn
            # ==================  ===================  ===================  =============  =====  ====  ====
            # No                  X                    X                    X              Yes    No    No
            # Yes                 No                   X                    X              Yes    No    No
            # Yes                 Yes                  No                   No             Yes    Yes   No
            # Yes                 Yes                  Yes                  No             No     No    Yes
            # Yes                 Yes                  X                    Yes            No     No    No
            # ==================  ===================  ===================  =============  =====  ====  ====
            internallyModified = qp.document().isModified()
            externallyModified = document.isExternallyModified()
            buildOnSave = core.config()['Sphinx']['BuildOnSave']
            saveThenBuild = (sphinxCanProcess and internallyModified and
                             not externallyModified and not buildOnSave)
            # If Sphinx is currently building, don't autosave -- this can
            # cause Sphinx to miss changes on its next build. Instead, wait
            # until Sphinx completes, then do a save and build.
            if saveThenBuild and currentlyBuilding:
                self._rebuildNeeded = True
                saveThenBuild = False
            else:
                self._rebuildNeeded = False
            # Save first, if needed.
            if saveThenBuild:
                # If trailing whitespace strip changes the cursor position,
                # restore the whitespace and cursor position.
                lineNum, col = qp.cursorPosition
                lineText = qp.lines[lineNum]
                # Invoking saveFile when Strip Trailing whitespace is enabled
                # causes ``onTextChanged`` (due to whitespace strips) and
                # ``onDocumentChanged`` signals to be emitted. These both
                # re-invoke this routine, causing a double build. So, ignore
                # both these signals.
                self._ignoreDocumentChanged = True
                self._ignoreTextChanges = True
                document.saveFile()
                self._ignoreDocumentChanged = False
                self._ignoreTextChanges = False
                if qp.cursorPosition != (lineNum, col):
                    # Mark this as one operation on the undo stack. To do so,
                    # enclose all editing operations in a context manager. See
                    # "Text modification and Undo/Redo" in the qutepart docs.
                    with qp:
                        qp.lines[lineNum] = lineText
                        qp.cursorPosition = lineNum, col
                    qp.document().setModified(False)
            # Build. Each line is one row in the table above.
            if ((not sphinxCanProcess) or
                    (sphinxCanProcess and not internallyModified) or
                    saveThenBuild):
                # Build the HTML in a separate thread.
                self._runLatest.start(self._setHtmlFuture, self.getHtml,
                                language, text, document.filePath())
            # Warn.
            if (sphinxCanProcess and internallyModified and
                    externallyModified and not buildOnSave):
                core.mainWindow().appendMessage('Warning: file modified externally. Auto-save disabled.')

    def getHtml(self, language, text, filePath):
        """Get HTML for document. This is run in a separate thread.
        """
        if language == 'Markdown':
            return filePath, _convertMarkdown(text), None, QUrl()
        # For ReST, use docutils only if Sphinx isn't available.
        elif language == 'reStructuredText' and not sphinxEnabledForFile(filePath):
            htmlUnicode, errString = _convertReST(text)
            return filePath, htmlUnicode, errString, QUrl()
        elif filePath and sphinxEnabledForFile(filePath):  # Use Sphinx to generate the HTML if possible.
            return self._sphinxConverter.convert(filePath)
        elif filePath and canUseCodeChat(filePath):  # Otherwise, fall back to using CodeChat+docutils.
            return _convertCodeChat(text, filePath)
        else:
            return filePath, 'No preview for this type of file', None, QUrl()

    def _copySphinxProjectTemplate(self, documentFilePath):
        """Add conf.py, CodeChat.css and index.rst (if ther're missing)
        to the Sphinx project directory.
        """
        if core.config()['Sphinx']['ProjectPath'] in self._sphinxTemplateCheckIgnoreList:
            return

        # Check for the existance Sphinx project files. Copy skeleton versions
        # of them to the project if necessary.
        sphinxPluginsPath = os.path.dirname(os.path.realpath(__file__))
        sphinxTemplatePath = os.path.join(sphinxPluginsPath, 'sphinx_templates')
        sphinxProjectPath = core.config()['Sphinx']['ProjectPath']
        errors = []
        checklist = ['index.rst', 'conf.py']
        if core.config()['CodeChat']['Enabled'] and CodeChat:
            checklist.append('CodeChat.css')
        missinglist = []
        for filename in checklist:
            if not os.path.exists(os.path.join(sphinxProjectPath, filename)):
                missinglist.append(filename)
        if not missinglist:
            return errors

        # For testing, check for test-provided button presses
        if ((len(self._sphinxTemplateCheckIgnoreList) == 1) and
                isinstance(self._sphinxTemplateCheckIgnoreList[0], QMessageBox.StandardButton)):
            res = self._sphinxTemplateCheckIgnoreList[0]
        else:
            res = QMessageBox.warning(
                self,
                r"Enki",
                "Sphinx project at:\n " +
                sphinxProjectPath +
                "\nis missing the template file(s): " +
                ' '.join(missinglist) +
                ". Auto-generate those file(s)?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes)
        if res != QMessageBox.Yes:
            if res == QMessageBox.No:
                self._sphinxTemplateCheckIgnoreList.append(sphinxProjectPath)
            return

        if core.config()['CodeChat']['Enabled'] and CodeChat:
            codeChatPluginsPath = os.path.dirname(os.path.realpath(CodeChat.__file__))
            codeChatTemplatePath = os.path.join(codeChatPluginsPath, 'template')
            copyTemplateFile(errors, codeChatTemplatePath, 'index.rst', sphinxProjectPath)
            copyTemplateFile(errors, codeChatTemplatePath, 'conf.py', sphinxProjectPath)
            copyTemplateFile(errors, codeChatTemplatePath, 'CodeChat.css', sphinxProjectPath)
        else:
            copyTemplateFile(errors, sphinxTemplatePath, 'index.rst', sphinxProjectPath)
            copyTemplateFile(errors, sphinxTemplatePath, 'conf.py', sphinxProjectPath)

        errInfo = ""
        for error in errors:
            errInfo += "Copy from " + error[0] + " to " + error[1] + " caused error " + error[2] + ';\n'
        if errInfo:
            QMessageBox.warning(self, "Sphinx template file copy error",
                                "Copy template project files failed. The following errors are returned:<br>"
                                + errInfo)

        return errors

    def _setHtmlFuture(self, future):
        """Receives a future and unpacks the result, calling _setHtml."""
        filePath, htmlText, errString, baseUrl = future.result
        self._setHtml(filePath, htmlText, errString, baseUrl)

    def _setHtml(self, filePath, htmlText, errString, baseUrl):
        """Set HTML to the view and restore scroll bars position.
        Called by the thread.
        """
        self._saveScrollPos()
        self._visiblePath = filePath
        self._widget.webEngineView.page().loadFinished.connect(
            self._restoreScrollPos)

        # Per http://stackoverflow.com/questions/36609489/how-to-prevent-qwebengineview-to-grab-focus-on-sethtml-and-load-calls,
        # the QWebEngineView steals the focus on a call to ``setHtml``. Disable
        # it to prevent this. Another approach:  disable `QWebEngineSettings::FocusOnNavigationEnabled <http://doc.qt.io/qt-5/qwebenginesettings.html#WebAttribute-enum>`_, which is enabled by default. However, since this was added in Qt 5.8 (PyQt 5.8 was `released in 15-Feb-2017 <https://www.riverbankcomputing.com/news>`_, it's too early to rely on it. TODO: use this after PyQt 5.9 is released?
        self._widget.webEngineView.setEnabled(False)
        if baseUrl.isEmpty():
            # Clear the log, then update it with build content.
            self._widget.teLog.clear()
            self._widget.webEngineView.setHtml(htmlText,
                                         baseUrl=QUrl.fromLocalFile(filePath))
        else:
            self._widget.webEngineView.setUrl(baseUrl)
        # Let the sync know that the contents have changed.
        # Re-enable it after updating the HTML.
        self._widget.webEngineView.setEnabled(True)

        # If there were messages from the conversion process, extract a count of
        # errors and warnings from these messages.
        if errString:
            # If there are errors/warnings, expand log window to make it visible
            if self._widget.splitterNormState:
                self._widget.splitterNormStateSize = self._widget.splitter.sizes()
                self._widget.splitterNormState = False
            self._widget.splitter.setSizes(self._widget.splitterErrorStateSize)

            # This code parses the error string to determine get the number of
            # warnings and errors. Common docutils error messages read::
            #
            #  <string>:1589: (ERROR/3) Unknown interpreted text role "ref".
            #
            #  X:\ode.py:docstring of sympy:5: (ERROR/3) Unexpected indentation.
            #
            # and common sphinx errors read::
            #
            #  X:\SVM_train.m.rst:2: SEVERE: Title overline & underline mismatch.
            #
            #  X:\indexs.rst:None: WARNING: image file not readable: a.jpg
            #
            #  X:\conf.py.rst:: WARNING: document isn't included in any toctree
            #
            #  In Sphinx 1.6.1:
            #  X:\file.rst: WARNING: document isn't included in any toctree
            #
            # Each error/warning occupies one line. The following `regular
            # expression
            # <https://docs.python.org/2/library/re.html#regular-expression-syntax>`_
            # is designed to find the error position (1589/None) and message
            # type (ERROR/WARNING/SEVERE). Extra spaces are added to show which
            # parts of the example string it matches. For more details about
            # Python regular expressions, refer to the
            # `re docs <https://docs.python.org/2/library/re.html>`_.
            #
            # Examining this expression one element at a time::
            #
            #   <string>:1589:        (ERROR/3)Unknown interpreted text role "ref".
            errPosRe = r':(\d*|None|):? '
            # Find the first occurence of a pair of colons, or just a single colon.
            # Between them there can be numbers or "None" or nothing. For example,
            # this expression matches the string ":1589:" or string ":None:" or
            # string "::" or the string ":". Next::
            #
            #   <string>:1589:        (ERROR/3)Unknown interpreted text role "ref".
            errTypeRe = r'\(?(WARNING|ERROR|SEVERE)'
            # Next match the error type, which can
            # only be "WARNING", "ERROR" or "SEVERE". Before this error type the
            # message may optionally contain one left parenthesis.
            #
            errEolRe = '.*$'
            # Since one error message occupies one line, a ``*``
            # quantifier is used along with end-of-line ``$`` to make sure only
            # the first match is used in each line.
            #
            # TODO: Is this necesary? Is there any case where omitting this
            # causes a failure?
            regex = re.compile(errPosRe + errTypeRe + errEolRe,
                               # The message usually contain multiple lines; search each line
                               # for errors and warnings.
                               re.MULTILINE)
            # Use findall to return all matches in the message, not just the
            # first.
            result = regex.findall(errString)

            # The variable ``result`` now contains a list of tuples, where each
            # tuples contains the two matched groups (line number, error_string).
            # For example::
            #
            #  [('1589', 'ERROR')]
            #
            # Therefeore, the second element of each tuple, represented as x[1],
            # is the error_string. The next two lines of code will collect all
            # ERRORs/SEVEREs and WARNINGs found in the error_string separately.
            errNum = sum([x[1] == 'ERROR' or x[1] == 'SEVERE' for x in result])
            warningNum = [x[1] for x in result].count('WARNING')
            # Report these results this to the user.
            status = 'Error(s): {}, warning(s): {}'.format(errNum, warningNum)
            # Since the error string might contain characters such as ">" and "<",
            # they need to be converted to "&gt;" and "&lt;" such that
            # they can be displayed correctly in the log window as HTML strings.
            # This step is handled by ``html.escape``.
            self._widget.teLog.appendHtml("<pre><font color='red'>\n" +
                                          html.escape(errString) +
                                          '</font></pre>')
            # Update the progress bar.
            color = 'red' if errNum else '#FF9955' if warningNum else None
            self._setHtmlProgress(status, color)
        else:
            # If there are no errors/warnings, collapse the log window (can mannually
            # expand it back to visible)
            if not self._widget.splitterNormState:
                self._widget.splitterErrorStateSize = self._widget.splitter.sizes()
                self._widget.splitterNormState = True
            self._widget.splitter.setSizes(self._widget.splitterNormStateSize)
            self._setHtmlProgress('Error(s): 0, warning(s): 0')

        # Do a rebuild if needed.
        if self._rebuildNeeded:
            self._rebuildNeeded = False
            self._scheduleDocumentProcessing()

    def _setHtmlProgress(self, text, color=None):
        """Set progress label.
        """
        if color:
            style = 'QLabel { background-color: ' + color + '; }'
        else:
            style = style = 'QLabel {}'
        self._widget.prgStatus.setStyleSheet(style)
        self._widget.prgStatus.setText(text)

