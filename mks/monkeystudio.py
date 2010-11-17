import sys
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mks.monkeycore
import mks.workspace

#QHash<QString,QsciLexer*> mGlobalsLexers
#QHash<QString,QsciAPIs*> mGlobalsAPIs

""" fixme remove
Use os.path.samefile
def isSameFile(  left,  right ):

    
"""

'''!
    \details Return a list of all know text codecs
'''
def availableTextCodecs():
    return [str(cod) for cod in QTextCodec.availableCodecs()]

'''!
    \details Return a list of all know image formats
'''
def availableImageFormats():
    return sorted([str(f) for f in QImageReader.availableImageFormats()])


'''!
    \details Return a QFileInfoList containing folders
    \param fromDir The folder from witch to get contents
    \param filters The filters to apply for validate folders name
    \param recursive If True, the folders are scanned recursively, else not
'''
def getFolders( fromDir,  filters, recursive ):
    files = QFileInfoList()
    for file in fromDir.entryInfoList( QDir.Dirs | QDir.AllDirs | QDir.NoDotAndDotDot, QDir.Name ):
        if  filters.isEmpty() or QDir.match( filters, file.fileName() ) :
            files.append(file)
        if  recursive :
            fromDir.cd( file.filePath() )
            files.append(getFolders( fromDir, filters, recursive ))
            fromDir.cdUp()
    
    return files


'''!
    \details Return a QFileInfoList containing files
    \param fromDir The folder from witch to get contents
    \param filters The filters to apply for validate files name
    \param recursive If True, the folders are scanned recursively, else not
'''
def getFiles( fromDir,  filters, recursive ):
    files = QFileInfoList()
    for file in fromDir.entryInfoList( QDir.AllEntries | QDir.AllDirs | QDir.NoDotAndDotDot, QDir.DirsFirst | QDir.Name ):
        if  file.isFile() and ( filters.isEmpty() or QDir.match( filters, file.fileName() ) ) :
            files.append(file)
        elif  file.isDir() and recursive :
            fromDir.cd( file.filePath() )
            files.append(getFiles( fromDir, filters, recursive ))
            fromDir.cdUp()
    
    return files


'''!
    \details Return a QFileInfoList containing files
    \param fromDir The folder from witch to get contents
    \param filters The filters to apply for validate files name
    \param recursive If True, the folders are scanned recursively, else not
'''
def getFiles( fromDir,  filter, recursive ):
    if filter.isEmpty():
        return getFiles( fromDir, QStringList(), recursive )
    else:
        return getFiles( fromDir, QStringList( filter ), recursive )


