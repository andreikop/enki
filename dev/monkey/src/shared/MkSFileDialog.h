#ifndef MKSFILEDIALOG_H
#define MKSFILEDIALOG_H

#include "widgets/pFileDialog.h"

class XUPAddFiles;
class XUPItem;

class Q_MONKEY_EXPORT MkSFileDialog : public pFileDialog
{
	Q_OBJECT
	
public:
	MkSFileDialog( QWidget* parent = 0, const QString& caption = QString(), const QString& directory = QString(), const QString& filter = QString(), bool textCodecEnabled = true, bool openReadOnlyEnabled = false );
	
	static pFileDialogResult getOpenFileName( QWidget* parent = 0, const QString& caption = QString(), const QString& dir = QString(), const QString& filter = QString(), bool enabledTextCodec = true, bool enabledOpenReadOnly = true, QString* selectedFilter = 0, Options options = 0 );
	static pFileDialogResult getOpenFileNames( QWidget* parent = 0, const QString& caption = QString(), const QString& dir = QString(), const QString& filter = QString(), bool enabledTextCodec = true, bool enabledOpenReadOnly = true, QString* selectedFilter = 0, Options options = 0 );
	static pFileDialogResult getSaveFileName( QWidget* parent = 0, const QString& caption = QString(), const QString& dir = QString(), const QString& filter = QString(), bool enabledTextCodec = true, QString* selectedFilter = 0, Options options = 0 );
	
	static pFileDialogResult getOpenProjects( QWidget* parent = 0 );
	static pFileDialogResult getProjectAddFiles( QWidget* parent = 0, bool allowChooseScope = true );
	static pFileDialogResult getNewEditorFile( QWidget* parent = 0 );

protected:
	XUPAddFiles* mAddFiles;

protected slots:
	void currentScopeChanged( XUPItem* scope );
};

#endif // MKSFILEDIALOG_H
