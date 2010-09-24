/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pConsoleManager.h
** Date      : 2008-01-14T00:36:51
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
	\file pConsoleManager.h
	\date 2008-01-14T00:36:50
	\author Filipe AZEVEDO aka Nox PasNox <pasnox@gmail.com>
	\brief Header of pConsoleManager class
*/

#ifndef PCONSOLEMANAGER_H
#define PCONSOLEMANAGER_H

#include <objects/MonkeyExport.h>

#include "pCommand.h"
#include "pConsoleManagerStep.h"
#include "EnvironmentVariablesManager.h"

#include <QProcess>
#include <QBuffer>
#include <QPoint>
#include <QHash>

class AbstractCommandParser;
class QAction;

/*!
	Console Manager provides support of running commands and parsing it's output
	
	It can in series execute commands, inform other systems by signals about 
	starting/stoping of execution command. 
	Output of commands is reading and parsing by availible parsers. Parsers can be
	configured separately for every command
*/
class Q_MONKEY_EXPORT pConsoleManager : public QProcess
{
	Q_OBJECT
	friend class MonkeyCore;
	
public:
	inline pCommand currentCommand() const { return mCommands.value( 0 ); }
	inline QStringList parsersName() const { return mParsers.keys(); }
	inline QAction* stopAction() const { return mStopAction; }
	inline EnvironmentVariablesManager* environmentVariablesManager() const { return &mEnvironmentVariablesManager; }
	
	void addParser( AbstractCommandParser* );
	void removeParser( AbstractCommandParser* );
	void removeParser( const QString& );
	AbstractCommandParser* getParser(const QString& name);
	
	QString quotedString( const QString& );
	QString processInternalVariables( const QString& );
	pCommand processCommand( pCommand );
	pCommand getCommand( const pCommandList&, const QString& );
	pCommandList recursiveCommandList( const pCommandList&, pCommand );
	
	static QString errorToString( QProcess::ProcessError error );

protected:
	int mTimerId;
	QBuffer mBuffer; //All output comming to this buffer
	QString mStringBuffer; //... then by portions to this buffer
	int mLinesInStringBuffer;
	pCommandList mCommands;
	QStringList mCurrentParsers;
	QHash<QString, AbstractCommandParser*> mParsers;
	QAction* mStopAction;
	int mStopAttempt;
	mutable EnvironmentVariablesManager mEnvironmentVariablesManager;

	pConsoleManager( QObject* = 0 );
	~pConsoleManager();
	void timerEvent( QTimerEvent* );

	/*
	Parse output, that are in the mBuffer.   
	*/
	void parseOutput( bool commandFinished );

public slots:
	void sendRawCommand( const QString& );
	void sendRawData( const QByteArray& );
	void stopCurrentCommand();
	void addCommand( const pCommand& );
	void addCommands( const pCommandList& );
	void removeCommand( const pCommand& );
	void removeCommands( const pCommandList& );

private slots:
	void executeProcess();
	void error( QProcess::ProcessError );
	void finished( int, QProcess::ExitStatus );
	void readyRead();
	void started();
	void stateChanged( QProcess::ProcessState );

signals:
	void warning( const QString& message );
	void commandError( const pCommand&, QProcess::ProcessError );
	void commandFinished( const pCommand&, int, QProcess::ExitStatus );
	void commandReadyRead( const pCommand&, const QByteArray& );
	void commandStarted( const pCommand& );
	void commandStateChanged( const pCommand&, QProcess::ProcessState );
	void commandSkipped( const pCommand& );
	void newStepAvailable( const pConsoleManagerStep& );
	void newStepsAvailable( const pConsoleManagerStepList& );
};

#endif // PCONSOLEMANAGER_H
