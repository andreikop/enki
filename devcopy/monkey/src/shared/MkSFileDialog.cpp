#include "MkSFileDialog.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "xupmanager/core/XUPProjectItemInfos.h"
#include "pMonkeyStudio.h"
#include "xupmanager/gui/XUPAddFiles.h"
#include "coremanager/MonkeyCore.h"
#include "xupmanager/gui/XUPProjectManager.h"

#include <widgets/pTreeComboBox.h>

#include <QComboBox>

MkSFileDialog.MkSFileDialog( QWidget* parent, caption, directory, filter, textCodecEnabled, openReadOnlyEnabled )
        : pFileDialog( parent, caption, directory, filter, textCodecEnabled, openReadOnlyEnabled )
    mAddFiles = XUPAddFiles( self )
    glDialog.addWidget( mAddFiles, 6, 0, 1, -1 )

    mAddFiles.currentScopeChanged.connect(self.currentScopeChanged)


def currentScopeChanged(self, scope ):
    if  scope :
        projectPath = QDir( scope.project().path() ).canonicalPath()

        if  not directory().canonicalPath().startsWith( projectPath ) :
            setDirectory( projectPath )




def getOpenFileName(self, parent, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options ):
    pFileDialogResult result
    MkSFileDialog fd( parent )
    setOpenFileNameDialog( &fd, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options )
    fd.setTextCodec( pMonkeyStudio.defaultCodec() )
    fd.mAddFiles.setVisible( False )

    if  fd.exec() == QDialog.Accepted :
        if  selectedFilter :
            *selectedFilter = fd.selectedFilter()


        result[ "filename" ] = fd.selectedFiles().value( 0 )
        result[ "codec" ] = fd.textCodec()
        result[ "openreadonly" ] = fd.openReadOnly()


    return result


def getOpenFileNames(self, parent, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options ):
    pFileDialogResult result
    MkSFileDialog fd( parent )
    setOpenFileNamesDialog( &fd, caption, dir, filter, enabledTextCodec, enabledOpenReadOnly, selectedFilter, options )
    fd.setTextCodec( pMonkeyStudio.defaultCodec() )
    fd.mAddFiles.setVisible( False )

    if  fd.exec() == QDialog.Accepted :
        if  selectedFilter :
            *selectedFilter = fd.selectedFilter()


        result[ "filenames" ] = fd.selectedFiles()
        result[ "codec" ] = fd.textCodec()
        result[ "openreadonly" ] = fd.openReadOnly()


    return result


def getSaveFileName(self, parent, caption, dir, filter, enabledTextCodec, selectedFilter, options ):
    pFileDialogResult result
    MkSFileDialog fd( parent )
    setSaveFileNameDialog( &fd, caption, dir, filter, enabledTextCodec, selectedFilter, options )
    fd.setTextCodec( pMonkeyStudio.defaultCodec() )
    fd.mAddFiles.setVisible( False )

    if  fd.exec() == QDialog.Accepted :
        if  selectedFilter :
            *selectedFilter = fd.selectedFilter()


        result[ "filename" ] = fd.selectedFiles().value( 0 )
        result[ "codec" ] = fd.textCodec()
        result[ "openreadonly" ] = fd.openReadOnly()


    return result


def getOpenProjects(self, parent ):
    pFileDialogResult result
    caption = tr( "Choose project(s) to open" )
    filter = XUPProjectItem.projectInfos().projectsFilter()
    enabledTextCodec = True
    enabledOpenReadOnly = False

    MkSFileDialog fd( parent )
    setOpenFileNamesDialog( &fd, caption, QDir.currentPath() , filter, enabledTextCodec, enabledOpenReadOnly, 0, 0 )
    fd.setTextCodec( pMonkeyStudio.defaultCodec() )
    fd.mAddFiles.setVisible( False )

    if  fd.exec() == QDialog.Accepted :
        result[ "filenames" ] = fd.selectedFiles()
        result[ "codec" ] = fd.textCodec()
        result[ "openreadonly" ] = fd.openReadOnly()


    return result


def getProjectAddFiles(self, parent, allowChooseScope ):
    pFileDialogResult result
    model = MonkeyCore.projectsManager().currentProjectModel()

    if  model :
        curProject = MonkeyCore.projectsManager().currentProject()
        operators = curProject.projectInfos().operators( curProject.projectType() )
        caption = tr( "Choose file(s) to add to your project" )
        filter = XUPProjectItem.projectInfos().variableSuffixesFilter( curProject.projectType() )
        enabledTextCodec = False
        enabledOpenReadOnly = False

        MkSFileDialog fd( parent )
        setOpenFileNamesDialog( &fd, caption, QDir.currentPath(), filter, enabledTextCodec, enabledOpenReadOnly, 0, 0 )
        fd.setTextCodec( pMonkeyStudio.defaultCodec() )
        fd.mAddFiles.setModel( model )
        fd.mAddFiles.setCurrentScope( curProject )
        fd.mAddFiles.setScopeChoiceEnabled( allowChooseScope )

        if  fd.exec() == QDialog.Accepted :
            result[ "filenames" ] = fd.selectedFiles()
            result[ "scope" ] = QVariant.fromValue<XUPItem*>( fd.mAddFiles.currentScope() )
            result[ "import" ] = fd.mAddFiles.importExternalFiles()
            result[ "importpath" ] = fd.mAddFiles.importExternalFilesPath()
            result[ "directory" ] = fd.directory().absolutePath()



    return result


def getNewEditorFile(self, parent ):
    pFileDialogResult result
    model = MonkeyCore.projectsManager().currentProjectModel()
    curProject = MonkeyCore.projectsManager().currentProject()
    operators = curProject ? curProject.projectInfos().operators( curProject.projectType() ) : QStringList()
    caption = tr( "New File Name..." )
    filter = curProject ? XUPProjectItem.projectInfos().variableSuffixesFilter( curProject.projectType() ) : pMonkeyStudio.availableFilesFilters()
    enabledTextCodec = True

    MkSFileDialog fd( parent )
    setSaveFileNameDialog( &fd, caption, QDir.currentPath(), filter, enabledTextCodec, 0, 0 )
    fd.setTextCodec( pMonkeyStudio.defaultCodec() )

    if  curProject :
        fd.mAddFiles.setModel( model )
        fd.mAddFiles.setAddToProjectChoice( True )
        fd.mAddFiles.setAddToProject( False )
        fd.mAddFiles.setCurrentScope( curProject )

    else:
        fd.mAddFiles.setVisible( False )


    if  fd.exec() == QDialog.Accepted :
        result[ "filename" ] = fd.selectedFiles().value( 0 )
        result[ "codec" ] = fd.textCodec()

        if  model :
            result[ "addtoproject" ] = fd.mAddFiles.addToProject()
            result[ "scope" ] = QVariant.fromValue<XUPItem*>( fd.mAddFiles.currentScope() )



    return result

