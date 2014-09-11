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
import subprocess
import shutil

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
from .preview_sync import PreviewSync

# Likewise, attempt importing CodeChat; failing that, disable the CodeChat feature.
try:
    # Needed to access CodeChat.__file__; not importing this, but using the
    # other CodeChat.* imports below, doesn't define this.
    import CodeChat
except ImportError:
    CodeToRest = None
    LSO = None
else:
    import CodeChat.CodeToRest as CodeToRest
    import CodeChat.LanguageSpecificOptions as LSO

# .. note::
#    Pan: This fails several of the unit tests I wrote for it. Would you try out the
#    other option at the website below instead? If that works, then write good
#    docs explaining why.
def commonPrefix(dir1, dir2):
    """This function provides a platform-independent path commonPrefix. See `this
    post <http://stackoverflow.com/questions/21498939/how-to-circumvent-the-fallacy-of-pythons-os-path-commonprefix>`_
    for more details.

    Parameters: dir1, dir2 - Two paths to compare.
    Return value: the common path prefix shared by dir1 and dir2.
    """
    # Split the two paths into components composed of subdirectories.
    # Use normpath to guarantee that os.path.sep is the only separator;
    # otherwise, there could be both / and \.
    component = []
    dir1List = dir1.split(os.path.sep)
    dir2List = dir2.split(os.path.sep)
    minList = min(len(dir1List), len(dir2List))
    for i in range(minList):
        s = set([dir1List[i], dir2List[i]])
        if len(s) != 1:
            break
        component.append(s.pop())
    return os.path.sep.join(component)



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

    # .. note::
    #    Pan: this is very similar to _SphinxEnabledForFile. I that that implementation
    #    a bit better, since it checks to make sure the project path actually exists.
    #    Would you remove this function, then make _SphinxEnabledForFile a function
    #    instead of a class method, using that instead?
    def _canUseSphinx(self, filePath=None):
        # Sphinx config can be altered during program execution, thus its
        # configuration must be kept synced with latest settings.
        self._updateSphinxConfig()
        # Sphinx is available for the current file when:
        # Sphinx is enabled by Enki [config()['sphinx']['Enabled']] and
        # the file to be rendered is in the htmlBuilderRootPath directory.
        return (core.config()['Sphinx']['Enabled'] and
          self.htmlBuilderRootPath == commonPrefix(self.htmlBuilderRootPath, filePath))

    def _updateSphinxConfig(self):
        # Executable to run the HTML builder.
        self.htmlBuilderExecutable = core.config()['Sphinx']['Executable']
        # Path to the root directory of an HTML builder.
        self.htmlBuilderRootPath = core.config()['Sphinx']['ProjectPath']
        # Path to the output produced by the HTML builder.
        self.htmlBuilderOutputPath = core.config()['Sphinx']['OutputPath']
        # Extension for the resluting HTML files.
        self.htmlBuilderExtension = u'.' + core.config()['Sphinx']['OutputExtension']
        if core.config()['Sphinx']['AdvancedMode']:
            self.htmlBuilderCommandLine = core.config()['Sphinx']['Cmdline']
        else:
            # For available builder options, refer to: http://sphinx-doc.org/builders.html
            self.htmlBuilderCommandLine = (self.htmlBuilderExecutable +
              # Place doctrees in the ``_build`` directory; by default, Sphinx places this in _build/html/.doctrees.
              u' -d _build/doctrees ' +
              # Source directory
              self.htmlBuilderRootPath + ' ' +
              # Build directory
              self.htmlBuilderOutputPath)

    def _getHtml(self, language, text, filePath):
        """Get HTML for document
        """
        # TODO: Pan: Calling core.config() in a non-GUI thread produces crashes. So,
        # would you move all calls to core.config() to the scheduleDocumentProcessing
        # method in the GUI thread? In particular, it looks like this code needs
        # the following values computed in the GUI thread then passed to it:
        #
        # - canUseSphinx, canUseCodeChat
        # - htmlFile, htmlFileAlter
        # - htmlBuilderCommandLine, htmlBuilderRootPath
        #
        # One method: use _getHtml(self, task) and place all these extra vars
        # in task.
        if language == 'Markdown':
            return self._convertMarkdown(text), None, QUrl()
        # For ReST, use docutils only if Sphinx isn't available.
        elif language == 'Restructured Text' and not self._canUseSphinx(filePath):
            htmlUnicode, errString = self._convertReST(text)
            return htmlUnicode, errString, QUrl()
        elif filePath:
            # Use Sphinx to generate the HTML if possible.
            if self._canUseSphinx(filePath):
                # Run the builder.
                errString = self._runHtmlBuilder()

                # Look for the HTML output.
                #
                # First, create an htmlPath as self.htmlBuilderOutputPath + remainder of htmlRelPath
                htmlPath = os.path.join(self.htmlBuilderOutputPath + filePath[len(self.htmlBuilderRootPath):])
                # First place to look: file.html. For example, look for foo.py
                # in foo.py.html.
                htmlFile = htmlPath + self.htmlBuilderExtension
                # Second place to look: file without extension.html. For
                # example, look for foo.rst in foo.html.
                htmlFileAlter = os.path.splitext(htmlPath)[0] + self.htmlBuilderExtension
                if os.path.exists(htmlFile):
                    return u'', errString, QUrl.fromLocalFile(htmlFile)
                elif os.path.exists(htmlFileAlter):
                    return u'', errString, QUrl.fromLocalFile(htmlFileAlter)
                else:
                    return ('No preview for this type of file in ' + htmlFile +
                            " or " + htmlFileAlter, None, QUrl())

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
                errString = errStream.getvalue()
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
        htmlString = docutils.core.publish_string(text, writer_name='html', settings_overrides={
                     # Make sure to use Unicode everywhere.
                     'output_encoding': 'unicode',
                     'input_encoding' : 'unicode',
                     # The default docutils stylesheet and template uses a relative path, which doesn't work when frozen ???.
                     'template': os.path.join(os.path.dirname(docutils.writers.html4css1.__file__), docutils.writers.html4css1.Writer.default_template),
                     'stylesheet_dirs': ['.', os.path.dirname(docutils.writers.html4css1.__file__)],
                     # Don't stop processing, no matter what.
                     'halt_level'     : 5,
                     # Capture errors to a string and return it.
                     'warning_stream' : errStream})
        errString = errStream.getvalue()
        errStream.close()
        return htmlString, errString

    # .. note::
    #    Pan: would you factor these changes back into enki.lib.get_console_output?
    def _runHtmlBuilder(self):
        if hasattr(subprocess, 'STARTUPINFO'):  # windows only
            # On Windows, subprocess will pop up a command window by default when run from
            # Pyinstaller with the --noconsole option. Avoid this distraction.
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Windows doesn't search the path by default. Pass it an environment so it will.
            env = os.environ
        else:
            si = None
            env = None

        try:
            # On Windows, running this from the binary produced by Pyinstller
            # with the ``--noconsole`` option requires redirecting everything
            # (stdin, stdout, stderr) to avoid a OSError exception
            # "[Error 6] the handle is invalid."
            popen = subprocess.Popen(self.htmlBuilderCommandLine,
                      cwd=self.htmlBuilderRootPath,
                      stdin=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE,
                      startupinfo=si, env=env)
        except Exception as ex:
            return '<pre><font color=red>Failed to execute HTML builder' + \
                   'console utility "{}":\n{}</font>\n'\
                   .format(self.htmlBuilderCommandLine, str(ex)) + \
                   '\nGo to Settings -> Settings -> CodeChat to set HTML builder configurations.'

        stdout, stderr = popen.communicate()
        return stdout + '</pre><br><pre><font color=red>' + stderr + '</font>'

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
        self._widget.webView.page().mainFrame().setZoomFactor(1.5)

        self._widget.webView.page().mainFrame().titleChanged.connect(self._updateTitle)
        self.setWidget(self._widget)
        self.setFocusProxy(self._widget.webView)

        self._widget.cbEnableJavascript.clicked.connect(self._onJavaScriptEnabledCheckbox)

        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)

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

        # If we update Preview on every key pressing, freezes are sensible (GUI thread draws preview too slowly
        # This timer is used for drawing Preview 300 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(300)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self._widget.cbTemplate.currentIndexChanged.connect(self._onCurrentTemplateChanged)

        self.previewSync = PreviewSync(self._widget.webView)

        self._applyJavaScriptEnabled(self._isJavaScriptEnabled())

        self._widget.tbSave.clicked.connect(self.onPreviewSave)

        # Don't need to schedule document processing; a call to show() does.


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

    def _sphinxEnabledForFile(self, filePath):
        sphinxProjectPath = os.path.abspath(core.config()['Sphinx']['ProjectPath'])
        return core.config()['Sphinx']['Enabled'] and \
               os.path.exists(core.config()['Sphinx']['ProjectPath']) and\
               sphinxProjectPath == commonPrefix(filePath, sphinxProjectPath)

    # .. note::
    #    Pan: this seems a bit broken. I think the self.typingTimer is already calling
    #    _scheduleDocumentProcessing a fixed delay after the last keypress. Why not
    #    simply include this code in _scheduleDocumentProcessing instead?
    def _onTextChanged(self, document):
        # TODO: This 'document' parameter is never used.
        """Text changed, update preview
        """
        # Once checked, build on save will force enki to only build on saving
        # actions. Text change will not trigger a rebuild.
        if core.config()['Preview']['Enabled']:
            if not (self._sphinxEnabledForFile(document.filePath()) and
            core.config()['Sphinx']['BuildOnSave']):
                self._scheduleDocumentProcessing()

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
            # .. note::
            #    Pan: I think this is a bit clearer, code-wise. Another option
            #    would be to rename the function to _copySphinxProjectTemplateIfNeeded
            #    or something like that.
            if self._sphinxEnabledForFile(document.filePath()):
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
            else:
                # .. note::
                #    Pan -- this should save the old value of StripTrailingWhitespace,
                #    save the file, then restore it. Otherwise, StripTrailingWhitespace
                #    will be turned on? (I think -- the config isn't flushed, but
                #    even if not, this is suspicious coding that will probably
                #    fail later).
                #
                # Only save when Sphinx is enabled for current document. Trailing
                # whitespace is not stripped when autosaving. When saving actions
                # are invoked manually, trailing whitespace will be stripped if
                # enabled.
                if qp.document().isModified() and self._sphinxEnabledForFile(document.filePath()):
                    core.config()["Qutepart"]["StripTrailingWhitespace"] = False
                    # TODO: Notice: Here core config has not been flushed.
                    document.saveFile()
                    core.config()["Qutepart"]["StripTrailingWhitespace"] = True
            self._setHtmlProgress(-1)
            # for rest language is already correct
            self._thread.process(document.filePath(), language, text)

    def _copySphinxProjectTemplate(self, documentFilePath):
        """Add conf.py, default.css and index.rst (if ther're missing)
           to the Sphinx project directory.
           """
        # Check the existance of conf.py, default.css, and index.rst. If
        # any of those files are missing, we will add a template file to it
        # But before that a notification will pop out tellign the user we are
        # about to copy some template files. If any system error (shutil
        # exceptions)
        codeChatPath = os.path.dirname(os.path.realpath(CodeChat.__file__))
        errors = []

        # .. note::
        #    Pan: This is repetitive code. DRY! (Don't Repeat Yourself). Make
        #    a helper function for each copy, then call that 3 times.
        if not os.path.exists(os.path.join(core.config()['Sphinx']['ProjectPath'], 'default.css')):
            cssPath = os.path.join(codeChatPath, 'template/default.css')
            try:
                shutil.copy(cssPath, core.config()['Sphinx']['ProjectPath'])
            except Exception as why:
                errors.append((cssPath, core.config()['Sphinx']['ProjectPath'], str(why)))
        if not os.path.exists(os.path.join(core.config()['Sphinx']['ProjectPath'], 'index.rst')):
            indexPath = os.path.join(codeChatPath, 'template/index.rst')
            try:
                shutil.copy(indexPath, core.config()['Sphinx']['ProjectPath'])
            except Exception as why:
                errors.append((indexPath, core.config()['Sphinx']['ProjectPath'], str(why)))
        if not os.path.exists(os.path.join(core.config()['Sphinx']['ProjectPath'], 'conf.py')):
            # Choose which conf.py file to copy based on whether CodeChat is enabled.
            try:
                if core.config()['CodeChat']['Enabled']:
                    # If CodeChat is also enabled, enable this in conf.py too.
                    confPath = os.path.join(codeChatPath, 'template/conf_codechat.py')
                    shutil.copy(confPath, os.path.join(core.config()['Sphinx']['ProjectPath'], 'conf.py'))
                else:
                    # else simple copy the default conf.py to sphinx target directory
                    confPath = os.path.join(codeChatPath, 'template/conf.py')
                    shutil.copy(confPath, core.config()['Sphinx']['ProjectPath'])
            except IOError as why:
                errors.append((confPath, core.config()['Sphinx']['ProjectPath'], str(why)))

        errInfo = ""
        for error in errors:
            errInfo += "Copy from " + error[0] + " to " + error[1] + " caused error " + error[2] + ';\n'
        if errInfo:
            # TODO: Test this
            QMessageBox.warning(self, "File copy error",  errInfo)

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
        # Pan: This seems unnecessary here -- the code below should run quickly
        # enough to make this invisible to the user.
        self._setHtmlProgress(-1)

        # If there were messages from the conversion process, extract a count of
        # errors and warnings from these messages.
        if errString:
            # .. note::
            #    Pan: rather than hard-code the splitter size, save it when
            #    it's auto-hidden then restore that saved value here.
            #
            # If there are errors/warnings, expand log window to make it visible
            self._widget.splitter.setSizes([180,60])

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
            status = 'Warning(s): ' + str(warningNum) + ' Error(s): ' + str(errNum)
            self._widget.teLog.appendHtml('<pre>' + errString + '</pre><pre><font color=red>' \
                                          + status + '</font></pre>')
            # Update the progress bar.
            color = 'red' if errNum else 'yellow' if warningNum else None
            self._setHtmlProgress(100, color)
        else:
            # TODO: probably remove this behavior or change it per the notes above.
            #
            # If there are no errors/warnings, collapse the log window (can mannually
            # expand it back to visible)
            self._widget.splitter.setSizes([1,0])
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
            style = 'QProgressBar::chunk {\nbackground-color: '+color+'\n}'
        else:
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
