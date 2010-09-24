/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIBuilderSettings.cpp
** Date      : 2008-01-14T00:36:58
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
#include "UIBuilderSettings.h"
#include "pluginsmanager/BuilderPlugin.h"
#include  "consolemanager/pConsoleManager.h"
#include "pMonkeyStudio.h"
#include "coremanager/MonkeyCore.h"

#include <QInputDialog>
#include <QPushButton>

using namespace pMonkeyStudio;

UIBuilderSettings::UIBuilderSettings( BuilderPlugin* p, QWidget* w )
	: QWidget( w ), mPlugin( p )
{
	Q_ASSERT( mPlugin );
	setupUi( this );
	// set button icons
	dbbButtons->button( QDialogButtonBox::Help )->setIcon( QIcon( ":/help/icons/help/keyword.png" ) );
	dbbButtons->button( QDialogButtonBox::Reset )->setIcon( QIcon( ":/tools/icons/tools/update.png" ) );
	dbbButtons->button( QDialogButtonBox::RestoreDefaults )->setIcon( QIcon( ":/file/icons/file/backup.png" ) );
	dbbButtons->button( QDialogButtonBox::Save )->setIcon( QIcon( ":/file/icons/file/save.png" ) );
	// delete widget when close
	setAttribute( Qt::WA_DeleteOnClose );
	// memorize defaults and user commands
	mDefault = mPlugin->defaultBuildCommand();
	mCommand = mPlugin->buildCommand();
	mReset = mCommand;
	// add parsers
	lwBuildCommandParsers->addItems( MonkeyCore::consoleManager()->parsersName() );
	// set uncheck state for parser items
	for ( int i = 0; i < lwBuildCommandParsers->count(); i++ )
		lwBuildCommandParsers->item( i )->setCheckState( Qt::Unchecked );
	// load commands
	updateCommand();
}

void UIBuilderSettings::updateCommand()
{
	leBuildCommandText->setText( mCommand.text() );
	leBuildCommandCommand->setText( mCommand.command() );
	leBuildCommandArguments->setText( mCommand.arguments() );
	leBuildCommandWorkingDirectory->setText( mCommand.workingDirectory() );
	cbBuildCommandSkipOnError->setChecked( mCommand.skipOnError() );
	for ( int i = 0; i < lwBuildCommandParsers->count(); i++ )
	{
		QListWidgetItem* it = lwBuildCommandParsers->item( i );
		it->setCheckState( mCommand.parsers().contains( it->text() ) ? Qt::Checked : Qt::Unchecked );
	}
	cbBuildCommandTryAll->setChecked( mCommand.tryAllParsers() );
}

void UIBuilderSettings::restoreDefault()
{
	mCommand = mDefault;
	updateCommand();
}

void UIBuilderSettings::reset()
{
	mCommand = mReset;
	updateCommand();
}

void UIBuilderSettings::save()
{
	mCommand.setText( leBuildCommandText->text() );
	mCommand.setCommand( leBuildCommandCommand->text() );
	mCommand.setArguments( leBuildCommandArguments->text() );
	mCommand.setWorkingDirectory( leBuildCommandWorkingDirectory->text() );
	mCommand.setSkipOnError( cbBuildCommandSkipOnError->isChecked() );
	QStringList l;
	for ( int i = 0; i < lwBuildCommandParsers->count(); i++ )
	{
		QListWidgetItem* it = lwBuildCommandParsers->item( i );
		if ( it->checkState() == Qt::Checked )
			l << it->text();
	}
	mCommand.setParsers( l );
	mCommand.setTryAllParsers( cbBuildCommandTryAll->isChecked() );
	mPlugin->setBuildCommand( mCommand );
}

void UIBuilderSettings::on_tbBuildCommandCommand_clicked()
{
	QString s = getOpenFileName( tr( "Select an executable" ), leBuildCommandCommand->text() );
	if ( !s.isNull() )
		leBuildCommandCommand->setText( s );
}

void UIBuilderSettings::on_tbBuildCommandWorkingDirectory_clicked()
{
	QString s = getExistingDirectory( tr( "Select a folder" ), leBuildCommandWorkingDirectory->text() );
	if ( !s.isNull() )
		leBuildCommandWorkingDirectory->setText( s );
}

void UIBuilderSettings::on_dbbButtons_clicked( QAbstractButton* b )
{
	if ( dbbButtons->standardButton( b ) == QDialogButtonBox::Reset )
		reset();
	else if ( dbbButtons->standardButton( b ) == QDialogButtonBox::RestoreDefaults )
		restoreDefault();
	else if ( dbbButtons->standardButton( b ) == QDialogButtonBox::Save )
		save();
}
