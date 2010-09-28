/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pConsoleManager.cpp
** Date      : 2008-01-14T00:36:50
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
**
    Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
**
****************************************************************************/
/*!
    \file pConsoleManager.cpp
    \date 2008-01-14T00:36:50
    \author Filipe AZEVEDO aka Nox PasNox <pasnox@gmail.com>
    \brief Implementation of pConsoleManager class
*/

#include <QTimer>
#include <QDir>
#include <QDebug>

#include "pConsoleManager.h"
#include "CommandParser.h"
#include "AbstractCommandParser.h"
#include "coremanager/MonkeyCore.h"
#include "variablesmanager/VariablesManager.h"

#include <widgets/pActionsManager.h>

/*!
    Defines maximum count of lines, which are storing in the buffer for parsing
*/
static const int MAX_LINES = 4; //Maximum lines count, that can be parsed by Monkey. Than less - than better perfomance

/*!
    Constructor of class
    \param o Parent object
*/
pConsoleManager::pConsoleManager( QObject* o )
    : QProcess( o ), mLinesInStringBuffer (0)
{
    pActionsManager* am = MonkeyCore::actionsManager();
    am->setPathPartTranslation( "Console Manager", tr( "Console Manager" ) );
    
#ifndef Q_OS_MAC
    mStopAction = MonkeyCore::actionsManager()->newAction( "Console Manager", tr( "Pause" ), "aStopAction" );
#else
    mStopAction = MonkeyCore::actionsManager()->newAction( "Console Manager", tr( "Alt+End" ), "aStopAction" );
#endif
    mStopAction->setIcon( QIcon( ":/console/icons/console/stop.png" ) );
    mStopAction->setText( tr( "Stop the currenttly running command" ) );
    mStopAction->setToolTip( mStopAction->text() );
    mStopAction->setStatusTip( mStopAction->text() );
    mStopAction->setEnabled( false );
    
    // mixe channels
    setReadChannelMode( QProcess::MergedChannels );
    
    // connections
    connect( this, SIGNAL( error( QProcess::ProcessError ) ), this, SLOT( error( QProcess::ProcessError ) ) );

    connect( this, SIGNAL( finished( int, QProcess::ExitStatus ) ), this, SLOT( finished( int, QProcess::ExitStatus ) ) );
    connect( this, SIGNAL( readyRead() ), this, SLOT( readyRead() ) );
    connect( this, SIGNAL( started() ), this, SLOT( started() ) );
    connect( this, SIGNAL( stateChanged( QProcess::ProcessState ) ), this, SLOT( stateChanged( QProcess::ProcessState ) ) );
    connect( mStopAction, SIGNAL( triggered() ), this, SLOT( stopCurrentCommand() ) );
    // start timerEvent
    mTimerId = startTimer( 100 );
    mStringBuffer.reserve (MAX_LINES *200);
    mStopAttempt = 0;
    
    CommandParser::installParserCommand();
}

/*!
    Destructor of class
*/
pConsoleManager::~pConsoleManager()
{
    terminate();
    waitForFinished();
    kill();
}

/*!
    Append parser to list of alailable parsers (which could be used for some commands)
    \param p Pointer to parser
*/
void pConsoleManager::addParser( AbstractCommandParser* p )
{
    Q_ASSERT( p );
    
    if (mParsers.contains(p->name()))
    {
        qDebug() << QString("Parser '%1' already had been added").arg(p->name());
        return;
    }
    
    mParsers[p->name()] = p;
    connect( p, SIGNAL( newStepAvailable( const pConsoleManagerStep& ) ), this, SIGNAL( newStepAvailable( const pConsoleManagerStep& ) ) );
    connect( p, SIGNAL( newStepsAvailable( const pConsoleManagerStepList& ) ), this, SIGNAL( newStepsAvailable( const pConsoleManagerStepList& ) ) );
}

