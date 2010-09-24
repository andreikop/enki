import sys

from PyQt4.QtCore import QObject
from PyQt4.QtCore import QFile
from PyQt4.QtCore import QFileInfo
from PyQt4.QtCore import QDir
from PyQt4.QtGui import qApp

from PyQt4.fresh import pSettings

import mks.config
import mks.monkeycore
import mks.monkeystudio

class Settings (pSettings):
    
    SP_PLUGINS = "plugins"
    SP_APIS = "apis"
    SP_TEMPLATES = "templates",
    SP_TRANSLATIONS = "translations"
    SP_SCRIPTS = "scripts"
    
    def __init__(self, parent = None):
        pSettings.__init__(self, parent)
    
    def storagePaths(self, type):
        result = self.value( "Paths/%s" % type )
        
        if  result:
            return [result]
        
        appPath = qApp.applicationDirPath()
    
        if sys.platform.startswith('win'): # Windows platform
            appIsInstalled = QFile.exists( QString( "%1/templates" ).arg( appPath ) )
            basePath = appPath
        elif sys.platform.startswith('darwin'): # MAC platform
            appIsInstalled = QFile.exists( "%s/../Resources/templates" % appPath )
            basePath = "%s/../Resources" % appPath
        else:
            print 'FIXME UNKNOWN PLATFORM!!!'
            appIsInstalled = QFile.exists( mks.config.PACKAGE_PREFIX ) and QFile.exists( mks.config.PACKAGE_DATAS )
            basePath = PACKAGE_DATAS
        
        if  not appIsInstalled :
            return self.storagePathsOutOfBox( type, appPath )
        
        if  type == Settings.SP_PLUGINS :
            if sys.platform.startswith('win'): # Windows platform
                basePath = appPath
            elif sys.platform.startswith('darwin'): # MAC platform
                basePath = "%s/.." % appPath
            else:
                print 'FIXME UNKNOWN PLATFORM!!!'
                return [PACKAGE_PLUGINS]
            
            return [QDir.cleanPath( "%s/%s" % (basePath, type ) )]
    
        return [QDir.cleanPath( "%s/%s" % ( basePath, type ) )]
    
    def setStoragePaths(self, type, paths ):
        self.setValue( "Paths/%s" % type, paths )

    def homeFilePath(self,  filePath ):
        path = QFileInfo( fileName() ).absolutePath()
        dir = QDir ( path )
        
        return QDir.cleanPath( dir.filePath( filePath ) )

    def homePath(self, type ):
        folder = type + "-%s" % mks.config.PACKAGE_VERSION_STR
        path = QFileInfo( self.fileName() ).absolutePath().append( "/%s" % folder )
        dir = QDir( path )

        if  not dir.exists() and not dir.mkpath( path ) :
            return QString.null
        
        return path

    def storagePathsOutOfBox( self, type,  appPath ):
        basePath = appPath

        if sys.platform.startswith('win'): # Windows platform
            basePath.append( "/../../../../datas" )
        elif sys.platform.startswith('darwin'): # MAC platform
            basePath.append( "/../datas" )
        
        if  type == Settings.SP_PLUGINS :
            if sys.platform.startswith('win'): # Windows platform
                basePath = appPath
            elif sys.platform.startswith('darwin'): # MAC platform
                basePath = QString( "%1/.." ).arg( appPath )
            else:
                basePath = appPath
            
            return [QDir.cleanPath( "%s/%s" % ( basePath, type ) )]
        
        return [QDir.cleanPath( "%s/%s" % (basePath, type ) )]
    
    def setDefaultSettings(self):
        # create default paths
        pluginsPaths = self.storagePaths( Settings.SP_PLUGINS )
        apisPaths = self.storagePaths( Settings.SP_APIS )
        templatesPaths = self.storagePaths( Settings.SP_TEMPLATES )
        translationsPaths = self.storagePaths( Settings.SP_TRANSLATIONS )
        scriptsPaths = self.storagePaths( Settings.SP_SCRIPTS )
        scriptsPath = self.homePath( Settings.SP_SCRIPTS )

        # save default paths
        self.setStoragePaths( Settings.SP_PLUGINS, pluginsPaths )
        self.setStoragePaths( Settings.SP_APIS, apisPaths )
        self.setStoragePaths( Settings.SP_TEMPLATES, templatesPaths )
        self.setStoragePaths( Settings.SP_TRANSLATIONS, translationsPaths )
        self.setStoragePaths( Settings.SP_SCRIPTS, scriptsPaths )

        # apis
        for path in apisPaths:
            if  QFile.exists( path.toString() +"/cmake.api" ) :
                self.setValue( "SourceAPIs/CMake", [QDir.cleanPath( path +"/cmake.api" )] )
            
            if  QFile.exists( path.toString() +"/cs.api" ) :
                setValue( "SourceAPIs/C#", [QDir.cleanPath( path +"/cs.api" )] )
            
            if  QFile.exists( path.toString() +"/c.api" ) :
                files = []
                files.append(QDir.cleanPath( path +"/c.api" ))
                files.append(QDir.cleanPath( path +"/cpp.api" ))
                files.append(QDir.cleanPath( path +"/glut.api" ))
                files.append(QDir.cleanPath( path +"/opengl.api" ))
                files.append(QDir.cleanPath( path +"/qt-4.5.x.api" ))
                
                self.setValue( "SourceAPIs/C++", files )
        
        # copy scripts to user's home
        for path in scriptsPaths:
            files = QDir( path.toString() ).entryInfoList( ["*.mks"] )
            
            for file in files:
                fn = QDir( scriptsPath ).absoluteFilePath( file.fileName() )
                
                if  not QFile.exists( fn ) :
                    f = QFile ( file.absoluteFilePath() )
                    
                    if  not f.copy( fn ) :
                        message = mks.monkeycore.messageManager().tr( "Can't copy script '%s', %s" ) % (file.fileName(), f.errorString())
                        mks.monkeycore.messageManager().appendMessage( message )
        
        # syntax highlighter
        self.setDefaultLexerProperties( mks.monkeystudio.defaultDocumentFont(), True )
        self.setDefaultCppSyntaxHighlight()


    def setDefaultCppSyntaxHighlight(self):
        font = mks.monkeystudio.defaultDocumentFont()
        parts = [font.family(), str(font.pointSize())]
        """TODO
        # configure default styles
        LexerStyleList styles
        styles << LexerStyle( 0, 0, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 1, 10526880, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 2, 10526880, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 3, 8421631, False, "%1, 1, 0, 0", 16777215 )
        styles << LexerStyle( 4, 15728880, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 5, 160, False, "%1, 1, 0, 0", 16777215 )
        styles << LexerStyle( 6, 255, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 7, 14721024, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 9, 40960, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 10, 16711680, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 11, 0, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 12, 0, True, "%1, 0, 0, 0", 16711680 )
        styles << LexerStyle( 15, 8421631, False, "%1, 1, 0, 0", 16777215 )
        styles << LexerStyle( 16,0 , False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 17, 32896, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 18, 8388608, False, "%1, 0, 0, 0", 16777215 )
        styles << LexerStyle( 19, 0, False, "%1, 0, 0, 0", 16777215 )

        # write styles
        beginGroup( "Scintilla/C++" )

        foreach (  LexerStyle& style, styles )
            beginGroup( QString( "style%1" ).arg( style.id ) )
            setValue( "color", style.color )
            setValue( "eolfill", style.eolfill )
            setValue( "font", style.font.arg( parts.join( ", " ) ).split( ',' ) )
            setValue( "paper", style.paper )
            endGroup()


        setValue( "properties/foldatelse", QVariant( True ).toString() )
        setValue( "properties/foldcomments", QVariant( True ).toString() )
        setValue( "properties/foldcompact", QVariant( True ).toString() )
        setValue( "properties/foldpreprocessor", QVariant( True ).toString() )
        setValue( "properties/stylepreprocessor", QVariant( True ).toString() )
        setValue( "defaultcolor", 0 )
        setValue( "defaultpaper", 16777215 )
        setValue( "defaultfont", QString( "Verdana, 10, 0, 0, 0" ).split( ',' ) )
        setValue( "autoindentstyle", 1 )

        endGroup()
        """


    def setDefaultLexerProperties(self, defaultFont, write ):
        pass
        """TODO
        foreach (  QString& language, pMonkeyStudio.availableLanguages() )
            QsciLexer* lexer = pMonkeyStudio.lexerForLanguage( language )

            for ( int i = 0; i < 128; i++ )
                if  not lexer.description( i ).isEmpty() :
                    QFont font = lexer.font( i )

                    font.setFamily( defaultFont.family() )
                    font.setPointSize( defaultFont.pointSize() )
                    lexer.setFont( font, i )



            if  write :
                lexer.writeSettings( *this, pMonkeyStudio.scintillaSettingsPath().toLocal8Bit().constData() )
        """
