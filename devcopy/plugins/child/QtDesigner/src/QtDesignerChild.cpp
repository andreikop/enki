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
#include "QtDesignerChild.h"
#include "QtDesignerManager.h"

#include "widgethost.h"

#include <objects/pIconManager.h>
#include <coremanager/MonkeyCore.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <objects/pStylesActionGroup.h>

#include <QDesignerFormWindowManagerInterface>
#include <QDesignerFormWindowInterface>
#include <QDesignerFormEditorInterface>
#include <QDesignerPropertyEditorInterface>
#include <QDesignerPropertySheetExtension>
#include <QExtensionManager>

#include <QPainter>
#include <QPrintDialog>
#include <QInputDialog>
#include <QStyleFactory>
#include <QPrinter>

QtDesignerChild.QtDesignerChild( QtDesignerManager* manager )
        : pAbstractChild()
    Q_ASSERT( manager )
    mDesignerManager = manager

    # set up ui
    setWindowIcon( pIconManager.icon( "designer.png", ":/icons" ) )

    # create form host widget
    form = mDesignerManager.createNewForm( self )
    mDesignerManager.addFormWindow( form )

    mHostWidget = SharedTools.WidgetHost( self, form )
    mHostWidget.setFrameStyle( QFrame.NoFrame | QFrame.Plain )
    mHostWidget.setFocusProxy( form )

    setWidget( mHostWidget )

    connect( mHostWidget.formWindow(), SIGNAL( changed() ), self, SLOT( formChanged() ) )
    connect( mHostWidget.formWindow(), SIGNAL( selectionChanged() ), self, SLOT( formSelectionChanged() ) )
    connect( mHostWidget.formWindow(), SIGNAL( geometryChanged() ), self, SLOT( formGeometryChanged() ) )
    connect( mHostWidget.formWindow(), SIGNAL( mainContainerChanged( QWidget* ) ), self, SLOT( formMainContainerChanged( QWidget* ) ) )


def showEvent(self, event ):
    pAbstractChild.showEvent( event )

    mDesignerManager.setActiveFormWindow( mHostWidget.formWindow() )


def formChanged(self):
    setWindowModified( mHostWidget.formWindow().isDirty() )
    modifiedChanged.emit( mHostWidget.formWindow().isDirty() )
    contentChanged.emit()


def formSelectionChanged(self):
    mHostWidget.updateFormWindowSelectionHandles( True )


def formGeometryChanged(self):
    # set modified state
    loading = property( "loadingFile" ).toBool()
    modified = not loading

    # update property
    sheet = qt_extension<QDesignerPropertySheetExtension*>( mDesignerManager.core().extensionManager(), mHostWidget.formWindow() )
    geo = sheet.property( sheet.indexOf( "geometry" ) ).toRect()
    geo.moveTopLeft( QPoint( 0, 0 ) )

    # update property
    mDesignerManager.core().propertyEditor().setPropertyValue( "geometry", geo, modified )

    # update state
    mHostWidget.formWindow().setDirty( modified )
    setWindowModified( modified )
    setProperty( "loadingFile", False )

    # modified.emit state
    modifiedChanged.emit( modified )
    contentChanged.emit()


def formMainContainerChanged(self, widget ):
    Q_UNUSED( widget )
    setProperty( "loadingFile", True )


def openFile(self, fileName, codec ):
    Q_UNUSED( codec )

    if  QFile.exists( fileName ) :
        # set content
        QFile file( fileName )

        if  not file.open( QIODevice.ReadOnly ) :
            return False


        setFilePath( fileName )
        mHostWidget.formWindow().setFileName( fileName )
        mHostWidget.formWindow().setContents( &file )

        if  mHostWidget.formWindow().mainContainer() :
            # set clean
            mHostWidget.formWindow().setDirty( False )

            setWindowModified( False )

            fileOpened.emit()
            return True

        else:
            setFilePath( QString.null )
            mHostWidget.formWindow().setFileName( QString.null )



    return False


def closeFile(self):
    setFilePath( QString.null )
    fileClosed.emit()


def reload(self):
    openFile( mHostWidget.formWindow().fileName(), QString.null )

    fileReloaded.emit()


def fileBuffer(self):
    if  mHostWidget.formWindow().mainContainer() :
        return mHostWidget.formWindow().contents()


    return QString.null


