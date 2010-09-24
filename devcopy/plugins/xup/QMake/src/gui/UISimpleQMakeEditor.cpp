#include "UISimpleQMakeEditor.h"
#include <xupmanager/core/XUPProjectItem.h>
#include "QMake.h"

#include <shared/MkSFileDialog.h>
#include <pMonkeyStudio.h>
#include <coremanager/MonkeyCore.h>
#include <pluginsmanager/PluginsManager.h>

#include <QInputDialog>
#include <QMessageBox>
#include <QMenu>
#include <QDebug>

UISimpleQMakeEditor.UISimpleQMakeEditor( XUPProjectItem* project, parent )
        : QDialog( parent )
    # init dialog
    setupUi( self )

    # set dialog infos
    setWindowIcon( project.displayIcon() )
    setWindowTitle( windowTitle().append( " - " ).append( project.displayText() ) )

    # set size hint for page item ( left panel )
    for ( i = 0; i < lwPages.count(); i++ )
        item = lwPages.item( i )
        item.setSizeHint( QSize( 154, 40 ) )


    # values editor actions
    # tbOthersValuesAdd actions
    addMenu = QMenu( tbOthersValuesAdd )
    aOthersValuesAddValue = addMenu.addAction( tr( "As Value..." ) )
    aOthersValuesAddFile = addMenu.addAction( tr( "As File..." ) )
    aOthersValuesAddPath = addMenu.addAction( tr( "As Path..." ) )
    tbOthersValuesAdd.setMenu( addMenu )

    # tbOthersValuesEdit actions
    editMenu = QMenu( tbOthersValuesEdit )
    aOthersValuesEditValue = editMenu.addAction( tr( "As Value..." ) )
    aOthersValuesEditFile = editMenu.addAction( tr( "As File..." ) )
    aOthersValuesEditPath = editMenu.addAction( tr( "As Path..." ) )
    tbOthersValuesEdit.setMenu( editMenu )

    # connections
    lwQtModules.itemSelectionChanged.connect(self.modules_itemSelectionChanged)
    lwModules.itemSelectionChanged.connect(self.modules_itemSelectionChanged)
    foreach ( QRadioButton* rb, gbProjectType.findChildren<QRadioButton*>() )
        rb.toggled.connect(self.projectTypeChanged)


    # init proejct settings dialog
    init( project )

    # set correct page
    lwPages.setCurrentRow( 1 )


UISimpleQMakeEditor.~UISimpleQMakeEditor()


def updateProjectFiles(self):
    pType = mProject.projectType()
    for variable in mFileVariables:
        topItem = mProjectFilesItems.value( variable )
        files = mProject.splitMultiLineValue( mValues[ variable ] )
        if  topItem and files.isEmpty() :
            delete mProjectFilesItems.take( variable )

        elif  not files.isEmpty() :
            if  not topItem :
                topItem = QTreeWidgetItem( twFiles, QTreeWidgetItem.UserType +1 )
                topItem.setText( 0, mProject.projectInfos().displayText( pType, variable ) )
                topItem.setIcon( 0, mProject.projectInfos().displayIcon( pType, variable ) )
                mProjectFilesItems[ variable ] = topItem


            for ( i = 0; i < topItem.childCount(); i++ )
                item = topItem.child( i )
                fn = item.data( 0, Qt.UserRole ).toString()
                if  files.contains( fn ) :
                    files.removeAll( fn )



            for fn in files:
                item = QTreeWidgetItem( topItem, QTreeWidgetItem.UserType )
                item.setText( 0, fn )
                item.setData( 0, Qt.UserRole, fn )
                item.setIcon( 0, mProject.projectInfos().displayIcon( XUPProjectItem.XUPProject, "FILES" ) )





