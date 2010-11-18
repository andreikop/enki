#include "XUPProjectItem.h"
#include "XUPProjectItemHelper.h"
#include "XUPProjectModel.h"
#include "pluginsmanager/BuilderPlugin.h"
#include "pluginsmanager/DebuggerPlugin.h"
#include "pluginsmanager/InterpreterPlugin.h"
#include "coremanager/MonkeyCore.h"
#include "pluginsmanager/PluginsManager.h"
#include "pMonkeyStudio.h"
#include "maininterface/UIMain.h"

#include <objects/pIconManager.h>
#include <widgets/pMenuBar.h>

#include <QTextCodec>
#include <QDir>
#include <QRegExp>
#include <QProcess>
#include <QFileDialog>
#include <QLibrary>

#include <QDebug>

 XUP_VERSION = "1.1.0"

XUPProjectItemInfos* XUPProjectItem.mXUPProjectInfos = XUPProjectItemInfos()
bool XUPProjectItem.mFoundCallerItem = False

XUPProjectItem.XUPProjectItem()
    : XUPItem( QDomElement(), 0 )


XUPProjectItem.~XUPProjectItem()


def setLastError(self, error ):
    setTemporaryValue( "lastError", error )


def lastError(self):
    return temporaryValue( "lastError" ).toString()


def fileName(self):
    return temporaryValue( "fileName" ).toString()


def path(self):
    return QFileInfo( fileName() ).path()


def filePath(self, fn ):
    if  fn.isEmpty() :
        return QString.null
    fname = QFileInfo( fn ).isRelative() ? path().append( "/" ).append( fn ) : fn
    return QDir.cleanPath( fname )


def relativeFilePath(self, fileName ):
    QDir dir( path() )
    return dir.relativeFilePath( fileName )


def sourceFiles(self):
    QStringList files

    # get variables that handle files
     fileVariables = mXUPProjectInfos.fileVariables( projectType() )

    # get all variable that represent files
    for variable in fileVariables:
         values = splitMultiLineValue( mVariableCache.value( variable ) )

        for value in values:
             file = filePath( value )
             QFileInfo fi( file )

            if  fi.isDir() :
                continue


            files << file


    
    # get dynamic files
    dynamicFolderItem = XUPProjectItemHelper.projectDynamicFolderItem( const_cast<XUPProjectItem*>( self ), False )
    
    if  dynamicFolderItem :
        for valueItem in dynamicFolderItem.childrenList():
            if  valueItem.type() == XUPItem.File :
                files << valueItem.attribute( "content" )




    return files


def topLevelProjectSourceFiles(self):
    QSet<QString> files

    projects = childrenProjects( True )

    for project in projects:
         sources = project.sourceFiles()

        for source in sources:
            files << source



    return files.toList()


def splitMultiLineValue(self, value ):
    tmpValues = value.split( " ", QString.SkipEmptyParts )
    inStr = False
    QStringList multivalues
    QString ajout

    for(ku = 0;ku < tmpValues.size();ku++)
        if tmpValues.value(ku).startsWith('"') :
                inStr = True
        if inStr:
            if ajout != "":
                    ajout += " "
            ajout += tmpValues.value(ku)
            if tmpValues.value(ku).endsWith('"') :
                    multivalues += ajout
                    ajout = ""
                    inStr = False


        else:
            multivalues += tmpValues.value(ku)



    return multivalues


def matchingPath(self, left, right ):
    QString result
    for ( i = 1; i < left.count() +1; i++ )
        result = left.left( i )
        if  not right.startsWith( result ) :
            result.chop( 1 )
            break



    if  QDir.drives().contains( result ) or result.isEmpty() :
        return QString.null


    return result


def compressedPaths(self, paths ):
    pathsList = paths
    QStringList result

    qSort( pathsList )
    for path in pathsList:
        if  result.isEmpty() :
            result << path

        else:
            matching = matchingPath( path, result.last() )
            if  matching.isEmpty() :
                result << path

            else:
                result.removeLast()
                result << matching




    return result


