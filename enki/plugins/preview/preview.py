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

# Third-party imports
# -------------------
from PyQt4.QtCore import pyqtSignal, QSize, Qt, QThread, QTimer, QUrl
from PyQt4.QtGui import QDesktopServices, QFileDialog, QIcon, QMessageBox, QWidget
from PyQt4.QtWebKit import QWebPage
from PyQt4 import uic

# Local imports
# -------------
from enki.core.core import core
from enki.widgets.dockwidget import DockWidget
from enki.plugins.preview import isHtmlFile
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
    LSO = None
else:
    import CodeChat.CodeToRest as CodeToRest
    import CodeChat.LanguageSpecificOptions as LSO

# Determine if we're frozen with Pyinstaller or not.
if getattr(sys, 'frozen', False):
    isFrozen = True
else:
    isFrozen = False

def commonPrefix(*dirs):
    """This function provides a platform-independent path commonPrefix. It
    returns the common path between all directories in input list dirs, assuming
    that any relative paths are rooted in the current directory. While`this post
    <http://stackoverflow.com/questions/21498939/how-to-circumvent-the-fallacy-of-pythons-os-path-commonprefix>`_
    has two solutions, neither are correct; hence, the following code.

    Parameters: dirs - Directory list.
    Return value: the common path prefix shared by all input directories.
    """
    # corner case (empty input list)
    if not dirs:
        return ''
    # Path cleaning toolset:
    #
    # - **realpath** follows symbolic links, so they will be compared in
    #   terms of what they refer to. realpath will also evaluate directory
    #   traversals.
    #
    #   #. get Canonical path.
    #   #. eliminate symbolic links.
    #
    # - **normcase** makes Windows filenames all lowercase, since the
    #   following code uses case-sensitive string comparions. Windows
    #   uses case-insensitive naming for its files.
    #
    #   #. converts path to lower case for case-insensitive filesystem.
    #   #. converts forward slashes to backward slashes (Windows only)
    # - **abspath** collapses and evaluates directory traversals like
    #   ``./../subdir``, to correctly compare absolute and relative paths,
    #   and normalizes the os.path.sep for the current platform
    #   (i.e. no `\a/b` paths). Similar to ``normpath(join(os.getcwd(), path))``.
    fullPathList = [os.path.normcase(os.path.abspath(os.path.realpath(d))) for d in dirs]
    # Now use ``commonprefix`` on absolute paths.
    prefix = os.path.commonprefix(fullPathList)
    # commonprefix stops at the first dissimilar character, leaving an incomplete
    # path name. For example, ``commonprefix(('aa', 'ab')) == 'a'``. Fix this
    # by removing this ending incomplete path if necessary.
    for d in fullPathList:
        # ``commonPrefix`` contains a complete path if the character in
        # ``d`` after its end is an os.path.sep or the end of the path name.
        if len(d) > len(prefix) and d[len(prefix)] != os.path.sep:
            # This is an incomplete path. Remove it.
            prefix = os.path.dirname(prefix)
            break
    # If any input directory is absolute path, then commonPrefix will return
    # an absolute path.
    if any((os.path.isabs(d)) for d in dirs):
        return prefix

    # If not, we will use the assumption that all relative paths
    # are rooted in the current directory. Test whether ``prefix`` starts with
    # the current working directory. If not, return an absolute path.
    cwd = os.getcwd()
    return prefix if not prefix.startswith(cwd) else prefix[len(cwd) + len(os.path.sep):]


def sphinxEnabledForFile(filePath):
    """Based on Sphinx settings under core.config()['Sphinx'], this function
    determines whether sphinx can be applied to *filePath*.
    """
    sphinxProjectPath = core.config()['Sphinx']['ProjectPath']
    return ( filePath and
           core.config()['Sphinx']['Enabled'] and
           os.path.exists(core.config()['Sphinx']['ProjectPath']) and
           os.path.normcase(sphinxProjectPath) == commonPrefix(filePath, sphinxProjectPath))

