#!/usr/bin/env python

import os
import os.path

from PyQt4.QtCore import QEvent, QAbstractListModel, QThread, Qt, pyqtSignal
from PyQt4.QtGui import QApplication, QDialog
from PyQt4 import uic

from enki.lib.htmldelegate import HTMLDelegate

from enki.core.core import core


def fuzzyMatch(pattern, text):
    """Match text with pattern and return
        (score, list of matching indexes)
        or None

    Score is a summa or distances of continuos matched peaces from the end of the text.
    Less peaces -> better mathing
    Peaces close to the end -> better matching

    Reverse mathing is used because symbols at the end of the path are usually more impotant.
    """
    iter_text = reversed(list(enumerate(text)))
    indexes = []

    sequence_start_indexes = []

    prev_matched = False
    for pattern_char in reversed(pattern):
        for text_index, text_char in iter_text:
            if pattern_char == text_char:
                if not prev_matched:  # start of sequence of matched symbols
                    sequence_start_indexes.append(text_index)
                    prev_matched = True
                indexes.append(text_index)
                break
            else:
                prev_matched = False

        else:
            return None

    if indexes:
        score = sum([len(text) - index for index in sequence_start_indexes])
        return (score, indexes)
    else:
        return None


class ScannerThread(QThread):
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


class ListModel(QAbstractListModel):
    def __init__(self, path):
        QAbstractListModel.__init__(self)
        self._items = []  # list of (text, indexes)
        self._message = '<i>loading</i>'

        biggerFont = QApplication.font().pointSizeF() * 1.5
        self._itemTemplate = ('<span style="font-size:{biggerFont}pt;">{{}}</span>'
                              '<div style="margin: 10px;">{{}}</div>'.format(biggerFont=biggerFont))

    def terminate(self):
        self._thread.stop()

    def rowCount(self, index):
        if self._message:
            return 1
        else:
            return len(self._items)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if self._message:
                return self._message
            else:
                path, score, indexes = self._items[index.row()]
                basename = os.path.basename(path)
                chars = ['<b>{}</b>'.format(char) if charIndex in indexes else char
                            for charIndex, char in enumerate(path)]
                pathFormatted = ''.join(chars)
                basenameFormatted = ''.join(chars[-len(basename):])
                return self._itemTemplate.format(basenameFormatted, pathFormatted)

    def setItems(self, items):
        self.beginResetModel()
        if len(items) > 10000:
            self._message = '<i>many</i>'
        else:
            self._message = None
        self._items = items
        self.endResetModel()

    def path(self, index):
        return self._items[index.row()][0]


class FuzzyOpener(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'fuzzyopen.ui'), self)

        self._pathList = []

        path = core.workspace().projectPath()

        self._model = ListModel(path)

        self._thread = ScannerThread(self, path)
        self._thread.itemsReady.connect(self._onPathListReady)
        self._thread.start()

        self.listView.setModel(self._model)
        self.listView.setItemDelegate(HTMLDelegate())

        self.lineEdit.textEdited.connect(self._updateModel)
        self.lineEdit.returnPressed.connect(self._onEnter)
        self.lineEdit.installEventFilter(self)  # catch Up, Down

        self.setWindowTitle(path)
        self.show()

    def terminate(self):
        self._thread.stop()

    def _onPathListReady(self, pathList):
        self._pathList = pathList
        self._updateModel()

    def _updateModel(self):
        pattern = self.lineEdit.text()
        if pattern:
            matching = []
            for path in self._pathList:
                res = fuzzyMatch(pattern, path)
                if res is not None:
                    score, indexes = res
                    matching.append((path, score, indexes))

            matching.sort(key=lambda item: item[1])  # sort starting from minimal score
            self._model.setItems(matching)
        else:
            self._model.setItems([(item, 0, []) for item in self._pathList])
        self.listView.setCurrentIndex(self._model.createIndex(0, 0))

    def _onEnter(self):
        index = self.listView.currentIndex()
        if index.isValid():
            path = self._model.path(index)
            core.workspace().openFile(path)
            self.accept()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and \
           event.key() in (Qt.Key_Up, Qt.Key_Down):
            self.listView.event(event)
            return True
        else:
            return False