def findFile(self, partialFilePath ):
    riProject = rootIncludeProject()
     projectPath = path()
     variablesPath = mXUPProjectInfos.pathVariables( projectType() )
    QStringList paths

    # add project path and variables content based on path
    paths << projectPath
    for variable in variablesPath:
        tmpPaths = riProject.variableCache().value( variable )

        foreach ( QString path, splitMultiLineValue( tmpPaths ) )
            path = filePath( path.remove( '"' ) )
            if  not paths.contains( path ) and not path.startsWith( projectPath ) :
                paths << path




    # get compressed path list
    paths = compressedPaths( paths )

    #qWarning() << "looking in" << paths

    # get all matching files in paths
    QFileInfoList files
    QDir dir

    for path in paths:
        dir.setPath( path )
        files << pMonkeyStudio.getFiles( dir, QFileInfo( partialFilePath ).fileName(), True )


    return files


def projectInfos(self):
    return mXUPProjectInfos


QMap<QString, XUPProjectItem.variableCache()
    return mVariableCache


def parentProject(self):
    if  mParentItem :
        return mParentItem.project()
    return const_cast<XUPProjectItem*>( self )


def topLevelProject(self):
    if  mParentItem :
        return mParentItem.project().topLevelProject()
    return const_cast<XUPProjectItem*>( self )


def rootIncludeProject(self):
    if  mParentItem and mParentItem.type() == XUPItem.Function and mParentItem.attribute( "name" ).toLower() == "include" :
        return mParentItem.project().rootIncludeProject()
    return const_cast<XUPProjectItem*>( self )


def childrenProjects(self, recursive ):
    model = self.model()
    thisProject = project()
    QMap<QString, projects

    if  model :
         projectIndexes = model.match( thisProject.index(), XUPProjectModel.TypeRole, XUPItem.Project, -1, Qt.MatchExactly | Qt.MatchWrap | Qt.MatchRecursive )

        for index in projectIndexes:
            item = static_cast<XUPItem*>( index.internalPointer() )
            project = item.project()

            if  recursive or project.parentProject() == thisProject :
                projects[ project.fileName() ] = project




    return projects.values()


def iconFileName(self, item ):
    pType = projectType()
    QString fn

    if  item.type() == XUPItem.Variable :
        fn = mXUPProjectInfos.iconName( pType, item.attribute( "name" ) )


    if  fn.isEmpty() :
        fn = item.mDomElement.nodeName()


    if  not fn.isEmpty() :
        fn.append( ".png" )


    return fn


def iconsPath(self):
    return mXUPProjectInfos.iconsPath( projectType() )


def variableDisplayText(self, variableName ):
    return mXUPProjectInfos.displayText( projectType(), variableName )


def itemDisplayText(self, item ):
    QString text

    if  item.temporaryValue( "hasDisplayText", False ).toBool() :
        text = item.temporaryValue( "displayText" ).toString()

    else:
        item.setTemporaryValue( "hasDisplayText", True )
        switch ( item.type() )
            case XUPItem.Project:
                text = item.attribute( "name" )
                break
            case XUPItem.Comment:
                text = item.attribute( "value" )
                break
            case XUPItem.EmptyLine:
                text = tr( "%1 empty line(s)" ).arg( item.attribute( "count" ) )
                break
            case XUPItem.Variable:
                text = variableDisplayText( item.attribute( "name" ) )
                break
            case XUPItem.Value:
                text = item.attribute( "content" )
                break
            case XUPItem.Function:
                text = QString( "%1(%2)" ).arg( item.attribute( "name" ) ).arg( item.attribute( "parameters" ) )
                break
            case XUPItem.Scope:
                text = item.attribute( "name" )
                break
            case XUPItem.DynamicFolder:
                text = tr( "Dynamic Folder" )
                break
            case XUPItem.Folder:
                text = item.attribute( "name" )
                break
            case XUPItem.File:
                text = QFileInfo( item.attribute( "content" ) ).fileName()
                break
            case XUPItem.Path:
                text = item.attribute( "content" )
                break
            default:
                text = "#Unknow"
                break

        item.setTemporaryValue( "displayText", text )


    return text


