#include "pFileDialog.h"

#include <QGridLayout>
#include <QTextCodec>
#include <QLabel>
#include <QComboBox>
#include <QCheckBox>

pFileDialog::pFileDialog( QWidget* parent, const QString& caption, const QString& directory, const QString& filter, bool textCodecEnabled, bool openReadOnlyEnabled )
	: QFileDialog( parent, caption, directory, filter )
{
	setFileMode( QFileDialog::AnyFile );

#if QT_VERSION >= 0x040500
	setOption( QFileDialog::DontUseNativeDialog, true );
#endif
	
	// get grid layout
	glDialog = qobject_cast<QGridLayout*>( layout() );
	
	// assert on gridlayout
	Q_ASSERT( glDialog );
	
	// text codec
	QStringList codecs;
	foreach ( const QByteArray& codec, QTextCodec::availableCodecs() )
	{
		codecs << codec;
	}
	codecs.sort();
	
	mTextCodecEnabled = true;
	
	lCodec = new QLabel( tr( "Codec:" ), this );
	cbCodec = new QComboBox( this );
	cbCodec->addItems( codecs );
	setTextCodec( QTextCodec::codecForLocale()->name() );
	
	glDialog->addWidget( lCodec, 4, 0 );
	glDialog->addWidget( cbCodec, 4, 1 );
	
	// read only
	mOpenReadOnlyEnabled = true;
	
	cbOpenReadOnly = new QCheckBox( tr( "Open in read only." ), this );
	
	glDialog->addWidget( cbOpenReadOnly, 5, 1 );
	
	// configuration
	
	setTextCodecEnabled( textCodecEnabled );
	setOpenReadOnlyEnabled( openReadOnlyEnabled );
}

QString pFileDialog::textCodec() const
{
	return cbCodec->currentText();
}

void pFileDialog::setTextCodec( const QString& codec )
{
	cbCodec->setCurrentIndex( cbCodec->findText( codec ) );
}

bool pFileDialog::textCodecEnabled() const
{
	return mTextCodecEnabled;
}

void pFileDialog::setTextCodecEnabled( bool enabled )
{
	mTextCodecEnabled = enabled;
	lCodec->setEnabled( enabled );
	cbCodec->setEnabled( enabled );
}

bool pFileDialog::openReadOnly() const
{
	return cbOpenReadOnly->isChecked();
}

void pFileDialog::setOpenReadOnly( bool readOnly )
{
	cbOpenReadOnly->setChecked( readOnly );
}

bool pFileDialog::openReadOnlyEnabled() const
{
	return mOpenReadOnlyEnabled;
}

void pFileDialog::setOpenReadOnlyEnabled( bool enabled )
{
	mOpenReadOnlyEnabled = enabled;
	cbOpenReadOnly->setEnabled( enabled );
}

QDir::Filters pFileDialog::filterForMode() const
{
	QDir::Filters filters = filter();
	
	if ( fileMode() == QFileDialog::DirectoryOnly )
	{
		filters |= QDir::Drives | QDir::AllDirs | QDir::Dirs;
		filters &= ~QDir::Files;
	}
	else
	{
		filters |= QDir::Drives | QDir::AllDirs | QDir::Files | QDir::Dirs;
	}
	
	return filters;
}