def copyTemplateFile(errors, source, templateFileName, dest, newName=None):
    """For each sphinx project, two files are needed: ``index.rst``as master
    document, and ``conf.py`` as sphinx configuration file. Given a file with
    ``templateFileName``, it will be copied to destination directory ``dest``.
    If any error occurs during copy operation, error information will
    be appended to ``errors``.
    """
    if not source or not dest:
        errors.append((source, dest, "Input or output directory cannot be None"))
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

    def _canUseCodeChat(self):
        # Codechat is available when LSO and CodeToRest can be found,
        # and Enki settings enable codechat (config()['CodeChat']['Enabled'] is true).
        return core.config()['CodeChat']['Enabled'] and LSO and CodeToRest

    def _getHtml(self, language, text, filePath):
        """Get HTML for document
        """
        if language == 'Markdown':
            return self._convertMarkdown(text), None, QUrl()
        # For ReST, use docutils only if Sphinx isn't available.
        elif language == 'Restructured Text' and not sphinxEnabledForFile(filePath):
            htmlUnicode, errString = self._convertReST(text)
            return htmlUnicode, errString, QUrl()
        elif filePath:
            # Use Sphinx to generate the HTML if possible.
            if sphinxEnabledForFile(filePath):
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
                # First place to look: file.html. For example, look for foo.py
                # in foo.py.html.
                ext =  u'.' + core.config()['Sphinx']['OutputExtension']
                htmlFile = htmlPath + ext
                # Second place to look: file without extension.html. For
                # example, look for foo.html for foo.rst.
                htmlFileAlter = os.path.splitext(htmlPath)[0] + ext
                if os.path.exists(htmlFile):
                    return u'', errString, QUrl.fromLocalFile(htmlFile)
                elif os.path.exists(htmlFileAlter):
                    return u'', errString, QUrl.fromLocalFile(htmlFileAlter)
                else:
                    return ('No preview for this type of file.<br>Expect ' + htmlFile +
                            " or " + htmlFileAlter, errString, QUrl())

            # Otherwise, fall back to using CodeChat+docutils.
            elif self._canUseCodeChat():
                # Use StringIO to pass CodeChat compilation information back to
                # the UI.
                errStream = StringIO.StringIO()
                lso = LSO.LanguageSpecificOptions()
                fileName, fileExtension = os.path.splitext(filePath)
                # Check to seee if CodeToRest supportgs this file's extension.
                if fileExtension not in lso.extension_to_options.keys():
                    return 'No preview for this type of file', None, QUrl()
                # CodeToRest can render this file. Do so.
                lso.set_language(fileExtension)
                htmlString = CodeToRest.code_to_html_string(text, lso, errStream)
                # Error string might contain characters such as ">" and "<",
                # they need to be converted to "&gt;" and "&lt;" such that
                # they can be displayed correctly in the log window as html strings.
                # This step is handled by ``cgi.escape``.
                errString = errStream.getvalue()
                if errString:
                    errString = "<font color='red'>" + cgi.escape(errString) + '</font>'
                errStream.close()
                return htmlString, errString, QUrl()

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
        self._widget = QWidget(self)

        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Preview.ui'), self._widget)

        self._loadTemplates()

        self._widget.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self._widget.webView.page().linkClicked.connect(self._onLinkClicked)

        self._widget.webView.page().mainFrame().titleChanged.connect(self._updateTitle)
        self.setWidget(self._widget)
        self.setFocusProxy(self._widget.webView)

        self._widget.cbEnableJavascript.clicked.connect(self._onJavaScriptEnabledCheckbox)

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
        core.uiSettingsManager().dialogAccepted.connect(self._scheduleDocumentProcessing)

        # File save actions always trigger a rebuild
        core.actionManager().action( "mFile/mSave/aCurrent" ).triggered.connect(self._scheduleDocumentProcessing)
        core.actionManager().action( "mFile/mSave/aAll" ).triggered.connect(self._scheduleDocumentProcessing)
        core.actionManager().action( "mFile/mSave/aSaveAs" ).triggered.connect(self._scheduleDocumentProcessing)

        self._scrollPos = {}
        self._vAtEnd = {}
        self._hAtEnd = {}

        self._thread = ConverterThread()
        self._thread.htmlReady.connect(self._setHtml)

        self._visiblePath = None

        # If we update Preview on every key press, freezes are noticable (the
        # GUI thread draws the preview too slowly).
        # This timer is used for drawing Preview 300 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(300)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self._widget.cbTemplate.currentIndexChanged.connect(self._onCurrentTemplateChanged)

        self.previewSync = PreviewSync(self._widget.webView)

        self._applyJavaScriptEnabled(self._isJavaScriptEnabled())

        self._widget.tbSave.clicked.connect(self.onPreviewSave)

        # Add an attribute to ``self._widget`` denoting the splitter location.
        # This value will be overwritten when the user changes splitter location.
        self._widget.splitterErrorStateSize = (199,50)
        self._widget.splitterNormStateSize = (1,0)
        self._widget.splitterNormState = True
        self._widget.splitter.setSizes(self._widget.splitterNormStateSize)
        self._widget.splitter.splitterMoved.connect(self.on_splitterMoved)
        # Don't need to schedule document processing; a call to show() does.

    def on_splitterMoved(self, pos, index):
        if self._widget.splitterNormState:
            self._widget.splitterNormStateSize = self._widget.splitter.sizes()
        else:
            self._widget.splitterErrorStateSize = self._widget.splitter.sizes()

    def del_(self):
        """Uninstall themselves
        """
        self._typingTimer.stop()
        self._thread.htmlReady.disconnect(self._setHtml)
        try:
            self._widget.webView.page().mainFrame().loadFinished.disconnect(self._restoreScrollPos)
        except TypeError:  # already has been disconnected
            pass
        self.previewSync.del_()
        core.actionManager().action( "mFile/mSave/aCurrent" ).triggered.disconnect(self._scheduleDocumentProcessing)
        core.actionManager().action( "mFile/mSave/aAll" ).triggered.disconnect(self._scheduleDocumentProcessing)
        core.actionManager().action( "mFile/mSave/aSaveAs" ).triggered.disconnect(self._scheduleDocumentProcessing)

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
        """When shown, update document, if possible.
        """
        DockWidget.show(self)
        self._scheduleDocumentProcessing()

    def _scheduleDocumentProcessing(self):
        """Start document processing with the thread.
        """
        self._typingTimer.stop()

        document = core.workspace().currentDocument()
        if document is not None:
            if sphinxEnabledForFile(document.filePath()):
                self._copySphinxProjectTemplate(document.filePath())
            qp = document.qutepart
            language = qp.language()
            text = qp.text
            if document.qutepart.language() == 'Markdown':
                language = 'Markdown'
                text = self._getCurrentTemplate() + text
            elif isHtmlFile(document):
                # No processing needed -- just display it.
                self._setHtml(document.filePath(), text)
                return
            elif language == 'Restructured Text':
                pass
            # Determine whether to initiate a build or not. The underlying
            # logic:
            #
            # - If Sphinx can't process this file, just build it.
            # - If Sphinx can process this file:
            #
            #   - If the document isn't internally modified, we're here because the file
            #     was saved or the refresh button was pressed. Build it.
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
            sphinxCanProcess = sphinxEnabledForFile(document.filePath())
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
                self._setHtmlProgress(-1)
                # for rest language is already correct
                self._thread.process(document.filePath(), language, text)
            # Warn.
            if (sphinxCanProcess and internallyModified and
                externallyModified and not buildOnSave):
                 # TODO: warn user. Andrei: what method do I use to put a
                 # warning message on the screen, like the warning produced
                 # when opening a file that utf-8 decoding fails on?
                pass

    def _copySphinxProjectTemplate(self, documentFilePath):
        """Add conf.py, CodeChat.css and index.rst (if ther're missing)
        to the Sphinx project directory.
        """
        try:
            if core.config()['Sphinx']['ProjectPath'] in self._sphinxTemplateCheckIgnoreList:
                return;
        except AttributeError:
            self._sphinxTemplateCheckIgnoreList = []

        # Check for the existance Sphinx project files. Copy skeleton versions
        # of them to the project if necessary.
        sphinxPluginsPath = os.path.dirname(os.path.realpath(__file__))
        sphinxTemplatePath = os.path.join(sphinxPluginsPath, 'sphinx_templates')
        sphinxProjectPath = core.config()['Sphinx']['ProjectPath']
        errors = []
        checklist = ['index.rst', 'conf.py', 'CodeChat.css']
        missinglist = []
        for filename in checklist:
            if not os.path.exists(os.path.join(sphinxProjectPath, filename)):
                missinglist.append(filename)
        if not missinglist:
            return errors

        question = QMessageBox(self)
        question.addButton(QMessageBox.Yes)
        question.addButton(QMessageBox.No)
        question.addButton("Not now", QMessageBox.RejectRole)
        question.setWindowTitle("Enki")
        question.setText("Sphinx prject at:\n " + sphinxProjectPath
                         + "\nmisses template file(s): "+ ' '.join(missinglist)
                         + ". Auto-generate those file(s)?")
        question.setDefaultButton(QMessageBox.Yes)
        res = question.exec_()
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
        self._widget.webView.page().mainFrame().loadFinished.connect(self._restoreScrollPos)

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
            self._setHtmlProgress(100, color)
        else:
            # If there are no errors/warnings, collapse the log window (can mannually
            # expand it back to visible)
            if not self._widget.splitterNormState:
                self._widget.splitterErrorStateSize = self._widget.splitter.sizes()
                self._widget.splitterNormState = True
            self._widget.splitter.setSizes(self._widget.splitterNormStateSize)
            self._setHtmlProgress(100)
        self.setHtmlDone.emit()

    def _setHtmlProgress(self, progress=None, color=None):
        """Set progress bar and status label.
        if progress is -1: use an indefinite progress bar.
        if progress is 0: reset the progress bar to 0.
        if progress is any value between 0 and 100: display progress bar
          with that percentage of completion.
        """
        if color:
            self._widget.prgStatus.setTextVisible(True)
            self._widget.prgStatus.setAlignment(Qt.AlignCenter)
            self._widget.prgStatus.setFormat(('Error' if color == 'red' else 'Warning')
                                             + '(s) detected')
            style = 'QProgressBar::chunk {\nbackground-color: '+color+'\n}'
        else:
            self._widget.prgStatus.setTextVisible(False)
            style = 'QProgressBar::chunk {}'
        self._widget.prgStatus.setStyleSheet(style)
        if progress == -1:
            self._widget.prgStatus.setRange(0, 0)
        elif progress == 0 or not progress:
            self._widget.prgStatus.reset()
        else:
            assert progress >= 0 and progress <= 100
            self._widget.prgStatus.setRange(0, 100)
            self._widget.prgStatus.setValue(progress)

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
