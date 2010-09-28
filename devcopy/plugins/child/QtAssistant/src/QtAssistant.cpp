#include "QtAssistant.h"
#include "QtAssistantDock.h"
#include "QtAssistantChild.h"
#include "MkSQtDocInstaller.h"
#include "3rdparty/preferencesdialog.h"

#include <maininterface/UIMain.h>
#include <workspace/pWorkspace.h>
#include <widgets/pDockToolBar.h>

#include <QHelpEngine>

QWidget* QtAssistant::settingsWidget()
{
    MkSQtDocInstaller::collectionFileDirectory( true );
    QHelpEngine* engine = new QHelpEngine( MkSQtDocInstaller::defaultHelpCollectionFileName() );
    
    QWidget* widget = new PreferencesDialog( engine, QApplication::activeWindow() );
    engine->setParent( widget );
    
    return widget;
}

pAbstractChild* QtAssistant::createDocument( const QString& fileName )
{
    Q_UNUSED( fileName );
    return 0;
}

void QtAssistant::fillPluginInfos()
{
    mPluginInfos.Caption = tr( "Qt Assistant" );
    mPluginInfos.Description = tr( "Qt Assistant Integration" );
    mPluginInfos.Author = "Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>";
    mPluginInfos.Type = BasePlugin::iChild;
    mPluginInfos.Name = PLUGIN_NAME;
    mPluginInfos.Version = "0.5.0";
    mPluginInfos.FirstStartEnabled = true;
    mPluginInfos.HaveSettingsWidget = true;
    mPluginInfos.Pixmap = pIconManager::pixmap( "QtAssistant.png", ":/assistant-icons" );
}

bool QtAssistant::install()
{
    mDock = new QtAssistantDock;
    connect( mDock, SIGNAL( helpShown() ), this, SLOT( helpShown() ) );
    MonkeyCore::mainWindow()->dockToolBar( Qt::RightToolBarArea )->addDock( mDock, infos().Caption, pIconManager::icon( "QtAssistant.png", ":/assistant-icons" ) );
    return true;
}

bool QtAssistant::uninstall()
{
    delete mDock;
    return true;
}

void QtAssistant::helpShown()
{
    QtAssistantChild* child = mDock->child();
    pWorkspace* workspace = MonkeyCore::workspace();
    
    if ( !workspace->documents().contains( child ) )
    {
        workspace->handleDocument( child );
        emit child->fileOpened();
        child->showMaximized();
    }
    
    workspace->setCurrentDocument( child );
}

Q_EXPORT_PLUGIN2( ChildQtAssistant, QtAssistant )
