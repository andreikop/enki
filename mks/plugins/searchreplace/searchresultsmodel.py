"""
searchresultsmodel --- Model for search results
===============================================
"""

from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, \
                         QDir, \
                         QModelIndex, Qt, \
                         QVariant

class Result:  # pylint: disable=R0902
    """One found by search thread item. Consists coordinates and capture. Used by SearchResultsModel
    """
    def __init__ (  self, fileName, wholeLine, line, column, match):  # pylint: disable=R0913
        self.fileName = fileName
        self.wholeLine = wholeLine
        self.line = line
        self.column = column
        self.match = match
        self.checkState =  Qt.Checked
        self.enabled = True
    
    def text(self, notUsed):  # pylint: disable=W0613
        """Displayable text of search result. Shown as line in the search results dock
        notUsed argument added for have same signature, as FileResults.text
        """
        return "Line: %d, Column: %d: %s" % ( self.line + 1, self.column, self.wholeLine )
    
    def tooltip(self):
        """Tooltip of the search result"""
        return self.wholeLine
    
    def hasChildren(self):
        """Check if QAbstractItem has children"""
        return False

class FileResults:
    """Object stores all items, found in the file
    """
    def __init__(self, fileName, results):
        self.fileName = fileName
        self.results = results
        self.checkState = Qt.Checked
    
    def __str__(self):
        """Convertor to string. Used for debugging
        """
        return '%s (%d)' % (self.fileName, len(self.results))
    
    def updateCheckState(self):
        """Update own checked state after checked state of child result changed or
        child result removed
        """
        if all([res.checkState == Qt.Checked for res in self.results]):  # if all checked
            self.checkState = Qt.Checked
        elif any([res.checkState == Qt.Checked for res in self.results]):  # if any checked
            self.checkState = Qt.PartiallyChecked
        else:
            self.checkState = Qt.Unchecked
    
    def text(self, baseDir):
        """Displayable text of the file results. Shown as line in the search results dock
        baseDir is base directory of current search operation
        """
        return '%s (%d)' % (baseDir.relativeFilePath(self.fileName), len(self.results))
    
    def tooltip(self):
        """Tooltip of the item in the results dock
        """
        return self.fileName
    
    def hasChildren(self):
        """Check if item has children
        """
        return 0 != len(self.results)