"""TODO
def getOpenDialog( QFileDialog.FileMode fileMode,  QString& caption,  QString& fileName,  QString& filter, QWidget* parent, QFileDialog.AcceptMode acceptMode = QFileDialog.AcceptOpen ):
    # create dialg
    QFileDialog* dlg = new QFileDialog( parent, caption, fileName, filter )
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
def getImageFileNames(  QString& caption,  QString& fileName, QWidget* parent ):
    # get image filters
    QStringList filters
    foreach ( QString filter, availableImageFormats() )
    filters << QObject.tr( "%1 Files (*.%2)" ).arg( filter.toUpper() ).arg( filter )
    # add all format as one filter at begining
    if  not filters.isEmpty() :
        filters.prepend( QObject.tr( "All Image Files (%1)" ).arg( QStringList( availableImageFormats() ).replaceInStrings( QRegExp( "^(.*)$" ), "*.\\1" ).join( " " ) ) )
    # create dialog
    QFileDialog* dlg = getOpenDialog( QFileDialog.ExistingFiles, caption.isEmpty() ? QObject.tr( "Select image(s)" ) : caption, fileName, filters.join( ";;" ), parent )
    # choose last used filter if available
    if  not filters.isEmpty() :
        dlg.selectFilter( mks.monkeycore.settings().value( "Recents/ImageFilter" ).toString() )
    # execute dialog
    if  dlg.exec() :
        # remember last filter if available
        if  not filters.isEmpty() :
            mks.monkeycore.settings().setValue( "Recents/ImageFilter", dlg.selectedFilter() )
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
def getImageFileName(  QString& caption,  QString& fileName, QWidget* parent ):
    return getImageFileNames( caption, fileName, parent ).value( 0 )


'''!
    \details Return a QStringList of files name
    \param caption The window title
    \param fileName The default filename to select ( or path )
    \param filter The filter to apply
    \param parent The parent widget
'''
def getOpenFileNames(  QString& caption,  QString& fileName,  QString& filter, QWidget* parent ):
    # create dialg
    QFileDialog* dlg = getOpenDialog( QFileDialog.ExistingFiles, caption.isEmpty() ? QObject.tr( "Select file(s)" ) : caption, fileName, filter, parent )
    # choose last used filter if available
    if  not filter.isEmpty() :
        dlg.selectFilter( mks.monkeycore.settings().value( "Recents/FileFilter" ).toString() )
    # execute dialog
    if  dlg.exec() :
        # remember last filter if available
        if  not filter.isEmpty() :
            mks.monkeycore.settings().setValue( "Recents/FileFilter", dlg.selectedFilter() )
        # remember selected files
        QStringList files = dlg.selectedFiles()
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
def getOpenFileName(  QString& caption,  QString& fileName,  QString& filter, QWidget* parent ):
    return getOpenFileNames( caption, fileName, filter, parent ).value( 0 )


'''!
    \details Return a QString file name
    \param caption The window title
    \param fileName The default filename to select ( or path )
    \param filter The filter to apply
    \param parent The parent widget
'''
def getSaveFileName(  QString& caption,  QString& fileName,  QString& filter, QWidget* parent ):
    # create dialg
    QFileDialog* dlg = getOpenDialog( QFileDialog.AnyFile, caption.isEmpty() ? QObject.tr( "Choose a filename" ) : caption, fileName, filter, parent, QFileDialog.AcceptSave )
    # choose last used filter if available
    if  not filter.isEmpty() :
        dlg.selectFilter( mks.monkeycore.settings().value( "Recents/FileFilter" ).toString() )
    # execute dialog
    if  dlg.exec() :
        # remember last filter if available
        if  not filter.isEmpty() :
            mks.monkeycore.settings().setValue( "Recents/FileFilter", dlg.selectedFilter() )
        # remember selected files
        QStringList files = dlg.selectedFiles()
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
def getExistingDirectory(  QString& caption,  QString& fileName, QWidget* parent ):
    return QFileDialog.getExistingDirectory( parent, caption.isEmpty() ? QObject.tr( "Select a folder" ) : caption, fileName )
"""

'''!
    \details Return a tokenized string, ie: the token $HOME$ is replaced by the home path of the user
    \param string The string to tokenize
'''
def tokenizeHome(  string ):
    return QString( string ).replace( QDir.homePath(), "$HOME$" )


'''!
    \details Return an untokenized string, ie: the home path is replaced by $HOME$
    \param string The string to untokenize
'''
def unTokenizeHome( string ):
    return QString( string ).replace( "$HOME$", QDir.homePath() )


'''!
    \details Return all available languages suffixes
'''
def availableLanguagesSuffixes():
    return mks.monkeycore.fileManager().associations()

