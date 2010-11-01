"""Module provides interface for store core and plugins settings and hardcodes default 
settings for MkS core.
If you added new option to the MkS core, do not forget to add default value for it here.
if you use settings from your plugin, you must call mks.settings.registerOption before
read and write it.
"""

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4.Qsci import *

defaults = {
"Editor/SelectionBackgroundColor" : QColor( "#bdff9b" ),
"Editor/SelectionForegroundColor" : QColor( "#000000" ),
"Editor/DefaultDocumentColours" : False,
"Editor/DefaultDocumentPen" : QColor( Qt.black ),
"Editor/DefaultDocumentPaper" : QColor( Qt.white ),
"Editor/AutoCompletionCaseSensitivity" : True,
"Editor/AutoCompletionReplaceWord" : True,
"Editor/AutoCompletionShowSingle" : False,
"Editor/AutoCompletionSource" : QsciScintilla.AcsAll,
"Editor/AutoCompletionThreshold" : 3,
"Editor/CallTipsBackgroundColor": QColor( "#ffff9b" ),
"Editor/CallTipsForegroundColor": QColor( "#000000" ),
"Editor/CallTipsHighlightColor": QColor( "#ff0000" ),
"Editor/CallTipsStyle" : QsciScintilla.CallTipsContext,
"Editor/CallTipsVisible" : -1,
"Editor/AutoIndent" : True,
"Editor/BackspaceUnindents" : True,
"Editor/IndentationGuides" : True,
"Editor/IndentationsUseTabs" : True,
"Editor/AutoDetectIndent" : False,
"Editor/IndentationWidth" : 4,
"Editor/TabIndents" : True,
"Editor/TabWidth" : 4,
"Editor/IndentationGuidesBackgroundColor": QColor( "#0000ff" ),
"Editor/IndentationGuidesForegroundColor": QColor( "#0000ff" ),
"Editor/BraceMatching" : QsciScintilla.SloppyBraceMatch,
"Editor/MatchedBraceBackgroundColor": QColor( "#ffff7f" ),
"Editor/MatchedBraceForegroundColor": QColor( "#ff0000" ),
"Editor/UnmatchedBraceBackgroundColor": QColor( "#ff0000" ),
"Editor/UnmatchedBraceForegroundColor": QColor( "#ffffff" ),
"Editor/EdgeMode" : QsciScintilla.EdgeNone,
"Editor/EdgeColor": QColor( "#ff0000" ),
"Editor/EdgeColumn" : 80,
"Editor/CaretLineVisible" : True,
"Editor/CaretLineBackgroundColor": QColor( "#aaaaff" ),
"Editor/CaretForegroundColor": QColor( "#000000" ),
"Editor/CaretWidth" : 1,
"Editor/EolMode" : os.linesep,
"Editor/EolVisibility" : False,
"Editor/AutoDetectEol" : False,
"Editor/WhitespaceVisibility" : QsciScintilla.WsInvisible,
"Editor/WrapMode" : QsciScintilla.WrapNone,
"Editor/WrapVisualFlagsEnabled" : False,
"Editor/StartWrapVisualFlag" : QsciScintilla.WrapFlagNone,
"Editor/EndWrapVisualFlag" : QsciScintilla.WrapFlagNone,
"Editor/WrappedLineIndentWidth" : 0,
"Editor/Assotiations/Bash" : "*.sh",
"Editor/Assotiations/Batch" : "*.bat, *.cmd",
"Editor/Assotiations/C#" : "*.cs",
"Editor/Assotiations/C++" : "*.h, *.hh, *.hpp, *.hxx, *.h++, *.c, *.cc, *.cpp, *.cxx, *.c++",
"Editor/Assotiations/CMake" : "*.cmake, CMake.txt",
"Editor/Assotiations/CSS" : "*.css",
"Editor/Assotiations/D" : "*.d",
"Editor/Assotiations/Diff" : "*.diff, *.patch",
"Editor/Assotiations/HTML" : "*.asp, *.xml, *.xsd, *.xsl, *.xslt, *.docbook, *.dtd, *.htm*, *.php*, *.phtm*, *.rdf, *.svg, *.shtm*",
"Editor/Assotiations/IDL" : "*.idl",
"Editor/Assotiations/Java" : "*.java",
"Editor/Assotiations/JavaScript" : "*.js",
"Editor/Assotiations/Lua" : "*.lua",
"Editor/Assotiations/Makefile" : "*.mak, *makefile, Makefile*, *.mk",
"Editor/Assotiations/POV" : "*.pov",
"Editor/Assotiations/Perl" : "*.ph, *.pl, *.pm",
"Editor/Assotiations/Properties" : "*.cfg, *.cnf, *.inf, *.ini, *.properties, *.rc, *.reg",
"Editor/Assotiations/Python" : "*.ptl, *.py, *.py, *.pyw, *.pyx",
"Editor/Assotiations/Ruby" : "*.rb, *.rbw",
"Editor/Assotiations/SQL" : "*.sql",
"Editor/Assotiations/TCL" : "*.tcl",
"Editor/Assotiations/TeX" : "*.aux, *.idx, *.sty, *.toc",
"Editor/Assotiations/VHDL" : "*.vhdl",
"Editor/ConvertTabsUponOpen" : True,
"Editor/CreateBackupUponOpen" : False,
"Editor/AutoEolConversion" : True,
"Editor/AutoDetectIndent" : True,
"Editor/AutoDetectEol" : True,
}

"""
"Editor/LineNumbersMarginEnabled" : True,
"Editor/LineNumbersMarginWidth" : 4,
"Editor/LineNumbersMarginAutoWidth" : True,
"Editor/Folding" : QsciScintilla.BoxedTreeFoldStyle,
"Editor/FoldMarginBackgroundColor": QColor( "#c0c0c0" ),
"Editor/FoldMarginForegroundColor": QColor( "#ffffff" ),
"Editor/MarginsEnabled" : False,
"Editor/MarginsBackgroundColor": QColor( "#c0c0c0" ),
"Editor/MarginsForegroundColor": QColor( "#ffffff" ),
"Editor/MarginsFont" : QFont(),
"""

if sys.platform.startswith('win'):  # Windows platform
    defaults["Editor/DefaultDocumentFont"] = QFont( "Courier", 10 )
elif sys.platform.startswith('darwin'):  # MAC platform
    defaults["Editor/DefaultDocumentFont"] = QFont( "Menlo", 11 )
else:  # probably, Linux
    defaults["Editor/DefaultDocumentFont"] = QFont( "Monospace", 9 )

def value(optionName):  # TODO it is temporary realisation
    return defaults[optionName]

"""
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


    def setDefaultLexerProperties(self, defaultFont, write ):
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
