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

#include "qdesigner_formbuilder_p.h"
#include "dynamicpropertysheet.h"
#include "qsimpleresource_p.h"
#include "widgetfactory_p.h"
#include "qdesigner_introspection_p.h"

#include <ui4_p.h>
#include <formbuilderextra_p.h>
# sdk
#include <QtDesigner/container.h>
#include <QtDesigner/customwidget.h>
#include <QtDesigner/propertysheet.h>
#include <QtDesigner/QExtensionManager>
#include <QtDesigner/QDesignerFormEditorInterface>
#include <QtDesigner/QDesignerFormWindowInterface>
#include <QtDesigner/QDesignerWidgetFactoryInterface>
#include <QtDesigner/QDesignerCustomWidgetInterface>
#include <abstractdialoggui_p.h>

# shared
#include <qdesigner_propertysheet_p.h>
#include <qdesigner_utils_p.h>
#include <formwindowbase_p.h>
#include <qtresourcemodel_p.h>
#include <scripterrordialog_p.h>

#include <QtGui/QWidget>
#include <QtGui/QMenu>
#include <QtGui/QToolBar>
#include <QtGui/QMenuBar>
#include <QtGui/QMainWindow>
#include <QtGui/QStyleFactory>
#include <QtGui/QStyle>
#include <QtGui/QApplication>
#include <QtGui/QAbstractScrollArea>
#include <QtGui/QMessageBox>
#include <QtGui/QPixmap>

#include <QtCore/QBuffer>
#include <QtCore/qdebug.h>
#include <QtCore/QCoreApplication>

QT_BEGIN_NAMESPACE

static QString summarizeScriptErrors( QFormScriptRunner.Errors &errors)
    rc =  QCoreApplication.translate("QDesignerFormBuilder", "Script errors occurred:")
    foreach (QFormScriptRunner.Error error, errors)
        rc += QLatin1Char('\n')
        rc += error.errorMessage

    return rc


namespace qdesigner_internal

QDesignerFormBuilder.QDesignerFormBuilder(QDesignerFormEditorInterface *core,
        Mode mode,
         DeviceProfile &deviceProfile) :
        m_core(core),
        m_mode(mode),
        m_deviceProfile(deviceProfile),
        m_pixmapCache(0),
        m_iconCache(0),
        m_ignoreCreateResources(False),
        m_tempResourceSet(0),
        m_mainWidget(True)
    Q_ASSERT(m_core)
    # Disable scripting in the editors.
    options = formScriptRunner().options()
    switch (m_mode)
    case DisableScripts:
        options |= QFormScriptRunner.DisableScripts
        break
    case EnableScripts:
        options |= QFormScriptRunner.DisableWarnings
        options &= ~QFormScriptRunner.DisableScripts
        break

    formScriptRunner(). setOptions(options)


def systemStyle(self):
    return m_deviceProfile.isEmpty() ?
           QString.fromUtf8(QApplication.style().metaObject().className()) :
           m_deviceProfile.style()


QWidget *QDesignerFormBuilder.createWidgetFromContents( QString &contents, *parentWidget)
    data = contents.toUtf8()
    QBuffer buffer(&data)
    buffer.open(QIODevice.ReadOnly)
    return load(&buffer, parentWidget)


QWidget *QDesignerFormBuilder.create(DomUI *ui, *parentWidget)
    m_mainWidget = True
    QtResourceSet *resourceSet = core().resourceModel().currentResourceSet()

    # reload resource properties
    createResources(ui.elementResources())
    core().resourceModel().setCurrentResourceSet(m_tempResourceSet)

    m_ignoreCreateResources = True
    DesignerPixmapCache pixmapCache
    DesignerIconCache iconCache(&pixmapCache)
    m_pixmapCache = &pixmapCache
    m_iconCache = &iconCache

    QWidget *widget = QFormBuilder.create(ui, parentWidget)

    core().resourceModel().setCurrentResourceSet(resourceSet)
    core().resourceModel().removeResourceSet(m_tempResourceSet)
    m_tempResourceSet = 0
    m_ignoreCreateResources = False
    m_pixmapCache = 0
    m_iconCache = 0

    m_customWidgetsWithScript.clear()
    return widget


QWidget *QDesignerFormBuilder.createWidget( QString &widgetName, *parentWidget, &name)
    QWidget *widget = 0

    if widgetName == QLatin1String("QToolBar"):
        widget = QToolBar(parentWidget)

    elif widgetName == QLatin1String("QMenu"):
        widget = QMenu(parentWidget)

    elif widgetName == QLatin1String("QMenuBar"):
        widget = QMenuBar(parentWidget)

    else:
        widget = core().widgetFactory().createWidget(widgetName, parentWidget)


    if widget:
        widget.setObjectName(name)
        if QSimpleResource.hasCustomWidgetScript(m_core, widget):
            m_customWidgetsWithScript.insert(widget)


    if (m_mainWidget)   # We need to apply the DPI here to take effect on size hints, etc.
        m_deviceProfile.apply(m_core, widget, DeviceProfile.ApplyPreview)
        m_mainWidget = False

    return widget


