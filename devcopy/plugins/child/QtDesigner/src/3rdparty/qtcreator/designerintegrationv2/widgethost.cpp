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

#include "widgethost.h"
#include "formresizer.h"
#include "widgethostconstants.h"

#include <QtDesigner/QDesignerFormWindowInterface>
#include <QtDesigner/QDesignerFormWindowCursorInterface>

#include <QtGui/QPalette>
#include <QtGui/QLayout>
#include <QtGui/QFrame>
#include <QtGui/QResizeEvent>
#include <QtCore/QDebug>

using namespace SharedTools

# ---------- WidgetHost
WidgetHost.WidgetHost(QWidget *parent, *formWindow) :
        QScrollArea(parent),
        m_formWindow(0),
        m_formResizer(new Internal.FormResizer)
    setWidget(m_formResizer)
    # Re-set flag (gets cleared by QScrollArea): Make the resize grip of a mainwindow form find the resizer as resizable window.
    m_formResizer.setWindowFlags(m_formResizer.windowFlags() | Qt.SubWindow)
    setFormWindow(formWindow)


WidgetHost.~WidgetHost()
    if m_formWindow:
        delete m_formWindow


def setFormWindow(self, *fw):
    m_formWindow = fw
    if not fw:
        return

    m_formResizer.setFormWindow(fw)

    setBackgroundRole(QPalette.Base)
    m_formWindow.setAutoFillBackground(True)
    m_formWindow.setBackgroundRole(QPalette.Background)

    connect(m_formResizer, SIGNAL(formWindowSizeChanged(QRect, QRect)),
            self, SLOT(fwSizeWasChanged(QRect, QRect)))


def formWindowSize(self):
    if not m_formWindow or not m_formWindow.mainContainer():
        return QSize()
    return m_formWindow.mainContainer().size()


def fwSizeWasChanged(self, &, &):
    # newGeo is the mouse coordinates, moving the Right will actually wrong.emit height
    formWindowSizeChanged.emit(formWindowSize().width(), formWindowSize().height())


def updateFormWindowSelectionHandles(self, active):
    state = Internal.SelectionHandleOff
     QDesignerFormWindowCursorInterface *cursor = m_formWindow.cursor()
    if cursor.isWidgetSelected(m_formWindow.mainContainer()):
        state = active ? Internal.SelectionHandleActive :  Internal.SelectionHandleInactive

    m_formResizer.setState(state)


QWidget *WidgetHost.integrationContainer()
    return m_formResizer