def itemDisplayIcon(self, item ):
    QIcon icon

    if  item.temporaryValue( "hasDisplayIcon", False ).toBool() :
        icon = item.temporaryValue( "displayIcon" ).value<QIcon>()

    else:
        item.setTemporaryValue( "hasDisplayIcon", True )
        path = iconsPath()
        fn = pIconManager.filePath( iconFileName( item ), path )

        if  not QFile.exists( fn ) :
            path = mXUPProjectInfos.pixmapsPath( XUPProjectItem.XUPProject )


        icon = pIconManager.icon( iconFileName( item ), path )
        item.setTemporaryValue( "displayIcon", icon )


    return icon


def rebuildCache(self):
    riProject = rootIncludeProject()
    riProject.mVariableCache.clear()
    analyze( riProject )


def getVariables(self, root, variableName, callerItem, recursive ):
    mFoundCallerItem = False
    XUPItemList variables

    for ( i = 0; i < root.childCount(); i++ )
        item = root.child( i )

        switch ( item.type() )
            case XUPItem.Project:
                if  recursive :
                    pItem = item.parent()
                    if  pItem.type() == XUPItem.Function and pItem.attribute( "name" ).toLower() == "include" :
                        variables << getVariables( item, variableName, callerItem )


                break

            case XUPItem.Comment:
                break
            case XUPItem.EmptyLine:
                break
            case XUPItem.Variable:
                if  item.attribute( "name" ) == variableName :
                    variables << item

                break

            case XUPItem.Value:
                break
            case XUPItem.Function:
                if  recursive :
                    variables << getVariables( item, variableName, callerItem )

                break

            case XUPItem.Scope:
                if  recursive :
                    variables << getVariables( item, variableName, callerItem )

                break

            default:
                break


        if  callerItem and item == callerItem :
            mFoundCallerItem = True
            break


        if  mFoundCallerItem :
            break


    return variables


def toString(self):
    return XUPProjectItemHelper.stripDynamicFolderFiles( mDocument ).toString( 4 )


def projectSettingsScope(self, create ):
    project = topLevelProject()

    if  project :
         mScopeName = "XUPProjectSettings"
        items = project.childrenList()

        for child in items:
            if  child.type() == XUPItem.Scope and child.attribute( "name" ) == mScopeName :
                child.setAttribute( "nested", "False" )
                return child



        if  create :
            scope = project.addChild( XUPItem.Scope, 0 )
            scope.setAttribute( "name", mScopeName )
            scope.setAttribute( "nested", "False" )

            emptyline = project.addChild( XUPItem.EmptyLine, 1 )
            emptyline.setAttribute( "count", "1" )

            return scope



    return 0


def projectSettingsValues(self, variableName, defaultValues ):
    QStringList values
    project = topLevelProject()

    if  project :
        scope = projectSettingsScope( False )

        if  scope :
            variables = getVariables( scope, variableName, 0, False )

            for variable in variables:
                for child in variable.childrenList():
                    if  child.type() == XUPItem.Value :
                        values << child.attribute( "content" )






    if  values.isEmpty() :
        # a hack that allow xupproejct settings variable to be added to project node
        if  defaultValues.isEmpty() :
            values = QStringList( attribute( variableName.toLower() ) )

        else:
            values = defaultValues



    return values


QString XUPProjectItem.projectSettingsValue(  QString& variableName, defaultValue )  
     dvalue = defaultValue.isEmpty() ? QStringList() : QStringList( defaultValue )
    return projectSettingsValues(variableName, dvalue ).join( " " )


