#include "UIXUPFindFiles.h"

#include <QDir>

UIXUPFindFiles::UIXUPFindFiles( const QString& findFile, QWidget* parent )
	: QDialog( parent )
{
	setupUi( this );
	lFindFile->setText( findFile );
}

UIXUPFindFiles::~UIXUPFindFiles()
{
}

void UIXUPFindFiles::setFiles( const QFileInfoList& files, const QString rootPath )
{
	QDir dir( rootPath );
	foreach ( const QFileInfo& fi, files )
	{
		QString text = rootPath.isEmpty() ? fi.fileName() : dir.relativeFilePath( fi.absoluteFilePath() );
		QListWidgetItem* item = new QListWidgetItem( lwFiles );
		item->setText( text );
		item->setToolTip( fi.absoluteFilePath() );
		lwFiles->addItem( item );
	}
	
	lwFiles->setCurrentRow( 0 );
}

void UIXUPFindFiles::on_lwFiles_itemSelectionChanged()
{
	QListWidgetItem* item = lwFiles->selectedItems().value( 0 );
	if ( item )
	{
		lAbsoluteFilePath->setText( item->toolTip() );
	}
}

void UIXUPFindFiles::on_lwFiles_itemActivated( QListWidgetItem* item )
{
	Q_UNUSED( item );
	accept();
}

QString UIXUPFindFiles::selectedFile() const
{
	QListWidgetItem* item = lwFiles->selectedItems().value( 0 );
	if ( item )
	{
		return item->toolTip();
	}
	
	return QString::null;
}

void UIXUPFindFiles::accept()
{
	if ( lwFiles->selectedItems().count() == 1 )
	{
		QDialog::accept();
	}
}
