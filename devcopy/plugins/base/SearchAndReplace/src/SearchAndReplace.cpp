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

QWidget* SearchAndReplace::settingsWidget()
{
    return new SearchAndReplaceSettings( this );
}

SearchAndReplace::Settings SearchAndReplace::settings() const
{
    SearchAndReplace::Settings settings;
    
    settings.replaceSearchText = settingsValue( "replaceSearchText", settings.replaceSearchText ).toBool();
    settings.onlyWhenNotVisible = settingsValue( "onlyWhenNotVisible", settings.onlyWhenNotVisible ).toBool();
    settings.onlyWhenNotRegExp = settingsValue( "onlyWhenNotRegExp", settings.onlyWhenNotRegExp ).toBool();
    settings.onlyWhenNotEmpty = settingsValue( "onlyWhenNotEmpty", settings.onlyWhenNotEmpty ).toBool();
    
    return settings;
}

void SearchAndReplace::setSettings( const SearchAndReplace::Settings& settings )
{
    setSettingsValue( "replaceSearchText", settings.replaceSearchText );
    setSettingsValue( "onlyWhenNotVisible", settings.onlyWhenNotVisible );
    setSettingsValue( "onlyWhenNotRegExp", settings.onlyWhenNotRegExp );
    setSettingsValue( "onlyWhenNotEmpty", settings.onlyWhenNotEmpty );
}

void SearchAndReplace::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "SearchAndReplace" );
    mPluginInfos.Description = tr( "Search & Replace plugin" );
    mPluginInfos.Author = "Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, Andrei KOPATS aka hlamer <hlamer@tut.by>";
    mPluginInfos.Type = BasePlugin::iBase;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "1.0.0";
    mPluginInfos.FirstStartEnabled = true;
    mPluginInfos.HaveSettingsWidget = true;
    mPluginInfos.Pixmap = pIconManager::pixmap( "SearchAndReplace.png", ":/icons" );
}

bool SearchAndReplace::install()
{
    mWidget = new SearchWidget( this );
    MonkeyCore::workspace()->layout()->addWidget( mWidget );
    mWidget->setVisible( false );

    mDock = new SearchResultsDock( mWidget->searchThread() );
    MonkeyCore::mainWindow()->dockToolBar( Qt::BottomToolBarArea )->addDock( mDock, mDock->windowTitle(), mDock->windowIcon() );
    mDock->setVisible( false );

    mWidget->setResultsDock( mDock );

    pMenuBar* mb = MonkeyCore::menuBar();
    QAction* action;

    mb->beginGroup( "mEdit/mSearchReplace" );
        action = mb->action( "aSearchFile" );
        connect( action, SIGNAL( triggered() ), this, SLOT( searchFile_triggered() ) );

        action = mb->action( "aReplaceFile", tr( "&Replace..." ), pIconManager::icon( "replace.png", ":/edit" ), tr( "Ctrl+R" ), tr( "Replace in the current file..." ) );
        connect( action, SIGNAL( triggered() ), this, SLOT( replaceFile_triggered() ) );

        action = mb->action( "aSearchPrevious", tr( "Search &Previous" ), pIconManager::icon( "previous.png", ":/edit" ), tr( "Shift+F3" ), tr( "Search previous occurrence" ) );
        connect( action, SIGNAL( triggered() ), mWidget, SLOT( on_pbPrevious_clicked() ) );

        action = mb->action( "aSearchNext", tr( "Search &Next" ), pIconManager::icon( "next.png", ":/edit" ), tr( "F3" ), tr( "Search next occurrence" ) );
        connect( action, SIGNAL( triggered() ), mWidget, SLOT( on_pbNext_clicked() ) );
        
        action = mb->action( "aSearchDirectory", tr( "Search in &Directory..." ), pIconManager::icon( "search-replace-directory.png" ), tr( "Ctrl+Shift+F" ), tr( "Search in directory..." ) );
        connect( action, SIGNAL( triggered() ), this, SLOT( searchDirectory_triggered() ) );
        
        action = mb->action( "aReplaceDirectory", tr( "Replace in Director&y..." ), pIconManager::icon( "search-replace-directory.png" ), tr( "Ctrl+Shift+R" ), tr( "Replace in directory..." ) );
        connect( action, SIGNAL( triggered() ), this, SLOT( replaceDirectory_triggered() ) );
        
        action = mb->action( "aSearchProjectFiles", tr( "Search in Project &Files..." ), pIconManager::icon( "search-replace-project-files.png" ), tr( "Ctrl+Meta+F" ), tr( "Search in the current project files.." ) );
        connect( action, SIGNAL( triggered() ), this, SLOT( searchProjectFiles_triggered() ) );
        
        action = mb->action( "aReplaceProjectFiles", tr( "Replace in Projec&t Files..." ), pIconManager::icon( "search-replace-project-files.png" ), tr( "Ctrl+Meta+R" ), tr( "Replace in the current project files..." ) );
        connect( action, SIGNAL( triggered() ), this, SLOT( replaceProjectFiles_triggered() ) );
        
        action = mb->action( "aSearchOpenedFiles", tr( "Search in &Opened Files..." ), pIconManager::icon( "search-replace-opened-files.png" ), tr( "Ctrl+Alt+Meta+F" ), tr( "Search in opened files..." ) );
        connect( action, SIGNAL( triggered() ), this, SLOT( searchOpenedFiles_triggered() ) );
        
        action = mb->action( "aReplaceOpenedFiles", tr( "Replace in Open&ed Files..." ), pIconManager::icon( "search-replace-opened-files.png" ), tr( "Ctrl+Alt+Meta+R" ), tr( "Replace in opened files..." ) );
        connect( action, SIGNAL( triggered() ), this, SLOT( replaceOpenedFiles_triggered() ) );
    mb->endGroup();

    return true;
}