"""TODO
'''!
    \details Return all available files suffixes
'''
def availableFilesSuffixes():
    # get language suffixes
    QMap<QString, QStringList> l = availableLanguagesSuffixes()
    # add document plugins suffixes
    QMap<QString, QStringList> ps = mks.monkeycore.pluginsManager().documentSuffixes()
    foreach ( QString k, ps.keys() )
    foreach ( QString s, ps[k] )
    if  not l[k].contains( s ) :
        l[k] << s
    # return list
    return l


'''!
    \details Return all available languages filters
'''
def availableLanguagesFilters():
    QString f
    # get suffixes
    QMap<QString, QStringList> sl = availableLanguagesSuffixes()
    #
    foreach ( QString k, sl.keys() )
    f += QString( "%1 Files (%2);;" ).arg( k ).arg( sl.value( k ).join( " " ) )
    # remove trailing 
    if  f.endsWith( ";;" ) :
        f.chop( 2 )
    # return filters list
    return f


'''!
    \details Return all available files filters
'''
def availableFilesFilters():
    QString f
    # get suffixes
    QMap<QString, QStringList> sl = availableFilesSuffixes()
    #
    foreach ( QString k, sl.keys() )
    f += QString( "%1 Files (%2);;" ).arg( k ).arg( sl.value( k ).join( " " ) )
    # remove trailing 
    if  f.endsWith( ";;" ) :
        f.chop( 2 )

    if  not f.isEmpty() :
        QString s
        foreach ( QStringList l, availableFilesSuffixes().values() )
        s.append( l.join( " " ).append( " " ) )
        f.prepend( QString( "All Files (*);;" ))
        f.prepend( QString( "All Supported Files (%1);;" ).arg( s.trimmed() ) )


    # return filters list
    return f

"""

'''!
    \details Return the base settings path used by all option in this namespace
'''
def settingsPath():
    return "/Settings"


'''!
    \details Return the scintilla settigns path
'''
def scintillaSettingsPath():
    return "/Scintilla"