def updateValuesEditorVariables(self):
    curItem = lwOthersVariables.selectedItems().value( 0 )
     curVariable = curItem ? curItem.text() : QString.null
    curItem = 0

    lwOthersVariables.clear()
    lwOthersValues.clear()

    for variable in mValues.keys():
        if  not mManagedVariables.contains( variable ) :
            lwOthersVariables.addItem( variable )

            if  variable == curVariable :
                curItem = lwOthersVariables.item( lwOthersVariables.count() -1 )
                curItem.setSelected( True )





def updateValuesEditorValues(self, variable ):
     values = mProject.splitMultiLineValue( mValues[ variable ] )

    lwOthersValues.clear()
    lwOthersValues.addItems( values )


def init(self, project ):
    mConfigGui.clear()
    mFileVariables = project.projectInfos().fileVariables( project.projectType() )
    mPathVariables = project.projectInfos().pathVariables( project.projectType() )
    QString value
    QStringList config
    QStringList values
    mProject = project
    mValues.clear()
    mManagedVariables.clear()
    mManagedVariables << "TEMPLATE" << "CONFIG" << "TARGET" << "DESTDIR" << "DLLDESTDIR" << "QT" << mFileVariables

    foreach ( QAbstractButton* ab, wCompilerSettings.findChildren<QAbstractButton*>() )
        if  not ab.statusTip().isEmpty() :
            mConfigGui << ab.statusTip()



    mConfigGui << "app_bundle" << "lib_bundle" << "embed_manifest_exe" << "embed_manifest_dll"
    '''<< "designer"''' << "plugin" << "shared" << "dll" << "static" << "staticlib"

    manager = QMake.versionManager()
    lwQtVersion.clear()
    lwQtModules.clear()
    lwModules.clear()

    mQtVersion = manager.version( mProject.projectSettingsValue( "QT_VERSION" ) )

    # qt versions
    for qv in manager.versions():
        it = QListWidgetItem( qv.Version, lwQtVersion )
        it.setData( Qt.UserRole, QVariant.fromValue( qv ) )

        if  qv.Default :
            it.setBackground( QBrush( Qt.green ) )

        if  qv == mQtVersion :
            it.setSelected( True )


    # qt modules
    for mi in manager.modules():
        it = QListWidgetItem( mi.Text, lwQtModules )
        it.setData( Qt.UserRole, QVariant.fromValue( mi ) )


    # configuration
    for ci in manager.configurations():
        if  not mConfigGui.contains( ci.Value, Qt.CaseInsensitive ) :
            if  ci.Text.toLower() != "lib only" and ci.Text.toLower() != "x11 only" and ci.Text.toLower() != "mac os x only" :
                it = QListWidgetItem( ci.Text, lwModules )
                it.setData( Qt.UserRole, QVariant.fromValue( ci ) )

                if  ci.Value.isEmpty() and ci.Variable.isEmpty() :
                    QFont font( it.font() )
                    font.setBold( True )
                    it.setFont( font )
                    it.setBackground( QBrush( QColor( Qt.darkBlue ) ) )
                    it.setForeground( QBrush( QColor( Qt.white ) ) )
                    it.setTextAlignment( Qt.AlignCenter )
                    it.setFlags( it.flags() ^ Qt.ItemIsUserCheckable )

                else:
                    it.setCheckState( Qt.Unchecked )




    # loading datas from variable of root scope having operator =, += or *= only
    for child in mProject.childrenList():
        if  child.type() == XUPItem.Variable :
            variableName = child.attribute( "name" )
            op = child.attribute( "operator", "=" )

            if  op != "=" and op != "+=" and op != "*=" :
                continue


            for value in child.childrenList():
                type = value.type()
                QString val

                if  type != XUPItem.Value and type != XUPItem.File and type != XUPItem.Path :
                    continue


                if  not mValues.keys().contains( "QT" ) and variableName == "QT" and ( op == "+=" or op == "*=" ) :
                    val += "core gui "


                val += mValues[ variableName ].trimmed()
                val += " " +value.attribute( "content" )
                mValues[ variableName ] = val.trimmed()




    # update gui
    config = project.splitMultiLineValue( mValues[ "CONFIG" ] )

    # project
    value = mValues[ "TEMPLATE" ]
    if  value == "app" :
        rbApplication.setChecked( True )

    elif  value == "subdirs" :
        rbSubdirs.setChecked( True )

    elif  value == "lib" :
        if  config.contains( "designer" ) :
            rbQtDesignerPlugin.setChecked( True )
            config.removeAll( "designer" )

        elif  config.contains( "plugin" ) :
            rbQtPlugin.setChecked( True )
            config.removeAll( "plugin" )

        elif  config.contains( "shared" ) or config.contains( "dll" ) :
            rbSharedLib.setChecked( True )
            config.removeAll( "shared" )
            config.removeAll( "dll" )

        elif  config.contains( "static" ) or config.contains( "staticlib" ) :
            rbStaticLib.setChecked( True )
            config.removeAll( "static" )
            config.removeAll( "staticlib" )



    if  not rbSubdirs.isChecked() :
        leProjectName.setText( mValues[ "TARGET" ] )
        if  rbApplication.isChecked() or rbStaticLib.isChecked() :
            leProjectTarget.setText( mValues[ "DESTDIR" ] )

        else:
            leProjectTarget.setText( mValues[ "DLLDESTDIR" ] )



    # modules
    values = project.splitMultiLineValue( mValues[ "QT" ] )
    for ( i = 0; i < lwQtModules.count(); i++ )
        item = lwQtModules.item( i )
        mi = item.data( Qt.UserRole ).value<QtItem>()

        if  values.contains( mi.Value ) :
            item.setCheckState( Qt.Checked )

        else:
            item.setCheckState( Qt.Unchecked )



    for ( i = 0; i < lwModules.count(); i++ )
        item = lwModules.item( i )
        ci = item.data( Qt.UserRole ).value<QtItem>()

        if  config.contains( ci.Value ) :
            item.setCheckState( Qt.Checked )
            config.removeAll( ci.Value )

        elif  not ci.Value.isEmpty() :
            item.setCheckState( Qt.Unchecked )



    # compiler settings
    foreach ( QAbstractButton* ab, wCompilerSettings.findChildren<QAbstractButton*>() )
        if  not ab.statusTip().isEmpty() :
            if  ab == cbBuildAll :
                ab.setChecked( config.contains( ab.statusTip() ) and config.contains( "debug_and_release" ) )
                config.removeAll( "debug_and_release" )

            else:
                ab.setChecked( config.contains( ab.statusTip() ) )


        elif  ab == cbBundle :
            ab.setChecked( config.contains( "app_bundle" ) or config.contains( "lib_bundle" ) )
            config.removeAll( "app_bundle" )
            config.removeAll( "lib_bundle" )

        elif  ab == cbManifest :
            ab.setChecked( config.contains( "embed_manifest_exe" ) or config.contains( "embed_manifest_dll" ) )
            config.removeAll( "embed_manifest_exe" )
            config.removeAll( "embed_manifest_dll" )


        config.removeAll( ab.statusTip() )


    # custom configuration
    leCustomConfig.setText( config.join( " " ) )

    updateProjectFiles()
    updateValuesEditorVariables()