def addItem(self, *ui_widget, *widget, *parentWidget):
    # Use container extension or rely on scripts unless main window.
    if QFormBuilder.addItem(ui_widget, widget, parentWidget):
        return True

    if QDesignerContainerExtension *container = qt_extension<QDesignerContainerExtension*>(m_core.extensionManager(), parentWidget):
        container.addWidget(widget)
        return True

    return False


def addItem(self, *ui_item, *item, *layout):
    return QFormBuilder.addItem(ui_item, item, layout)


def nameToIcon(self, &filePath, &qrcPath):
    Q_UNUSED(filePath)
    Q_UNUSED(qrcPath)
    qWarning() << "QDesignerFormBuilder.nameToIcon() is obsoleted"
    return QIcon()


def nameToPixmap(self, &filePath, &qrcPath):
    Q_UNUSED(filePath)
    Q_UNUSED(qrcPath)
    qWarning() << "QDesignerFormBuilder.nameToPixmap() is obsoleted"
    return QPixmap()


''' If the property is a enum or flag value, retrieve
 * the existing enum/flag type via property sheet and use it to convert '''

static bool readDomEnumerationValue( DomProperty *p,
                                     QDesignerPropertySheetExtension* sheet,
                                    QVariant &v)
    switch (p.kind())
    case DomProperty.Set:
         index = sheet.indexOf(p.attributeName())
        if index == -1:
            return False
         sheetValue = sheet.property(index)
        if qVariantCanConvert<PropertySheetFlagValue>(sheetValue):
             f = qvariant_cast<PropertySheetFlagValue>(sheetValue)
            ok = False
            v = f.metaFlags.parseFlags(p.elementSet(), &ok)
            if not ok:
                designerWarning(f.metaFlags.messageParseFailed(p.elementSet()))
            return True


    break
    case DomProperty.Enum:
         index = sheet.indexOf(p.attributeName())
        if index == -1:
            return False
         sheetValue = sheet.property(index)
        if qVariantCanConvert<PropertySheetEnumValue>(sheetValue):
             e = qvariant_cast<PropertySheetEnumValue>(sheetValue)
            ok = False
            v = e.metaEnum.parseEnum(p.elementEnum(), &ok)
            if not ok:
                designerWarning(e.metaEnum.messageParseFailed(p.elementEnum()))
            return True


    break
    default:
        break

    return False


def applyProperties(self, *o, &properties):
    typedef QList<DomProperty*> DomPropertyList

    if properties.empty():
        return

    QFormBuilderExtra *formBuilderExtra = QFormBuilderExtra.instance(self)
     QDesignerPropertySheetExtension *sheet = qt_extension<QDesignerPropertySheetExtension*>(core().extensionManager(), o)
     QDesignerDynamicPropertySheetExtension *dynamicSheet = qt_extension<QDesignerDynamicPropertySheetExtension*>(core().extensionManager(), o)
     changingMetaObject = WidgetFactory.classNameOf(core(), o) == QLatin1String("QAxWidget")
     QDesignerMetaObjectInterface *meta = core().introspection().metaObject(o)
     dynamicPropertiesAllowed = dynamicSheet and dynamicSheet.dynamicPropertiesAllowed()

    QDesignerPropertySheet *designerPropertySheet = qobject_cast<QDesignerPropertySheet *>(
                core().extensionManager().extension(o, Q_TYPEID(QDesignerPropertySheetExtension)))

    if designerPropertySheet:
        if designerPropertySheet.pixmapCache():
            designerPropertySheet.setPixmapCache(m_pixmapCache)
        if designerPropertySheet.iconCache():
            designerPropertySheet.setIconCache(m_iconCache)


     cend = properties.constEnd()
    for (it = properties.constBegin(); it != cend; ++it)
        DomProperty *p = *it
        QVariant v
        if not readDomEnumerationValue(p, sheet, v):
            v = toVariant(o.metaObject(), p)

        if v.isNull():
            continue

         attributeName = p.attributeName()
        if formBuilderExtra.applyPropertyInternally(o, attributeName, v):
            continue

        # refuse fake properties like current tab name (weak test)
        if not dynamicPropertiesAllowed:
            if (changingMetaObject) # Changes after setting control of QAxWidget
                meta = core().introspection().metaObject(o)
            if meta.indexOfProperty(attributeName) == -1:
                continue


        QObject *obj = o
        QAbstractScrollArea *scroll = qobject_cast<QAbstractScrollArea *>(o)
        if scroll and attributeName == QLatin1String("cursor") and scroll.viewport():
            obj = scroll.viewport()

        # a real property
        obj.setProperty(attributeName.toUtf8(), v)



DomWidget *QDesignerFormBuilder.createDom(QWidget *widget, *ui_parentWidget, recursive)
    DomWidget *ui_widget = QFormBuilder.createDom(widget, ui_parentWidget, recursive)
    QSimpleResource.addExtensionDataToDOM(self, m_core, ui_widget, widget)
    return ui_widget