class SearchResultsModel(QAbstractItemModel):
    """AbstractItemodel used for display search results in 'Search in directory' and 'Replace in directory' mode
    """
    firstResultsAvailable = pyqtSignal()
    
    EnabledRole = Qt.UserRole
        
    def __init__(self, searchThread, parent ):
        """Constructor of SearchResultsModel class
        """
        QAbstractItemModel.__init__(self, parent )
        self._rowCount = 0
        self.searchThread = searchThread
        
        self.fileResults = []  # list of FileResults
        self._searchDir = QDir()
        
        # connections
        self.searchThread.reset.connect(self.clear)
        self.searchThread.resultsAvailable.connect(self.thread_resultsAvailable)
        
        from mks.plugins.searchreplace import Plugin
        self.Plugin = Plugin  #  FIXME remove this dirty hack

    def index(self, row, column, parent ):
        """See QAbstractItemModel docs
        """
        if  row >= self.rowCount( parent ) or column > self.columnCount(parent):
            return QModelIndex()
        
        if parent.isValid():  # index for result
            result = parent.internalPointer().results[row]
            return self.createIndex( row, column, result )
        else:  # need index for fileRes
            return self.createIndex( row, column, self.fileResults[row])

    def parent(self, index):
        """See QAbstractItemModel docs
        """
        if not index.isValid() :
            return QModelIndex()
        
        if not isinstance(index.internalPointer(), Result):  # it is an top level item
            return QModelIndex()
        
        result = index.internalPointer()
        for row, fileRes in enumerate(self.fileResults):
            if fileRes.fileName == result.fileName:
                return self.createIndex(row, 0, fileRes)
        else:
            assert(0)

    def hasChildren(self, item):
        """See QAbstractItemModel docs
        """
        # root parents
        if item.isValid():
            return item.internalPointer().hasChildren()
        else:
            return len(self.fileResults) != 0

    def columnCount(self, parent ):  # pylint: disable=W0613
        """See QAbstractItemModel docs
        """
        return 1
    
    def rowCount(self, parent):
        """See QAbstractItemModel docs
        """
        if not parent.isValid():  # root elements
            return len(self.fileResults)
        elif isinstance(parent.internalPointer(), Result):  # result
            return 0
        elif isinstance(parent.internalPointer(), FileResults):  # file
            return len(parent.internalPointer().results)
        else:
            assert(0)
    
    def flags(self, index ):
        """See QAbstractItemModel docs
        """
        flags = QAbstractItemModel.flags( self, index )
        context = self.searchThread.searchContext

        if context.mode & self.Plugin.ModeFlagReplace :
            flags |= Qt.ItemIsUserCheckable
        
        if isinstance(index.internalPointer(), Result):
            if not index.internalPointer().enabled :
                flags &= ~Qt.ItemIsEnabled
                flags &= ~Qt.ItemIsSelectable
        
        return flags
    
    def data(self, index, role ):
        """See QAbstractItemModel docs
        """
        if not index.isValid() :
            return QVariant()
        
        # Common code for file and result
        if role == Qt.DisplayRole:
            return self.tr( index.internalPointer().text(self._searchDir))
        elif role == Qt.ToolTipRole:
            return index.internalPointer().tooltip()
        elif role == Qt.CheckStateRole:
            if  self.flags( index ) & Qt.ItemIsUserCheckable:
                return index.internalPointer().checkState
        
        return QVariant()
    
    def setData(self, index, value, role ):
        """See QAbstractItemModel docs
        This method changes checked state of the item.
        If file unchecked - we need uncheck all items,
        if item unchecked...
        """
        if isinstance(index.internalPointer(), Result):  # it is a Result
            if role == Qt.CheckStateRole:
                # update own state
                index.internalPointer().checkState = value.toInt()[0]
                self.dataChanged.emit( index, index )  # own checked state changed
                # update parent state
                fileRes = index.parent().internalPointer()
                assert(isinstance(fileRes, FileResults))
                fileRes.updateCheckState()
                self.dataChanged.emit(index.parent(), index.parent())  # parent checked state might be changed
        elif isinstance(index.internalPointer(), FileResults):  # it is a FileResults
            if role == Qt.CheckStateRole:
                fileRes = index.internalPointer()
                fileRes.checkState = value.toInt()[0]
                for res in fileRes.results:
                    res.checkState = value.toInt()[0]
                firstChildIndex = self.index(0, 0, index)
                lastChildIndex = self.index(len(fileRes.results) - 1, 0, index)
                self.dataChanged.emit(firstChildIndex, lastChildIndex)
        else:
            assert(0)
        return True
    
    def clear(self):
        """Clear all results
        """
        self.beginRemoveRows(QModelIndex(), 0, len(self.fileResults) - 1)
        self.fileResults = []
        self.endRemoveRows()

    def thread_resultsAvailable(self, fileResultsList ):
        """Handler of signal from the search thread.
        New result is available, add it to the model
        """
        context = self.searchThread.searchContext
        if not self.fileResults:  # appending first
            self.firstResultsAvailable.emit()
            self._searchDir.setPath( context.searchPath )
        self.beginInsertRows( QModelIndex(), \
                              len(self.fileResults), \
                              len(self.fileResults) + len(fileResultsList) - 1)
        self.fileResults.extend(fileResultsList)
        self.endInsertRows()
    
    def thread_resultsHandled(self, fileName, results):
        """Replace thread processed result, need to remove it from the model
        """
        for index, fileRes in enumerate(self.fileResults):  # try to find FileResults
            if fileRes.fileName == fileName:  # found
                fileResIndex = self.createIndex(index, 0, fileRes)
                if len(results) == len(fileRes.results):  # removing all
                    self.beginRemoveRows(QModelIndex(), index, index)
                    self.fileResults.pop(index)
                    self.endRemoveRows()                    
                else:
                    for res in results:
                        resIndex = fileRes.results.index(res)
                        self.beginRemoveRows(fileResIndex, resIndex, resIndex)
                        fileRes.results.pop(resIndex)
                        self.endRemoveRows()
                    if not fileRes.results:  # no results left
                        self.beginRemoveRows(QModelIndex(), index, index)
                        self.fileResults.pop(index)
                        self.endRemoveRows()
                    else:
                        fileRes.updateCheckState()
                return
        else:  # not found
            assert(0)
