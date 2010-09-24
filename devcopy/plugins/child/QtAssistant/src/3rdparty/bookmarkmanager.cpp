'''***************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
** All rights reserved.
** Contact: Nokia Corporation (qt-info@nokia.com)
**
** This file is part of the Qt Assistant of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** No Commercial Usage
** This file contains pre-release code and may not be distributed.
** You may use self file in accordance with the terms and conditions
** contained in the Technology Preview License Agreement accompanying
** self package.
**
** GNU Lesser General Public License Usage
** Alternatively, file may be used under the terms of the GNU Lesser
** General Public License version 2.1 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU Lesser General Public License version 2.1 requirements
** will be met: http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, a special exception, gives you certain additional
** rights.  These rights are described in the Nokia Qt LGPL Exception
** version 1.1, in the file LGPL_EXCEPTION.txt in self package.
**
** If you have questions regarding the use of self file, contact
** Nokia at qt-info@nokia.com.
**
**
**
**
**
**
**
**
** $QT_END_LICENSE$
**
***************************************************************************'''

#include "bookmarkmanager.h"
##include "centralwidget.h"

#include <QtGui/QMenu>
#include <QtGui/QIcon>
#include <QtGui/QStyle>
#include <QtGui/QLabel>
#include <QtGui/QLayout>
#include <QtCore/QEvent>
#include <QtGui/QComboBox>
#include <QtGui/QKeyEvent>
#include <QtGui/QLineEdit>
#include <QtGui/QMessageBox>
#include <QtGui/QHeaderView>
#include <QtGui/QToolButton>
#include <QtGui/QPushButton>
#include <QtGui/QApplication>
#include <QtHelp/QHelpEngineCore>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QSortFilterProxyModel>

QT_BEGIN_NAMESPACE

BookmarkDialog.BookmarkDialog(BookmarkManager *manager, &title,
                                QString &url, *parent)
        : QDialog(parent)
        , m_url(url)
        , m_title(title)
        , bookmarkManager(manager)
    installEventFilter(self)

    ui.setupUi(self)
    ui.bookmarkEdit.setText(title)
    ui.newFolderButton.setVisible(False)
    ui.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
    ui.bookmarkFolders.addItems(bookmarkManager.bookmarkFolders())

    proxyModel = QSortFilterProxyModel(self)
    proxyModel.setFilterKeyColumn(0)
    proxyModel.setDynamicSortFilter(True)
    proxyModel.setFilterRole(Qt.UserRole + 10)
    proxyModel.setSourceModel(bookmarkManager.treeBookmarkModel())
    proxyModel.setFilterRegExp(QRegExp(QLatin1String("Folder"),
                                        Qt.CaseSensitive, QRegExp.FixedString))
    ui.treeView.setModel(proxyModel)

    ui.treeView.expandAll()
    ui.treeView.setVisible(False)
    ui.treeView.header().setVisible(False)
    ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)

    connect(ui.buttonBox, SIGNAL(rejected()), self, SLOT(reject()))
    connect(ui.buttonBox, SIGNAL(accepted()), self, SLOT(addAccepted()))
    connect(ui.newFolderButton, SIGNAL(clicked()), self, SLOT(addNewFolder()))
    connect(ui.toolButton, SIGNAL(clicked()), self, SLOT(toolButtonClicked()))
    connect(ui.bookmarkEdit, SIGNAL(textChanged(QString)), self,
            SLOT(textChanged(QString)))

    connect(bookmarkManager.treeBookmarkModel(),
            SIGNAL(itemChanged(QStandardItem*)),
            self, SLOT(itemChanged(QStandardItem*)))

    connect(ui.bookmarkFolders, SIGNAL(currentIndexChanged(QString)), self,
            SLOT(selectBookmarkFolder(QString)))

    connect(ui.treeView, SIGNAL(customContextMenuRequested(QPoint)), self,
            SLOT(customContextMenuRequested(QPoint)))

    connect(ui.treeView.selectionModel(), SIGNAL(currentChanged(QModelIndex,
            QModelIndex)), self, SLOT(currentChanged(QModelIndex)))


