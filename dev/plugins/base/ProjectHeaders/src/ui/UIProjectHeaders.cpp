/****************************************************************************
**
** 		Created using Monkey Studio v1.8.0.0
** Author    : Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>
** Project   : UIProjectHeaders
** FileName  : UIProjectHeaders.cpp
** Date      : 2007-11-04T02:21:34
** License   : GPL
** Comment   : Your comment here
**
** This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
** WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
**
****************************************************************************/
#include "UIProjectHeaders.h"
#include "ProjectHeaders.h"

#include <QDir>
#include <QFileInfoList>
#include <QTextCodec>
#include <QHash>
#include <QStringList>
#include <QPushButton>
#include <QDateTime>
#include <QMessageBox>
#include <QDebug>

#include <pMonkeyStudio.h>
#include <variablesmanager/VariablesManager.h>

UIProjectHeaders::UIProjectHeaders( QWidget* parent, ProjectHeaders* plugin )
	: QDialog( parent ), mPlugin( plugin )
{
	// setup dialog
	setupUi( this );
	// restore settings
	restoreSettings();
	// set buttons icons
	dbbButtons->button( QDialogButtonBox::Apply )->setIcon( QPixmap( ":/icons/icons/ok.png" ) );
	dbbButtons->button( QDialogButtonBox::Close )->setIcon( QPixmap( ":/icons/icons/cancel.png" ) );
	// connections
	connect( dbbButtons->button( QDialogButtonBox::Apply ), SIGNAL( clicked() ), this, SLOT( accept() ) );
}

void UIProjectHeaders::restoreSettings()
{
	// add languages to combo
	cbLanguages->addItems( pMonkeyStudio::availableLanguages() );
	// save inputs
	leDirectory->setText( mPlugin->settingsValue( "Directory" ).toString() );
	leAuthors->setText( mPlugin->settingsValue( "Authors" ).toString() );
	leProjectName->setText( mPlugin->settingsValue( "ProjectName" ).toString() );
	leHomePage->setText( mPlugin->settingsValue( "HomePage" ).toString() );
	const QString license = mPlugin->settingsValue( "License", "GPL" ).toString();
	if ( cbLicenses->findText( license ) == -1 )
		cbLicenses->addItem( license );
	cbLicenses->setCurrentIndex( cbLicenses->findText( license ) );
	teComment->setPlainText( mPlugin->settingsValue( "Comment" ).toString() );
	// set regexp and licensing
	for ( int i = 0; i < cbLanguages->count(); i++ )
	{
		cbLanguages->setItemData( i, templatesHeaderRegExp( cbLanguages->itemText( i ) ), Qt::UserRole +1 );
		cbLanguages->setItemData( i, templatesHeader( cbLanguages->itemText( i ) ), Qt::UserRole +2 );
	}
	// show current language information
	if ( cbLanguages->count() )
	{
		cbLanguages->setCurrentIndex( 0 );
		leRegExp->setText( cbLanguages->itemData( 0, Qt::UserRole +1 ).toString() );
		teLicensing->setPlainText( cbLanguages->itemData( 0, Qt::UserRole +2 ).toString() );
	}
	// encodings
	QStringList encodings = pMonkeyStudio::availableTextCodecs();
	lwSourceEncoding->addItems( encodings );
	lwTargetEncoding->addItems( encodings );
	QList<QListWidgetItem*> items;
	items = lwSourceEncoding->findItems( mPlugin->settingsValue( "SourceEncoding", "UTF-8" ).toString(), Qt::MatchFixedString );
	lwSourceEncoding->setCurrentItem( items.value( 0 ) );
	items = lwTargetEncoding->findItems( mPlugin->settingsValue( "TargetEncoding", "UTF-8" ).toString(), Qt::MatchFixedString );
	lwTargetEncoding->setCurrentItem( items.value( 0 ) );
}

