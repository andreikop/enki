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

#include <QtCore/QDir>
#include <QtCore/QLibraryInfo>
#include <QtCore/QDateTime>
#include <QtHelp/QHelpEngineCore>
#include "qtdocinstaller.h"

QT_BEGIN_NAMESPACE

QtDocInstaller.QtDocInstaller( QString &collectionFile)
    m_abort = False
    m_collectionFile = collectionFile


QtDocInstaller.~QtDocInstaller()
    if not isRunning():
        return
    m_mutex.lock()
    m_abort = True
    m_mutex.unlock()
    wait()


def installDocs(self):
    start(LowPriority)


def run(self):
    QHelpEngineCore *helpEngine = QHelpEngineCore(m_collectionFile)
    helpEngine.setupData()
    changes = False

    QStringList docs
    docs << QLatin1String("assistant")
        << QLatin1String("designer")
        << QLatin1String("linguist")
        << QLatin1String("qmake")
        << QLatin1String("qt")

    foreach ( QString &doc, docs)        changes |= installDoc(doc, helpEngine)
        m_mutex.lock()
        if m_abort:            delete helpEngine
            m_mutex.unlock()
            return

        m_mutex.unlock()

    delete helpEngine
    docsInstalled.emit(changes)


def installDoc(self, &name, *helpEngine):
    versionKey = QString(QLatin1String("qtVersion%1$$$%2")).
        arg(QLatin1String(QT_VERSION_STR)).arg(name)

    info = helpEngine.customValue(versionKey, QString()).toString()
    lst = info.split(QLatin1String("|"))

    QDateTime dt
    if lst.count() and not lst.first().isEmpty():
        dt = QDateTime.fromString(lst.first(), Qt.ISODate)

    QString qchFile
    if lst.count() == 2:
        qchFile = lst.last()

    QDir dir(QLibraryInfo.location(QLibraryInfo.DocumentationPath)
        + QDir.separator() + QLatin1String("qch"))

     files = dir.entryList(QStringList() << QLatin1String("*.qch"))
    if files.isEmpty():        helpEngine.setCustomValue(versionKey, QDateTime().toString(Qt.ISODate)
            + QLatin1String("|"))
        return False

    foreach ( QString &f, files)        if f.startsWith(name):            QFileInfo fi(dir.absolutePath() + QDir.separator() + f)
            if dt.isValid() and fi.lastModified().toString(Qt.ISODate) == dt.toString(Qt.ISODate:
                and qchFile == fi.absoluteFilePath())
                return False

            namespaceName = QHelpEngineCore.namespaceName(fi.absoluteFilePath())
            if namespaceName.isEmpty():
                continue

            if helpEngine.registeredDocumentations().contains(namespaceName):
                helpEngine.unregisterDocumentation(namespaceName)

            if not helpEngine.registerDocumentation(fi.absoluteFilePath()):                errorMessage.emit(
                    tr("The file %1 could not be registered successfullynot \n\nReason: %2")
                    .arg(fi.absoluteFilePath()).arg(helpEngine.error()))


            helpEngine.setCustomValue(versionKey, fi.lastModified().toString(Qt.ISODate)
                + QLatin1String("|") + fi.absoluteFilePath())
            return True


    return False


QT_END_NAMESPACE
