/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UITemplatesWizard.cpp
** Date      : 2008-01-14T00:37:11
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
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
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
**
****************************************************************************/
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

UITemplatesWizard::UITemplatesWizard( QWidget* parent )
    : QDialog( parent )
{
    // init dialog
    setupUi( this );
    saWidgets->setWidgetResizable( true );
    
    // create scrollarea widget
    QWidget* cw = new QWidget;
    gridLayout = new QGridLayout( cw );
    gridLayout->setMargin( 5 );
    gridLayout->setSpacing( 3 );
    saWidgets->setWidget( cw );
    
    // get templates
    mTemplates = pTemplatesManager::instance()->getTemplates();
    
    // set default language/type
    cbLanguages->addItem( tr( "All" ), "All" );
    cbTypes->addItem( tr( "All" ), "All" );
    
    cbCodec->addItems( pMonkeyStudio::availableTextCodecs() );
    
    // languages/types
    foreach( pTemplate tp, mTemplates )
    {
        if ( cbLanguages->findData( tp.Language, Qt::UserRole, Qt::MatchFixedString ) == -1 )
            cbLanguages->addItem( tr( tp.Language.toLocal8Bit().constData() ), tp.Language );
        if ( cbTypes->findData( tp.Type, Qt::UserRole, Qt::MatchFixedString ) == -1 )
            cbTypes->addItem( tr( tp.Type.toLocal8Bit().constData() ), tp.Type );
    }
    
    // restore infos
    pSettings* s = MonkeyCore::settings();
    cbLanguages->setCurrentIndex( cbLanguages->findText( s->value( "Recents/FileWizard/Language", "C++" ).toString() ) );
    cbExpert->setChecked( s->value( "Recents/FileWizard/Expert", false ).toBool() );
    leDestination->setText( s->value( "Recents/FileWizard/Destination", QDir::currentPath() ).toString() );
    cbOpen->setChecked( s->value( "Recents/FileWizard/Open", true ).toBool() );
    cbCodec->setCurrentIndex( cbCodec->findText( pMonkeyStudio::defaultCodec() ) );

    // assign projects combobox
    mModel = MonkeyCore::projectsManager()->currentProjectModel();
    mProxy = new XUPProjectModelProxy( this, cbExpert->isChecked() );
    XUPProjectItem* project = MonkeyCore::projectsManager()->currentProject();
    QModelIndex index = project ? project->index() : QModelIndex();
    
    mProxy->setSourceModel( mModel );
    cbProjects->setModel( mProxy );
    cbProjects->setCurrentIndex( mProxy->mapFromSource( index ) );
    
    gbAddToProject->setEnabled( mModel && mModel->rowCount() > 0 );
    
    // connections
    connect( cbLanguages, SIGNAL( currentIndexChanged( int ) ), this, SLOT( onFiltersChanged() ) );
    connect( cbTypes, SIGNAL( currentIndexChanged( int ) ), this, SLOT( onFiltersChanged() ) );
    
    // init template
    onFiltersChanged();
}

void UITemplatesWizard::setType( const QString& type )
{ cbTypes->setCurrentIndex( cbTypes->findData( type ) ); }

void UITemplatesWizard::onFiltersChanged()
{
    // get combobox text
    QString t = cbTypes->itemData( cbTypes->currentIndex() ).toString();
    QString l = cbLanguages->itemData( cbLanguages->currentIndex() ).toString();
    QString i;

    // clear lwTemplates
    lwTemplates->clear();

    // create templates items
    foreach ( pTemplate tp, mTemplates )
    {
        if (  ( l == "All" || tp.Language == l || tp.Language == "All" ) &&
            ( t == "All" || tp.Type == t || tp.Type == "All" ) )
        {
            QListWidgetItem* it = new QListWidgetItem( lwTemplates );
            i = ":/templates/icons/templates/empty.png";
            if ( !tp.Icon.isEmpty() )
            {
                if ( QFile::exists( tp.DirPath +tp.Icon ) )
                    i = tp.DirPath +tp.Icon;
                else if ( QFile::exists( ":/templates/icons/templates/" +tp.Icon ) )
                    i = ":/templates/icons/templates/" +tp.Icon;
            }
            it->setIcon( QIcon( i ) );
            it->setToolTip( tp.Description );
            it->setText( tp.Name );
            it->setData( Qt::UserRole +1, mTemplates.indexOf( tp ) );
        }
    }

    // disable groupbox
    lInformations->setText( "No Template Selected" );
    gbInformations->setEnabled( false );
}

