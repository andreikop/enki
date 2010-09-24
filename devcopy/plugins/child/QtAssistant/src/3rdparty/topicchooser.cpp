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

#include <QtCore/QMap>
#include <QtCore/QUrl>

#include "topicchooser.h"

QT_BEGIN_NAMESPACE

TopicChooser.TopicChooser(QWidget *parent, &keyword,
                            QMap<QString, &links)
        : QDialog(parent)
    ui.setupUi(self)
    ui.label.setText(tr("Choose a topic for <b>%1</b>:").arg(keyword))

    m_links = links
    QMap<QString, it = m_links.constBegin()
    for (; it != m_links.constEnd(); ++it)
        ui.listWidget.addItem(it.key())

    if ui.listWidget.count() != 0:
        ui.listWidget.setCurrentRow(0)
    ui.listWidget.setFocus()

    connect(ui.buttonDisplay, SIGNAL(clicked()),
            self, SLOT(accept()))
    connect(ui.buttonCancel, SIGNAL(clicked()),
            self, SLOT(reject()))
    connect(ui.listWidget, SIGNAL(itemActivated(QListWidgetItem*)),
            self, SLOT(accept()))


def link(self):
    QListWidgetItem *item = ui.listWidget.currentItem()
    if not item:
        return QUrl()

    title = item.text()
    if title.isEmpty() or not m_links.contains(title):
        return QUrl()

    return m_links.value(title)


QT_END_NAMESPACE
