#include "SearchAndReplaceSettings.h"

SearchAndReplaceSettings::SearchAndReplaceSettings( SearchAndReplace* plugin, QWidget* parent )
	: QWidget( parent )
{
	Q_ASSERT( plugin );
	mPlugin = plugin;
	
	setupUi( this );
	
	loadSettings( mPlugin->settings() );
}

SearchAndReplaceSettings::~SearchAndReplaceSettings()
{
}

void SearchAndReplaceSettings::loadSettings( const SearchAndReplace::Settings& settings )
{
	cbReplaceSearchText->setChecked( settings.replaceSearchText );
	cbOnlyWhenNotVisible->setChecked( settings.onlyWhenNotVisible );
	cbOnlyWhenNotRegExp->setChecked( settings.onlyWhenNotRegExp );
	cbOnlyWhenNotEmpty->setChecked( settings.onlyWhenNotEmpty );
}

void SearchAndReplaceSettings::restoreDefault()
{
	loadSettings( SearchAndReplace::Settings() );
}

void SearchAndReplaceSettings::reject()
{
	close();
}

void SearchAndReplaceSettings::accept()
{
	SearchAndReplace::Settings settings;
	
	settings.replaceSearchText = cbReplaceSearchText->isChecked();
	settings.onlyWhenNotVisible = cbOnlyWhenNotVisible->isChecked();
	settings.onlyWhenNotRegExp = cbOnlyWhenNotRegExp->isChecked();
	settings.onlyWhenNotEmpty = cbOnlyWhenNotEmpty->isChecked();
	
	mPlugin->setSettings( settings );
	
	close();
}

void SearchAndReplaceSettings::on_dbbButtons_clicked( QAbstractButton* button )
{
	switch ( dbbButtons->standardButton( button ) )
	{
		case QDialogButtonBox::Help:
			//help();
			break;
		case QDialogButtonBox::RestoreDefaults:
			restoreDefault();
			break;
		case QDialogButtonBox::Ok:
			accept();
			break;
		case QDialogButtonBox::Cancel:
			reject();
			break;
		default:
			break;
	}
}
