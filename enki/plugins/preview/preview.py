# .. -*- coding: utf-8 -*-
#
# ********************************************
# preview.py - HTML, Markdown and ReST preview
# ********************************************
#
# Imports
# =======
# Library imports
# ---------------
import os.path
import collections
import Queue
import StringIO
import traceback
import re
import shutil
import cgi
import sys
import shlex
import codecs

from PyQt4.QtCore import pyqtSignal, QSize, Qt, QThread, QTimer, QUrl
from PyQt4.QtGui import QDesktopServices, QFileDialog, QIcon, QMessageBox, QWidget, QPalette, QWheelEvent
from PyQt4.QtWebKit import QWebPage
from PyQt4 import uic

from enki.core.core import core
from enki.widgets.dockwidget import DockWidget
from enki.plugins.preview import isHtmlFile, canUseCodeChat, \
    sphinxEnabledForFile
from preview_sync import PreviewSync
from enki.lib.get_console_output import get_console_output


# Likewise, attempt importing CodeChat; failing that, disable the CodeChat feature.
try:
    # Needed to access CodeChat.__file__; not importing this, but using the
    # other CodeChat.* imports below, doesn't define this.
    import CodeChat
except ImportError:
    CodeChat = None
    CodeToRest = None
else:
    import CodeChat.CodeToRest as CodeToRest


# Determine if we're frozen with Pyinstaller or not.
if getattr(sys, 'frozen', False):
    isFrozen = True
else:
    isFrozen = False


