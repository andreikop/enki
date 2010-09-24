'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pConsoleManager.cpp
** Date      : 2008-01-14T00:36:50
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
'''!
    \file pConsoleManager.cpp
    \date 2008-01-14T00:36:50
    \author Filipe AZEVEDO aka Nox PasNox <pasnox@gmail.com>
    \brief Implementation of pConsoleManager class
'''

#include <QTimer>
#include <QDir>
#include <QDebug>

#include "pConsoleManager.h"
#include "CommandParser.h"
#include "AbstractCommandParser.h"
#include "coremanager/MonkeyCore.h"
#include "variablesmanager/VariablesManager.h"

#include <widgets/pActionsManager.h>

'''!
    Defines maximum count of lines, are storing in the buffer for parsing
'''
static  MAX_LINES = 4; #Maximum lines count, can be parsed by Monkey. Than less - than better perfomance

'''!
    Constructor of class
    \param o Parent object
'''
pConsoleManager.pConsoleManager( QObject* o )
        : QProcess( o ), mLinesInStringBuffer (0)
    am = MonkeyCore.actionsManager()
    am.setPathPartTranslation( "Console Manager", tr( "Console Manager" ) )

#ifndef Q_OS_MAC
    mStopAction = MonkeyCore.actionsManager().newAction( "Console Manager", tr( "Pause" ), "aStopAction" )
#else:
    mStopAction = MonkeyCore.actionsManager().newAction( "Console Manager", tr( "Alt+End" ), "aStopAction" )
#endif
    mStopAction.setIcon( QIcon( ":/console/icons/console/stop.png" ) )
    mStopAction.setText( tr( "Stop the currenttly running command" ) )
    mStopAction.setToolTip( mStopAction.text() )
    mStopAction.setStatusTip( mStopAction.text() )
    mStopAction.setEnabled( False )

    # mixe channels
    setReadChannelMode( QProcess.MergedChannels )

    # connections
    self.error.connect(self.error)

    self.finished.connect(self.finished)
    self.readyRead.connect(self.readyRead)
    self.started.connect(self.started)
    self.stateChanged.connect(self.stateChanged)
    mStopAction.triggered.connect(self.stopCurrentCommand)
    # start timerEvent
    mTimerId = startTimer( 100 )
    mStringBuffer.reserve (MAX_LINES *200)
    mStopAttempt = 0

    CommandParser.installParserCommand()


'''!
    Destructor of class
'''
pConsoleManager.~pConsoleManager()
    terminate()
    waitForFinished()
    kill()


'''!
    Append parser to list of alailable parsers (which could be used for some commands)
    \param p Pointer to parser
'''
def addParser(self, p ):
    Q_ASSERT( p )

    if mParsers.contains(p.name()):
        qDebug() << QString("Parser '%1' already had been added").arg(p.name())
        return


    mParsers[p.name()] = p
    connect( p, SIGNAL( newStepAvailable(  pConsoleManagerStep& ) ), self, SIGNAL( newStepAvailable(  pConsoleManagerStep& ) ) )
    connect( p, SIGNAL( newStepsAvailable(  pConsoleManagerStepList& ) ), self, SIGNAL( newStepsAvailable(  pConsoleManagerStepList& ) ) )


'''!
    Remove parser to list of available parsers (which could be used for some commands)
    \param p Pointer to parser
'''
def removeParser(self, p ):
    if  p and mParsers.contains( p.name() ) :
        disconnect( p, SIGNAL( newStepAvailable(  pConsoleManagerStep& ) ), self, SIGNAL( newStepAvailable(  pConsoleManagerStep& ) ) )
        disconnect( p, SIGNAL( newStepsAvailable(  pConsoleManagerStepList& ) ), self, SIGNAL( newStepsAvailable(  pConsoleManagerStepList& ) ) )
        mParsers.remove( p.name() )



'''!
    Remove parser to list of available parsers (which could be used for some commands)
    \param s Name of parser
'''
def removeParser(self, s ):
    removeParser( mParsers.value( s ) )


'''!
    Returns pointer to parser, NULL if not found
 '''
def getParser(self, name):
    return mParsers.value(name)


'''!
    Check, string contains spaces, and, it do - add quotes <"> to start and end of it
    \param s Source string
    \return Result string
'''
def quotedString(self, s ):
    if  s.contains( " " ) and not s.startsWith( '"' ) '''and not s.endsWith( '"' )''' :
        return QString( s ).prepend( '"' ).append( '"' )


    return s


