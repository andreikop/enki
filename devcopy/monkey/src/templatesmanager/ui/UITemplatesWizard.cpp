'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UITemplatesWizard.cpp
** Date      : 2008-01-14T00:37:11
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
**
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
**
***************************************************************************'''
#include "UITemplatesWizard.h"
#include "workspace/pFileManager.h"
#include "pMonkeyStudio.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"
#include "xupmanager/core/XUPProjectModelProxy.h"
#include "xupmanager/core/XUPProjectModel.h"
#include "xupmanager/core/XUPItem.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "xupmanager/gui/XUPProjectManager.h"
#include "variablesmanager/VariablesManager.h"

#include <QDir>
#include <QMessageBox>

UITemplatesWizard.UITemplatesWizard( QWidget* parent )
    : QDialog( parent )
    # init dialog
    setupUi( self )
    saWidgets.setWidgetResizable( True )
    
    # create scrollarea widget
    cw = QWidget
    gridLayout = QGridLayout( cw )
    gridLayout.setMargin( 5 )
    gridLayout.setSpacing( 3 )
    saWidgets.setWidget( cw )
    
    # get templates
    mTemplates = pTemplatesManager.instance().getTemplates()
    
    # set default language/type
    cbLanguages.addItem( tr( "All" ), "All" )
    cbTypes.addItem( tr( "All" ), "All" )
    
    cbCodec.addItems( pMonkeyStudio.availableTextCodecs() )
    
    # languages/types
    for tp in mTemplates:
        if  cbLanguages.findData( tp.Language, Qt.UserRole, Qt.MatchFixedString ) == -1 :
            cbLanguages.addItem( tr( tp.Language.toLocal8Bit().constData() ), tp.Language )
        if  cbTypes.findData( tp.Type, Qt.UserRole, Qt.MatchFixedString ) == -1 :
            cbTypes.addItem( tr( tp.Type.toLocal8Bit().constData() ), tp.Type )

    
    # restore infos
    s = MonkeyCore.settings()
    cbLanguages.setCurrentIndex( cbLanguages.findText( s.value( "Recents/FileWizard/Language", "C++" ).toString() ) )
    cbExpert.setChecked( s.value( "Recents/FileWizard/Expert", False ).toBool() )
    leDestination.setText( s.value( "Recents/FileWizard/Destination", QDir.currentPath() ).toString() )
    cbOpen.setChecked( s.value( "Recents/FileWizard/Open", True ).toBool() )
    cbCodec.setCurrentIndex( cbCodec.findText( pMonkeyStudio.defaultCodec() ) )

    # assign projects combobox
    mModel = MonkeyCore.projectsManager().currentProjectModel()
    mProxy = XUPProjectModelProxy( self, cbExpert.isChecked() )
    project = MonkeyCore.projectsManager().currentProject()
    index = project ? project.index() : QModelIndex()
    
    mProxy.setSourceModel( mModel )
    cbProjects.setModel( mProxy )
    cbProjects.setCurrentIndex( mProxy.mapFromSource( index ) )
    
    gbAddToProject.setEnabled( mModel and mModel.rowCount() > 0 )
    
    # connections
    cbLanguages.currentIndexChanged.connect(self.onFiltersChanged)
    cbTypes.currentIndexChanged.connect(self.onFiltersChanged)
    
    # init template
    onFiltersChanged()


def setType(self, type ):
{ cbTypes.setCurrentIndex( cbTypes.findData( type ) );

def onFiltersChanged(self):
    # get combobox text
    t = cbTypes.itemData( cbTypes.currentIndex() ).toString()
    l = cbLanguages.itemData( cbLanguages.currentIndex() ).toString()
    QString i

    # clear lwTemplates
    lwTemplates.clear()

    # create templates items
    for tp in mTemplates:
        if (  ( l == "All" or tp.Language == l or tp.Language == "All" ) and
            ( t == "All" or tp.Type == t or tp.Type == "All" ) )
            it = QListWidgetItem( lwTemplates )
            i = ":/templates/icons/templates/empty.png"
            if  not tp.Icon.isEmpty() :
                if  QFile.exists( tp.DirPath +tp.Icon ) :
                    i = tp.DirPath +tp.Icon
                elif  QFile.exists( ":/templates/icons/templates/" +tp.Icon ) :
                    i = ":/templates/icons/templates/" +tp.Icon

            it.setIcon( QIcon( i ) )
            it.setToolTip( tp.Description )
            it.setText( tp.Name )
            it.setData( Qt.UserRole +1, mTemplates.indexOf( tp ) )



    # disable groupbox
    lInformations.setText( "No Template Selected" )
    gbInformations.setEnabled( False )


def on_lwTemplates_itemPressed(self, it ):
    # delete labels & combos
    qDeleteAll( mLabels )
    mLabels.clear()
    qDeleteAll( mCombos )
    mCombos.clear()
    
    # get template
    t = mTemplates.value( it.data( Qt.UserRole +1 ).toInt() )
    r = 1
    
    # set template informations
    lInformations.setText( t.Description )
    
    # create labels/combos
    for v in t.Variables.keys():
        c = QComboBox()
        c.setSizeAdjustPolicy( QComboBox.AdjustToMinimumContentsLength )
        c.setEditable( True )
        c.addItems( t.Variables.value( v ) )
        
        l = QLabel( v +" :" )
        l.setSizePolicy( QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Preferred ) )
        l.setToolTip( v )
        l.setBuddy( c )
        
        gridLayout.addWidget( l, r, 0 )
        mLabels << l
        
        gridLayout.addWidget( c, r++, 1 )
        mCombos << c

    
    # enable groupbox
    gbInformations.setEnabled( True )


def on_gbAddToProject_toggled(self, toggled ):
     idx = mProxy.mapToSource( cbProjects.currentIndex() )
    item = mModel.itemFromIndex( idx )
    project = item ? item.project() : 0
    
    if  toggled and project :
        codec = project.temporaryValue( "codec", pMonkeyStudio.defaultCodec() ).toString()
        cbCodec.setCurrentIndex( cbCodec.findText( codec ) )



def on_cbExpert_clicked(self, checked ):
     idx = mProxy.mapToSource( cbProjects.currentIndex() )
    item = mModel.itemFromIndex( idx )
    
    blocked = cbProjects.blockSignals( True )
    mProxy.setShowDisabled( checked )
    
    proxyIndex = mProxy.mapFromSource( item.index() )
    if  not proxyIndex.isValid() :
        proxyIndex = mProxy.mapFromSource( item.project().index() )

    
    cbProjects.setCurrentIndex( proxyIndex )
    cbProjects.blockSignals( blocked )


def on_cbProjects_currentChanged(self, index ):
     idx = mProxy.mapToSource( index )
    item = mModel.itemFromIndex( idx )
    project = item ? item.project() : 0
    
    if  project :
         path = project.path()
        
        if  not leDestination.text().startsWith( path ) :
            leDestination.setText( project.path() )

        
        if  gbAddToProject.isChecked() :
            codec = project.temporaryValue( "codec", pMonkeyStudio.defaultCodec() ).toString()
            cbCodec.setCurrentIndex( cbCodec.findText( codec ) )




def on_tbDestination_clicked(self):
    s = pMonkeyStudio.getExistingDirectory( tr( "Select the file(s) destination" ), leDestination.text(), window() )
    if  not s.isNull() :
        leDestination.setText( s )


def checkTemplate(self):
    # check item available
    if  not lwTemplates.selectedItems().count() :
        QMessageBox.information( window(), tr( "Template..." ), tr( "You need to select a template." ) )
        return False

    
    # return default value
    return True


def on_pbCreate_clicked(self):
    # check if we can go later
    if  not checkTemplate() :
        return
    
    # get variables
    VariablesManager.Dictionary v
    v[ "Destination" ] = leDestination.text()
    
    # iterate each labels
    for l in mLabels:
        v[l.toolTip()] = qobject_cast<QComboBox*>( l.buddy() ).currentText()
    
    # get template
    t = mTemplates.value( lwTemplates.selectedItems().value( 0 ).data( Qt.UserRole +1 ).toInt() )
    
    # check if need open files
    if  not cbOpen.isChecked() :
        t.FilesToOpen.clear()
        t.ProjectsToOpen.clear()

    
    # check if need add files
    if  not gbAddToProject.isChecked() or not cbProjects.currentIndex().isValid() :
        t.FilesToAdd.clear()
    
    # don t open project, adding it to a parent will automatically open it
    if  not t.FilesToAdd.isEmpty() :
        t.ProjectsToOpen.clear()
    
    # get proejct to add
    proxyIndex = cbProjects.currentIndex()
    index = mProxy.mapToSource( proxyIndex )
    si = t.FilesToAdd.isEmpty() ? 0 : mModel.itemFromIndex( index )
    
    # process templates
    if  not pTemplatesManager.instance().realiseTemplate( si, t, cbCodec.currentText(), v ) :
        return
    
    # remember some infos
    s = MonkeyCore.settings()
    s.setValue( "Recents/FileWizard/Language", cbLanguages.currentText() )
    s.setValue( "Recents/FileWizard/Expert", cbExpert.isChecked() )
    s.setValue( "Recents/FileWizard/Destination", leDestination.text() )
    s.setValue( "Recents/FileWizard/Open", cbOpen.isChecked() )
    
    # close dialog
    QDialog.accept();    

