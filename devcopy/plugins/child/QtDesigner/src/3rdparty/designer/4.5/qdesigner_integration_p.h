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

#ifndef QDESIGNER_INTEGRATION_H
#define QDESIGNER_INTEGRATION_H

#include "shared_global_p.h"
#include <QtDesigner/QDesignerIntegrationInterface>

#include <QtCore/QObject>

QT_BEGIN_NAMESPACE

class QDesignerFormEditorInterface
class QDesignerFormWindowInterface
class QDesignerResourceBrowserInterface

class QVariant
class QWidget

namespace qdesigner_internal

struct Selection
class QDesignerIntegrationPrivate

class QDESIGNER_SHARED_EXPORT QDesignerIntegration: public QDesignerIntegrationInterface
    Q_OBJECT
public:
    explicit QDesignerIntegration(QDesignerFormEditorInterface *core, *parent = 0)
    virtual ~QDesignerIntegration()

    static void requestHelp( QDesignerFormEditorInterface *core, &manual, &document)

    virtual QWidget *containerWindow(QWidget *widget)

    # Load plugins into widget database and factory.
    static void initializePlugins(QDesignerFormEditorInterface *formEditor)
    void emitObjectNameChanged(QDesignerFormWindowInterface *formWindow, *object,
                                QString &newName, &oldName)
    void emitNavigateToSlot( QString &objectName, &signalSignature, &parameterNames)
    void emitNavigateToSlot( QString &slotSignature)

    # Create a resource browser specific to integration. Language integration takes precedence
    virtual QDesignerResourceBrowserInterface *createResourceBrowser(QWidget *parent = 0)

    enum ResourceFileWatcherBehaviour
        NoWatcher,
        ReloadSilently,
        PromptAndReload


    ResourceFileWatcherBehaviour resourceFileWatcherBehaviour()
    bool isResourceEditingEnabled()
    bool isSlotNavigationEnabled()

protected:

    void setResourceFileWatcherBehaviour(ResourceFileWatcherBehaviour behaviour); # PromptAndReload by default
    void setResourceEditingEnabled(bool enable); # True by default
    void setSlotNavigationEnabled(bool enable); # False by default

signals:
    void propertyChanged(QDesignerFormWindowInterface *formWindow, &name, &value)
    void objectNameChanged(QDesignerFormWindowInterface *formWindow, *object, &newName, &oldName)
    void helpRequested( QString &manual, &document)

    void navigateToSlot( QString &objectName, &signalSignature, &parameterNames)
    void navigateToSlot( QString &slotSignature)

public slots:
    virtual void updateProperty( QString &name, &value, enableSubPropertyHandling)
    # Additional signals of designer property editor
    virtual void resetProperty( QString &name)
    virtual void addDynamicProperty( QString &name, &value)
    virtual void removeDynamicProperty( QString &name)

    virtual void updateActiveFormWindow(QDesignerFormWindowInterface *formWindow)
    virtual void setupFormWindow(QDesignerFormWindowInterface *formWindow)
    virtual void updateSelection()
    virtual void updateGeometry()
    virtual void activateWidget(QWidget *widget)

    void updateCustomWidgetPlugins()

private slots:
    void updatePropertyPrivate( QString &name, &value)

private:
    void initialize()
    void getSelection(Selection &s)
    QObject *propertyEditorObject()

    QDesignerIntegrationPrivate *m_d


} # namespace qdesigner_internal

QT_END_NAMESPACE

#endif # QDESIGNER_INTEGRATION_H
