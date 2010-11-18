'''***************************************************************************
    Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
***************************************************************************'''
#include "pMonkeyStudio.h"
#include "pluginsmanager/PluginsManager.h"
#include "coremanager/MonkeyCore.h"
#include "workspace/pFileManager.h"

#include "workspace/pAbstractChild.h"
#include "qscintillamanager/pEditor.h"

#include <widgets/pQueuedMessageToolBar.h>

#include <qsciapis.h>
#include <qsciglobal.h>
#include "qscilexerbash.h"
#include "qscilexerbatch.h"
#include "qscilexercmake.h"
#include "qscilexercpp.h"
#include "qscilexercsharp.h"
#include "qscilexercss.h"
#include "qscilexerd.h"
#include "qscilexerdiff.h"
#include "qscilexer.h"
#include "qscilexerhtml.h"
#include "qscilexeridl.h"
#include "qscilexerjava.h"
#include "qscilexerjavascript.h"
#include "qscilexerlua.h"
#include "qscilexermakefile.h"
#include "qscilexerperl.h"
#include "qscilexerpov.h"
#include "qscilexerproperties.h"
#include "qscilexerpython.h"
#include "qscilexerruby.h"
#include "qscilexersql.h"
#include "qscilexertex.h"
#include "qscilexervhdl.h"
#if QSCINTILLA_VERSION >= 0x020300
#include "qscilexertcl.h"
#include "qscilexerfortran.h"
#include "qscilexerfortran77.h"
#include "qscilexerpascal.h"
#include "qscilexerpostscript.h"
#include "qscilexerxml.h"
#include "qscilexeryaml.h"
#endif
#if QSCINTILLA_VERSION > 0x020400
#include "qscilexerverilog.h"
#include "qscilexerspice.h"
#endif

#include <QTextCodec>
#include <QImageReader>
#include <QFileDialog>
#include <QFileInfo>
#include <QLocale>

QHash<QString, mGlobalsLexers
QHash<QString, mGlobalsAPIs

'''!
    \details Return True if files point to same file, when files are symbolic link, windows link
    \param left The left file
    \param right The right file
'''
def isSameFile(self, left, right ):
    # get file info
    QFileInfo fif  left :
    QFileInfo fio( right )

    # check files exists
    if  fif.exists() != fio.exists() :
        return False

    # check simlink
    if  fif.isSymLink() :
        fif.setFile( fif.symLinkTarget() )
    if  fio.isSymLink() :
        fio.setFile( fio.symLinkTarget() )

    # check canonical file path
    return fif.canonicalFilePath() == fio.canonicalFilePath()


'''!
    \details Return a list of all know text codecs
'''
def availableTextCodecs(self):
    static QMap<QString, codecs

    if  codecs.isEmpty() :
        for codec in QTextCodec.availableCodecs():
            codecs[ codec.toLower() ] = codec


    return codecs.values()


'''!
    \details Return a list of all know image formats
'''
def availableImageFormats(self):
    static QStringList l
    if  l.isEmpty() :
        for a in QImageReader.supportedImageFormats():
            l << a
        l.sort()

    return l


'''!
    \details Return a lsit of all know qscintilla languages
'''
def availableLanguages(self):
    static QStringList languages

    if  languages.isEmpty() :
        languages = QStringList() << "Bash" << "Batch" << "C#" << "C++" << "CMake" << "CSS"
            << "D" << "Diff" << "HTML" << "IDL" << "Java" << "JavaScript" << "Lua" << "Makefile" << "Perl"
            << "POV" << "Properties" << "Ruby" << "Python" << "SQL" << "TeX" << "VHDL"
#if QSCINTILLA_VERSION >= 0x020300
            << "Fortran" << "Fortran77" << "Pascal" << "PostScript" << "TCL" << "XML" << "YAML"
#endif
#if QSCINTILLA_VERSION > 0x020400
            << "Verilog" << "Spice"
#endif
        

        languages.sort()


    return languages


'''!
    \details Return a QFileInfoList containing folders
    \param fromDir The folder from witch to get contents
    \param filters The filters to apply for validate folders name
    \param recursive If True, folders are scanned recursively, not
'''
def getFolders(self, fromDir, filters, recursive ):
    QFileInfoList files
    foreach ( QFileInfo file, fromDir.entryInfoList( QDir.Dirs | QDir.AllDirs | QDir.NoDotAndDotDot, QDir.Name ) )
        if  filters.isEmpty() or QDir.match( filters, file.fileName() ) :
            files << file
        if  recursive :
            fromDir.cd( file.filePath() )
            files << getFolders( fromDir, filters, recursive )
            fromDir.cdUp()


    return files


'''!
    \details Return a QFileInfoList containing files
    \param fromDir The folder from witch to get contents
    \param filters The filters to apply for validate files name
    \param recursive If True, folders are scanned recursively, not
'''
def getFiles(self, fromDir, filters, recursive ):
    QFileInfoList files
    foreach ( QFileInfo file, fromDir.entryInfoList( QDir.AllEntries | QDir.AllDirs | QDir.NoDotAndDotDot, QDir.DirsFirst | QDir.Name ) )
        if  file.isFile() and ( filters.isEmpty() or QDir.match( filters, file.fileName() ) ) :
            files << file
        elif  file.isDir() and recursive :
            fromDir.cd( file.filePath() )
            files << getFiles( fromDir, filters, recursive )
            fromDir.cdUp()


    return files


