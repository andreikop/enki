#include "QtAssistant.h"
#include "QtAssistantDock.h"
#include "QtAssistantChild.h"
#include "MkSQtDocInstaller.h"
#include "3rdparty/preferencesdialog.h"

#include <maininterface/UIMain.h>
#include <workspace/pWorkspace.h>
#include <widgets/pDockToolBar.h>

#include <QHelpEngine>

def settingsWidget(self):
    MkSQtDocInstaller.collectionFileDirectory( True )
    engine = QHelpEngine( MkSQtDocInstaller.defaultHelpCollectionFileName() )

    widget = PreferencesDialog( engine, QApplication.activeWindow() )
    engine.setParent( widget )

    return widget


def createDocument(self, fileName ):
    Q_UNUSED( fileName )
    return 0


def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "Qt Assistant" )
    mPluginInfos.Description = tr( "Qt Assistant Integration" )
    mPluginInfos.Author = "Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iChild
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "0.5.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = True
    mPluginInfos.Pixmap = pIconManager.pixmap( "QtAssistant.png", ":/assistant-icons" )


def install(self):
    mDock = QtAssistantDock
    mDock.helpShown.connect(self.helpShown)
    MonkeyCore.mainWindow().dockToolBar( Qt.RightToolBarArea ).addDock( mDock, infos().Caption, pIconManager.icon( "QtAssistant.png", ":/assistant-icons" ) )
    return True


def uninstall(self):
    delete mDock
    return True


def helpShown(self):
    child = mDock.child()
    workspace = MonkeyCore.workspace()

    if  not workspace.documents().contains( child ) :
        workspace.handleDocument( child )
        child.emit.fileOpened()
        child.showMaximized()


    workspace.setCurrentDocument( child )


Q_EXPORT_PLUGIN2( ChildQtAssistant, QtAssistant )