BookmarkDialog.~BookmarkDialog()


def addAccepted(self):
    QItemSelectionModel *model = ui.treeView.selectionModel()
     QModelIndexList &list = model.selection().indexes()

    QModelIndex index
    if not list.isEmpty():
        index = proxyModel.mapToSource(list.at(0))

    bookmarkManager.addNewBookmark(index, ui.bookmarkEdit.text(), m_url)
    accept()


def addNewFolder(self):
    QItemSelectionModel *model = ui.treeView.selectionModel()
     QModelIndexList &list = model.selection().indexes()

    QModelIndex index
    if not list.isEmpty():
        index = list.at(0)

    QModelIndex newFolder =
        bookmarkManager.addNewFolder(proxyModel.mapToSource(index))
    if newFolder.isValid():
        ui.treeView.expand(index)
         QModelIndex &index = proxyModel.mapFromSource(newFolder)
        model.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

        ui.bookmarkFolders.clear()
        ui.bookmarkFolders.addItems(bookmarkManager.bookmarkFolders())

         QString &name = index.data().toString()
        ui.bookmarkFolders.setCurrentIndex(ui.bookmarkFolders.findText(name))

    ui.treeView.setFocus()


def toolButtonClicked(self):
    visible = not ui.treeView.isVisible()
    ui.treeView.setVisible(visible)
    ui.newFolderButton.setVisible(visible)

    if visible:
        resize(QSize(width(), 400))
        ui.toolButton.setText(QLatin1String("-"))

    else:
        resize(width(), minimumHeight())
        ui.toolButton.setText(QLatin1String("+"))



def itemChanged(self, *item):
    if renameItem != item:
        renameItem = item
        oldText = item.text()
        return


    if item.text() != oldText:
        ui.bookmarkFolders.clear()
        ui.bookmarkFolders.addItems(bookmarkManager.bookmarkFolders())

        name = tr("Bookmarks")
         QModelIndex &index = ui.treeView.currentIndex()
        if index.isValid():
            name = index.data().toString()
        ui.bookmarkFolders.setCurrentIndex(ui.bookmarkFolders.findText(name))



def textChanged(self, &string):
    ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not string.isEmpty())


def selectBookmarkFolder(self, &folderName):
    if folderName.isEmpty():
        return

    if folderName == tr("Bookmarks"):
        ui.treeView.clearSelection()
        return


    QStandardItemModel *model = bookmarkManager.treeBookmarkModel()
    QList<QStandardItem*> list = model.findItems(folderName,
                                 Qt.MatchCaseSensitive | Qt.MatchRecursive, 0)
    if not list.isEmpty():
         QModelIndex &index = model.indexFromItem(list.at(0))
        QItemSelectionModel *model = ui.treeView.selectionModel()
        if model:
            model.setCurrentIndex(proxyModel.mapFromSource(index),
                                   QItemSelectionModel.ClearAndSelect)




def customContextMenuRequested(self, &point):
    index = ui.treeView.indexAt(point)
    if not index.isValid():
        return

    QMenu menu(QLatin1String(""), self)

    QAction *removeItem = menu.addAction(tr("Delete Folder"))
    QAction *renameItem = menu.addAction(tr("Rename Folder"))

    QAction *picked = menu.exec(ui.treeView.mapToGlobal(point))
    if not picked:
        return

     QModelIndex &proxyIndex = proxyModel.mapToSource(index)
    if picked == removeItem:
        bookmarkManager.removeBookmarkItem(ui.treeView, proxyIndex)
        ui.bookmarkFolders.clear()
        ui.bookmarkFolders.addItems(bookmarkManager.bookmarkFolders())

        name = tr("Bookmarks")
        index = ui.treeView.currentIndex()
        if index.isValid():
            name = index.data().toString()
        ui.bookmarkFolders.setCurrentIndex(ui.bookmarkFolders.findText(name))

    elif picked == renameItem:
        BookmarkModel *model = bookmarkManager.treeBookmarkModel()
        if QStandardItem *item = model.itemFromIndex(proxyIndex):
            item.setEditable(True)
            ui.treeView.edit(index)
            item.setEditable(False)




