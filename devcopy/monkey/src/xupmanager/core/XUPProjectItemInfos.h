#ifndef XUPPROJECTITEMINFOS_H
#define XUPPROJECTITEMINFOS_H

#include <objects/MonkeyExport.h>

#include <QStringList>
#include <QPair>
#include <QMap>
#include <QApplication>

typedef QPair<QString, PairStringStringList
typedef QList<PairStringStringList> StringStringListList

typedef QPair<QString, PairStringString
typedef QList<PairStringString> StringStringList

class XUPProjectItem

class Q_MONKEY_EXPORT XUPProjectItemInfos
    friend class XUPProjectItem

public:
    XUPProjectItemInfos()

    inline QString tr(  char* text )
        return qApp.translate( "XUPProjectItemInfos", text )


    # return True if proejct type is a registered proejct type else False
    bool isRegisteredType( int projectType )
    # register the proejct type
    void registerType( int projectType, projectItem )
    # unregister the projecttype
    void unRegisterType( int projectType )

    # return a valid project item for fileName
    XUPProjectItem* newProjectItem(  QString& fileName )

    # register the resource path for project type pixmap
    void registerPixmapsPath( int projectType, path )
    # return the resource path for proejct type pixmap
    QString pixmapsPath( int projectType )

    # register the operators for project type
    void registerOperators( int projectType, operators )
    # return the operators list for proejct type
    QStringList operators( int projectType )

    # register the filtered variable list for project type: ie the list a variable shown in filtered view
    void registerFilteredVariables( int projectType, variables )
    # return the filtered variable list for project type
    QStringList filteredVariables( int projectType )

    # register the file based variable list for project type: ie variables that contains filepath
    void registerFileVariables( int projectType, variables )
    # return the file based variables list for project type
    QStringList fileVariables( int projectType )

    # register the path based variable list for project type: ie variables that contains path
    void registerPathVariables( int projectType, variables )
    # return the path based variables list for project type
    QStringList pathVariables( int projectType )

    # register project type suffixes
    void registerSuffixes( int projectType, suffixes )
    # return the project type suffixes
    StringStringListList suffixes( int projectType )

    # register the project type variable labels: ie. the text shown for some variable in item view
    void registerVariableLabels( int projectType, labels )
    # return the project type variable labels
    StringStringList variableLabels( int projectType )

    # register the variable icons for project type
    void registerVariableIcons( int projectType, icons )
    # return the variable icons for project type
    StringStringList variableIcons( int projectType )

    # register variable suffixes for project type: ie. for file base variable, suffixes they can handle
    void registerVariableSuffixes( int projectType, suffixes )
    # return the variable suffixes for project type
    StringStringListList variableSuffixes( int projectType )

    # return a filter of all project type suffixes: ie. for giving it to open/save file dialog
    QString projectsFilter()
    # return the project type to use for opening the filename project or -1 if no project type can handle the suffixe
    int projectTypeForFileName(  QString& fileName )
    # return True if variable name is variable wich values are files
    bool isFileBased( int projectType, variableName )
    # return True if variable name is variable wich values are paths
    bool isPathBased( int projectType, variableName )
    # return the icon name for a variable name or QString.null
    QString iconName( int projectType, variableName )
    # return the display text for a variable name or itself if no match found
    QString displayText( int projectType, variableName )
    # return the disply icon for a variable name
    QIcon displayIcon( int projectType, variableName )
    # return the icons path for proejct type
    QString iconsPath( int projectType )
    # return a files filter for variables base on files
    QString variableSuffixesFilter( int projectType )
    # return the variable name associated with self filename
    QString variableNameForFileName( int projectType, fileName )
    # return a list of all know variable for self kind of project
    QStringList knowVariables( int projectType )

protected:
    QMap<int, mRegisteredProjectItems; # project type, item
    QMap<int, mPixmapsPath; # project type, path
    QMap<int, mOperators; # project type, operators
    QMap<int, mFilteredVariables; # project type, variable name
    QMap<int, mFileVariables; # project type, based variable name
    QMap<int, mPathVariables; # project type, based variable name
    QMap<int, mSuffixes; # project type, label, suffixes
    QMap<int, mVariableLabels; # project type, name, label
    QMap<int, mVariableIcons; # project type, name, icon
    QMap<int, mVariableSuffixes; # project type, based variable name, suffixes


#endif # XUPPROJECTITEMINFOS_H
