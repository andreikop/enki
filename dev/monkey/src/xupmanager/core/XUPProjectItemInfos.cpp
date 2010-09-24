#include "XUPProjectItemInfos.h"
#include "XUPProjectItem.h"

#include <objects/pIconManager.h>

#include <QDir>

#include <QDebug>

XUPProjectItemInfos::XUPProjectItemInfos()
{
}

bool XUPProjectItemInfos::isRegisteredType( int projectType ) const
{
	return mRegisteredProjectItems.keys().contains( projectType );
}

void XUPProjectItemInfos::registerType( int projectType, XUPProjectItem* projectItem )
{
	if ( !isRegisteredType( projectType ) )
		mRegisteredProjectItems[ projectType ] = projectItem;
}

void XUPProjectItemInfos::unRegisterType( int projectType )
{
	delete mRegisteredProjectItems.take( projectType );
	mPixmapsPath.remove( projectType );
	mOperators.remove( projectType );
	mFilteredVariables.remove( projectType );
	mFileVariables.remove( projectType );
	mPathVariables.remove( projectType );
	mSuffixes.remove( projectType );
	mVariableLabels.remove( projectType );
	mVariableIcons.remove( projectType );
	mVariableSuffixes.remove( projectType );
}

XUPProjectItem* XUPProjectItemInfos::newProjectItem( const QString& fileName ) const
{
	int projectType = projectTypeForFileName( fileName );
	return projectType == XUPProjectItem::InvalidProject ? 0 : mRegisteredProjectItems[ projectType ]->newProject();
}

void XUPProjectItemInfos::registerPixmapsPath( int projectType, const QString& path )
{
	mPixmapsPath[ projectType ] = path;
}

QString XUPProjectItemInfos::pixmapsPath( int projectType ) const
{
	return mPixmapsPath.value( projectType );
}

void XUPProjectItemInfos::registerOperators( int projectType, const QStringList& operators )
{
	mOperators[ projectType ] = operators;
}

QStringList XUPProjectItemInfos::operators( int projectType ) const
{
	return mOperators.value( projectType );
}

void XUPProjectItemInfos::registerFilteredVariables( int projectType, const QStringList& variables )
{
	mFilteredVariables[ projectType ] = variables;
}

QStringList XUPProjectItemInfos::filteredVariables( int projectType ) const
{
	return mFilteredVariables.value( projectType );
}

void XUPProjectItemInfos::registerFileVariables( int projectType, const QStringList& variables )
{
	mFileVariables[ projectType ] = variables;
}

QStringList XUPProjectItemInfos::fileVariables( int projectType ) const
{
	return mFileVariables.value( projectType );
}

void XUPProjectItemInfos::registerPathVariables( int projectType, const QStringList& variables )
{
	mPathVariables[ projectType ] = variables;
}

QStringList XUPProjectItemInfos::pathVariables( int projectType ) const
{
	return mPathVariables.value( projectType );
}

void XUPProjectItemInfos::registerSuffixes( int projectType, const StringStringListList& suffixes )
{
	mSuffixes[ projectType ] = suffixes;
}

StringStringListList XUPProjectItemInfos::suffixes( int projectType ) const
{
	return mSuffixes.value( projectType );
}

void XUPProjectItemInfos::registerVariableLabels( int projectType, const StringStringList& labels )
{
	mVariableLabels[ projectType ] = labels;
}

StringStringList XUPProjectItemInfos::variableLabels( int projectType ) const
{
	return mVariableLabels.value( projectType );
}

void XUPProjectItemInfos::registerVariableIcons( int projectType, const StringStringList& icons )
{
	mVariableIcons[ projectType ] = icons;
}

StringStringList XUPProjectItemInfos::variableIcons( int projectType ) const
{
	return mVariableIcons.value( projectType );
}

void XUPProjectItemInfos::registerVariableSuffixes( int projectType, const StringStringListList& suffixes )
{
	mVariableSuffixes[ projectType ] = suffixes;
}

StringStringListList XUPProjectItemInfos::variableSuffixes( int projectType ) const
{
	return mVariableSuffixes.value( projectType );
}

QString XUPProjectItemInfos::projectsFilter() const
{
	QStringList suffixes;
	QStringList filters;
	foreach ( const int& projectType, mSuffixes.keys() )
	{
		foreach ( const PairStringStringList& p, mSuffixes[ projectType ] )
		{
			suffixes << p.second;
			filters << QString( "%1 (%2)" ).arg( p.first ).arg( p.second.join( " " ) );
		}
	}
	if ( !filters.isEmpty() )
		filters.prepend( tr( QT_TR_NOOP( "All Projects (%1)" ) ).arg( suffixes.join( " " ) ) );
	return filters.join( ";;" );
}