"""TODO
'''!
    \details Reload all available api files
'''
def prepareAPIs():
    # check lexers & apis
    if  mGlobalsLexers.isEmpty() or mGlobalsAPIs.isEmpty() :
        # free hashes
        qDeleteAll( mGlobalsLexers )
        mGlobalsLexers.clear()
        qDeleteAll( mGlobalsAPIs )
        mGlobalsAPIs.clear()

    # get monkey status bar
    pQueuedMessageToolBar* sbar = mks.monkeycore.messageManager()
    # iterate each language
    foreach ( QString ln, availableLanguages() )
        QsciLexer* l = lexerForLanguage( ln )
        QsciAPIs* a = apisForLexer( l )
        # clear raw api
        a.clear()
        # load prepared files
        foreach ( QString f, mks.monkeycore.settings().value( QString( "SourceAPIs/" ).append( ln ) ).toStringList() )
            if  not a.load( QDir.isRelativePath( f ) ? qApp.applicationDirPath().append( "/%1" ).arg( f ) : f ) :
                sbar.appendMessage( QObject.tr( "Can't load api file: '%1'" ).arg( QFileInfo( f ).fileName() ) )

        # start prepare for apis
        a.prepare()



'''!
    \details Return a QsciAPIs for the given lexer
    \param lexer The lexer to get apis object
'''
def apisForLexer( QsciLexer* lexer ):
    # cancel if no lexer
    if  not lexer :
        return 0
    # check if apis already exists
    if  not mGlobalsAPIs.contains( lexer.language() ) :
        # create apis
        QsciAPIs* apis = new QsciAPIs( lexer )
        # store global apis
        mGlobalsAPIs[lexer.language()] = apis

    # return apis
    return mGlobalsAPIs.value( lexer.language() )


'''!
    \details Return the language of a file name
    \param fileName The fil name to get language from
'''
def languageForFileName(  QString& fileName ):
    QsciLexer* lexer = lexerForFileName( fileName )
    return lexer ? QString( lexer.language() ) : QString()


'''!
    \details Return a QsciLexer for the given file name
    \param fileName The filenae to get lexer from
'''
def lexerForFileName(  QString& fileName ):
    # get suffixes
    QMap<QString, QStringList> l = availableFilesSuffixes()
    # check suffixe
    foreach ( QString k, l.keys() )
    if  QDir.match( l.value( k ), fileName ) :
        return lexerForLanguage( k )
    return 0


'''!
    \details Return a QsciLexer for the given language
    \param language The language to get lexer from
'''
def lexerForLanguage(  QString& language ):
    if  mGlobalsLexers.keys().contains( language ) :
        return mGlobalsLexers.value( language )
    # get language
     QString ln = language.toLower()
    # lexer
    QsciLexer* l = 0
    # init lexer
    if  ln == "bash" :
        l = new QsciLexerBash( QApplication.instance() )
    elif  ln == "batch" :
        l = new QsciLexerBatch( QApplication.instance() )
    elif  ln == "c#" :
        l = new QsciLexerCSharp( QApplication.instance() )
    elif  ln == "c++" :
        l = new QsciLexerCPP( QApplication.instance() )
    elif  ln == "cmake" :
        l = new QsciLexerCMake( QApplication.instance() )
    elif  ln == "css" :
        l = new QsciLexerCSS( QApplication.instance() )
    elif  ln == "d" :
        l = new QsciLexerD( QApplication.instance() )
    elif  ln == "diff" :
        l = new QsciLexerDiff( QApplication.instance() )
    elif  ln == "html" :
        l = new QsciLexerHTML( QApplication.instance() )
    elif  ln == "idl" :
        l = new QsciLexerIDL( QApplication.instance() )
    elif  ln == "java" :
        l = new QsciLexerJava( QApplication.instance() )
    elif  ln == "javascript" :
        l = new QsciLexerJavaScript( QApplication.instance() )
    elif  ln == "lua" :
        l = new QsciLexerLua( QApplication.instance() )
    elif  ln == "makefile" :
        l = new QsciLexerMakefile( QApplication.instance() )
    elif  ln == "pov" :
        l = new QsciLexerPOV( QApplication.instance() )
    elif  ln == "perl" :
        l = new QsciLexerPerl( QApplication.instance() )
    elif  ln == "properties" :
        l = new QsciLexerProperties( QApplication.instance() )
    elif  ln == "python" :
        l = new QsciLexerPython( QApplication.instance() )
    elif  ln == "ruby" :
        l = new QsciLexerRuby( QApplication.instance() )
    elif  ln == "sql" :
        l = new QsciLexerSQL( QApplication.instance() )
    elif  ln == "tex" :
        l = new QsciLexerTeX( QApplication.instance() )
    elif  ln == "vhdl" :
        l = new QsciLexerVHDL( QApplication.instance() )
#if QSCINTILLA_VERSION >= 0x020300
    elif  ln == "tcl" :
        l = new QsciLexerTCL( QApplication.instance() )
    elif  ln == "fortran" :
        l = new QsciLexerFortran( QApplication.instance() )
    elif  ln == "fortran77" :
        l = new QsciLexerFortran77( QApplication.instance() )
    elif  ln == "pascal" :
        l = new QsciLexerPascal( QApplication.instance() )
    elif  ln == "postscript" :
        l = new QsciLexerPostScript( QApplication.instance() )
    elif  ln == "xml" :
        l = new QsciLexerXML( QApplication.instance() )
    elif  ln == "yaml" :
        l = new QsciLexerYAML( QApplication.instance() )
#endif
#if QSCINTILLA_VERSION > 0x020400
    elif  ln == "verilog" :
        l = new QsciLexerVerilog( QApplication.instance() )
    elif  ln == "spice" :
        l = new QsciLexerSpice( QApplication.instance() )
#endif
    # init lexer settings
    if  l :
        # add lexer to global lexers hash
        mGlobalsLexers[l.language()] = l
        # read settings
        pSettings* ss = mks.monkeycore.settings()
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
def setLexerProperty(  QString& property, QsciLexer* lexer,  QVariant& value ):
    # cancel no property, no lexer or if variant is not valid
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
def lexerProperty(  QString& property, QsciLexer* lexer ):
    # if no member or lexer return null variant
    if  not lexer or property.isEmpty() :
        return QVariant()
    # get language
     QString lng = QString( lexer.language() ).toLower()
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
def resetLexer( QsciLexer* lexer ):
    # cancel if no lexer
    if  not lexer :
        return
    # get settings pointer
    pSettings* settings = mks.monkeycore.settings()
    # remove lexer entry
    settings.remove( QString( "%1/%2" ).arg( scintillaSettingsPath() ).arg( lexer.language() ) )
    # set default styles & font
    lexer.setDefaultFont( defaultDocumentFont() )
    for ( int i = 0; i < 128; ++i )
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
def applyProperties():
    # apply editor properties
    foreach ( AbstractDocument* c, mks.monkeycore.workspace().documents() )
    foreach ( pEditor* e, c.findChildren<pEditor*>() )
    setEditorProperties( e )
    # apply lexers properties
    pSettings* ss = mks.monkeycore.settings()
    foreach ( QsciLexer* l, mGlobalsLexers.values() )
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
    \details control if mac widgets show their focus rect or not.
    \param widget The widget to apply
    \param show Control focus rect visibility
    \param recursive If True, children are updated too, else not
'''
def showMacFocusRect( QWidget* widget, bool show, bool recursive ):
    QList<QWidget*> widgets

    widgets << widget

    if  recursive :
        widgets << widget.findChildren<QWidget*>()


    foreach ( QWidget* w, widgets )
        w.setAttribute( Qt.WA_MacShowFocusRect, show )



'''!
    \details control if mac widgets use small size.
    \param widget The widget to apply
    \param small Control small activation
    \param recursive If True, children are updated too, else not
'''
def setMacSmallSize( QWidget* widget, bool small, bool recursive ):
    QList<QWidget*> widgets

    widgets << widget

    if  recursive :
        widgets << widget.findChildren<QWidget*>()


    foreach ( QWidget* w, widgets )
        w.setAttribute( Qt.WA_MacSmallSize, small )

"""

