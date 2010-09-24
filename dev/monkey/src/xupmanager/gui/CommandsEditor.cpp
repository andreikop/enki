#include "CommandsEditor.h"

#include <QDebug>

CommandsEditor::CommandsEditor( QWidget* parent )
	: QFrame( parent )
{
	mLastCommandType = BasePlugin::iAll;
	setupUi( this );
	updateGui();
}

CommandsEditor::~CommandsEditor()
{
}

void CommandsEditor::finalize()
{
	// save current command, and global commands
	on_cbCommandTypes_currentIndexChanged( cbCommandTypes->currentIndex() );
}

void CommandsEditor::setCommandTypes( const BasePluginTypeList& types )
{
	mCommandTypes = types;
	cbCommandTypes->clear();
	
	foreach ( const BasePlugin::Type& type, types )
	{
		cbCommandTypes->addItem( BasePlugin::typeToString( type ), type );
	}
	
	cbCommandTypes->setCurrentIndex( -1 );
}

BasePluginTypeList CommandsEditor::commandTypes() const
{
	return mCommandTypes;
}

void CommandsEditor::setCommands( const TypeCommandListMap& commands )
{
	mCommands = commands;
}

TypeCommandListMap CommandsEditor::commands() const
{
	return mCommands;
}

void CommandsEditor::setCurrentType( BasePlugin::Type type )
{
	const int index = cbCommandTypes->findData( type );
	cbCommandTypes->setCurrentIndex( index );
}

BasePlugin::Type CommandsEditor::currentType() const
{
	const int index = cbCommandTypes->currentIndex();
	return (BasePlugin::Type)cbCommandTypes->itemData( index ).toInt();
}

void CommandsEditor::setParsers( const QStringList& parsers )
{
	mParsers = parsers;
	
	lwCommandParsers->clear();
	
	foreach ( const QString& parser, parsers )
	{
		QListWidgetItem* item = new QListWidgetItem( parser, lwCommandParsers );
		item->setCheckState( Qt::Unchecked );
	}
}

QStringList CommandsEditor::parsers() const
{
	return mParsers;
}

void CommandsEditor::updateGui()
{
	QListWidgetItem* item = lwCommands->currentItem();
	const int index = lwCommands->row( item );
	const int count = lwCommands->count();
	
	if ( item )
	{
		const pCommand command = item->data( Qt::UserRole ).value<pCommand>();
		const QSet<QString> parsers = command.parsers().toSet();
		
		leCommandText->setText( command.text() );
		leCommandCommand->setText( command.command() );
		leCommandArguments->setText( command.arguments() );
		leCommandWorkingDirectory->setText( command.workingDirectory() );
		cbCommandSkipOnError->setChecked( command.skipOnError() );
		cbCommandTryAll->setChecked( command.tryAllParsers() );
		
		for ( int i = 0; i < lwCommandParsers->count(); i++ )
		{
			QListWidgetItem* item = lwCommandParsers->item( i );
			
			if ( parsers.contains( item->text() ) )
			{
				item->setCheckState( Qt::Checked );
			}
			else
			{
				item->setCheckState( Qt::Unchecked );
			}
		}
	}
	else
	{
		leCommandText->clear();
		leCommandCommand->clear();
		leCommandArguments->clear();
		leCommandWorkingDirectory->clear();
		cbCommandSkipOnError->setChecked( false );
		cbCommandTryAll->setChecked( false );
		
		for ( int i = 0; i < lwCommandParsers->count(); i++ )
		{
			QListWidgetItem* item = lwCommandParsers->item( i );
			item->setCheckState( Qt::Unchecked );
		}
	}
	
	tbCommandRemove->setEnabled( item );
	tbCommandUp->setEnabled( item && index > 0 );
	tbCommandDown->setEnabled( item && count > 1 && index < count -1 );
	gbEditor->setEnabled( item );
}

void CommandsEditor::on_cbCommandTypes_currentIndexChanged( int index )
{
	Q_UNUSED( index );
	QListWidgetItem* current = lwCommands->currentItem();
	
	on_lwCommands_currentItemChanged( current, current );
	
	if ( mCommandTypes.contains( mLastCommandType ) )
	{
		pCommandList commands;
		
		for ( int i = 0; i < lwCommands->count(); i++ )
		{
			const QListWidgetItem* item = lwCommands->item( i );
			const pCommand command = item->data( Qt::UserRole ).value<pCommand>();
			
			commands << command;
		}
		
		mCommands[ mLastCommandType ] = commands;
	}
	
	mLastCommandType = currentType();
	const bool locked = lwCommands->blockSignals( true );
	lwCommands->clear();
	
	foreach ( const pCommand& command, mCommands.value( mLastCommandType ) )
	{
		QListWidgetItem* item = new QListWidgetItem( command.text(), lwCommands );
		item->setData( Qt::UserRole, QVariant::fromValue( command ) );
	}
	
	lwCommands->blockSignals( locked );
	
	updateGui();
}

void CommandsEditor::on_tbCommandAdd_clicked()
{
	QListWidgetItem* item = new QListWidgetItem( tr( "" ), lwCommands );
	lwCommands->setCurrentItem( item );
}

void CommandsEditor::on_tbCommandRemove_clicked()
{
	delete lwCommands->currentItem();
	updateGui();
}

void CommandsEditor::on_tbCommandUp_clicked()
{
	if ( QListWidgetItem* it = lwCommands->currentItem() )
	{
		int i = lwCommands->row( it );
		if ( i != 0 )
			lwCommands->insertItem( i -1, lwCommands->takeItem( i ) );
		lwCommands->setCurrentItem( it );
	}
}

void CommandsEditor::on_tbCommandDown_clicked()
{
	if ( QListWidgetItem* it = lwCommands->currentItem() )
	{
		int i = lwCommands->row( it );
		if ( i != lwCommands->count() -1 )
			lwCommands->insertItem( i +1, lwCommands->takeItem( i ) );
		lwCommands->setCurrentItem( it );
	}
}

void CommandsEditor::on_lwCommands_itemSelectionChanged()
{
	QListWidgetItem* item = lwCommands->selectedItems().value( 0 );
	lwCommands->setCurrentItem( item );
}

void CommandsEditor::on_lwCommands_currentItemChanged( QListWidgetItem* current, QListWidgetItem* previous )
{
	Q_UNUSED( current );
	
	if ( previous )
	{
		pCommand command = previous->data( Qt::UserRole ).value<pCommand>();
		QStringList parsers;
		
		for ( int i = 0; i < lwCommandParsers->count(); i++ )
		{
			QListWidgetItem* item = lwCommandParsers->item( i );
			
			if ( item->checkState() == Qt::Checked )
			{
				parsers << item->text();
			}
		}
		
		command.setText( leCommandText->text() );
		command.setCommand( leCommandCommand->text() );
		command.setArguments( leCommandArguments->text() );
		command.setWorkingDirectory( leCommandWorkingDirectory->text() );
		command.setParsers( parsers );
		command.setSkipOnError( cbCommandSkipOnError->isChecked() );
		command.setTryAllParsers( cbCommandTryAll->isChecked() );
		
		previous->setData( Qt::UserRole, QVariant::fromValue( command ) );
		previous->setText( command.text() );
	}
	
	updateGui();
}