'''!
    Replace internal varibles in the string with it's values

    \param s Source string
    \return Result string
'''
def processInternalVariables(self, s ):
    return VariablesManager.instance().replaceAllVariables( s )


'''!
    Prepare command for starting (set internal variables)

    \param c Command for execution
    \return Command for execution
    \retval Command, as parameter
'''
def processCommand(self, c ):
    # process variables
    c.setCommand( processInternalVariables( c.command() ) )
    c.setArguments( processInternalVariables( c.arguments() ) )
    c.setWorkingDirectory( processInternalVariables( c.workingDirectory() ) )
    # return command
    return c


'''!
    Search command in the list by it's text, return empty one
    \param l List of commands, to search
    \param s Text of command for searhing
    \return Finded command, empty command if not finded
'''
def getCommand(self, l, s ):
    for c in l:
    if  c.text() == s :
        return c
    return pCommand()


'''!
    FIXME PasNox, please

'''
def recursiveCommandList(self, l, c ):
    pCommandList cl
    # check if chan command
    lc = c.command().split( ";" )
    if  lc.count() > 1 :
        for s in lc:
        cl << recursiveCommandList( l, getCommand( l, s ) )

    # process variables
    else:
        # process variables
        pc = processCommand( c )
        # set skit on error
        pc.setSkipOnError( True )
        # add to list
        cl << pc

    # return list
    return cl


'''!
    Return human readable string of a QProcess.ProcessError

    \param error The error to get string from
'''
def errorToString(self, error ):
    switch ( error )
    case QProcess.FailedToStart:
        return tr( "The process failed to start. Either the invoked program is missing, you may have insufficient permissions to invoke the program." )
    case QProcess.Crashed:
        return tr( "The process crashed some time after starting successfully." )
    case QProcess.Timedout:
        return tr( "The last waitFor...() function timed out. The state of QProcess is unchanged, you can try calling waitFor...() again." )
    case QProcess.WriteError:
        return tr( "An error occurred when attempting to write to the process. For example, process may not be running, it may have closed its input channel." )
    case QProcess.ReadError:
        return tr( "An error occurred when attempting to read from the process. For example, process may not be running." )
    case QProcess.UnknownError:
    default:
        return tr( "An unknown error occurred. This is the default return value of error()." )



'''!
    Handler of timer event

    Exucutes next command, there is available in the list, no currently running commands
    FIXME Check, it's realy nessesery to use timer
    \param e Timer event
'''
def timerEvent(self, e ):
    if  e.timerId() == mTimerId :
        # if running continue
        if  state() != QProcess.NotRunning :
            return
        # execute next task is available
        if  not mCommands.isEmpty() :
            executeProcess()



'''!
    Emit signal, process failing with error
    \param e Process error
'''
def error(self, e ):
    # signal.emit error
    commandError.emit( currentCommand(), e )
    # need emulate state 0 for linux
#ifndef Q_WS_WIN
    if  e == QProcess.FailedToStart :
        stateChanged( QProcess.NotRunning )
#endif


'''!
    Handler of finishing of execution of command

    \param i Ask PasNox, is it
    \param e Exit status of process
'''
def finished(self, i, e ):
     command = currentCommand()
    # parse output
    parseOutput( True )
    # signal.emit finished
    commandFinished.emit( command, i, e )
    # remove command from list
    removeCommand( command )
    # disable stop action
    mStopAction.setEnabled( False )
    # clear buffer
    mBuffer.buffer().clear()
    mStringBuffer.clear(); # For perfomance issues
    mLinesInStringBuffer = 0


'''!
    Handler or 'ready read' event from child process

    Reads output from process and tryes to parse it
'''
def readyRead(self):
    # append data to buffer to parse
     data = readAll()
    mBuffer.buffer().append( data )

    # get current command
     command = currentCommand()

    # try parse output
    if  not command.isValid() :
        return

    '''Alrorithm is not ideal, fix, will be problems with it
        Some text, next parser possible to parse, be removed
        And, possible, it's not idealy quick.   hlamer
        '''

    parseOutput( False )

    # signal.emit
    commandReadyRead.emit( command, data )


'''!
    Handler of 'started' event from child process
'''
def started(self):
    # enable stop action
    mStopAction.setEnabled( True )
    # signal.emit
    commandStarted.emit( currentCommand() )