def currentChanged(self, &current):
    text = tr("Bookmarks")
    if current.isValid():
        text = current.data().toString()
    ui.bookmarkFolders.setCurrentIndex(ui.bookmarkFolders.findText(text))


def eventFilter(self, *object, *e):
    if object == self and e.type() == QEvent.KeyPress:
        QKeyEvent *ke = static_cast<QKeyEvent*>(e)

        index = ui.treeView.currentIndex()
        switch (ke.key())
        case Qt.Key_F2:
             QModelIndex &source = proxyModel.mapToSource(index)
            QStandardItem *item =
                bookmarkManager.treeBookmarkModel().itemFromIndex(source)
            if item:
                item.setEditable(True)
                ui.treeView.edit(index)
                item.setEditable(False)


        break

        case Qt.Key_Delete:
            bookmarkManager.removeBookmarkItem(ui.treeView,
                                                proxyModel.mapToSource(index))
            ui.bookmarkFolders.clear()
            ui.bookmarkFolders.addItems(bookmarkManager.bookmarkFolders())

            name = tr("Bookmarks")
            index = ui.treeView.currentIndex()
            if index.isValid():
                name = index.data().toString()
            ui.bookmarkFolders.setCurrentIndex(ui.bookmarkFolders.findText(name))

        break

        default:
            break


    return QObject.eventFilter(object, e)



# #pragma mark -- BookmarkWidget


BookmarkWidget.BookmarkWidget(BookmarkManager *manager, *parent,
                               bool showButtons)
        : QWidget(parent)
        , addButton(0)
        , removeButton(0)
        , bookmarkManager(manager)
    setup(showButtons)
    installEventFilter(self)


BookmarkWidget.~BookmarkWidget()


def removeClicked(self):
     QModelIndex &index = treeView.currentIndex()
    if searchField.text().isEmpty():
        bookmarkManager.removeBookmarkItem(treeView,
                                            filterBookmarkModel.mapToSource(index))



def filterChanged(self):
    searchBookmarks = searchField.text().isEmpty()
    if not searchBookmarks:
        regExp.setPattern(searchField.text())
        filterBookmarkModel.setSourceModel(bookmarkManager.listBookmarkModel())

    else:
        regExp.setPattern(QLatin1String(""))
        filterBookmarkModel.setSourceModel(bookmarkManager.treeBookmarkModel())


    if addButton:
        addButton.setEnabled(searchBookmarks)

    if removeButton:
        removeButton.setEnabled(searchBookmarks)

    filterBookmarkModel.setFilterRegExp(regExp)

     QModelIndex &index = treeView.indexAt(QPoint(1, 1))
    if index.isValid():
        treeView.setCurrentIndex(index)

    if searchBookmarks:
        expandItems()


def expand(self, &index):
     QModelIndex &source = filterBookmarkModel.mapToSource(index)
    QStandardItem *item =
        bookmarkManager.treeBookmarkModel().itemFromIndex(source)
    if item:
        item.setData(treeView.isExpanded(index), Qt.UserRole + 11)


def activated(self, &index):
    if not index.isValid():
        return

    data = index.data(Qt.UserRole + 10).toString()
    if data != QLatin1String("Folder"):
        requestShowLink.emit(data)


