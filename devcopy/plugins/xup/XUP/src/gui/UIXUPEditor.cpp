#include "UIXUPEditor.h"

#include <xupmanager/core/XUPProjectItem.h>
#include <shared/MkSFileDialog.h>
#include <pMonkeyStudio.h>
#include <coremanager/MonkeyCore.h>
#include <pluginsmanager/PluginsManager.h>
#include <xupmanager/core/XUPProjectItemHelper.h>

#include <QInputDialog>
#include <QMessageBox>
#include <QDebug>

UIXUPEditor::UIXUPEditor( XUPProjectItem* project, QWidget* parent )
    : QDialog( parent )
{
    // init dialog
    setupUi( this );
    
    // set dialog infos
    setWindowIcon( project->displayIcon() );
    setWindowTitle( tr( "%1 Project Editor - %2" ).arg( PLUGIN_NAME ).arg( project->displayText() ) );
    
    // set size hint for page item ( left panel )
    for ( int i = 0; i < lwPages->count(); i++ )
    {
        QListWidgetItem* item = lwPages->item( i );
        item->setSizeHint( QSize( 154, 40 ) );
    }
    
    // does not show variable editor by defaultAction
    setVariableEditorVisible( false );
    
    // commands
    const BasePluginTypeList types = BasePluginTypeList() << BasePlugin::iBuilder << BasePlugin::iDebugger << BasePlugin::iInterpreter;
    const QStringList parsers = MonkeyCore::consoleManager()->parsersName();
    
    // commands editor
    ceEditor->setCommandTypes( types );
    ceEditor->setParsers( parsers );
    
    // init project settings dialog
    init( project );
    
    // set correct page
    lwPages->setCurrentRow( 0 );
}

UIXUPEditor::~UIXUPEditor()
{
}

void UIXUPEditor::setVariableEditorVisible( bool visible )
{
    lwPages->item( 2 )->setHidden( !visible );
}

bool UIXUPEditor::isVariableEditorVisible() const
{
    return !lwPages->item( 2 )->isHidden();
}

void UIXUPEditor::updateMainFileComboBox( const QString& selectFile )
{
    cbMainFile->clear();
    
    const QStringList sources = mProject->sourceFiles();
    QMap<QString, QString> files;
    
    foreach ( const QString& file, sources )
    {
        const QString fileName = mProject->relativeFilePath( file );
        
        files[ fileName.toLower() ] = fileName;
    }
    
    cbMainFile->addItems( files.values() );
    const int index = cbMainFile->findText( mProject->relativeFilePath( selectFile ) );
    cbMainFile->setCurrentIndex( index );
}

void UIXUPEditor::updateProjectFiles()
{
    int pType = mProject->projectType();
    QMap<QString, QString>& values = veEditor->values();
    
    foreach ( const QString& variable, veEditor->fileVariables() )
    {
        QTreeWidgetItem* topItem = mProjectFilesItems.value( variable );
        QStringList files = mProject->splitMultiLineValue( values[ variable ] );
        
        if ( topItem && files.isEmpty() )
        {
            delete mProjectFilesItems.take( variable );
        }
        else if ( !files.isEmpty() )
        {
            if ( !topItem )
            {
                topItem = new QTreeWidgetItem( twFiles, QTreeWidgetItem::UserType +1 );
                topItem->setText( 0, mProject->projectInfos()->displayText( pType, variable ) );
                topItem->setIcon( 0, mProject->projectInfos()->displayIcon( pType, variable ) );
                mProjectFilesItems[ variable ] = topItem;
            }
            
            for ( int i = 0; i < topItem->childCount(); i++ )
            {
                QTreeWidgetItem* item = topItem->child( i );
                QString fn = item->data( 0, Qt::UserRole ).toString();
                
                if ( files.contains( fn ) )
                {
                    files.removeAll( fn );
                }
            }
            
            foreach ( const QString& fn, files )
            {
                QTreeWidgetItem* item = new QTreeWidgetItem( topItem, QTreeWidgetItem::UserType );
                item->setText( 0, fn );
                item->setData( 0, Qt::UserRole, fn );
                item->setIcon( 0, mProject->projectInfos()->displayIcon( XUPProjectItem::XUPProject, "FILES" ) );
            }
        }
    }
}

void UIXUPEditor::init( XUPProjectItem* project )
{
    mProject = project;
    const XUPDynamicFolderSettings folder = XUPProjectItemHelper::projectDynamicFolderSettings( mProject );

    leProjectName->setText( mProject->attribute( "name" ) );
    gbDynamicFolder->setChecked( folder.Active );
    leDynamicFolder->setText( folder.AbsolutePath );
    gbDynamicFilesPatterns->setValues( folder.FilesPatterns );
    updateMainFileComboBox( mProject->projectSettingsValue( "MAIN_FILE" ) );
    veEditor->init( mProject );
    updateProjectFiles();
    ceEditor->setCommands( XUPProjectItemHelper::projectCommands( mProject ) );
    ceEditor->setCurrentType( ceEditor->commandTypes().first() );
}

