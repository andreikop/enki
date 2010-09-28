/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, 
**                
** Project   : Monkey Studio Base Plugins
** FileName  : UIMessageBoxSettings.h
** Date      : 2008-01-14T00:40:08
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
/*!
    \file UIMessageBoxSettings.h
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO
    \brief Header of UIMessageBoxSettings class
*/

#include "UIMessageBoxSettings.h"
#include "MessageBox.h"

#include <QWhatsThis>
#include <QPushButton>

/*!
    Create settings widget
    \param plugin Pointer to MessageBox plugin
    \param parent Parent widget
*/
UIMessageBoxSettings::UIMessageBoxSettings( MessageBox* plugin, QWidget* parent )
    : QWidget( parent )
{
    mPlugin = plugin;
    setupUi( this );
    
    dbbButtons->button( QDialogButtonBox::Help )->setIcon( QIcon( ":/help/icons/help/keyword.png" ) );
    dbbButtons->button( QDialogButtonBox::RestoreDefaults )->setIcon( QIcon( ":/file/icons/file/backup.png" ) );
    dbbButtons->button( QDialogButtonBox::Apply )->setIcon( QIcon( ":/file/icons/file/save.png" ) );
    
    // fill combobox
    cbActivateDock->addItem( tr( "Build Step" ), UIMessageBoxSettings::BuildStep );
    cbActivateDock->addItem( tr( "Output" ), UIMessageBoxSettings::Output );
    cbActivateDock->addItem( tr( "Commands" ), UIMessageBoxSettings::Command );
    
    // restore settings
    gbActivateDock->setChecked( mPlugin->settingsValue( "ActivateDock", true ).toBool() );
    UIMessageBoxSettings::Dock dock = (UIMessageBoxSettings::Dock)mPlugin->settingsValue( "ActivatedDock", UIMessageBoxSettings::Output ).toInt();
    cbActivateDock->setCurrentIndex( cbActivateDock->findData( dock ) );
}

/*!
    Handler of pressing of any button on settings widget
    
    Help, Restore Defaults or Apply button can be pressed
    Function will do action, according to button
    \param button Pressed button (Help, RestoreDefaults, Apply)
*/
void UIMessageBoxSettings::on_dbbButtons_clicked( QAbstractButton* button )
{
    if ( button == dbbButtons->button( QDialogButtonBox::Help ) )
    {
        const QString help = tr( "You can activate a special Message Box dock when console is started, for this check the box and choose witch dock to activate." );
        QWhatsThis::showText( mapToGlobal( rect().center() ), help, this ) ;
    }
    else if ( button == dbbButtons->button( QDialogButtonBox::RestoreDefaults ) )
    {
        gbActivateDock->setChecked( true );
        cbActivateDock->setCurrentIndex( cbActivateDock->findData( UIMessageBoxSettings::Output ) );
    }
    else if ( button == dbbButtons->button( QDialogButtonBox::Apply ) )
    {
        mPlugin->setSettingsValue( "ActivateDock", gbActivateDock->isChecked() );
        mPlugin->setSettingsValue( "ActivatedDock", cbActivateDock->itemData( cbActivateDock->currentIndex() ).toInt() );
    }
}
