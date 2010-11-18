'''***************************************************************************
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
***************************************************************************'''
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
#else:
#include "LegacyDesigner.h"
#endif

QtDesignerManager.QtDesignerManager( QObject* parent )
    : QObject( parent )
    # init designer core
    QDesignerComponents.initializeResources()
    mCore = QDesignerComponents.createFormEditor( MonkeyCore.workspace() )
    
    # initialize plugins
    QDesignerComponents.initializePlugins( mCore )
    
    # init task menus
    (void) QDesignerComponents.createTaskMenu( mCore, MonkeyCore.workspace() )
    
    # init actions
    fwm = mCore.formWindowManager()
    
    # create edit widget mode action
    aEditWidgets = QAction( tr( "Edit Widgets" ), self )
    aEditWidgets.setIcon( QIcon( mCore.resourceLocation().append( "/widgettool.png" ) ) )
    aEditWidgets.setCheckable( True )
    aEditWidgets.setChecked( True )
    
    # preview action
    stb = pStylesToolButton( tr( "Preview in %1..." ) )
    stb.setCheckableActions( False )
    stb.defaultAction().setShortcut( tr( "Ctrl+R" ) )
    stb.setIcon( QIcon( ":/icons/preview.png" ) )
    aPreview = QWidgetAction( self )
    aPreview.setDefaultWidget( stb )
    
    # action group for modes
    aModes = QActionGroup( MonkeyCore.workspace() )
    aModes.setExclusive( True )
    aModes.addAction( aEditWidgets )
    
    # simplify gridlayout
    fwm.actionSimplifyLayout().setIcon( fwm.actionGridLayout().icon() )
    
    # edit actions
    fwm.actionUndo().setIcon( QIcon( ":/icons/undo.png" ) )
    fwm.actionUndo().setShortcut( MonkeyCore.menuBar().action( "mEdit/aUndo" ).shortcut() )
    fwm.actionRedo().setIcon( QIcon( ":/icons/redo.png" ) )
    fwm.actionRedo().setShortcut( MonkeyCore.menuBar().action( "mEdit/aRedo" ).shortcut() )
    fwm.actionDelete().setIcon( QIcon( ":/icons/delete.png" ) )
    fwm.actionSelectAll().setIcon( QIcon( ":/icons/selectall.png" ) )
    fwm.actionDelete().setShortcut( tr( "Del" ) )
    
    # initialize designer plugins
    for o in QPluginLoader.staticInstances(: << mCore.pluginManager().instances() )
        if   fep = qobject_cast<QDesignerFormEditorPluginInterface*>( o ) :
            # initialize plugin if needed
            if  not fep.isInitialized() :
                fep.initialize( mCore )
            
            # set action chackable
            fep.action().setCheckable( True )
            
            # add action mode to group
            aModes.addAction( fep.action() )


    
    # create designer docks
    pWidgetBox = QDesignerWidgetBox( mCore )
    pWidgetBox.setVisible( False )
    MonkeyCore.mainWindow().dockToolBar( Qt.LeftToolBarArea ).addDock( pWidgetBox, pWidgetBox.windowTitle(), pWidgetBox.windowIcon() )
    
    pObjectInspector = QDesignerObjectInspector( mCore )
    pObjectInspector.setVisible( False )
    MonkeyCore.mainWindow().dockToolBar( Qt.RightToolBarArea ).addDock( pObjectInspector, pObjectInspector.windowTitle(), pObjectInspector.windowIcon() )
    
    pPropertyEditor = QDesignerPropertyEditor( mCore )
    pPropertyEditor.setVisible( False )
    MonkeyCore.mainWindow().dockToolBar( Qt.RightToolBarArea ).addDock( pPropertyEditor, pPropertyEditor.windowTitle(), pPropertyEditor.windowIcon() )
    
    pActionEditor = QDesignerActionEditor( mCore )
    pActionEditor.setVisible( False )
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( pActionEditor, pActionEditor.windowTitle(), pActionEditor.windowIcon() )
    
    pSignalSlotEditor = QDesignerSignalSlotEditor( mCore )
    pSignalSlotEditor.setVisible( False )
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( pSignalSlotEditor, pSignalSlotEditor.windowTitle(), pSignalSlotEditor.windowIcon() )
    
    pResourcesEditor = QDesignerResourcesEditor( mCore )
    pResourcesEditor.setVisible( False )
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( pResourcesEditor, pResourcesEditor.windowTitle(), pResourcesEditor.windowIcon() )
    
    # perform integration
    mIntegration = MkSDesignerIntegration( mCore, MonkeyCore.mainWindow() )
    mCore.setTopLevel( MonkeyCore.mainWindow() )
    
