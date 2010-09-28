//TODO make it standalone application

#include "RegExpEditor.h"
#include "UIRegExpEditor.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <widgets/pMenuBar.h>

void RegExpEditor::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "Regular Expression Editor" );
    mPluginInfos.Description = tr( "This plugin allow you to test regular expression for a given buffer." );
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>";
    mPluginInfos.Type = BasePlugin::iBase;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "1.0.0";
    mPluginInfos.FirstStartEnabled = false;
    mPluginInfos.Pixmap = pIconManager::pixmap( "regexp.png", ":/icons" );
}

bool RegExpEditor::install()
{
    // create action
    QAction* a = MonkeyCore::menuBar()->action( "mTools/aRegExpEditor", infos().Caption, infos().Pixmap, QString::null, infos().Description );
    // connections
    connect( a, SIGNAL( triggered() ), this, SLOT( action_triggered() ) );
    return true;
}

bool RegExpEditor::uninstall()
{
    // delete widget
    delete mEditor;
    // delete action
    delete MonkeyCore::menuBar()->action( "mTools/aRegExpEditor" );
    return true;
}

void RegExpEditor::action_triggered()
{
    if ( !mEditor )
        mEditor = new UIRegExpEditor( MonkeyCore::mainWindow() );
    mEditor->setVisible( !mEditor->isVisible() );
}

Q_EXPORT_PLUGIN2( BaseRegExpEditor, RegExpEditor )