void pFileDialog::setDialog( pFileDialog* dlg, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, bool enabledOpenReadOnly, QString* selectedFilter, Options options )
{
#if defined( Q_OS_MAC ) && QT_VERSION < 0x040500
	if ( !( options & DontUseSheet ) )
	{
		// that's impossible to have a sheet in a sheet
		QWidget* parent = dlg->parentWidget();
		if ( parent && !parent->windowFlags().testFlag( Qt::Sheet ) )
		{
			dlg->setWindowFlags( dlg->windowFlags() | Qt::Sheet );
		}
	}
#endif
	
	// dialog settings
	dlg->setWindowTitle( caption );
	dlg->setDirectory( dir );
	dlg->setNameFilter( filter );
	dlg->setTextCodecEnabled( enabledTextCodec );
	dlg->setOpenReadOnlyEnabled( enabledOpenReadOnly );
	dlg->setConfirmOverwrite( !( options & DontConfirmOverwrite ) );
	dlg->setResolveSymlinks( !( options & DontResolveSymlinks ) );
	
	// select file if needed )
	if ( !( options & ShowDirsOnly ) && QFileInfo( dir ).isFile() )
	{
		dlg->selectFile( dir );
	}
	
	// select correct filter if needed
	if ( selectedFilter )
	{
		dlg->selectNameFilter( *selectedFilter );
	}
}

void pFileDialog::setOpenFileNameDialog( pFileDialog* dlg, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, bool enabledOpenReadOnly, QString* selectedFilter, Options options )
{
	setDialog( dlg, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options );
	dlg->setFileMode( QFileDialog::ExistingFile );
	dlg->setFilter( dlg->filterForMode() );
	dlg->setAcceptMode( AcceptOpen );
}

void pFileDialog::setOpenFileNamesDialog( pFileDialog* dlg, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, bool enabledOpenReadOnly, QString* selectedFilter, Options options )
{
	setDialog( dlg, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options );
	dlg->setFileMode( QFileDialog::ExistingFiles );
	dlg->setFilter( dlg->filterForMode() );
	dlg->setAcceptMode( AcceptOpen );
}

void pFileDialog::setSaveFileNameDialog( pFileDialog* dlg, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, QString* selectedFilter, Options options )
{
	setDialog( dlg, caption, dir, filter, enabledTextCodec, false, selectedFilter, options );
	dlg->setFileMode( QFileDialog::AnyFile );
	dlg->setFilter( dlg->filterForMode() );
	dlg->setAcceptMode( AcceptSave );
}

pFileDialogResult pFileDialog::getOpenFileName( QWidget* parent, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, bool enabledOpenReadOnly, QString* selectedFilter, Options options )
{
	pFileDialogResult result;
	pFileDialog fd( parent );
	setOpenFileNameDialog( &fd, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options );
	
	if ( fd.exec() == QDialog::Accepted )
	{
		if ( selectedFilter )
		{
			*selectedFilter = fd.selectedFilter();
		}
		
		result[ "filename" ] = fd.selectedFiles().value( 0 );
		result[ "codec" ] = fd.textCodec();
		result[ "openreadonly" ] = fd.openReadOnly();
	}
	
	return result;
}

pFileDialogResult pFileDialog::getOpenFileNames( QWidget* parent, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, bool enabledOpenReadOnly, QString* selectedFilter, Options options )
{
	pFileDialogResult result;
	pFileDialog fd( parent );
	setOpenFileNamesDialog( &fd, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options );
	
	if ( fd.exec() == QDialog::Accepted )
	{
		if ( selectedFilter )
		{
			*selectedFilter = fd.selectedFilter();
		}
		
		result[ "filenames" ] = fd.selectedFiles().value( 0 );
		result[ "codec" ] = fd.textCodec();
		result[ "openreadonly" ] = fd.openReadOnly();
	}
	
	return result;
}

pFileDialogResult pFileDialog::getSaveFileName( QWidget* parent, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, QString* selectedFilter, Options options )
{
	pFileDialogResult result;
	pFileDialog fd( parent );
	setSaveFileNameDialog( &fd, caption, dir, filter, enabledTextCodec, selectedFilter, options );
	
	if ( fd.exec() == QDialog::Accepted )
	{
		if ( selectedFilter )
		{
			*selectedFilter = fd.selectedFilter();
		}
		
		result[ "filename" ] = fd.selectedFiles().value( 0 );
		result[ "codec" ] = fd.textCodec();
		result[ "openreadonly" ] = fd.openReadOnly();
	}
	
	return result;
}
