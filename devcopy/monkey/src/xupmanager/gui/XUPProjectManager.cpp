#include "XUPProjectManager.h"
#include "UIXUPFindFiles.h"
#include "xupmanager/core/XUPProjectModel.h"
#include "xupmanager/core/XUPFilteredProjectModel.h"
#include "shared/MkSFileDialog.h"
#include "pMonkeyStudio.h"
#include "coremanager/MonkeyCore.h"
#include "pluginsmanager/PluginsManager.h"
#include "workspace/pWorkspace.h"
#include "pluginsmanager/XUPPlugin.h"
#include "templatesmanager/ui/UITemplatesWizard.h"
#include "recentsmanager/pRecentsManager.h"

#include <widgets/pDockWidgetTitleBar.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <widgets/pMenuBar.h>
#include <objects/pIconManager.h>

#include <QTextCodec>
#include <QMenu>
#include <QInputDialog>
#include <QMessageBox>
#include <QFileSystemWatcher>
#include <QDebug>

XUPProjectManager.XUPProjectManager( QWidget* parent )
    : pDockWidget( parent )
    setupUi( self )
    setActionsManager( MonkeyCore.actionsManager() )
    
    # register generic xup project format
    pItem = XUPProjectItem()
    pItem.registerProjectType()
    
    titleBar().addAction( action( atNew ), 0 )
    titleBar().addAction( action( atOpen ), 1 )
    titleBar().addAction( action( atClose ), 2 )
    titleBar().addAction( action( atCloseAll ), 3 )
    titleBar().addAction( action( atEdit ), 4 )
    titleBar().addAction( action( atAddFiles ), 5 )
    titleBar().addAction( action( atRemoveFiles ), 6 )
    titleBar().addSeparator( 7 )
    
    mFilteredModel = XUPFilteredProjectModel( tvFiltered )
    tvFiltered.setModel( mFilteredModel )
    
    tvFiltered.selectionModel().currentChanged.connect(self.tvFiltered_currentChanged)
    tvFiltered.customContextMenuRequested.connect(self.projectCustomContextMenuRequested)
    
    pMonkeyStudio.showMacFocusRect( wCentral, False, True )
    pMonkeyStudio.setMacSmallSize( wCentral, True, True )
    setCurrentProject( 0, 0 )


XUPProjectManager.~XUPProjectManager()
    delete XUPProjectItem.projectInfos()


def on_cbProjects_currentIndexChanged(self, id ):
    model = cbProjects.itemData( id ).value<XUPProjectModel*>()
    project = model ? model.mRootProject : 0
    setCurrentProject( project, currentProject() )


def tvFiltered_currentChanged(self, current, previous ):
    curItem = mFilteredModel.mapToSource( current )
    preItem = mFilteredModel.mapToSource( previous )
    curProject = curItem ? curItem.project() : 0
    preProject = preItem ? preItem.project() : 0
    
    if  not previous.isValid() :
        preProject = curProject.topLevelProject()

    
    setCurrentProject( curProject, preProject )


def on_tvFiltered_activated(self, index ):
    item = mFilteredModel.mapToSource( index )
    if  item :
        if  item.type() == XUPItem.Project :
            projectDoubleClicked.emit( item.project() )

        elif  item.type() == XUPItem.File :
            project = item.project()
            rootIncludeProject = project.rootIncludeProject()
            fn = rootIncludeProject.filePath( item.cacheValue( "content" ) )
            
            if  not QFile.exists( fn ) :
                findFile = item.attribute( "content" ).remove( '"' )
                files = rootIncludeProject.findFile( findFile )
                switch ( files.count() )
                    case 0:
                        fn.clear()
                        break
                    case 1:
                        fn = files.at( 0 ).absoluteFilePath()
                        break
                    default:
                        UIXUPFindFiles dlg( findFile, self )
                        dlg.setFiles( files, rootIncludeProject.path() )
                        fn.clear()
                        if  dlg.exec() == QDialog.Accepted :
                            fn = dlg.selectedFile()

                        break



            
            if  QFile.exists( fn ) :
                 codec = project.temporaryValue( "codec" ).toString()
                fileDoubleClicked.emit( project, fn, codec )
                fileDoubleClicked.emit( fn, codec )





