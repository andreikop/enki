"""
project --- Open project and manage it
======================================

:class:`enki.core.project.Project`
"""

import os

from PyQt4.QtCore import QObject, QThread, pyqtSignal

from enki.core.core import core


class _ScannerThread(QThread):
    itemsReady = pyqtSignal(list)

    def __init__(self, parent, path):
        QThread.__init__(self, parent)
        self._path = path
        self._stop = False

    def run(self):
        results = []

        filterRe = core.fileFilter().regExp()

        for root, dirnames, filenames in os.walk(self._path):
            if self._stop:
                break
            for pattern in '.git', '.svn':
                if pattern in dirnames:
                    dirnames.remove(pattern)
            for filename in filenames:
                if not filterRe.match(filename):
                    results.append(os.path.relpath(os.path.join(root, filename), self._path))

        if not self._stop:
            self.itemsReady.emit(results)

    def stop(self):
        self._stop = True


class Project(QObject):

    changed = pyqtSignal(unicode)
    """
    chagned(projectPath)

    **Signal** emitted, when project path is changed
    """

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._path = None
        self._projectFiles = []
        self._thread = None
        self.open(os.path.abspath('.'))

    def del_(self):
        self._stopScannerThread()

    def _startScannerThread(self):
        assert self._thread is None
        self._thread = _ScannerThread(self, self._path)
        self._thread.itemsReady.connect(self._onFilesReady)
        self._thread.start()

    def _stopScannerThread(self):
        if self._thread is not None:
            self._thread.stop()
            self._thread.wait()
            self._thread = None

    def open(self, path):
        """Open project.
        Replaces previous opened project
        """
        self._stopScannerThread()
        self._path = path
        self._projectFiles = []
        self._startScannerThread()
        self.changed.emit(path)

    def path(self):
        """Current project path.

        Can be `None` if no project is opened
        """
        return self._path

    def files(self):
        """List of project files

        Empty list if not loaded yet
        """
        return self._projectFiles

    def _onFilesReady(self, files):
        self._projectFiles = files
        self._stopScannerThread()