void UIXUPEditor::on_tbDynamicFolder_clicked()
{
    QString path = leDynamicFolder->text();
    path = QFileDialog::getExistingDirectory( this, tr( "Select the folder to monitor" ), path );
    
    if ( path.isEmpty() )
    {
        return;
    }
    
    leDynamicFolder->setText( path );
}

void UIXUPEditor::on_tbAddFile_clicked()
{
    pFileDialogResult result = MkSFileDialog::getProjectAddFiles( window(), false );
    
    if ( !result.isEmpty() )
    {
        QStringList files = result[ "filenames" ].toStringList();
        QMap<QString, QString>& values = veEditor->values();
        
        // import files if needed
        if ( result[ "import" ].toBool() )
        {
            const QString projectPath = mProject->path();
            const QString importPath = result[ "importpath" ].toString();
            const QString importRootPath = result[ "directory" ].toString();
            QDir dir( importRootPath );
            
            for ( int i = 0; i < files.count(); i++ )
            {
                if ( !files.at( i ).startsWith( projectPath ) )
                {
                    QString fn = QString( files.at( i ) ).remove( importRootPath ).replace( "\\", "/" );
                    fn = QDir::cleanPath( QString( "%1/%2/%3" ).arg( projectPath ).arg( importPath ).arg( fn ) );
                    
                    if ( dir.mkpath( QFileInfo( fn ).absolutePath() ) && QFile::copy( files.at( i ), fn ) )
                    {
                        files[ i ] = fn;
                    }
                }
            }
        }
        
        // add files
        foreach ( QString fn, files )
        {
            fn = mProject->relativeFilePath( fn );
            
            if ( fn.contains( " " ) )
            {
                fn.prepend( '"' ).append( '"' );
            }
            
            QString variable = mProject->projectInfos()->variableNameForFileName( mProject->projectType(), fn );
            
            if ( !values[ variable ].contains( fn ) )
            {
                values[ variable ] += " " +fn;
            }
            
        }
        
        updateProjectFiles();
    }
}

void UIXUPEditor::on_tbEditFile_clicked()
{
    QTreeWidgetItem* item = twFiles->selectedItems().value( 0 );
    
    if ( item && twFiles->indexOfTopLevelItem( item ) == -1 )
    {
        bool ok;
        QString oldValue = item->data( 0, Qt::UserRole ).toString();
        QString fn = QInputDialog::getText( this, tr( "Edit file name" ), tr( "Type a new name for this file" ), QLineEdit::Normal, oldValue, &ok );
        
        if ( ok && !fn.isEmpty() )
        {
            QString variable = mProject->projectInfos()->variableNameForFileName( mProject->projectType(), fn );
            QMap<QString, QString>& values = veEditor->values();
            
            item->setText( 0, fn );
            item->setData( 0, Qt::UserRole, fn );
            
            values[ variable ].remove( oldValue ).append( " " +fn );
            
            updateProjectFiles();
        }
    }
}

void UIXUPEditor::on_tbRemoveFile_clicked()
{
    QList<QTreeWidgetItem*> selectedItems = twFiles->selectedItems();
    
    if ( selectedItems.count() > 0 )
    {
        if ( QMessageBox::question( this, tr( "Remove files" ), tr( "Are you sure you want to remove all the selected files ?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::No ) == QMessageBox::No )
        {
            return;
        }
        
        QMap<QString, QString>& values = veEditor->values();
        
        foreach ( QTreeWidgetItem* item, selectedItems )
        {
            if ( item->type() == QTreeWidgetItem::UserType +1 )
            {
                continue;
            }
            
            const QString variable = mProjectFilesItems.key( item->parent() );
            const QString fn = item->data( 0, Qt::UserRole ).toString();
            
            values[ variable ].remove( fn );
            delete item;
        }
        
        if ( !selectedItems.isEmpty() )
        {
            updateProjectFiles();
        }
    }
}

void UIXUPEditor::accept()
{
    XUPDynamicFolderSettings folder;
    folder.Active = gbDynamicFolder->isChecked();
    folder.AbsolutePath = leDynamicFolder->text();
    folder.FilesPatterns = gbDynamicFilesPatterns->values();
    
    ceEditor->finalize();
    veEditor->finalize();
    mProject->setAttribute( "name", leProjectName->text() );
    mProject->setProjectSettingsValue( "MAIN_FILE", cbMainFile->currentText() );
    XUPProjectItemHelper::setProjectDynamicFolderSettings( mProject, folder );
    XUPProjectItemHelper::setProjectCommands( mProject, ceEditor->commands() );
    
    // close dialog
    QDialog::accept();
}
