#include "MkSFileDialog.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "xupmanager/core/XUPProjectItemInfos.h"
#include "pMonkeyStudio.h"
#include "xupmanager/gui/XUPAddFiles.h"
#include "coremanager/MonkeyCore.h"
#include "xupmanager/gui/XUPProjectManager.h"

#include <widgets/pTreeComboBox.h>

#include <QComboBox>

MkSFileDialog::MkSFileDialog( QWidget* parent, const QString& caption, const QString& directory, const QString& filter, bool textCodecEnabled, bool openReadOnlyEnabled )
    : pFileDialog( parent, caption, directory, filter, textCodecEnabled, openReadOnlyEnabled )
{
    mAddFiles = new XUPAddFiles( this );
    glDialog->addWidget( mAddFiles, 6, 0, 1, -1 );
    
    connect( mAddFiles, SIGNAL( currentScopeChanged( XUPItem* ) ), this, SLOT( currentScopeChanged( XUPItem* ) ) );
}

void MkSFileDialog::currentScopeChanged( XUPItem* scope )
{
    if ( scope )
    {
        QString projectPath = QDir( scope->project()->path() ).canonicalPath();
        
        if ( !directory().canonicalPath().startsWith( projectPath ) )
        {
            setDirectory( projectPath );
        }
    }
}

pFileDialogResult MkSFileDialog::getOpenFileName( QWidget* parent, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, bool enabledOpenReadOnly, QString* selectedFilter, Options options )
{
    pFileDialogResult result;
    MkSFileDialog fd( parent );
    setOpenFileNameDialog( &fd, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options );
    fd.setTextCodec( pMonkeyStudio::defaultCodec() );
    fd.mAddFiles->setVisible( false );
    
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

pFileDialogResult MkSFileDialog::getOpenFileNames( QWidget* parent, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, bool enabledOpenReadOnly, QString* selectedFilter, Options options )
{
    pFileDialogResult result;
    MkSFileDialog fd( parent );
    setOpenFileNamesDialog( &fd, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options );
    fd.setTextCodec( pMonkeyStudio::defaultCodec() );
    fd.mAddFiles->setVisible( false );
    
    if ( fd.exec() == QDialog::Accepted )
    {
        if ( selectedFilter )
        {
            *selectedFilter = fd.selectedFilter();
        }
        
        result[ "filenames" ] = fd.selectedFiles();
        result[ "codec" ] = fd.textCodec();
        result[ "openreadonly" ] = fd.openReadOnly();
    }
    
    return result;
}

pFileDialogResult MkSFileDialog::getSaveFileName( QWidget* parent, const QString& caption, const QString& dir, const QString& filter, bool enabledTextCodec, QString* selectedFilter, Options options )
{
    pFileDialogResult result;
    MkSFileDialog fd( parent );
    setSaveFileNameDialog( &fd, caption, dir, filter, enabledTextCodec, selectedFilter, options );
    fd.setTextCodec( pMonkeyStudio::defaultCodec() );
    fd.mAddFiles->setVisible( false );
    
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

pFileDialogResult MkSFileDialog::getOpenProjects( QWidget* parent )
{
    pFileDialogResult result;
    QString caption = tr( "Choose project(s) to open" );
    QString filter = XUPProjectItem::projectInfos()->projectsFilter();
    bool enabledTextCodec = true;
    bool enabledOpenReadOnly = false;
    
    MkSFileDialog fd( parent );
    setOpenFileNamesDialog( &fd, caption, QDir::currentPath() , filter, enabledTextCodec, enabledOpenReadOnly, 0, 0 );
    fd.setTextCodec( pMonkeyStudio::defaultCodec() );
    fd.mAddFiles->setVisible( false );
    
    if ( fd.exec() == QDialog::Accepted )
    {
        result[ "filenames" ] = fd.selectedFiles();
        result[ "codec" ] = fd.textCodec();
        result[ "openreadonly" ] = fd.openReadOnly();
    }
    
    return result;
}

pFileDialogResult MkSFileDialog::getProjectAddFiles( QWidget* parent, bool allowChooseScope )
{
    pFileDialogResult result;
    XUPProjectModel* model = MonkeyCore::projectsManager()->currentProjectModel();
    
    if ( model )
    {
        XUPProjectItem* curProject = MonkeyCore::projectsManager()->currentProject();
        QStringList operators = curProject->projectInfos()->operators( curProject->projectType() );
        QString caption = tr( "Choose file(s) to add to your project" );
        QString filter = XUPProjectItem::projectInfos()->variableSuffixesFilter( curProject->projectType() );
        bool enabledTextCodec = false;
        bool enabledOpenReadOnly = false;
        
        MkSFileDialog fd( parent );
        setOpenFileNamesDialog( &fd, caption, QDir::currentPath(), filter, enabledTextCodec, enabledOpenReadOnly, 0, 0 );
        fd.setTextCodec( pMonkeyStudio::defaultCodec() );
        fd.mAddFiles->setModel( model );
        fd.mAddFiles->setCurrentScope( curProject );
        fd.mAddFiles->setScopeChoiceEnabled( allowChooseScope );
        
        if ( fd.exec() == QDialog::Accepted )
        {
            result[ "filenames" ] = fd.selectedFiles();
            result[ "scope" ] = QVariant::fromValue<XUPItem*>( fd.mAddFiles->currentScope() );
            result[ "import" ] = fd.mAddFiles->importExternalFiles();
            result[ "importpath" ] = fd.mAddFiles->importExternalFilesPath();
            result[ "directory" ] = fd.directory().absolutePath();
        }
    }
    
    return result;
}

pFileDialogResult MkSFileDialog::getNewEditorFile( QWidget* parent )
{
    pFileDialogResult result;
    XUPProjectModel* model = MonkeyCore::projectsManager()->currentProjectModel();
    XUPProjectItem* curProject = MonkeyCore::projectsManager()->currentProject();
    QStringList operators = curProject ? curProject->projectInfos()->operators( curProject->projectType() ) : QStringList();
    QString caption = tr( "New File Name..." );
    QString filter = curProject ? XUPProjectItem::projectInfos()->variableSuffixesFilter( curProject->projectType() ) : pMonkeyStudio::availableFilesFilters();
    bool enabledTextCodec = true;
    
    MkSFileDialog fd( parent );
    setSaveFileNameDialog( &fd, caption, QDir::currentPath(), filter, enabledTextCodec, 0, 0 );
    fd.setTextCodec( pMonkeyStudio::defaultCodec() );
    
    if ( curProject )
    {
        fd.mAddFiles->setModel( model );
        fd.mAddFiles->setAddToProjectChoice( true );
        fd.mAddFiles->setAddToProject( false );
        fd.mAddFiles->setCurrentScope( curProject );
    }
    else
    {
        fd.mAddFiles->setVisible( false );
    }
    
    if ( fd.exec() == QDialog::Accepted )
    {
        result[ "filename" ] = fd.selectedFiles().value( 0 );
        result[ "codec" ] = fd.textCodec();
        
        if ( model )
        {
            result[ "addtoproject" ] = fd.mAddFiles->addToProject();
            result[ "scope" ] = QVariant::fromValue<XUPItem*>( fd.mAddFiles->currentScope() );
        }
    }
    
    return result;
}
