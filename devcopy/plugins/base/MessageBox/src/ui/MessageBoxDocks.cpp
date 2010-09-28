/****************************************************************************
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
****************************************************************************/
/*!
    \file MessageBoxDocks.cpp
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, Andrei KOPATS
    \brief Implementation of MessageBoxDocks class
*/

#include "MessageBoxDocks.h"

#include <QScrollBar>
#include <QLineEdit>

#include <coremanager/MonkeyCore.h>
#include <workspace/pWorkspace.h>
#include <workspace/pAbstractChild.h>
#include <workspace/pFileManager.h>
#include <xupmanager/core/XUPProjectItem.h>
#include <xupmanager/gui/UIXUPFindFiles.h>
#include <consolemanager/pConsoleManagerStepModel.h>

#include <QDebug>

/*!
    Constructor of class

    Installs plugin to IDE, creates GUI, connects self to signals from sources
    on informations.

    \param parent Parent object
*/
MessageBoxDocks::MessageBoxDocks( QObject* parent )
    : QObject( parent )
{
    // create docks
    mBuildStep = new UIBuildStep;
    mOutput = new UIOutput;
    mCommand = new UICommand;
    mStepModel = new pConsoleManagerStepModel( this );
    mBuildStep->lvBuildSteps->setModel( mStepModel );
    
    // set defaultshortcuts
    pActionsManager::setDefaultShortcut( mBuildStep->toggleViewAction(), QKeySequence( "F9" ) );
    pActionsManager::setDefaultShortcut( mOutput->toggleViewAction(), QKeySequence( "F10" ) );
    pActionsManager::setDefaultShortcut( mCommand->toggleViewAction(), QKeySequence( "F11" ) );
    
    // connections
    connect( mBuildStep->lvBuildSteps, SIGNAL( activated( const QModelIndex& ) ), this, SLOT( lvBuildSteps_activated( const QModelIndex& ) ) );
    connect( mOutput->cbRawCommand->lineEdit(), SIGNAL( returnPressed() ), this, SLOT( cbRawCommand_returnPressed() ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( commandError( const pCommand&, QProcess::ProcessError ) ), this, SLOT( commandError( const pCommand&, QProcess::ProcessError ) ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( commandFinished( const pCommand&, int, QProcess::ExitStatus ) ), this, SLOT( commandFinished( const pCommand&, int, QProcess::ExitStatus ) ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( commandReadyRead( const pCommand&, const QByteArray& ) ), this, SLOT( commandReadyRead( const pCommand&, const QByteArray& ) ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( commandStarted( const pCommand& ) ), this, SLOT( commandStarted( const pCommand& ) ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( commandStateChanged( const pCommand&, QProcess::ProcessState ) ), this, SLOT( commandStateChanged( const pCommand&, QProcess::ProcessState ) ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( commandSkipped( const pCommand& ) ), this, SLOT( commandSkipped( const pCommand& ) ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( newStepAvailable( const pConsoleManagerStep& ) ), this, SLOT( appendStep( const pConsoleManagerStep& ) ) );
    connect( MonkeyCore::consoleManager(), SIGNAL( newStepsAvailable( const pConsoleManagerStepList& ) ), this, SLOT( appendSteps( const pConsoleManagerStepList& ) ) );
}

/*!
    Destuctor of class

    Deletes docks of Message Box
*/
MessageBoxDocks::~MessageBoxDocks()
{
    delete mBuildStep;
    delete mOutput;
    delete mCommand;
}

/*!
    Make text colored by adding HTML tags before and after text

    \param s Source string
    \param c Desired color
    \return String, containing color tags at start and end
*/
QString MessageBoxDocks::colourText( const QString& s, const QColor& c )
{ return QString( "<font color=\"%1\">%2</font>" ).arg( c.name() ).arg( s ); }

/*!
    Append text to Output dock
    \param s Text to append
*/
void MessageBoxDocks::appendOutput( const QString& s )
{
    // we check if the scroll bar is at maximum
    int p = mOutput->tbOutput->verticalScrollBar()->value();
    bool b = p == mOutput->tbOutput->verticalScrollBar()->maximum();
    // appendOutput text
    mOutput->tbOutput->moveCursor( QTextCursor::End );
    // QPlainTextEdit does not have an insertHtml member
    QTextCursor cursor = mOutput->tbOutput->textCursor();
    cursor.insertHtml( s +"<br />" );
    mOutput->tbOutput->setTextCursor( cursor );
    // if scrollbar is at maximum, increase it
    mOutput->tbOutput->verticalScrollBar()->setValue( b ? mOutput->tbOutput->verticalScrollBar()->maximum() : p );
}

/*!
    Append text to Commands dock
    \param s Text to append
*/
void MessageBoxDocks::appendLog( const QString& s )
{
    // we check if the scroll bar is at maximum
    int p = mCommand->teLog->verticalScrollBar()->value();
    bool b = p == mCommand->teLog->verticalScrollBar()->maximum();
    // appendOutput text
    mCommand->teLog->moveCursor( QTextCursor::End );
    // QPlainTextEdit does not have an insertHtml member
    QTextCursor cursor = mCommand->teLog->textCursor();
    cursor.insertHtml( s +"<br />" );
    mCommand->teLog->setTextCursor( cursor );
    // if scrollbar is at maximum, increase it
    mCommand->teLog->verticalScrollBar()->setValue( b ? mCommand->teLog->verticalScrollBar()->maximum() : p );
}

/*!
    Append text to Commands dock, which will be displayed in the box of stars

    Example:
    *******************************************************
    Here is your text
    *******************************************************
    \param s String to append
    \param c Color of string
*/
void MessageBoxDocks::appendInBox( const QString& s, const QColor& c )
{
    appendLog( colourText( "********************************************************************************", c ) );
    appendLog( s );
    appendLog( colourText( "********************************************************************************", c ) );
}

/*!
    Append build step to Build Steps dock
    \param s Build step to append
*/
void MessageBoxDocks::appendStep( const pConsoleManagerStep& step )
{
    QScrollBar* sb = mBuildStep->lvBuildSteps->verticalScrollBar();
    const bool atBottom = sb->value() == sb->maximum();
    
    // update steps
    mStepModel->appendStep( step ); // append row to the model
    
    if ( atBottom )
    {
        mBuildStep->lvBuildSteps->scrollToBottom();
    }
}

void MessageBoxDocks::appendSteps( const pConsoleManagerStepList& steps )
{
    QScrollBar* sb = mBuildStep->lvBuildSteps->verticalScrollBar();
    const bool atBottom = sb->value() == sb->maximum();
    
    // update steps
    mStepModel->appendSteps( steps ); // append rows to the model
    
    if ( atBottom )
    {
        mBuildStep->lvBuildSteps->scrollToBottom();
    }
}

/*!
    Show Build Steps dock
*/
void MessageBoxDocks::showBuild()
{
    // show it if need
    if ( !mBuildStep->isVisible() )
        mBuildStep->show();
}

/*!
    Show Output dock
*/
void MessageBoxDocks::showOutput()
{
    // show it if need
    if ( !mOutput->isVisible() )
        mOutput->show();
}

/*!
    Show Log dock
*/
void MessageBoxDocks::showLog()
{
    // show it if need
    if ( !mCommand->isVisible() )
        mCommand->show();
}

/*!
    Show next warning on Build Steps dock
*/
void MessageBoxDocks::showNextWarning()
{
    const QModelIndex selectedIndex = mBuildStep->lvBuildSteps->selectionModel()->selectedIndexes().value( 0 );
    const QModelIndex index = mStepModel->nextWarning( selectedIndex );
    
    if ( !index.isValid() )
    {
        return;
    }
    
    // show it if need
    if ( !mBuildStep->isVisible() )
    {
        mBuildStep->show();
    }
    
    mBuildStep->lvBuildSteps->setCurrentIndex( index );
    lvBuildSteps_activated( index );
}

/*!
    Show next error on Build Steps dock
*/
void MessageBoxDocks::showNextError()
{
    const QModelIndex selectedIndex = mBuildStep->lvBuildSteps->selectionModel()->selectedIndexes().value( 0 );
    const QModelIndex index = mStepModel->nextError( selectedIndex );
    
    if ( !index.isValid() )
    {
        return;
    }
    
    // show it if need
    if ( !mBuildStep->isVisible() )
    {
        mBuildStep->show();
    }
    
    mBuildStep->lvBuildSteps->setCurrentIndex( index );
    lvBuildSteps_activated( index );
}

/*!
    Handler of pressing on step in the Build Steps dock

    Trying to open file/line according to step in the editor
    If there are more than one file, which possible are target file, (same name,
    but different path) - user will asked, which file should be opened
*/
void MessageBoxDocks::lvBuildSteps_activated( const QModelIndex& index )
{
    // get filename
    const pConsoleManagerStep itemStep = mStepModel->step( index );
    QString fn = itemStep.roleValue( pConsoleManagerStep::FileNameRole ).toString();
    qDebug() << "fn " << fn;

    // cancel if no file
    if ( fn.isEmpty() )
    {
        return;
    }

    XUPProjectItem* project = MonkeyCore::fileManager()->currentProject();
    XUPProjectItem* topLevelProject = project ? project->topLevelProject() : 0;

    if ( project && QFileInfo( fn ).isRelative() )
    {
        QString filePath = project->filePath( fn );

        if ( QFile::exists( filePath ) )
        {
            fn = filePath;
        }
        else if ( topLevelProject )
        {
            filePath = topLevelProject->filePath( fn );

            if ( QFile::exists( filePath ) )
            {
                fn = filePath;
            }
        }
    }

    if ( !QFile::exists( fn ) || QFileInfo( fn ).isRelative() )
    {
        if ( topLevelProject )
        {
            QString findFile = fn;
            QFileInfoList files = topLevelProject->findFile( findFile );

            switch ( files.count() )
            {
                case 0:
                    fn.clear();
                    break;
                case 1:
                    fn = files.at( 0 ).absoluteFilePath();
                    break;
                default:
                {
                    UIXUPFindFiles dlg( findFile, mBuildStep->parentWidget()->window() );
                    dlg.setFiles( files, topLevelProject->path() );
                    fn.clear();

                    if ( dlg.exec() == QDialog::Accepted )
                    {
                        fn = dlg.selectedFile();
                    }

                    break;
                }
            }
        }
    }

    if ( QFileInfo( fn ).isRelative() )
    {
        qWarning( "Can't open relative file: %s", fn.toLocal8Bit().constData() );
        return;
    }

    if ( QFile::exists( fn ) )
    {
        const QString codec = project ? project->temporaryValue( "codec" ).toString() : pMonkeyStudio::defaultCodec();
        const QPoint position = itemStep.roleValue( pConsoleManagerStep::PositionRole ).toPoint();
        qWarning() << "point" << position;
        MonkeyCore::fileManager()->goToLine( fn, position, codec );
    }
}

/*!
    Handler of pressing return in the edit of Raw Command. Executes command
    using console manager
*/
void MessageBoxDocks::cbRawCommand_returnPressed()
{
    // send command
    MonkeyCore::consoleManager()->sendRawCommand( mOutput->cbRawCommand->currentText() );
    // clear lineedit
    mOutput->cbRawCommand->setCurrentIndex( -1 );
}

/*!
    Handler of finishing command with error. Prints information about error
    to Commands dock
    \param c Command, which are finished
    \param e Error type
*/
void MessageBoxDocks::commandError( const pCommand& command, QProcess::ProcessError error )
{
    QString s( tr( "* Error            : '%1'<br />" ).arg( colourText( command.text() ) ) );
    s.append( tr( "* Command          : %1<br />" ).arg( colourText( command.command() ) ) );
    s.append( tr( "* Arguments        : %1<br />" ).arg( colourText( command.arguments() ) ) );
    s.append( tr( "* Working Directory: %1<br />" ).arg( colourText( command.workingDirectory() ) ) );
    s.append( tr( "* Error            : #%1<br />" ).arg( colourText( QString::number( error ) ) ) );
    s.append( colourText( pConsoleManager::errorToString( error ), Qt::darkGreen ) );

    // appendOutput to console log
    appendInBox( colourText( s, Qt::blue ), Qt::red );
    
    // append finish/error step
    pConsoleManagerStep::Data data;
    data[ pConsoleManagerStep::TypeRole ] = pConsoleManagerStep::Finish;
    data[ Qt::DisplayRole ] = pConsoleManager::errorToString( error );
    appendStep( pConsoleManagerStep( data ) );
}

/*!
    Handler of finishing command

    Prints information about exit status to Commands tab
    \param c Finished command
    \param exitCode Exit code of process
    \param e Exit status of process
*/
void MessageBoxDocks::commandFinished( const pCommand& c, int exitCode, QProcess::ExitStatus e )
{
    QString s( tr( "* Finished   : '%1'<br />" ).arg( colourText( c.text() ) ) );
    s.append( tr( "* Exit Code  : #%1<br />" ).arg( colourText( QString::number( exitCode ) ) ) );
    s.append( tr( "* Status Code: #%1<br />" ).arg( colourText( QString::number( e ) ) ) );
    //
    if (e == QProcess::NormalExit && exitCode == 0)
        s.append( colourText( tr( "The process exited normally." ), Qt::darkGreen ) );
    else if (e == QProcess::CrashExit)
        s.append( colourText( tr( "The process crashed." ), Qt::darkGreen ) );
    else
        s.append( colourText( tr( "The exited with exit code %1" ).arg(exitCode), Qt::darkGreen ) );

    // appendOutput to console log
    appendInBox( colourText( s, Qt::blue ), Qt::red );
    
    // append finish step
    pConsoleManagerStep::Data data;
    data[ pConsoleManagerStep::TypeRole ] = pConsoleManagerStep::Finish;
    
    // add finish step
    if (exitCode != 0)
    {
        data[ Qt::DisplayRole ] = tr("Process finished with exit code %1").arg(exitCode);
    }
    
    appendStep( pConsoleManagerStep( data ) );
}

/*!
    Handler of Ready Read event from runned command.

    Appends text, readed from process to Output dock
    \param a Text in the QByteArray format
*/
void MessageBoxDocks::commandReadyRead( const pCommand&, const QByteArray& a )
{
    // we check if the scroll bar is at maximum
    QScrollBar* sb = mOutput->tbOutput->verticalScrollBar();
    const int oldValue = sb->value();
    bool atBottom = oldValue == sb->maximum();
    
    // appendOutput log
    mOutput->tbOutput->moveCursor( QTextCursor::End );
    /*
    QTextCursor cursor = mOutput->tbOutput->textCursor();
    QTextCharFormat format = cursor.blockCharFormat();
    if ( format.foreground().color() != QColor( Qt::black ) )
    {
        format.setForeground( QBrush( Qt::black ) );
        cursor.setBlockCharFormat( format );
        mOutput->tbOutput->setTextCursor( cursor );
    }
    */
    mOutput->tbOutput->insertPlainText( QTextCodec::codecForLocale()->toUnicode( a ) );
    
    // restore position
    sb->setValue( atBottom ? sb->maximum() : oldValue );
}

/*!
    Handler of Command Started event

    Prints information about start to Commands dock
    \param c Command, which are started
*/
void MessageBoxDocks::commandStarted( const pCommand& c )
{
    QString s( tr( "* Started          : '%1'<br />" ).arg( colourText( c.text() ) ) );
    s.append( tr( "* Command          : %1<br />" ).arg( colourText( c.command() ) ) );
    s.append( tr( "* Arguments        : %1<br />" ).arg( colourText( c.arguments() ) ) );
    s.append( tr( "* Working Directory: %1" ).arg( colourText( c.workingDirectory() ) ) );
    // appendOutput to console log
    appendInBox( colourText( s, Qt::blue ), Qt::red );
}

/*!
    Handler of State Changed event from executed process.

    Prints information about change to Commands dock
    \param c Command
    \param s State of process
*/
void MessageBoxDocks::commandStateChanged( const pCommand& c, QProcess::ProcessState s )
{
    QString ss;
    switch ( s )
    {
        case QProcess::NotRunning:
            ss = tr( "Not Running" );
            break;
        case QProcess::Starting:
            ss = tr( "Starting" );
            // clear all tabs
            mStepModel->clear();
            mOutput->tbOutput->clear();
            mCommand->teLog->clear();
            break;
        case QProcess::Running:
            ss = tr( "Running" );
            break;
    }
    // appendOutput to console log
    appendOutput( colourText( tr( "*** State changed to %1" ).arg( ss ), Qt::gray ) );
    appendLog( colourText( tr( "*** State changed to #%1 (%2) for command: '%3'" ).arg( s ).arg( ss ).arg( c.text() ), Qt::gray ) );
}

/*!
    Handler of Command Skipped event.

    Prints information to Commands dock
    \param c Command, which was skipped
*/
void MessageBoxDocks::commandSkipped( const pCommand& c )
{
    QString s( tr( "* Skipped          : '%1'<br />" ).arg( colourText( c.text() ) ) );
    s.append( tr( "* Command          : %1<br />" ).arg( colourText( c.command() ) ) );
    s.append( tr( "* Arguments        : %1<br />" ).arg( colourText( c.arguments() ) ) );
    s.append( tr( "* Working Directory: %1" ).arg( colourText( c.workingDirectory() ) ) );
    s.append( colourText( tr( "The command has been skipped due to previous error." ), Qt::darkGreen ) );
    // appendOutput to console log
    appendInBox( colourText( s, Qt::blue ), Qt::red );
}