def getUniqueVariableItem(self, variableName, create ):
     mOperators = QStringList() << "=" << "+=" << "*="
    variables = mProject.getVariables( mProject, variableName, 0, False )
    variableItem = 0

    # remove duplicate variables
    for variable in variables:
        op = variable.attribute( "operator", "=" )

        if  not variableItem and mOperators.contains( op ) :
            variableItem = variable

        elif  mOperators.contains( op ) :
            variable.parent().removeChild( variable )



    # create it if needed
    if  not variableItem and create :
        variableItem = mProject.addChild( XUPItem.Variable )
        variableItem.setAttribute( "name", variableName )


    # return item
    return variableItem


def projectTypeChanged(self):
    isSubdirs = rbSubdirs.isChecked()
    leProjectName.setDisabled( isSubdirs )
    leProjectTarget.setDisabled( isSubdirs )
    tbProjectTarget.setDisabled( isSubdirs )


def on_tbProjectTarget_clicked(self):
    path = leProjectTarget.text().isEmpty() ? mProject.path() : mProject.filePath( leProjectTarget.text() )
    path = QFileDialog.getExistingDirectory( self, tr( "Choose a target path for your project" ), path )

    if  not path.isEmpty() :
        leProjectTarget.setText( mProject.relativeFilePath( path ) )