#if QT_VERSION >= 0x040500
    # create previewver
    mPreviewer = qdesigner_internal.PreviewManager( qdesigner_internal.PreviewManager.SingleFormNonModalPreview, self )
#endif

    setToolBarsIconSize( QSize( 16, 16 ) )
    updateMacAttributes()
    
    # connections
    aEditWidgets.triggered.connect(self.editWidgets)
    stb.styleSelected.connect(self.previewCurrentForm)


QtDesignerManager.~QtDesignerManager()
    delete pWidgetBox
    delete pActionEditor
    delete pPropertyEditor
    delete pObjectInspector
    delete pSignalSlotEditor
    delete pResourcesEditor


def core(self):
    return mCore


def createNewForm(self, parent ):
    form = mCore.formWindowManager().createFormWindow( parent )
    form.setFeatures( QDesignerFormWindowInterface.DefaultFeature )
    return form


def addFormWindow(self, form ):
    mCore.formWindowManager().addFormWindow( form )


def setActiveFormWindow(self, form ):
    # update active form
    if  form and mCore.formWindowManager().activeFormWindow() != form :
        mCore.formWindowManager().setActiveFormWindow( form )

    
    # update preview actino state
    aPreview.setEnabled( form )


def previewWidget(self, form, style ):
    widget = 0
    QString error
    
    if  form :
#if QT_VERSION >= 0x040500
        widget = mPreviewer.showPreview( form, style, &error )
#else:
        widget = LegacyDesigner.showPreview( form, style, &error )
#endif
        
        if  not widget :
            MonkeyCore.messageManager().appendMessage( tr( "Can't preview form '%1': %2" ).arg( form.fileName() ).arg( error ) )


    
    return widget


def previewPixmap(self, form, style ):
    QPixmap pixmap
    QString error
    
    if  form :
#if QT_VERSION >= 0x040500
        pixmap = mPreviewer.createPreviewPixmap( form, style, &error )
#else:
        pixmap = LegacyDesigner.createPreviewPixmap( form, style, &error )
#endif
        
        if  pixmap.isNull() :
            MonkeyCore.messageManager().appendMessage( tr( "Can't preview form pixmap '%1': %2" ).arg( form.fileName() ).arg( error ) )


    
    return pixmap


def setToolBarsIconSize(self, size ):
    QList<QWidget*> widgets
    widgets << pWidgetBox << pActionEditor << pPropertyEditor << pObjectInspector << pSignalSlotEditor << pResourcesEditor
    
    for widget in widgets:
        foreach ( QToolBar* tb, widget.findChildren<QToolBar*>() )
            tb.setIconSize( size )




def updateMacAttributes(self):
    QList<QWidget*> widgets
    widgets << pWidgetBox << pActionEditor << pPropertyEditor << pObjectInspector << pSignalSlotEditor << pResourcesEditor
    
    for widget in widgets:
        foreach ( QWidget* child, widget.findChildren<QWidget*>() )
            child.setAttribute( Qt.WA_MacShowFocusRect, False )
            child.setAttribute( Qt.WA_MacSmallSize )




def editWidgets(self):
    # set edit mode for all forms
    fwm = mCore.formWindowManager()
    
    for ( i = 0; i < fwm.formWindowCount(); i++ )
        fwm.formWindow( i ).editWidgets()



def previewCurrentForm(self, style ):
    previewWidget( mCore.formWindowManager().activeFormWindow(), style )

