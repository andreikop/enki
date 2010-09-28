#include "XUPAddFiles.h"
#include "xupmanager/core/XUPProjectModelProxy.h"
#include "xupmanager/core/XUPProjectModel.h"
#include "xupmanager/core/XUPItem.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "pMonkeyStudio.h"

XUPAddFiles::XUPAddFiles( QWidget* parent )
    : QWidget( parent )
{
    setupUi( this );
    
    mModel = 0;
    mProxy = new XUPProjectModelProxy( this );
    tcbScopes->setModel( mProxy );
}

XUPAddFiles::~XUPAddFiles()
{
}

void XUPAddFiles::on_tcbScopes_currentChanged( const QModelIndex& index )
{
    Q_UNUSED( index );
    XUPItem* scope = currentScope();
    
    QString curText = cbImport->currentText();
    cbImport->clear();
    
    if ( scope )
    {
        QDir dir( scope->project()->path() );
        
        foreach ( const QFileInfo& fi, pMonkeyStudio::getFolders( dir, QStringList() ) )
        {
            cbImport->addItem( fi.filePath(), dir.relativeFilePath( fi.filePath() ) );
        }
        
        int id = cbImport->findData( curText );
        
        if ( id == -1 )
        {
            cbImport->setEditText( curText );
        }
        else
        {
            cbImport->setCurrentIndex( id );
        }
    }
    
    emit currentScopeChanged( scope );
}

void XUPAddFiles::setModel( XUPProjectModel* model )
{
    if ( mModel != model )
    {
        if ( mModel )
        {
            // disconnect
        }
        
        mModel = model;
        mProxy->setSourceModel( mModel );
        
        if ( mModel )
        {
            // connect
        }
    }
}

XUPProjectModel* XUPAddFiles::model() const
{
    return mModel;
}

void XUPAddFiles::setAddToProjectChoice( bool choice )
{
    if ( choice )
    {
        gbScopes->setCheckable( true );
    }
    else
    {
        gbScopes->setCheckable( false );
    }
}

bool XUPAddFiles::addToProjectChoice() const
{
    return gbScopes->isCheckable();
}

void XUPAddFiles::setAddToProject( bool add )
{
    setAddToProjectChoice( true );
    gbScopes->setChecked( add );
}

bool XUPAddFiles::addToProject() const
{
    if ( gbScopes->isCheckable() )
    {
        return gbScopes->isChecked();
    }
    
    return true;
}

void XUPAddFiles::setCurrentScope( XUPItem* item )
{
    QModelIndex index = item->index();
    index = mProxy->mapFromSource( index );
    tcbScopes->setCurrentIndex( index );
}

XUPItem* XUPAddFiles::currentScope() const
{
    QModelIndex index = tcbScopes->currentIndex();
    index = mProxy->mapToSource( index );
    return mModel->itemFromIndex( index );
}

void XUPAddFiles::setImportExternalFiles( bool import )
{
    gbImport->setChecked( import );
}

bool XUPAddFiles::importExternalFiles() const
{
    return gbImport->isChecked();
}

void XUPAddFiles::setImportExternalFilesPath( const QString& path )
{
    int id = cbImport->findData( path );
    
    if ( id == -1 )
    {
        cbImport->addItem( path, path );
        id = cbImport->findData( path );
    }
    
    cbImport->setCurrentIndex( id );
}

QString XUPAddFiles::importExternalFilesPath() const
{
    const int id = cbImport->currentIndex();
    
    if ( id == -1 )
    {
        return cbImport->currentText();
    }
    
    return cbImport->itemData( id ).toString();
}

void XUPAddFiles::setScopeChoiceEnabled( bool enabled )
{
    gbScopes->setEnabled( enabled );
}

void XUPAddFiles::setImportExternalFilesPathEnabled( bool enabled )
{
    gbImport->setEnabled( enabled );
}