/*!
    Remove parser to list of available parsers (which could be used for some commands)
    \param p Pointer to parser
*/
void pConsoleManager::removeParser( AbstractCommandParser* p )
{
    if ( p && mParsers.contains( p->name() ) )
    {
        disconnect( p, SIGNAL( newStepAvailable( const pConsoleManagerStep& ) ), this, SIGNAL( newStepAvailable( const pConsoleManagerStep& ) ) );
        disconnect( p, SIGNAL( newStepsAvailable( const pConsoleManagerStepList& ) ), this, SIGNAL( newStepsAvailable( const pConsoleManagerStepList& ) ) );
        mParsers.remove( p->name() );
    }
}

/*!
    Remove parser to list of available parsers (which could be used for some commands)
    \param s Name of parser
*/
void pConsoleManager::removeParser( const QString& s )
{ removeParser( mParsers.value( s ) ); }

/*!
    Returns pointer to parser, or NULL if not found
 */
AbstractCommandParser* pConsoleManager::getParser(const QString& name)
{
    return mParsers.value(name);
}

/*!
    Check, if string contains spaces, and, if it do - add quotes <"> to start and end of it
    \param s Source string
    \return Result string
*/
QString pConsoleManager::quotedString( const QString& s )
{
    if ( s.contains( " " ) && !s.startsWith( '"' ) /*&& !s.endsWith( '"' )*/ )
    {
        return QString( s ).prepend( '"' ).append( '"' );
    }
    
    return s;
}

/*!
    Replace internal varibles in the string with it's values

    \param s Source string
    \return Result string
*/
QString pConsoleManager::processInternalVariables( const QString& s )
{
    return VariablesManager::instance()->replaceAllVariables( s );
}

/*!
    Prepare command for starting (set internal variables)

    \param c Command for execution
    \return Command for execution
    \retval Command, gived as parameter
*/
pCommand pConsoleManager::processCommand( pCommand c )
{
    // process variables
    c.setCommand( processInternalVariables( c.command() ) );
    c.setArguments( processInternalVariables( c.arguments() ) );
    c.setWorkingDirectory( processInternalVariables( c.workingDirectory() ) );
    // return command
    return c;
}

/*!
    Search command in the list by it's text, or return empty one
    \param l List of commands, where to search
    \param s Text of command for searhing
    \return Finded command, or empty command if not finded
*/
pCommand pConsoleManager::getCommand( const pCommandList& l, const QString& s )
{
    foreach ( pCommand c, l )
        if ( c.text() == s )
            return c;
    return pCommand();
}

/*!
    FIXME PasNox, comment please

*/
pCommandList pConsoleManager::recursiveCommandList( const pCommandList& l, pCommand c )
{
    pCommandList cl;
    // check if chan command
    QStringList lc = c.command().split( ";" );
    if ( lc.count() > 1 )
    {
        foreach ( QString s, lc )
            cl << recursiveCommandList( l, getCommand( l, s ) );
    }
    // process variables
    else
    {
        // process variables
        pCommand pc = processCommand( c );
        // set skit on error
        pc.setSkipOnError( true );
        // add to list
        cl << pc;
    }
    // return list
    return cl;
}

/*!
    Return human readable string of a QProcess::ProcessError

    \param error The error to get string from
*/
QString pConsoleManager::errorToString( QProcess::ProcessError error )
{
    switch ( error )
    {
        case QProcess::FailedToStart:
            return tr( "The process failed to start. Either the invoked program is missing, or you may have insufficient permissions to invoke the program." );
        case QProcess::Crashed:
            return tr( "The process crashed some time after starting successfully." );
        case QProcess::Timedout:
            return tr( "The last waitFor...() function timed out. The state of QProcess is unchanged, and you can try calling waitFor...() again." );
        case QProcess::WriteError:
            return tr( "An error occurred when attempting to write to the process. For example, the process may not be running, or it may have closed its input channel." );
        case QProcess::ReadError:
            return tr( "An error occurred when attempting to read from the process. For example, the process may not be running." );
        case QProcess::UnknownError:
        default:
            return tr( "An unknown error occurred. This is the default return value of error()." );
    }
}

