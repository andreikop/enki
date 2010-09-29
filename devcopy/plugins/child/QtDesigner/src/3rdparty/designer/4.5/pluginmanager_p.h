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

#
#  W A R N I N G
#  -------------
#
# This file is not part of the Qt API.  It exists for the convenience
# of Qt Designer.  This header
# file may change from version to version without notice, even be removed.
#
# We mean it.
#

#ifndef PLUGINMANAGER_H
#define PLUGINMANAGER_H

#include "shared_global_p.h"

#include <QtCore/QSharedDataPointer>
#include <QtCore/QMap>
#include <QtCore/QStringList>

QT_BEGIN_NAMESPACE

class QDesignerFormEditorInterface
class QDesignerCustomWidgetInterface
class QDesignerPluginManagerPrivate

class QDesignerCustomWidgetSharedData

''' Information contained in the Dom XML of a custom widget. '''
class QDESIGNER_SHARED_EXPORT QDesignerCustomWidgetDatapublic:
    explicit QDesignerCustomWidgetData( QString &pluginPath = QString())

    enum ParseResult { ParseOk, ParseWarning, ParseError
    ParseResult parseXml( QString &xml, &name, *errorMessage)

    QDesignerCustomWidgetData( QDesignerCustomWidgetData&)
    QDesignerCustomWidgetData& operator=( QDesignerCustomWidgetData&)
    ~QDesignerCustomWidgetData()

    bool isNull()

    QString pluginPath()

    # Data as parsed from the widget's domXML().
    QString xmlClassName()
    # Optional. The language the plugin is supposed to be used with.
    QString xmlLanguage()
    # Optional. method used to add pages to a container with a container extension
    QString xmlAddPageMethod()
    # Optional. Base class
    QString xmlExtends()
    # Optional. The name to be used in the widget box.
    QString xmlDisplayName()

private:
    QSharedDataPointer<QDesignerCustomWidgetSharedData> m_d


class QDESIGNER_SHARED_EXPORT QDesignerPluginManager: public QObject
    Q_OBJECT
public:
    typedef QList<QDesignerCustomWidgetInterface*> CustomWidgetList

    explicit QDesignerPluginManager(QDesignerFormEditorInterface *core)
    virtual ~QDesignerPluginManager()

    QDesignerFormEditorInterface *core()

    QObject *instance( QString &plugin)

    QStringList registeredPlugins()

    QStringList findPlugins( QString &path)

    QStringList pluginPaths()
    void setPluginPaths( QStringList &plugin_paths)

    QStringList disabledPlugins()
    void setDisabledPlugins( QStringList &disabled_plugins)

    QStringList failedPlugins()
    QString failureReason( QString &pluginName)

    QObjectList instances()

    CustomWidgetList registeredCustomWidgets()
    QDesignerCustomWidgetData customWidgetData(QDesignerCustomWidgetInterface *w)

    bool registerNewPlugins()

public slots:
    bool syncSettings()
    void ensureInitialized()

private:
    void updateRegisteredPlugins()
    void registerPath( QString &path)
    void registerPlugin( QString &plugin)

private:
    static QStringList defaultPluginPaths()

    QDesignerPluginManagerPrivate *m_d


QT_END_NAMESPACE

#endif # PLUGINMANAGER_H