def context(self):
    return PLUGIN_NAME


def initializeContext(self, tb ):
    fwm = mDesignerManager.core().formWindowManager()

    # add actions to toolbar
    tb.addAction( fwm.actionUndo() )
    tb.addAction( fwm.actionRedo() )
    tb.addAction( fwm.actionCut() )
    tb.addAction( fwm.actionCopy() )
    tb.addAction( fwm.actionPaste() )
    tb.addAction( fwm.actionLower() )
    tb.addAction( fwm.actionRaise() )
    tb.addAction( fwm.actionDelete() )
    tb.addAction( fwm.actionSelectAll() )
    tb.addSeparator()

    # tools
    tb.addActions( mDesignerManager.modesActions() )
    tb.addSeparator()

    # form
    tb.addAction( fwm.actionHorizontalLayout() )
    tb.addAction( fwm.actionVerticalLayout() )
    tb.addAction( fwm.actionSplitHorizontal() )
    tb.addAction( fwm.actionSplitVertical() )
    tb.addAction( fwm.actionGridLayout() )
    tb.addAction( fwm.actionFormLayout() )
    tb.addAction( fwm.actionSimplifyLayout() )
    tb.addAction( fwm.actionBreakLayout() )
    tb.addAction( fwm.actionAdjustSize() )

    # preview
    tb.addSeparator()
    tb.addAction( mDesignerManager.previewFormAction() )


def cursorPosition(self):
    return QPoint( -1, -1 )


def isModified(self):
    return mHostWidget.formWindow().isDirty()


def isUndoAvailable(self):
    return False


def isRedoAvailable(self):
    return False


def isPasteAvailable(self):
    return False


def isCopyAvailable(self):
    return False



def saveFile(self):
    # cancel if not modified
    if  not mHostWidget.formWindow().isDirty() :
        return


    # write file
    QFile file( mHostWidget.formWindow().fileName() )

    if  file.open( QIODevice.WriteOnly ) :
        file.resize( 0 )
        file.write( mHostWidget.formWindow().contents().toUtf8() )
        file.close()

        mHostWidget.formWindow().setDirty( False )
        setWindowModified( False )

        modifiedChanged.emit( False )

    else:
        MonkeyCore.messageManager().appendMessage( tr( "An error occurs when saving :\n%1" ).arg( mHostWidget.formWindow().fileName() ) )


    return


def printFormHelper(self, form, quick ):
    bool ok
     styles = QStyleFactory.keys()
     id = styles.indexOf( pStylesActionGroup.systemStyle() )
    style = QInputDialog.getItem( self, tr( "Choose a style..." ), tr( "Choose a style to render the form:" ), styles, id, False, &ok )

    if  not ok :
        return


    # get printer
    QPrinter printer

    # if quick print
    if  quick :
        # check if default printer is set
        if  printer.printerName().isEmpty() :
            MonkeyCore.messageManager().appendMessage( tr( "There is no default printer, set one before trying quick print" ) )
            return


        # print and return
        QPainter painter( &printer )
        painter.drawPixmap( 0, 0, mDesignerManager.previewPixmap( form, style ) )

    else:
        # printer dialog
        QPrintDialog printDialog( &printer )

        # if ok
        if  printDialog.exec() :
            # print and return
            QPainter painter( &printer )
            painter.drawPixmap( 0, 0, mDesignerManager.previewPixmap( form, style ) )




def printFile(self):
    printFormHelper( mHostWidget.formWindow(), False )


def quickPrintFile(self):
    printFormHelper( mHostWidget.formWindow(), True )


def undo(self):
def redo(self):
def cut(self):
def copy(self):
def paste(self):
def searchReplace(self):
def goTo(self):
def goTo(self, pos, selectionLength ):
    Q_UNUSED( pos )
    Q_UNUSED( selectionLength )


def backupFileAs(self, fileName ):
    QFile file( fileName )

    if  file.open( QIODevice.WriteOnly ) :
        file.resize( 0 )
        file.write( mHostWidget.formWindow().contents().toUtf8() )
        file.close()

    else:
        MonkeyCore.messageManager().appendMessage( tr( "An error occurs when backuping: %1" ).arg( fileName ) )



def isSearchReplaceAvailable(self):
    return False


def isGoToAvailable(self):
    return False


def isPrintAvailable(self):
    return True