def setProjectSettingsValues(self, variableName, values ):
    project = topLevelProject()

    if  project :
        scope = projectSettingsScope( not values.isEmpty() )

        if  not scope :
            return


        variables = getVariables( scope, variableName, 0, False )
        variable = variables.value( 0 )
        haveVariable = variable

        if  not haveVariable and values.isEmpty() :
            return


        if  haveVariable and values.isEmpty() :
            scope.removeChild( variable )
            return


        if  not haveVariable :
            variable = scope.addChild( XUPItem.Variable )
            variable.setAttribute( "name", variableName )
            variable.setAttribute( "multiline", "True" )


        cleanValues = values
        for child in variable.childrenList():
            if  child.type() == XUPItem.Value :
                value = child.attribute( "content" )
                if  cleanValues.contains( value ) :
                    cleanValues.removeAll( value )

                elif  not cleanValues.contains( value ) :
                    variable.removeChild( child )




        for value in cleanValues:
            valueItem = variable.addChild( XUPItem.Value )
            valueItem.setAttribute( "content", value )




void XUPProjectItem.setProjectSettingsValue(  QString& variable, value ) 
    setProjectSettingsValues( variable, value.isEmpty() ? QStringList() : QStringList( value ) )


def addProjectSettingsValues(self, variableName, values ):
    project = topLevelProject()

    if  project :
        scope = projectSettingsScope( not values.isEmpty() )

        if  not scope :
            return


        variables = getVariables( scope, variableName, 0, False )
        variable = variables.value( 0 )
        haveVariable = variable

        if  not haveVariable and values.isEmpty() :
            return


        if  haveVariable and values.isEmpty() :
            return


        if  not haveVariable :
            variable = scope.addChild( XUPItem.Variable )
            variable.setAttribute( "name", variableName )
            variable.setAttribute( "multiline", "True" )


        cleanValues = values
        for child in variable.childrenList():
            if  child.type() == XUPItem.Value :
                value = child.attribute( "content" )
                if  cleanValues.contains( value ) :
                    cleanValues.removeAll( value )




        for value in cleanValues:
            valueItem = variable.addChild( XUPItem.Value )
            valueItem.setAttribute( "content", value )




def addProjectSettingsValue(self, variable, value ):
    addProjectSettingsValues( variable, value.isEmpty() ? QStringList() : QStringList( value ) )


def projectType(self):
    return XUPProjectItem.XUPProject


def targetTypeString(self, type ):
    switch ( type )
        case XUPProjectItem.DefaultTarget:
            return QLatin1String( "TARGET_DEFAULT" )
            break
        case XUPProjectItem.DebugTarget:
            return QLatin1String( "TARGET_DEBUG" )
            break
        case XUPProjectItem.ReleaseTarget:
            return QLatin1String( "TARGET_RELEASE" )
            break

    
    Q_ASSERT( 0 )
    return QString.null


def projectTargetType(self):
    return (XUPProjectItem.TargetType)projectSettingsValue( "TARGET_TYPE", QString.number( XUPProjectItem.DefaultTarget ) ).toInt()


def platformTypeString(self, type ):
    switch ( type )
        case XUPProjectItem.AnyPlatform:
            return QLatin1String( "ANY_PLATFORM" )
            break
        case XUPProjectItem.WindowsPlatform:
            return QLatin1String( "WINDOWS_PLATFORM" )
            break
        case XUPProjectItem.MacPlatform:
            return QLatin1String( "MAC_PLATFORM" )
            break
        case XUPProjectItem.OthersPlatform:
            return QLatin1String( "OTHERS_PLATFORM" )
            break

    
    Q_ASSERT( 0 )
    return QString.null


