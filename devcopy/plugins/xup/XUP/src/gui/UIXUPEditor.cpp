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

UIXUPEditor.UIXUPEditor( XUPProjectItem* project, parent )
    : QDialog( parent )
    # init dialog
    setupUi( self )
    
    # set dialog infos
    setWindowIcon( project.displayIcon() )
    setWindowTitle( tr( "%1 Project Editor - %2" ).arg( PLUGIN_NAME ).arg( project.displayText() ) )
    
    # set size hint for page item ( left panel )
    for ( i = 0; i < lwPages.count(); i++ )
        item = lwPages.item( i )
        item.setSizeHint( QSize( 154, 40 ) )

    
    # does not show variable editor by defaultAction
    setVariableEditorVisible( False )
    
    # commands
     types = BasePluginTypeList() << BasePlugin.iBuilder << BasePlugin.iDebugger << BasePlugin.iInterpreter
     parsers = MonkeyCore.consoleManager().parsersName()
    
    # commands editor
    ceEditor.setCommandTypes( types )
    ceEditor.setParsers( parsers )
    
    # init project settings dialog
    init( project )
    
    # set correct page
    lwPages.setCurrentRow( 0 )


UIXUPEditor.~UIXUPEditor()


def setVariableEditorVisible(self, visible ):
    lwPages.item( 2 ).setHidden( not visible )


def isVariableEditorVisible(self):
    return not lwPages.item( 2 ).isHidden()


def updateMainFileComboBox(self, selectFile ):
    cbMainFile.clear()
    
     sources = mProject.sourceFiles()
    QMap<QString, files
    
    for file in sources:
         fileName = mProject.relativeFilePath( file )
        
        files[ fileName.toLower() ] = fileName

    
    cbMainFile.addItems( files.values() )
     index = cbMainFile.findText( mProject.relativeFilePath( selectFile ) )
    cbMainFile.setCurrentIndex( index )


def updateProjectFiles(self):
    pType = mProject.projectType()
    QMap<QString, values = veEditor.values()
    
    for variable in veEditor.fileVariables():
        topItem = mProjectFilesItems.value( variable )
        files = mProject.splitMultiLineValue( values[ variable ] )
        
        if  topItem and files.isEmpty() :
            delete mProjectFilesItems.take( variable )

        elif  not files.isEmpty() :
            if  not topItem :
                topItem = QTreeWidgetItem( twFiles, QTreeWidgetItem.UserType +1 )
                topItem.setText( 0, mProject.projectInfos().displayText( pType, variable ) )
                topItem.setIcon( 0, mProject.projectInfos().displayIcon( pType, variable ) )
                mProjectFilesItems[ variable ] = topItem

            
            for ( i = 0; i < topItem.childCount(); i++ )
                item = topItem.child( i )
                fn = item.data( 0, Qt.UserRole ).toString()
                
                if  files.contains( fn ) :
                    files.removeAll( fn )


            
            for fn in files:
                item = QTreeWidgetItem( topItem, QTreeWidgetItem.UserType )
                item.setText( 0, fn )
                item.setData( 0, Qt.UserRole, fn )
                item.setIcon( 0, mProject.projectInfos().displayIcon( XUPProjectItem.XUPProject, "FILES" ) )





def init(self, project ):
    mProject = project
     folder = XUPProjectItemHelper.projectDynamicFolderSettings( mProject )

    leProjectName.setText( mProject.attribute( "name" ) )
    gbDynamicFolder.setChecked( folder.Active )
    leDynamicFolder.setText( folder.AbsolutePath )
    gbDynamicFilesPatterns.setValues( folder.FilesPatterns )
    updateMainFileComboBox( mProject.projectSettingsValue( "MAIN_FILE" ) )
    veEditor.init( mProject )
    updateProjectFiles()
    ceEditor.setCommands( XUPProjectItemHelper.projectCommands( mProject ) )
    ceEditor.setCurrentType( ceEditor.commandTypes().first() )


