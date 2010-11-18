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

#ifndef BOOKMARKMANAGER_H
#define BOOKMARKMANAGER_H

#include "ui_bookmarkdialog.h"

#include <QtCore/QUrl>
#include <QtCore/QObject>
#include <QtCore/QString>
#include <QtCore/QByteArray>
#include <QtCore/QDataStream>

#include <QtGui/QIcon>
#include <QtGui/QDialog>
#include <QtGui/QWidget>
#include <QtGui/QTreeView>
#include <QtGui/QStandardItemModel>

QT_BEGIN_NAMESPACE

class QEvent
class QLineEdit
class QTreeView
class QToolButton
class QStandardItem
class QHelpEngineCore
class QAbstractItemModel
class QSortFilterProxyModel

class BookmarkManager

class BookmarkDialog : public QDialog
    Q_OBJECT

public:
    BookmarkDialog(BookmarkManager *manager, &title,
         QString &url, *parent = 0)
    ~BookmarkDialog()

private slots:
    void addAccepted()
    void addNewFolder()
    void toolButtonClicked()
    void itemChanged(QStandardItem *item)
    void textChanged( QString& string)
    void selectBookmarkFolder( QString &folderName)
    void customContextMenuRequested( QPoint &point)
    void currentChanged( QModelIndex& current)

private:
    bool eventFilter(QObject *object, *e)

private:
    QString m_url
    QString m_title

    QString oldText
    QStandardItem *renameItem

    Ui.BookmarkDialog ui
    BookmarkManager *bookmarkManager
    QSortFilterProxyModel *proxyModel


class TreeView : public QTreeView    Q_OBJECT
public:
    TreeView(parent = 0) : QTreeView(parent) {
    void subclassKeyPressEvent(QKeyEvent* event)
        QTreeView.keyPressEvent(event)



class BookmarkWidget : public QWidget
    Q_OBJECT

public:
    BookmarkWidget(BookmarkManager *manager, *parent = 0,
        showButtons = True)
    ~BookmarkWidget()

signals:
    void addBookmark()
    void requestShowLink( QUrl &url)
    void requestShowLinkInNewTab( QUrl &url)
    void escapePressed()

private slots:
    void removeClicked()
    void filterChanged()
    void expand( QModelIndex& index)
    void activated( QModelIndex &index)
    void customContextMenuRequested( QPoint &point)

private:
    void setup(bool showButtons)
    void expandItems()
    void focusInEvent(QFocusEvent *e)
    bool eventFilter(QObject *object, *event)

private:
    QRegExp regExp
    TreeView *treeView
    QLineEdit *searchField
    QToolButton *addButton
    QToolButton *removeButton
    BookmarkManager *bookmarkManager
    QSortFilterProxyModel* filterBookmarkModel


class BookmarkModel : public QStandardItemModel
    Q_OBJECT

public:
    BookmarkModel(int rows, columns, *parent = 0)
    ~BookmarkModel()

    Qt.DropActions supportedDropActions()
    Qt.ItemFlags flags( QModelIndex &index)


class BookmarkManager : public QObject
    Q_OBJECT

public:
    BookmarkManager(QHelpEngineCore* helpEngine)
    ~BookmarkManager()

    BookmarkModel* treeBookmarkModel()
    BookmarkModel* listBookmarkModel()

    void saveBookmarks()
    QStringList bookmarkFolders()
    QModelIndex addNewFolder( QModelIndex& index)
    void removeBookmarkItem(QTreeView *treeView, index)
    void showBookmarkDialog(QWidget* parent, &name,
         QString &url)
    void addNewBookmark( QModelIndex& index, &name,
         QString &url)
    void setupBookmarkModels()

    void fillBookmarkMenu(QMenu *menu)
    QUrl urlForAction(QAction* action)

signals:
    void bookmarksChanged()

private slots:
    void itemChanged(QStandardItem *item)

private:
    QString uniqueFolderName()
    void removeBookmarkFolderItems(QStandardItem *item)
    void readBookmarksRecursive( QStandardItem *item, &stream,
         qint32 depth)
    void fillBookmarkMenu(QMenu *menu, *root)

private:
    QString oldText
    QIcon folderIcon

    BookmarkModel *treeModel
    BookmarkModel *listModel
    QStandardItem *renameItem
    QHelpEngineCore *helpEngine
    QMap<QAction*, map


QT_END_NAMESPACE

#endif