def modules_itemSelectionChanged(self):
    lw = qobject_cast<QListWidget*>( sender() )
    it = lw ? lw.selectedItems().value( 0 ) : 0

    teModuleHelp.clear()

    if  it :
        teModuleHelp.setHtml( it.data( Qt.UserRole ).value<QtItem>().Help )



def on_tbAddFile_clicked(self):
    result = MkSFileDialog.getProjectAddFiles( window(), False )

    if  not result.isEmpty() :
        files = result[ "filenames" ].toStringList()

        # import files if needed
        if  result[ "import" ].toBool() :
             projectPath = mProject.path()
             importPath = result[ "importpath" ].toString()
             importRootPath = result[ "directory" ].toString()
            QDir dir( importRootPath )

            for ( i = 0; i < files.count(); i++ )
                if  not files.at( i ).startsWith( projectPath ) :
                    fn = QString( files.at( i ) ).remove( importRootPath ).replace( "\\", "/" )
                    fn = QDir.cleanPath( QString( "%1/%2/%3" ).arg( projectPath ).arg( importPath ).arg( fn ) )

                    if  dir.mkpath( QFileInfo( fn ).absolutePath() ) and QFile.copy( files.at( i ), fn ) :
                        files[ i ] = fn





        # add files
        for fn in files:
            fn = mProject.relativeFilePath( fn )

            if  fn.contains( " " ) :
                fn.prepend( '"' ).append( '"' )


            variable = mProject.projectInfos().variableNameForFileName( mProject.projectType(), fn )

            if  not mValues[ variable ].contains( fn ) :
                mValues[ variable ] += " " +fn



        updateProjectFiles()



def on_tbEditFile_clicked(self):
    item = twFiles.selectedItems().value( 0 )
    if  item and twFiles.indexOfTopLevelItem( item ) == -1 :
        bool ok
        oldValue = item.data( 0, Qt.UserRole ).toString()
        fn = QInputDialog.getText( self, tr( "Edit file name" ), tr( "Type a name for self file" ), QLineEdit.Normal, oldValue, &ok )
        if  ok and not fn.isEmpty() :
            variable = mProject.projectInfos().variableNameForFileName( mProject.projectType(), fn )

            item.setText( 0, fn )
            item.setData( 0, Qt.UserRole, fn )

            mValues[ variable ].remove( oldValue ).append( " " +fn )

            updateProjectFiles()