def customContextMenuRequested(self, &point):
    index = treeView.indexAt(point)
    if not index.isValid():
        return

    QAction *showItem = 0
    QAction *removeItem = 0
    QAction *renameItem = 0
    QAction *showItemNewTab = 0

    QMenu menu(QLatin1String(""), self)
    data = index.data(Qt.UserRole + 10).toString()
    if data == QLatin1String("Folder"):
        removeItem = menu.addAction(tr("Delete Folder"))
        renameItem = menu.addAction(tr("Rename Folder"))

    else:
        showItem = menu.addAction(tr("Show Bookmark"))
        showItemNewTab = menu.addAction(tr("Show Bookmark in New Tab"))
        if searchField.text().isEmpty():
            menu.addSeparator()
            removeItem = menu.addAction(tr("Delete Bookmark"))
            renameItem = menu.addAction(tr("Rename Bookmark"))



    QAction *pickedAction = menu.exec(treeView.mapToGlobal(point))
    if not pickedAction:
        return

    if pickedAction == showItem:
        requestShowLink.emit(data)

    elif pickedAction == showItemNewTab:
        #CentralWidget.instance().setSourceInNewTab(data)
        requestShowLinkInNewTab.emit(data)

    elif pickedAction == removeItem:
        bookmarkManager.removeBookmarkItem(treeView,
                                            filterBookmarkModel.mapToSource(index))

    elif pickedAction == renameItem:
         QModelIndex &source = filterBookmarkModel.mapToSource(index)
        QStandardItem *item =
            bookmarkManager.treeBookmarkModel().itemFromIndex(source)
        if item:
            item.setEditable(True)
            treeView.edit(index)
            item.setEditable(False)




def setup(self, showButtons):
    regExp.setPatternSyntax(QRegExp.FixedString)
    regExp.setCaseSensitivity(Qt.CaseInsensitive)

    QLayout *vlayout = QVBoxLayout(self)
    vlayout.setMargin(4)

    QLabel *label = QLabel(tr("Filter:"), self)
    vlayout.addWidget(label)

    searchField = QLineEdit(self)
    vlayout.addWidget(searchField)
    connect(searchField, SIGNAL(textChanged(QString)), self,
            SLOT(filterChanged()))

    treeView = TreeView(self)
    vlayout.addWidget(treeView)

#ifdef Q_OS_MAC
#   define SYSTEM "mac"
#else:
#   define SYSTEM "win"
#endif

    if showButtons:
        QLayout *hlayout = QHBoxLayout()
        vlayout.addItem(hlayout)

        hlayout.addItem(new QSpacerItem(40, 20, QSizePolicy.Expanding))

        addButton = QToolButton(self)
        addButton.setText(tr("Add"))
        addButton.setIcon(QIcon(QLatin1String(":/assistant-icons/addtab.png")))
        addButton.setAutoRaise(True)
        addButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        hlayout.addWidget(addButton)
        connect(addButton, SIGNAL(clicked()), self, SIGNAL(addBookmark()))

        removeButton = QToolButton(self)
        removeButton.setText(tr("Remove"))
        removeButton.setIcon(QIcon(QLatin1String(":/assistant-icons/closetab.png")))
        removeButton.setAutoRaise(True)
        removeButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        hlayout.addWidget(removeButton)
        removeButton.clicked.connect(self.removeClicked)


    filterBookmarkModel = QSortFilterProxyModel(self)
    treeView.setModel(filterBookmarkModel)

    treeView.setDragEnabled(True)
    treeView.setAcceptDrops(True)
    treeView.setAutoExpandDelay(1000)
    treeView.setDropIndicatorShown(True)
    treeView.header().setVisible(False)
    treeView.viewport().installEventFilter(self)
    treeView.setContextMenuPolicy(Qt.CustomContextMenu)

    connect(treeView, SIGNAL(expanded(QModelIndex)), self,
            SLOT(expand(QModelIndex)))
    connect(treeView, SIGNAL(collapsed(QModelIndex)), self,
            SLOT(expand(QModelIndex)))
    connect(treeView, SIGNAL(activated(QModelIndex)), self,
            SLOT(activated(QModelIndex)))
    connect(treeView, SIGNAL(customContextMenuRequested(QPoint)),
            self, SLOT(customContextMenuRequested(QPoint)))

    filterBookmarkModel.setFilterKeyColumn(0)
    filterBookmarkModel.setDynamicSortFilter(True)
    filterBookmarkModel.setSourceModel(bookmarkManager.treeBookmarkModel())

    expandItems()


