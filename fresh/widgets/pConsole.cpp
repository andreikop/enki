#include "pConsole.h"

#include <QTextBlock>
#include <QApplication>
#include <QClipboard>
#include <QFile>

#include <QDebug>

pConsole::pConsole( QWidget* parent )
	: QPlainTextEdit( parent )
{
	reset();
}

pConsole::~pConsole()
{
	qDeleteAll( mAvailableCommands );
	mAvailableCommands.clear();
}

QString pConsole::prompt() const
{
	return mPrompt;
}

void pConsole::setPrompt( const QString& prompt )
{
	mPrompt = prompt;
	
	if ( isPromptVisible() )
	{
		displayPrompt();
	}
}

bool pConsole::isPromptVisible() const
{
	return !isReadOnly();
}

void pConsole::setPromptVisible( bool visible )
{
	setReadOnly( !visible );
}

QStringList pConsole::history() const
{
	return mHistory;
}

void pConsole::setHistory( const QStringList& history )
{
	mHistory = history;
	mHistoryIndex = mHistory.count();
}

QColor pConsole::color( ColorType type ) const
{
	return mColors.value( type );
}

void pConsole::setColor( ColorType type, const QColor& color )
{
	mColors[ type ] = color;
}

void pConsole::executeCommand( const QString& command, bool writeCommand, bool showPrompt )
{
	const QStringList clearCommands = QStringList( "clear" ) << "cls";
	
	if ( clearCommands.contains( command, Qt::CaseInsensitive ) )
	{
		clear();
		
		if ( showPrompt )
		{
			displayPrompt();
		}
		
		return;
	}
	
	// write command to execute
	if ( writeCommand )
	{
		if ( !currentCommand().isEmpty() )
		{
			displayPrompt();
		}
		
		insertPlainText( command );
	}
	
	// execute command
	int res;
	QString strRes = interpretCommand( command, &res );
	
	// write output in different colors if needed
	if ( res == 0 )
	{
		useColor( ctOutput );
	}
	else
	{
		useColor( ctError );
	}
	
	if ( !strRes.isEmpty() )
	{
		appendPlainText( strRes );
	}
	
	useColor( ctCommand );
	
	// display the prompt again if needed
	if ( showPrompt )
	{
		displayPrompt();
	}
}

bool pConsole::saveScript( const QString& fileName )
{
	QFile file( fileName );
	
	if ( !file.open( QIODevice::WriteOnly | QIODevice::Text ) )
	{
		return false;
	}
	
	file.resize( 0 );
	
	foreach ( QString command, mRecordedScript )
	{
		if ( file.write( command.append( "\n" ).toUtf8() ) == -1 )
		{
			file.close();
			return false;
		}
	}
	
	file.close();
	return true;
}

bool pConsole::loadScript( const QString& fileName )
{
	QFile file( fileName );
	
	if ( !file.open( QIODevice::ReadOnly | QIODevice::Text ) )
	{
		return false;
	}
	
	while ( file.canReadLine() )
	{
		executeCommand( file.readLine(), true, false );
	}
	
	file.close();
	return true;
}

void pConsole::clear()
{
	QPlainTextEdit::clear();
}

//Reset the console
void pConsole::reset()
{
	clear();
	
	setTextInteractionFlags( Qt::TextSelectableByMouse | Qt::TextSelectableByKeyboard | Qt::LinksAccessibleByMouse | Qt::LinksAccessibleByKeyboard | Qt::TextEditable );
	setUndoRedoEnabled( false );
	setTabStopWidth( 30 );
	
	QFont font = QFont( "Bitstream Vera Sans Mono", 11 );
	font.setBold( true );
	setFont( font );
	
	QPalette pal = viewport()->palette();
	pal.setColor( viewport()->backgroundRole(), QColor( Qt::black ) );
	pal.setColor( viewport()->foregroundRole(), QColor( Qt::white ) );
	viewport()->setPalette( pal );
	
	mColors[ ctCommand ] = Qt::white;
	mColors[ ctError ] = Qt::red;
	mColors[ ctOutput ] = Qt::blue;
	mColors[ ctCompletion ] = Qt::green;
	
	mRecordedScript.clear();
	mTypedCommand.clear();
	
	setHistory( QStringList() );
	setPromptVisible( true );
	setPrompt( "@:/> " );
}

pConsoleCommandList pConsole::availableCommands() const
{
	return mAvailableCommands;
}

