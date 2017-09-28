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
# TODO Change file backward
# TODO change styling
# TODO Setting page
# TODO checkbox if autosave is activated,
# TODO Cleanup code (Terminate plugin, etc.)

from pprint import pprint

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QTreeWidget, QTreeWidgetItem, QWidget, QCheckBox, QVBoxLayout,
                             QSpacerItem, QSizePolicy, QLabel)
from PyQt5.QtGui import QIcon


from enki.core.core import core
from enki.core.uisettings import CheckableOption

class Plugin:
    """Plugin interface implementation

    The plugin looks for focusWindowChanged event, get all opened files
    and saves them.
    """

    def __init__(self):
        """pass"""
        self._fileswitcher = Fileswitcher(core.mainWindow())
        self._addAction()

    def terminate(self):
        core.actionManager().removeAction(self._action)

    def _addAction(self):
        """Add action to main menu
        """
        action = core.actionManager().addAction("mNavigation/aFileSwitcher",
                                                "File Switcher",
                                                QIcon(':enkiicons/console.png'))
        core.actionManager().setDefaultShortcut(action, "Ctrl+Tab")
        action.triggered.connect(self._fileswitcher._showFileswitcher)
        self._action = action

class Fileswitcher(QDialog):
    """docstring for Fileswitcher."""
    def __init__(self, parent):
        super(Fileswitcher, self).__init__(parent)
        self._filestack = list()

        self.resize(400, 200)
        self.setModal(True)
        self.setWindowTitle("File Switcher")
        vboxLayout = QVBoxLayout(self)
        filelist = QTreeWidget(self)
        filelist.setColumnCount(3)
        filelist.setHeaderLabels(["Name", "Type", "Path"])
        filelist.setRootIsDecorated(False)
        filelist.setAlternatingRowColors(True)

        vboxLayout.addWidget(filelist)

        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().documentClosed.connect(self._onDocumentClosed)
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)

        self._filelist = filelist

    def _showFileswitcher(self):
        self._filelist.clear()
        for document in self._filestack:
            self._filelist.addTopLevelItem(
            QTreeWidgetItem((document.fileName(), "Type", document.filePath())))
            # pprint(dir(document))
        self._currentLine = 1
        self._filelist.setCurrentItem(
            self._filelist.topLevelItem(self._currentLine))
        self.show()

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
        #super(Fileswitcher, self).keyPressEvent(event)
        if (event.modifiers() & Qt.CTRL and event.key() == Qt.Key_Tab):
            if self._currentLine < self._filelist.topLevelItemCount() - 1:
                self._currentLine += 1
            else:
                self._currentLine = 0
            self._filelist.setCurrentItem(
                self._filelist.topLevelItem(self._currentLine))

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            core.workspace().setCurrentDocument(
                self._filestack[self._currentLine])
            self._currentLine = None
            self.hide()