def registerProjectType(self):
    # get proejct type
    pType = projectType()

    # register it
    mXUPProjectInfos.unRegisterType( pType )
    mXUPProjectInfos.registerType( pType, const_cast<XUPProjectItem*>( self ) )

    # values
     mPixmapsPath = ":/items"
     mOperators = QStringList( "=" ) << "+=" << "-=" << "*="
     mFilteredVariables = QStringList( "FILES" )
     mFileVariables = QStringList( "FILES" )
     mSuffixes = StringStringListList()
        << qMakePair( tr( "XUP Project" ), QStringList( "*.xup" ) )
        << qMakePair( tr( "XUP Include Project" ), QStringList( "*.xui" ) )
     mVariableLabels = StringStringList()
        << qMakePair( QString( "FILES" ), tr( "Files" ) )
     mVariableIcons = StringStringList()
        << qMakePair( QString( "FILES" ), QString( "files" ) )
     mVariableSuffixes = StringStringListList()
        << qMakePair( QString( "FILES" ), QStringList( "*" ) )

    # register values
    mXUPProjectInfos.registerPixmapsPath( pType, mPixmapsPath )
    mXUPProjectInfos.registerOperators( pType, mOperators )
    mXUPProjectInfos.registerFilteredVariables( pType, mFilteredVariables )
    mXUPProjectInfos.registerFileVariables( pType, mFileVariables )
    mXUPProjectInfos.registerPathVariables( pType, mFileVariables )
    mXUPProjectInfos.registerSuffixes( pType, mSuffixes )
    mXUPProjectInfos.registerVariableLabels( pType, mVariableLabels )
    mXUPProjectInfos.registerVariableIcons( pType, mVariableIcons )
    mXUPProjectInfos.registerVariableSuffixes( pType, mVariableSuffixes )


def unRegisterProjectType(self):
    mXUPProjectInfos.unRegisterType( projectType() )


def getVariableContent(self, variableName ):
    name = QString( variableName ).replace( '$', "" ).replace( '{', "" ).replace( '}', "" ).replace( '[', "" ).replace( ']', "" ).replace( '(', "" ).replace( ')', "" )

    # environment var
    if  variableName.startsWith( "$$(" ) or variableName.startsWith( "$(" ) :
        if  name == "PWD" :
            return rootIncludeProject().path()

        else:
            return QString.fromLocal8Bit( qgetenv( name.toLocal8Bit().constData() ) )


    else:
        if  name == "PWD" :
            return project().path()

        else:
            return rootIncludeProject().variableCache().value( name )



    return QString.null


def interpretContent(self, content ):
    QRegExp rx( "\\$\\$?[\\{\\(\\[]?([\\w\\.]+(?not \\w*\\s*\\{\\[\\(\\)\\]\\}))[\\]\\)\\}]?" )
    value = content
    pos = 0

    while ( ( pos = rx.indexIn( content, pos ) ) != -1 )
        value.replace( rx.cap( 0 ), getVariableContent( rx.cap( 0 ) ) )
        pos += rx.matchedLength()


    return value


def handleIncludeFile(self, function ):
     parameters = function.cacheValue( "parameters" )
     fn = filePath( parameters )
    QStringList projects

    for cit in function.childrenList():
        if  cit.type() == XUPItem.Project :
            projects << cit.project().fileName()



    # check if project is already handled
    if  projects.contains( fn ) :
        return True


    # open project
    project = newProject()
    function.addChild( project )

    # remove and delete project if can't open
    if  not project.open( fn, temporaryValue( "codec" ).toString() ) :
        function.removeChild( project )
        topLevelProject().setLastError( tr( "Failed to handle include file %1" ).arg( fn ) )
        return False


    return True


