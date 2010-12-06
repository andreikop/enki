import sys
import os.path

#from PyQt4.QtCore import *
from PyQt4.QtGui import QIcon

import mks.monkeycore

#QHash<QString,QsciLexer*> mGlobalsLexers
#QHash<QString,QsciAPIs*> mGlobalsAPIs

""" fixme remove
Use os.path.samefile
def isSameFile(  left,  right ):


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