def on_tvFiltered_customContextMenuRequested(self, pos ):
    if  currentProject() :
        # get menubar
        mb = MonkeyCore.menuBar()
        QMenu menu
        
        # add menu commands
        menu.addActions( mb.menu( "mProject" ).actions() )
        menu.addSeparator()
        menu.addActions( mb.menu( "mBuilder" ).actions() )
        menu.addSeparator()
        menu.addActions( mb.menu( "mDebugger" ).actions() )
        menu.addSeparator()
        menu.addActions( mb.menu( "mInterpreter" ).actions() )
        
        # show menu
        menu.exec( tvFiltered.mapToGlobal( pos ) )



def action(self, type ):
    if  mActions.contains( type ) :
        return mActions[ type ]

    
    action = 0
    switch ( type )
        case XUPProjectManager.atNew:
            action = QAction( pIconManager.icon( "new.png", ":/project" ), tr( "New project..." ), self )
            mActionsManager.setDefaultShortcut( action, tr( "Ctrl+Shift+N" ) )
            action.triggered.connect(self.newProject)
            break
        case XUPProjectManager.atOpen:
            action = QAction( pIconManager.icon( "open.png", ":/project" ), tr( "Open project..." ), self )
            mActionsManager.setDefaultShortcut( action, tr( "Ctrl+Shift+O" ) )
            action.triggered.connect(self.openProject)
            break
        case XUPProjectManager.atClose:
            action = QAction( pIconManager.icon( "close.png", ":/project" ), tr( "Close current project" ), self )
            action.triggered.connect(self.closeProject)
            break
        case XUPProjectManager.atCloseAll:
            action = QAction( pIconManager.icon( "closeall.png", ":/project" ), tr( "Close all projects" ), self )
            action.triggered.connect(self.closeAllProjects)
            break
        case XUPProjectManager.atEdit:
            action = QAction( pIconManager.icon( "settings.png", ":/project" ), tr( "Edit current project..." ), self )
            action.triggered.connect(self.editProject)
            break
        case XUPProjectManager.atAddFiles:
            action = QAction( pIconManager.icon( "add.png", ":/project" ), tr( "Add existing files to current project..." ), self )
            action.triggered.connect(self.addFiles)
            break
        case XUPProjectManager.atRemoveFiles:
            action = QAction( pIconManager.icon( "remove.png", ":/project" ), tr( "Remove files from current project..." ), self )
            action.triggered.connect(self.removeFiles)
            break

    
    if  action :
        action.setToolTip( action.text() )
        action.setStatusTip( action.text() )
        mActions[ type ] = action

    
    return action


def newProject(self):
    UITemplatesWizard wizard( self )
    wizard.setType( "Projects" )
    wizard.exec()


def openProject(self, fileName, codec ):
    # check that project is not yet open
    for project in topLevelProjects():
        if  pMonkeyStudio.isSameFile( project.fileName(), fileName ) :
            setCurrentProject( project, currentProject() )
            return True


    
    QFileInfo fi( fileName )
    
    if  fi.exists() and fi.isFile() :
        model = XUPProjectModel( self )
        if  model.open( fileName, codec ) :
            # append file to recents project
            MonkeyCore.recentsManager().addRecentProject( fileName )
            
            model.registerWithFileWatcher( MonkeyCore.workspace().fileWatcher() )
            
            id = cbProjects.count()
            cbProjects.addItem( model.headerData( 0, Qt.Horizontal, Qt.DisplayRole ).toString(), QVariant.fromValue<XUPProjectModel*>( model ) )
            cbProjects.setItemIcon( id, model.headerData( 0, Qt.Horizontal, Qt.DecorationRole ).value<QIcon>() )
            setCurrentProject( model.rootProject(), currentProject() )
            projectOpened.emit( currentProject() )
            
            return True

        else:
            # remove from recents
            MonkeyCore.recentsManager().removeRecentProject( fileName )
            # inform user about error
            MonkeyCore.messageManager().appendMessage( tr( "An error occur while opening project '%1': %2" ).arg( fileName ).arg( model.lastError() ) )
            # free
            delete model


    
    return False