def on_tbRemoveFile_clicked(self):
    QList<QTreeWidgetItem*> selectedItems = twFiles.selectedItems()

    if  selectedItems.count() > 0 :
        if  QMessageBox.question( self, tr( "Remove files" ), tr( "Are you sure you want to remove all the selected files ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.No :
            return


        for item in selectedItems:
            if  item.type() == QTreeWidgetItem.UserType +1 :
                continue


             variable = mProjectFilesItems.key( item.parent() )
             fn = item.data( 0, Qt.UserRole ).toString()

            mValues[ variable ].remove( fn )
            delete item


        if  not selectedItems.isEmpty() :
            updateProjectFiles()




def on_lwOthersVariables_currentItemChanged(self, current, previous ):
    # enable/disable actions
    gbOthersValues.setEnabled( current )
    tbOthersVariablesEdit.setEnabled( current )
    tbOthersVariablesRemove.setEnabled( current )

    # save previous variable datas
    if  previous :
         variable = previous.text()
        QStringList values

        for ( i = 0; i < lwOthersValues.count(); i++ )
            values << lwOthersValues.item( i ).text()


        mValues[ variable ] = values.join( " " )


    # update values view
     variable = current ? current.text() : QString.null
    updateValuesEditorValues( variable )


def on_tbOthersVariablesAdd_clicked(self):
    bool ok
     variables = mProject.projectInfos().knowVariables( mProject.projectType() )
     variable = QInputDialog.getItem( window(), tr( "Add variable..." ), tr( "Select a variable name or enter a one" ), variables, 0, True, &ok )

    if  not variable.isEmpty() and ok :
        if  not mValues.keys().contains( variable ) and not mManagedVariables.contains( variable ) :
            item = QListWidgetItem( variable, lwOthersVariables )
            lwOthersVariables.setCurrentItem( item )

            mValues[ variable ] = QString.null
            mVariablesToRemove.removeAll( variable )

        else:
            QMessageBox.information( window(), tr( "Information..." ), tr( "This variable already exists or is filtered out." ) )




def on_tbOthersVariablesEdit_clicked(self):
    item = lwOthersVariables.currentItem()

    if  not item :
        return


    bool ok
    oldVariable = item.text()
    variable = QInputDialog.getText( window(), tr( "Edit variable..." ), tr( "Enter a name for self variable" ), QLineEdit.Normal, oldVariable, &ok )

    if  not variable.isEmpty() and ok :
        if  not mValues.keys().contains( variable ) and not mManagedVariables.contains( variable ) :
            item.setText( variable )

            mValues.remove( oldVariable )
            if  not mVariablesToRemove.contains( oldVariable ) :
                mVariablesToRemove << oldVariable


        else:
            QMessageBox.information( window(), tr( "Information..." ), tr( "This variable already exists or is filtered out." ) )




def on_tbOthersVariablesRemove_clicked(self):
    item = lwOthersVariables.currentItem()

    if  not item :
        return


    # confirm user request
    if  QMessageBox.question( QApplication.activeWindow(), tr( "Remove a variable..." ), tr( "A you sure you want to remove self variable and all its content ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.Yes :
        variable = item.text()

        lwOthersValues.clear()
        delete item

        mValues.remove( variable )
        if  not mVariablesToRemove.contains( variable ) :
            mVariablesToRemove << variable




def on_lwOthersValues_currentItemChanged(self, current, previous ):
    # enable button according to item validity
    tbOthersValuesEdit.setEnabled( current )
    tbOthersValuesRemove.setEnabled( current )
    Q_UNUSED( previous )


def on_tbOthersValuesAdd_clicked(self):
    on_tbOthersValuesAdd_triggered( aOthersValuesAddValue )


def on_tbOthersValuesAdd_triggered(self, action ):
    variableItem = lwOthersVariables.currentItem()

    if  variableItem :
         title = tr( "Add a value..." )
        ok = True
        QString val

        if  action == aOthersValuesAddValue :
            val    = QInputDialog.getText( window(), title, tr( "Enter the value :" ), QLineEdit.Normal, QString(), &ok )
            if  not ok :
                val.clear()


        elif  action == aOthersValuesAddFile :
            val = QFileDialog.getOpenFileName( window(), tr( "Choose a file" ), mProject.path() )
            if  not val.isEmpty() :
                val = mProject.relativeFilePath( val )


        elif  action == aOthersValuesAddPath :
            val = QFileDialog.getExistingDirectory( window(), tr( "Choose a path" ), mProject.path() )
            if  not val.isEmpty() :
                val = mProject.relativeFilePath( val )



        if  not val.isEmpty() :
            # quote value if needed
            if  val.contains( " " ) and not val.startsWith( '"' ) and not val.endsWith( '"' ) :
                val.prepend( '"' ).append( '"' )


            # check if value exists
            for ( i = 0; i < lwOthersValues.count(); i++ )
                valueItem = lwOthersValues.item( i )

                if  valueItem.text() == val :
                    lwOthersValues.setCurrentItem( valueItem )
                    return



            # create value item
            valueItem = QListWidgetItem( val, lwOthersValues )
            lwOthersValues.setCurrentItem( valueItem )




def on_tbOthersValuesEdit_clicked(self):
    on_tbOthersValuesEdit_triggered( aOthersValuesEditValue )


def on_tbOthersValuesEdit_triggered(self, action ):
    valueItem = lwOthersValues.currentItem()

    if  valueItem :
         title = tr( "Edit a value..." )
        ok = True
        oldValue = valueItem.text()
        QString val

        if  action == aOthersValuesEditValue :
            val    = QInputDialog.getText( window(), title, tr( "Edit the value :" ), QLineEdit.Normal, oldValue, &ok )
            if  not ok :
                val.clear()


        elif  action == aOthersValuesEditFile :
            val = QFileDialog.getOpenFileName( window(), tr( "Choose a file" ), oldValue )
            if  not val.isEmpty() :
                val = mProject.relativeFilePath( val )


        elif  action == aOthersValuesEditPath :
            val = QFileDialog.getExistingDirectory( window(), tr( "Choose a path" ), oldValue )
            if  not val.isEmpty() :
                val = mProject.relativeFilePath( val )



        if  not val.isEmpty() :
            # quote value if needed
            if  val.contains( " " ) and not val.startsWith( '"' ) and not val.endsWith( '"' ) :
                val.prepend( '"' ).append( '"' )


            # check if value exists
            for ( i = 0; i < lwOthersValues.count(); i++ )
                item = lwOthersValues.item( i )

                if  item.text() == val :
                    lwOthersValues.setCurrentItem( item )
                    return



            # update item
            valueItem.setText( val )




def on_tbOthersValuesRemove_clicked(self):
    valueItem = lwOthersValues.currentItem()

    if  valueItem :
        # confirm user request
        if  QMessageBox.question( QApplication.activeWindow(), tr( "Remove a value..." ), tr( "A you sure you want to remove self value ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.No :
            return


        # remove value
        delete valueItem



def on_tbOthersValuesClear_clicked(self):
    variableItem = lwOthersVariables.currentItem()

    if  variableItem :
        # request user confirm
        if  QMessageBox.question( QApplication.activeWindow(), tr( "Clear values..." ), tr( "A you sure you want to clear these values ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.Yes :
            lwOthersValues.clear()




def accept(self):
    QString plugin
    QString tmplate
    QStringList config
    QStringList qt
    QStringList target
    QString destdir
    QString dlldestdir

    # project
    if  rbApplication.isChecked() :
        tmplate = "app"

    elif  rbSubdirs.isChecked() :
        tmplate = "subdirs"

    else:
        tmplate = "lib"
        if  rbQtDesignerPlugin.isChecked() :
            config << "designer"

        elif  rbQtPlugin.isChecked() :
            config << "plugin"

        elif  rbSharedLib.isChecked() :
            config << "dll"

        elif  rbStaticLib.isChecked() :
            config << "staticlib"



    if  not rbSubdirs.isChecked() :
        target << leProjectName.text()
        if  rbApplication.isChecked() or rbStaticLib.isChecked() :
            destdir = leProjectTarget.text()

        else:
            dlldestdir = leProjectTarget.text()



    # modules
    for ( i = 0; i < lwQtModules.count(); i++ )
        item = lwQtModules.item( i )
        if  item.checkState() == Qt.Checked :
            qt << item.data( Qt.UserRole ).value<QtItem>().Value



    for ( i = 0; i < lwModules.count(); i++ )
        item = lwModules.item( i )
        if  item.checkState() == Qt.Checked :
            config << item.data( Qt.UserRole ).value<QtItem>().Value



    # compiler settings
    foreach ( QAbstractButton* ab, wCompilerSettings.findChildren<QAbstractButton*>() )
        if  not ab.isChecked() or not ab.isEnabled() :
            continue


        if  not ab.statusTip().isEmpty() :
            config << ab.statusTip()

        else:
            if  ab == cbManifest :
                if  tmplate == "app" :
                    config << "embed_manifest_exe"

                elif  tmplate == "lib" :
                    config << "embed_manifest_dll"


            elif  ab == cbBundle :
                if  tmplate == "app" :
                    config << "app_bundle"

                elif  tmplate == "lib" :
                    config << "lib_bundle"





    # save current variable if needed
    curItem = lwOthersVariables.currentItem()
    on_lwOthersVariables_currentItemChanged( curItem, curItem )

    # custom configuration
    config << mProject.splitMultiLineValue( leCustomConfig.text() )

    mValues[ "TEMPLATE" ] = tmplate
    mValues[ "CONFIG" ] = config.join( " " )
    mValues[ "QT" ] = qt.join( " " )
    mValues[ "TARGET" ] = target.join( " " )
    mValues[ "DESTDIR" ] = destdir
    mValues[ "DLLDESTDIR" ] = dlldestdir

    # tell about variables to remove
    for variable in mVariablesToRemove:
        mValues[ variable ] = QString.null


    for variable in mValues.keys():
        isEmpty = mValues[ variable ].trimmed().isEmpty()
        variableItem = getUniqueVariableItem( variable, isEmpty )
        if  not variableItem :
            continue


        if  not isEmpty :
            if  mFileVariables.contains( variable ) or mPathVariables.contains( variable ) :
                # get child type
                type = mFileVariables.contains( variable ) ? XUPItem.File : XUPItem.Path
                # get values
                values = mProject.splitMultiLineValue( mValues[ variable ] )

                # update variable
                variableItem.setAttribute( "operator", "+=" )
                variableItem.setAttribute( "multiline", "True" )

                # remove all child
                for child in variableItem.childrenList():
                    if  child.type() == type :
                        value = child.attribute( "content" )
                        if  values.contains( value ) :
                            values.removeAll( value )

                        elif  not values.contains( value ) :
                            variableItem.removeChild( child )




                # add ones
                for v in values:
                    value = variableItem.addChild( type )
                    value.setAttribute( "content", v )


            elif  variable == "CONFIG" :
                # update variable
                variableItem.setAttribute( "operator", "+=" )
                variableItem.setAttribute( "multiline", "False" )

                # remove all child values
                for child in variableItem.childrenList():
                    if  child.type() == XUPItem.Value :
                        variableItem.removeChild( child )



                # add one
                value = variableItem.addChild( XUPItem.Value )
                value.setAttribute( "content", mValues[ variable ] )

            else:
                # update variable
                variableItem.setAttribute( "operator", "=" )
                variableItem.setAttribute( "multiline", "False" )

                # remove all child values
                for child in variableItem.childrenList():
                    if  child.type() == XUPItem.Value :
                        variableItem.removeChild( child )



                # add one
                value = variableItem.addChild( XUPItem.Value )
                value.setAttribute( "content", mValues[ variable ] )


        elif  isEmpty and variableItem and variableItem.childCount() > 0 :
            # remove all child values
            for child in variableItem.childrenList():
                if  child.type() == XUPItem.Value or child.type() == XUPItem.File or child.type() == XUPItem.Path :
                    variableItem.removeChild( child )




        # remove empty variable
        if  variableItem.childCount() == 0 :
            variableItem.parent().removeChild( variableItem )



    # xup settings
    mQtVersion = QtVersion()
    qtVersionItem = lwQtVersion.selectedItems().value( 0 )

    if  qtVersionItem :
        mQtVersion = qtVersionItem.data( Qt.UserRole ).value<QtVersion>()


    mProject.setProjectSettingsValue( "QT_VERSION", mQtVersion.Version )

    # close dialog
    QDialog.accept()