/*!
    Handler of timer event

    Exucutes next command, if there is available in the list, and no currently running commands
    FIXME Check, if it's realy nessesery to use timer
    \param e Timer event
*/
void pConsoleManager::timerEvent( QTimerEvent* e )
{
    if ( e->timerId() == mTimerId )
    {
        // if running continue
        if ( state() != QProcess::NotRunning )
            return;
        // execute next task is available
        if ( !mCommands.isEmpty() )
            executeProcess();
    }
}

/*!
    Emit signal, when process failing with error
    \param e Process error
*/
void pConsoleManager::error( QProcess::ProcessError e )
{
    // emit signal error
    emit commandError( currentCommand(), e );
    // need emulate state 0 for linux
#ifndef Q_WS_WIN
    if ( e == QProcess::FailedToStart )
        stateChanged( QProcess::NotRunning );
#endif
}

/*!
    Handler of finishing of execution of command

    \param i Ask PasNox, what is it
    \param e Exit status of process
*/
void pConsoleManager::finished( int i, QProcess::ExitStatus e )
{
    const pCommand command = currentCommand();
    // parse output
    parseOutput( true );
    // emit signal finished
    emit commandFinished( command, i, e );
    // remove command from list
    removeCommand( command );
    // disable stop action
    mStopAction->setEnabled( false );
    // clear buffer
    mBuffer.buffer().clear();
    mStringBuffer.clear(); // For perfomance issues
    mLinesInStringBuffer = 0;
}

/*!
    Handler or 'ready read' event from child process

    Reads output from process and tryes to parse it
*/
void pConsoleManager::readyRead()
{
    // append data to buffer to parse
    const QByteArray data = readAll();
    mBuffer.buffer().append( data );
    
    // get current command
    const pCommand command = currentCommand();
    
    // try parse output
    if ( !command.isValid() )
        return;
    
    /*Alrorithm is not ideal, need fix, if will be problems with it
        Some text, that next parser possible to parse, can be removed
        And, possible, it's not idealy quick.   hlamer
        */

    parseOutput( false );

    // emit signal
    emit commandReadyRead( command, data );
}

/*!
    Handler of 'started' event from child process
*/
void pConsoleManager::started()
{
    // enable stop action
    mStopAction->setEnabled( true );
    // emit signal
    emit commandStarted( currentCommand() );
}

/*!
    Handler of changing status of child process
    \param e New process state
*/
void pConsoleManager::stateChanged( QProcess::ProcessState e )
{
    // emit signal state changed
    emit commandStateChanged( currentCommand(), e );
    // remove command if crashed and state 0
    if ( QProcess::error() == QProcess::FailedToStart && e == QProcess::NotRunning )
        removeCommand( currentCommand() );
}

/*!
    Create command and append it to list for executing
    \param s Command to execute
*/
void pConsoleManager::sendRawCommand( const QString& s )
{ addCommand( pCommand( tr( "User Raw Command" ), s, QString::null, false ) ); }

void pConsoleManager::sendRawData( const QByteArray& a )
{
    if ( state() != QProcess::NotRunning )
    {
        // if program is starting wait
        while ( state() == QProcess::Starting )
            QApplication::processEvents( QEventLoop::ExcludeUserInputEvents );
        // send raw command to process
        write( a );
    }
    else
        emit warning( tr( "Can't send raw data to console" ) );
}

/*!
    Try to stop current command. if stop attempt for same commend = 3 the command is killed
*/
void pConsoleManager::stopCurrentCommand()
{
    if ( state() != QProcess::NotRunning )
    {
        // terminate properly
        terminate();

        // increment attempt
        mStopAttempt++;

        // auto kill if attempt = 3
        if ( mStopAttempt == 3 )
        {
            mStopAttempt = 0;
            kill();
        }
    }
}