'''!
    \details Save files on custom actions triggered ( builder, debugger, interpreter )
    \param save True to save, else False
'''
def setSaveFilesOnCustomAction( save ):
    mks.monkeycore.settings().setValue( settingsPath() +"/SaveFilesOnCustomAction", save )


'''!
    \details Return True if files are saved on custom actions triggered, else False
'''
def saveFilesOnCustomAction():
    return mks.monkeycore.settings().value( settingsPath() +"/SaveFilesOnCustomAction", False ).toBool()


'''!
    \details Set if tabs have close button
    \param have True to have button, else False
'''
def setTabsHaveCloseButton( have ):
    mks.monkeycore.settings().setValue( settingsPath() +"/TabsHaveCloseButton", have )


'''!
    \details Return if tabs have  close button
'''
def tabsHaveCloseButton():
    return mks.monkeycore.settings().value( settingsPath() +"/TabsHaveCloseButton", False ).toBool()


'''!
    \details Set tabs have shortcut
    \param have True for shortcut, else False
'''
def setTabsHaveShortcut( have ):
    mks.monkeycore.settings().setValue( settingsPath() +"/TabsHaveShortcut", have )


'''!
    \details Return True if tabs have shortcut, else False
'''
def tabsHaveShortcut():
    return mks.monkeycore.settings().value( settingsPath() +"/TabsHaveShortcut", False ).toBool()


'''!
    \details Set tabs text are elided
    \param elided True for elided text, else False
'''
def setTabsElided( have ):
    mks.monkeycore.settings().setValue( settingsPath() +"/TabsElided", have )


'''!
    \details Return True if tabs text is elided, else False
'''
def tabsElided():
    return mks.monkeycore.settings().value( settingsPath() +"/TabsElided", False ).toBool()


'''!
    \details Set tabs text color
    \param color The tabs text color
'''
def setTabsTextColor(  color ):
    mks.monkeycore.settings().setValue( settingsPath() +"/TabsTextColor", color )


'''!
    \details Return the tabs text color
'''
def tabsTextColor():
    return mks.monkeycore.settings().value( settingsPath() +"/TabsTextColor", QColor( Qt.black ) ).value<QColor>()


'''!
    \details Set the current tab text color
    \param color The current tab text color
'''
def setCurrentTabTextColor(  color ):
    mks.monkeycore.settings().setValue( settingsPath() +"/CurrentTabTextColor", color )