void UITemplatesWizard::on_lwTemplates_itemPressed( QListWidgetItem* it )
{
    // delete labels & combos
    qDeleteAll( mLabels );
    mLabels.clear();
    qDeleteAll( mCombos );
    mCombos.clear();
    
    // get template
    pTemplate t = mTemplates.value( it->data( Qt::UserRole +1 ).toInt() );
    int r = 1;
    
    // set template informations
    lInformations->setText( t.Description );
    
    // create labels/combos
    foreach( QString v, t.Variables.keys() )
    {
        QComboBox* c = new QComboBox();
        c->setSizeAdjustPolicy( QComboBox::AdjustToMinimumContentsLength );
        c->setEditable( true );
        c->addItems( t.Variables.value( v ) );
        
        QLabel* l = new QLabel( v +" :" );
        l->setSizePolicy( QSizePolicy( QSizePolicy::Maximum, QSizePolicy::Preferred ) );
        l->setToolTip( v );
        l->setBuddy( c );
        
        gridLayout->addWidget( l, r, 0 );
        mLabels << l;
        
        gridLayout->addWidget( c, r++, 1 );
        mCombos << c;
    }
    
    // enable groupbox
    gbInformations->setEnabled( true );
}

void UITemplatesWizard::on_gbAddToProject_toggled( bool toggled )
{
    const QModelIndex idx = mProxy->mapToSource( cbProjects->currentIndex() );
    XUPItem* item = mModel->itemFromIndex( idx );
    XUPProjectItem* project = item ? item->project() : 0;
    
    if ( toggled && project )
    {
        QString codec = project->temporaryValue( "codec", pMonkeyStudio::defaultCodec() ).toString();
        cbCodec->setCurrentIndex( cbCodec->findText( codec ) );
    }
}

void UITemplatesWizard::on_cbExpert_clicked( bool checked )
{
    const QModelIndex idx = mProxy->mapToSource( cbProjects->currentIndex() );
    XUPItem* item = mModel->itemFromIndex( idx );
    
    bool blocked = cbProjects->blockSignals( true );
    mProxy->setShowDisabled( checked );
    
    QModelIndex proxyIndex = mProxy->mapFromSource( item->index() );
    if ( !proxyIndex.isValid() )
    {
        proxyIndex = mProxy->mapFromSource( item->project()->index() );
    }
    
    cbProjects->setCurrentIndex( proxyIndex );
    cbProjects->blockSignals( blocked );
}

void UITemplatesWizard::on_cbProjects_currentChanged( const QModelIndex& index )
{
    const QModelIndex idx = mProxy->mapToSource( index );
    XUPItem* item = mModel->itemFromIndex( idx );
    XUPProjectItem* project = item ? item->project() : 0;
    
    if ( project )
    {
        const QString path = project->path();
        
        if ( !leDestination->text().startsWith( path ) )
        {
            leDestination->setText( project->path() );
        }
        
        if ( gbAddToProject->isChecked() )
        {
            QString codec = project->temporaryValue( "codec", pMonkeyStudio::defaultCodec() ).toString();
            cbCodec->setCurrentIndex( cbCodec->findText( codec ) );
        }
    }
}

void UITemplatesWizard::on_tbDestination_clicked()
{
    QString s = pMonkeyStudio::getExistingDirectory( tr( "Select the file(s) destination" ), leDestination->text(), window() );
    if ( !s.isNull() )
        leDestination->setText( s );
}

bool UITemplatesWizard::checkTemplate()
{
    // check item available
    if ( !lwTemplates->selectedItems().count() )
    {
        QMessageBox::information( window(), tr( "Template..." ), tr( "You need to select a template." ) );
        return false;
    }
    
    // return default value
    return true;
}

void UITemplatesWizard::on_pbCreate_clicked()
{
    // check if we can go later
    if ( !checkTemplate() )
        return;
    
    // get variables
    VariablesManager::Dictionary v;
    v[ "Destination" ] = leDestination->text();
    
    // iterate each labels
    foreach ( QLabel* l, mLabels )
        v[l->toolTip()] = qobject_cast<QComboBox*>( l->buddy() )->currentText();
    
    // get template
    pTemplate t = mTemplates.value( lwTemplates->selectedItems().value( 0 )->data( Qt::UserRole +1 ).toInt() );
    
    // check if need open files
    if ( !cbOpen->isChecked() )
    {
        t.FilesToOpen.clear();
        t.ProjectsToOpen.clear();
    }
    
    // check if need add files
    if ( !gbAddToProject->isChecked() || !cbProjects->currentIndex().isValid() )
        t.FilesToAdd.clear();
    
    // don t open project, because adding it to a parent will automatically open it
    if ( !t.FilesToAdd.isEmpty() )
        t.ProjectsToOpen.clear();
    
    // get proejct to add
    QModelIndex proxyIndex = cbProjects->currentIndex();
    QModelIndex index = mProxy->mapToSource( proxyIndex );
    XUPItem* si = t.FilesToAdd.isEmpty() ? 0 : mModel->itemFromIndex( index );
    
    // process templates
    if ( !pTemplatesManager::instance()->realiseTemplate( si, t, cbCodec->currentText(), v ) )
        return;
    
    // remember some infos
    pSettings* s = MonkeyCore::settings();
    s->setValue( "Recents/FileWizard/Language", cbLanguages->currentText() );
    s->setValue( "Recents/FileWizard/Expert", cbExpert->isChecked() );
    s->setValue( "Recents/FileWizard/Destination", leDestination->text() );
    s->setValue( "Recents/FileWizard/Open", cbOpen->isChecked() );
    
    // close dialog
    QDialog::accept();    
}
