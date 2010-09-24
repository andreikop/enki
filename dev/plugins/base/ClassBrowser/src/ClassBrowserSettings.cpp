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
/*!
	\file ClassBrowserSettings.cpp
	\date 2009-05-01
	\author Filipe AZEVEDO
	\brief Settings widget of ClassBrowser plugin
*/
#include "ClassBrowserSettings.h"
#include "ClassBrowser.h"

#include <objects/pIconManager.h>
#include <widgets/pPathListEditor.h>

#include <QBoxLayout>
#include <QLabel>
#include <QComboBox>
#include <QDialogButtonBox>
#include <QPushButton>
#include <QFileDialog>
#include <QGroupBox>
#include <QLineEdit>
#include <QToolButton>

/*!
	Creates settings widget
	\param plugin Pointer to ClassBrowser plugin
	\param parent Parent widget of settings widget
*/
ClassBrowserSettings::ClassBrowserSettings( ClassBrowser* plugin, QWidget* parent )
	: QWidget( parent )
{
	// retain plugin
	mPlugin = plugin;
	
	qCtagsSenseProperties properties = mPlugin->properties();
	
	// integration
	QLabel* label = new QLabel( tr( "Integration Mode:" ) );
	cbIntegrationMode = new QComboBox;
	QHBoxLayout* hbox = new QHBoxLayout;
	cbIntegrationMode->addItem( tr( "Dock" ), ClassBrowser::imDock );
	cbIntegrationMode->addItem( tr( "Combo" ), ClassBrowser::imCombo );
	cbIntegrationMode->addItem( tr( "Both" ), ClassBrowser::imBoth );
	cbIntegrationMode->setCurrentIndex( cbIntegrationMode->findData( plugin->integrationMode() ) );
	hbox->addWidget( label );
	hbox->addWidget( cbIntegrationMode );
	
	// db filename
	gbUseDBFileName = new QGroupBox( tr( "Use a physical database" ), this );
	gbUseDBFileName->setCheckable( true );
	gbUseDBFileName->setChecked( properties.UsePhysicalDatabase );
	lDBFileName = new QLabel( tr( "Database file name" ), this );
	leDBFileName = new QLineEdit( this );
	leDBFileName->setText( properties.DatabaseFileName );
	tbDBFileName = new QToolButton( this );
	tbDBFileName->setIcon( pIconManager::icon( "file.png", ":/listeditor" ) );
	QGridLayout* hbox2 = new QGridLayout( gbUseDBFileName );
	hbox2->addWidget( lDBFileName, 0, 0, 1, 2 );
	hbox2->addWidget( leDBFileName, 1, 0 );
	hbox2->addWidget( tbDBFileName, 1, 1 );
	
	// list editor
	mPathEditor = new pPathListEditor( this, tr( "System include paths" ) );
	mPathEditor->setValues( properties.SystemPaths );
	
	mStringEditor = new pStringListEditor( this, tr( "Filtered file suffixes" ) );
	mStringEditor->setValues( properties.FilteredSuffixes );
	
	// apply button
	QDialogButtonBox* dbbApply = new QDialogButtonBox( this );
	dbbApply->addButton( QDialogButtonBox::Apply );
	
	// global layout
	QVBoxLayout* vbox = new QVBoxLayout( this );
	vbox->addLayout( hbox );
	vbox->addWidget( gbUseDBFileName );
	vbox->addWidget( mPathEditor );
	vbox->addWidget( mStringEditor );
	vbox->addWidget( dbbApply );
	
	// connections
	connect( tbDBFileName, SIGNAL( clicked() ), this, SLOT( tbDBFileName_clicked() ) );
	connect( dbbApply->button( QDialogButtonBox::Apply ), SIGNAL( clicked() ), this, SLOT( applySettings() ) );
}

void ClassBrowserSettings::tbDBFileName_clicked()
{
	const QString fn = QFileDialog::getSaveFileName( this, tr( "Select a filename to use for the temporary database" ), leDBFileName->text() );
	
	if ( !fn.isNull() )
	{
		leDBFileName->setText( fn );
	}
}

/*!
	Handler of clicking Apply button. Applying settings
*/
void ClassBrowserSettings::applySettings()
{
	qCtagsSenseProperties properties;
	properties.SystemPaths = mPathEditor->values();
	properties.FilteredSuffixes = mStringEditor->values();
	properties.UsePhysicalDatabase = gbUseDBFileName->isChecked();
	properties.DatabaseFileName = leDBFileName->text();
	
	mPlugin->setIntegrationMode( (ClassBrowser::IntegrationMode)cbIntegrationMode->itemData( cbIntegrationMode->currentIndex() ).toInt() );
	mPlugin->setProperties( properties );
}