def copyTemplateFile(errors, source, templateFileName, dest, newName=None):
    """For each sphinx project, two files are needed: ``index.rst``as master
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


class ConverterThread(QThread):
    """Thread converts markdown to HTML.
    """

    # This signal is emitted by the converter thread when a file has been
    # converted to HTML.
    htmlReady = pyqtSignal(
      # Path to the file which should be converted to / displayed as HTML.
      unicode,
      # HTML rendering of the file; empty if the HTML is provided in a file
      # specified by the URL below.
      unicode,
      # Error text resulting from the conversion process.
      unicode,
      # A reference to a file containing HTML rendering. Empty if the second
      # parameter above contains the HTML instead.
      QUrl)

    _Task = collections.namedtuple("Task", ["filePath", "language", "text"])

    def __init__(self):
        QThread.__init__(self)
        self._queue = Queue.Queue()
        self.start(QThread.LowPriority)

    def process(self, filePath, language, text):
        """Convert data and emit result.
        """
        self._queue.put(self._Task(filePath, language, text))

    def stop_async(self):
        self._queue.put(None)

    def _getHtml(self, language, text, filePath):
        """Get HTML for document
        """
        if language == 'Markdown':
            return self._convertMarkdown(text), None, QUrl()
        # For ReST, use docutils only if Sphinx isn't available.
        elif language == 'Restructured Text' and not sphinxEnabledForFile(filePath):
            htmlUnicode, errString = self._convertReST(text)
            return htmlUnicode, errString, QUrl()
        elif filePath and sphinxEnabledForFile(filePath):  # Use Sphinx to generate the HTML if possible.
            return self._convertSphinx(filePath)
        elif filePath and canUseCodeChat(filePath):  # Otherwise, fall back to using CodeChat+docutils.
            return self._convertCodeChat(text, filePath)
        else:
            return 'No preview for this type of file', None, QUrl()

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

        extensions = ['fenced_code', 'nl2br', 'tables']

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
            return markdown.markdown(text, extensions + ['mathjax'])
        except (ImportError, ValueError):  # markdown raises ValueError or ImportError, depends on version
                                           # it is not clear, how to distinguish missing mathjax from other errors
            return markdown.markdown(text, extensions) #keep going without mathjax

    def _convertReST(self, text):
        """Convert ReST
        """
        try:
            import docutils.core
            import docutils.writers.html4css1
        except ImportError:
            return 'Restructured Text preview requires the <i>python-docutils</i> package.<br/>' \
                   'Install it with your package manager or see ' \
                   '<a href="http://pypi.python.org/pypi/docutils"/>this page.</a>', None

        errStream = StringIO.StringIO()
        settingsDict = {
          # Make sure to use Unicode everywhere.
          'output_encoding': 'unicode',
          'input_encoding' : 'unicode',
          # Don't stop processing, no matter what.
          'halt_level'     : 5,
          # Capture errors to a string and return it.
          'warning_stream' : errStream }
        # Frozen-specific settings.
        if isFrozen:
            settingsDict['template'] = (
              # The default docutils stylesheet and template uses a relative path,
              # which doesn't work when frozen ???. Under Unix when not frozen,
              # it produces:
              # ``IOError: [Errno 2] No such file or directory:
              # '/usr/lib/python2.7/dist-packages/docutils/writers/html4css1/template.txt'``.
              os.path.join(os.path.dirname(docutils.writers.html4css1.__file__),
                           docutils.writers.html4css1.Writer.default_template) )
            settingsDict['stylesheet_dirs'] = ['.',
              os.path.dirname(docutils.writers.html4css1.__file__)]
        htmlString = docutils.core.publish_string(text, writer_name='html',
                                                  settings_overrides=settingsDict)
        errString = errStream.getvalue()
        if errString:
            errString = "<font color='red'>" + cgi.escape(errString) + '</font>'
        errStream.close()
        return htmlString, errString

    def _convertSphinx(self, filePath):
        def checkModificationTime(sourceFile, outputFile, s):
            """Make sure the outputFile is newer than the sourceFile.
            Otherwise, return an error."""
            # Recall that time is measured in seconds since the epoch,
            # so that larger = newer.
            try:
                if os.path.getmtime(outputFile) > os.path.getmtime(sourceFile):
                    return u'', s, QUrl.fromLocalFile(outputFile)
                else:
                    return ('The file {} is older than the source file {}.'
                            .format(outputFile, sourceFile), s, QUrl())
            except OSError as e:
                return ('Error checking modification time: {}'.format(str(e)),
                        s, QUrl())
        # Run the builder.
        errString = self._runHtmlBuilder()

        # Look for the HTML output.
        #
        # Get an absolute path to the output path, which could be relative.
        outputPath = core.config()['Sphinx']['OutputPath']
        projectPath = core.config()['Sphinx']['ProjectPath']
        if not os.path.isabs(outputPath):
            outputPath = os.path.join(projectPath, outputPath)
        # Create an htmlPath as OutputPath + remainder of filePath.
        htmlPath = os.path.join(outputPath + filePath[len(projectPath):])
        html_file_suffix = u'.html'
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
            return checkModificationTime(filePath, htmlFile, errString)
        elif os.path.exists(htmlFileAlter):
            return checkModificationTime(filePath, htmlFileAlter, errString)
        else:
            return ('No preview for this type of file.<br>Expect ' +
                    htmlFile + " or " + htmlFileAlter, errString, QUrl())

    def _convertCodeChat(self, text, filePath):
        # Use StringIO to pass CodeChat compilation information back to
        # the UI.
        errStream = StringIO.StringIO()
        fileName, fileExtension = os.path.splitext(filePath)
        lexer = CodeToRest.get_lexer(filename=filePath)
        htmlString = CodeToRest.code_to_html_string(text, errStream, lexer=lexer)
        # Since the error string might contain characters such as ">" and "<",
        # they need to be converted to "&gt;" and "&lt;" such that
        # they can be displayed correctly in the log window as html strings.
        # This step is handled by ``cgi.escape``.
        errString = errStream.getvalue()
        if errString:
            errString = "<font color='red'>" + cgi.escape(errString) + '</font>'
        errStream.close()
        return htmlString, errString, QUrl()

    def _runHtmlBuilder(self):
        # Build the commond line for Sphinx.
        if core.config()['Sphinx']['AdvancedMode']:
            htmlBuilderCommandLine = core.config()['Sphinx']['Cmdline']
            if sys.platform.startswith('linux'):
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
              '.',
              # Build directory
              core.config()['Sphinx']['OutputPath']]

        # Invoke it.
        try:
            cwd = core.config()['Sphinx']['ProjectPath']
            # If the command line is already a string (advanced mode), just print it.
            # Otherwise, it's a list that should be transformed to a string.
            if isinstance(htmlBuilderCommandLine, str):
                htmlBuilderCommandLineStr = htmlBuilderCommandLine
            else:
                htmlBuilderCommandLineStr = ' '.join(htmlBuilderCommandLine)
            s = '<pre>{} : {}\n\n'.format(cwd, htmlBuilderCommandLineStr)
            stdout, stderr = get_console_output(htmlBuilderCommandLine,
                                                cwd=cwd)
        except OSError as ex:
            return s + '<font color=red>Failed to execute HTML builder:\n' + \
                   '{}\n'.format(str(ex)) + \
                   'Go to Settings -> Settings -> CodeChat to set HTML builder configurations.</pre>'

        return s + cgi.escape(stdout) + '<br><font color=red>' + cgi.escape(stderr) + '</font></pre>'

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

            # TODO: This is ugly. Should pass this exception back to the main
            # thread and re-raise it there, or use a QFuture like approach which
            # does this automaticlaly.
            try:
                html, errString, url = self._getHtml(task.language, task.text, task.filePath)
            except Exception:
                traceback.print_exc()

            if not self._queue.qsize():  # Do not emit results, if having new task
                self.htmlReady.emit(task.filePath, html, errString, url)


class PreviewDock(DockWidget):
    """GUI and implementation
    """
    closed = pyqtSignal()
    # Sent when the _setHtml methods completes.
    setHtmlDone = pyqtSignal()

    def __init__(self):
        DockWidget.__init__(self, core.mainWindow(), "Previe&w", QIcon(':/enkiicons/internet.png'), "Alt+W")

        self._widget = self._createWidget()
        # Don't need to schedule document processing; a call to show() does.

        self._loadTemplates()
        self._widget.cbTemplate.currentIndexChanged.connect(
          self._onCurrentTemplateChanged) # Disconnected.

        # When quitting this program, don't rebuild when closing all open
        # documents. This can take a long time, particularly if a some of the
        # documents are associated with a Sphinx project.
        self._programRunning = True
        core.aboutToTerminate.connect(self._quitingApplication) # Disconnected.

        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged) # Disconnected.
        core.workspace().textChanged.connect(self._onTextChanged) # Disconnected.

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
          self._scheduleDocumentProcessing) # Disconnected.

        core.workspace().modificationChanged.connect(
          self._onDocumentModificationChanged) # disconnected

        self._scrollPos = {}
        self._vAtEnd = {}
        self._hAtEnd = {}

        # Keep track of which Sphinx template copies we've already asked the user about.
        self._sphinxTemplateCheckIgnoreList = []

        self._thread = ConverterThread() # stopped
        self._thread.htmlReady.connect(self._setHtml) # disconnected

        self._visiblePath = None

        # If we update Preview on every key press, freezes are noticable (the
        # GUI thread draws the preview too slowly).
        # This timer is used for drawing Preview 800 ms After user has stopped typing text
        self._typingTimer = QTimer() # stopped.
        self._typingTimer.setInterval(800)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing) # Disconnected.

        self.previewSync = PreviewSync(self._widget.webView) # del_ called

        self._applyJavaScriptEnabled(self._isJavaScriptEnabled())

    def _createWidget(self):
        widget = QWidget(self)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Preview.ui'), widget)
        widget.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        widget.webView.page().linkClicked.connect(self._onLinkClicked) # Disconnected.
        # Fix preview palette. See https://github.com/bjones1/enki/issues/34
        webViewPalette = widget.webView.palette()
        webViewPalette.setColor(QPalette.Inactive, QPalette.HighlightedText,
                                webViewPalette.color(QPalette.Text))
        widget.webView.setPalette(webViewPalette)

        widget.webView.page().mainFrame().titleChanged.connect(
          self._updateTitle) # Disconnected.
        widget.cbEnableJavascript.clicked.connect(
          self._onJavaScriptEnabledCheckbox) # Disconnected.
        widget.webView.installEventFilter(self)

        self.setWidget(widget)
        self.setFocusProxy(widget.webView)

        widget.tbSave.clicked.connect(self.onPreviewSave) # Disconnected.
        # Add an attribute to ``widget`` denoting the splitter location.
        # This value will be overwritten when the user changes splitter location.
        widget.splitterErrorStateSize = (199,50)
        widget.splitterNormStateSize = (1,0)
        widget.splitterNormState = True
        widget.splitter.setSizes(widget.splitterNormStateSize)
        widget.splitter.splitterMoved.connect(self.on_splitterMoved) # Disconnected.

        return widget


    def _quitingApplication(self):
        self._programRunning = False

    def on_splitterMoved(self, pos, index):
        if self._widget.splitterNormState:
            self._widget.splitterNormStateSize = self._widget.splitter.sizes()
        else:
            self._widget.splitterErrorStateSize = self._widget.splitter.sizes()

    def del_(self):
        """Uninstall themselves
        """
        self._typingTimer.stop()
        self._typingTimer.timeout.disconnect(self._scheduleDocumentProcessing)
        try:
            self._widget.webView.page().mainFrame().loadFinished.disconnect(
              self._restoreScrollPos)
        except TypeError:  # already has been disconnected
            pass
        self.previewSync.del_()
        core.workspace().modificationChanged.disconnect(
          self._onDocumentModificationChanged)

        self._widget.cbTemplate.currentIndexChanged.disconnect(
          self._onCurrentTemplateChanged)
        core.aboutToTerminate.disconnect(self._quitingApplication)
        core.workspace().currentDocumentChanged.disconnect(
          self._onDocumentChanged)
        core.workspace().textChanged.disconnect(self._onTextChanged)
        core.uiSettingsManager().dialogAccepted.disconnect(
          self._scheduleDocumentProcessing)
        self._widget.webView.page().linkClicked.disconnect(self._onLinkClicked)
        self._widget.webView.page().mainFrame().titleChanged.disconnect(
          self._updateTitle)
        self._widget.cbEnableJavascript.clicked.disconnect(
          self._onJavaScriptEnabledCheckbox)
        self._widget.tbSave.clicked.disconnect(self.onPreviewSave)
        self._widget.splitter.splitterMoved.disconnect(self.on_splitterMoved)

        self._thread.htmlReady.disconnect(self._setHtml)
        self._thread.stop_async()
        self._thread.wait()

    def closeEvent(self, event):
        """Widget is closed. Clear it
        """
        self.closed.emit()
        self._clear()
        return DockWidget.closeEvent(self, event)

    def eventFilter(self, obj, ev):
        """ Event filter for the web view
        Zooms the web view
        """
        if isinstance(ev, QWheelEvent) and \
           ev.modifiers() == Qt.ControlModifier:
            multiplier = 1 + (0.1 * (ev.delta() / 120.))
            view = self._widget.webView
            view.setZoomFactor(view.zoomFactor() * multiplier)
            return True
        else:
            return DockWidget.eventFilter(self, obj, ev)

    def _onDocumentModificationChanged(self, document, modified):
        if not modified:  # probably has been saved just now
            self._scheduleDocumentProcessing()

    def _onLinkClicked(self, url):
        res = QDesktopServices.openUrl(url)
        if res:
            core.mainWindow().statusBar().showMessage("{} opened in a browser".format(url.toString()), 2000)
        else:
            core.mainWindow().statusBar().showMessage("Failed to open {}".format(url.toString()), 2000)

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
        frame = self._widget.webView .page().mainFrame()
        if frame.contentsSize() == QSize(0, 0):
            return # no valida data, nothing to save

        pos = frame.scrollPosition()
        self._scrollPos[self._visiblePath] = pos
        self._hAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Horizontal) == pos.x()
        self._vAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Vertical) == pos.y()

    def _restoreScrollPos(self, ok):
        """Restore scroll bar position for document
        """
        if core.workspace().currentDocument() is None:
            return  # nothing to restore if don't have document

        try:
            self._widget.webView.page().mainFrame().loadFinished.disconnect(self._restoreScrollPos)
        except TypeError:  # already has been disconnected
            pass

        if not self._visiblePath in self._scrollPos:
            return  # no data for this document

        frame = self._widget.webView.page().mainFrame()

        frame.setScrollPosition(self._scrollPos[self._visiblePath])

        if self._hAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Horizontal, frame.scrollBarMaximum(Qt.Horizontal))

        if self._vAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Vertical, frame.scrollBarMaximum(Qt.Vertical))

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

            self._clear()

            if core.config()['Preview']['Enabled']:
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
        """When shown, update document, if possible.
        """
        DockWidget.show(self)
        self._scheduleDocumentProcessing()

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
            if language == 'Markdown':
                text = self._getCurrentTemplate() + text
                # Hide the progress bar, since processing is usually short and
                # Markdown produces no errors or warnings to display in the
                # progress bar. See https://github.com/bjones1/enki/issues/36.
                self._widget.prgStatus.setVisible(False)
            elif isHtmlFile(document):
                # No processing needed -- just display it.
                self._setHtml(document.filePath(), text)
                # Hide the progress bar, since no processing is necessary.
                self._widget.prgStatus.setVisible(False)
                return
            elif ( (language == 'Restructured Text') or sphinxCanProcess or
                  canUseCodeChat(document.filePath()) ):
                # Show the progress bar for reST, CodeChat, or Sphinx builds. It
                # will display progress (Sphinx only) and errors/warnings (for
                # all three).
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
            # Save first, if needed.
            saveThenBuild = (sphinxCanProcess and internallyModified and
                not externallyModified and not buildOnSave)
            if saveThenBuild:
                # Trailing whitespace is not stripped when
                # autosaving. When a save is invoked manually,
                # trailing whitespace will be stripped if enabled.
                whitespaceSetting = core.config()["Qutepart"]["StripTrailingWhitespace"]
                core.config()["Qutepart"]["StripTrailingWhitespace"] = False
                document.saveFile()
                core.config()["Qutepart"]["StripTrailingWhitespace"] = whitespaceSetting
            # Build. Each line is one row in the table above.
            if ( (not sphinxCanProcess) or
                (sphinxCanProcess and not internallyModified) or
                saveThenBuild ):
                # For reST language is already correct.
                self._thread.process(document.filePath(), language, text)
            # Warn.
            if (sphinxCanProcess and internallyModified and
                externallyModified and not buildOnSave):
                core.mainWindow().appendMessage('Warning: file modified externally. Auto-save disabled.')

    def _copySphinxProjectTemplate(self, documentFilePath):
        """Add conf.py, CodeChat.css and index.rst (if ther're missing)
        to the Sphinx project directory.
        """
        if core.config()['Sphinx']['ProjectPath'] in self._sphinxTemplateCheckIgnoreList:
            return;

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
        if ( (len(self._sphinxTemplateCheckIgnoreList) == 1) and
            isinstance(self._sphinxTemplateCheckIgnoreList[0], int) ):
            res = self._sphinxTemplateCheckIgnoreList[0]
        else:
            res = QMessageBox.warning(self, r"Enki", "Sphinx project at:\n " + sphinxProjectPath
                         + "\nis missing the template file(s): "+ ' '.join(missinglist)
                         + ". Auto-generate those file(s)?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        if res != QMessageBox.Yes:
            if res == QMessageBox.No:
                self._sphinxTemplateCheckIgnoreList.append(sphinxProjectPath)
            return

        copyTemplateFile(errors, sphinxTemplatePath, 'index.rst', sphinxProjectPath)
        if core.config()['CodeChat']['Enabled'] and CodeChat:
            codeChatPluginsPath = os.path.dirname(os.path.realpath(CodeChat.__file__))
            codeChatTemplatePath = os.path.join(codeChatPluginsPath, 'template')
            copyTemplateFile(errors, codeChatTemplatePath, 'conf.py', sphinxProjectPath)
            copyTemplateFile(errors, codeChatTemplatePath, 'CodeChat.css', sphinxProjectPath)
        else:
            copyTemplateFile(errors, sphinxTemplatePath, 'conf.py', sphinxProjectPath)

        errInfo = ""
        for error in errors:
            errInfo += "Copy from " + error[0] + " to " + error[1] + " caused error " + error[2] + ';\n'
        if errInfo:
            QMessageBox.warning(self, "Sphinx template file copy error",
            "Copy template project files failed. The following errors are returned:<br>"
            + errInfo)

        return errors

    def _setHtml(self, filePath, html, errString=None, baseUrl=QUrl()):
        """Set HTML to the view and restore scroll bars position.
        Called by the thread
        """
        self._saveScrollPos()
        self._visiblePath = filePath
        self._widget.webView.page().mainFrame().loadFinished.connect(
          self._restoreScrollPos) # disconnected

        if baseUrl.isEmpty():
            self._widget.webView.setHtml(html, baseUrl=QUrl.fromLocalFile(filePath))
        else:
            self._widget.webView.setUrl(baseUrl)

        self._widget.teLog.clear()

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
            errPosRe = ':(\d*|None): '
            # Find the first occurence of a pair of colons.
            # Between them there can be numbers or "None" or nothing. For example,
            # this expression matches the string ":1589:" or string ":None:" or
            # string "::". Next::
            #
            #   <string>:1589:        (ERROR/3)Unknown interpreted text role "ref".
            errTypeRe =             '\(?(WARNING|ERROR|SEVERE)'
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
            # tuples contains the two matche groups (line number, error_string).
            # For example::
            #
            #  [('1589', 'ERROR')]
            #
            # Therefeore, the second element of each tuple, represented as x[1],
            # is the error_string. The next two lines of code will collect all
            # ERRORs/SEVEREs and WARNINGs found in the error_string separately.
            errNum = sum([x[1]==u'ERROR' or x[1]==u'SEVERE' for x in result])
            warningNum = [x[1] for x in result].count('WARNING')
            # Report these results this to the user.
            status = 'Warning(s): ' + str(warningNum) \
                     + ', error(s): ' + str(errNum)
            self._widget.teLog.appendHtml('<pre>' + errString + '<font color=red>' \
                                          + status + '</font></pre>')
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
            self._setHtmlProgress('Warning(s): 0, error(s): 0')
        self.setHtmlDone.emit()

    def _setHtmlProgress(self, text, color=None):
        """Set progress label.
        """
        if color:
            style = 'QLabel { background-color: '+color+'; }'
        else:
            style = style = 'QLabel {}'
        self._widget.prgStatus.setStyleSheet(style)
        self._widget.prgStatus.setText(text)
        self._widget.prgStatus.setVisible(True)

    def _clear(self):
        """Clear the preview dock contents.
        Might be necesssary for stop executing JS and loading data.
        """
        self._setHtml('', '', None, QUrl())

    def _isJavaScriptEnabled(self):
        """Check if JS is enabled in the settings.
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

    def onPreviewSave(self):
        """Save contents of the preview"""
        path = QFileDialog.getSaveFileName(self, 'Save Preview as HTML', filter='HTML (*.html)')
        if path:
            text = self._widget.webView.page().mainFrame().toHtml()
            data = text.encode('utf8')
            try:
                # Andrei: Shouldn't this be wb, since utf8 can produce binary data
                # where \n is different than \r\n?
                with open(path, 'w') as openedFile:
                    openedFile.write(data)
            except (OSError, IOError) as ex:
                QMessageBox.critical(self, "Failed to save HTML", unicode(str(ex), 'utf8'))