void UIProjectHeaders::saveSettings()
{
	// save inputs
	mPlugin->setSettingsValue( "Directory", leDirectory->text() );
	mPlugin->setSettingsValue( "Authors", leAuthors->text() );
	mPlugin->setSettingsValue( "ProjectName", leProjectName->text() );
	mPlugin->setSettingsValue( "HomePage", leHomePage->text() );
	mPlugin->setSettingsValue( "License", cbLicenses->currentText() );
	mPlugin->setSettingsValue( "Comment", teComment->toPlainText() );
	// save regexp and licensing
	on_cbLanguages_highlighted( -1 );
	for ( int i = 0; i < cbLanguages->count(); i++ )
	{
		setTemplatesHeaderRegExp( cbLanguages->itemText( i ), cbLanguages->itemData( i, Qt::UserRole +1 ).toString() );
		setTemplatesHeader( cbLanguages->itemText( i ), cbLanguages->itemData( i, Qt::UserRole +2 ).toString() );
	}
	// encodings
	if ( QListWidgetItem* item = lwSourceEncoding->selectedItems().value( 0 ) )
		mPlugin->setSettingsValue( "SourceEncoding", item->text() );
	if ( QListWidgetItem* item = lwTargetEncoding->selectedItems().value( 0 ) )
		mPlugin->setSettingsValue( "TargetEncoding", item->text() );
}

void UIProjectHeaders::setTemplatesHeaderRegExp( const QString& language, const QString& regexp )
{ mPlugin->setSettingsValue( QString( "RegExp/" ).append( language ), regexp ); }

QString UIProjectHeaders::templatesHeaderRegExp( const QString& language ) const
{
	QString regexp = mPlugin->settingsValue( QString( "RegExp/" ).append( language ), QString() ).toString();
	return regexp.isEmpty() ? defaultTemplatesHeaderRegExp( language ) : regexp;
}

QString UIProjectHeaders::defaultTemplatesHeaderRegExp( const QString& language ) const
{
	QString regexp;
	
	if ( language == "C++" )
		regexp = "^(/\\*.*\\*/)";
	else if ( language == "HTML" )
		regexp = "^(<!--+.*--+>)";
	
	// default
	return regexp;
}

void UIProjectHeaders::setTemplatesHeader( const QString& language, const QString& license )
{ mPlugin->setSettingsValue( QString( "Licensing/" ).append( language ), license ); }

QString UIProjectHeaders::templatesHeader( const QString& language ) const
{
	QString license = mPlugin->settingsValue( QString( "Licensing/" ).append( language ), QString() ).toString();
	return license.isEmpty() ? defaultTemplatesHeader( language ) : license;
}

QString UIProjectHeaders::defaultTemplatesHeader( const QString& language ) const
{
	QString license;
	
	if ( language == "C++" )
		license = "/****************************************************************************\n"
			"**\n"
			"** 		Created using $editor_version_string$\n"
			"** Authors   : $authors$\n"
			"** Project   : $projectname$\n"
			"** FileName  : $filename$\n"
			"** Date      : $date$\n"
			"** License   : $license$\n"
			"** Comment   : $comment$\n"
			"** Home Page : $homepage$\n"
			"**\n"
			"** This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE\n"
			"** WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.\n"
			"**\n"
			"****************************************************************************/\n";
	else if ( language == "HTML" )
		license = "<!---------------------------------------------------------------------\n"
			"--\n"
			"--		Created using $editor_version_string$\n"
			"-- Authors   : $authors$\n"
			"-- Project   : $projectname$\n"
			"-- FileName  : $filename$\n"
			"-- Date      : $date$\n"
			"-- License   : $license$\n"
			"-- Comment   : $comment$\n"
			"-- Home Page : $homepage$\n"
			"--\n"
			"-- This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE\n"
			"-- WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.\n"
			"--\n"
			"---------------------------------------------------------------------------->\n";
	
	// default
	return license;
}

