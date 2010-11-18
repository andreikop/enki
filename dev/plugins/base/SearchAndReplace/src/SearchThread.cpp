#include "SearchThread.h"

#include <QMutexLocker>
#include <QTextCodec>
#include <QTime>
#include <QTimer>
#include <QDebug>

int SearchThread::mMaxTime = 125;

SearchThread::SearchThread( QObject* parent )
	: QThread( parent )
{
	mReset = false;
	mExit = false;

	qRegisterMetaType<SearchResultsModel::ResultList>( "SearchResultsModel::ResultList" );
}

SearchThread::~SearchThread()
{
	stop();
	wait();
}

void SearchThread::search( const SearchAndReplace::Properties& properties )
{
	{
		QMutexLocker locker( &mMutex );
		mProperties = properties;
		mReset = isRunning() ? true : false;
		mExit = false;
	}

	if ( !isRunning() )
	{
		start();
	}
}

void SearchThread::stop()
{
	{
		QMutexLocker locker( &mMutex );
		mReset = false;
		mExit = true;
	}
}

SearchAndReplace::Properties* SearchThread::properties() const
{
	QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );
	return &const_cast<SearchThread*>( this )->mProperties;
}

QStringList SearchThread::getFiles( QDir fromDir, const QStringList& filters, bool recursive ) const
{
	QStringList files;

	foreach ( const QFileInfo& file, fromDir.entryInfoList( QDir::AllEntries | QDir::AllDirs | QDir::NoDotAndDotDot, QDir::DirsFirst | QDir::Name ) )
	{
		if ( file.isFile() && ( filters.isEmpty() || QDir::match( filters, file.fileName() ) ) )
		{
			files << file.absoluteFilePath();
		}
		else if ( file.isDir() && recursive )
		{
			fromDir.cd( file.filePath() );
			files << getFiles( fromDir, filters, recursive );
			fromDir.cdUp();
		}

		{
			QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );

			if ( mReset || mExit )
			{
				return files;
			}
		}
	}

	return files;
}

QStringList SearchThread::getFilesToScan() const
{
	QSet<QString> files;
	SearchAndReplace::Mode mode = SearchAndReplace::ModeNo;

	{
		QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );
		mode = mProperties.mode;
	}

	switch ( mode )
	{
		case SearchAndReplace::ModeNo:
		case SearchAndReplace::ModeSearch:
		case SearchAndReplace::ModeReplace:
			qWarning() << "Invalid mode used.";
			Q_ASSERT( 0 );
			return files.toList();
		case SearchAndReplace::ModeSearchDirectory:
		case SearchAndReplace::ModeReplaceDirectory:
		{
			QString path;
			QStringList mask;

			{
				QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );
				path = mProperties.searchPath;
				mask = mProperties.mask;
			}

			QDir dir( path );
			files = getFiles( dir, mask, true ).toSet();
			break;
		}
		case SearchAndReplace::ModeSearchProjectFiles:
		case SearchAndReplace::ModeReplaceProjectFiles:
		{
			QStringList sources;
			QStringList mask;

			{
				QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );
				sources = mProperties.sourcesFiles;
				mask = mProperties.mask;
			}

			foreach ( const QString& fileName, sources )
			{
				if ( QDir::match( mask, fileName ) )
				{
					files << fileName;
				}

				{
					QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );

					if ( mReset || mExit )
					{
						return files.toList();
					}
				}
			}
			break;
		}
		case SearchAndReplace::ModeSearchOpenedFiles:
		case SearchAndReplace::ModeReplaceOpenedFiles:
		{
			QStringList sources;
			QStringList mask;

			{
				QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );
				sources = mProperties.openedFiles.keys();
				mask = mProperties.mask;
			}

			foreach ( const QString& fileName, sources )
			{
				if ( QDir::match( mask, fileName ) )
				{
					files << fileName;
				}

				{
					QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );

					if ( mReset || mExit )
					{
						return files.toList();
					}
				}
			}
			break;
		}
	}

	return files.toList();
}

QString SearchThread::fileContent( const QString& fileName ) const
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

void SearchThread::search( const QString& fileName, const QString& content ) const
{
	static const QString eol( "\n" );
	bool checkable = false;
	bool isRE = false;
	QRegExp rx;
	
	{
		QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );

		isRE = mProperties.options & SearchAndReplace::OptionRegularExpression;
		const bool isWw = mProperties.options & SearchAndReplace::OptionWholeWord;
		const bool isCS = mProperties.options & SearchAndReplace::OptionCaseSensitive;
		const Qt::CaseSensitivity sensitivity = isCS ? Qt::CaseSensitive : Qt::CaseInsensitive;
		checkable = mProperties.mode & SearchAndReplace::ModeFlagReplace;
		QString pattern = isRE ? mProperties.searchText : QRegExp::escape( mProperties.searchText );

		if ( isWw )
		{
			pattern.prepend( "\\b" ).append( "\\b" );
		}

		rx.setMinimal( true );
		rx.setPattern( pattern );
		rx.setCaseSensitivity( sensitivity );
	}
	
	int pos = 0;
	int lastPos = 0;
	int eolCount = 0;
	SearchResultsModel::ResultList results;
	QTime tracker;

	tracker.start();

	while ( ( pos = rx.indexIn( content, pos ) ) != -1 )
	{
		const int eolStart = content.lastIndexOf( eol, pos );
		const int eolEnd = content.indexOf( eol, pos );
		const QString capture = content.mid( eolStart + 1, eolEnd -1 -eolStart ).simplified();
		eolCount += content.mid( lastPos, pos -lastPos ).count( eol );
		const int column = ( pos -eolStart ) -( eolStart != 0 ? 1 : 0 );
		SearchResultsModel::Result* result = new SearchResultsModel::Result( fileName, capture );
		result->position = QPoint( column, eolCount );
		result->offset = pos;
		result->length = rx.matchedLength();
		result->checkable = checkable;
		result->checkState = checkable ? Qt::Checked : Qt::Unchecked;
		result->capturedTexts = isRE ? rx.capturedTexts() : QStringList();

		results << result;

		lastPos = pos;
		pos += rx.matchedLength();

		if ( tracker.elapsed() >= mMaxTime )
		{
			emit const_cast<SearchThread*>( this )->resultsAvailable( fileName, results );
			results.clear();
			tracker.restart();
		}

		{
			QMutexLocker locker( const_cast<QMutex*>( &mMutex ) );

			if ( mReset || mExit )
			{
				return;
			}
		}
	}

	if ( !results.isEmpty() )
	{
		emit const_cast<SearchThread*>( this )->resultsAvailable( fileName, results );
	}
}

void SearchThread::run()
{
	QTime tracker;

	forever
	{
		{
			QMutexLocker locker( &mMutex );
			mReset = false;
			mExit = false;
		}

		emit reset();
		emit progressChanged( -1, 0 );
		tracker.restart();

		QStringList files = getFilesToScan();
		files.sort();

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
		
		const int total = files.count();
		int value = 0;
		
		emit progressChanged( 0, total );

		foreach ( const QString& fileName, files )
		{
			const QString content = fileContent( fileName );
			search( fileName, content );
			value++;
			
			emit progressChanged( value, total );

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

			if ( mReset )
			{
				continue;
			}
		}

		break;
	}

	qWarning() << "Search finished in " << tracker.elapsed() /1000.0;
}

void SearchThread::clear()
{
	stop();
	emit reset();
}
