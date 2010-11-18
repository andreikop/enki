#ifndef XUPADDFILES_H
#define XUPADDFILES_H

#include "ui_XUPAddFiles.h"

class XUPProjectModelProxy;
class XUPProjectModel;
class XUPItem;

class XUPAddFiles : public QWidget, public Ui::XUPAddFiles
{
	Q_OBJECT

public:
	XUPAddFiles( QWidget* parent = 0 );
	virtual ~XUPAddFiles();
	
	void setModel( XUPProjectModel* model );
	XUPProjectModel* model() const;
	
	void setAddToProjectChoice( bool choice );
	bool addToProjectChoice() const;
	
	void setAddToProject( bool add );
	bool addToProject() const;
	
	void setCurrentScope( XUPItem* item );
	XUPItem* currentScope() const;
	
	void setImportExternalFiles( bool import );
	bool importExternalFiles() const;
	
	void setImportExternalFilesPath( const QString& path );
	QString importExternalFilesPath() const;
	
	void setScopeChoiceEnabled( bool enabled );
	void setImportExternalFilesPathEnabled( bool enabled );

protected:
	XUPProjectModelProxy* mProxy;
	XUPProjectModel* mModel;

protected slots:
	void on_tcbScopes_currentChanged( const QModelIndex& index );

signals:
	void currentScopeChanged( XUPItem* scope );
};

#endif // XUPADDFILES_H
