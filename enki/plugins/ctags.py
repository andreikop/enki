"""Navigator dock widget and functionality
"""

from PyQt4.QtCore import QObject, Qt, QVariant, QAbstractItemModel, QModelIndex
from PyQt4.QtGui import QIcon, QTreeView

from enki.widgets.dockwidget import DockWidget

from enki.core.core import core


class Tag:
    def __init__(self, name, lineNumber, parent):
        self.name = name
        self.lineNumber = lineNumber
        self.parent = parent
        self.children = []
    
    def format(self, indentLevel=0):
        indent = '\t' * indentLevel
        formattedChildren = [child.format(indentLevel + 1) \
                                for child in self.children]
        result = '{}{} {}'.format(indent, self.lineNumber, self.name)
        if formattedChildren:
            result += '\n'
            result += '\n'.join(formattedChildren)
        
        return result


def parseTags(text):
    def parseTag(line):
        items = line.split('\t')
        print items
        name = items[0]
        if len(items) == 5:
            type_ = items[-2]
            lineText = items[-1]
            scopeText = None
        else:
            type_ = items[-3]
            lineText = items[-2]
            scopeText = items[-1]
        
        lineNumber = int(lineText.split(':')[-1])
        
        scope = scopeText.split(':')[-1].split('.')[-1] if scopeText else None
        return name, lineNumber, type_, scope
    
    def findScope(tag, scopeName):
        """Check tag and its parents, it theirs name is scopeName.
        Return tag or None
        """
        if tag is None:
            return None
        print tag.name, scopeName
        if tag.name == scopeName:
            return tag
        elif tag.parent is not None:
            return findScope(tag.parent, scopeName)
        else:
            return None
    
    ignoredTypes = ('variable')
    
    tags = []
    lastTag = None
    for line in text.splitlines():
        name, lineNumber, type_, scope = parseTag(line)
        if type_ not in ignoredTypes:
            parent = findScope(lastTag, scope)
            tag = Tag(name, lineNumber, parent)
            if parent is not None:
                parent.children.append(tag)
            else:
                tags.append(tag)
            lastTag = tag
    
    return tags


class TagModel(QAbstractItemModel):
    def __init__(self, *args):
        QAbstractItemModel.__init__(self, *args)
        self._tags = []
    
    def setTags(self, tags):
        self._tags = tags
        self.layoutChanged.emit()
    
    def index(self, row, column, parent):
        if not parent.isValid():  # top level
            return self.createIndex(row, column, self._tags[row])
        else:  # nested
            parentTag = parent.internalPointer()
            return self.createIndex(row, column, parentTag.children[row])
    
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        tag = index.internalPointer()
        if tag.parent is not None:
            parent = tag.parent
            if parent.parent:
                row = parent.parent.children.index(parent)
            else:
                row = self._tags.index(parent)
            
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
            return QVariant()
        
        tag = index.internalPointer()
        if role == Qt.DisplayRole:
            return '{} {}'.format(tag.name, tag.lineNumber)
        else:
            return QVariant()


class Plugin(QObject):
    """Main class. Interface for the core.
    """
    def __init__(self):
        QObject.__init__(self)
        self._dock = DockWidget(core.mainWindow(), '&Navigator', QIcon(':/enkiicons/goto.png'), "Alt+N")
        
        self._tree = QTreeView(self._dock)
        self._tree.setHeaderHidden(True)
        self._dock.setWidget(self._tree)
        self._dock.setFocusProxy(self._tree)
        
        self._model = TagModel(self._tree)
        self._tree.setModel(self._model)

        core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)
        core.actionManager().addAction("mView/aNavigator", self._dock.showAction())

    def del_(self):
        """Uninstall the plugin
        """
        core.actionManager().removeAction("mView/aNavigator")
