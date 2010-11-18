#ifndef UIXUPFINDFILES_H
#define UIXUPFINDFILES_H

#include <objects/MonkeyExport.h>

#include "ui_UIXUPFindFiles.h"

#include <QFileInfo>

class Q_MONKEY_EXPORT UIXUPFindFiles : public QDialog, public Ui::UIXUPFindFiles
{
	Q_OBJECT

public:
	UIXUPFindFiles( const QString& findFile, QWidget* parent = 0 );
	virtual ~UIXUPFindFiles();
	
	void setFiles( const QFileInfoList& files, const QString rootPath = QString::null );
	QString selectedFile() const;

protected slots:
	void on_lwFiles_itemSelectionChanged();
	void on_lwFiles_itemActivated( QListWidgetItem* item );
	void accept();
};

#endif // UIXUPFINDFILES_H