int XUPProjectItemInfos::projectTypeForFileName( const QString& fileName ) const
{
	foreach ( const int& projectType, mSuffixes.keys() )
	{
		foreach ( const PairStringStringList& p, mSuffixes[ projectType ] )
		{
			if ( QDir::match( p.second, fileName ) )
				return projectType;
		}
	}
	return XUPProjectItem::InvalidProject;
}

bool XUPProjectItemInfos::isFileBased( int projectType, const QString& variableName ) const
{
	return mFileVariables.value( projectType ).contains( variableName );
}

bool XUPProjectItemInfos::isPathBased( int projectType, const QString& variableName ) const
{
	return mPathVariables.value( projectType ).contains( variableName );
}

QString XUPProjectItemInfos::iconName( int projectType, const QString& variableName ) const
{
	foreach ( const PairStringString& pair, mVariableIcons.value( projectType ) )
	{
		if ( pair.first == variableName )
			return pair.second;
	}
	return QString::null;
}

QString XUPProjectItemInfos::displayText( int projectType, const QString& variableName ) const
{
	foreach ( const PairStringString& pair, mVariableLabels.value( projectType ) )
	{
		if ( pair.first == variableName )
			return pair.second;
	}
	return variableName;
}

QIcon XUPProjectItemInfos::displayIcon( int projectType, const QString& variableName ) const
{
	QIcon icon;
	QString path = iconsPath( projectType );
	QString fn = pIconManager::filePath( iconName( projectType, variableName ).append( ".png" ), path );
	
	if ( !QFile::exists( fn ) )
	{
		path = pixmapsPath( XUPProjectItem::XUPProject );
	}
	
	icon = pIconManager::icon( iconName( projectType, variableName ).append( ".png" ), path );
	
	return icon;
}

QString XUPProjectItemInfos::iconsPath( int projectType ) const
{
	QString path = pixmapsPath( projectType );
	
	if ( path.isEmpty() && projectType != XUPProjectItem::XUPProject )
	{
		path = pixmapsPath( XUPProjectItem::XUPProject );
	}
	
	return path;
}

QString XUPProjectItemInfos::variableSuffixesFilter( int projectType ) const
{
	const StringStringListList suffixes = variableSuffixes( projectType );
	QStringList allSuffixesList;
	QStringList suffixesList;
	
	foreach ( const PairStringStringList& pair, suffixes )
	{
		QString text = displayText( projectType, pair.first );
		suffixesList << QString( "%1 (%2)" ).arg( text ).arg( pair.second.join( " " ) );
		
		foreach ( const QString& suffixe, pair.second )
		{
			if ( !allSuffixesList.contains( suffixe ) )
			{
				allSuffixesList << suffixe;
			}
		}
	}
	
	suffixesList.prepend( tr( "All Files (*)" ) );
	
	if ( !allSuffixesList.isEmpty() )
	{
		suffixesList.prepend( tr( "All Supported Files (%2)" ).arg( allSuffixesList.join( " " ) ) );
	}
	
	return suffixesList.join( ";;" );
}

QString XUPProjectItemInfos::variableNameForFileName( int projectType, const QString& fileName ) const
{
	const StringStringListList suffixes = variableSuffixes( projectType );
	
	foreach ( const PairStringStringList& pair, suffixes )
	{
		QString variable = pair.first;
		
		if ( QDir::match( pair.second, fileName ) )
		{
			return pair.first;
		}
	}
	
	return QString::null;
}

QStringList XUPProjectItemInfos::knowVariables( int projectType ) const
{
	QStringList variables;
	
	foreach ( const QString& variable, mFilteredVariables.value( projectType ) )
	{
		if ( !variables.contains( variable ) )
		{
			variables << variable;
		}
	}
	
	foreach ( const QString& variable, mFileVariables.value( projectType ) )
	{
		if ( !variables.contains( variable ) )
		{
			variables << variable;
		}
	}
	
	foreach ( const QString& variable, mPathVariables.value( projectType ) )
	{
		if ( !variables.contains( variable ) )
		{
			variables << variable;
		}
	}
	
	foreach ( const PairStringString& pair, mVariableLabels.value( projectType ) )
	{
		if ( !variables.contains( pair.first ) )
		{
			variables << pair.first;
		}
	}
	
	foreach ( const PairStringString& pair, mVariableIcons.value( projectType ) )
	{
		if ( !variables.contains( pair.first ) )
		{
			variables << pair.first;
		}
	}
	
	foreach ( const PairStringStringList& pair, mVariableSuffixes.value( projectType ) )
	{
		if ( !variables.contains( pair.first ) )
		{
			variables << pair.first;
		}
	}
	
	variables.sort();
	return variables;
}