void pConsole::setAvailableCommands( const pConsoleCommandList& commands )
{
	qDeleteAll( mAvailableCommands );
	mAvailableCommands.clear();
	mAvailableCommands = commands;
}

void pConsole::addAvailableCommand( pConsoleCommand* command )
{
	if ( !mAvailableCommands.contains( command ) )
	{
		mAvailableCommands << command;
	}
}

void pConsole::removeAvailableCommand( pConsoleCommand* command )
{
	mAvailableCommands.removeAll( command );
}

void pConsole::keyPressEvent( QKeyEvent* event )
{
	// filter out cut action
	if ( event->matches( QKeySequence::Cut ) )
	{
		return;
	}
	
	// filter out paste
	if ( event->matches( QKeySequence::Paste ) )
	{
		QString command = QApplication::clipboard()->text().replace( "\r\n", "\n" );
		
		command.replace( "\r", "\n" );
		while ( command.contains( "\n\n" ) )
		{
			command.replace( "\n\n", "\n" );
		}
		
		QStringList commands = command.split( "\n" );
		
		foreach ( command, commands )
		{
			//if ( isCommandComplete( command ) )
			{
				executeCommand( command, true );
			}
		}
		
		return;
	}
	
	// some needed infos
	int relativePos = textCursor().position() -textCursor().block().position();
	int historyId = mHistoryIndex;
	bool processEvent = true;
	
	// case
	switch ( event->key() )
	{
		case Qt::Key_Enter:
		case Qt::Key_Return:
		{
			const QString command = currentCommand();
			
			//if ( isCommandComplete( command ) )
			{
				executeCommand( command, false );
			}
			
			return;
			break;
		}
		case Qt::Key_Escape:
		{
			// stopCommand();
			
			return;
			break;
		}
		case Qt::Key_Left:
		case Qt::Key_Backspace:
		{
			if ( relativePos <= mPrompt.length() )
			{
				return;
			}
			
			break;
		}
		case Qt::Key_Right:
		{
			break;
		}
		case Qt::Key_Up:
		{
			processEvent = false;
			historyId--;
			
			break;
		}
		case Qt::Key_Down:
		{
			processEvent = false;
			historyId++;
			
			break;
		}
		case Qt::Key_Home:
		{
			processEvent = false;
			QTextCursor cursor = textCursor();
			
			cursor.setPosition( cursor.block().position() +mPrompt.length() );
			setTextCursor( cursor );
			
			break;
		}
		case Qt::Key_PageUp:
		{
			processEvent = false;
			historyId = -1;
			
			if ( !mHistory.isEmpty() )
			{
				historyId = 0;
			}
			
			break;
		}
		case Qt::Key_PageDown:
		{
			processEvent = false;
			historyId = -1;
			
			if ( !mHistory.isEmpty() )
			{
				historyId = mHistory.count() -1;
			}
			
			break;
		}
		case Qt::Key_Tab:
		{
			QString command = currentCommand();
			QStringList sl = autocompleteCommand( command );
			QString str = sl.join( "    " );
			
			if ( sl.count() == 1 )
			{
				replaceCommand( sl.at( 0 ) +" " );
			}
			else if ( !sl.isEmpty() )
			{
				useColor( ctCompletion );
				appendPlainText( str );
				useColor( ctCommand );
				displayPrompt();
				insertPlainText( command );
			}
			
			return;
			break;
		}
		default:
			break;
	}
	
	if ( processEvent )
	{
		if ( textCursor().hasSelection() && event->modifiers() == Qt::NoModifier )
		{
			focusCommand();
		}
		
		QPlainTextEdit::keyPressEvent( event );
		
		mTypedCommand = currentCommand();
	}
	
	if ( historyId != mHistoryIndex )
	{
		if ( !showHistoryItem( historyId ) )
		{
			if ( historyId < 0 )
			{
				mHistoryIndex = 0;
			}
			else
			{
				mHistoryIndex = mHistory.count();
				
				replaceCommand( mTypedCommand );
			}
		}
	}
	
	mPromptPosition.setX( textCursor().columnNumber() );
}

void pConsole::mousePressEvent( QMouseEvent* event )
{
	QTextCursor cursor = textCursor();
	int length = mPrompt.length();
	int column = cursor.columnNumber() < length ? length : cursor.columnNumber();
	
	mPromptPosition = QPoint( column, cursor.blockNumber() );
	
	setPromptVisible( false );
	
	QPlainTextEdit::mousePressEvent( event );
}

