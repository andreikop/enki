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
#include "UIToolsEdit.h"
#include "ToolsManager.h"

#include <pMonkeyStudio.h>

#include <QMessageBox>
#include <QCloseEvent>
#include <QFileInfo>
#include <QUrl>
#include <QWhatsThis>

UIToolsEdit.UIToolsEdit( ToolsManager* manager, parent )
        : QDialog( parent )
    Q_ASSERT( manager )
    mToolsManager = manager

    # init dialog
    setupUi( self )
    setAttribute( Qt.WA_DeleteOnClose )

    # event filters
    leCaption.installEventFilter( self )
    tbFileIcon.installEventFilter( self )
    leFilePath.installEventFilter( self )
    leWorkingPath.installEventFilter( self )

    # create items
    foreach (  ToolsManager.Tool& tool, mToolsManager.tools( ToolsManager.UserEntry ) )
        # create item
        item = QListWidgetItem( ToolsManager.icon( tool.fileIcon ), tool.caption, lwTools )
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )


    # modified state
    setWindowModified( False )

    # connection
    dbbButtons.helpRequested.connect(self.helpRequested)


def closeEvent(self, event ):
    # ask user confirmation if we have pending modification
    if  isWindowModified(:
            and QMessageBox.question( QApplication.activeWindow(), QString.null, tr( "You're about to discard all changes. Are you sure ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.No )
        event.ignore()
        return


    QDialog.closeEvent( event )


def eventFilter(self, object, event ):
    # accept drag enter event
    if  event.type() == QEvent.DragEnter :
        event.accept()


    # got the event as drop event
    de = static_cast<QDropEvent*>( event )

    # if not a drop event or has urls, return
    if  event.type() != QEvent.Drop or not de.mimeData().hasUrls() :
        return QDialog.eventFilter( object, event )


    # if there is no current item selected, to create one
    item = lwTools.selectedItems().value( 0 )

    if  not item :
         button = QMessageBox.question( self, QString.null, tr( "There is no current tool, you want to add a one ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No )

        # filter the even to avoid default drop event
        if  button == QMessageBox.No :
            return True


        item = QListWidgetItem( tr( "new Tool" ), lwTools )


    # get link info
    QFileInfo fi( de.mimeData().urls().at( 0 ).toLocalFile() )

    # drag for tbFileIcon
    tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()

    if  tool.caption.isEmpty() :
        tool.caption = item.text()


    if  object == tbFileIcon :
        if  fi.isFile() :
            tool.fileIcon = fi.absoluteFilePath()


    # others
    else:
        if  fi.isFile() :
            tool.caption = fi.baseName()
            tool.filePath = fi.absoluteFilePath()
            tool.workingPath = fi.absolutePath()

        elif  fi.isDir() :
            tool.workingPath = fi.absoluteFilePath()



    # update item data
    item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
    updateGui( item, True )

    # modified state
    setWindowModified( True )

    # we finish
    return QDialog.eventFilter( object, event )


def updateGui(self, item, makeCurrent ):
     tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()

    item.setText( tool.caption )
    item.setIcon( ToolsManager.icon( tool.fileIcon ) )
    leCaption.setText( tool.caption )
    tbFileIcon.setIcon( item.icon() )
    leFilePath.setText( tool.filePath )
    leWorkingPath.setText( tool.workingPath )
    cbUseConsoleManager.setChecked( tool.useConsoleManager )

    if  makeCurrent :
        lwTools.clearSelection()
        lwTools.setCurrentItem( item )
        item.setSelected( True )



def on_lwTools_itemSelectionChanged(self):
    if  item = lwTools.selectedItems().value( 0 ) :
        updateGui( item )



def on_aNew_triggered(self):
    item = QListWidgetItem( tr( "new Tool" ), lwTools )
    tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
    tool.caption = item.text()
    item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
    updateGui( item, True )

    # modified state
    setWindowModified( True )


def on_aDelete_triggered(self):
    delete lwTools.selectedItems().value( 0 )

    if  lwTools.count() :
        updateGui( lwTools.item( 0 ), True )


    # modified state
    setWindowModified( True )


def on_aUp_triggered(self):
    item = lwTools.selectedItems().value( 0 )

    if  not item or lwTools.row( item ) == 0 :
        return


     row = lwTools.row( item )
    item = lwTools.takeItem( row )
    lwTools.insertItem( row -1, item )
    lwTools.setCurrentRow( row -1 )

    # modified state
    setWindowModified( True )


def on_aDown_triggered(self):
    item = lwTools.selectedItems().value( 0 )

    if  not item or lwTools.row( item ) == lwTools.count() -1 :
        return


     row = lwTools.row( item )
    item = lwTools.takeItem( row )
    lwTools.insertItem( row +1, item )
    lwTools.setCurrentRow( row +1 )

    # modified state
    setWindowModified( True )


def helpRequested(self):
    help = tr( "<b>Tools Editor</b> give you the possibility to use variables<br><br>"
                       "<b>$cpp$</b> : Current project path<br>"
                       "<b>$cp$</b> : Current project filepath<br>"
                       "<b>$cfp$</b> : Current tab path<br>"
                       "<b>$cf$</b> : Current tab filepath<br>"
                       "<b>$cip$</b> : Current item path<br>"
                       "<b>$ci$</b> : Current item filepath" )

    QWhatsThis.showText( mapToGlobal( rect().center() ), help )


def on_leCaption_editingFinished(self):
    if  item = lwTools.selectedItems().value( 0 ) :
        tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
        tool.caption = leCaption.text()
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
        updateGui( item )

        # modified state
        setWindowModified( True )



def on_tbFileIcon_clicked(self):
    if  item = lwTools.selectedItems().value( 0 ) :
        tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
         fn = pMonkeyStudio.getImageFileName( tr( "Choose an icon for self tool" ), tool.fileIcon, self )

        if  fn.isEmpty() :
            return


        tool.fileIcon = fn
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
        updateGui( item )

        # modified state
        setWindowModified( True )



def on_leFilePath_editingFinished(self):
    if  item = lwTools.selectedItems().value( 0 ) :
        tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
        tool.filePath = leFilePath.text()
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
        updateGui( item )

        # modified state
        setWindowModified( True )



def on_tbFilePath_clicked(self):
    if  item = lwTools.selectedItems().value( 0 ) :
        tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
         fn = pMonkeyStudio.getOpenFileName( tr( "Choose the file to execute for self tool" ), tool.filePath, QString.null, self )

        if  fn.isEmpty() :
            return


        tool.filePath = fn
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
        updateGui( item )
        leFilePath.setFocus()

        # modified state
        setWindowModified( True )



def on_tbUpdateWorkingPath_clicked(self):
    if  item = lwTools.selectedItems().value( 0 ) :
         QFileInfo fi( leFilePath.text() )

        if  fi.exists() and fi.absolutePath() != leWorkingPath.text() :
            tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
            tool.workingPath = fi.absolutePath()
            item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
            updateGui( item )
            leWorkingPath.setFocus()

            # modified state
            setWindowModified( True )




def on_leWorkingPath_editingFinished(self):
    if  item = lwTools.selectedItems().value( 0 ) :
        tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
        tool.workingPath = leWorkingPath.text()
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
        updateGui( item )

        # modified state
        setWindowModified( True )



def on_tbWorkingPath_clicked(self):
    if  item = lwTools.selectedItems().value( 0 ) :
        tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
         path = pMonkeyStudio.getExistingDirectory( tr( "Choose the working path for self tool" ), tool.workingPath, self )

        if  path.isEmpty() :
            return


        tool.workingPath = path
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
        updateGui( item )
        leWorkingPath.setFocus()

        # modified state
        setWindowModified( True )



def on_cbUseConsoleManager_clicked(self, clicked ):
    if  item = lwTools.selectedItems().value( 0 ) :
        tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
        tool.useConsoleManager = clicked
        item.setData( Qt.UserRole, QVariant.fromValue( tool ) )
        updateGui( item )

        # modified state
        setWindowModified( True )



def accept(self):
    if  isWindowModified() :
        tools = mToolsManager.tools( ToolsManager.DesktopEntry )

        for ( i = 0; i < lwTools.count(); i++ )
            item = lwTools.item( i )
             tool = item.data( Qt.UserRole ).value<ToolsManager.Tool>()
            tools << tool


        mToolsManager.mTools = tools
        mToolsManager.updateMenuActions()
        mToolsManager.writeTools( tools )


    # close dialog
    QDialog.accept()

