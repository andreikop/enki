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
#include "QtDesignerManager.h"
#include "MkSDesignerIntegration.h"
#include "QDesignerWidgetBox.h"
#include "QDesignerActionEditor.h"
#include "QDesignerPropertyEditor.h"
#include "QDesignerObjectInspector.h"
#include "QDesignerSignalSlotEditor.h"
#include "QDesignerResourcesEditor.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <workspace/pWorkspace.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <widgets/pStylesToolButton.h>
#include <widgets/pMenuBar.h>
#include <widgets/pDockToolBar.h>

#include <QPluginLoader>

#include <QDesignerComponents>
#include <QDesignerFormEditorInterface>
#include <QDesignerFormWindowInterface>
#include <QDesignerFormWindowManagerInterface>
#include <QDesignerFormEditorPluginInterface>
#include <QDesignerObjectInspectorInterface>
#include <QDesignerPropertyEditorInterface>
#include <QDesignerActionEditorInterface>
#include <QDesignerFormWindowCursorInterface>
#include <QDesignerPropertySheetExtension>
#include <QExtensionManager>

#include "pluginmanager_p.h"
#if QT_VERSION >= 0x040500
#include <previewmanager_p.h>
#else
#include "LegacyDesigner.h"
#endif

QtDesignerManager::QtDesignerManager( QObject* parent )
    : QObject( parent )
{
    // init designer core
    QDesignerComponents::initializeResources();
    mCore = QDesignerComponents::createFormEditor( MonkeyCore::workspace() );
    
    // initialize plugins
    QDesignerComponents::initializePlugins( mCore );
    
    // init task menus
    (void) QDesignerComponents::createTaskMenu( mCore, MonkeyCore::workspace() );
    
    // init actions
    QDesignerFormWindowManagerInterface* fwm = mCore->formWindowManager();
    
    // create edit widget mode action
    aEditWidgets = new QAction( tr( "Edit Widgets" ), this );
    aEditWidgets->setIcon( QIcon( mCore->resourceLocation().append( "/widgettool.png" ) ) );
    aEditWidgets->setCheckable( true );
    aEditWidgets->setChecked( true );
    
    // preview action
    pStylesToolButton* stb = new pStylesToolButton( tr( "Preview in %1..." ) );
    stb->setCheckableActions( false );
    stb->defaultAction()->setShortcut( tr( "Ctrl+R" ) );
    stb->setIcon( QIcon( ":/icons/preview.png" ) );
    aPreview = new QWidgetAction( this );
    aPreview->setDefaultWidget( stb );
    
    // action group for modes
    aModes = new QActionGroup( MonkeyCore::workspace() );
    aModes->setExclusive( true );
    aModes->addAction( aEditWidgets );
    
    // simplify gridlayout
    fwm->actionSimplifyLayout()->setIcon( fwm->actionGridLayout()->icon() );
    
    // edit actions
    fwm->actionUndo()->setIcon( QIcon( ":/icons/undo.png" ) );
    fwm->actionUndo()->setShortcut( MonkeyCore::menuBar()->action( "mEdit/aUndo" )->shortcut() );
    fwm->actionRedo()->setIcon( QIcon( ":/icons/redo.png" ) );
    fwm->actionRedo()->setShortcut( MonkeyCore::menuBar()->action( "mEdit/aRedo" )->shortcut() );
    fwm->actionDelete()->setIcon( QIcon( ":/icons/delete.png" ) );
    fwm->actionSelectAll()->setIcon( QIcon( ":/icons/selectall.png" ) );
    fwm->actionDelete()->setShortcut( tr( "Del" ) );
    
    // initialize designer plugins
    foreach ( QObject* o, QPluginLoader::staticInstances() << mCore->pluginManager()->instances() )
    {
        if (  QDesignerFormEditorPluginInterface* fep = qobject_cast<QDesignerFormEditorPluginInterface*>( o ) )
        {
            // initialize plugin if needed
            if ( !fep->isInitialized() )
                fep->initialize( mCore );
            
            // set action chackable
            fep->action()->setCheckable( true );
            
            // add action mode to group
            aModes->addAction( fep->action() );
        }
    }
    
    // create designer docks
    pWidgetBox = new QDesignerWidgetBox( mCore );
    pWidgetBox->setVisible( false );
    MonkeyCore::mainWindow()->dockToolBar( Qt::LeftToolBarArea )->addDock( pWidgetBox, pWidgetBox->windowTitle(), pWidgetBox->windowIcon() );
    
    pObjectInspector = new QDesignerObjectInspector( mCore );
    pObjectInspector->setVisible( false );
    MonkeyCore::mainWindow()->dockToolBar( Qt::RightToolBarArea )->addDock( pObjectInspector, pObjectInspector->windowTitle(), pObjectInspector->windowIcon() );
    
    pPropertyEditor = new QDesignerPropertyEditor( mCore );
    pPropertyEditor->setVisible( false );
    MonkeyCore::mainWindow()->dockToolBar( Qt::RightToolBarArea )->addDock( pPropertyEditor, pPropertyEditor->windowTitle(), pPropertyEditor->windowIcon() );
    
    pActionEditor = new QDesignerActionEditor( mCore );
    pActionEditor->setVisible( false );
    MonkeyCore::mainWindow()->dockToolBar( Qt::BottomToolBarArea )->addDock( pActionEditor, pActionEditor->windowTitle(), pActionEditor->windowIcon() );
    
    pSignalSlotEditor = new QDesignerSignalSlotEditor( mCore );
    pSignalSlotEditor->setVisible( false );
    MonkeyCore::mainWindow()->dockToolBar( Qt::BottomToolBarArea )->addDock( pSignalSlotEditor, pSignalSlotEditor->windowTitle(), pSignalSlotEditor->windowIcon() );
    
    pResourcesEditor = new QDesignerResourcesEditor( mCore );
    pResourcesEditor->setVisible( false );
    MonkeyCore::mainWindow()->dockToolBar( Qt::BottomToolBarArea )->addDock( pResourcesEditor, pResourcesEditor->windowTitle(), pResourcesEditor->windowIcon() );
    
    // perform integration
    mIntegration = new MkSDesignerIntegration( mCore, MonkeyCore::mainWindow() );
    mCore->setTopLevel( MonkeyCore::mainWindow() );
    
#if QT_VERSION >= 0x040500
    // create previewver
    mPreviewer = new qdesigner_internal::PreviewManager( qdesigner_internal::PreviewManager::SingleFormNonModalPreview, this );
#endif

    setToolBarsIconSize( QSize( 16, 16 ) );
    updateMacAttributes();
    
    // connections
    connect( aEditWidgets, SIGNAL( triggered() ), this, SLOT( editWidgets() ) );
    connect( stb, SIGNAL( styleSelected( const QString& ) ), this, SLOT( previewCurrentForm( const QString& ) ) );
}

