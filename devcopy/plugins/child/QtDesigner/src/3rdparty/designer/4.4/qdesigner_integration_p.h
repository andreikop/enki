'''***************************************************************************
**
** Copyright (C) 2008 Nokia Corporation and/or its subsidiary(-ies).
** Contact: Qt Software Information (qt-info@nokia.com)
**
** This file is part of the Qt Designer of the Qt Toolkit.
**
** Commercial Usage
** Licensees holding valid Qt Commercial licenses may use self file in
** accordance with the Qt Commercial License Agreement provided with the
** Software or, alternatively, accordance with the terms contained in
** a written agreement between you and Nokia.
**
**
** GNU General Public License Usage
** Alternatively, file may be used under the terms of the GNU
** General Public License versions 2.0 or 3.0 as published by the Free
** Software Foundation and appearing in the file LICENSE.GPL included in
** the packaging of self file.  Please review the following information
** to ensure GNU General Public Licensing requirements will be met:
** http:#www.fsf.org/licensing/licenses/info/GPLv2.html and
** http:#www.gnu.org/copyleft/gpl.html.  In addition, a special
** exception, gives you certain additional rights. These rights
** are described in the Nokia Qt GPL Exception version 1.3, in
** the file GPL_EXCEPTION.txt in self package.
**
** Qt for Windows(R) Licensees
** As a special exception, Nokia, the sole copyright holder for Qt
** Designer, users of the Qt/Eclipse Integration plug-in the
** right for the Qt/Eclipse Integration to link to functionality
** provided by Qt Designer and its related libraries.
**
** If you are unsure which license is appropriate for your use, please
** contact the sales department at qt-sales@nokia.com.
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
    void emitObjectNameChanged(QDesignerFormWindowInterface *formWindow, *object, &newName, &oldName)

    # Create a resource browser specific to integration. Language integration takes precedence
    virtual QDesignerResourceBrowserInterface *createResourceBrowser(QWidget *parent = 0)

signals:
    void propertyChanged(QDesignerFormWindowInterface *formWindow, &name, &value)
    void objectNameChanged(QDesignerFormWindowInterface *formWindow, *object, &newName, &oldName)
    void helpRequested( QString &manual, &document)

public slots:
    virtual void updateProperty( QString &name, &value, enableSubPropertyHandling)
    # Additional signals of designer property editor
    virtual void updatePropertyComment( QString &name, &value)
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