def openProject(self):
    result = MkSFileDialog.getOpenProjects( window() )
    
     files = result[ "filenames" ].toStringList()
    if  not files.isEmpty() :
         codec = result[ "codec" ].toString()
        for file in files:
            if  not openProject( file, codec ) :
                return False


        
        return True

    
    return False


def closeProject(self):
    curModel = currentProjectModel()
    
    if  curModel :
        preProject = currentProject()
        
        blocked = cbProjects.blockSignals( True )
        id = cbProjects.findData( QVariant.fromValue<XUPProjectModel*>( curModel ) )
        cbProjects.removeItem( id )
        model = cbProjects.itemData( cbProjects.currentIndex() ).value<XUPProjectModel*>()
        setCurrentProjectModel( model )
        cbProjects.blockSignals( blocked )
        
        curProject = currentProject()
        
        setCurrentProject( curProject, preProject )
        
        projectAboutToClose.emit( preProject )
        
        curModel.unregisterWithFileWatcher( MonkeyCore.workspace().fileWatcher() )
        curModel.close()
        delete curModel



def closeAllProjects(self):
    while ( cbProjects.count() > 0 )
        closeProject()



def editProject(self):
    project = currentProject()
    
    if  not project :
        return

    
    topLevelProject = project.topLevelProject()
    
    # get plugin name that can manage self project
     pluginName = topLevelProject.projectSettingsValue( "EDITOR" )
    
    if  pluginName.isEmpty() or not MonkeyCore.pluginsManager().plugins<XUPPlugin*>( PluginsManager.stAll, pluginName ).value( 0 ) :
        # get xup plugins
        QHash<QString, plugins
        
        for plugin in MonkeyCore.pluginsManager(:.plugins<XUPPlugin*>( PluginsManager.stAll ) )
            plugins[ plugin.infos().Caption ] = plugin

    
        bool ok
         caption = QInputDialog.getItem( window(), tr( "Choose an editor plugin..." ), tr( "Your project is not yet editable, select a correct project settings plugin" ), plugins.keys(), 0, False, &ok )
        
        if  ok and not caption.isEmpty() :
            topLevelProject.setProjectSettingsValue( "EDITOR", plugins[ caption ].infos().Name )


    
    # edit project settings
    if  topLevelProject.projectSettingsValue( "EDITOR" ).isEmpty() :
        QMessageBox.warning( QApplication.activeWindow(), tr( "Warning..." ), tr( "The project can't be edited because there is no associate project settings plugin." ) )
        return

    
    plugin = MonkeyCore.pluginsManager().plugins<XUPPlugin*>( PluginsManager.stAll, topLevelProject.projectSettingsValue( "EDITOR" ) ).value( 0 )
    
    if  plugin :
        model = currentProjectModel()
        watcher = MonkeyCore.workspace().fileWatcher()
        
        model.unregisterWithFileWatcher( watcher, project )
        
        # edit project and save it if needed
        if  plugin.editProject( project ) :
            if  project.save() :
                # need save topLevelProject ( for XUPProejctSettings scope  )
                if  not topLevelProject.save() :
                    MonkeyCore.messageManager().appendMessage( tr( "An error occur while saving project '%1': %2" ).arg( topLevelProject.fileName() ).arg( topLevelProject.lastError() ) )


            else:
                MonkeyCore.messageManager().appendMessage( tr( "An error occur while saving project '%1': %2" ).arg( project.fileName() ).arg( project.lastError() ) )

            
            # rebuild cache
            project.rebuildCache()
            topLevelProject.rebuildCache()
            
            # update menu actions
            project.uninstallCommands()
            project.installCommands()

        
        model.registerWithFileWatcher( watcher, project )