'''!
    \details Return a QFileInfoList containing files
    \param fromDir The folder from witch to get contents
    \param filters The filters to apply for validate files name
    \param recursive If True, folders are scanned recursively, not
'''
def getFiles(self, fromDir, filter, recursive ):
{ return getFiles( fromDir, filter.isEmpty() ? QStringList() : QStringList( filter ), recursive );

def getOpenDialog(self, fileMode, caption, fileName, filter, parent, acceptMode = QFileDialog.AcceptOpen ):
    # create dialg
    dlg = QFileDialog( parent, caption, fileName, filter )
    # set file accept mode
    dlg.setAcceptMode( acceptMode )
    # set file mode
    dlg.setFileMode( fileMode )
    # return dialog
    return dlg


'''!
    \details A dialog that return a list of files name choosen from available know image formats
    \param caption The window title
    \param fileName The default filename to select ( or path )
    \param parent The parent widget
'''
def getImageFileNames(self, caption, fileName, parent ):
    # get image filters
    QStringList filters
    for filter in availableImageFormats():
        filters << QObject.tr( "%1 Files (*.%2)" ).arg( filter.toUpper() ).arg( filter )
    # add all format as one filter at begining
    if  not filters.isEmpty() :
        filters.prepend( QObject.tr( "All Image Files (%1)" ).arg( QStringList( availableImageFormats() ).replaceInStrings( QRegExp( "^(.*)$" ), "*.\\1" ).join( " " ) ) )
    # create dialog
    dlg = getOpenDialog( QFileDialog.ExistingFiles, caption.isEmpty() ? QObject.tr( "Select image(s)" ) : caption, fileName, filters.join( ";;" ), parent )
    # choose last used filter if available
    if  not filters.isEmpty() :
        dlg.selectFilter( MonkeyCore.settings().value( "Recents/ImageFilter" ).toString() )
    # execute dialog
    if  dlg.exec() :
        # remember last filter if available
        if  not filters.isEmpty() :
            MonkeyCore.settings().setValue( "Recents/ImageFilter", dlg.selectedFilter() )
        # remember selected files
        filters = dlg.selectedFiles()
        # delete dialog
        delete dlg
        # return selected files
        return filters

    # delete dialog
    delete dlg
    # return empty list
    return QStringList()


'''!
    \details A dialog that return a file name choosen from available know image formats
    \param caption The window title
    \param fileName The default filename to select ( or path )
    \param parent The parent widget
'''
def getImageFileName(self, caption, fileName, parent ):
{ return getImageFileNames( caption, fileName, parent ).value( 0 );

'''!
    \details Return a QStringList of files name
    \param caption The window title
    \param fileName The default filename to select ( or path )
    \param filter The filter to apply
    \param parent The parent widget
'''
def getOpenFileNames(self, caption, fileName, filter, parent ):
    # create dialg
    dlg = getOpenDialog( QFileDialog.ExistingFiles, caption.isEmpty() ? QObject.tr( "Select file(s)" ) : caption, fileName, filter, parent )
    # choose last used filter if available
    if  not filter.isEmpty() :
        dlg.selectFilter( MonkeyCore.settings().value( "Recents/FileFilter" ).toString() )
    # execute dialog
    if  dlg.exec() :
        # remember last filter if available
        if  not filter.isEmpty() :
            MonkeyCore.settings().setValue( "Recents/FileFilter", dlg.selectedFilter() )
        # remember selected files
        files = dlg.selectedFiles()
        # delete dialog
        delete dlg
        # return selected files
        return files

    # delete dialog
    delete dlg
    # return empty list
    return QStringList()


'''!
    \details Return a QString file name
    \param caption The window title
    \param fileName The default filename to select ( or path )
    \param filter The filter to apply
    \param parent The parent widget
'''
def getOpenFileName(self, caption, fileName, filter, parent ):
{ return getOpenFileNames( caption, fileName, filter, parent ).value( 0 );

'''!
    \details Return a QString file name
    \param caption The window title
    \param fileName The default filename to select ( or path )
    \param filter The filter to apply
    \param parent The parent widget
'''
def getSaveFileName(self, caption, fileName, filter, parent ):
    # create dialg
    dlg = getOpenDialog( QFileDialog.AnyFile, caption.isEmpty() ? QObject.tr( "Choose a filename" ) : caption, fileName, filter, parent, QFileDialog.AcceptSave )
    # choose last used filter if available
    if  not filter.isEmpty() :
        dlg.selectFilter( MonkeyCore.settings().value( "Recents/FileFilter" ).toString() )
    # execute dialog
    if  dlg.exec() :
        # remember last filter if available
        if  not filter.isEmpty() :
            MonkeyCore.settings().setValue( "Recents/FileFilter", dlg.selectedFilter() )
        # remember selected files
        files = dlg.selectedFiles()
        # delete dialog
        delete dlg
        # return selected files
        return files.value( 0 )

    # delete dialog
    delete dlg
    # return empty list
    return QString()


'''!
    \details Convenient function for get an existing folder
    \param caption The window title
    \param fileName The default path to shown
    \param parent The parent widget
'''
def getExistingDirectory(self, caption, fileName, parent ):
{ return QFileDialog.getExistingDirectory( parent, caption.isEmpty() ? QObject.tr( "Select a folder" ) : caption, fileName );

'''!
    \details Return a tokenized string, the token $HOME$ is replaced by the home path of the user
    \param string The string to tokenize
'''
def tokenizeHome(self, string ):
{ return QString( string ).replace( QDir.homePath(), "$HOME$" );

'''!
    \details Return an untokenized string, the home path is replaced by $HOME$
    \param string The string to untokenize
'''
def unTokenizeHome(self, string ):
{ return QString( string ).replace( "$HOME$", QDir.homePath() );

'''!
    \details Return all available languages suffixes
'''
QMap<QString, pMonkeyStudio.availableLanguagesSuffixes()
    return MonkeyCore.fileManager().associations()


'''!
    \details Return all available files suffixes
'''
QMap<QString, pMonkeyStudio.availableFilesSuffixes()
    # get language suffixes
    QMap<QString, l = availableLanguagesSuffixes()
    # add child plugins suffixes
    QMap<QString, ps = MonkeyCore.pluginsManager().childSuffixes()
    for k in ps.keys():
        foreach ( QString s, ps[k] )
            if  not l[k].contains( s ) :
                l[k] << s
    # return list
    return l


'''!
    \details Return all available languages filters
'''
def availableLanguagesFilters(self):
    QString f
    # get suffixes
    QMap<QString, sl = availableLanguagesSuffixes()
    #
    for k in sl.keys():
        f += QString( "%1 Files (%2);;" ).arg( k ).arg( sl.value( k ).join( " " ) )
    # remove trailing ;
    if  f.endsWith( ";;" ) :
        f.chop( 2 )
    # return filters list
    return f


'''!
    \details Return all available files filters
'''
def availableFilesFilters(self):
    QString f
    # get suffixes
    QMap<QString, sl = availableFilesSuffixes()
    #
    for k in sl.keys():
        f += QString( "%1 Files (%2);;" ).arg( k ).arg( sl.value( k ).join( " " ) )
    # remove trailing ;
    if  f.endsWith( ";;" ) :
        f.chop( 2 )

    if  not f.isEmpty() :
        QString s
        for l in availableFilesSuffixes().values():
            s.append( l.join( " " ).append( " " ) )
        f.prepend( QString( "All Files (*);;" ))
        f.prepend( QString( "All Supported Files (%1);;" ).arg( s.trimmed() ) )


    # return filters list
    return f


'''!
    \details Return the base settings path used by all option in self namespace
'''
def settingsPath(self):
    return "/Settings"


'''!
    \details Return the scintilla settigns path
'''
def scintillaSettingsPath(self):
    return "/Scintilla"


'''!
    \details Reload all available api files
'''
def prepareAPIs(self):
    # check lexers & apis
    if  mGlobalsLexers.isEmpty() or mGlobalsAPIs.isEmpty() :
        # free hashes
        qDeleteAll( mGlobalsLexers )
        mGlobalsLexers.clear()
        qDeleteAll( mGlobalsAPIs )
        mGlobalsAPIs.clear()

    # get monkey status bar
    sbar = MonkeyCore.messageManager()
    # iterate each language
    for ln in availableLanguages():
        l = lexerForLanguage( ln )
        a = apisForLexer( l )
        # clear raw api
        a.clear()
        # load prepared files
        for f in MonkeyCore.settings(:.value( QString( "SourceAPIs/" ).append( ln ) ).toStringList() )
            if  not a.load( QDir.isRelativePath( f ) ? qApp.applicationDirPath().append( "/%1" ).arg( f ) : f ) :
                sbar.appendMessage( QObject.tr( "Can't load api file: '%1'" ).arg( QFileInfo( f ).fileName() ) )

        # start prepare for apis
        a.prepare()



'''!
    \details Return a QsciAPIs for the given lexer
    \param lexer The lexer to get apis object
'''
def apisForLexer(self, lexer ):
    # cancel if no lexer
    if  not lexer :
        return 0
    # check if apis already exists
    if  not mGlobalsAPIs.contains( lexer.language() ) :
        # create apis
        apis = QsciAPIs( lexer )
        # store global apis
        mGlobalsAPIs[lexer.language()] = apis

    # return apis
    return mGlobalsAPIs.value( lexer.language() )


'''!
    \details Return the language of a file name
    \param fileName The fil name to get language from
'''
def languageForFileName(self, fileName ):
    lexer = lexerForFileName( fileName )
    return lexer ? QString( lexer.language() ) : QString()


'''!
    \details Return a QsciLexer for the given file name
    \param fileName The filenae to get lexer from
'''
def lexerForFileName(self, fileName ):
    # get suffixes
    QMap<QString, l = availableFilesSuffixes()
    # check suffixe
    for k in l.keys():
        if  QDir.match( l.value( k ), fileName ) :
            return lexerForLanguage( k )
    return 0


'''!
    \details Return a QsciLexer for the given language
    \param language The language to get lexer from
'''
def lexerForLanguage(self, language ):
    if  mGlobalsLexers.keys().contains( language ) :
        return mGlobalsLexers.value( language )
    # get language
     ln = language.toLower()
    # lexer
    l = 0
    # init lexer
    if  ln == "bash" :
        l = QsciLexerBash( QApplication.instance() )
    elif  ln == "batch" :
        l = QsciLexerBatch( QApplication.instance() )
    elif  ln == "c#" :
        l = QsciLexerCSharp( QApplication.instance() )
    elif  ln == "c++" :
        l = QsciLexerCPP( QApplication.instance() )
    elif  ln == "cmake" :
        l = QsciLexerCMake( QApplication.instance() )
    elif  ln == "css" :
        l = QsciLexerCSS( QApplication.instance() )
    elif  ln == "d" :
        l = QsciLexerD( QApplication.instance() )
    elif  ln == "diff" :
        l = QsciLexerDiff( QApplication.instance() )
    elif  ln == "html" :
        l = QsciLexerHTML( QApplication.instance() )
    elif  ln == "idl" :
        l = QsciLexerIDL( QApplication.instance() )
    elif  ln == "java" :
        l = QsciLexerJava( QApplication.instance() )
    elif  ln == "javascript" :
        l = QsciLexerJavaScript( QApplication.instance() )
    elif  ln == "lua" :
        l = QsciLexerLua( QApplication.instance() )
    elif  ln == "makefile" :
        l = QsciLexerMakefile( QApplication.instance() )
    elif  ln == "pov" :
        l = QsciLexerPOV( QApplication.instance() )
    elif  ln == "perl" :
        l = QsciLexerPerl( QApplication.instance() )
    elif  ln == "properties" :
        l = QsciLexerProperties( QApplication.instance() )
    elif  ln == "python" :
        l = QsciLexerPython( QApplication.instance() )
    elif  ln == "ruby" :
        l = QsciLexerRuby( QApplication.instance() )
    elif  ln == "sql" :
        l = QsciLexerSQL( QApplication.instance() )
    elif  ln == "tex" :
        l = QsciLexerTeX( QApplication.instance() )
    elif  ln == "vhdl" :
        l = QsciLexerVHDL( QApplication.instance() )
#if QSCINTILLA_VERSION >= 0x020300
    elif  ln == "tcl" :
        l = QsciLexerTCL( QApplication.instance() )
    elif  ln == "fortran" :
        l = QsciLexerFortran( QApplication.instance() )
    elif  ln == "fortran77" :
        l = QsciLexerFortran77( QApplication.instance() )
    elif  ln == "pascal" :
        l = QsciLexerPascal( QApplication.instance() )
    elif  ln == "postscript" :
        l = QsciLexerPostScript( QApplication.instance() )
    elif  ln == "xml" :
        l = QsciLexerXML( QApplication.instance() )
    elif  ln == "yaml" :
        l = QsciLexerYAML( QApplication.instance() )
#endif
#if QSCINTILLA_VERSION > 0x020400
    elif  ln == "verilog" :
        l = QsciLexerVerilog( QApplication.instance() )
    elif  ln == "spice" :
        l = QsciLexerSpice( QApplication.instance() )
#endif
    # init lexer settings
    if  l :
        # add lexer to global lexers hash
        mGlobalsLexers[l.language()] = l
        # read settings
        ss = MonkeyCore.settings()
        l.readSettings( *ss, scintillaSettingsPath().toLocal8Bit().constData() )
        # set apis
        l.setAPIs( apisForLexer( l ) )

    # return lexer
    return l


'''!
    \details Return True if can set \c property for \c lexer to \c value else return False
    \param property The property name
    \param lexer The lexer to modify
    \param value The value to set
'''
def setLexerProperty(self, property, lexer, value ):
    # cancel no property, lexer or if variant is not valid
    if  not lexer or property.trimmed().isEmpty() or not value.isValid() :
        return False
    # if bool
    if  value.type() == QVariant.Bool :
        return QMetaObject.invokeMethod( lexer, property.toLocal8Bit().constData(), Q_ARG( bool, value.toBool() ) )
    # if int
    elif  value.type() == QVariant.Int :
        return QMetaObject.invokeMethod( lexer, property.toLocal8Bit().constData(), Q_ARG( QsciLexerPython.IndentationWarning, (QsciLexerPython.IndentationWarning)value.toInt() ) )
    # return default value
    return False


'''!
    \details Return a lexer property value
    \param property The property to query
    \param lexer The lexer to query property from
'''
def lexerProperty(self, property, lexer ):
    # if no member or lexer return null variant
    if  not lexer or property.isEmpty() :
        return QVariant()
    # get language
     lng = QString( lexer.language() ).toLower()
    # checking property
    if  property == "foldComments" :
        if  lng == "bash" :
            return qobject_cast<QsciLexerBash*>( lexer ).foldComments()
        elif  lng == "css" :
            return qobject_cast<QsciLexerCSS*>( lexer ).foldComments()
        elif  lng == "d" :
            return qobject_cast<QsciLexerD*>( lexer ).foldComments()
        elif  lng == "perl" :
            return qobject_cast<QsciLexerPerl*>( lexer ).foldComments()
        elif  lng == "pov" :
            return qobject_cast<QsciLexerPOV*>( lexer ).foldComments()
        elif  lng == "python" :
            return qobject_cast<QsciLexerPython*>( lexer ).foldComments()
        elif  lng == "sql" :
            return qobject_cast<QsciLexerSQL*>( lexer ).foldComments()
        elif  lng == "vhdl" :
            return qobject_cast<QsciLexerVHDL*>( lexer ).foldComments()
        elif  lng == "javascript" :
            return qobject_cast<QsciLexerJavaScript*>( lexer ).foldComments()
        elif  lng == "java" :
            return qobject_cast<QsciLexerJava*>( lexer ).foldComments()
        elif  lng == "c#" :
            return qobject_cast<QsciLexerCSharp*>( lexer ).foldComments()
        elif  lng == "c++" :
            return qobject_cast<QsciLexerCPP*>( lexer ).foldComments()
#if QSCINTILLA_VERSION >= 0x020300
        elif  lng == "pascal" :
            return qobject_cast<QsciLexerPascal*>( lexer ).foldComments()
        elif  lng == "yaml" :
            return qobject_cast<QsciLexerYAML*>( lexer ).foldComments()
#endif
#if QSCINTILLA_VERSION > 0x020400
        elif  lng == "verilog" :
            return qobject_cast<QsciLexerVerilog*>( lexer ).foldComments()
#endif

    elif  property == "foldCompact" :
        if  lng == "bash" :
            return qobject_cast<QsciLexerBash*>( lexer ).foldCompact()
        elif  lng == "css" :
            return qobject_cast<QsciLexerCSS*>( lexer ).foldCompact()
        elif  lng == "d" :
            return qobject_cast<QsciLexerD*>( lexer ).foldCompact()
        elif  lng == "html" :
            return qobject_cast<QsciLexerHTML*>( lexer ).foldCompact()
        elif  lng == "lua" :
            return qobject_cast<QsciLexerLua*>( lexer ).foldCompact()
        elif  lng == "perl" :
            return qobject_cast<QsciLexerPerl*>( lexer ).foldCompact()
        elif  lng == "pov" :
            return qobject_cast<QsciLexerPOV*>( lexer ).foldCompact()
        elif  lng == "properties" :
            return qobject_cast<QsciLexerProperties*>( lexer ).foldCompact()
        elif  lng == "sql" :
            return qobject_cast<QsciLexerSQL*>( lexer ).foldCompact()
        elif  lng == "vhdl" :
            return qobject_cast<QsciLexerVHDL*>( lexer ).foldCompact()
        elif  lng == "javascript" :
            return qobject_cast<QsciLexerJavaScript*>( lexer ).foldCompact()
        elif  lng == "java" :
            return qobject_cast<QsciLexerJava*>( lexer ).foldCompact()
        elif  lng == "c#" :
            return qobject_cast<QsciLexerCSharp*>( lexer ).foldCompact()
        elif  lng == "c++" :
            return qobject_cast<QsciLexerCPP*>( lexer ).foldCompact()
#if QSCINTILLA_VERSION >= 0x020300
        elif  lng == "tcl" :
            return qobject_cast<QsciLexerTCL*>( lexer ).foldCompact()
        elif  lng == "fortran" :
            return qobject_cast<QsciLexerFortran*>( lexer ).foldCompact()
        elif  lng == "fortran77" :
            return qobject_cast<QsciLexerFortran77*>( lexer ).foldCompact()
        elif  lng == "pascal" :
            return qobject_cast<QsciLexerPascal*>( lexer ).foldCompact()
        elif  lng == "postscript" :
            return qobject_cast<QsciLexerPostScript*>( lexer ).foldCompact()
        elif  lng == "xml" :
            return qobject_cast<QsciLexerXML*>( lexer ).foldCompact()
#endif
#if QSCINTILLA_VERSION > 0x020400
        elif  lng == "verilog" :
            return qobject_cast<QsciLexerVerilog*>( lexer ).foldCompact()
#endif

    elif  property == "foldQuotes" :
        if  lng == "python" :
            return qobject_cast<QsciLexerPython*>( lexer ).foldQuotes()

    elif  property == "foldDirectives" :
        if  lng == "pov" :
            return qobject_cast<QsciLexerPOV*>( lexer ).foldDirectives()

    elif  property == "foldAtBegin" :
        if  lng == "vhdl" :
            return qobject_cast<QsciLexerVHDL*>( lexer ).foldAtBegin()

    elif  property == "foldAtParenthesis" :
        if  lng == "vhdl" :
            return qobject_cast<QsciLexerVHDL*>( lexer ).foldAtParenthesis()

    elif  property == "foldAtElse" :
        if  lng == "cmake" :
            return qobject_cast<QsciLexerCMake*>( lexer ).foldAtElse()
        elif  lng == "d" :
            return qobject_cast<QsciLexerD*>( lexer ).foldAtElse()
        elif  lng == "vhdl" :
            return qobject_cast<QsciLexerVHDL*>( lexer ).foldAtElse()
        elif  lng == "javascript" :
            return qobject_cast<QsciLexerJavaScript*>( lexer ).foldAtElse()
        elif  lng == "java" :
            return qobject_cast<QsciLexerJava*>( lexer ).foldAtElse()
        elif  lng == "c#" :
            return qobject_cast<QsciLexerCSharp*>( lexer ).foldAtElse()
        elif  lng == "c++" :
            return qobject_cast<QsciLexerCPP*>( lexer ).foldAtElse()
#if QSCINTILLA_VERSION >= 0x020300
        elif  lng == "postscript" :
            return qobject_cast<QsciLexerPostScript*>( lexer ).foldAtElse()
#endif
#if QSCINTILLA_VERSION > 0x020400
        elif  lng == "verilog" :
            return qobject_cast<QsciLexerVerilog*>( lexer ).foldAtElse()
#endif

    elif  property == "foldAtModule" :
#if QSCINTILLA_VERSION > 0x020400
        if  lng == "verilog" :
            return qobject_cast<QsciLexerVerilog*>( lexer ).foldAtModule()
#endif

    elif  property == "foldPreprocessor" :
        if  lng == "html" :
            return qobject_cast<QsciLexerHTML*>( lexer ).foldPreprocessor()
        elif  lng == "javascript" :
            return qobject_cast<QsciLexerJavaScript*>( lexer ).foldPreprocessor()
        elif  lng == "java" :
            return qobject_cast<QsciLexerJava*>( lexer ).foldPreprocessor()
        elif  lng == "c#" :
            return qobject_cast<QsciLexerCSharp*>( lexer ).foldPreprocessor()
        elif  lng == "c++" :
            return qobject_cast<QsciLexerCPP*>( lexer ).foldPreprocessor()
#if QSCINTILLA_VERSION >= 0x020300
        elif  lng == "pascal" :
            return qobject_cast<QsciLexerPascal*>( lexer ).foldPreprocessor()
        elif  lng == "xml" :
            return qobject_cast<QsciLexerXML*>( lexer ).foldPreprocessor()
#endif
#if QSCINTILLA_VERSION > 0x020400
        elif  lng == "verilog" :
            return qobject_cast<QsciLexerVerilog*>( lexer ).foldPreprocessor()
#endif

    elif  property == "stylePreprocessor" :
        if  lng == "javascript" :
            return qobject_cast<QsciLexerJavaScript*>( lexer ).stylePreprocessor()
        elif  lng == "java" :
            return qobject_cast<QsciLexerJava*>( lexer ).stylePreprocessor()
        elif  lng == "c#" :
            return qobject_cast<QsciLexerCSharp*>( lexer ).stylePreprocessor()
        elif  lng == "c++" :
            return qobject_cast<QsciLexerCPP*>( lexer ).stylePreprocessor()

    elif  property == "caseSensitiveTags" :
        if  lng == "html" :
            return qobject_cast<QsciLexerHTML*>( lexer ).caseSensitiveTags()
#if QSCINTILLA_VERSION >= 0x020300
        elif  lng == "xml" :
            return qobject_cast<QsciLexerXML*>( lexer ).caseSensitiveTags()
#endif

    elif  property == "backslashEscapes" :
        if  lng == "sql" :
            return qobject_cast<QsciLexerSQL*>( lexer ).backslashEscapes()

    elif  property == "indentationWarning" :
        if  lng == "python" :
            return qobject_cast<QsciLexerPython*>( lexer ).indentationWarning()

    # default return value
    return QVariant()


'''!
    \details Reset the properties of a lexer
    \param lexer The lexer to reset
'''
def resetLexer(self, lexer ):
    # cancel if no lexer
    if  not lexer :
        return
    # get settings pointer
    settings = MonkeyCore.settings()
    # remove lexer entry
    settings.remove( QString( "%1/%2" ).arg( scintillaSettingsPath() ).arg( lexer.language() ) )
    # set default styles & font
    lexer.setDefaultFont( defaultDocumentFont() )
    for ( i = 0; i < 128; ++i )
        if  not lexer.description( i ).isEmpty() :
            lexer.setColor( lexer.defaultColor( i ), i )
            lexer.setEolFill( lexer.defaultEolFill( i ), i )
            lexer.setFont( lexer.defaultFont( i ), i )
            lexer.setPaper( lexer.defaultPaper( i ), i )


    # re read properties
    lexer.readSettings( *settings, scintillaSettingsPath().toLocal8Bit().constData() )


'''!
    \details Apply the settings ( after having pressed apply/ok in the settings dialog )
'''
def applyProperties(self):
    # apply editor properties
    for c in MonkeyCore.workspace().documents():
        foreach ( pEditor* e, c.findChildren<pEditor*>() )
            setEditorProperties( e )
    # apply lexers properties
    ss = MonkeyCore.settings()
    for l in mGlobalsLexers.values():
        # refresh properties
        l.readSettings( *ss, scintillaSettingsPath().toLocal8Bit().constData() )
        # refresh default pen/paper if needed
        l.setDefaultFont( defaultDocumentFont() )
        if  defaultDocumentColours() :
            l.setDefaultColor( defaultDocumentPen() )
            l.setDefaultPaper( defaultDocumentPaper() )


    # reloads apis
    prepareAPIs()


'''!
    \details Apply properties to the given \c editor
    \param editor The editor to set properties
'''
def setEditorProperties(self, editor ):
    if  not editor :
        return
    # apply settings from UISettings
    # General
    editor.setSelectionBackgroundColor( selectionBackgroundColor() )
    editor.setSelectionForegroundColor( selectionForegroundColor() )
    if  defaultDocumentColours() :
        # set scintilla default colors
        editor.setColor( defaultDocumentPen() )
        editor.setPaper( defaultDocumentPaper() )

    editor.setFont( defaultDocumentFont() )
    # Auto Completion
    editor.setAutoCompletionCaseSensitivity( autoCompletionCaseSensitivity() )
    editor.setAutoCompletionReplaceWord( autoCompletionReplaceWord() )
    editor.setAutoCompletionShowSingle( autoCompletionShowSingle() )
    editor.setAutoCompletionSource( autoCompletionSource() )
    editor.setAutoCompletionThreshold( autoCompletionThreshold() )
    # CallTips
    editor.setCallTipsBackgroundColor( callTipsBackgroundColor() )
    editor.setCallTipsForegroundColor( callTipsForegroundColor() )
    editor.setCallTipsHighlightColor( callTipsHighlightColor() )
    editor.setCallTipsStyle( callTipsStyle() )
    editor.setCallTipsVisible( callTipsVisible() )
    # Indentation
    editor.setAutoIndent( autoIndent() )
    editor.setBackspaceUnindents( backspaceUnindents() )
    editor.setIndentationGuides( indentationGuides() )
    editor.setIndentationsUseTabs( indentationsUseTabs() )
    editor.setIndentationWidth( indentationWidth() )
    editor.setTabIndents( tabIndents() )
    editor.setTabWidth( tabWidth() )
    editor.setIndentationGuidesBackgroundColor( indentationGuidesBackgroundColor() )
    editor.setIndentationGuidesForegroundColor( indentationGuidesForegroundColor() )
    # Brace Matching
    editor.setBraceMatching( braceMatching() )
    editor.setMatchedBraceBackgroundColor( matchedBraceBackgroundColor() )
    editor.setMatchedBraceForegroundColor( matchedBraceForegroundColor() )
    editor.setUnmatchedBraceBackgroundColor( unmatchedBraceBackgroundColor() )
    editor.setUnmatchedBraceForegroundColor( unmatchedBraceForegroundColor() )
    # Edge Mode
    editor.setEdgeMode( edgeMode() )
    editor.setEdgeColor( edgeColor() )
    editor.setEdgeColumn( edgeColumn() )
    # Caret
    editor.setCaretLineVisible( caretLineVisible() )
    editor.setCaretLineBackgroundColor( caretLineBackgroundColor() )
    editor.setCaretForegroundColor( caretForegroundColor() )
    editor.setCaretWidth( caretWidth() )
    # Margins
    if  marginsEnabled() :
        editor.setMarginsBackgroundColor( marginsBackgroundColor() )
        editor.setMarginsForegroundColor( marginsForegroundColor() )
        editor.setMarginsFont( marginsFont() )

    editor.setLineNumbersMarginEnabled( lineNumbersMarginEnabled() )
    editor.setLineNumbersMarginWidth( lineNumbersMarginWidth() )
    editor.setLineNumbersMarginAutoWidth( lineNumbersMarginAutoWidth() )
    editor.setFolding( folding() )
    editor.setFoldMarginColors( foldMarginForegroundColor(), foldMarginBackgroundColor() )
    # Special Characters
    editor.setEolMode( eolMode() )
    editor.setEolVisibility( eolVisibility() )
    editor.setWhitespaceVisibility( whitespaceVisibility() )
    editor.setWrapMode( wrapMode() )
    editor.setWrapVisualFlags( endWrapVisualFlag(), startWrapVisualFlag(), wrappedLineIndentWidth() )


'''!
    \details control if mac widgets show their focus rect or not.
    \param widget The widget to apply
    \param show Control focus rect visibility
    \param recursive If True, are updated too, not
'''
def showMacFocusRect(self, widget, show, recursive ):
    QList<QWidget*> widgets

    widgets << widget

    if  recursive :
        widgets << widget.findChildren<QWidget*>()


    for w in widgets:
        w.setAttribute( Qt.WA_MacShowFocusRect, show )



'''!
    \details control if mac widgets use small size.
    \param widget The widget to apply
    \param small Control small activation
    \param recursive If True, are updated too, not
'''
def setMacSmallSize(self, widget, small, recursive ):
    QList<QWidget*> widgets

    widgets << widget

    if  recursive :
        widgets << widget.findChildren<QWidget*>()


    for w in widgets:
        w.setAttribute( Qt.WA_MacSmallSize, small )



'''!
    \details Save files on custom actions triggered ( builder, debugger, interpreter )
    \param save True to save, False
'''
def setSaveFilesOnCustomAction(self, save ):
{ MonkeyCore.settings().setValue( settingsPath() +"/SaveFilesOnCustomAction", save );

'''!
    \details Return True if files are saved on custom actions triggered, False
'''
def saveFilesOnCustomAction(self):
{ return MonkeyCore.settings().value( settingsPath() +"/SaveFilesOnCustomAction", False ).toBool();

'''!
    \details Set if tabs have close button
    \param have True to have button, False
'''
def setTabsHaveCloseButton(self, have ):
{ MonkeyCore.settings().setValue( settingsPath() +"/TabsHaveCloseButton", have );

'''!
    \details Return if tabs have  close button
'''
def tabsHaveCloseButton(self):
{ return MonkeyCore.settings().value( settingsPath() +"/TabsHaveCloseButton", False ).toBool();

'''!
    \details Set tabs have shortcut
    \param have True for shortcut, False
'''
def setTabsHaveShortcut(self, have ):
{ MonkeyCore.settings().setValue( settingsPath() +"/TabsHaveShortcut", have );

'''!
    \details Return True if tabs have shortcut, False
'''
def tabsHaveShortcut(self):
{ return MonkeyCore.settings().value( settingsPath() +"/TabsHaveShortcut", False ).toBool();

'''!
    \details Set tabs text are elided
    \param elided True for elided text, False
'''
def setTabsElided(self, have ):
{ MonkeyCore.settings().setValue( settingsPath() +"/TabsElided", have );

'''!
    \details Return True if tabs text is elided, False
'''
def tabsElided(self):
{ return MonkeyCore.settings().value( settingsPath() +"/TabsElided", False ).toBool();

'''!
    \details Set tabs text color
    \param color The tabs text color
'''
def setTabsTextColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/TabsTextColor", color );

'''!
    \details Return the tabs text color
'''
def tabsTextColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/TabsTextColor", QColor( Qt.black ) ).value<QColor>();

'''!
    \details Set the current tab text color
    \param color The current tab text color
'''
def setCurrentTabTextColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CurrentTabTextColor", color );

'''!
    \details Return the current tab text color
'''
def currentTabTextColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CurrentTabTextColor", QColor( Qt.blue ) ).value<QColor>();

'''!
    \details Set the workspace doc mode
    \param mode The mode to apply
'''
def setDocumentMode(self, mode ):
{ MonkeyCore.settings().setValue( settingsPath() +"/DocMode", mode );

'''!
    \details Return the mod used by the workspace
'''
def documentMode(self):
{ return (pWorkspace.ViewMode)MonkeyCore.settings().value( settingsPath() +"/DocMode", pWorkspace.NoTabs ).toInt();

'''!
    \details Set if session must be save on close
    \param save If True, is saved, not
'''
def setSaveSessionOnClose(self, save ):
{ MonkeyCore.settings().setValue( settingsPath() +"/SaveSessionOnClose", save );

'''!
    \details Return True if session is saved at close, False
'''
def saveSessionOnClose(self):
{ return MonkeyCore.settings().value( settingsPath() +"/SaveSessionOnClose", True ).toBool();

'''!
    \details Set if session is restored on startup
    \param restore If True, will be restored on startup, not
'''
def setRestoreSessionOnStartup(self, restore ):
{ MonkeyCore.settings().setValue( settingsPath() +"/RestoreSessionOnStartup", restore );

'''!
    \details Return True if session will be restored on startup, False
'''
def restoreSessionOnStartup(self):
{ return MonkeyCore.settings().value( settingsPath() +"/RestoreSessionOnStartup", True ).toBool();

'''!
    \details Set if quick file access combobox is visible in context toolbar
    \param show If True, is visible, it's not visible
'''
def setShowQuickFileAccess(self, show ):
{ MonkeyCore.settings().setValue( settingsPath() +"/ShowQuickFileAccess", show );

'''!
    \details Return True if a quick file access combobox is visible in the child context toolbar
'''
def showQuickFileAccess(self):
{ return MonkeyCore.settings().value( settingsPath() +"/ShowQuickFileAccess", False ).toBool();

'''!
    \details Set the sorting mode used by the Opened Files List dock
    \param mode Specify the used mode
'''
def setOpenedFileSortingMode(self, mode ):
{ MonkeyCore.settings().setValue( settingsPath() +"/OpenedFileSortingMode", mode );

'''!
    \details Return the sorting mode used by the Opened Files List dock
'''
def openedFileSortingMode(self):
{ return (pOpenedFileModel.SortMode)MonkeyCore.settings().value( settingsPath() +"/OpenedFileSortingMode", pOpenedFileModel.OpeningOrder ).toInt();

'''!
    \details Set if auto syntax check is performed
    \param activate If True, syntax check will be performed, not
'''
def setAutoSyntaxCheck(self, activate ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoSyntaxCheck", activate );

'''!
    \details Return True if auto syntax check is performed, False
'''
def autoSyntaxCheck(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoSyntaxCheck", False ).toBool();

'''!
    \details Set is tabs are converted upon open
    \param convert If True tabs will be converted, not
'''
def setConvertTabsUponOpen(self, convert ):
{ MonkeyCore.settings().setValue( settingsPath() +"/ConvertTabsUponOpen", convert );

'''!
    \details Return True if tabs are converted upon open, False
'''
def convertTabsUponOpen(self):
{ return MonkeyCore.settings().value( settingsPath() +"/ConvertTabsUponOpen", False ).toBool();

'''!
    \details Set if file are backup upon open
    \param backup If True, is backup upon open
'''
def setCreateBackupUponOpen(self, backup ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CreateBackupUponOpen", backup );

'''!
    \details Return True if file is backup upon open, False
'''
def createBackupUponOpen(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CreateBackupUponOpen", False ).toBool();

'''!
    \details Set if eol are convert upon open
    \param convert If True, are convert, not
'''
def setAutoEolConversion(self, convert ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoEolConversion", convert );

'''!
    \details Return True if eol are convert, False
'''
def autoEolConversion(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoEolConversion", True ).toBool();

'''!
    \details Set the default used codec for opening/saving files
    \param codec The codec to use
'''
def setDefaultCodec(self, codec ):
{ MonkeyCore.settings().setValue( settingsPath() +"/DefaultCodec", codec );

'''!
    \details Return the default used codec for opening/saving files. Default UTF-8
'''
def defaultCodec(self):
{ return MonkeyCore.settings().value( settingsPath() +"/DefaultCodec", "UTF-8" ).toString();

'''!
    \details Set the selection background color
    \param color The color to apply
'''
def setSelectionBackgroundColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/SelectionBackgroundColor", color );

'''!
    \details Return the selection background color
'''
def selectionBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/SelectionBackgroundColor", QColor( "#bdff9b" ) ).value<QColor>();

'''!
    \details Set the selection foreground color
    \param color The color to apply
'''
def setSelectionForegroundColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/SelectionForegroundColor", color );

'''!
    \details Return the selection foreground color
'''
def selectionForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/SelectionForegroundColor", QColor( "#000000" ) ).value<QColor>();

'''!
    \details Set if editors got default colors or no
    \param useDefault If True, default pen and paper for editors, use custom one
'''
def setDefaultDocumentColours(self, useDefault ):
{ MonkeyCore.settings().setValue( settingsPath() +"/DefaultDocumentColours", useDefault );

'''!
    \details Return if editors use default colros or custom one
'''
def defaultDocumentColours(self):
{ return MonkeyCore.settings().value( settingsPath() +"/DefaultDocumentColours", False ).toBool();

'''!
    \details Set custom editor pen color
    \param color The color to apply
'''
def setDefaultDocumentPen(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/DefaultDocumentPen", color );

'''!
    \details Return the custom editor pen color
'''
def defaultDocumentPen(self):
{ return MonkeyCore.settings().value( settingsPath() +"/DefaultDocumentPen", QColor( Qt.black ) ).value<QColor>();

'''!
    \details Set the custom editor paper color
    \param color The color to apply
'''
def setDefaultDocumentPaper(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/DefaultDocumentPaper", color );

'''!
    \details Return the custom editor paper color
'''
def defaultDocumentPaper(self):
{ return MonkeyCore.settings().value( settingsPath() +"/DefaultDocumentPaper", QColor( Qt.white ) ).value<QColor>();

'''!
    \details Set the custom editor font
    \param font The font to apply
'''
def setDefaultDocumentFont(self, font ):
{ MonkeyCore.settings().setValue( settingsPath() +"/DefaultDocumentFont", font );

'''!
    \details Return the custom editor font
'''
def defaultDocumentFont(self):
    QFont font

#if defined( Q_OS_WIN )
    font = QFont( "Courier", 10 )
#elif defined( Q_OS_MAC )
    font = QFont( "Monaco", 11 )
    #if defined( MAC_OS_X_VERSION_10_6 )
        font = QFont( "Menlo", 11 )
    #endif
#else:
    font = QFont( "Monospace", 9 )
#endif

    return MonkeyCore.settings().value( settingsPath() +"/DefaultDocumentFont", font ).value<QFont>()


f    \details Set auto completion is case sensitive or not
    \param sensitive If True auto completion is case sensitive, not
'''
def setAutoCompletionCaseSensitivity(self, sensitive ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoCompletionCaseSensitivity", sensitive );

'''!
    \details Return True if auto completion is case sensitive, False
'''
def autoCompletionCaseSensitivity(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoCompletionCaseSensitivity", True ).toBool();

'''!
    \details Set if applying an autocompletion replace current word, append to it
    \param replace If True repalce word, append to it
'''
def setAutoCompletionReplaceWord(self, replace ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoCompletionReplaceWord", replace );

'''!
    \details Return True if auto completion repalce word else False
'''
def autoCompletionReplaceWord(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoCompletionReplaceWord", True ).toBool();

'''!
    \details Set if auto completion list is shown for single match
    \param show If True, single match in list popup, auto complate
'''
def setAutoCompletionShowSingle(self, show ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoCompletionShowSingle", show );

'''!
    \details Return True if single match is shown, False
'''
def autoCompletionShowSingle(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoCompletionShowSingle", False ).toBool();

'''!
    \details Set autocompletion source mode
    \param mode The mode to use
'''
def setAutoCompletionSource(self, mode ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoCompletionSource", mode );

'''!
    \details Return the autocompletion mode used
'''
def autoCompletionSource(self):
{ return (QsciScintilla.AutoCompletionSource)MonkeyCore.settings().value( settingsPath() +"/AutoCompletionSource", (int)QsciScintilla.AcsAll ).toInt();

'''!
    \details Set the autocompletion threshold ( ie: needed typed letters to invoke autocompletion list )
    \param count The number of letters to type
'''
def setAutoCompletionThreshold(self, count ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoCompletionThreshold", count );

'''!
    \details Return the autocompletion threshold count
'''
def autoCompletionThreshold(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoCompletionThreshold", 3 ).toInt();

'''!
    \details Set the calltips background color
    \param color The color to apply
'''
def setCallTipsBackgroundColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CallTipsBackgroundColor", color );

'''!
    \details Return the calltips baclground color
'''
def callTipsBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CallTipsBackgroundColor", QColor( "#ffff9b" ) ).value<QColor>();

'''!
    \details Set calltips foreground color
    \param color The color to apply
'''
def setCallTipsForegroundColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CallTipsForegroundColor", color );

'''!
    \details Return the calltips foreground color
'''
def callTipsForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CallTipsForegroundColor", QColor( "#000000" ) ).value<QColor>();

'''!
    \details Set the calltips highlight color
    \param color The color to apply
'''
def setCallTipsHighlightColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CallTipsHighlightColor", color );

'''!
    \details Return the calltips highlight color
'''
def callTipsHighlightColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CallTipsHighlightColor", QColor( "#ff0000" ) ).value<QColor>();

'''!
    \details Set the calltips style
    \param style The style to apply
'''
def setCallTipsStyle(self, style ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CallTipsStyle", style );

'''!
    \details Return the calltips style
'''
def callTipsStyle(self):
{ return (QsciScintilla.CallTipsStyle)MonkeyCore.settings().value( settingsPath() +"/CallTipsStyle", (int)QsciScintilla.CallTipsContext ).toInt();

'''!
    \details Set the calltips visible count
    \param count The number of calltips to show at one time
'''
def setCallTipsVisible(self, count ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CallTipsVisible", count );

'''!
    \details Return the calltips visible number
'''
def callTipsVisible(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CallTipsVisible", -1 ).toInt();

'''!
    \details Set auto indentation
    \param autoindent If True auto indentation is performed, no
'''
def setAutoIndent(self, autoindent ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoIndent", autoindent );

'''!
    \details Return True if auto indentation is active, False
'''
def autoIndent(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoIndent", True ).toBool();

'''!
    \details Set if backspace unindents
    \param unindents If True, key do unindents, no
'''
def setBackspaceUnindents(self, unindents ):
{ MonkeyCore.settings().setValue( settingsPath() +"/BackspaceUnindents", unindents );

'''!
    \details Return True if backspace key unindents else False
'''
def backspaceUnindents(self):
{ return MonkeyCore.settings().value( settingsPath() +"/BackspaceUnindents", True ).toBool();

'''!
    \details Set if indentation guides are visible
    \param visible If True guides are visible
'''
def setIndentationGuides(self, visible ):
{ MonkeyCore.settings().setValue( settingsPath() +"/IndentationGuides", visible );

'''!
    \details Return True if indentation guides are shown, False
'''
def indentationGuides(self):
{ return MonkeyCore.settings().value( settingsPath() +"/IndentationGuides", True ).toBool();

'''!
    \details Set if indentation use tabs
    \param tabs If True, are used, spaces
'''
def setIndentationsUseTabs(self, tabs ):
{ MonkeyCore.settings().setValue( settingsPath() +"/IndentationsUseTabs", tabs );

'''!
    \details Return True if indentation use tabs, False
'''
def indentationsUseTabs(self):
{ return MonkeyCore.settings().value( settingsPath() +"/IndentationsUseTabs", True ).toBool();

'''!
    \details Set if indent is auto detected
    \param detect If True, is auto detected, no
'''
def setAutoDetectIndent(self, detect ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoDetectIndent", detect );

'''!
    \details Return True if indent is auto detected, False
'''
def autoDetectIndent(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoDetectIndent", False ).toBool();

'''!
    \details Set indentation width
    \param width The indentation width
'''
def setIndentationWidth(self, width ):
{ MonkeyCore.settings().setValue( settingsPath() +"/IndentationWidth", width );

'''!
    \details Return the indentation width
'''
def indentationWidth(self):
{ return MonkeyCore.settings().value( settingsPath() +"/IndentationWidth", 4 ).toInt();

'''!
    \details Set if tab key indents
    \param indent If True, key do indent, add simple tabulation
'''
def setTabIndents(self, indent ):
{ MonkeyCore.settings().setValue( settingsPath() +"/TabIndents", indent );

'''!
    \details Return True if tab key do indent, False
'''
def tabIndents(self):
{ return MonkeyCore.settings().value( settingsPath() +"/TabIndents", True ).toBool();

'''!
    \details Set tab width
    \param width The tab width
'''
def setTabWidth(self, width ):
{ MonkeyCore.settings().setValue( settingsPath() +"/TabWidth", width );

'''!
    \details Return the tab width
'''
def tabWidth(self):
{ return MonkeyCore.settings().value( settingsPath() +"/TabWidth", 4 ).toInt();

'''!
    \details Set the indentation guide guide background color
    \param color The color to apply
'''
def setIndentationGuidesBackgroundColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/IndentationGuidesBackgroundColor", color );

'''!
    \details Return the indentation guide background color
'''
def indentationGuidesBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/IndentationGuidesBackgroundColor", QColor( "#0000ff" ) ).value<QColor>();

'''!
    \details Set the indentation guide foreground color
    \param color The color to apply
'''
def setIndentationGuidesForegroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/IndentationGuidesForegroundColor", c );

'''!
    \details Return the indentation guide foreground color
'''
def indentationGuidesForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/IndentationGuidesForegroundColor", QColor( "#0000ff" ) ).value<QColor>();

'''!
    \details Set the brace matching mode
    \param mode The mode to apply
'''
def setBraceMatching(self, mode ):
{ MonkeyCore.settings().setValue( settingsPath() +"/BraceMatching", mode );

'''!
    \details Return the brace matching mode
'''
def braceMatching(self):
{ return (QsciScintilla.BraceMatch)MonkeyCore.settings().value( settingsPath() +"/BraceMatching", (int)QsciScintilla.SloppyBraceMatch ).toInt();

'''!
    \details Set the matched brace background color
    \param color The color to apply
'''
def setMatchedBraceBackgroundColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/MatchedBraceBackgroundColor", color );

'''!
    \details Return the matched brace background color
'''
def matchedBraceBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/MatchedBraceBackgroundColor", QColor( "#ffff7f" ) ).value<QColor>();

'''!
    \details Set the matched brache foreground color
    \param color The color to apply
'''
def setMatchedBraceForegroundColor(self, color ):
{ MonkeyCore.settings().setValue( settingsPath() +"/MatchedBraceForegroundColor", color );

'''!
    \details Return the matched brace foreground color
'''
def matchedBraceForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/MatchedBraceForegroundColor", QColor( "#ff0000" ) ).value<QColor>();

def setUnmatchedBraceBackgroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/UnmatchedBraceBackgroundColor", c );

def unmatchedBraceBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/UnmatchedBraceBackgroundColor", QColor( "#ff0000" ) ).value<QColor>();

def setUnmatchedBraceForegroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/UnmatchedBraceForegroundColor", c );

def unmatchedBraceForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/UnmatchedBraceForegroundColor", QColor( "#ffffff" ) ).value<QColor>();

def setEdgeMode(self, m ):
{ MonkeyCore.settings().setValue( settingsPath() +"/EdgeMode", m );

def edgeMode(self):
{ return (QsciScintilla.EdgeMode)MonkeyCore.settings().value( settingsPath() +"/EdgeMode", (int)QsciScintilla.EdgeNone ).toInt();

def setEdgeColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/EdgeColor", c );

def edgeColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/EdgeColor", QColor( "#ff0000" ) ).value<QColor>();

def setEdgeColumn(self, i ):
{ MonkeyCore.settings().setValue( settingsPath() +"/EdgeColumn", i );

def edgeColumn(self):
{ return MonkeyCore.settings().value( settingsPath() +"/EdgeColumn", 80 ).toInt();

def setCaretLineVisible(self, b ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CaretLineVisible", b );

def caretLineVisible(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CaretLineVisible", True ).toBool();

def setCaretLineBackgroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CaretLineBackgroundColor", c );

def caretLineBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CaretLineBackgroundColor", QColor( "#aaaaff" ) ).value<QColor>();

def setCaretForegroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CaretForegroundColor", c );

def caretForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CaretForegroundColor", QColor( "#000000" ) ).value<QColor>();

def setCaretWidth(self, i ):
{ MonkeyCore.settings().setValue( settingsPath() +"/CaretWidth", i );

def caretWidth(self):
{ return MonkeyCore.settings().value( settingsPath() +"/CaretWidth", 1 ).toInt();

def setLineNumbersMarginEnabled(self, b ):
{ MonkeyCore.settings().setValue( settingsPath() +"/LineNumbersMarginEnabled", b );

def lineNumbersMarginEnabled(self):
{ return MonkeyCore.settings().value( settingsPath() +"/LineNumbersMarginEnabled", True ).toBool();

def setLineNumbersMarginWidth(self, i ):
{ MonkeyCore.settings().setValue( settingsPath() +"/LineNumbersMarginWidth", i );

def lineNumbersMarginWidth(self):
{ return MonkeyCore.settings().value( settingsPath() +"/LineNumbersMarginWidth", 4 ).toInt();

def setLineNumbersMarginAutoWidth(self, b ):
{ MonkeyCore.settings().setValue( settingsPath() +"/LineNumbersMarginAutoWidth", b );

def lineNumbersMarginAutoWidth(self):
{ return MonkeyCore.settings().value( settingsPath() +"/LineNumbersMarginAutoWidth", True ).toBool();

def setFolding(self, f ):
{ MonkeyCore.settings().setValue( settingsPath() +"/Folding", f );

def folding(self):
{ return (QsciScintilla.FoldStyle)MonkeyCore.settings().value( settingsPath() +"/Folding", (int)QsciScintilla.BoxedTreeFoldStyle ).toInt();

def setFoldMarginBackgroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/FoldMarginBackgroundColor", c );

def foldMarginBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/FoldMarginBackgroundColor", QColor( "#c0c0c0" ) ).value<QColor>();

def setFoldMarginForegroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/FoldMarginForegroundColor", c );

def foldMarginForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/FoldMarginForegroundColor", QColor( "#ffffff" ) ).value<QColor>();

def setMarginsEnabled(self, b ):
{ MonkeyCore.settings().setValue( settingsPath() +"/MarginsEnabled", b );

def marginsEnabled(self):
{ return MonkeyCore.settings().value( settingsPath() +"/MarginsEnabled", False ).toBool();

def setMarginsBackgroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/MarginsBackgroundColor", c );

def marginsBackgroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/MarginsBackgroundColor", QColor( "#c0c0c0" ) ).value<QColor>();

def setMarginsForegroundColor(self, c ):
{ MonkeyCore.settings().setValue( settingsPath() +"/MarginsForegroundColor", c );

def marginsForegroundColor(self):
{ return MonkeyCore.settings().value( settingsPath() +"/MarginsForegroundColor", QColor( "#ffffff" ) ).value<QColor>();

def setMarginsFont(self, f ):
{ MonkeyCore.settings().setValue( settingsPath() +"/MarginsFont", f.toString() );

def marginsFont(self):
    QFont f
    f.fromString( MonkeyCore.settings().value( settingsPath() +"/MarginsFont", f.toString() ).toString() )
    return f


def setEolMode(self, e ):
{ MonkeyCore.settings().setValue( settingsPath() +"/EolMode", e );

def eolMode(self, os ):
    i = QsciScintilla.EolUnix

    switch ( os )
        case pMonkeyStudio.UnixOS:
            i = QsciScintilla.EolUnix
            break
        case pMonkeyStudio.MacOS:
            i = QsciScintilla.EolMac
            break
        case pMonkeyStudio.WindowsOS:
            i = QsciScintilla.EolWindows
            break


    return (QsciScintilla.EolMode)MonkeyCore.settings().value( settingsPath() +"/EolMode", i ).toInt()


def getEol(self, e ):
    switch ( e )
        case QsciScintilla.EolWindows:
            return QString( "\r\n" )
            break
        case QsciScintilla.EolUnix:
            return QString( "\n" )
            break
        case QsciScintilla.EolMac:
            return QString( "\n" )
            break
        default:
            return QString( "\r\n" )



def setEolVisibility(self, b ):
{ MonkeyCore.settings().setValue( settingsPath() +"/EolVisibility", b );

def eolVisibility(self):
{ return MonkeyCore.settings().value( settingsPath() +"/EolVisibility", False ).toBool();

def setAutoDetectEol(self, detect ):
{ MonkeyCore.settings().setValue( settingsPath() +"/AutoDetectEol", detect );

def autoDetectEol(self):
{ return MonkeyCore.settings().value( settingsPath() +"/AutoDetectEol", False ).toBool();

def setWhitespaceVisibility(self, w ):
{ MonkeyCore.settings().setValue( settingsPath() +"/WhitespaceVisibility", w );

def whitespaceVisibility(self):
{ return (QsciScintilla.WhitespaceVisibility)MonkeyCore.settings().value( settingsPath() +"/WhitespaceVisibility", (int)QsciScintilla.WsInvisible ).toInt();

def setWrapMode(self, w ):
{ MonkeyCore.settings().setValue( settingsPath() +"/WrapMode", w );

def wrapMode(self):
{ return (QsciScintilla.WrapMode)MonkeyCore.settings().value( settingsPath() +"/WrapMode", (int)QsciScintilla.WrapNone ).toInt();

def setWrapVisualFlagsEnabled(self, b ):
{ MonkeyCore.settings().setValue( settingsPath() +"/WrapVisualFlagsEnabled", b );

def wrapVisualFlagsEnabled(self):
{ return MonkeyCore.settings().value( settingsPath() +"/WrapVisualFlagsEnabled", False ).toBool();

def setStartWrapVisualFlag(self, f ):
{ MonkeyCore.settings().setValue( settingsPath() +"/StartWrapVisualFlag", f );

def startWrapVisualFlag(self):
{ return (QsciScintilla.WrapVisualFlag)MonkeyCore.settings().value( settingsPath() +"/StartWrapVisualFlag", (int)QsciScintilla.WrapFlagNone ).toInt();

def setEndWrapVisualFlag(self, f ):
{ MonkeyCore.settings().setValue( settingsPath() +"/EndWrapVisualFlag", f );

def endWrapVisualFlag(self):
{ return (QsciScintilla.WrapVisualFlag)MonkeyCore.settings().value( settingsPath() +"/EndWrapVisualFlag", (int)QsciScintilla.WrapFlagNone ).toInt();

def setWrappedLineIndentWidth(self, i ):
{ MonkeyCore.settings().setValue( settingsPath() +"/WrappedLineIndentWidth", i );

def wrappedLineIndentWidth(self):
{ return MonkeyCore.settings().value( settingsPath() +"/WrappedLineIndentWidth", 0 ).toInt();