def analyze(self, item ):
    QStringList values
    project = item.project()
    riProject = rootIncludeProject()

    for cItem in item.childrenList():
        switch ( cItem.type() )
            case XUPItem.Value:
            case XUPItem.File:
            case XUPItem.Path:
                content = interpretContent( cItem.attribute( "content" ) )

                if  cItem.type() != XUPItem.Value :
                    fn = project.filePath( content )

                    if  QFile.exists( fn ) :
                        fn = riProject.relativeFilePath( fn )


                    content = fn


                values << content

                cItem.setCacheValue( "content", content )
                break

            case XUPItem.Function:
                parameters = interpretContent( cItem.attribute( "parameters" ) )

                cItem.setCacheValue( "parameters", parameters )
                break

            case XUPItem.Project:
            case XUPItem.Comment:
            case XUPItem.EmptyLine:
            case XUPItem.Variable:
            case XUPItem.Scope:
            case XUPItem.DynamicFolder:
            case XUPItem.Folder:
            default:
                break


        if  not analyze( cItem ) :
            return False



    if  item.type() == XUPItem.Variable :
        name = item.attribute( "name" )
        op = item.attribute( "operator", "=" )

        if  op == "=" :
            riProject.variableCache()[ name ] = values.join( " " )

        elif  op == "-=" :
            for value in values:
                riProject.variableCache()[ name ].replace( QRegExp( QString( "\\b%1\\b" ).arg( value ) ), QString.null )


        elif  op == "+=" :
            riProject.variableCache()[ name ] += " " +values.join( " " )

        elif  op == "*=" :
            #if  not riProject.variableCache()[ name ].contains( content ) :
                riProject.variableCache()[ name ] += " " +values.join( " " )




    # handle include projects
    if  item.attribute( "name" ).toLower() == "include" :
        if  not handleIncludeFile( item ) :
            return False



    return True


def open(self, fileName, codec ):
    # get QFile
    QFile file( fileName )

    # check existence
    if  not file.exists() :
        topLevelProject().setLastError( "file not exists" )
        return False


    # try open it for reading
    if  not file.open( QIODevice.ReadOnly ) :
        topLevelProject().setLastError( "can't open file for reading" )
        return False


    # decode content
    c = QTextCodec.codecForName( codec.toUtf8() )
    buffer = c.toUnicode( file.readAll() )

    # parse content
    QString errorMsg
    int errorLine
    int errorColumn
    if  not mDocument.setContent( buffer, &errorMsg, &errorLine, &errorColumn ) :
        topLevelProject().setLastError( QString( "%1 on line: %2, column: %3" ).arg( errorMsg ).arg( errorLine ).arg( errorColumn ) )
        return False


    # check project validity
    mDomElement = mDocument.firstChildElement( "project" )
    if  mDomElement.isNull() :
        topLevelProject().setLastError( "no project node" )
        return False


    # all is ok
    setTemporaryValue( "codec", codec )
    setTemporaryValue( "fileName", fileName )
    topLevelProject().setLastError( QString.null )
    file.close()

    return analyze( self )


def save(self):
    # try open file for writing
    QFile file( temporaryValue( "fileName" ).toString() )

    if  not file.open( QIODevice.WriteOnly ) :
        return False


    # erase file content
    file.resize( 0 )

    # set xup version
    setAttribute( "version", XUP_VERSION )

    # encode content
    codec = QTextCodec.codecForName( temporaryValue( "codec" ).toString().toUtf8() )
    content = codec.fromUnicode( toString() )

    # write content
    result = file.write( content ) != -1
    file.close()

    # set error message if needed
    if  result :
        topLevelProject().setLastError( QString.null )

    else:
        topLevelProject().setLastError( tr( "Can't write content" ) )


    return result


def targetFilePath(self, allowToAskUser, targetType, platformType ):
    tlProject = topLevelProject()
     targetTypeString = self.targetTypeString( targetType )
     platformTypeString = self.platformTypeString( platformType )
     key = QString( "%1_%2" ).arg( platformTypeString ).arg( targetTypeString )
    target = tlProject.filePath( projectSettingsValue( key ) )
    QFileInfo targetInfo( target )
    
    if  not targetInfo.exists() or ( not targetInfo.isExecutable() and not QLibrary.isLibrary( target ) ) :
        if  allowToAskUser :
            QString type
            
            switch ( targetType )
                case XUPProjectItem.DebugTarget:
                    type = tr( "debug" ) +" "
                    break
                case XUPProjectItem.ReleaseTarget:
                    type = tr( "release" ) +" "
                    break
                default:
                    break

            
             userTarget = QFileDialog.getOpenFileName( MonkeyCore.mainWindow(), tr( "Point please project %1target" ).arg( type ), tlProject.path() )
            targetInfo.setFile( userTarget )
            
            if  not userTarget.isEmpty() :
                target = userTarget

            
            if  targetInfo.exists() :
                setProjectSettingsValue( key, tlProject.relativeFilePath( userTarget ) )
                save()



    
    return target


