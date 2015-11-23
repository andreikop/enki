# **********************************************************
# __init__.py - The HTML, Markdown, and reST preview package
# **********************************************************
# The Preview plugin provides an HTML-based rendering of the
# file currently being edited. This file implements the
# Plugin interface; other modules are given below.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Library imports
# ---------------
import sys
import os.path
import fnmatch
#
# Third-party imports
# -------------------
from PyQt4.QtCore import QObject, Qt, pyqtSlot
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QWidget, QFileDialog, \
    QPalette
from PyQt4 import uic
#
# Local imports
# -------------
from enki.core.core import core
from enki.core.uisettings import CheckableOption, TextOption, ChoiseOption
from enki.lib.get_console_output import get_console_output

# Import CodeChat if possible; otherwise, indicate it wasn't available.
try:
    from CodeChat import CodeToRest
    from CodeChat.CommentDelimiterInfo import SUPPORTED_GLOBS
except ImportError:
    CodeToRest = None

# Utilities
# =========
def isHtmlFile(document):
    """Return True if document refers to an HTML file; return False otherwise.
    """
    return ( document is not None and
        document.qutepart.language() is not None and
        'html' in document.qutepart.language().lower() and
        # Return True if this is a Django HTML template;
        # return False for HTML (PHP).
        (not 'php' in document.qutepart.language().lower()) )

def canUseCodeChat(filePath):
    """Return True if CodeChat can be used with ``filePath``; return False
    otherwise.
    """
    # CodeChat can preview a file if it's enabled and if that file's
    # name/extension is supported.
    if ( CodeToRest is not None and core.config()['CodeChat']['Enabled']
         and filePath ):
        filename = os.path.basename(filePath)
        for glob in SUPPORTED_GLOBS:
            if fnmatch.fnmatch(filename, glob):
                return True
    return False

def sphinxEnabledForFile(filePath):
    """Based on Sphinx settings under core.config()['Sphinx'], this function
    determines whether Sphinx can be applied to filePath. It can't know if
    Sphinx actually processes the file or not, since this is based on conf.py
    settings.
    """
    sphinxProjectPath = core.config()['Sphinx']['ProjectPath']
    return ( filePath and
           core.config()['Sphinx']['Enabled'] and
           os.path.exists(core.config()['Sphinx']['ProjectPath']) and
           os.path.normcase(sphinxProjectPath) ==
             commonPrefix(filePath, sphinxProjectPath))

