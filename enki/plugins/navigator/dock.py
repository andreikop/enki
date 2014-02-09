"""Navigator dock implementation.
Contains tag model class
"""

import fnmatch

from PyQt4.QtCore import pyqtSignal, Qt, QEvent, QTimer,  QAbstractItemModel, QModelIndex
from PyQt4.QtGui import QApplication, QBrush, QColor, QVBoxLayout, QIcon, QLabel, QLineEdit, \
                        QTreeView, QWidget

from enki.widgets.dockwidget import DockWidget
from enki.core.core import core

from enki.widgets.lineedit import LineEdit

import ctags


def _tagPath(tag):
    if tag is None:
        return ''
    elif tag.parent is None:
        return tag.name
    else:
        return _tagPath(tag.parent) + '.' + tag.name


class _TagModel(QAbstractItemModel):
    jumpToTagDone = pyqtSignal()

    def __init__(self, *args):
        QAbstractItemModel.__init__(self, *args)
        self._tags = []

        self._currentTagIndex = QModelIndex()

        defBaseColor = QApplication.instance().palette().base().color()
        # yellow or maroon
        brightBg = QColor('#ffff80') if defBaseColor.lightnessF() > 0.5 else QColor('#800000')
        self._currentTagBrush = QBrush(brightBg)

        core.workspace().cursorPositionChanged.connect(self._onCursorPositionChanged)
        self._updateCurrentTagTimer = QTimer()
        self._updateCurrentTagTimer.setInterval(300)
        self._updateCurrentTagTimer.timeout.connect(self._updateCurrentTagAndEmitSignal)

    def setTags(self, tags):
        self.beginResetModel()
        self._tags = tags
        self._updateCurrentTag(False)
        self.endResetModel()

    def _onCursorPositionChanged(self):
        """If position is updated on every key pressing - cursor movement might be slow
        Update position, when movement finished
        """
        self._updateCurrentTagTimer.stop()
        self._updateCurrentTagTimer.start()

    def _updateCurrentTagAndEmitSignal(self):
        self._updateCurrentTag(True)

    def _updateCurrentTag(self, emitChanged):
        old = self._currentTagIndex

        # Workspace might be None, if core terminated
        if core.workspace() is not None and \
           core.workspace().currentDocument() is not None:
            lineNumber = core.workspace().currentDocument().qutepart.cursorPosition[0]
            self._currentTagIndex = self._indexForLineNumber(lineNumber)
        else:
            self._currentTagIndex = QModelIndex()

        if emitChanged:
            if old != self._currentTagIndex and \
               old.isValid():
               self.dataChanged.emit(old, old)
            if self._currentTagIndex.isValid():
                self.dataChanged.emit(self._currentTagIndex, self._currentTagIndex)

    def index(self, row, column, parent):
        if row < 0 or column != 0:
            return QModelIndex()

        if not parent.isValid():  # top level
            if row < len(self._tags):
                return self.createIndex(row, column, self._tags[row])
            else:
                return QModelIndex()
        else:  # nested
            parentTag = parent.internalPointer()
            if row < len(parentTag.children):
                return self.createIndex(row, column, parentTag.children[row])
            else:
                return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        tag = index.internalPointer()
        if tag.parent is not None:
            parent = tag.parent
            if parent.parent:
                try:
                    row = parent.parent.children.index(parent)
                except ValueError:
                    return QModelIndex()
            else:
                try:
                    row = self._tags.index(parent)
                except ValueError:
                    return QModelIndex()

            return self.createIndex(row, 0, parent)
        else:
            return QModelIndex()

    def rowCount(self, index):
        if index.isValid():
            tag = index.internalPointer()
            return len(tag.children)
        else:
            return len(self._tags)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            tag = index.internalPointer()
            return tag.name
        elif role == Qt.BackgroundRole:
            return self._currentTagBrush if index == self._currentTagIndex else None
        else:
            return None

    def onActivated(self, index):
        tag = index.internalPointer()

        document = core.workspace().currentDocument()
        if document is not None:
            core.workspace().cursorPositionChanged.disconnect(self._onCursorPositionChanged)
            document.qutepart.cursorPosition = (tag.lineNumber, 0)
            core.workspace().cursorPositionChanged.connect(self._onCursorPositionChanged)
            self._updateCurrentTagAndEmitSignal()

            document.qutepart.centerCursor()
            document.qutepart.setFocus()
            self.jumpToTagDone.emit()

    def tagPathForIndex(self, index):
        tag = index.internalPointer()
        return _tagPath(tag)

    def indexForTagPath(self, tagPath):
        def findTag(tagList, name):
            for tag in tagList:
                if tag.name == name:
                    return tag
            else:
                return None

        def findPath(currentTag, childTags, parts):
            if not parts:
                return currentTag

            part = parts[0]
            tag = findTag(childTags, part)
            if tag is not None:
                return findPath(tag, tag.children, parts[1:])
            else:
                return currentTag

        parts = tagPath.split('.')
        tag = findPath(None, self._tags, parts)
        if tag is not None:
            row = tag.parent.children.index(tag) if tag.parent else self._tags.index(tag)
            return self.createIndex(row, 0, tag)
        else:
            return QModelIndex()

    def _indexForLineNumber(self, number):

        def recursiveTagGenerator(tags):
            for childRow, childTag in enumerate(tags):
                yield childRow, childTag
                for gcRow, grandChild in recursiveTagGenerator(childTag.children):
                    yield gcRow, grandChild

        prevRow, prevTag = None, None
        for row, tag in recursiveTagGenerator(self._tags):
            if tag.lineNumber == number:
                return self.createIndex(row, 0, tag)
            elif tag.lineNumber > number and \
                 prevTag is not None and \
                 prevTag.lineNumber <= number:
                return self.createIndex(prevRow, 0, prevTag)
            else:
                prevRow, prevTag = row, tag
        else:
            if prevTag is not None and \
               prevTag.lineNumber <= number: # the last tag is current
                return self.createIndex(prevRow, 0, prevTag)

        return QModelIndex()