'''!
    Handler of changing status of child process
    \param e New process state
'''
def stateChanged(self, e ):
    # signal.emit state changed
    commandStateChanged.emit( currentCommand(), e )
    # remove command if crashed and state 0
    if  QProcess.error() == QProcess.FailedToStart and e == QProcess.NotRunning :
        removeCommand( currentCommand() )


'''!
    Create command and append it to list for executing
    \param s Command to execute
'''
def sendRawCommand(self, s ):
    addCommand( pCommand( tr( "User Raw Command" ), s, QString.null, False ) )


def sendRawData(self, a ):
    if  state() != QProcess.NotRunning :
        # if program is starting wait
        while ( state() == QProcess.Starting )
            QApplication.processEvents( QEventLoop.ExcludeUserInputEvents )
        # send raw command to process
        write( a )

    else:
        warning.emit( tr( "Can't send raw data to console" ) )


'''!
    Try to stop current command. if stop attempt for commend = 3 the command is killed
'''
def stopCurrentCommand(self):
    if  state() != QProcess.NotRunning :
        # terminate properly
        terminate()

        # increment attempt
        mStopAttempt++

        # auto kill attempt = 3
        if  mStopAttempt == 3 :
            mStopAttempt = 0
            kill()




'''!
    Add command to list for executing
    \param c  Command
'''
def addCommand(self, c ):
    if  c.isValid() :
        mCommands << c


'''!
    Add list of command for executing
    \param l List of commands
'''
def addCommands(self, l ):
    for c in l:
    addCommand( c )


'''!
    Remove command from list of commands for executing

    \param c Command
'''
def removeCommand(self, c ):
    if  mCommands.contains( c ) :
        mCommands.removeAt( mCommands.indexOf ( c ) )


'''!
    Remove list of commands from list for executing
    \param l List of commands
'''
def removeCommands(self, l ):
    for c in l:
    removeCommand( c )


'''!
    Execute commands, currently are in the list
'''
def executeProcess(self):
    for c in mCommands:
        # if last was error, self one if it want to
        if  c.skipOnError() and QProcess.error() != QProcess.UnknownError :
            # command.emit skipped
            commandSkipped.emit( c )
            # remove command from command to execute
            removeCommand( c )
            # execute next
            continue


        # set current parsers list
        # parsers comamnd want to test/check
        mCurrentParsers = c.parsers()

        # check if need tryall, had all other parsers if needed at end
        if  c.tryAllParsers() :
            for s in parsersName():
            if  not mCurrentParsers.contains( s ) :
                mCurrentParsers << s
        # execute command
        mStopAttempt = 0
        setWorkingDirectory( c.workingDirectory() )

        variables = mEnvironmentVariablesManager.variables( False )

        # unset some variables environments when no parsers is defined
        if  not mCurrentParsers.isEmpty() :
             index = variables.indexOf( QRegExp( "^LANG=.*$" ) )

            if  index != -1 :
                variables.removeAt( index )



        setEnvironment( variables )

        start( QString( "%1 %2" ).arg( quotedString( c.command() ) ).arg( c.arguments() ) )

        mBuffer.open( QBuffer.ReadOnly )
        # exit
        return



'''!
    Parse output of command, are storing in the buffer, parsers.

    \param commandFinished If command already are finished, processing while
    buffer will not be empty. If not finished - wait for further output.
'''
def parseOutput(self, commandFinished ):
    bool finished

    do
        # Fill string buffer
        while ( mBuffer.canReadLine() and mLinesInStringBuffer < MAX_LINES )

            mStringBuffer.append( QString.fromLocal8Bit( mBuffer.readLine() ) )
            mLinesInStringBuffer ++


        if  not mLinesInStringBuffer :
            return

        finished = True
        linesToRemove = 0

        #try all parsers
        for parserName in mCurrentParsers:
            parser = mParsers.value( parserName )

            if  not parser :
                qWarning() << "Invalid parser" << parserName
                continue; #for


            linesToRemove =  parser.processParsing( &mStringBuffer )

            if  linesToRemove :
                break; #for


        if ( linesToRemove == 0 or commandFinished ) #need to remove one
            linesToRemove = 1

        if  not linesToRemove :
            continue; # do-while

        finished = False; #else one iteration of do-while after it

        #removing of lines
        mLinesInStringBuffer -= linesToRemove
        posEnd = 0

        while ( linesToRemove-- )
            posEnd = mStringBuffer.indexOf( '\n', posEnd ) +1

        mStringBuffer.remove( 0, posEnd )

    while ( not finished and mLinesInStringBuffer )


