'''*************************************************************************
**
** This file is part of Qt Creator
**
** Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
**
** Contact:  Qt Software Information (qt-info@nokia.com)
**
** Commercial Usage
**
** Licensees holding valid Qt Commercial licenses may use self file in
** accordance with the Qt Commercial License Agreement provided with the
** Software or, alternatively, accordance with the terms contained in
** a written agreement between you and Nokia.
**
** GNU Lesser General Public License Usage
**
** Alternatively, file may be used under the terms of the GNU Lesser
** General Public License version 2.1 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU Lesser General Public License version 2.1 requirements
** will be met: http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** If you are unsure which license is appropriate for your use, please
** contact the sales department at qt-sales@nokia.com.
**
*************************************************************************'''

#include "formresizer.h"
#include "sizehandlerect.h"
#include "widgethostconstants.h"

#include <QtCore/QDebug>

#include <QtDesigner/QDesignerFormWindowInterface>

#include <QtGui/QResizeEvent>
#include <QtGui/QPalette>
#include <QtGui/QLayout>
#include <QtGui/QFrame>
#include <QtGui/QResizeEvent>

enum { debugFormResizer = 0

using namespace SharedTools.Internal

FormResizer.FormResizer(QWidget *parent) :
        QWidget(parent),
        m_frame(new QFrame),
        m_formWindow(0)
    # Make the resize grip of a mainwindow form find us as resizable window.
    setWindowFlags(windowFlags() | Qt.SubWindow)
    setBackgroundRole(QPalette.Base)

    QVBoxLayout *handleLayout = QVBoxLayout(self)
    handleLayout.setMargin(SELECTION_MARGIN)
    handleLayout.addWidget(m_frame)

    m_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
    QVBoxLayout *layout = QVBoxLayout(m_frame)
    layout.setMargin(0)
    # handles
    m_handles.reserve(SizeHandleRect.Left)
    for (i = SizeHandleRect.LeftTop; i <= SizeHandleRect.Left; ++i)
        SizeHandleRect *shr = SizeHandleRect(self, static_cast<SizeHandleRect.Direction>(i), self)
        connect(shr, SIGNAL(mouseButtonReleased(QRect,QRect)), self, SIGNAL(formWindowSizeChanged(QRect,QRect)))
        m_handles.push_back(shr)

    setState(SelectionHandleActive)
    updateGeometry()


def updateGeometry(self):
     QRect &geom = m_frame.geometry()

    if debugFormResizer:
        qDebug() << "FormResizer.updateGeometry() " << size() << " frame " << geom

     w = SELECTION_HANDLE_SIZE
     h = SELECTION_HANDLE_SIZE

     hend =  m_handles.end()
    for (it = m_handles.begin(); it != hend; ++it)
        SizeHandleRect *hndl = *it
        switch (hndl.dir())
        case SizeHandleRect.LeftTop:
            hndl.move(geom.x() - w / 2, geom.y() - h / 2)
            break
        case SizeHandleRect.Top:
            hndl.move(geom.x() + geom.width() / 2 - w / 2, geom.y() - h / 2)
            break
        case SizeHandleRect.RightTop:
            hndl.move(geom.x() + geom.width() - w / 2, geom.y() - h / 2)
            break
        case SizeHandleRect.Right:
            hndl.move(geom.x() + geom.width() - w / 2, geom.y() + geom.height() / 2 - h / 2)
            break
        case SizeHandleRect.RightBottom:
            hndl.move(geom.x() + geom.width() - w / 2, geom.y() + geom.height() - h / 2)
            break
        case SizeHandleRect.Bottom:
            hndl.move(geom.x() + geom.width() / 2 - w / 2, geom.y() + geom.height() - h / 2)
            break
        case SizeHandleRect.LeftBottom:
            hndl.move(geom.x() - w / 2, geom.y() + geom.height() - h / 2)
            break
        case SizeHandleRect.Left:
            hndl.move(geom.x() - w / 2, geom.y() + geom.height() / 2 - h / 2)
            break
        default:
            break




def update(self):
     hend =  m_handles.end()
    for (it = m_handles.begin(); it != hend; ++it)
        (*it).update()



def setState(self, st):
    if debugFormResizer:
        qDebug() << "FormResizer.setState " << st

     hend =  m_handles.end()
    for (it = m_handles.begin(); it != hend; ++it)
        (*it).setState(st)


def setFormWindow(self, *fw):
    if debugFormResizer:
        qDebug() << "FormResizer.setFormWindow " << fw
    QVBoxLayout *layout = qobject_cast<QVBoxLayout *>(m_frame.layout())
    Q_ASSERT(layout)
    if layout.count():
        delete layout.takeAt(0)
    m_formWindow = fw

    if m_formWindow:
        layout.addWidget(m_formWindow)
    mainContainerChanged()
    fw.mainContainerChanged.connect(self.mainContainerChanged)


def resizeEvent(self, *event):
    if debugFormResizer:
        qDebug() << ">FormResizer.resizeEvent" <<  event.size()
    updateGeometry()
    QWidget.resizeEvent(event)
    if debugFormResizer:
        qDebug() << "<FormResizer.resizeEvent"


def decorationSize(self):
     margin = 2 * SELECTION_MARGIN + 2 * m_frame.lineWidth()
    return QSize(margin, margin)


QWidget *FormResizer.mainContainer()
    if m_formWindow:
        return m_formWindow.mainContainer()
    return 0


def mainContainerChanged(self):
     maxWidgetSize = QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
    if  QWidget *mc = mainContainer():
        # Set Maximum size which is not handled via a hint (as opposed to minimum size)
         maxWidgetSize = QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
         formMaxSize = mc.maximumSize()
        newMaxSize = maxWidgetSize
        if formMaxSize != maxWidgetSize:
            newMaxSize = formMaxSize + decorationSize()
        if debugFormResizer:
            qDebug() << "FormResizer.mainContainerChanged" <<  mc << " Size " << mc.size()<< newMaxSize
        setMaximumSize(newMaxSize)
        resize(decorationSize() + mc.size())

    else:
        setMaximumSize(maxWidgetSize)


