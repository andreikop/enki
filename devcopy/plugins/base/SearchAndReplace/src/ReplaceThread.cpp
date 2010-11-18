#include "ReplaceThread.h"
#include "SearchWidget.h"

#include <QMutexLocker>
#include <QTextCodec>
#include <QTime>
#include <QDebug>

int ReplaceThread.mMaxTime = 125

ReplaceThread.ReplaceThread( QObject* parent )
    : QThread( parent )
    mReset = False
    mExit = False


ReplaceThread.~ReplaceThread()
    stop()
    wait()


def replace(self, properties,  QHash<QString, results ):
        QMutexLocker locker( &mMutex )
        mProperties = properties
        mResults = results
        mReset = isRunning() ? True : False
        mExit = False


    if  not isRunning() :
        start()



def stop(self):
        QMutexLocker locker( &mMutex )
        mReset = False
        mExit = True



def saveContent(self, fileName, content, codec ):
    QFile file( fileName )

    if  not file.open( QIODevice.WriteOnly ) :
        error.emit( tr( "Error while saving replaced content: %1" ).arg( file.errorString() ) )
        return


    file.resize( 0 )

    textCodec = QTextCodec.codecForName( codec.toLocal8Bit() )

    Q_ASSERT( textCodec )

    if  file.write( textCodec.fromUnicode( content ) ) == -1 :
        error.emit( tr( "Error while saving replaced content: %1" ).arg( file.errorString() ) )
        return


    file.close()


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


def replace(self, fileName, content ):
    QString replaceText
    QString codec
    SearchResultsModel.ResultList results
    isOpenedFile = False
    isRE = False
    SearchResultsModel.ResultList handledResults

        QMutexLocker locker( &mMutex )
        replaceText = mProperties.replaceText
        codec = mProperties.codec
        results = mResults[ fileName ]
        isOpenedFile = mProperties.openedFiles.contains( fileName )
        isRE = mProperties.options & SearchAndReplace.OptionRegularExpression

'''
    QTime tracker
    tracker.start()
'''
    static QRegExp rx( "\\$(\\d+)" )
    rx.setMinimal( True )

    # count from end to begin because we are replacing by offset in content
    for ( i = results.count() -1; i > -1; i-- )
        result = results.at( i )
         searchLength = result.length
         captures = result.capturedTexts
    
        # compute replace text
        if  isRE and captures.count() > 1 :            pos = 0
            
            while ( ( pos = rx.indexIn( replaceText, pos ) ) != -1 )                 id = rx.cap( 1 ).toInt()
                
                if  id < 0 or id >= captures.count() :                    pos += rx.matchedLength()
                    continue

                
                # update replace text with partial occurrences
                replaceText.replace( pos, rx.matchedLength(), captures.at( id ) )
                
                # next
                pos += captures.at( id ).length()


        
        # replace text
        content.replace( result.offset, searchLength, replaceText )

        handledResults << result
'''
        if  tracker.elapsed() >= mMaxTime :
            if  not handledResults.isEmpty() :
                if  not isOpenedFile :
                    saveContent( fileName, content, codec )


                resultsHandled.emit( fileName, handledResults )


            if  isOpenedFile :
                openedFileHandled.emit( fileName, content, codec )


            handledResults.clear()
            tracker.restart()

'''
            QMutexLocker locker( &mMutex )

            if  mExit :
                return

            elif  mReset :
                break




    if  not handledResults.isEmpty() :
        if  not isOpenedFile :
            saveContent( fileName, content, codec )


        resultsHandled.emit( fileName, handledResults )


    if  isOpenedFile :
        openedFileHandled.emit( fileName, content, codec )



def run(self):
    QTime tracker

    forever
            QMutexLocker locker( &mMutex )
            mReset = False
            mExit = False


        tracker.restart()

        QStringList keys

            QMutexLocker locker( &mMutex )
            keys = mResults.keys()


        for fileName in keys:
            content = fileContent( fileName )

            replace( fileName, content )

                QMutexLocker locker( &mMutex )

                if  mExit :
                    return

                elif  mReset :
                    break




            QMutexLocker locker( &mMutex )

            if  mExit :
                return

            elif  mReset :
                continue



        break


    qWarning() << "Replace finished in " << tracker.elapsed() /1000.0