/*!
    Add command to list for executing
    \param c  Command
*/
void pConsoleManager::addCommand( const pCommand& c )
{
    if ( c.isValid() )
        mCommands << c;
}

/*!
    Add list of command for executing
    \param l List of commands
*/
void pConsoleManager::addCommands( const pCommandList& l )
{
    foreach ( pCommand c, l )
        addCommand( c );
}

/*!
    Remove command from list of commands for executing

    \param c Command
*/
void pConsoleManager::removeCommand( const pCommand& c )
{
    if ( mCommands.contains( c ) )
        mCommands.removeAt( mCommands.indexOf ( c ) );
}

/*!
    Remove list of commands from list for executing
    \param l List of commands
*/
void pConsoleManager::removeCommands( const pCommandList& l )
{
    foreach ( pCommand c, l )
        removeCommand( c );
}

/*!
    Execute commands, which currently are in the list
*/
void pConsoleManager::executeProcess()
{
    foreach ( pCommand c, mCommands )
    {
        // if last was error, cancel this one if it want to
        if ( c.skipOnError() && QProcess::error() != QProcess::UnknownError )
        {
            // emit command skipped
            emit commandSkipped( c );
            // remove command from command to execute
            removeCommand( c );
            // execute next
            continue;
        }

        // set current parsers list
        // parsers comamnd want to test/check
        mCurrentParsers = c.parsers();
        
        // check if need tryall, and had all other parsers if needed at end
        if ( c.tryAllParsers() )
            foreach ( QString s, parsersName() )
                if ( !mCurrentParsers.contains( s ) )
                    mCurrentParsers << s;
        // execute command
        mStopAttempt = 0;
        setWorkingDirectory( c.workingDirectory() );
        
        QStringList variables = mEnvironmentVariablesManager.variables( false );
        
        // unset some variables environments when no parsers is defined
        if ( !mCurrentParsers.isEmpty() )
        {
            const int index = variables.indexOf( QRegExp( "^LANG=.*$" ) );
            
            if ( index != -1 )
            {
                variables.removeAt( index );
            }
        }
        
        setEnvironment( variables );

        start( QString( "%1 %2" ).arg( quotedString( c.command() ) ).arg( c.arguments() ) );

        mBuffer.open( QBuffer::ReadOnly );
        // exit
        return;
    }
}

/*!
    Parse output of command, which are storing in the buffer, using parsers.

    \param commandFinished If command already are finished, make processing while
    buffer will not be empty. If not finished - wait for further output.
*/
void pConsoleManager::parseOutput( bool commandFinished )
{
    bool finished;
    
    do
    {
        // Fill string buffer
        while ( mBuffer.canReadLine() && mLinesInStringBuffer < MAX_LINES )
        {

            mStringBuffer.append( QString::fromLocal8Bit( mBuffer.readLine() ) );
            mLinesInStringBuffer ++;
        }

        if ( !mLinesInStringBuffer )
            return;

        finished = true;
        int linesToRemove = 0;
        
        //try all parsers
        foreach ( const QString& parserName, mCurrentParsers )
        {
            AbstractCommandParser* parser = mParsers.value( parserName );
            
            if ( !parser )
            {
                qWarning() << "Invalid parser" << parserName;
                continue; //for
            }
            
            linesToRemove =  parser->processParsing( &mStringBuffer );
            
            if ( linesToRemove )
                break; //for
        }
        
        if ( linesToRemove == 0 || commandFinished ) //need to remove one
            linesToRemove = 1;

        if ( !linesToRemove )
            continue; // do-while

        finished = false; //else one iteration of do-while after it

        //removing of lines
        mLinesInStringBuffer -= linesToRemove;
        int posEnd = 0;
        
        while ( linesToRemove-- )
            posEnd = mStringBuffer.indexOf( '\n', posEnd ) +1;
            
        mStringBuffer.remove( 0, posEnd );
    }
    while ( !finished && mLinesInStringBuffer );
}