def addFilesToScope(self, scope, allFiles, ope ):
    files = allFiles
    project = scope.project()
    rootIncludeProject = project.rootIncludeProject()
     mVariableSuffixes = project.projectInfos().variableSuffixes( project.projectType() )
    QMap<QString, variablesOperator; # variableName, operator
    QMap<QString, suffixeVariables; # suffixe, variable
    
    # self map allow to know if a suffixe can be handled by more than one variable
    for pair in mVariableSuffixes:
        for suffixe in pair.second:
            suffixe = suffixe.toLower()
            
            if  not suffixeVariables[ suffixe ].contains( pair.first ) :
                suffixeVariables[ suffixe ] << pair.first



    
    for file in files:
        for suffixe in suffixeVariables.keys():
            if  QDir.match( suffixe, file ) :
                 variablesName = suffixeVariables[ suffixe ]
            
                QString variableName
                if  variablesName.count() > 1 :
                    bool ok
                    variableName = QInputDialog.getItem( QApplication.activeWindow(), tr( "Choose variable..." ), tr( "More than one variable can handle self file,\nplease select the variable you want to use for self file :\n%1" ).arg( QFileInfo( file ).fileName() ), variablesName, 0, False, &ok )
                    
                    if  not ok :
                        variableName.clear()


                else:
                    variableName = variablesName.at( 0 )

                
                if  variableName.isEmpty() :
                    variableName = "OTHER_FILES"

                
                variables = project.getVariables( scope, variableName, 0, False )
                
                foundFile = False
                usedVariable = 0
                op = ope.isEmpty() ? variablesOperator[ variableName ] : ope
                
                if  op.isEmpty() :
                    op = checkForBestAddOperator( variables )

                
                for variable in variables:
                    if  variable.attribute( "operator", "=" ) != op :
                        continue

                    
                    usedVariable = variable
                    
                    for child in variable.childrenList():
                        if  child.type() != XUPItem.File :
                            continue

                        
                         fn = rootIncludeProject.filePath( child.cacheValue( "content" ) )
                        
                        if  fn == file :
                            foundFile = True
                            break


                    
                    if  foundFile :
                        break


                
                if  foundFile :
                    break

                
                if  not usedVariable :
                    usedVariable = scope.addChild( XUPItem.Variable )
                    usedVariable.setAttribute( "name", variableName )
                    usedVariable.setAttribute( "operator", op )
                    variables << usedVariable

                
                usedVariable.setAttribute( "multiline", "True" )
                
                value = usedVariable.addChild( XUPItem.File )
                value.setAttribute( "content", project.relativeFilePath( file ) )
                
                break



    
    # rebuild cache
    project.rebuildCache()
    project.topLevelProject().rebuildCache()
    
    # save project
    if  not project.save() :
        MonkeyCore.messageManager().appendMessage( tr( "An error occur while saving project '%1': %2" ).arg( project.fileName() ).arg( project.lastError() ) )



def checkForBestAddOperator(self, variables ):
    haveSet = False
    haveAdd = False
    haveAddIfNotExists = False
    
    for variable in variables:
         op = variable.attribute( "operator", "=" )
        
        if  op == "*=" :
            haveAddIfNotExists = True

        elif  op == "+=" :
            haveAdd = True

        elif  op == "=" :
            haveSet = True


    
    if  haveAddIfNotExists :
        return "*="

    
    if  haveAdd :
        return "+="

    
    if  haveSet :
        return "="

    
    return "+="


