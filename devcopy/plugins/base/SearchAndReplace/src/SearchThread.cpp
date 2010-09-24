#include "SearchThread.h"

#include <QMutexLocker>
#include <QTextCodec>
#include <QTime>
#include <QTimer>
#include <QDebug>

int SearchThread.mMaxTime = 125

SearchThread.SearchThread( QObject* parent )
        : QThread( parent )
    mReset = False
    mExit = False

    qRegisterMetaType<SearchResultsModel.ResultList>( "SearchResultsModel.ResultList" )


SearchThread.~SearchThread()
    stop()
    wait()


def search(self, properties ):
        QMutexLocker locker( &mMutex )
        mProperties = properties
        mReset = isRunning() ? True : False
        mExit = False


    if  not isRunning() :
        start()



def stop(self):
        QMutexLocker locker( &mMutex )
        mReset = False
        mExit = True



def properties(self):
    QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )
    return &const_cast<SearchThread*>( self ).mProperties


def getFiles(self, fromDir, filters, recursive ):
    QStringList files

    foreach (  QFileInfo& file, fromDir.entryInfoList( QDir.AllEntries | QDir.AllDirs | QDir.NoDotAndDotDot, QDir.DirsFirst | QDir.Name ) )
        if  file.isFile() and ( filters.isEmpty() or QDir.match( filters, file.fileName() ) ) :
            files << file.absoluteFilePath()

        elif  file.isDir() and recursive :
            fromDir.cd( file.filePath() )
            files << getFiles( fromDir, filters, recursive )
            fromDir.cdUp()


            QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )

            if  mReset or mExit :
                return files




    return files


def getFilesToScan(self):
    QSet<QString> files
    mode = SearchAndReplace.ModeNo

        QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )
        mode = mProperties.mode


    switch ( mode )
    case SearchAndReplace.ModeNo:
    case SearchAndReplace.ModeSearch:
    case SearchAndReplace.ModeReplace:
        qWarning() << "Invalid mode used."
        Q_ASSERT( 0 )
        return files.toList()
    case SearchAndReplace.ModeSearchDirectory:
    case SearchAndReplace.ModeReplaceDirectory:
        QString path
        QStringList mask

            QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )
            path = mProperties.searchPath
            mask = mProperties.mask


        QDir dir( path )
        files = getFiles( dir, mask, True ).toSet()
        break

    case SearchAndReplace.ModeSearchProjectFiles:
    case SearchAndReplace.ModeReplaceProjectFiles:
        QStringList sources
        QStringList mask

            QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )
            sources = mProperties.sourcesFiles
            mask = mProperties.mask


        for fileName in sources:
            if  QDir.match( mask, fileName ) :
                files << fileName


                QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )

                if  mReset or mExit :
                    return files.toList()



        break

    case SearchAndReplace.ModeSearchOpenedFiles:
    case SearchAndReplace.ModeReplaceOpenedFiles:
        QStringList sources
        QStringList mask

            QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )
            sources = mProperties.openedFiles.keys()
            mask = mProperties.mask


        for fileName in sources:
            if  QDir.match( mask, fileName ) :
                files << fileName


                QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )

                if  mReset or mExit :
                    return files.toList()



        break



    return files.toList()


def fileContent(self, fileName ):
    codec = 0

        QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )

        codec = QTextCodec.codecForName( mProperties.codec.toLocal8Bit() )

        if  mProperties.openedFiles.contains( fileName ) :
            return mProperties.openedFiles[ fileName ]



    Q_ASSERT( codec )

    QFile file( fileName )

    if  not file.open( QIODevice.ReadOnly ) :
        return QString.null


    if  SearchWidget.isBinary( file ) :
        return QString.null


    return codec.toUnicode( file.readAll() )


def search(self, fileName, content ):
    static  QString eol( "\n" )
    checkable = False
    isRE = False
    QRegExp rx

        QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )

        isRE = mProperties.options & SearchAndReplace.OptionRegularExpression
         isWw = mProperties.options & SearchAndReplace.OptionWholeWord
         isCS = mProperties.options & SearchAndReplace.OptionCaseSensitive
         sensitivity = isCS ? Qt.CaseSensitive : Qt.CaseInsensitive
        checkable = mProperties.mode & SearchAndReplace.ModeFlagReplace
        pattern = isRE ? mProperties.searchText : QRegExp.escape( mProperties.searchText )

        if  isWw :
            pattern.prepend( "\\b" ).append( "\\b" )


        rx.setMinimal( True )
        rx.setPattern( pattern )
        rx.setCaseSensitivity( sensitivity )


    pos = 0
    lastPos = 0
    eolCount = 0
    SearchResultsModel.ResultList results
    QTime tracker

    tracker.start()

    while ( ( pos = rx.indexIn( content, pos ) ) != -1 )
         eolStart = content.lastIndexOf( eol, pos )
         eolEnd = content.indexOf( eol, pos )
         capture = content.mid( eolStart + 1, eolEnd -1 -eolStart ).simplified()
        eolCount += content.mid( lastPos, pos -lastPos ).count( eol )
         column = ( pos -eolStart ) -( eolStart != 0 ? 1 : 0 )
        result = SearchResultsModel.Result( fileName, capture )
        result.position = QPoint( column, eolCount )
        result.offset = pos
        result.length = rx.matchedLength()
        result.checkable = checkable
        result.checkState = checkable ? Qt.Checked : Qt.Unchecked
        result.capturedTexts = isRE ? rx.capturedTexts() : QStringList()

        results << result

        lastPos = pos
        pos += rx.matchedLength()

        if  tracker.elapsed() >= mMaxTime :
            const_cast.emit<SearchThread*>( self ).resultsAvailable( fileName, results )
            results.clear()
            tracker.restart()


            QMutexLocker locker( const_cast<QMutex*>( &mMutex ) )

            if  mReset or mExit :
                return




    if  not results.isEmpty() :
        const_cast.emit<SearchThread*>( self ).resultsAvailable( fileName, results )



def run(self):
    QTime tracker

    forever
            QMutexLocker locker( &mMutex )
            mReset = False
            mExit = False


        reset.emit()
        progressChanged.emit( -1, 0 )
        tracker.restart()

        files = getFilesToScan()
        files.sort()

            QMutexLocker locker( &mMutex )

            if  mExit :
                return

            elif  mReset :
                continue



         total = files.count()
        value = 0

        progressChanged.emit( 0, total )

        for fileName in files:
             content = fileContent( fileName )
            search( fileName, content )
            value++

            progressChanged.emit( value, total )

                QMutexLocker locker( &mMutex )

                if  mExit :
                    return

                elif  mReset :
                    break




            QMutexLocker locker( &mMutex )

            if  mReset :
                continue



        break


    qWarning() << "Search finished in " << tracker.elapsed() /1000.0


def clear(self):
    stop()
    reset.emit()