void pConsole::mouseReleaseEvent( QMouseEvent* event )
{
	QPlainTextEdit::mouseReleaseEvent( event );
	
	if ( textCursor().hasSelection() )
	{
		copy();
	}
	
	focusCommand();
	setPromptVisible( true );
}

bool pConsole::isCommandComplete( const QString& command )
{
	foreach ( const pConsoleCommand* cmd, mAvailableCommands )
	{
		if ( cmd->isComplete( command ) )
		{
			return true;
		}
	}
	
	return false;
}

QString pConsole::interpretCommand( const QString& command, int* result )
{
	QString output;
	bool foundCommand = false;
	
	foreach ( const pConsoleCommand* cmd, mAvailableCommands )
	{
		if ( cmd->isComplete( command ) )
		{
			foundCommand = true;
			output = cmd->interpret( command, result );
			break;
		}
	}
	
	if ( !foundCommand )
	{
		output = tr( "%1: Command not found." ).arg( command );
	}
	
	// add the command to the recordedScript list
	if ( !*result )
	{
		mRecordedScript << command;
	}
	
	// update history
	mHistory << QString( command ).replace( "\n", "\\n" );
	mHistoryIndex = mHistory.count();
	
	// emit command executed
	emit commandExecuted( command, *result );
	
	// return output
	return output;
}

QStringList pConsole::autocompleteCommand( const QString& command )
{
	QStringList result;
	
	foreach ( const pConsoleCommand* cmd, mAvailableCommands )
	{
		const QStringList list = cmd->autoCompleteList( command );
		
		if ( !list.isEmpty() )
		{
			result << list;
		}
	}
	
	return result;
}

bool pConsole::replaceCommand( const QString& command )
{
	QTextBlock block = document()->findBlockByNumber( mPromptPosition.y() );
	
	if ( !block.isValid() )
	{
		return false;
	}
	
	QTextCursor cursor( block );
	cursor.beginEditBlock();
	cursor.movePosition( QTextCursor::StartOfBlock );
	cursor.movePosition( QTextCursor::EndOfBlock, QTextCursor::KeepAnchor );
	cursor.removeSelectedText();
	cursor.insertText( mPrompt );
	cursor.insertText( command );
	cursor.endEditBlock();
	
	mPromptPosition.setX( cursor.columnNumber() );
	
	return true;
}

QString pConsole::currentCommand() const
{
	QTextBlock block = document()->findBlockByNumber( mPromptPosition.y() );
	
	if ( !block.isValid() )
	{
		return QString::null;
	}
	
	return block.text().mid( mPrompt.length() );
}

void pConsole::focusCommand()
{
	QTextBlock block = document()->findBlockByNumber( mPromptPosition.y() );
	
	if ( !block.isValid() )
	{
		return;
	}
	
	QTextCursor cursor( block );
	cursor.beginEditBlock();
	cursor.movePosition( QTextCursor::StartOfBlock );
	cursor.setPosition( cursor.position() +mPromptPosition.x(), QTextCursor::MoveAnchor );
	cursor.endEditBlock();
	
	setTextCursor( cursor );
}

void pConsole::useColor( ColorType type )
{
	QTextCursor cursor = textCursor();
	QTextCharFormat format = cursor.charFormat();
	
	format.setForeground( color( type ) );
	cursor.setCharFormat( format );
	setTextCursor( cursor );
}

void pConsole::displayPrompt()
{
	if ( mPrompt.isEmpty() )
	{
		return;
	}
	
	useColor( ctCommand );
	
	appendPlainText( mPrompt );
	
	mHistoryIndex = mHistory.count();
	QTextBlock block = document()->lastBlock();
	QTextCursor cursor( block );
	
	mTypedCommand.clear();
	cursor.movePosition( QTextCursor::EndOfBlock, QTextCursor::MoveAnchor );
	setTextCursor( cursor );
	
	mPromptPosition = QPoint( cursor.columnNumber(), cursor.blockNumber() );
}

bool pConsole::showHistoryItem( int index )
{
	if ( index >= 0 && index < mHistory.count() )
	{
		mHistoryIndex = index;
		
		return replaceCommand( mHistory.at( index ) );
	}
	
	return false;
}
