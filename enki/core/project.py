"""
project --- Open project and manage it
======================================

:class:`enki.core.project.Project`
"""

import os
import os.path
import time

from PyQt4.QtCore import QObject, QThread, pyqtSignal

from enki.core.core import core


STATUS_UPDATE_TIMEOUT_SEC = 0.25
STATUS_SHOW_TIMEOUT_MSEC = 3000


class _ScannerThread(QThread):
    itemsReady = pyqtSignal(str, list)
    status = pyqtSignal(str)

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

            # remove not interesting directories
            for dirname in dirnames[:]:
                if filterRe.match(dirname):
                    dirnames.remove(dirname)

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

    changed = pyqtSignal(str)
    """
    chagned(projectPath)

    **Signal** emitted, when project path is changed
    """

    filesReady = pyqtSignal()
    """
    filesReady()

    **Signal** emitted, when list of project files has been loaded
    """
    scanStatusChanged = pyqtSignal(str)
    """
    scanStatusChanged()

    **Signal** is periodically emited during FS scanning.
    Parameter contains readable text
    """

    def __init__(self, core):
        QObject.__init__(self, core)
        self._path = None
        self._projectFiles = None
        self._thread = None
        self._scanStatus = None
        self._core = core
        self.open(os.path.abspath('.'))
        core.fileFilter().regExpChanged.connect(self._onFileFilterChanged)

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
        path = os.path.normpath(path)
        if self._path == path:
            return

        self._stopScannerThread()
        self._path = path
        self._projectFiles = None
        self._scanStatus = 'Not scanning'
        self._backgroundScan = False

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
        if self._thread is None and self._projectFiles is None:
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

    def startBackgroundScan(self):
        """Scan the project in background.

        Report progress to status bar.
        It is allowed to call this method multiple times.
        """
        if self._thread is not None:
            return

        self._backgroundScan = True
        self._startScannerThread()

    def isScanning(self):
        return self._thread is not None

    def _onScanStatus(self, text):
        self._scanStatus = text
        self.scanStatusChanged.emit(text)
        if self._backgroundScan:
            self._core.mainWindow().statusBar().showMessage(text,
                                                            STATUS_SHOW_TIMEOUT_MSEC)

    def _onFilesReady(self, path, files):
        self._projectFiles = files
        self._backgroundScan = False
        self._stopScannerThread()
        self.filesReady.emit()

    def _onFileFilterChanged(self):
        if self.isScanning():
            self._stopScannerThread()
            self._startScannerThread()
        else:
            self._projectFiles = None
