#include "XUPAddFiles.h"
#include "xupmanager/core/XUPProjectModelProxy.h"
#include "xupmanager/core/XUPProjectModel.h"
#include "xupmanager/core/XUPItem.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "pMonkeyStudio.h"

XUPAddFiles.XUPAddFiles( QWidget* parent )
    : QWidget( parent )
    setupUi( self )
    
    mModel = 0
    mProxy = XUPProjectModelProxy( self )
    tcbScopes.setModel( mProxy )


XUPAddFiles.~XUPAddFiles()


def on_tcbScopes_currentChanged(self, index ):
    Q_UNUSED( index )
    scope = currentScope()
    
    curText = cbImport.currentText()
    cbImport.clear()
    
    if  scope :
        QDir dir( scope.project().path() )
        
        foreach (  QFileInfo& fi, pMonkeyStudio.getFolders( dir, QStringList() ) )
            cbImport.addItem( fi.filePath(), dir.relativeFilePath( fi.filePath() ) )

        
        id = cbImport.findData( curText )
        
        if  id == -1 :
            cbImport.setEditText( curText )

        else:
            cbImport.setCurrentIndex( id )


    
    currentScopeChanged.emit( scope )


def setModel(self, model ):
    if  mModel != model :
        if  mModel :
            # disconnect

        
        mModel = model
        mProxy.setSourceModel( mModel )
        
        if  mModel :
            # connect




def model(self):
    return mModel


def setAddToProjectChoice(self, choice ):
    if  choice :
        gbScopes.setCheckable( True )

    else:
        gbScopes.setCheckable( False )



def addToProjectChoice(self):
    return gbScopes.isCheckable()


def setAddToProject(self, add ):
    setAddToProjectChoice( True )
    gbScopes.setChecked( add )


def addToProject(self):
    if  gbScopes.isCheckable() :
        return gbScopes.isChecked()

    
    return True


def setCurrentScope(self, item ):
    index = item.index()
    index = mProxy.mapFromSource( index )
    tcbScopes.setCurrentIndex( index )


def currentScope(self):
    index = tcbScopes.currentIndex()
    index = mProxy.mapToSource( index )
    return mModel.itemFromIndex( index )


def setImportExternalFiles(self, import ):
    gbImport.setChecked( import )


def importExternalFiles(self):
    return gbImport.isChecked()


def setImportExternalFilesPath(self, path ):
    id = cbImport.findData( path )
    
    if  id == -1 :
        cbImport.addItem( path, path )
        id = cbImport.findData( path )

    
    cbImport.setCurrentIndex( id )


def importExternalFilesPath(self):
     id = cbImport.currentIndex()
    
    if  id == -1 :
        return cbImport.currentText()

    
    return cbImport.itemData( id ).toString()


def setScopeChoiceEnabled(self, enabled ):
    gbScopes.setEnabled( enabled )


def setImportExternalFilesPathEnabled(self, enabled ):
    gbImport.setEnabled( enabled )