def targetFilePath(self, execution ):
    return targetFilePath( True, (XUPProjectItem.TargetType)execution.targetType, (XUPProjectItem.PlatformType)execution.platformType )


def builder(self, plugin ):
    return MonkeyCore.pluginsManager().plugin<BuilderPlugin*>( PluginsManager.stAll, projectSettingsValue( "BUILDER", plugin ) )


def debugger(self, plugin ):
    return MonkeyCore.pluginsManager().plugin<DebuggerPlugin*>( PluginsManager.stAll, projectSettingsValue( "DEBUGGER", plugin ) )


def interpreter(self, plugin ):
    return MonkeyCore.pluginsManager().plugin<InterpreterPlugin*>( PluginsManager.stAll, projectSettingsValue( "INTERPRETER", plugin ) )


def addCommand(self, cmd, mnu ):
    if  cmd.isValid() :
        cmd.setUserData( QVariant.fromValue( &mCommands ) )
        cmd.setProject( self )
        
        if  cmd.workingDirectory().isEmpty() :
            cmd.setWorkingDirectory( path() )

        
        installCommandRequested.emit( cmd, mnu )
        mCommands.insertMulti( mnu, cmd )



def installCommands(self):
    # get plugins
    bp = builder()
    #dp = debugger()
    ip = interpreter()

    emptyBuilderBuildMenu = MonkeyCore.menuBar().menu( "mBuilder/mBuild" ).actions().isEmpty()
    emptyInterpreterMenu = MonkeyCore.menuBar().menu( "mInterpreter" ).actions().isEmpty()

    # build command
    if  bp and emptyBuilderBuildMenu :
        cmd = bp.buildCommand()

        cmd.setSkipOnError( False )
        addCommand( cmd, "mBuilder/mBuild" )

        # clean
        cmd.setText( tr( "Clean" ) )
        cmd.setArguments( "clean" )
        addCommand( cmd, "mBuilder/mClean" )

        # distclean
        cmd.setText( tr( "Distclean" ) )
        cmd.setArguments( "distclean" )
        addCommand( cmd, "mBuilder/mClean" )

        # rebuild
        cmd.setText( tr( "Rebuild" ) )
        cmd.setCommand( ( QStringList() << tr( "Clean" ) << tr( "Build" ) ).join( ";" ) )
        cmd.setArguments( QString() )
        addCommand( cmd, "mBuilder/mRebuild" )

    
    # interprete file command
    if  ip and emptyInterpreterMenu :
        cmd = ip.interpretCommand()
        cmd.setSkipOnError( False )
        addCommand( cmd, "mInterpreter" )


    # install builder user command
    if  bp :
        for cmd in bp.userCommands():
            cmd.setSkipOnError( False )
            addCommand( cmd, "mBuilder/mUserCommands" )



    '''
    # install debugger user command
    if  dp :
        for cmd in dp.userCommands():
            cmd.setSkipOnError( False )
            addCommand( cmd, "mDebugger/mUserCommands" )


    '''
    # install interpreter user command
    if  ip :
        for cmd in ip.userCommands():
            cmd.setSkipOnError( False )
            addCommand( cmd, "mInterpreter/mUserCommands" )


    
    # install custom project commands
    XUPProjectItemHelper.installProjectCommands( self )


def uninstallCommands(self):
    for cmd in mCommands.values():
        uninstallCommandRequested.emit( cmd, mCommands.key( cmd ) )
    mCommands.clear()


def directoryChanged(self, path ):
    XUPProjectItemHelper.updateDynamicFolder( self, path )

