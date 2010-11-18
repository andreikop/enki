#include "XUPProjectItemInfos.h"
#include "XUPProjectItem.h"

#include <objects/pIconManager.h>

#include <QDir>

#include <QDebug>

XUPProjectItemInfos.XUPProjectItemInfos()


def isRegisteredType(self, projectType ):
    return mRegisteredProjectItems.keys().contains( projectType )


def registerType(self, projectType, projectItem ):
    if  not isRegisteredType( projectType ) :
        mRegisteredProjectItems[ projectType ] = projectItem


def unRegisterType(self, projectType ):
    delete mRegisteredProjectItems.take( projectType )
    mPixmapsPath.remove( projectType )
    mOperators.remove( projectType )
    mFilteredVariables.remove( projectType )
    mFileVariables.remove( projectType )
    mPathVariables.remove( projectType )
    mSuffixes.remove( projectType )
    mVariableLabels.remove( projectType )
    mVariableIcons.remove( projectType )
    mVariableSuffixes.remove( projectType )


def newProjectItem(self, fileName ):
    projectType = projectTypeForFileName( fileName )
    return projectType == XUPProjectItem.InvalidProject ? 0 : mRegisteredProjectItems[ projectType ].newProject()


def registerPixmapsPath(self, projectType, path ):
    mPixmapsPath[ projectType ] = path


def pixmapsPath(self, projectType ):
    return mPixmapsPath.value( projectType )


def registerOperators(self, projectType, operators ):
    mOperators[ projectType ] = operators


def operators(self, projectType ):
    return mOperators.value( projectType )


def registerFilteredVariables(self, projectType, variables ):
    mFilteredVariables[ projectType ] = variables


def filteredVariables(self, projectType ):
    return mFilteredVariables.value( projectType )


def registerFileVariables(self, projectType, variables ):
    mFileVariables[ projectType ] = variables


def fileVariables(self, projectType ):
    return mFileVariables.value( projectType )


def registerPathVariables(self, projectType, variables ):
    mPathVariables[ projectType ] = variables


def pathVariables(self, projectType ):
    return mPathVariables.value( projectType )


def registerSuffixes(self, projectType, suffixes ):
    mSuffixes[ projectType ] = suffixes


def suffixes(self, projectType ):
    return mSuffixes.value( projectType )


def registerVariableLabels(self, projectType, labels ):
    mVariableLabels[ projectType ] = labels


def variableLabels(self, projectType ):
    return mVariableLabels.value( projectType )


def registerVariableIcons(self, projectType, icons ):
    mVariableIcons[ projectType ] = icons


def variableIcons(self, projectType ):
    return mVariableIcons.value( projectType )


def registerVariableSuffixes(self, projectType, suffixes ):
    mVariableSuffixes[ projectType ] = suffixes


def variableSuffixes(self, projectType ):
    return mVariableSuffixes.value( projectType )


def projectsFilter(self):
    QStringList suffixes
    QStringList filters
    for projectType in mSuffixes.keys():
        foreach (  PairStringStringList& p, mSuffixes[ projectType ] )
            suffixes << p.second
            filters << QString( "%1 (%2)" ).arg( p.first ).arg( p.second.join( " " ) )


    if  not filters.isEmpty() :
        filters.prepend( tr( QT_TR_NOOP( "All Projects (%1)" ) ).arg( suffixes.join( " " ) ) )
    return filters.join( ";;" )


def projectTypeForFileName(self, fileName ):
    for projectType in mSuffixes.keys():
        foreach (  PairStringStringList& p, mSuffixes[ projectType ] )
            if  QDir.match( p.second, fileName ) :
                return projectType


    return XUPProjectItem.InvalidProject


def isFileBased(self, projectType, variableName ):
    return mFileVariables.value( projectType ).contains( variableName )


def isPathBased(self, projectType, variableName ):
    return mPathVariables.value( projectType ).contains( variableName )


def iconName(self, projectType, variableName ):
    foreach (  PairStringString& pair, mVariableIcons.value( projectType ) )
        if  pair.first == variableName :
            return pair.second

    return QString.null


def displayText(self, projectType, variableName ):
    foreach (  PairStringString& pair, mVariableLabels.value( projectType ) )
        if  pair.first == variableName :
            return pair.second

    return variableName


def displayIcon(self, projectType, variableName ):
    QIcon icon
    path = iconsPath( projectType )
    fn = pIconManager.filePath( iconName( projectType, variableName ).append( ".png" ), path )
    
    if  not QFile.exists( fn ) :
        path = pixmapsPath( XUPProjectItem.XUPProject )

    
    icon = pIconManager.icon( iconName( projectType, variableName ).append( ".png" ), path )
    
    return icon


def iconsPath(self, projectType ):
    path = pixmapsPath( projectType )
    
    if  path.isEmpty() and projectType != XUPProjectItem.XUPProject :
        path = pixmapsPath( XUPProjectItem.XUPProject )

    
    return path


def variableSuffixesFilter(self, projectType ):
     suffixes = variableSuffixes( projectType )
    QStringList allSuffixesList
    QStringList suffixesList
    
    for pair in suffixes:
        text = displayText( projectType, pair.first )
        suffixesList << QString( "%1 (%2)" ).arg( text ).arg( pair.second.join( " " ) )
        
        for suffixe in pair.second:
            if  not allSuffixesList.contains( suffixe ) :
                allSuffixesList << suffixe



    
    suffixesList.prepend( tr( "All Files (*)" ) )
    
    if  not allSuffixesList.isEmpty() :
        suffixesList.prepend( tr( "All Supported Files (%2)" ).arg( allSuffixesList.join( " " ) ) )

    
    return suffixesList.join( ";;" )


def variableNameForFileName(self, projectType, fileName ):
     suffixes = variableSuffixes( projectType )
    
    for pair in suffixes:
        variable = pair.first
        
        if  QDir.match( pair.second, fileName ) :
            return pair.first


    
    return QString.null


def knowVariables(self, projectType ):
    QStringList variables
    
    foreach (  QString& variable, mFilteredVariables.value( projectType ) )
        if  not variables.contains( variable ) :
            variables << variable


    
    foreach (  QString& variable, mFileVariables.value( projectType ) )
        if  not variables.contains( variable ) :
            variables << variable


    
    foreach (  QString& variable, mPathVariables.value( projectType ) )
        if  not variables.contains( variable ) :
            variables << variable


    
    foreach (  PairStringString& pair, mVariableLabels.value( projectType ) )
        if  not variables.contains( pair.first ) :
            variables << pair.first


    
    foreach (  PairStringString& pair, mVariableIcons.value( projectType ) )
        if  not variables.contains( pair.first ) :
            variables << pair.first


    
    foreach (  PairStringStringList& pair, mVariableSuffixes.value( projectType ) )
        if  not variables.contains( pair.first ) :
            variables << pair.first


    
    variables.sort()
    return variables

