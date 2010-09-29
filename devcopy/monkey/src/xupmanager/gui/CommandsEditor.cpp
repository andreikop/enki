#include "CommandsEditor.h"

#include <QDebug>

CommandsEditor.CommandsEditor( QWidget* parent )
    : QFrame( parent )
    mLastCommandType = BasePlugin.iAll
    setupUi( self )
    updateGui()


CommandsEditor.~CommandsEditor()


def finalize(self):
    # save current command, global commands
    on_cbCommandTypes_currentIndexChanged( cbCommandTypes.currentIndex() )


def setCommandTypes(self, types ):
    mCommandTypes = types
    cbCommandTypes.clear()
    
    foreach (  BasePlugin.Type& type, types )
        cbCommandTypes.addItem( BasePlugin.typeToString( type ), type )

    
    cbCommandTypes.setCurrentIndex( -1 )


def commandTypes(self):
    return mCommandTypes


def setCommands(self, commands ):
    mCommands = commands


def commands(self):
    return mCommands


def setCurrentType(self, type ):
     index = cbCommandTypes.findData( type )
    cbCommandTypes.setCurrentIndex( index )


def currentType(self):
     index = cbCommandTypes.currentIndex()
    return (BasePlugin.Type)cbCommandTypes.itemData( index ).toInt()


def setParsers(self, parsers ):
    mParsers = parsers
    
    lwCommandParsers.clear()
    
    for parser in parsers:
        item = QListWidgetItem( parser, lwCommandParsers )
        item.setCheckState( Qt.Unchecked )



def parsers(self):
    return mParsers


def updateGui(self):
    item = lwCommands.currentItem()
     index = lwCommands.row( item )
     count = lwCommands.count()
    
    if  item :
         command = item.data( Qt.UserRole ).value<pCommand>()
         QSet<QString> parsers = command.parsers().toSet()
        
        leCommandText.setText( command.text() )
        leCommandCommand.setText( command.command() )
        leCommandArguments.setText( command.arguments() )
        leCommandWorkingDirectory.setText( command.workingDirectory() )
        cbCommandSkipOnError.setChecked( command.skipOnError() )
        cbCommandTryAll.setChecked( command.tryAllParsers() )
        
        for ( i = 0; i < lwCommandParsers.count(); i++ )
            item = lwCommandParsers.item( i )
            
            if  parsers.contains( item.text() ) :
                item.setCheckState( Qt.Checked )

            else:
                item.setCheckState( Qt.Unchecked )



    else:
        leCommandText.clear()
        leCommandCommand.clear()
        leCommandArguments.clear()
        leCommandWorkingDirectory.clear()
        cbCommandSkipOnError.setChecked( False )
        cbCommandTryAll.setChecked( False )
        
        for ( i = 0; i < lwCommandParsers.count(); i++ )
            item = lwCommandParsers.item( i )
            item.setCheckState( Qt.Unchecked )


    
    tbCommandRemove.setEnabled( item )
    tbCommandUp.setEnabled( item and index > 0 )
    tbCommandDown.setEnabled( item and count > 1 and index < count -1 )
    gbEditor.setEnabled( item )


def on_cbCommandTypes_currentIndexChanged(self, index ):
    Q_UNUSED( index )
    current = lwCommands.currentItem()
    
    on_lwCommands_currentItemChanged( current, current )
    
    if  mCommandTypes.contains( mLastCommandType ) :
        pCommandList commands
        
        for ( i = 0; i < lwCommands.count(); i++ )
             item = lwCommands.item( i )
             command = item.data( Qt.UserRole ).value<pCommand>()
            
            commands << command

        
        mCommands[ mLastCommandType ] = commands

    
    mLastCommandType = currentType()
     locked = lwCommands.blockSignals( True )
    lwCommands.clear()
    
    foreach (  pCommand& command, mCommands.value( mLastCommandType ) )
        item = QListWidgetItem( command.text(), lwCommands )
        item.setData( Qt.UserRole, QVariant.fromValue( command ) )

    
    lwCommands.blockSignals( locked )
    
    updateGui()


def on_tbCommandAdd_clicked(self):
    item = QListWidgetItem( tr( "" ), lwCommands )
    lwCommands.setCurrentItem( item )


def on_tbCommandRemove_clicked(self):
    delete lwCommands.currentItem()
    updateGui()


def on_tbCommandUp_clicked(self):
    if  it = lwCommands.currentItem() :
        i = lwCommands.row( it )
        if  i != 0 :
            lwCommands.insertItem( i -1, lwCommands.takeItem( i ) )
        lwCommands.setCurrentItem( it )



def on_tbCommandDown_clicked(self):
    if  it = lwCommands.currentItem() :
        i = lwCommands.row( it )
        if  i != lwCommands.count() -1 :
            lwCommands.insertItem( i +1, lwCommands.takeItem( i ) )
        lwCommands.setCurrentItem( it )



def on_lwCommands_itemSelectionChanged(self):
    item = lwCommands.selectedItems().value( 0 )
    lwCommands.setCurrentItem( item )


def on_lwCommands_currentItemChanged(self, current, previous ):
    Q_UNUSED( current )
    
    if  previous :
        command = previous.data( Qt.UserRole ).value<pCommand>()
        QStringList parsers
        
        for ( i = 0; i < lwCommandParsers.count(); i++ )
            item = lwCommandParsers.item( i )
            
            if  item.checkState() == Qt.Checked :
                parsers << item.text()


        
        command.setText( leCommandText.text() )
        command.setCommand( leCommandCommand.text() )
        command.setArguments( leCommandArguments.text() )
        command.setWorkingDirectory( leCommandWorkingDirectory.text() )
        command.setParsers( parsers )
        command.setSkipOnError( cbCommandSkipOnError.isChecked() )
        command.setTryAllParsers( cbCommandTryAll.isChecked() )
        
        previous.setData( Qt.UserRole, QVariant.fromValue( command ) )
        previous.setText( command.text() )

    
    updateGui()

