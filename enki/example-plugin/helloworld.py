from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QWidget

# core is main enki.core singletone. It is usually used for getting pointers to other singletones
from enki.core.core import core

import enki.widgets.dockwidget

__pluginname__ = "Hello World"
__author__ = "Hello Author"
__version__ = "0.0.1"

class MyDock(enki.widgets.dockwidget.DockWidget):

    def __init__(self):
        enki.widgets.dockwidget.DockWidget.__init__(self, core.mainWindow(),
                                                    "Hello dock",
                                                    QIcon(":enkiicons/help.png"),
                                                    "Alt+H")
        self.label = QLabel("This is Hello World dock")
        self.setWidget(self.label)


from enki.core.uisettings import TextOption


class SettingsPage(QWidget):
    """Settings page for Hello World plugin
    """

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._layout = QHBoxLayout(self)
        self._label = QLabel("Very important option", self)
        self._layout.addWidget(self._label)
        self.edit = QLineEdit(self)
        self._layout.addWidget(self.edit)


class Plugin:
    """During initialization, core imports all modules and packages in **enki/plugins** directory,
    searches for **Plugin** class in every module and creates an instance
    """

    def __init__(self):
        QMessageBox.information(core.mainWindow(), "Hello, world", "Plugin loaded")
        self._addAction()
        self._createDock()
        self._readSettings()

        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)

        core.uiSettingsManager().dialogAccepted.connect(self._applySettings)
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

    def terminate(self):
        """This method is called by core for each plugin during termination
        """
        core.actionManager().removeAction(self._action)
        QMessageBox.information(core.mainWindow(), "Hello, world", "Plugin terminated")


    def _addAction(self):
        """Add action to main menu
        This action uses embedded icons. You can find list of icons in **icons** directory at project root
        """
        self._action = core.actionManager().addAction("mHelp/aSayHello", 'Say Hello...', QIcon(':/enkiicons/logo/32x32/enki.png'))
        core.actionManager().setDefaultShortcut(self._action, "Ctrl+Alt+Shift+H")
        self._action.triggered.connect(self._sayHello)

    def _sayHello(self):
        """Handler for main menu action
        """
        QMessageBox.information(core.mainWindow(), "Hello, world", "Menu action has been triggered!")

    def _createDock(self):
        """Create dock widget and add it to main window
        """
        self._dock = MyDock()
        core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)

    def _readSettings(self):
        """Read settings from core configuration file
        """
        if not "HelloWorld" in core.config():
            core.config()["HelloWorld"] = {}
            core.config()["HelloWorld"]["VeryImportantOption"] = "the correct value"
        self._dock.label.setText('Option value: %s' % core.config()["HelloWorld"]["VeryImportantOption"])

    def _writeSettings(self):
        """This method is never called.
        Just an example implementation
        """
        core.config()["HelloWorld"]["VeryImportantOption"] = "new value"
        # Don't forget to flush config!
        # if settings has been edited with main settings dialogue, it will be flushed automatically
        core.config().flush()

    def _onDocumentChanged(self, old, new):
        """Current document has been changed. Let's notify the user
        """
        if new is not None:
            core.mainWindow().appendMessage("Current file is '%s'" % new.fileName(), 1000)

    def _applySettings(self):
        """Apply settings. Called by configurator class
        """
        self._dock.label.setText('Option value: %s' % core.config()["HelloWorld"]["VeryImportantOption"])

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        page = SettingsPage(dialog)
        dialog.appendPage("Hello World", page, QIcon(':/enkiicons/help.png'))

        # Options
        dialog.appendOption(TextOption(dialog, core.config(), "HelloWorld/VeryImportantOption", page.edit))
