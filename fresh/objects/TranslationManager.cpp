#include "TranslationManager.h"

#include <QDir>
#include <QCoreApplication>
#include <QTranslator>
#include <QLibraryInfo>
#include <QDebug>

TranslationManager::TranslationManager( QObject* parent )
	: QObject( parent )
{
	mCurrentLocale = systemLocale();
	mSystemTranslationsPaths << QLibraryInfo::location( QLibraryInfo::TranslationsPath );
	mFakeCLocaleEnabled = false;
}

TranslationManager::~TranslationManager()
{
}

bool TranslationManager::addTranslator( const QString& filePath, const QLocale& locale )
{
	QTranslator* translator = new QTranslator( QCoreApplication::instance() );
	
	if ( translator->load( filePath ) ) {
		QCoreApplication::installTranslator( translator );
		mTranslators[ locale ] << translator;
		//qWarning() << "added" << filePath << locale.name();
		return true;
	}
	
	delete translator;
	return false;
}

void TranslationManager::clearTranslators()
{
	foreach ( const QLocale& locale, mTranslators.keys() ) {
		foreach ( QTranslator* translator, mTranslators[ locale ] ) {
			QCoreApplication::removeTranslator( translator );
		}
		
		qDeleteAll( mTranslators[ locale ] );
	}
	
	mAvailableLocales.clear();
	mTranslators.clear();
}

QStringList TranslationManager::availableLocales() const
{
	return mAvailableLocales.toList();
}

QList<QLocale> TranslationManager::availableQLocales() const
{
	QList<QLocale> locales;
	
	foreach ( const QString& locale, availableLocales() ) {
		locales << QLocale( locale );
	}
	
	return locales;
}

void TranslationManager::reloadTranslations()
{
	clearTranslators();
	
	const QStringList paths = QStringList() << mTranslationsPaths << mSystemTranslationsPaths;
	const QString appDirPath = qApp->applicationDirPath();
	QList<QFileInfo> files;
	QSet<QString> translations;

	foreach ( QString path, paths ) {
		if ( QDir::isRelativePath( path ) ) {
			path = QString( "%1/%2" ).arg( appDirPath ).arg( path );
		}
		
		files << QDir( path ).entryInfoList( mTranslationsMasks.toList() );
	}
	
	foreach ( const QFileInfo& file, files ) {
		const QString cfp = file.canonicalFilePath();
		QString fileName = file.fileName();
		
		if ( translations.contains( cfp )
			|| QDir::match( mForbiddenTranslationsMasks.toList(), fileName ) ) {
			continue;
		}
		
		fileName.remove( ".qm", Qt::CaseInsensitive ).replace( ".", "_" );
		const int count = fileName.count( "_" );
		bool added = false;
		bool foundValidLocale = false;
		QLocale locale;
		
		for ( int i = 1; i < count +1; i++ ) {
			QString part = fileName.section( '_', i );
			
			if ( part.toLower() == "iw" || part.toLower().endsWith( "_iw" ) )
			{
				part.replace( "iw", "he" );
			}
			
			locale = QLocale( part );
			
			//qWarning() << fileName << part << locale.name() << mCurrentLocale.name();
			
			if ( locale != QLocale::c() ) {
				foundValidLocale = true;
				mAvailableLocales << locale.name();
				
				if ( locale == mCurrentLocale
					|| locale.language() == mCurrentLocale.language() ) {
					if ( addTranslator( cfp, locale ) ) {
						translations << cfp;
						added = true;
					}
				}
				
				break;
			}
		}
		
		if ( foundValidLocale || added /*|| mCurrentLocale != QLocale::c()*/ ) {
			continue;
		}
		
		mAvailableLocales << QLocale::c().name();
		
		if ( mCurrentLocale.language() == QLocale::C
			|| mCurrentLocale.language() == QLocale::English ) {
			if ( addTranslator( cfp, QLocale::c() ) ) {
				translations << cfp;
			}
		}
	}
	
	if ( !mAvailableLocales.contains( QLocale::c().name() ) && mFakeCLocaleEnabled ) {
		mAvailableLocales << QLocale::c().name();
	}
}

QStringList TranslationManager::translationsMasks() const
{
	return mTranslationsMasks.toList();
}

void TranslationManager::setTranslationsMasks( const QStringList& masks )
{
	mTranslationsMasks = masks.toSet();
}

void TranslationManager::addTranslationsMask( const QString& mask )
{
	mTranslationsMasks << mask;
}

void TranslationManager::removeTranslationsMask( const QString& mask )
{
	mTranslationsMasks.remove( mask );
}

QStringList TranslationManager::forbiddenTranslationsMasks() const
{
	return mForbiddenTranslationsMasks.toList();
}

void TranslationManager::setForbiddenTranslationsMasks( const QStringList& masks )
{
	mForbiddenTranslationsMasks = masks.toSet();
}

void TranslationManager::addForbiddenTranslationsMask( const QString& mask )
{
	mForbiddenTranslationsMasks << mask;
}

void TranslationManager::removeForbiddenTranslationsMask( const QString& mask )
{
	mForbiddenTranslationsMasks.remove( mask );
}

QLocale TranslationManager::currentLocale() const
{
	return mCurrentLocale;
}

QLocale TranslationManager::systemLocale() const
{
	return QLocale::system();
}

void TranslationManager::setCurrentLocale( const QLocale& locale )
{
	mCurrentLocale = locale;
}

QStringList TranslationManager::translationsPaths() const
{
	return mTranslationsPaths;
}

void TranslationManager::setTranslationsPaths( const QStringList& paths )
{
	mTranslationsPaths = paths;
}

QStringList TranslationManager::systemTranslationsPaths() const
{
	return mSystemTranslationsPaths;
}

void TranslationManager::setSystemTranslationsPaths( const QStringList& paths )
{
	mSystemTranslationsPaths = paths;
}

void TranslationManager::setFakeCLocaleEnabled( bool enabled )
{
	mFakeCLocaleEnabled = enabled;
}

bool TranslationManager::isFakeCLocaleEnabled() const
{
	return mFakeCLocaleEnabled;
}
