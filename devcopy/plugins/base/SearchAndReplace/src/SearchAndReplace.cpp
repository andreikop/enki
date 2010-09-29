#include "SearchAndReplace.h"
#include "SearchAndReplaceSettings.h"
#include "SearchWidget.h"
#include "SearchResultsDock.h"

#include <coremanager/MonkeyCore.h>
#include <workspace/pWorkspace.h>
#include <workspace/pAbstractChild.h>
#include <maininterface/UIMain.h>
#include <objects/pIconManager.h>
#include <widgets/pDockToolBar.h>
#include <widgets/pMenuBar.h>

def settingsWidget(self):
    return SearchAndReplaceSettings( self )


def settings(self):
    SearchAndReplace.Settings settings
    
    settings.replaceSearchText = settingsValue( "replaceSearchText", settings.replaceSearchText ).toBool()
    settings.onlyWhenNotVisible = settingsValue( "onlyWhenNotVisible", settings.onlyWhenNotVisible ).toBool()
    settings.onlyWhenNotRegExp = settingsValue( "onlyWhenNotRegExp", settings.onlyWhenNotRegExp ).toBool()
    settings.onlyWhenNotEmpty = settingsValue( "onlyWhenNotEmpty", settings.onlyWhenNotEmpty ).toBool()
    
    return settings


def setSettings(self, settings ):
    setSettingsValue( "replaceSearchText", settings.replaceSearchText )
    setSettingsValue( "onlyWhenNotVisible", settings.onlyWhenNotVisible )
    setSettingsValue( "onlyWhenNotRegExp", settings.onlyWhenNotRegExp )
    setSettingsValue( "onlyWhenNotEmpty", settings.onlyWhenNotEmpty )


def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "SearchAndReplace" )
    mPluginInfos.Description = tr( "Search & Replace plugin" )
    mPluginInfos.Author = "Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, KOPATS aka hlamer <hlamer@tut.by>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = True
    mPluginInfos.Pixmap = pIconManager.pixmap( "SearchAndReplace.png", ":/icons" )


def install(self):
    mWidget = SearchWidget( self )
    MonkeyCore.workspace().layout().addWidget( mWidget )
    mWidget.setVisible( False )

    mDock = SearchResultsDock( mWidget.searchThread() )
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( mDock, mDock.windowTitle(), mDock.windowIcon() )
    mDock.setVisible( False )

    mWidget.setResultsDock( mDock )

    mb = MonkeyCore.menuBar()
    QAction* action

    mb.beginGroup( "mEdit/mSearchReplace" )
        action = mb.action( "aSearchFile" )
        action.triggered.connect(self.searchFile_triggered)

        action = mb.action( "aReplaceFile", tr( "&Replace..." ), pIconManager.icon( "replace.png", ":/edit" ), tr( "Ctrl+R" ), tr( "Replace in the current file..." ) )
        action.triggered.connect(self.replaceFile_triggered)

        action = mb.action( "aSearchPrevious", tr( "Search &Previous" ), pIconManager.icon( "previous.png", ":/edit" ), tr( "Shift+F3" ), tr( "Search previous occurrence" ) )
        action.triggered.connect(mWidget.on_pbPrevious_clicked)

        action = mb.action( "aSearchNext", tr( "Search &Next" ), pIconManager.icon( "next.png", ":/edit" ), tr( "F3" ), tr( "Search next occurrence" ) )
        action.triggered.connect(mWidget.on_pbNext_clicked)
        
        action = mb.action( "aSearchDirectory", tr( "Search in &Directory..." ), pIconManager.icon( "search-replace-directory.png" ), tr( "Ctrl+Shift+F" ), tr( "Search in directory..." ) )
        action.triggered.connect(self.searchDirectory_triggered)
        
        action = mb.action( "aReplaceDirectory", tr( "Replace in Director&y..." ), pIconManager.icon( "search-replace-directory.png" ), tr( "Ctrl+Shift+R" ), tr( "Replace in directory..." ) )
        action.triggered.connect(self.replaceDirectory_triggered)
        
        action = mb.action( "aSearchProjectFiles", tr( "Search in Project &Files..." ), pIconManager.icon( "search-replace-project-files.png" ), tr( "Ctrl+Meta+F" ), tr( "Search in the current project files.." ) )
        action.triggered.connect(self.searchProjectFiles_triggered)
        
        action = mb.action( "aReplaceProjectFiles", tr( "Replace in Projec&t Files..." ), pIconManager.icon( "search-replace-project-files.png" ), tr( "Ctrl+Meta+R" ), tr( "Replace in the current project files..." ) )
        action.triggered.connect(self.replaceProjectFiles_triggered)
        
        action = mb.action( "aSearchOpenedFiles", tr( "Search in &Opened Files..." ), pIconManager.icon( "search-replace-opened-files.png" ), tr( "Ctrl+Alt+Meta+F" ), tr( "Search in opened files..." ) )
        action.triggered.connect(self.searchOpenedFiles_triggered)
        
        action = mb.action( "aReplaceOpenedFiles", tr( "Replace in Open&ed Files..." ), pIconManager.icon( "search-replace-opened-files.png" ), tr( "Ctrl+Alt+Meta+R" ), tr( "Replace in opened files..." ) )
        action.triggered.connect(self.replaceOpenedFiles_triggered)
    mb.endGroup()

    return True


def uninstall(self):
    mb = MonkeyCore.menuBar()
    QAction* action

    mb.beginGroup( "mEdit/mSearchReplace" )
        action = mb.action( "aSearchFile" )
        disaction.triggered.connect(self.searchFile_triggered)

        action = mb.action( "aReplaceFile" )
        disaction.triggered.connect(self.replaceFile_triggered)
        delete action

        action = mb.action( "aSearchPrevious" )
        disaction.triggered.connect(mWidget.on_pbPrevious_clicked)
        delete action

        action = mb.action( "aSearchNext" )
        disaction.triggered.connect(mWidget.on_pbNext_clicked)
        delete action
        
        action = mb.action( "aSearchDirectory" )
        disaction.triggered.connect(self.searchDirectory_triggered)
        delete action
        
        action = mb.action( "aReplaceDirectory" )
        disaction.triggered.connect(self.replaceDirectory_triggered)
        delete action
        
        action = mb.action( "aSearchProjectFiles" )
        disaction.triggered.connect(self.searchProjectFiles_triggered)
        delete action
        
        action = mb.action( "aReplaceProjectFiles" )
        disaction.triggered.connect(self.replaceProjectFiles_triggered)
        delete action
        
        action = mb.action( "aSearchOpenedFiles" )
        disaction.triggered.connect(self.searchOpenedFiles_triggered)
        delete action
        
        action = mb.action( "aReplaceOpenedFiles" )
        disaction.triggered.connect(self.replaceOpenedFiles_triggered)
        delete action
    mb.endGroup()

    delete mDock
    delete mWidget

    return True


def searchFile_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeSearch )



def replaceFile_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeReplace )



def searchDirectory_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeSearchDirectory )



def replaceDirectory_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeReplaceDirectory )



def searchProjectFiles_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeSearchProjectFiles )



def replaceProjectFiles_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeReplaceProjectFiles )



def searchOpenedFiles_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeSearchOpenedFiles )



def replaceOpenedFiles_triggered(self):
    document = MonkeyCore.workspace().currentDocument()

    if  ( document and document.editor() ) or not document :
        mWidget.setMode( SearchAndReplace.ModeReplaceOpenedFiles )



Q_EXPORT_PLUGIN2( BaseSearchAndReplace, SearchAndReplace )