def _filterTag(wildcard, tag, parent):
    """Filter tag by returning NEW tag, which matches the filter.
    Original tag is not modified
    """
    newTag = ctags.Tag(tag.type, tag.name, tag.lineNumber, parent)

    children = _filterTags(wildcard, tag.children, newTag)

    if children or fnmatch.fnmatch(tag.name.lower(), wildcard):
        newTag.children = children
        return newTag
    else:
        return None


def _filterTags(wildcard, tags, parent=None):
    """Filter tags by returning list of NEW tags,
    which match filter.
    Original tags are not modified
    """
    res = []
    for tag in tags:
        filteredTag = _filterTag(wildcard, tag, parent)
        if filteredTag is not None:
            res.append(filteredTag)

    return res


def _findFirstMatching(wildcard, filteredTags):
    """Find first tag, which matches whildcard.
    It is assumed, that tags are filtered and not empty
    """
    assert filteredTags
    firstTag = filteredTags[0]

    if fnmatch.fnmatch(firstTag.name.lower(), wildcard):
        return firstTag
    else:
        return _findFirstMatching(wildcard, firstTag.children)


class NavigatorDock(DockWidget):

    closed = pyqtSignal()

    def __init__(self):
        DockWidget.__init__(self, core.mainWindow(), '&Navigator', QIcon(':/enkiicons/goto.png'), "Alt+N")

        self._tags = []

        self._tree = QTreeView(self)
        self._tree.installEventFilter(self)
        self._tree.setHeaderHidden(True)
        self.setFocusProxy(self._tree)

        self._filterEdit = LineEdit(self)
        self._filterEdit.setClearButtonVisible(True)
        self._filterEdit.textEdited.connect(self._applyFilter)
        self._filterEdit.clearButtonClicked.connect(self._applyFilter)
        self._filterEdit.clearButtonClicked.connect(self._tree.setFocus)
        self._filterEdit.clearButtonClicked.connect(self._hideFilter)
        self._filterEdit.installEventFilter(self)

        self._displayWidget = QWidget(self)
        layout = QVBoxLayout(self._displayWidget)
        layout.addWidget(self._tree)
        layout.addWidget(self._filterEdit)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setWidget(self._displayWidget)

        self._tagModel = _TagModel(self._tree)
        self._tagModel.jumpToTagDone.connect(self._hideFilter)

        self._tree.setModel(self._tagModel)
        self._tree.activated.connect(self._tagModel.onActivated)
        self._tree.clicked.connect(self._tagModel.onActivated)
        self._tagModel.modelAboutToBeReset.connect(self._onModelAboutToBeReset)
        self._tagModel.modelReset.connect(self._onModelReset)
        self._currentTagPath = None

        self._errorLabel = None

        self._installed = False

    def install(self):
        if not self._installed:
            core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self)
            core.actionManager().addAction("mView/aNavigator", self.showAction())
            self._installed = True

    def remove(self):
        if self._installed:
            core.mainWindow().removeDockWidget(self)
            core.actionManager().removeAction("mView/aNavigator")
            self.hide()
            self._installed = False

    def setTags(self, tags):
        self._tags = tags
        self._setFilteredTags(tags)
        self._hideFilter()

        if self.widget() is not self._displayWidget:
            self.setWidget(self._displayWidget)
            self._displayWidget.show()
        if self._errorLabel is not None:
            self._errorLabel.hide()

    def _setFilteredTags(self, tags):
        self._tagModel.setTags(tags)

    def onError(self, error):
        self._displayWidget.hide()
        if self._errorLabel is None:
            self._errorLabel = QLabel(self)
            self._errorLabel.setWordWrap(True)

        self._errorLabel.setText(error)

        if not self.widget() is self._errorLabel:
            self.setWidget(self._errorLabel)
            self._errorLabel.show()
            self._displayWidget.hide()

    def closeEvent(self, event):
        """Widget is closed.
        Probably should update enabled state
        """
        self.closed.emit()
        self.setTags([])

    def _onModelAboutToBeReset(self):
        currIndex = self._tree.currentIndex()
        self._currentTagPath = self._tagModel.tagPathForIndex(currIndex) if currIndex.isValid() else None

    def _onModelReset(self):
        self._tree.expandAll()

        # restore current item
        if self._currentTagPath is not None:
            index = self._tagModel.indexForTagPath(self._currentTagPath)
            if index.isValid():
                self._tree.setCurrentIndex(index)

    def eventFilter(self, object_, event ):
        if object_ is self._tree:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Backspace:
                    if event.modifiers() == Qt.ControlModifier:
                        self._onTreeCtrlBackspace()
                    else:
                        self._onTreeBackspace()
                    return True
                elif event.text() and \
                     (event.text().isalnum() or event.text() == '_'):
                    self._onTreeTextTyped(event.text())
                    return True
        elif object_ is self._filterEdit:
            if event.type() == QEvent.KeyPress:
                if event.key() in (Qt.Key_Up, Qt.Key_Down):
                    self._tree.setFocus()
                    self._tree.event(event)
                    return True
                elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
                    currIndex = self._tree.currentIndex()
                    if currIndex.isValid():
                        self._tagModel.onActivated(currIndex)

        return DockWidget.eventFilter(self, object_, event)

    def _hideFilter(self):
        hadText = self._filterEdit.text() != ''
        self._filterEdit.clear()
        self._filterEdit.hide()
        if hadText:
            self._applyFilter()

    def _applyFilter(self):
        text = self._filterEdit.text()
        if text:
            if not text.startswith('*'):
                text = '*' + text
            if not text.endswith('*'):
                text = text + '*'

            wildcard = text.lower()

            filteredTags = _filterTags(wildcard, self._tags)

            self._setFilteredTags(filteredTags)
            self._tree.expandAll()
            if filteredTags:
                firstMatchingTag = _findFirstMatching(wildcard, filteredTags)
                path = _tagPath(firstMatchingTag)
                index = self._tagModel.indexForTagPath(path)
                self._tree.setCurrentIndex(index)
        else:
            self._setFilteredTags(self._tags)

        if text:
            self._filterEdit.show()
        elif not self._filterEdit.hasFocus():
            self._hideFilter()

    def _onTreeTextTyped(self, text):
        self._filterEdit.setText(self._filterEdit.text() + text)
        self._applyFilter()

    def _onTreeBackspace(self):
        text = self._filterEdit.text()
        if text:
            self._filterEdit.setText(text[:-1])
            self._applyFilter()

    def _onTreeCtrlBackspace(self):
        self._hideFilter()
        self._applyFilter()