bool SearchAndReplace::uninstall()
{
    pMenuBar* mb = MonkeyCore::menuBar();
    QAction* action;

    mb->beginGroup( "mEdit/mSearchReplace" );
        action = mb->action( "aSearchFile" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( searchFile_triggered() ) );

        action = mb->action( "aReplaceFile" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( replaceFile_triggered() ) );
        delete action;

        action = mb->action( "aSearchPrevious" );
        disconnect( action, SIGNAL( triggered() ), mWidget, SLOT( on_pbPrevious_clicked() ) );
        delete action;

        action = mb->action( "aSearchNext" );
        disconnect( action, SIGNAL( triggered() ), mWidget, SLOT( on_pbNext_clicked() ) );
        delete action;
        
        action = mb->action( "aSearchDirectory" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( searchDirectory_triggered() ) );
        delete action;
        
        action = mb->action( "aReplaceDirectory" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( replaceDirectory_triggered() ) );
        delete action;
        
        action = mb->action( "aSearchProjectFiles" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( searchProjectFiles_triggered() ) );
        delete action;
        
        action = mb->action( "aReplaceProjectFiles" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( replaceProjectFiles_triggered() ) );
        delete action;
        
        action = mb->action( "aSearchOpenedFiles" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( searchOpenedFiles_triggered() ) );
        delete action;
        
        action = mb->action( "aReplaceOpenedFiles" );
        disconnect( action, SIGNAL( triggered() ), this, SLOT( replaceOpenedFiles_triggered() ) );
        delete action;
    mb->endGroup();

    delete mDock;
    delete mWidget;

    return true;
}

void SearchAndReplace::searchFile_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeSearch );
    }
}

void SearchAndReplace::replaceFile_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeReplace );
    }
}

void SearchAndReplace::searchDirectory_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeSearchDirectory );
    }
}

void SearchAndReplace::replaceDirectory_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeReplaceDirectory );
    }
}

void SearchAndReplace::searchProjectFiles_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeSearchProjectFiles );
    }
}

void SearchAndReplace::replaceProjectFiles_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeReplaceProjectFiles );
    }
}

void SearchAndReplace::searchOpenedFiles_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeSearchOpenedFiles );
    }
}

void SearchAndReplace::replaceOpenedFiles_triggered()
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();

    if ( ( document && document->editor() ) || !document )
    {
        mWidget->setMode( SearchAndReplace::ModeReplaceOpenedFiles );
    }
}

Q_EXPORT_PLUGIN2( BaseSearchAndReplace, SearchAndReplace )