def expandItems(self):
    QStandardItemModel *model = bookmarkManager.treeBookmarkModel()
    QList<QStandardItem*>list = model.findItems(QLatin1String("*"),
                                Qt.MatchWildcard | Qt.MatchRecursive, 0)
    foreach ( QStandardItem *item, list)
         QModelIndex &index = model.indexFromItem(item)
        treeView.setExpanded(filterBookmarkModel.mapFromSource(index),
                              item.data(Qt.UserRole + 11).toBool())



def focusInEvent(self, *e):
    if e.reason() != Qt.MouseFocusReason:
        searchField.selectAll()
        searchField.setFocus()

        index = treeView.indexAt(QPoint(1, 1))
        if index.isValid():
            treeView.setCurrentIndex(index)




def eventFilter(self, *object, *e):
    if (object == self) or (object == treeView.viewport()):
        index = treeView.currentIndex()
        if e.type() == QEvent.KeyPress:
            QKeyEvent *ke = static_cast<QKeyEvent*>(e)
            if index.isValid() and searchField.text().isEmpty():
                 QModelIndex &src = filterBookmarkModel.mapToSource(index)
                if ke.key() == Qt.Key_F2:
                    QStandardItem *item =
                        bookmarkManager.treeBookmarkModel().itemFromIndex(src)
                    if item:
                        item.setEditable(True)
                        treeView.edit(index)
                        item.setEditable(False)


                elif ke.key() == Qt.Key_Delete:
                    bookmarkManager.removeBookmarkItem(treeView, src)



            switch (ke.key())
            default:
                break
            case Qt.Key_Up:
                case Qt.Key_Down:
                    treeView.subclassKeyPressEvent(ke)

                break

            case Qt.Key_Enter:
                case Qt.Key_Return:
                    index = treeView.selectionModel().currentIndex()
                    if index.isValid():
                        data = index.data(Qt.UserRole + 10).toString()
                        if not data.isEmpty() and data != QLatin1String("Folder"):
                            requestShowLink.emit(data)


                break

            case Qt.Key_Escape:
                escapePressed.emit()

            break


        elif e.type() == QEvent.MouseButtonRelease:
            if index.isValid():
                QMouseEvent *me = static_cast<QMouseEvent*>(e)
                controlPressed = me.modifiers() & Qt.ControlModifier
                if ((me.button() == Qt.LeftButton) and controlPressed:
                        or (me.button() == Qt.MidButton))
                    data = index.data(Qt.UserRole + 10).toString()
                    if not data.isEmpty() and data != QLatin1String("Folder"):
                        #CentralWidget.instance().setSourceInNewTab(data)
                        requestShowLinkInNewTab.emit(data)





    return QWidget.eventFilter(object, e)



# #pragma mark -- BookmarkModel


BookmarkModel.BookmarkModel(int rows, columns, *parent)
        : QStandardItemModel(rows, columns, parent)


BookmarkModel.~BookmarkModel()


def supportedDropActions(self):
    return Qt.MoveAction


def flags(self, &index):
    defaultFlags = QStandardItemModel.flags(index)
    if ((not index.isValid()) # can only happen for the invisible root item
            or index.data(Qt.UserRole + 10).toString() == QLatin1String("Folder"))
        return (Qt.ItemIsDropEnabled | defaultFlags) &~ Qt.ItemIsDragEnabled

    return (Qt.ItemIsDragEnabled | defaultFlags) &~ Qt.ItemIsDropEnabled



# #pragma mark -- BookmarkManager


