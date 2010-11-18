#include "MkSQtDocInstaller.h"
#include "main.h"
#include "3rdparty/qtdocinstaller.h"

#include <coremanager/MonkeyCore.h>
#include <widgets/pQueuedMessageToolBar.h>

#include <QDesktopServices>
#include <QDir>
#include <QHelpEngine>
#include <QResource>
#include <QTimer>

MkSQtDocInstaller.MkSQtDocInstaller( QHelpEngine* engine )
    : QObject( engine )
    mHelpEngine = engine
    mQtDocInstaller = 0


def collectionFileDirectory(self, createDir, cacheDir ):
    collectionPath = QDesktopServices.storageLocation( QDesktopServices.DataLocation ).remove( PACKAGE_NAME )
    if  collectionPath.isEmpty() :
        if  cacheDir.isEmpty() :
            collectionPath = QDir.homePath() +QDir.separator() +QLatin1String( ".assistant" )
        else:
            collectionPath = QDir.homePath() +QLatin1String( "/." ) +cacheDir

    else:
        if  cacheDir.isEmpty() :
            collectionPath = collectionPath +QLatin1String( "/Trolltech/Assistant" )
        else:
            collectionPath = collectionPath +QDir.separator() +cacheDir

    collectionPath = QDir.cleanPath( collectionPath )
    if  createDir :
        QDir dir
        if  not dir.exists( collectionPath ) :
            dir.mkpath( collectionPath )

    return QDir.cleanPath( collectionPath )


def defaultHelpCollectionFileName(self):
    return collectionFileDirectory() +QDir.separator() +QString( "qthelpcollection_%1.qhc" ).arg( qVersion() )


def checkDocumentation(self):
    b = initHelpDB()
    if  b :
        QTimer.singleShot( 0, self, SLOT( lookForNewQtDocumentation() ) )
    else:
        MonkeyCore.messageManager().appendMessage( tr( "Can't initialize documentation database" ) +" (Qt Assistant)" )
    return b


def initHelpDB(self):
    if  not mHelpEngine.setupData() :
        return False

    assistantInternalDocRegistered = False
    for ns in mHelpEngine.registeredDocumentations():
        if  ns.startsWith( QLatin1String( "com.trolltech.com.assistantinternal_" ) ) :
            assistantInternalDocRegistered = True
            break



    needsSetup = False
    if  not assistantInternalDocRegistered :
        QFileInfo fi( mHelpEngine.collectionFile() )
         helpFile = fi.absolutePath() +QDir.separator() +QLatin1String( "assistant.qch" )
        if  not QFile.exists( helpFile ) :
            QFile file( helpFile )
            if  file.open( QIODevice.WriteOnly ) :
                QResource res( QLatin1String( ":/documentation/assistant.qch" ) )
                if  file.write( ( char*)res.data(), res.size() ) != res.size() :
                    MonkeyCore.messageManager().appendMessage( tr( "Could not write assistant.qch" ) +" (Qt Assistant )" )
                file.close()


        QHelpEngineCore hc( fi.absoluteFilePath() )
        hc.setupData()
        hc.registerDocumentation( helpFile )
        needsSetup = True


    i = mHelpEngine.customValue( QLatin1String( "UnfilteredFilterInserted" ) ).toInt()
    if  i != 1 :
            QHelpEngineCore hc( mHelpEngine.collectionFile() )
            hc.setupData()
            hc.addCustomFilter( tr( "Unfiltered" ), QStringList() )
            hc.setCustomValue( QLatin1String( "UnfilteredFilterInserted" ), 1 )

        block = mHelpEngine.blockSignals( True )
        mHelpEngine.setCurrentFilter( tr( "Unfiltered" ) )
        mHelpEngine.blockSignals( block )
        needsSetup = True


    if  needsSetup :
        mHelpEngine.setupData()
    return True


def lookForNewQtDocumentation(self):
    mQtDocInstaller = QtDocInstaller( mHelpEngine.collectionFile() )
    mQtDocInstaller.errorMessage.connect(self.displayInstallationError)
    mQtDocInstaller.docsInstalled.connect(self.qtDocumentationInstalled)

    '''
    versionKey = QString( QLatin1String( "qtVersion%1$$$qt" ) ).arg( QLatin1String( QT_VERSION_STR ) )
    if  mHelpEngine.customValue( versionKey, 0 ).toInt() != 1 :
        MonkeyCore.messageManager().appendMessage( tr( "Looking for Qt Documentation..." ) )
    '''
    mQtDocInstaller.installDocs()


def displayInstallationError(self, errorMessage ):
    MonkeyCore.messageManager().appendMessage( errorMessage )


def qtDocumentationInstalled(self, newDocsInstalled ):
    if  newDocsInstalled :
        mHelpEngine.setupData()