def commonPrefix(*dirs):
    """This function provides a platform-independent path commonPrefix. It
    returns the common path between all directories in input list dirs, assuming
    that any relative paths are rooted in the current directory. While `this post
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
    #   (i.e. no `\a/b` paths). Similar to ``normpath(join(os.getcwd(),
    #   path))``.
    fullPathList = [os.path.normcase(os.path.abspath(os.path.realpath(d)))
                    for d in dirs]
    # Now use ``commonprefix`` on absolute paths.
    prefix = os.path.commonprefix(fullPathList)
    # commonprefix stops at the first dissimilar character, leaving an
    # incomplete path name. For example, ``commonprefix(('aa', 'ab')) == 'a'``.
    # Fix this by removing this ending incomplete path if necessary.
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
    return prefix if not prefix.startswith(cwd) \
                  else prefix[len(cwd) + len(os.path.sep):]

def _getSphinxVersion(path):
    """Return the Sphinx version as a list of integer items.

    Raise OSError if not found, or
          ValueError if failed to parse.
    """
    stdout, stderr = get_console_output([path, "--version"])
    # Command "Sphinx-build --version" will only output sphinx version info.
    # Typical output looks like: ``Sphinx (sphinx-build) 1.2.3`` or
    # ``Sphinx v1.2.3``
    # But the problem is sometimes version info goes to stdout(version 1.2.3),
    # while sometimes it goes to stderr(version 1.1.3). Thus combining stdout
    # and stderr is necessary.
    out = stdout + '\n' + stderr
    for line in out.split('\n'):
        if line.startswith("Sphinx"):
            # Split on space, take the last segment, if it starts with character
            # 'v', strip the 'v'. Then split on dot. returning the version as a
            # tuple.
            version = line.split(' ')[-1]
            version = version[1:] if version.startswith('v') else version
            return [int(num) for num in version.split('.')]
    raise ValueError

# GUIs
# ====
# This class implements the GUI for a combined CodeChat settings page.
class CodeChatSettingsWidget(QWidget):
    """Insert the preview plugin as a page of the UISettings dialog.
    """
    def __init__(self, dialog):
        # Initialize the dialog, loading in the literate programming settings
        # GUI.
        QWidget.__init__(self, dialog)
        uic.loadUi(os.path.join(os.path.dirname(__file__),
                                'CodeChat_Settings.ui'), self)

        if CodeToRest is None:
            # If the CodeChat module can't be loaded, then disable the
            # associated checkbox and show the "not installed" message.
            self.cbCodeChat.setEnabled(False)
            self.labelCodeChatNotInstalled.setVisible(True)
            self.labelCodeChatNotInstalled.setEnabled(True)
        else:
            # Hide the "not installed" message.
            self.labelCodeChatNotInstalled.setVisible(False)

        # Add this GUI to the settings dialog box.
        dialog.appendPage(u"Literate programming", self)
        # Next, have the setting UI auto-update the corresponding CodeChat and
        # config entries.
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "CodeChat/Enabled",
                                            self.cbCodeChat))

# This class implements the GUI for a combined CodeChat / Sphinx settings page.
class SphinxSettingsWidget(QWidget):
    """Insert the preview plugin as a page of the UISettings dialog.
    """
    def __init__(self, dialog):
        # Initialize the dialog, loading in the literate programming settings
        # GUI.
        QWidget.__init__(self, dialog)
        uic.loadUi(os.path.join(os.path.dirname(__file__),
                                'Sphinx_Settings.ui'), self)

        # Make links gray when they are disabled
        palette = self.palette()
        palette.setColor(QPalette.Disabled,
                         QPalette.Link,
                         palette.color(QPalette.Disabled, QPalette.Text))
        self.lbSphinxReference.setPalette(palette)

        palette = self.palette()
        palette.setColor(QPalette.Active,
                         QPalette.WindowText,
                         palette.color(QPalette.Normal, QPalette.Link))
        self.lbSphinxEnableAdvMode.setPalette(palette)

        # Clicking on advanced mode label triggers either advanced mode or
        # normal mode.
        self.lbSphinxEnableAdvMode.mousePressEvent = self.on_ToggleSphinxSettingModeClicked

        # Update misc pieces of the GUI that can't be stored in the .ui file.
        self._updateSphinxSettingMode()

        # Add this GUI to the settings dialog box.
        dialog.appendPage("Sphinx", self)
        # Next, have the setting UI auto-update the corresponding CodeChat and
        # config entries.
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "Sphinx/Enabled",
                                            self.gbSphinxProject))
        dialog.appendOption(ChoiseOption(dialog, core.config(),
                                         "Sphinx/BuildOnSave",
                                         {self.rbBuildOnlyOnSave: True,
                                          self.rbBuildOnFileChange: False}))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/ProjectPath",
                                       self.leSphinxProjectPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/OutputPath",
                                       self.leSphinxOutputPath))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/Executable",
                                       self.leSphinxExecutable))
        dialog.appendOption(TextOption(dialog, core.config(),
                                       "Sphinx/Cmdline",
                                       self.leSphinxCmdline))

        # Run this after the appendOption calls, since these fields must be set
        # up before _updateleValidateSphinxExecutable can run.
        self._updateleValidateSphinxExecutable()

    def _updateleValidateSphinxExecutable(self):
        """ Check if Sphinx is installed. Sphinx version is not important

        Update leValidateSphinxExecutable based on Sphinx status.
        """
        path = self.leSphinxExecutable.text()
        try:
            _getSphinxVersion(path)
        except OSError as ex:
            self.leValidateSphinxExecutable.setText('Failed to execute {}: {}'.format(path, ex))
        except ValueError:
            self.leValidateSphinxExecutable.setText('Failed to parse {} version. Does sphinx work?'.format(path))
        else:
            self.leValidateSphinxExecutable.setText('Sphinx is found!')

    @pyqtSlot()
    def on_pbSphinxProjectPath_clicked(self):
        """Provide a directory chooser for the user to select a project path.
        """
        path = QFileDialog.getExistingDirectory(core.mainWindow(),
            'Project path', self.leSphinxProjectPath.text())
        if path:
            self.leSphinxProjectPath.setText(path)
            # Automatically set the builder output path to '_build\\html' under
            # builder root path.
            #
            # Since relative paths are supported, we will only set
            # leSphinxOutputPath if the path was none or was absolute (and
            # therefore presumabely wrong). If it's a relative path such as
            # ``_build\html``, then it's probably OK without changing.
            if (not self.leSphinxOutputPath.text()
                or os.path.isabs(self.leSphinxOutputPath.text())):
                self.leSphinxOutputPath.setText(os.path.join(path, '_build',
                                                             'html'))

    @pyqtSlot()
    def on_pbSphinxOutputPath_clicked(self):
        """Proivde a directory chooser for the user to select an output path.
        """
        path = QFileDialog.getExistingDirectory(core.mainWindow(), 'Output path')
        if path:
            self.leSphinxOutputPath.setText(path)

    # The Sphinx executable can be selected by the user. A filter is needed
    # such that non-executable files will not be selected by the user.
    @pyqtSlot()
    def on_pbSphinxExecutable_clicked(self):
        fltr = "sphinx-build" + (".exe" if sys.platform.startswith("win") else "") \
               + ";; All files (*)"
        path = QFileDialog.getOpenFileName(self,
                                           "Select Sphinx executable",
                                           filter=fltr)
        if path:
            self.leSphinxExecutable.setText(path)
            self._updateleValidateSphinxExecutable()

    def on_ToggleSphinxSettingModeClicked(self, *args):
        core.config()['Sphinx']['AdvancedMode'] = not core.config()['Sphinx']['AdvancedMode']
        core.config().flush()
        self._updateSphinxSettingMode()

    # The project path and Sphinx executable directory must be absolute;
    # the output path may be relative to the project path or absolute.
    # Use abspath or normpath as appropriate to guarantee this is true.
    def on_leSphinxProjectPath_editingFinished(self):
        self.leSphinxProjectPath.setText(os.path.abspath(self.leSphinxProjectPath.text()))

    def on_leSphinxOutputPath_editingFinished(self):
        self.leSphinxOutputPath.setText(os.path.normpath(self.leSphinxOutputPath.text()))

    def on_leSphinxExecutable_editingFinished(self):
        self._updateleValidateSphinxExecutable()

    def _updateSphinxSettingMode(self):
        """Update the Sphinx settings mode by hiding/revealing the appropriate
        controls.
        """
        if core.config()['Sphinx']['AdvancedMode']:
            # Switch to advanced setting mode:
            # hide all path setting line edit boxes and buttons.
            for i in range(self.gridLtNotAdvancedSettings.count()):
                if self.gridLtNotAdvancedSettings.itemAt(i):
                    self.gridLtNotAdvancedSettings.itemAt(i).widget().setVisible(False)
            # Enable advanced setting mode items
            self.lbSphinxEnableAdvMode.setText('<html><head/><body><p>' +
            '<span style="text-decoration: underline;">Switch to Normal Mode' +
            '</span></p></body></html>')
            self.lbSphinxCmdline.setVisible(True)
            self.leSphinxCmdline.setVisible(True)
            self.lbSphinxReference.setVisible(True)
        else:
            # Reenable all path setting line edit boxes and buttons
            for i in range(self.gridLtNotAdvancedSettings.count()):
                if self.gridLtNotAdvancedSettings.itemAt(i):
                    self.gridLtNotAdvancedSettings.itemAt(i).widget().setVisible(True)
            # Hide all advanced mode entries.
            self.lbSphinxEnableAdvMode.setText('<html><head/><body><p>' +
              '<span style="text-decoration: underline;">Switch to Advanced Mode' +
              '</span></p></body></html>')
            self.lbSphinxCmdline.setVisible(False)
            self.leSphinxCmdline.setVisible(False)
            self.lbSphinxReference.setVisible(False)


# Plugin
# ======
# This class integrates the preview dock into Enki. Specifically, it:
#
# #. Adds the GUI defined above to the Settings dialog box
class Plugin(QObject):
    """Plugin interface implementation.
    """
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)

        self._dock = None
        self._saveAction = None
        self._dockInstalled = False
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged) # Disconnected.
        core.workspace().languageChanged.connect(self._onDocumentChanged) # Disconnected.

        # Install our CodeChat page into the settings dialog.
        core.uiSettingsManager().aboutToExecute.connect(
          self._onSettingsDialogAboutToExecute) # Disconnected.
        # Update preview dock when the settings dialog (which contains the
        # CodeChat enable checkbox) is changed.
        core.uiSettingsManager().dialogAccepted.connect(self._onDocumentChanged) # Disconnected.

        # Provide a "Set Sphinx Path" menu item.
        core.uiSettingsManager().dialogAccepted.connect(
          self._setSphinxActionVisibility)
        self._sphinxAction = QAction('Set Sphinx path', self._dock)
        self._sphinxAction.setShortcut(QKeySequence('Alt+Shift+S'))
        self._sphinxAction.triggered.connect(self.onSphinxPath)
        self._setSphinxActionVisibility()

        # If user's config .json file lacks it, populate CodeChat's default
        # config key and Sphinx's default config key.
        if not 'CodeChat' in core.config():
            core.config()['CodeChat'] = {}
            core.config()['CodeChat']['Enabled'] = False
            core.config().flush()
        if not 'Sphinx' in core.config():
            core.config()['Sphinx'] = {}
            core.config()['Sphinx']['Enabled'] = False
            core.config()['Sphinx']['Executable'] = u'sphinx-build'
            core.config()['Sphinx']['ProjectPath'] = u''
            core.config()['Sphinx']['BuildOnSave'] = False
            core.config()['Sphinx']['OutputPath'] = os.path.join('_build',
                                                                 'html')
            core.config()['Sphinx']['AdvancedMode'] = False
            core.config()['Sphinx']['Cmdline'] = ( u'sphinx-build -d ' +
              os.path.join('_build','doctrees') + ' . ' +
              os.path.join('_build', 'html') )
            core.config().flush()

    def del_(self):
        """Uninstall the plugin
        """
        if self._dockInstalled:
            self._removeDock()

        if self._dock is not None:
            self._dock.del_()

        core.workspace().currentDocumentChanged.disconnect(self._onDocumentChanged)
        core.workspace().languageChanged.disconnect(self._onDocumentChanged)
        core.uiSettingsManager().aboutToExecute.disconnect(
          self._onSettingsDialogAboutToExecute)
        core.uiSettingsManager().dialogAccepted.disconnect(
          self._onDocumentChanged)
        if self._dock:
            self._dock.closed.disconnect(self._onDockClosed)
            self._dock.shown.disconnect(self._onDockShown)
            self._saveAction.triggered.disconnect(self._dock.onPreviewSave)

    def _onDocumentChanged(self):
        """Document or Language changed.
        Create dock, if necessary
        """
        if self._canPreview(core.workspace().currentDocument()):
            if not self._dockInstalled:
                self._createDock()
        else:
            if self._dockInstalled:
                self._removeDock()

    def _canPreview(self, document):
        """Check if the given document can be shown in the Preview dock.
        """
        if document is None:
            return False

        if document.qutepart.language() in ('Markdown', 'Restructured Text') or \
           isHtmlFile(document):
            return True

        if canUseCodeChat(document.filePath()):
            return True

        if sphinxEnabledForFile(document.filePath()):
            return True

        return False

    def _createDock(self):
        """Install dock
        """
        # create dock
        if self._dock is None:
            from enki.plugins.preview.preview import PreviewDock
            self._dock = PreviewDock()
            self._dock.closed.connect(self._onDockClosed) # Disconnected.
            self._dock.shown.connect(self._onDockShown) # Disconnected.


            self._saveAction = QAction(QIcon(':enkiicons/save.png'),
                                       'Save Preview as HTML', self._dock)
            self._saveAction.setShortcut(QKeySequence("Alt+Shift+P"))
            self._saveAction.triggered.connect(self._dock.onPreviewSave) # Disconnected.

        core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)

        core.actionManager().addAction("mView/aPreview",
                                       self._dock.showAction())
        core.actionManager().addAction("mFile/aSavePreview", self._saveAction)
        core.actionManager().addAction('mTools/aSetSphinxPath',
                                       self._sphinxAction)
        self._dockInstalled = True
        if core.config()['Preview']['Enabled']:
            self._dock.show()

    def _onDockClosed(self):
        """Dock has been closed by user. Change Enabled option
        """
        if core.config()['Preview']['Enabled']:
            core.config()['Preview']['Enabled'] = False
            core.config().flush()

    def _onDockShown(self):
        """Dock has been shown by user. Change Enabled option
        """
        if not core.config()['Preview']['Enabled']:
            core.config()['Preview']['Enabled'] = True
            core.config().flush()

    def _removeDock(self):
        """Remove dock from GUI
        """
        core.actionManager().removeAction("mView/aPreview")
        core.actionManager().removeAction("mFile/aSavePreview")
        core.actionManager().removeAction('mTools/aSetSphinxPath')
        core.mainWindow().removeDockWidget(self._dock)
        self._dockInstalled = False

    def _onSettingsDialogAboutToExecute(self, dialog):
        """The UI settings dialog is about to execute. Install preview-related
           settings."""
        CodeChatSettingsWidget(dialog)
        SphinxSettingsWidget(dialog)

    @pyqtSlot()
    def _setSphinxActionVisibility(self):
        self._sphinxAction.setVisible(core.config()['Sphinx']['Enabled'])

    @pyqtSlot()
    def onSphinxPath(self):
        core.config()['Sphinx']['ProjectPath'] = os.getcwd()
        core.config().flush()
        if core.config()['Preview']['Enabled']:
            self._dock._scheduleDocumentProcessing()
