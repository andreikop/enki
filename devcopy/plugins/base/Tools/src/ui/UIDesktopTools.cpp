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
#include "UIDesktopTools.h"
#include "ToolsManager.h"
#include "DesktopApplications.h"

#include <pMonkeyStudio.h>
#include <coremanager/MonkeyCore.h>
#include <settingsmanager/Settings.h>

#include <QTimer>
#include <QCloseEvent>
#include <QMessageBox>
#include <QPushButton>
#include <QDebug>

Q_DECLARE_METATYPE( QTreeWidgetItem* )

UIDesktopTools.UIDesktopTools( ToolsManager* manager, parent )
        : QDialog( parent )
    Q_ASSERT( manager )
    mToolsManager = manager
    mStartMenu = DesktopApplications( self )
    mShown = False

    setupUi( self )
    setAttribute( Qt.WA_DeleteOnClose )
    pbLoading.setVisible( False )

    if  not mStartMenu.categoriesAvailable() :
        lCategoriesFilters.hide()
        leCategoriesFilters.hide()


    # connection
    twLeft.itemDoubleClicked.connect(self.on_tbRight_clicked)
    lwRight.itemDoubleClicked.connect(self.on_tbLeft_clicked)


UIDesktopTools.~UIDesktopTools()


def showEvent(self, event ):
    QDialog.showEvent( event )

    if  not mShown :
        mShown = True
        QTimer.singleShot( 100, self, SLOT( scanApplications() ) )



