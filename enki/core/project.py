"""
project --- Open project and manage it
======================================

:class:`enki.core.project.Project`
"""

import os
import time

from PyQt4.QtCore import QObject, QThread, pyqtSignal

from enki.core.core import core


STATUS_UPDATE_TIMEOUT_SEC = 0.25
STATUS_SHOW_TIMEOUT_MSEC = 3000


class _ScannerThread(QThread):
    itemsReady = pyqtSignal(unicode, list)
    status = pyqtSignal(unicode)

    def __init__(self, parent, path):
        QThread.__init__(self, parent)
        self._path = path
        self._stop = False

    def run(self):
        results = []

        filterRe = core.fileFilter().regExp()

        basename = os.path.basename(self._path)
        lastUpdateTime = time.time()

        self.status.emit('Scanning {}: {} files found'.format(basename, len(results)))

        for root, dirnames, filenames in os.walk(self._path):
            if self._stop:
                break
            for pattern in '.git', '.svn':
                if pattern in dirnames:
                    dirnames.remove(pattern)
            for filename in filenames:
                if not filterRe.match(filename):
                    results.append(os.path.relpath(os.path.join(root, filename), self._path))
            if time.time() - lastUpdateTime > STATUS_UPDATE_TIMEOUT_SEC:
                self.status.emit('Scanning {}: {} files found'.format(basename, len(results)))
                lastUpdateTime = time.time()

        if not self._stop:
            self.status.emit('Scanning {} done: {} files found'.format(basename, len(results)))
            self.itemsReady.emit(self._path, results)

    def stop(self):
        self._stop = True


class Project(QObject):

    changed = pyqtSignal(unicode)
    """
    chagned(projectPath)

    **Signal** emitted, when project path is changed
    """

    filesReady = pyqtSignal()
    """
    filesReady()

    **Signal** emitted, when list of project files has been loaded
    """
    scanStatusChanged = pyqtSignal(unicode)
    """
    scanStatusChanged()

    **Signal** is periodically emited during FS scanning.
    Parameter contains readable text
    """

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._path = None
        self._projectFiles = None
        self._thread = None
        self._scanStatus = None
        self.open(os.path.abspath('.'))

    def del_(self):
        self._stopScannerThread()

    def _startScannerThread(self):
        assert self._thread is None
        self._thread = _ScannerThread(self, self._path)
        self._thread.itemsReady.connect(self._onFilesReady)
        self._thread.status.connect(self._onScanStatus)
        self._scanStatus = ''
        self._thread.start()

    def _stopScannerThread(self):
        if self._thread is not None:
            self._thread.stop()
            self._thread.wait()
            self._thread.itemsReady.disconnect(self._onFilesReady)
            self._thread.status.disconnect(self._onScanStatus)
            self._thread = None

    def open(self, path):
        """Open project.
        Replaces previous opened project
        """
        self._stopScannerThread()
        self._path = path
        self._projectFiles = None
        self._scanStatus = 'Not scanning'

        try:
            os.chdir(path)
        except:
            pass

        self.changed.emit(path)

    def path(self):
        """Current project path.

        Can be `None` if no project is opened
        """
        return self._path

    def files(self):
        """List of project files

        ``None`` if not loaded yet
        """
        return self._projectFiles

    def startLoadingFiles(self):
        """Start asyncronous loading project files.

        It is allowed to call this method multiple times.
        """
        if self._thread is None:
            self._startScannerThread()

    def cancelLoadingFiles(self):
        """Cancel asyncronous loading project files.

        It is allowed to call this method multiple times.

        If files are already loaded, they will be kept.
        """
        if self._thread is not None:
            self._stopScannerThread()

    def scanStatus(self):
        """Get scanning status as text message
        """
        return self._scanStatus

    def _onScanStatus(self, text):
        self._scanStatus = text
        self.scanStatusChanged.emit(text)

    def _onFilesReady(self, path, files):
        self._projectFiles = files
        self._stopScannerThread()
        self.filesReady.emit()
