'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pCommand.h
** Date      : 2008-01-14T00:36:49
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
    \file pCommand.h
    \date 2008-01-14T00:36:50
    \author Filipe AZEVEDO aka Nox PasNox <pasnox@gmail.com>
    \brief Header for pCommand
'''
#ifndef PCOMMAND_H
#define PCOMMAND_H

#include <objects/MonkeyExport.h>

#include <QStringList>
#include <QVariant>

class XUPProjectItem

struct Q_MONKEY_EXPORT pCommandTargetExecution
    pCommandTargetExecution()
        isActive = False
        targetType = -1
        platformType = -1


    bool operator==(  pCommandTargetExecution& other )
        return isActive == other.isActive and
               targetType == other.targetType and platformType == other.platformType


    bool isActive
    int targetType
    int platformType


'''!
    Container for storing console command

    pCommand can store command line for executing command, dirrectory,
    options of execution of command, define parsers, could be used
    for executing, also can remember project, which command is
    executing
'''
class Q_MONKEY_EXPORT pCommand
public:
    pCommand()
        mSkipOnError = False
        mTryAllParsers = False
        mProject = 0


    pCommand(  QString& t, c, a, b = False, p = QStringList(), d = QString.null, bb = False )
        mText = t
        mCommand = c
        mArguments = a
        mSkipOnError = b
        mParsers = p
        mWorkingDirectory = d
        mTryAllParsers = bb
        mProject = 0

    ~pCommand()
    bool isValid()
        return not text().isEmpty() and ( not command().isEmpty() or mTargetExecution.isActive )


    bool operator==(  pCommand& t )
        return mText == t.mText and mCommand == t.mCommand and mArguments == t.mArguments and
               mWorkingDirectory == t.mWorkingDirectory and mParsers == t.mParsers and mSkipOnError == t.mSkipOnError and
               mTryAllParsers == t.mTryAllParsers and mUserData == t.mUserData and mProject == t.mProject and
               mTargetExecution == t.mTargetExecution


    QString text()
        return mText

    QString command()
        return mCommand

    QString arguments()
        return mArguments

    QString workingDirectory()
        return mWorkingDirectory

    QStringList parsers()
        return mParsers

    bool skipOnError()
        return mSkipOnError

    bool tryAllParsers()
        return mTryAllParsers

    QVariant userData()
        return mUserData

    XUPProjectItem* project()
        return mProject

    pCommandTargetExecution& targetExecution()
        return mTargetExecution


    void setText(  QString& s )
        mText = s

    void setCommand(  QString& s )
        mCommand = s

    void setArguments(  QString& s )
        mArguments = s

    void setWorkingDirectory(  QString& s )
        mWorkingDirectory = s

    void addParser(  QString& p )
        if ( not mParsers.contains( p ) ) mParsers << p

    void setParsers(  QStringList& p )
        mParsers = p

    void addParsers(  QStringList& p )
        for s in p: addParser( s )

    void setSkipOnError( bool b )
        mSkipOnError = b

    void setTryAllParsers( bool b )
        mTryAllParsers = b

    void setUserData(  QVariant& data )
        mUserData = data

    void setProject( XUPProjectItem* project )
        mProject = project


    QString toString()
        QString s
        s += QString( "mText: %1\n" ).arg( mText )
        s += QString( "mCommand: %1\n" ).arg( mCommand )
        s += QString( "mArguments: %1\n" ).arg( mArguments )
        s += QString( "mWorkingDirectory: %1\n" ).arg( mWorkingDirectory )
        s += QString( "mSkipOnError: %1\n" ).arg( mSkipOnError )
        s += QString( "mParsers: %1\n" ).arg( mParsers.join( " " ) )
        s += QString( "mTryAllParsers: %1\n" ).arg( mTryAllParsers )
        s += QString( "mUserData: %1\n" ).arg( mUserData.toString() )
        s += QString( "mProject: %1" ).arg( (quintptr)mProject )
        return s


    void debug()
        qWarning( "%s", toString().toLocal8Bit().constData() )


protected:
    QString mText;                                 '''*< Comment about command '''
    QString mCommand;                            '''*< Console command '''
    QString mArguments;                            '''*< Arguments '''
    QString mWorkingDirectory;                    '''*< Working dirrectory of process '''
    bool mSkipOnError;                            '''*< Skip command, error ocurred '''
    QStringList mParsers;                        '''*< List of parsers, should be used for command. Position in the list is not ignored '''
    bool mTryAllParsers;                        '''*< Try to use all availible parsers after parsers from list '''
    XUPProjectItem* mProject;                    '''*< Project, which command is executing '''
    QVariant mUserData;                            '''*< User custom placeholder to stock customdata, it's internally used to store commands map '''
    pCommandTargetExecution mTargetExecution;    '''*< Determine if the command is the result of proejct target execution '''


'''!
    List of pCommand objects
'''
typedef QList<pCommand> pCommandList
typedef QMap<QString, pCommandMap

Q_DECLARE_METATYPE( pCommand )
Q_DECLARE_METATYPE( pCommandList )
Q_DECLARE_METATYPE( pCommandMap )
Q_DECLARE_METATYPE( pCommandMap* )

#endif # PCOMMAND_H
