#ifndef XUPPROJECTITEM_H
#define XUPPROJECTITEM_H

#include <QObject>
#include <QFileInfo>

#include <objects/MonkeyExport.h>

#include "XUPItem.h"
#include "XUPProjectItemInfos.h"
#include "consolemanager/pCommand.h"

class BuilderPlugin
class DebuggerPlugin
class InterpreterPlugin

typedef QList<class XUPProjectItem*> XUPProjectItemList

class Q_MONKEY_EXPORT XUPProjectItem : public QObject, XUPItem
    Q_OBJECT

public:
    # project type id
    enum ProjectType { InvalidProject = -1, XUPProject = 0
    # target type
    enum TargetType { DefaultTarget = 0, DebugTarget, ReleaseTarget
    # platform type
    enum PlatformType
        AnyPlatform = 0,
        WindowsPlatform,
        MacPlatform,
        OthersPlatform,
#if defined( Q_OS_WIN )
        CurrentPlatform = WindowsPlatform
#elif defined( Q_OS_MAC )
        CurrentPlatform = MacPlatform
#else:
        CurrentPlatform = OthersPlatform
#endif


    # ctor
    XUPProjectItem()
    # dtor
    virtual ~XUPProjectItem()

    # return the global static proejcts types informations
    static XUPProjectItemInfos* projectInfos()

    # the variable cache
    QMap<QString, variableCache()

    # set last encounter error
    void setLastError(  QString& error )
    # return the last encounter error
    QString lastError()

    # return the project absolute filename
    QString fileName()
    # return the project absolute path
    QString path()
    # return an absolute file name according to project path
    QString filePath(  QString& fileName )
    # return a filepath relative to project path
    QString relativeFilePath(  QString& fileName )
    # return the list of all source files for self project
    QStringList sourceFiles()
    # return the list of all source files for all projects from the root project
    QStringList topLevelProjectSourceFiles()

    # return the direct parent proejct if one, return itself
    XUPProjectItem* parentProject()
    # return the most toplevel project ( ie: the model root project )
    XUPProjectItem* topLevelProject()
    # return the parent project for include project ( recursive parent project for include project, return project itself )
    XUPProjectItem* rootIncludeProject()
    # return children project recursively according to bool
    XUPProjectItemList childrenProjects( bool recursive )

    # return icon filename for item
    QString iconFileName( XUPItem* item )
    # return the project icons path
    QString iconsPath()

    # return the display text of a project variable name
    QString variableDisplayText(  QString& variableName )

    # return the display text for the project item
    QString itemDisplayText( XUPItem* item )
    # return the display icon for the project item
    QIcon itemDisplayIcon( XUPItem* item )

    # rebuild the project cache by clearing values and analyzing again the project
    void rebuildCache()

    # split a multi line value into QStringList
    static QStringList splitMultiLineValue(  QString& value )
    # return the matching path ( from start ) between left and right string or null string if result isa drive on windows, or / on unix like
    QString matchingPath(  QString& left, right )
    # return the compressed result list of paths list given in parameter
    QStringList compressedPaths(  QStringList& paths )
    # return a list of QFileInfo having corresponding partial file path
    virtual QFileInfoList findFile(  QString& partialFilePath )
    # return all variable items named variableName until caller is found ( if define ) or until the the complete tree is scanned
    # if recursive is True, the scan recurse in each item, not
    virtual XUPItemList getVariables(  XUPItem* root, variableName, callerItem = 0, recursive = True )
    # return the project datas as qstring
    virtual QString toString()

    # return the project settings scope, it if needed
    XUPItem* projectSettingsScope( bool create )
    # return a project settings value as stringlist or string.
    virtual QStringList projectSettingsValues(  QString& variable, defaultValues = QStringList() )
    virtual QString projectSettingsValue(  QString& variable, defaultValue = QString() )
    # set a project setting value
    virtual void setProjectSettingsValues(  QString& variable, values )
    virtual void setProjectSettingsValue(  QString& variable, value )
    # add project setting value
    virtual void addProjectSettingsValues(  QString& variable, values )
    virtual void addProjectSettingsValue(  QString& variable, value )

    # return the project type id
    virtual int projectType()
    # return the textual representation key for target type
    virtual QString targetTypeString( XUPProjectItem.TargetType type )
    # return the current project target type
    virtual XUPProjectItem.TargetType projectTargetType()
    # return the textual representation key for platform type
    virtual QString platformTypeString( XUPProjectItem.PlatformType type )
    # register the project type
    virtual void registerProjectType()
    # unregister the project type
    virtual void unRegisterProjectType()
    # return a instance of self kind of projecttype
    # FIXME AK in future I think XUPProject will be abstract class
    inline virtual XUPProjectItem* newProject()
        return XUPProjectItem()

    # get a variable content in the project at the call instant
    virtual QString getVariableContent(  QString& variableName )
    # interpret the content, ie, variables by their content
    virtual QString interpretContent(  QString& content )
    # handle the inclusion of include files
    virtual bool handleIncludeFile( XUPItem* function )
    # analyze a project for caching the variables keys
    virtual bool analyze( XUPItem* item )
    # open a project with codec
    virtual bool open(  QString& fileName, codec )
    # save the project
    virtual bool save()
    # return the project target file, the binary / library file path, allowToAskUser is set to True - user might be asked for it via doalog
    virtual QString targetFilePath( allowToAskUser = False, type = XUPProjectItem.DefaultTarget, XUPProjectItem.PlatformType = XUPProjectItem.CurrentPlatform )
    QString targetFilePath(  pCommandTargetExecution& execution )

    # return plugin associated with the project
    virtual BuilderPlugin* builder(  plugin = QString() )
    virtual DebuggerPlugin* debugger(  plugin = QString() )
    virtual InterpreterPlugin* interpreter(  plugin = QString() )

    # add a pCommand in menu
    virtual void addCommand( pCommand& cmd, mnu )
    # install custom project actions in menus
    virtual void installCommands()
    # uninstall custom project actions in menus
    virtual void uninstallCommands()

public slots:
    # called when a watched path of a DynamicFolder have changed
    void directoryChanged(  QString& path )

protected:
    QDomDocument mDocument
    pCommandMap mCommands
    static XUPProjectItemInfos* mXUPProjectInfos
    static bool mFoundCallerItem

    QMap<QString, mVariableCache

signals:
    void installCommandRequested(  pCommand& cmd, mnu )
    void uninstallCommandRequested(  pCommand& cmd, mnu )


#endif # XUPPROJECTITEM_H
