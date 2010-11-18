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

#ifndef QDESIGNER_FORMBUILDER_H
#define QDESIGNER_FORMBUILDER_H

#include "shared_global_p.h"
#include "deviceprofile_p.h"

#include "formscriptrunner_p.h"
#include "formbuilder.h"

#include <QtCore/QMap>
#include <QtCore/QSet>

QT_BEGIN_NAMESPACE

class QDesignerFormEditorInterface
class QDesignerFormWindowInterface

class QPixmap
class QtResourceSet

namespace qdesigner_internal
class DesignerPixmapCache
class DesignerIconCache

''' Form builder used for previewing forms, box and form dialog.
 * It applies the system settings to its toplevel window. '''

class QDESIGNER_SHARED_EXPORT QDesignerFormBuilder: public QFormBuilder
public:
    enum Mode        DisableScripts,
        EnableScripts


    QDesignerFormBuilder(QDesignerFormEditorInterface *core,
                         Mode mode,
                          DeviceProfile &deviceProfile = DeviceProfile())

    QWidget *createWidgetFromContents( QString &contents, *parentWidget = 0)

    virtual QWidget *createWidget(DomWidget *ui_widget, *parentWidget = 0)
    { return QFormBuilder.create(ui_widget, parentWidget);

    inline QDesignerFormEditorInterface *core()
    { return m_core;

    QString systemStyle()

    typedef QFormScriptRunner.Errors ScriptErrors
    # Create a preview widget (for integrations) or return 0. The widget has to be embedded into a main window.
    # Experimental, on script support.
    static QWidget *createPreview( QDesignerFormWindowInterface *fw, &styleName ''' ="" ''',
                                   QString &appStyleSheet  ''' ="" ''',
                                   DeviceProfile &deviceProfile,
                                  ScriptErrors *scriptErrors, *errorMessage)
    # Convenience that pops up message boxes in case of failures.
    static QWidget *createPreview( QDesignerFormWindowInterface *fw, &styleName = QString())
    #  Create a preview widget (for integrations) or return 0. The widget has to be embedded into a main window.
    static QWidget *createPreview( QDesignerFormWindowInterface *fw, &styleName, &appStyleSheet, *errorMessage)
    static QWidget *createPreview( QDesignerFormWindowInterface *fw, &styleName, &appStyleSheet, &deviceProfile, *errorMessage)
    # Convenience that pops up message boxes in case of failures.
    static QWidget *createPreview( QDesignerFormWindowInterface *fw, &styleName, &appStyleSheet)

    # Create a preview image
    static QPixmap createPreviewPixmap( QDesignerFormWindowInterface *fw, &styleName = QString(), &appStyleSheet = QString())

protected:
    using QFormBuilder.createDom
    using QFormBuilder.create

    virtual QWidget *create(DomUI *ui, *parentWidget)
    virtual DomWidget *createDom(QWidget *widget, *ui_parentWidget, recursive = True)
    virtual QWidget *create(DomWidget *ui_widget, *parentWidget)
    virtual QLayout *create(DomLayout *ui_layout, *layout, *parentWidget)
    virtual void createResources(DomResources *resources)

    virtual QWidget *createWidget( QString &widgetName, *parentWidget, &name)
    virtual bool addItem(DomWidget *ui_widget, *widget, *parentWidget)
    virtual bool addItem(DomLayoutItem *ui_item, *item, *layout)

    virtual QIcon nameToIcon( QString &filePath, &qrcPath)
    virtual QPixmap nameToPixmap( QString &filePath, &qrcPath)

    virtual void applyProperties(QObject *o, &properties)

    virtual void loadExtraInfo(DomWidget *ui_widget, *widget, *parentWidget)

    QtResourceSet *internalResourceSet()  { return m_tempResourceSet;

    DeviceProfile deviceProfile()  { return m_deviceProfile;

private:
    QDesignerFormEditorInterface *m_core
     Mode m_mode

    typedef QSet<QWidget *> WidgetSet
    WidgetSet m_customWidgetsWithScript

     DeviceProfile m_deviceProfile

    DesignerPixmapCache *m_pixmapCache
    DesignerIconCache *m_iconCache
    bool m_ignoreCreateResources
    QtResourceSet *m_tempResourceSet
    bool m_mainWidget


} # namespace qdesigner_internal

QT_END_NAMESPACE

#endif # QDESIGNER_FORMBUILDER_H