def closeEvent(self, event ):
    if  isWindowModified(:
            and QMessageBox.question( self, QString.null, tr( "You're about to discard all changes. Are you sure ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.No )
        event.ignore()
        return


    QDialog.closeEvent( event )


def applyFilters(self):
     QList<QTreeWidgetItem*> items = twLeft.findItems( "*", Qt.MatchWildcard | Qt.MatchRecursive )
     nameFilter = leNameFilter.text()
     categoriesFilter = leCategoriesFilters.text().split( ";", QString.SkipEmptyParts )

    for item in items:
        da = item.data( 0, Qt.UserRole ).value<DesktopApplication*>()

        if  not da or mApplications.contains( da.parent.applications.key( *da ) ) :
            continue


        # validate name filter
         nameFilterMatch = not nameFilter.isEmpty() and item.text( 0 ).contains( nameFilter, Qt.CaseInsensitive )
        visible = nameFilter.isEmpty() or nameFilterMatch

        # validate categories filter
        if  visible :
            categoriesFilterMatch = False

            for filter in categoriesFilter:
                if  da.categories.contains( filter, Qt.CaseInsensitive ) :
                    categoriesFilterMatch = True
                    break



            visible = categoriesFilter.isEmpty() or categoriesFilterMatch


        # set item visibility
        item.setHidden( not visible )



def populateTree(self, _item, folder ):
    Q_ASSERT( folder )

    # Folders
    for folderName in folder.folders.keys():
        df = &folder.folders[ folderName ]
        item = 0

        if  _item :
            item = QTreeWidgetItem( _item )

        else:
            item = QTreeWidgetItem( twLeft )


        item.setText( 0, folderName )
        item.setIcon( 0, ToolsManager.icon( df.icon, df.path ) )
        item.setData( 0, Qt.UserRole, QVariant.fromValue( df ) )

        populateTree( item, df )


    # Applications
    for fileName in folder.applications.keys():
        da = &folder.applications[ fileName ]
        item = 0

        QApplication.processEvents( QEventLoop.ExcludeUserInputEvents )

        if  _item :
            item = QTreeWidgetItem( _item )

        else:
            item = QTreeWidgetItem( twLeft )


        item.setText( 0, da.name )
        item.setIcon( 0, ToolsManager.icon( da.icon, fileName ) )
        item.setToolTip( 0, QString( "<b>%1</b><br />%2<br /><i>%3</i>" )
                          .arg( da.genericName.isEmpty() ? da.name : da.genericName )
                          .arg( da.comment.isEmpty() ? tr( "No available comment" ) : da.comment )
                          .arg( da.categories.isEmpty() ? tr( "No available categories" ) : da.categories.join( ", " ).prepend( ' ' ).prepend( tr( "Categories:" ) ) )
                        )

        item.setData( 0, Qt.UserRole, QVariant.fromValue( da ) )

        pbLoading.setValue( pbLoading.value() +1 )



def scanApplications(self):
    # show progressbar
    pbLoading.setVisible( True )
    # set temp progressbar for loading application
    pbLoading.setRange( 0, 0 )
    # populate applications
    mStartMenu.scan()
    # set progressbar range
    pbLoading.setRange( 0, mStartMenu.applicationCount() )
    # clear tree
    twLeft.clear()
    # disable update
    twLeft.setUpdatesEnabled( False )
    # populate tree
    populateTree( 0, mStartMenu.startMenu() )
    # enable update
    twLeft.setUpdatesEnabled( True )
    # hide progressbar
    pbLoading.setVisible( False )

    # restore selected applications
    foreach (  ToolsManager.Tool& tool, mToolsManager.tools( ToolsManager.DesktopEntry ) )
        mApplications << tool.filePath


    foreach ( QTreeWidgetItem* item, twLeft.findItems( "*", Qt.MatchWildcard | Qt.MatchRecursive ) )
        da = item.data( 0, Qt.UserRole ).value<DesktopApplication*>()

        if  not da :
            continue


        if  mApplications.contains( da.parent.applications.key( *da ) ) :
            item.setSelected( True )



    # simulate click to add items to right
    tbRight.click()

    # modified state
    setWindowModified( False )


def on_leNameFilter_textChanged(self,   QString& '''text''' ):
    applyFilters()


def on_leCategoriesFilters_textChanged(self,   QString& '''text''' ):
    applyFilters()


def on_tbRight_clicked(self):
    for item in twLeft.selectedItems():
        da = item.data( 0, Qt.UserRole ).value<DesktopApplication*>()

        if  item.isHidden() or not da :
            continue


        it = QListWidgetItem( lwRight )
        it.setText( item.text( 0 ) )
        it.setIcon( item.icon( 0 ) )
        it.setToolTip( item.toolTip( 0 ) )
        it.setData( Qt.UserRole, QVariant.fromValue( da ) )
        it.setData( Qt.UserRole +1, QVariant.fromValue( item ) )
        item.setHidden( True )

        mApplications << da.parent.applications.key( *da )

        # modified state
        setWindowModified( True )



def on_tbLeft_clicked(self):
    for item in lwRight.selectedItems():
        da = item.data( Qt.UserRole ).value<DesktopApplication*>()
        it = item.data( Qt.UserRole +1 ).value<QTreeWidgetItem*>()

        if  it :
            mApplications.remove( da.parent.applications.key( *da ) )

            # modified state
            setWindowModified( True )


        delete item


    # revalidate the filters
    if  isWindowModified() :
        applyFilters()



def on_tbUp_clicked(self):
    if  lwRight.selectedItems().count() > 1 :
        QMessageBox.warning( QApplication.activeWindow(), QString.null, tr( "Only one item can be move up, select only one item." ) )
        return


    item = lwRight.selectedItems().value( 0 )

    if  not item or lwRight.row( item ) == 0 :
        return


     index = lwRight.row( item )
    item = lwRight.takeItem( index )
    lwRight.insertItem( index -1, item )
    lwRight.setCurrentRow( index -1 )

    # modified state
    setWindowModified( True )


def on_tbDown_clicked(self):
    if  lwRight.selectedItems().count() > 1 :
        QMessageBox.warning( QApplication.activeWindow(), QString.null, tr( "Only one item can be move down, select only one item." ) )
        return


    item = lwRight.selectedItems().value( 0 )

    if  not item or lwRight.row( item ) == lwRight.count() -1 :
        return


     index = lwRight.row( item )
    item = lwRight.takeItem( index )
    lwRight.insertItem( index +1, item )
    lwRight.setCurrentRow( index +1 )

    # modified state
    setWindowModified( True )


def accept(self):
    if  isWindowModified() :
        tools = mToolsManager.tools( ToolsManager.UserEntry )

        for ( i = 0; i < lwRight.count(); i++ )
            item = lwRight.item( i )
            da = item.data( Qt.UserRole ).value<DesktopApplication*>()
            ToolsManager.Tool tool

            tool.caption = item.text()
            tool.fileIcon = da.icon
            tool.filePath = da.parent.applications.key( *da )
            tool.workingPath = QString.null
            tool.desktopEntry = True
            tool.useConsoleManager = False

            tools << tool


        mToolsManager.mTools = tools
        mToolsManager.updateMenuActions()
        mToolsManager.writeTools( tools )


    # close dialog
    QDialog.accept()