BookmarkManager.BookmarkManager(QHelpEngineCore *_helpEngine)
        : treeModel(new BookmarkModel(0, 1, self))
        , listModel(new BookmarkModel(0, 1, self))
        , helpEngine(_helpEngine)
    folderIcon = QApplication.style().standardIcon(QStyle.SP_DirClosedIcon)

    connect(treeModel, SIGNAL(itemChanged(QStandardItem*)), self,
            SLOT(itemChanged(QStandardItem*)))
    connect(treeModel, SIGNAL(itemChanged(QStandardItem*)), self,
            SIGNAL(bookmarksChanged()))
    connect(treeModel, SIGNAL(rowsRemoved(QModelIndex, int, int)),
            self, SIGNAL(bookmarksChanged()))


BookmarkManager.~BookmarkManager()
    treeModel.clear()
    listModel.clear()


def treeBookmarkModel(self):
    return treeModel


def listBookmarkModel(self):
    return listModel


def saveBookmarks(self):
    QByteArray bookmarks
    QDataStream stream(&bookmarks, QIODevice.WriteOnly)

    readBookmarksRecursive(treeModel.invisibleRootItem(), stream, 0)
    helpEngine.setCustomValue(QLatin1String("Bookmarks"), bookmarks)


def bookmarkFolders(self):
    QStringList folders(tr("Bookmarks"))

    QList<QStandardItem*>list = treeModel.findItems(QLatin1String("*"),
                                Qt.MatchWildcard | Qt.MatchRecursive, 0)

    QString data
    foreach ( QStandardItem *item, list)
        data = item.data(Qt.UserRole + 10).toString()
        if data == QLatin1String("Folder"):
            folders << item.data(Qt.DisplayRole).toString()

    return folders


def addNewFolder(self, &index):
    QStandardItem *item = QStandardItem(uniqueFolderName())
    item.setEditable(False)
    item.setData(False, Qt.UserRole + 11)
    item.setData(QLatin1String("Folder"), Qt.UserRole + 10)
    item.setIcon(QApplication.style().standardIcon(QStyle.SP_DirClosedIcon))

    if index.isValid():
        treeModel.itemFromIndex(index).appendRow(item)

    else:
        treeModel.appendRow(item)

    return treeModel.indexFromItem(item)


void BookmarkManager.removeBookmarkItem(QTreeView *treeView,
         QModelIndex &index)
    QStandardItem *item = treeModel.itemFromIndex(index)
    if item:
        data = index.data(Qt.UserRole + 10).toString()
        if data == QLatin1String("Folder") and item.rowCount() > 0:
            value = QMessageBox.question(treeView, tr("Remove"),
                                              tr("You are going to delete a Folder, will also<br>"
                                                 "remove it's content. Are you sure to continue?"),
                                              QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)

            if value == QMessageBox.Cancel:
                return


        if data != QLatin1String("Folder"):
            QList<QStandardItem*>itemList = listModel.findItems(item.text())
            foreach ( QStandardItem *i, itemList)
                if i.data(Qt.UserRole + 10) == data:
                    listModel.removeRow(i.row())
                    break



        else:
            removeBookmarkFolderItems(item)

        treeModel.removeRow(item.row(), index.parent())



void BookmarkManager.showBookmarkDialog(QWidget *parent, &name,
         QString &url)
    BookmarkDialog dialog(self, name, url, parent)
    dialog.exec()


void BookmarkManager.addNewBookmark( QModelIndex &index,
                                      QString &name, &url)
    QStandardItem *item = QStandardItem(name)
    item.setEditable(False)
    item.setData(False, Qt.UserRole + 11)
    item.setData(url, Qt.UserRole + 10)

    if index.isValid():
        treeModel.itemFromIndex(index).appendRow(item)
    else:
        treeModel.appendRow(item)
    listModel.appendRow(item.clone())
    bookmarksChanged.emit()


def fillBookmarkMenu(self, *menu):
    if not menu or not treeModel:
        return

    map.clear()
    fillBookmarkMenu(menu, treeModel.invisibleRootItem())