QtDesignerManager::~QtDesignerManager()
{
    delete pWidgetBox;
    delete pActionEditor;
    delete pPropertyEditor;
    delete pObjectInspector;
    delete pSignalSlotEditor;
    delete pResourcesEditor;
}

QDesignerFormEditorInterface* QtDesignerManager::core()
{
    return mCore;
}

QDesignerFormWindowInterface* QtDesignerManager::createNewForm( QWidget* parent )
{
    QDesignerFormWindowInterface* form = mCore->formWindowManager()->createFormWindow( parent );
    form->setFeatures( QDesignerFormWindowInterface::DefaultFeature );
    return form;
}

void QtDesignerManager::addFormWindow( QDesignerFormWindowInterface* form )
{
    mCore->formWindowManager()->addFormWindow( form );
}

void QtDesignerManager::setActiveFormWindow( QDesignerFormWindowInterface* form )
{
    // update active form
    if ( form && mCore->formWindowManager()->activeFormWindow() != form )
    {
        mCore->formWindowManager()->setActiveFormWindow( form );
    }
    
    // update preview actino state
    aPreview->setEnabled( form );
}

QWidget* QtDesignerManager::previewWidget( QDesignerFormWindowInterface* form, const QString& style )
{
    QWidget* widget = 0;
    QString error;
    
    if ( form )
    {
#if QT_VERSION >= 0x040500
        widget = mPreviewer->showPreview( form, style, &error );
#else
        widget = LegacyDesigner::showPreview( form, style, &error );
#endif
        
        if ( !widget )
        {
            MonkeyCore::messageManager()->appendMessage( tr( "Can't preview form '%1': %2" ).arg( form->fileName() ).arg( error ) );
        }
    }
    
    return widget;
}

QPixmap QtDesignerManager::previewPixmap( QDesignerFormWindowInterface* form, const QString& style )
{
    QPixmap pixmap;
    QString error;
    
    if ( form )
    {
#if QT_VERSION >= 0x040500
        pixmap = mPreviewer->createPreviewPixmap( form, style, &error );
#else
        pixmap = LegacyDesigner::createPreviewPixmap( form, style, &error );
#endif
        
        if ( pixmap.isNull() )
        {
            MonkeyCore::messageManager()->appendMessage( tr( "Can't preview form pixmap '%1': %2" ).arg( form->fileName() ).arg( error ) );
        }
    }
    
    return pixmap;
}

void QtDesignerManager::setToolBarsIconSize( const QSize& size )
{
    QList<QWidget*> widgets;
    widgets << pWidgetBox << pActionEditor << pPropertyEditor << pObjectInspector << pSignalSlotEditor << pResourcesEditor;
    
    foreach ( QWidget* widget, widgets )
    {
        foreach ( QToolBar* tb, widget->findChildren<QToolBar*>() )
        {
            tb->setIconSize( size );
        }
    }
}

void QtDesignerManager::updateMacAttributes()
{
    QList<QWidget*> widgets;
    widgets << pWidgetBox << pActionEditor << pPropertyEditor << pObjectInspector << pSignalSlotEditor << pResourcesEditor;
    
    foreach ( QWidget* widget, widgets )
    {
        foreach ( QWidget* child, widget->findChildren<QWidget*>() )
        {
            child->setAttribute( Qt::WA_MacShowFocusRect, false );
            child->setAttribute( Qt::WA_MacSmallSize );
        }
    }
}

void QtDesignerManager::editWidgets()
{
    // set edit mode for all forms
    QDesignerFormWindowManagerInterface* fwm = mCore->formWindowManager();
    
    for ( int i = 0; i < fwm->formWindowCount(); i++ )
    {
        fwm->formWindow( i )->editWidgets();
    }
}

void QtDesignerManager::previewCurrentForm( const QString& style )
{
    previewWidget( mCore->formWindowManager()->activeFormWindow(), style );
}
