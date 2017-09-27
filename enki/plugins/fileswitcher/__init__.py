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
# TODO Populate dialog
# TODO Change file in dialog
# TODO change file in enki

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
        fileswitcher = QDialog(core.mainWindow())
        fileswitcher.resize(400, 200)
        fileswitcher.setModal(True)
        fileswitcher.setWindowTitle("File Switcher")
        vboxLayout = QVBoxLayout(fileswitcher)
        filelist = QTreeWidget(fileswitcher)
        filelist.setColumnCount(3)
        filelist.setHeaderLabels(["Name", "Type", "Path"])
        filelist.addTopLevelItem(QTreeWidgetItem(["File 1", "Type1", "Path 1"]))
        filelist.addTopLevelItem(QTreeWidgetItem(("File 2", "Type2", "Path 2")))
        filelist.addTopLevelItem(QTreeWidgetItem(("File 3", "Type3", "Path 3")))
        filelist.setRootIsDecorated(False)

        vboxLayout.addWidget(filelist)
        self._addAction()
        self._fileSwitcher = fileswitcher


    def terminate(self):
        core.actionManager().removeAction(self._action)

    def _addAction(self):
        """Add action to main menu
        """
        action = core.actionManager().addAction("mNavigation/aFileSwitcher",
                                                "File Switcher",
                                                QIcon(':enkiicons/console.png'))
        core.actionManager().setDefaultShortcut(action, "Ctrl+Tab")
        action.triggered.connect(self._showFileswitcher)
        self._action = action

    def _showFileswitcher(self):
        self._fileSwitcher.show()
