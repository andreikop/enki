"""
openedfilemodel --- Model and treeview for list of opened files
===============================================================

Module displays list of opened files, implements files sorting, drag-n-drop in the list, switches current file.

Used only internally by Workspace
"""

import os.path
import copy


from PyQt5.QtCore import QAbstractItemModel, \
                         QByteArray, \
                         QMimeData, \
                         QModelIndex, \
                         QObject, \
                         Qt
from PyQt5.QtWidgets import QAbstractItemView, QAction, QActionGroup, \
                        QMenu, \
                        QMessageBox, \
                        QTreeView
from PyQt5.QtGui import QIcon


from enki.core.core import core, DATA_FILES_PATH
from enki.core.uisettings import ChoiseOption
from enki.widgets.dockwidget import DockWidget


class _OpenedFileModel(QAbstractItemModel):
    """Model, herited from QAbstractItemModel, used for show list of opened files
    in the tree view (_OpenedFileExplorer)
    It switches current file, does file sorting
    """

    def __init__(self, parentObject):
        QAbstractItemModel.__init__(self, parentObject )
        self._manuallySorted = False
        self._workspace = parentObject.parent()
        self._workspace.documentOpened.connect(self._onDocumentOpened)
        self._workspace.documentClosed.connect(self._onDocumentClosed)
        self._workspace.modificationChanged.connect(self._onDocumentDataChanged)

    def columnCount(self, parent):  # pylint: disable=W0613
        """See QAbstractItemModel documentation"""
        return 1

    def rowCount(self, parent ):
        """See QAbstractItemModel documentation"""
        if parent.isValid():
            return 0
        else:
            return len(self._workspace.sortedDocuments)

    def hasChildren(self, parent ):
        """See QAbstractItemModel documentation"""
        if parent.isValid():
            return False
        else:
            return (len(self._workspace.sortedDocuments) > 0)

    def headerData(self, section, orientation, role ):
        """See QAbstractItemModel documentation"""
        if  section == 0 and \
            orientation == Qt.Horizontal and \
            role == Qt.DecorationRole:
            return self.tr( "Opened Files" )
        else:
            return None

    def _uniqueDocumentPath(self, document):
        """ Get unique file path, which will be displayed in the list.
        Usually unique path includes only file name, but, if there are duplicating files in the list,
        last one or more directory name may be preppended.
        """
        docPath = document.filePath()
        if docPath is None:
            return 'untitled'

        documentPathes = [d.filePath() for d in self._workspace.documents()]

        uniquePath = os.path.basename(docPath)
        leftPath = os.path.dirname(docPath)

        sameEndOfPath = [path for path in documentPathes \
                            if path is not None and path.endswith('/' + uniquePath)]
        while len(sameEndOfPath) > 1:
            leftPathDirname = os.path.dirname(leftPath)
            leftPathBasename = os.path.basename(leftPath)
            uniquePath = os.path.join(leftPathBasename, uniquePath)
            leftPath = leftPathDirname
            sameEndOfPath = [path for path in documentPathes if path is not None and path.endswith('/' + uniquePath)]

        return uniquePath

    def data(self, index, role ):
        """See QAbstractItemModel documentation"""
        if  not index.isValid() :
            return None

        document = self.document( index )
        assert(document)

        if   role == Qt.DecorationRole:
            return document.modelIcon()
        elif role == Qt.DisplayRole:
            return self._uniqueDocumentPath(document)
        elif role == Qt.EditRole:
            return document.filePath()
        elif role == Qt.ToolTipRole:
            return document.modelToolTip()
        else:
            return None

    def setData(self, index, value, role=Qt.EditRole):
        document = self.document(index)
        newPath = value

        if newPath == document.filePath():
            return False

        if newPath == '/dev/null':
            try:
                os.remove(document.filePath())
            except (OSError, IOError) as ex:
                QMessageBox.critical(core.mainWindow(), 'Not this time', 'The OS thinks it needs the file')
                return False
            core.workspace().closeDocument(document)
        else:
            try:
                os.rename(document.filePath(), newPath)
            except (OSError, IOError) as ex:
                QMessageBox.critical(core.mainWindow(), 'Failed to rename file', str(ex))
                return False
            else:
                document.setFilePath(newPath)
                document.saveFile()
                self.dataChanged.emit(index, index)

        return True

    def flags(self, index ):
        """See QAbstractItemModel documentation"""
        if index.isValid():
            document = self.document( index )
            if document.filePath() is None or \
               document.qutepart.document().isModified() or \
               document.isExternallyModified() or \
               document.isExternallyRemoved() or \
               document.isNeverSaved():
                # if path editing is not allowed now
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEditable
        else:
            # invalid index, probably root
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled

    def index(self, row, column, parent=QModelIndex()):
        """See QAbstractItemModel documentation"""
        if  parent.isValid() or column > 0 or column < 0 or row < 0 or row >= len(self._workspace.sortedDocuments) :
            return QModelIndex()

        return self.createIndex( row, column, self._workspace.sortedDocuments[row] )

    def parent(self, index ):  # pylint: disable=W0613
        """See QAbstractItemModel documentation"""
        return QModelIndex()

    def mimeTypes(self):
        """See QAbstractItemModel documentation"""
        return ["application/x-modelindexrow"]

    def mimeData(self, indexes ):
        """See QAbstractItemModel documentation"""
        if len(indexes) != 1:
            return 0

        data = QMimeData()
        data.setData( self.mimeTypes()[0], QByteArray.number( indexes[0].row() ) )
        return data

    def supportedDropActions(self):
        """See QAbstractItemModel documentation"""
        return Qt.MoveAction

    def dropMimeData(self, data, action, row, column, parent ):  # pylint: disable=R0913
        """See QAbstractItemModel documentation"""
        if  parent.isValid() or \
            ( row == -1 and column == -1 ) or \
            action != Qt.MoveAction or \
            not data or \
            not data.hasFormat( self.mimeTypes()[0] ) :
            return False

        fromRow = data.data( self.mimeTypes()[0] ).toInt()[0]

        if  row >= len(self._workspace.sortedDocuments):
            row -= 1
        elif  fromRow < row :
            row -= 1

        newDocuments = copy.copy(self._workspace.sortedDocuments)

        item = newDocuments.pop(fromRow)

        #if row > fromRow:
        #    row -= 1

        newDocuments.insert(row, item)

        self.rebuildMapping( self._workspace.sortedDocuments, newDocuments )

        self._manuallySorted = True

        QObject.parent(self).tvFiles.setCurrentIndex(self.documentIndex(item))

        return True

    def document(self, index ):
        """Get document by model index"""
        if not index.isValid() :
            return None

        return index.internalPointer()

    def documentIndex(self, document):
        """Get model index by document"""
        row = self._workspace.sortedDocuments.index( document )

        if  row != -1 :
            return self.createIndex( row, 0, document )

        return QModelIndex()

    def sortDocuments(self):
        """Sort documents list according to current sort mode"""
        sortedDocuments = self._workspace.sortedDocuments
        if not self._manuallySorted:
            sortedDocuments = sorted(sortedDocuments,
                                     key=lambda d: d.filePath())
        self.rebuildMapping( self._workspace.sortedDocuments, sortedDocuments )
        # scroll the view
        selected = QObject.parent(self).tvFiles.selectionModel().selectedIndexes()
        if selected:
            QObject.parent(self).tvFiles.scrollTo( selected[0] )

    def rebuildMapping(self, oldList, newList ):
        """TODO black magic code. Understand and comment it
        """
        self.layoutAboutToBeChanged.emit()
        pOldIndexes = self.persistentIndexList()
        pIndexes = []
        documentsMapping = {}
        mapping = {}

        # build old mapping
        for index in pOldIndexes:
            row = index.row()
            documentsMapping[ row ] = oldList[row]
            mapping[ row ] = row

        self._workspace.sortedDocuments = newList

        # build mapping
        for pIndex in pOldIndexes:
            row = pIndex.row()
            document = documentsMapping[ row ]
            index = self._workspace.sortedDocuments.index( document )
            mapping[ row ] = index

        for pIndex in pOldIndexes:
            row = pIndex.row()
            index = mapping[ row ]

            if  pIndex.isValid():
                pIndexes.append(self.createIndex( index, pIndex.column(), self._workspace.sortedDocuments[index] ))
            else:
                pIndexes.append(QModelIndex())

        self.changePersistentIndexList( pOldIndexes, pIndexes )
        self.layoutChanged.emit()

    def _onDocumentOpened(self, document ):
        """New document opened at workspace. Handle it
        """
        assert( not document in self._workspace.sortedDocuments )
        self._workspace.sortedDocuments.append( document )
        self.sortDocuments()
        document.documentDataChanged.connect(self._onDocumentDataChanged)

    def _onDocumentDataChanged(self, document=None):
        """Document data has been changed. Update views
        """
        if document is None:
            document_ = self.sender()
        else:
            document_ = document

        index = self.documentIndex( document_ )
        self.dataChanged.emit( index, index )

    def _onDocumentClosed(self, document ):
        """Document has been closed. Unhandle it
        """
        index = self._workspace.sortedDocuments.index( document )

        if  index == -1 :
            return

        # scroll the view
        QObject.parent(self).startModifyModel()
        self.beginRemoveRows( QModelIndex(), index, index )
        self._workspace.sortedDocuments.remove( document )
        self.endRemoveRows()
        QObject.parent(self).finishModifyModel()