QWidget *QDesignerFormBuilder.create(DomWidget *ui_widget, *parentWidget)
    QWidget *widget = QFormBuilder.create(ui_widget, parentWidget)
    # Do not apply state if scripts are to be run in preview mode
    QSimpleResource.applyExtensionDataFromDOM(self, m_core, ui_widget, widget, m_mode == DisableScripts)
    return widget


def createResources(self, *resources):
    if m_ignoreCreateResources:
        return
    QStringList paths
    if resources != 0:
         QList<DomResource*> dom_include = resources.elementInclude()
        foreach (DomResource *res, dom_include)
            path = QDir.cleanPath(workingDirectory().absoluteFilePath(res.attributeLocation()))
            paths << path



    m_tempResourceSet = core().resourceModel().addResourceSet(paths)


QLayout *QDesignerFormBuilder.create(DomLayout *ui_layout, *layout, *parentWidget)
    return QFormBuilder.create(ui_layout, layout, parentWidget)


def loadExtraInfo(self, *ui_widget, *widget, *parentWidget):
    QFormBuilder.loadExtraInfo(ui_widget, widget, parentWidget)


QWidget *QDesignerFormBuilder.createPreview( QDesignerFormWindowInterface *fw,
         QString &styleName,
         QString &appStyleSheet,
         DeviceProfile &deviceProfile,
        ScriptErrors *scriptErrors,
        QString *errorMessage)
    scriptErrors.clear()

    # load
    QDesignerFormBuilder builder(fw.core(), EnableScripts, deviceProfile)
    builder.setWorkingDirectory(fw.absoluteDir())

     warningsEnabled = QSimpleResource.setWarningsEnabled(False)
    bytes = fw.contents().toUtf8()
    QSimpleResource.setWarningsEnabled(warningsEnabled)

    QBuffer buffer(&bytes)
    buffer.open(QIODevice.ReadOnly)

    QWidget *widget = builder.load(&buffer, 0)
    if (not widget)   # Shouldn't happen
        *errorMessage = QCoreApplication.translate("QDesignerFormBuilder", "The preview failed to build.")
        return  0

    # Make sure palette is applied
     styleToUse = styleName.isEmpty() ? builder.deviceProfile().style() : styleName
    if not styleToUse.isEmpty():
        if WidgetFactory *wf = qobject_cast<qdesigner_internal.WidgetFactory *>(fw.core().widgetFactory()):
            if styleToUse != wf.styleName():
                WidgetFactory.applyStyleToTopLevel(wf.getStyle(styleToUse), widget)


    # Check for script errors
    *scriptErrors = builder.formScriptRunner().errors()
    if not scriptErrors.empty():
        *errorMessage = summarizeScriptErrors(*scriptErrors)
        delete widget
        return  0

    # Fake application style sheet by prepending. (If self doesn't work, by nesting
    # into parent widget).
    if not appStyleSheet.isEmpty():
        styleSheet = appStyleSheet
        styleSheet += QLatin1Char('\n')
        styleSheet +=  widget.styleSheet()
        widget.setStyleSheet(styleSheet)

    return widget


QWidget *QDesignerFormBuilder.createPreview( QDesignerFormWindowInterface *fw, &styleName)
    return createPreview(fw, styleName, QString())


QWidget *QDesignerFormBuilder.createPreview( QDesignerFormWindowInterface *fw,
         QString &styleName,
         QString &appStyleSheet,
         DeviceProfile &deviceProfile,
        QString *errorMessage)
    ScriptErrors scriptErrors
    return  createPreview(fw, styleName, appStyleSheet, deviceProfile, &scriptErrors, errorMessage)


QWidget *QDesignerFormBuilder.createPreview( QDesignerFormWindowInterface *fw,
         QString &styleName,
         QString &appStyleSheet,
        QString *errorMessage)
    ScriptErrors scriptErrors
    return  createPreview(fw, styleName, appStyleSheet, DeviceProfile(), &scriptErrors, errorMessage)


QWidget *QDesignerFormBuilder.createPreview( QDesignerFormWindowInterface *fw, &styleName, &appStyleSheet)
    ScriptErrors scriptErrors
    QString errorMessage
    QWidget *widget = createPreview(fw, styleName, appStyleSheet, DeviceProfile(), &scriptErrors, &errorMessage)
    if not widget:
        # Display Script errors or message box
        QWidget *dialogParent = fw.core().topLevel()
        if scriptErrors.empty():
            fw.core().dialogGui().message(dialogParent, QDesignerDialogGuiInterface.PreviewFailureMessage,
                                             QMessageBox.Warning, QCoreApplication.translate("QDesignerFormBuilder", "Designer"), errorMessage, QMessageBox.Ok)

        else:
            ScriptErrorDialog scriptErrorDialog(scriptErrors, dialogParent)
            scriptErrorDialog.exec()

        return 0

    return widget


def createPreviewPixmap(self, *fw, &styleName, &appStyleSheet):
    QWidget *widget = createPreview(fw, styleName, appStyleSheet)
    if not widget:
        return QPixmap()

     rc = QPixmap.grabWidget (widget)
    widget.deleteLater()
    return rc


} # namespace qdesigner_internal

QT_END_NAMESPACE