def addFiles(self):
    result = MkSFileDialog.getProjectAddFiles( window() )
    
    if  not result.isEmpty() :
        files = result[ "filenames" ].toStringList()
        scope = result[ "scope" ].value<XUPItem*>()
        
        # import files if needed
        if  result[ "import" ].toBool() :
             projectPath = scope.project().path()
             importPath = result[ "importpath" ].toString()
             importRootPath = result[ "directory" ].toString()
            QDir dir( importRootPath )
            
            for ( i = 0; i < files.count(); i++ )
                if  not files.at( i ).startsWith( projectPath ) :
                    fn = QString( files.at( i ) ).remove( importRootPath ).replace( "\\", "/" )
                    fn = QDir.cleanPath( QString( "%1/%2/%3" ).arg( projectPath ).arg( importPath ).arg( fn ) )
                    
                    if  dir.mkpath( QFileInfo( fn ).absolutePath() ) and QFile.copy( files.at( i ), fn ) :
                        files[ i ] = fn




        
        # add files to scope
        addFilesToScope( scope, files )



def removeFiles(self):
    curItem = currentItem()
    
    
    if  not curItem or not ( curItem.type() == XUPItem.Value or curItem.type() == XUPItem.File or curItem.type() == XUPItem.Path ) :
        return

    
    if  QMessageBox.question( window(), tr( "Remove Value..." ), tr( "Are you sur you want to remove self value ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.Yes :
        project = curItem.project()
        
        # if file item
        if  curItem.type() == XUPItem.File :
            rootIncludeProject = project.rootIncludeProject()
             fp = rootIncludeProject.filePath( curItem.cacheValue( "content" ) )
            
            # ask removing file
            if  QFile.exists( fp ) and QMessageBox.question( window(), tr( "Delete associations..." ), tr( "Do you want to delete the associate file ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.Yes :
                if  not QFile.remove( fp ) :
                    QMessageBox.warning( window(), tr( "Error..." ), tr( "Can't delete file: %1" ).arg( fp ) )



        
        # remove value & variable if needed
        variable = curItem.parent()
        variableParent = variable.parent()
        
        variable.removeChild( curItem )
        
        if  variable.childCount() == 0 :
            variableParent.removeChild( variable )

        
        # rebuild cache
        project.rebuildCache()
        project.topLevelProject().rebuildCache()
        
        # save project
        if  not project.save() :
            MonkeyCore.messageManager().appendMessage( tr( "An error occur while saving project '%1': %2" ).arg( project.fileName() ).arg( project.lastError() ) )




def currentProjectModel(self):
    return mFilteredModel.sourceModel()


def currentProject(self):
    curModel = currentProjectModel()
    curItem = currentItem()
    
    if  curItem :
        return curItem.project()

    
    if  not curItem and curModel :
        return curModel.mRootProject

    
    return 0


def currentItem(self):
     index = tvFiltered.currentIndex()
    return mFilteredModel.mapToSource( index )


def topLevelProjects(self):
    XUPProjectItemList projects
    
    for ( i = 0; i < cbProjects.count(); i++ )
        project = cbProjects.itemData( i ).value<XUPProjectModel*>().mRootProject
        projects << project

    
    return projects


def setCurrentProjectModel(self, model ):
    mFilteredModel.setSourceModel( model )
    id = cbProjects.findData( QVariant.fromValue<XUPProjectModel*>( model ) )
    cbProjects.setCurrentIndex( id )


def setCurrentProject(self, curProject, preProject ):
    # update project actions
    action( atClose ).setEnabled( curProject )
    action( atCloseAll ).setEnabled( curProject )
    action( atEdit ).setEnabled( curProject )
    action( atAddFiles ).setEnabled( curProject )
    action( atRemoveFiles ).setEnabled( curProject )
    
    if  not curProject :
        setCurrentProjectModel( 0 )

    elif  curProject.model() != currentProjectModel() :
        setCurrentProjectModel( curProject.model() )

    
    # if project != old update gui
    if  curProject != preProject :
        currentProjectChanged.emit( curProject, preProject )
        currentProjectChanged.emit( curProject )


