#include "ReplaceThread.h"
#include "SearchWidget.h"

#include <QMutexLocker>
#include <QTextCodec>
#include <QTime>
#include <QDebug>

int ReplaceThread::mMaxTime = 125;

ReplaceThread::ReplaceThread( QObject* parent )
    : QThread( parent )
{
    mReset = false;
    mExit = false;
}

ReplaceThread::~ReplaceThread()
{
    stop();
    wait();
}

void ReplaceThread::replace( const SearchAndReplace::Properties& properties, const QHash<QString, SearchResultsModel::ResultList>& results )
{
    {
        QMutexLocker locker( &mMutex );
        mProperties = properties;
        mResults = results;
        mReset = isRunning() ? true : false;
        mExit = false;
    }

    if ( !isRunning() )
    {
        start();
    }
}

void ReplaceThread::stop()
{
    {
        QMutexLocker locker( &mMutex );
        mReset = false;
        mExit = true;
    }
}

void ReplaceThread::saveContent( const QString& fileName, const QString& content, const QString& codec )
{
    QFile file( fileName );

    if ( !file.open( QIODevice::WriteOnly ) )
    {
        emit error( tr( "Error while saving replaced content: %1" ).arg( file.errorString() ) );
        return;
    }

    file.resize( 0 );

    QTextCodec* textCodec = QTextCodec::codecForName( codec.toLocal8Bit() );

    Q_ASSERT( textCodec );

    if ( file.write( textCodec->fromUnicode( content ) ) == -1 )
    {
        emit error( tr( "Error while saving replaced content: %1" ).arg( file.errorString() ) );
        return;
    }

    file.close();
}

QString ReplaceThread::fileContent( const QString& fileName ) const
{
    QTextCodec* codec = 0;

    {
        QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );

        codec = QTextCodec::codecForName( mProperties.codec.toLocal8Bit() );

        if ( mProperties.openedFiles.contains( fileName ) )
        {
            return mProperties.openedFiles[ fileName ];
        }
    }

    Q_ASSERT( codec );

    QFile file( fileName );

    if ( !file.open( QIODevice::ReadOnly ) )
    {
        return QString::null;
    }

    if ( SearchWidget::isBinary( file ) )
    {
        return QString::null;
    }

    return codec->toUnicode( file.readAll() );
}

void ReplaceThread::replace( const QString& fileName, QString content )
{
    QString replaceText;
    QString codec;
    SearchResultsModel::ResultList results;
    bool isOpenedFile = false;
    bool isRE = false;
    SearchResultsModel::ResultList handledResults;

    {
        QMutexLocker locker( &mMutex );
        replaceText = mProperties.replaceText;
        codec = mProperties.codec;
        results = mResults[ fileName ];
        isOpenedFile = mProperties.openedFiles.contains( fileName );
        isRE = mProperties.options & SearchAndReplace::OptionRegularExpression;
    }
/*
    QTime tracker;
    tracker.start();
*/
    static QRegExp rx( "\\$(\\d+)" );
    rx.setMinimal( true );

    // count from end to begin because we are replacing by offset in content
    for ( int i = results.count() -1; i > -1; i-- )
    {
        SearchResultsModel::Result* result = results.at( i );
        const int searchLength = result->length;
        const QStringList captures = result->capturedTexts;
    
        // compute replace text
        if ( isRE && captures.count() > 1 ) {
            int pos = 0;
            
            while ( ( pos = rx.indexIn( replaceText, pos ) ) != -1 ) {
                const int id = rx.cap( 1 ).toInt();
                
                if ( id < 0 || id >= captures.count() ) {
                    pos += rx.matchedLength();
                    continue;
                }
                
                // update replace text with partial occurrences
                replaceText.replace( pos, rx.matchedLength(), captures.at( id ) );
                
                // next
                pos += captures.at( id ).length();
            }
        }
        
        // replace text
        content.replace( result->offset, searchLength, replaceText );

        handledResults << result;
/*
        if ( tracker.elapsed() >= mMaxTime )
        {
            if ( !handledResults.isEmpty() )
            {
                if ( !isOpenedFile )
                {
                    saveContent( fileName, content, codec );
                }

                emit resultsHandled( fileName, handledResults );
            }

            if ( isOpenedFile )
            {
                emit openedFileHandled( fileName, content, codec );
            }

            handledResults.clear();
            tracker.restart();
        }
*/
        {
            QMutexLocker locker( &mMutex );

            if ( mExit )
            {
                return;
            }
            else if ( mReset )
            {
                break;
            }
        }
    }

    if ( !handledResults.isEmpty() )
    {
        if ( !isOpenedFile )
        {
            saveContent( fileName, content, codec );
        }

        emit resultsHandled( fileName, handledResults );
    }

    if ( isOpenedFile )
    {
        emit openedFileHandled( fileName, content, codec );
    }
}

void ReplaceThread::run()
{
    QTime tracker;

    forever
    {
        {
            QMutexLocker locker( &mMutex );
            mReset = false;
            mExit = false;
        }

        tracker.restart();

        QStringList keys;

        {
            QMutexLocker locker( &mMutex );
            keys = mResults.keys();
        }

        foreach ( const QString& fileName, keys )
        {
            QString content = fileContent( fileName );

            replace( fileName, content );

            {
                QMutexLocker locker( &mMutex );

                if ( mExit )
                {
                    return;
                }
                else if ( mReset )
                {
                    break;
                }
            }
        }

        {
            QMutexLocker locker( &mMutex );

            if ( mExit )
            {
                return;
            }
            else if ( mReset )
            {
                continue;
            }
        }

        break;
    }

    qWarning() << "Replace finished in " << tracker.elapsed() /1000.0;
}
