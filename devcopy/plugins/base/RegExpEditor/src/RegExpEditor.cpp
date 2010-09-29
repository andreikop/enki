#TODO make it standalone application

#include "RegExpEditor.h"
#include "UIRegExpEditor.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <widgets/pMenuBar.h>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "Regular Expression Editor" )
    mPluginInfos.Description = tr( "This plugin allow you to test regular expression for a given buffer." )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = False
    mPluginInfos.Pixmap = pIconManager.pixmap( "regexp.png", ":/icons" )


def install(self):
    # create action
    a = MonkeyCore.menuBar().action( "mTools/aRegExpEditor", infos().Caption, infos().Pixmap, QString.null, infos().Description )
    # connections
    a.triggered.connect(self.action_triggered)
    return True


def uninstall(self):
    # delete widget
    delete mEditor
    # delete action
    delete MonkeyCore.menuBar().action( "mTools/aRegExpEditor" )
    return True


def action_triggered(self):
    if  not mEditor :
        mEditor = UIRegExpEditor( MonkeyCore.mainWindow() )
    mEditor.setVisible( not mEditor.isVisible() )


Q_EXPORT_PLUGIN2( BaseRegExpEditor, RegExpEditor )