def on_tbDynamicFolder_clicked(self):
    path = leDynamicFolder.text()
    path = QFileDialog.getExistingDirectory( self, tr( "Select the folder to monitor" ), path )
    
    if  path.isEmpty() :
        return

    
    leDynamicFolder.setText( path )


def on_tbAddFile_clicked(self):
    result = MkSFileDialog.getProjectAddFiles( window(), False )
    
    if  not result.isEmpty() :
        files = result[ "filenames" ].toStringList()
        QMap<QString, values = veEditor.values()
        
        # import files if needed
        if  result[ "import" ].toBool() :
             projectPath = mProject.path()
             importPath = result[ "importpath" ].toString()
             importRootPath = result[ "directory" ].toString()
            QDir dir( importRootPath )
            
            for ( i = 0; i < files.count(); i++ )
                if  not files.at( i ).startsWith( projectPath ) :
                    fn = QString( files.at( i ) ).remove( importRootPath ).replace( "\\", "/" )
                    fn = QDir.cleanPath( QString( "%1/%2/%3" ).arg( projectPath ).arg( importPath ).arg( fn ) )
                    
                    if  dir.mkpath( QFileInfo( fn ).absolutePath() ) and QFile.copy( files.at( i ), fn ) :
                        files[ i ] = fn




        
        # add files
        for fn in files:
            fn = mProject.relativeFilePath( fn )
            
            if  fn.contains( " " ) :
                fn.prepend( '"' ).append( '"' )

            
            variable = mProject.projectInfos().variableNameForFileName( mProject.projectType(), fn )
            
            if  not values[ variable ].contains( fn ) :
                values[ variable ] += " " +fn

            

        
        updateProjectFiles()



def on_tbEditFile_clicked(self):
    item = twFiles.selectedItems().value( 0 )
    
    if  item and twFiles.indexOfTopLevelItem( item ) == -1 :
        bool ok
        oldValue = item.data( 0, Qt.UserRole ).toString()
        fn = QInputDialog.getText( self, tr( "Edit file name" ), tr( "Type a name for self file" ), QLineEdit.Normal, oldValue, &ok )
        
        if  ok and not fn.isEmpty() :
            variable = mProject.projectInfos().variableNameForFileName( mProject.projectType(), fn )
            QMap<QString, values = veEditor.values()
            
            item.setText( 0, fn )
            item.setData( 0, Qt.UserRole, fn )
            
            values[ variable ].remove( oldValue ).append( " " +fn )
            
            updateProjectFiles()




def on_tbRemoveFile_clicked(self):
    QList<QTreeWidgetItem*> selectedItems = twFiles.selectedItems()
    
    if  selectedItems.count() > 0 :
        if  QMessageBox.question( self, tr( "Remove files" ), tr( "Are you sure you want to remove all the selected files ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.No :
            return

        
        QMap<QString, values = veEditor.values()
        
        for item in selectedItems:
            if  item.type() == QTreeWidgetItem.UserType +1 :
                continue

            
             variable = mProjectFilesItems.key( item.parent() )
             fn = item.data( 0, Qt.UserRole ).toString()
            
            values[ variable ].remove( fn )
            delete item

        
        if  not selectedItems.isEmpty() :
            updateProjectFiles()




def accept(self):
    XUPDynamicFolderSettings folder
    folder.Active = gbDynamicFolder.isChecked()
    folder.AbsolutePath = leDynamicFolder.text()
    folder.FilesPatterns = gbDynamicFilesPatterns.values()
    
    ceEditor.finalize()
    veEditor.finalize()
    mProject.setAttribute( "name", leProjectName.text() )
    mProject.setProjectSettingsValue( "MAIN_FILE", cbMainFile.currentText() )
    XUPProjectItemHelper.setProjectDynamicFolderSettings( mProject, folder )
    XUPProjectItemHelper.setProjectCommands( mProject, ceEditor.commands() )
    
    # close dialog
    QDialog.accept()

