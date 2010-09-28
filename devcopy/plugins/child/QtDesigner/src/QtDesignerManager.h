/****************************************************************************
    Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
****************************************************************************/
#ifndef QTDESIGNERMANAGER_H
#define QTDESIGNERMANAGER_H

#include <QObject>
#include <QActionGroup>
#include <QWidgetAction>

namespace qdesigner_internal {
    class QDesignerIntegration;
#if QT_VERSION >= 0x040500
    class PreviewManager;
#endif
};

class QDesignerFormEditorInterface;
class QDesignerFormWindowInterface;
class QDesignerWidgetBox;
class QDesignerActionEditor;
class QDesignerPropertyEditor;
class QDesignerObjectInspector;
class QDesignerSignalSlotEditor;
class QDesignerResourcesEditor;

class QtDesignerManager : public QObject
{
    Q_OBJECT

public:
    QtDesignerManager( QObject* parent = 0 );
    virtual ~QtDesignerManager();

    QDesignerFormEditorInterface* core();
    inline qdesigner_internal::QDesignerIntegration* integration() const { return mIntegration; }
    inline QAction* editWidgetsAction() const { return aEditWidgets; }
    inline QWidgetAction* previewFormAction() const { return aPreview; }
    inline QList<QAction*> modesActions() const { return aModes->actions(); }

    QDesignerFormWindowInterface* createNewForm( QWidget* parent = 0 );

    void addFormWindow( QDesignerFormWindowInterface* form );
    void setActiveFormWindow( QDesignerFormWindowInterface* form );

    QWidget* previewWidget( QDesignerFormWindowInterface* form, const QString& style = QString::null );
    QPixmap previewPixmap( QDesignerFormWindowInterface* form, const QString& style = QString::null );

protected:
    QDesignerFormEditorInterface* mCore;
    qdesigner_internal::QDesignerIntegration* mIntegration;
#if QT_VERSION >= 0x040500
    qdesigner_internal::PreviewManager* mPreviewer;
#endif

    QActionGroup* aModes;
    QWidgetAction* aPreview;
    QAction* aEditWidgets;

    QDesignerWidgetBox* pWidgetBox;
    QDesignerActionEditor* pActionEditor;
    QDesignerPropertyEditor* pPropertyEditor;
    QDesignerObjectInspector* pObjectInspector;
    QDesignerSignalSlotEditor* pSignalSlotEditor;
    QDesignerResourcesEditor* pResourcesEditor;

    void setToolBarsIconSize( const QSize& size );
    void updateMacAttributes();

protected slots:
    void editWidgets();
    void previewCurrentForm( const QString& style = QString::null );
};

#endif // QTDESIGNERMANAGER_H
