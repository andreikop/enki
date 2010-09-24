#include "VariablesEditor.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "xupmanager/core/XUPProjectItemHelper.h"
#include "pMonkeyStudio.h"

#include <QMenu>
#include <QInputDialog>
#include <QMessageBox>
#include <QFileDialog>

VariablesEditor.VariablesEditor( QWidget* parent )
        : QFrame( parent )
    mProject = 0

    setupUi( self )

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


VariablesEditor.~VariablesEditor()


def init(self, project ):
    mProject = project

    pType = mProject.projectType()
    mFileVariables = mProject.projectInfos().fileVariables( pType )
    mPathVariables = mProject.projectInfos().pathVariables( pType )
    mManagedVariables << mFileVariables << XUPProjectItemHelper.DynamicFolderName << XUPProjectItemHelper.DynamicFolderSettingsName

    # loading datas from variable of root scope having operator =, += or *= only
    for child in mProject.childrenList():
        if  child.type() == XUPItem.Variable :
            variableName = child.attribute( "name" )
            op = child.attribute( "operator", "=" )

            if  op != "=" and op != "+=" and op != "*=" :
                continue


            if ( variableName == XUPProjectItemHelper.DynamicFolderSettingsName or
                    variableName == XUPProjectItemHelper.DynamicFolderName )
                continue


            for value in child.childrenList():
                type = value.type()
                QString val

                if  type != XUPItem.Value and type != XUPItem.File and type != XUPItem.Path :
                    continue


                val += mValues[ variableName ].trimmed()
                val += " " +value.attribute( "content" )
                mValues[ variableName ] = val.trimmed()




    updateValuesEditorVariables()


def finalize(self):
    curItem = lwOthersVariables.currentItem()
    on_lwOthersVariables_currentItemChanged( curItem, curItem )

    # tell about variables to remove
    for variable in mVariablesToRemove:
        mValues[ variable ] = QString.null


    # update project
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
                variableItem.setAttribute( "operator", "=" )
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
     values = XUPProjectItem.splitMultiLineValue( mValues[ variable ] )

    lwOthersValues.clear()
    lwOthersValues.addItems( values )


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
            QMessageBox.information( QApplication.activeWindow(), tr( "Information..." ), tr( "This variable already exists or is filtered out." ) )




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