def fillBookmarkMenu(self, *menu, *root):
    for (i = 0; i < root.rowCount(); ++i)
        QStandardItem *item = root.child(i)
        if item and item.data(Qt.UserRole + 10:
                .toString() == QLatin1String("Folder"))
            newMenu = menu.addMenu(folderIcon, item.text())
            if item.rowCount() > 0:
                fillBookmarkMenu(newMenu, item)

        else:
            map.insert(menu.addAction(item.text()), item.index())




def urlForAction(self, action):
    if map.contains(action):
         QModelIndex &index = map.value(action)
        if item = treeModel.itemFromIndex(index):
            return QUrl(item.data(Qt.UserRole + 10).toString())

    return QUrl()


def itemChanged(self, *item):
    if renameItem != item:
        renameItem = item
        oldText = item.text()
        return


    if item.text() != oldText:
        if item.data(Qt.UserRole + 10).toString() != QLatin1String("Folder"):
            QList<QStandardItem*>itemList = listModel.findItems(oldText)
            if itemList.count() > 0:
                itemList.at(0).setText(item.text())




def setupBookmarkModels(self):
    treeModel.clear()
    listModel.clear()

    qint32 depth
    bool expanded
    QString name, type
    QList<int> lastDepths
    QList<QStandardItem*> parents

    QByteArray ba =
        helpEngine.customValue(QLatin1String("Bookmarks")).toByteArray()
    QDataStream stream(ba)
    while (not stream.atEnd())
        stream >> depth >> name >> type >> expanded

        QStandardItem *item = QStandardItem(name)
        item.setEditable(False)
        item.setData(type, Qt.UserRole + 10)
        item.setData(expanded, Qt.UserRole + 11)
        if depth == 0:
            parents.clear()
            lastDepths.clear()
            treeModel.appendRow(item)
            parents << item
            lastDepths << depth

        else:
            if depth <= lastDepths.last():
                while (depth <= lastDepths.last() and parents.count() > 0)
                    parents.pop_back()
                    lastDepths.pop_back()


            parents.last().appendRow(item)
            if type == QLatin1String("Folder"):
                parents << item
                lastDepths << depth



        if type == QLatin1String("Folder"):
            item.setIcon(folderIcon)
        else:
            listModel.appendRow(item.clone())



def uniqueFolderName(self):
    folderName = tr("New Folder")
    QList<QStandardItem*> list = treeModel.findItems(folderName,
                                 Qt.MatchContains | Qt.MatchRecursive, 0)
    if not list.isEmpty():
        QStringList names
        foreach ( QStandardItem *item, list)
        names << item.text()

        for (i = 1; i <= names.count(); ++i)
            folderName = (tr("New Folder") + QLatin1String(" %1")).arg(i)
            if not names.contains(folderName):
                break


    return folderName


def removeBookmarkFolderItems(self, *item):
    for (j = 0; j < item.rowCount(); ++j)
        QStandardItem *child = item.child(j)
        if child.rowCount() > 0:
            removeBookmarkFolderItems(child)

        data = child.data(Qt.UserRole + 10).toString()
        QList<QStandardItem*>itemList = listModel.findItems(child.text())
        foreach ( QStandardItem *i, itemList)
            if i.data(Qt.UserRole + 10) == data:
                listModel.removeRow(i.row())
                break





void BookmarkManager.readBookmarksRecursive( QStandardItem *item,
        QDataStream &stream, depth)
    for (j = 0; j < item.rowCount(); ++j)
         QStandardItem *child = item.child(j)
        stream << depth
        stream << child.data(Qt.DisplayRole).toString()
        stream << child.data(Qt.UserRole + 10).toString()
        stream << child.data(Qt.UserRole + 11).toBool()

        if child.rowCount() > 0:
            readBookmarksRecursive(child, stream, (depth +1))



QT_END_NAMESPACE