'''!
    \details Return the current tab text color
'''
def currentTabTextColor():
    return mks.monkeycore.settings().value( settingsPath() +"/CurrentTabTextColor", QColor( Qt.blue ) ).value<QColor>()


'''!
    \details Set the workspace doc mode
    \param mode The mode to apply
'''
def setDocumentMode( mode ):
    mks.monkeycore.settings().setValue( settingsPath() +"/DocMode", mode )


'''!
    \details Return the mod used by the workspace
'''
def documentMode():
    return mks.monkeycore.settings().value( settingsPath() +"/DocMode", mks.workspace.Workspace.NoTabs ).toInt()


'''!
    \details Set if session must be save on close
    \param save If True, session is saved, else not
'''
def setSaveSessionOnClose( save ):
    mks.monkeycore.settings().setValue( settingsPath() +"/SaveSessionOnClose", save )


'''!
    \details Return True if session is saved at close, else False
'''
def saveSessionOnClose():
    return mks.monkeycore.settings().value( settingsPath() +"/SaveSessionOnClose", True ).toBool()


'''!
    \details Set if session is restored on startup
    \param restore If True, session will be restored on startup, else not
'''
def setRestoreSessionOnStartup( restore ):
    mks.monkeycore.settings().setValue( settingsPath() +"/RestoreSessionOnStartup", restore )


'''!
    \details Return True if session will be restored on startup, else False
'''
def restoreSessionOnStartup():
    return mks.monkeycore.settings().value( settingsPath() +"/RestoreSessionOnStartup", True ).toBool()


'''!
    \details Set if quick file access combobox is visible in context toolbar
    \param show If True, combobox is visible, else it's not visible
'''
def setShowQuickFileAccess( show ):
    mks.monkeycore.settings().setValue( settingsPath() +"/ShowQuickFileAccess", show )


'''!
    \details Return True if a quick file access combobox is visible in the document context toolbar
'''
def showQuickFileAccess():
    return mks.monkeycore.settings().value( settingsPath() +"/ShowQuickFileAccess", False ).toBool()


'''!
    \details Set the sorting mode used by the Opened Files List dock
    \param mode Specify the used mode
'''
def setOpenedFileSortingMode( mode ):
    mks.monkeycore.settings().setValue( settingsPath() +"/OpenedFileSortingMode", mode )


'''!
    \details Return the sorting mode used by the Opened Files List dock
'''
def openedFileSortingMode():
    return mks.monkeycore.settings().value( settingsPath() +"/OpenedFileSortingMode", pOpenedFileModel.OpeningOrder ).toInt()


'''!
    \details Set if auto syntax check is performed
    \param activate If True, automatic syntax check will be performed, else not
'''
def setAutoSyntaxCheck( activate ):
    mks.monkeycore.settings().setValue( settingsPath() +"/AutoSyntaxCheck", activate )


'''!
    \details Return True if auto syntax check is performed, else False
'''
def autoSyntaxCheck():
    return mks.monkeycore.settings().value( settingsPath() +"/AutoSyntaxCheck", False ).toBool()

'''!
    \details Set the default used codec for opening/saving files
    \param codec The codec to use
'''
def setDefaultCodec( codec ):
    mks.monkeycore.settings().setValue( settingsPath() +"/DefaultCodec", codec )


'''!
    \details Return the default used codec for opening/saving files. Default UTF-8
'''
def defaultCodec():
    return mks.monkeycore.settings().value( settingsPath() +"/DefaultCodec", "UTF-8" ).toString()


def getIcon(name):
    """Loads QIcon from the icons path and returns it. Example:
      mks.monkeystudio.getIcon('application/monkey2.png')
    returns main application icon.
    Probably caching would be added later.
    """
    # TODO suppor something like /usr/share/monkeystudio, and something on Windows
    return QIcon(os.path.dirname(mks.__file__) + '/../icons/' + name)
