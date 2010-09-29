'''***************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
** Contact: Qt Software Information (qt-info@nokia.com)
**
** This file is part of the Qt Designer of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial Usage
** Licensees holding valid Qt Commercial licenses may use self file in
** accordance with the Qt Commercial License Agreement provided with the
** Software or, alternatively, accordance with the terms contained in
** a written agreement between you and Nokia.
**
** GNU Lesser General Public License Usage
** Alternatively, file may be used under the terms of the GNU Lesser
** General Public License version 2.1 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU Lesser General Public License version 2.1 requirements
** will be met: http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, a special exception, gives you certain
** additional rights. These rights are described in the Nokia Qt LGPL
** Exception version 1.0, in the file LGPL_EXCEPTION.txt in self
** package.
**
** GNU General Public License Usage
** Alternatively, file may be used under the terms of the GNU
** General Public License version 3.0 as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU General Public License version 3.0 requirements will be
** met: http:#www.gnu.org/copyleft/gpl.html.
**
** If you are unsure which license is appropriate for your use, please
** contact the sales department at qt-sales@nokia.com.
** $QT_END_LICENSE$
**
***************************************************************************'''

#ifndef FORMBUILDER_H
#define FORMBUILDER_H

#include <QtDesigner/uilib_global.h>
#include <QtDesigner/QAbstractFormBuilder>

#include <QtCore/QStringList>
#include <QtCore/QMap>

QT_BEGIN_HEADER

QT_BEGIN_NAMESPACE
#if 0
# pragma for syncqt, don't remove.

#pragma qt_class(QFormBuilder)
#endif

class QDesignerCustomWidgetInterface

#ifdef QFORMINTERNAL_NAMESPACE
namespace QFormInternal
#endif

class QDESIGNER_UILIB_EXPORT QFormBuilder: public QAbstractFormBuilder
public:
    QFormBuilder()
    virtual ~QFormBuilder()

    QStringList pluginPaths()

    void clearPluginPaths()
    void addPluginPath( QString &pluginPath)
    void setPluginPath( QStringList &pluginPaths)

    QList<QDesignerCustomWidgetInterface*> customWidgets()

protected:
    virtual QWidget *create(DomUI *ui, *parentWidget)
    virtual QWidget *create(DomWidget *ui_widget, *parentWidget)
    virtual QLayout *create(DomLayout *ui_layout, *layout, *parentWidget)
    virtual QLayoutItem *create(DomLayoutItem *ui_layoutItem, *layout, *parentWidget)
    virtual QAction *create(DomAction *ui_action, *parent)
    virtual QActionGroup *create(DomActionGroup *ui_action_group, *parent)

    virtual QWidget *createWidget( QString &widgetName, *parentWidget, &name)
    virtual QLayout *createLayout( QString &layoutName, *parent, &name)

    virtual void createConnections(DomConnections *connections, *widget)

    virtual bool addItem(DomLayoutItem *ui_item, *item, *layout)
    virtual bool addItem(DomWidget *ui_widget, *widget, *parentWidget)

    virtual void updateCustomWidgets()
    virtual void applyProperties(QObject *o, &properties)

    static QWidget *widgetByName(QWidget *topLevel, &name)

private:
    QStringList m_pluginPaths
    QMap<QString, m_customWidgets


#ifdef QFORMINTERNAL_NAMESPACE

#endif

QT_END_NAMESPACE

QT_END_HEADER

#endif # FORMBUILDER_H