class OpenedFileExplorer(DockWidget):
    """Opened File Explorer is list widget with list of opened files.
    It implements switching current file, files sorting. Uses _OpenedFileModel internally.
    Class instance created by Workspace.
    """
    def __init__(self, workspace):
        DockWidget.__init__(self, workspace, "&Opened Files", QIcon(":/enkiicons/filtered.png"), "Alt+O")

        self._workspace = workspace

        self.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )

        self.tvFiles = QTreeView(self)
        self.tvFiles.setHeaderHidden(True)
        self.tvFiles.setEditTriggers(QAbstractItemView.SelectedClicked)
        self.tvFiles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tvFiles.setDragEnabled(True)
        self.tvFiles.setDragDropMode(QAbstractItemView.InternalMove)
        self.tvFiles.setRootIsDecorated(False)
        self.tvFiles.setTextElideMode(Qt.ElideMiddle)
        self.tvFiles.setUniformRowHeights( True )

        self.tvFiles.customContextMenuRequested.connect(self._onTvFilesCustomContextMenuRequested)

        self.setWidget(self.tvFiles)
        self.setFocusProxy(self.tvFiles)

        self.model = _OpenedFileModel(self)  # Not protected, because used by Configurator
        self.tvFiles.setModel( self.model )
        self.tvFiles.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.tvFiles.setAttribute( Qt.WA_MacSmallSize )

        self._workspace.currentDocumentChanged.connect(self._onCurrentDocumentChanged)

        # disconnected by startModifyModel()
        self.tvFiles.selectionModel().selectionChanged.connect(self._onSelectionModelSelectionChanged)

        self.tvFiles.activated.connect(self._workspace.focusCurrentDocument)

        core.actionManager().addAction("mView/aOpenedFiles", self.showAction())

    def del_(self):
        """Explicitly called destructor
        """
        core.actionManager().removeAction("mView/aOpenedFiles")

    def startModifyModel(self):
        """Blocks signals from model while it is modified by code
        """
        self.tvFiles.selectionModel().selectionChanged.disconnect(self._onSelectionModelSelectionChanged)

    def finishModifyModel(self):
        """Unblocks signals from model
        """
        self.tvFiles.selectionModel().selectionChanged.connect(self._onSelectionModelSelectionChanged)

    def _onCurrentDocumentChanged(self, oldDocument, currentDocument ):  # pylint: disable=W0613
        """ Current document has been changed on workspace
        """
        if currentDocument is not None:
            index = self.model.documentIndex( currentDocument )

            self.startModifyModel()
            self.tvFiles.setCurrentIndex( index )
            # scroll the view
            self.tvFiles.scrollTo( index )
            self.finishModifyModel()

    def _onSelectionModelSelectionChanged(self, selected, deselected ):  # pylint: disable=W0613
        """ Item selected in the list. Switch current document
        """
        if not selected.indexes():  # empty list, last file closed
            return

        index = selected.indexes()[0]
        # backup/restore current focused widget as setting active mdi window will steal it
        focusWidget = self.window().focusWidget()

        # set current document
        document = self._workspace.sortedDocuments[index.row()]
        self._workspace.setCurrentDocument( document )

        # restore focus widget
        if  focusWidget :
            focusWidget.setFocus()

    def _onTvFilesCustomContextMenuRequested(self, pos ):
        """Connected automatically by uic
        """
        menu = QMenu()

        menu.addAction( core.actionManager().action( "mFile/mClose/aCurrent" ) )
        menu.addAction( core.actionManager().action( "mFile/mSave/aCurrent" ) )
        menu.addAction( core.actionManager().action( "mFile/mReload/aCurrent" ) )
        menu.addSeparator()
        menu.addAction( core.actionManager().action( "mFile/mFileSystem/aRename" ) )
        toggleExecutableAction = core.actionManager().action("mFile/mFileSystem/aToggleExecutable")
        if toggleExecutableAction:  # not available on Windows
            menu.addAction(toggleExecutableAction)
        core.actionManager().action("mFile/mFileSystem").menu().aboutToShow.emit()  # to update aToggleExecutable

        menu.exec_( self.tvFiles.mapToGlobal( pos ) )