void UIProjectHeaders::on_cbLanguages_highlighted( int )
{
	cbLanguages->setItemData( cbLanguages->currentIndex(), leRegExp->text(), Qt::UserRole +1 );
	cbLanguages->setItemData( cbLanguages->currentIndex(), teLicensing->toPlainText(), Qt::UserRole +2 );
}

void UIProjectHeaders::on_cbLanguages_currentIndexChanged( int i )
{
	leRegExp->setText( cbLanguages->itemData( i, Qt::UserRole +1 ).toString() );
	teLicensing->setPlainText( cbLanguages->itemData( i, Qt::UserRole +2 ).toString() );
}

void UIProjectHeaders::on_tbDirectory_clicked()
{
	const QString s = pMonkeyStudio::getExistingDirectory( tr( "Choose the directory to scan" ), QString(), window() );
	if ( !s.isEmpty() )
		leDirectory->setText( s );
}

void UIProjectHeaders::reject()
{
	saveSettings();
	QDialog::reject();
}

void UIProjectHeaders::accept()
{
	// save settings
	saveSettings();
	// get languages filters
	QStringList filters;
	QMap<QString, QStringList> l = pMonkeyStudio::availableLanguagesSuffixes();
	foreach ( QString k, l.keys() )
		foreach ( QString e, l.value( k ) )
			if ( !filters.contains( e ) )
				filters << e;
	// encodings
	QTextCodec* sourceCodec = QTextCodec::codecForName( mPlugin->settingsValue( "SourceEncoding", "UTF-8" ).toString().toAscii() );
	QTextCodec* targetCodec = QTextCodec::codecForName( mPlugin->settingsValue( "SourceEncoding", "UTF-8" ).toString().toAscii() );
	// set dictionnary
	VariablesManager::Dictionary v;
	v[ "authors" ] = leAuthors->text();
	v[ "projectname" ] = leProjectName->text();
	v[ "license" ] = cbLicenses->currentText();
	v[ "homepage" ] = leHomePage->text();
	v[ "comment" ] = teComment->toPlainText().trimmed();
	// get variables manager
	VariablesManager* vm = VariablesManager::instance();
	// get recursive files
	bool yesToAll = false;
	foreach ( QFileInfo fi, pMonkeyStudio::getFiles( QDir( leDirectory->text() ), filters, true ) )
	{
		QFile f( fi.absoluteFilePath() );
		f.open( QIODevice::ReadWrite | QIODevice::Text );
		QString b = sourceCodec->toUnicode( f.readAll() );
		QString l = pMonkeyStudio::languageForFileName( fi.fileName() );
		// regexp
		QRegExp rx( templatesHeaderRegExp( l ) );
		rx.setMinimal( true );
		if ( rx.indexIn( b ) != -1 && rx.cap( 1 ).trimmed().length() > 0 )
		{
			if ( !yesToAll )
			{
				QMessageBox msg( window() );
				msg.setWindowTitle( tr( "Replace Licensing..." ) );
				msg.setIcon( QMessageBox::Question );
				msg.setStandardButtons( QMessageBox::YesToAll | QMessageBox::Yes | QMessageBox::No | QMessageBox::Cancel );
				msg.setText( tr( "There already is a licensing, in file :\n%1\n replace it ?" ).arg( fi.fileName() ) );
				msg.setDetailedText( rx.cap( 1 ) );
				switch ( msg.exec() )
				{
					case QMessageBox::YesToAll:
						yesToAll = true;
						break;
					case QMessageBox::No:
						continue;
						break;
					case QMessageBox::Cancel:
						return;
					default:
						break;
				}
			}
			b.remove( 0, rx.cap( 1 ).length() );
		}
		// set variables
		v[ "filename" ] = fi.fileName();
		v[ "date" ] = fi.created().toString( Qt::ISODate );
		// replaces variables
		b = b.trimmed().prepend( vm->replaceAllVariables( templatesHeader( l ), v ) ).append( pMonkeyStudio::getEol() );
		// write buffer
		f.resize( 0 );
		f.write( targetCodec->fromUnicode( b ) );
		f.close();
	}
}
