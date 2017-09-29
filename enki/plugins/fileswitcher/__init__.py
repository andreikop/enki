#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file switcher --- switches through all files Opera style
=============================================================

@author: Marco Laspe <marco@rockiger.com>

Released under the GPL2 license
https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
"""
# DONE Create dialog
# DONE Populate dialog
# DONE Change file in dialog
# DONE change file in enki
# DONE Change file backward
# DONE change styling
# DONE Settings page
# DONE checkbox if file switcher is activated
# DONE grey out menu items, if no file is opened
# TODO Cleanup code (Terminate plugin, etc.)

from os.path import expanduser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QTreeWidget, QTreeWidgetItem, QWidget,
                             QCheckBox, QVBoxLayout, QSpacerItem, QSizePolicy,
                             QLabel)
from PyQt5.QtGui import QIcon, QFontMetrics


from enki.core.core import core
from enki.core.uisettings import CheckableOption

class SettingsPage(QWidget):
    """Settings page for File Switcher plugin"""
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        text = """
            <h2>File Switcher</h2>
            <p>The File Switcher plugin let's you switch through your files. In the style of the Opera web browser it stacks the files in the order of last used files.</p>
            <p></p>"""
        self._label = QLabel(text, self)
        self.checkbox = QCheckBox('Enable File Switcher')
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self.checkbox)
        self._layout.addSpacerItem(QSpacerItem(0, 0,
                                               QSizePolicy.MinimumExpanding,
                                               QSizePolicy.MinimumExpanding))


class Plugin:
    """Plugin interface implementation

    The plugin looks for focusWindowChanged event, get all opened files
    and saves them.
    """

    def __init__(self):
        """pass"""
        self._fileswitcher = None
        self._checkSettings()
        core.uiSettingsManager().aboutToExecute.connect(
            self._onSettingsDialogAboutToExecute)
        core.uiSettingsManager().dialogAccepted.connect(
            self._onSettingsDialogAccepted)

        if self._isFileswitcherActive():
            self._activate()


    def terminate(self):
        self._removeActions()
        core.uiSettingsManager().aboutToExecute.disconnect(
            self._onSettingsDialogAboutToExecute)

    def _activate(self):
        self._fileswitcher = Fileswitcher(core.mainWindow())
        self._addActions()
        core.workspace().documentOpened.connect(self._onDocumentOpenedOrClosed)
        core.workspace().documentClosed.connect(self._onDocumentOpenedOrClosed)

    def _deactivate(self):
        self._fileswitcher = None
        self._removeActions()
        core.workspace().documentOpened.disconnect(self._onDocumentOpenedOrClosed)
        core.workspace().documentClosed.disconnect(self._onDocumentOpenedOrClosed)

    def _addActions(self):
        """Add action to main menu
        """
        forwardAction = core.actionManager().addAction("mNavigation/aForwardSwitch",
                                                "Switch file forward")
        core.actionManager().setDefaultShortcut(forwardAction, "Ctrl+Tab")
        backwardAction = core.actionManager().addAction("mNavigation/aBackwardSwitch",
                                                "Switch file back")
        core.actionManager().setDefaultShortcut(backwardAction, "Ctrl+Shift+Tab")
        forwardAction.triggered.connect(self._onForwardAction)
        backwardAction.triggered.connect(self._onBackwardAction)
        self._forwardAction = forwardAction
        self._backwardAction = backwardAction

    def _removeActions(self):
        core.actionManager().removeAction(self._forwardAction)
        core.actionManager().removeAction(self._backwardAction)

    def _onForwardAction(self):
        self._fileswitcher.showFileswitcher(1)

    def _onBackwardAction(self):
        self._fileswitcher.showFileswitcher(
            self._fileswitcher.filestackLength() - 1)

    def _onDocumentOpenedOrClosed(self):
        # update view menu
        moreThanOneDocument = len(core.workspace().documents()) > 0
        core.actionManager().action("mNavigation/aForwardSwitch").setEnabled(moreThanOneDocument)
        core.actionManager().action("mNavigation/aBackwardSwitch").setEnabled(moreThanOneDocument)

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        page = SettingsPage(dialog)
        dialog.appendPage(u"File Switcher", page)

        # Options
        dialog.appendOption(CheckableOption(dialog, core.config(),
                                            "Fileswitcher/Active",
                                            page.checkbox))

    def _onSettingsDialogAccepted(self):
        if self._isFileswitcherActive():
            if self._fileswitcher == None:
                self._activate()
        else:
            if self._fileswitcher != None:
                self._deactivate()

    def _checkSettings(self):
        """Check if settings are present in the core configuration file,
        else create and return them.
        """
        if "Fileswitcher" not in core.config():
            core.config()["Fileswitcher"] = {}
            core.config()["Fileswitcher"]["Active"] = False
        return core.config()["Fileswitcher"]["Active"]

    def _isFileswitcherActive(self):
        """Return if file switcher is enabled"""
        return core.config()["Fileswitcher"]["Active"]


class Fileswitcher(QDialog):
    """docstring for Fileswitcher."""
    def __init__(self, parent):
        super(Fileswitcher, self).__init__(parent)
        self._filestack = list()
        self.populateFilestack()

        self.resize(600, 300)
        self.setModal(True)
        self.setWindowTitle("File Switcher")
        biggerFont = self.font()
        biggerFont.setPointSizeF(biggerFont.pointSizeF() * 1.5)
        self.setFont(biggerFont)
        width = QFontMetrics(self.font()).width('x' * 96)  # width of 64 'x' letters
        self.resize(width, width * 0.62)

        vboxLayout = QVBoxLayout(self)
        filelist = QTreeWidget(self)
        filelist.setColumnCount(2)
        filelist.setHeaderLabels(["Name", "Path"])
        filelist.setRootIsDecorated(False)
        filelist.setAlternatingRowColors(True)
        filelist.header().setFont(biggerFont)
        filelist.setFont(biggerFont)
        vboxLayout.addWidget(filelist)

        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().documentClosed.connect(self._onDocumentClosed)
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)

        self._filelist = filelist

    def filestackLength(self):
        return len(self._filestack)

    def showFileswitcher(self, currentLine = 1):
        if self.filestackLength() > 0:
            self._filelist.clear()
            for document in self._filestack:
                self._filelist.addTopLevelItem(
                QTreeWidgetItem((document.fileName(),
                                 document.filePath().replace(
                                                             expanduser("~"),
                                                             "~"))))
            self._filelist.resizeColumnToContents(0)

            self._currentLine = self.filestackLength() - 1 \
                if self.filestackLength() >= currentLine else currentLine
            self._filelist.setCurrentItem(
                self._filelist.topLevelItem(self._currentLine))
            self.show()

    def populateFilestack(self):
        for document in core.workspace().documents():
            self._filestack.insert(0, document)

    def _onDocumentOpened(self, document):
        self._filestack.insert(0, document)

    def _onDocumentClosed(self, document):
        idx = self._filestack.index(document)
        self._filestack.pop(idx)

    def _onDocumentChanged(self, old, new):
        try:
            idx = self._filestack.index(new)
            self._filestack.pop(idx)
            self._filestack.insert(0, new)
        except ValueError as e:
            print("new document couldn't be found")
            print(e)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.CTRL and event.key() == Qt.Key_Tab:
            print(event.modifiers())
            if self._currentLine < self._filelist.topLevelItemCount() - 1:
                self._currentLine += 1
            else:
                self._currentLine = 0
            self._filelist.setCurrentItem(
                self._filelist.topLevelItem(self._currentLine))

        elif event.modifiers() & Qt.CTRL and event.key() == Qt.Key_Backtab:
            if self._currentLine > 0:
                self._currentLine -= 1
            else:
                self._currentLine = self._filelist.topLevelItemCount() - 1
            self._filelist.setCurrentItem(
                self._filelist.topLevelItem(self._currentLine))

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            core.workspace().setCurrentDocument(
                self._filestack[self._currentLine])
            self._currentLine = None
            self.hide()
