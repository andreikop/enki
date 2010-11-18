'''***************************************************************************
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
***************************************************************************'''
'''!
    \file MessageBoxDocks.cpp
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, KOPATS
    \brief Implementation of MessageBoxDocks class
'''

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

'''!
    Constructor of class

    Installs plugin to IDE, GUI, self to signals from sources
    on informations.

    \param parent Parent object
'''
MessageBoxDocks.MessageBoxDocks( QObject* parent )
    : QObject( parent )
    # create docks
    mBuildStep = UIBuildStep
    mOutput = UIOutput
    mCommand = UICommand
    mStepModel = pConsoleManagerStepModel( self )
    mBuildStep.lvBuildSteps.setModel( mStepModel )
    
    # set defaultshortcuts
    pActionsManager.setDefaultShortcut( mBuildStep.toggleViewAction(), QKeySequence( "F9" ) )
    pActionsManager.setDefaultShortcut( mOutput.toggleViewAction(), QKeySequence( "F10" ) )
    pActionsManager.setDefaultShortcut( mCommand.toggleViewAction(), QKeySequence( "F11" ) )
    
    # connections
    mBuildStep.lvBuildSteps.activated.connect(self.lvBuildSteps_activated)
    mOutput.cbRawCommand.lineEdit().returnPressed.connect(self.cbRawCommand_returnPressed)
    MonkeyCore.consoleManager().commandError.connect(self.commandError)
    MonkeyCore.consoleManager().commandFinished.connect(self.commandFinished)
    MonkeyCore.consoleManager().commandReadyRead.connect(self.commandReadyRead)
    MonkeyCore.consoleManager().commandStarted.connect(self.commandStarted)
    MonkeyCore.consoleManager().commandStateChanged.connect(self.commandStateChanged)
    MonkeyCore.consoleManager().commandSkipped.connect(self.commandSkipped)
    MonkeyCore.consoleManager().newStepAvailable.connect(self.appendStep)
    MonkeyCore.consoleManager().newStepsAvailable.connect(self.appendSteps)


'''!
    Destuctor of class

    Deletes docks of Message Box
'''
MessageBoxDocks.~MessageBoxDocks()
    delete mBuildStep
    delete mOutput
    delete mCommand


'''!
    Make text colored by adding HTML tags before and after text

    \param s Source string
    \param c Desired color
    \return String, color tags at start and end
'''
def colourText(self, s, c ):
{ return QString( "<font color=\"%1\">%2</font>" ).arg( c.name() ).arg( s );

'''!
    Append text to Output dock
    \param s Text to append
'''
def appendOutput(self, s ):
    # we check if the scroll bar is at maximum
    p = mOutput.tbOutput.verticalScrollBar().value()
    b = p == mOutput.tbOutput.verticalScrollBar().maximum()
    # appendOutput text
    mOutput.tbOutput.moveCursor( QTextCursor.End )
    # QPlainTextEdit does not have an insertHtml member
    cursor = mOutput.tbOutput.textCursor()
    cursor.insertHtml( s +"<br />" )
    mOutput.tbOutput.setTextCursor( cursor )
    # if scrollbar is at maximum, it
    mOutput.tbOutput.verticalScrollBar().setValue( b ? mOutput.tbOutput.verticalScrollBar().maximum() : p )


'''!
    Append text to Commands dock
    \param s Text to append
'''
def appendLog(self, s ):
    # we check if the scroll bar is at maximum
    p = mCommand.teLog.verticalScrollBar().value()
    b = p == mCommand.teLog.verticalScrollBar().maximum()
    # appendOutput text
    mCommand.teLog.moveCursor( QTextCursor.End )
    # QPlainTextEdit does not have an insertHtml member
    cursor = mCommand.teLog.textCursor()
    cursor.insertHtml( s +"<br />" )
    mCommand.teLog.setTextCursor( cursor )
    # if scrollbar is at maximum, it
    mCommand.teLog.verticalScrollBar().setValue( b ? mCommand.teLog.verticalScrollBar().maximum() : p )


'''!
    Append text to Commands dock, will be displayed in the box of stars

    Example:
    *******************************************************
    Here is your text
    *******************************************************
    \param s String to append
    \param c Color of string
'''
def appendInBox(self, s, c ):
    appendLog( colourText( "********************************************************************************", c ) )
    appendLog( s )
    appendLog( colourText( "********************************************************************************", c ) )


'''!
    Append build step to Build Steps dock
    \param s Build step to append
'''
def appendStep(self, step ):
    sb = mBuildStep.lvBuildSteps.verticalScrollBar()
     atBottom = sb.value() == sb.maximum()
    
    # update steps
    mStepModel.appendStep( step ); # append row to the model
    
    if  atBottom :
        mBuildStep.lvBuildSteps.scrollToBottom()



def appendSteps(self, steps ):
    sb = mBuildStep.lvBuildSteps.verticalScrollBar()
     atBottom = sb.value() == sb.maximum()
    
    # update steps
    mStepModel.appendSteps( steps ); # append rows to the model
    
    if  atBottom :
        mBuildStep.lvBuildSteps.scrollToBottom()



'''!
    Show Build Steps dock
'''
def showBuild(self):
    # show it if need
    if  not mBuildStep.isVisible() :
        mBuildStep.show()


'''!
    Show Output dock
'''
def showOutput(self):
    # show it if need
    if  not mOutput.isVisible() :
        mOutput.show()


'''!
    Show Log dock
'''
def showLog(self):
    # show it if need
    if  not mCommand.isVisible() :
        mCommand.show()


'''!
    Show next warning on Build Steps dock
'''
def showNextWarning(self):
     selectedIndex = mBuildStep.lvBuildSteps.selectionModel().selectedIndexes().value( 0 )
     index = mStepModel.nextWarning( selectedIndex )
    
    if  not index.isValid() :
        return

    
    # show it if need
    if  not mBuildStep.isVisible() :
        mBuildStep.show()

    
    mBuildStep.lvBuildSteps.setCurrentIndex( index )
    lvBuildSteps_activated( index )


'''!
    Show next error on Build Steps dock
'''
def showNextError(self):
     selectedIndex = mBuildStep.lvBuildSteps.selectionModel().selectedIndexes().value( 0 )
     index = mStepModel.nextError( selectedIndex )
    
    if  not index.isValid() :
        return

    
    # show it if need
    if  not mBuildStep.isVisible() :
        mBuildStep.show()

    
    mBuildStep.lvBuildSteps.setCurrentIndex( index )
    lvBuildSteps_activated( index )


'''!
    Handler of pressing on step in the Build Steps dock

    Trying to open file/line according to step in the editor
    If there are more than one file, possible are target file, (same name,
    but different path) - user will asked, file should be opened
'''
def lvBuildSteps_activated(self, index ):
    # get filename
     itemStep = mStepModel.step( index )
    fn = itemStep.roleValue( pConsoleManagerStep.FileNameRole ).toString()
    qDebug() << "fn " << fn

    # cancel if no file
    if  fn.isEmpty() :
        return


    project = MonkeyCore.fileManager().currentProject()
    topLevelProject = project ? project.topLevelProject() : 0

    if  project and QFileInfo( fn ).isRelative() :
        filePath = project.filePath( fn )

        if  QFile.exists( filePath ) :
            fn = filePath

        elif  topLevelProject :
            filePath = topLevelProject.filePath( fn )

            if  QFile.exists( filePath ) :
                fn = filePath




    if  not QFile.exists( fn ) or QFileInfo( fn ).isRelative() :
        if  topLevelProject :
            findFile = fn
            files = topLevelProject.findFile( findFile )

            switch ( files.count() )
                case 0:
                    fn.clear()
                    break
                case 1:
                    fn = files.at( 0 ).absoluteFilePath()
                    break
                default:
                    UIXUPFindFiles dlg( findFile, mBuildStep.parentWidget().window() )
                    dlg.setFiles( files, topLevelProject.path() )
                    fn.clear()

                    if  dlg.exec() == QDialog.Accepted :
                        fn = dlg.selectedFile()


                    break





    if  QFileInfo( fn ).isRelative() :
        qWarning( "Can't open relative file: %s", fn.toLocal8Bit().constData() )
        return


    if  QFile.exists( fn ) :
         codec = project ? project.temporaryValue( "codec" ).toString() : pMonkeyStudio.defaultCodec()
         position = itemStep.roleValue( pConsoleManagerStep.PositionRole ).toPoint()
        qWarning() << "point" << position
        MonkeyCore.fileManager().goToLine( fn, position, codec )



'''!
    Handler of pressing return in the edit of Raw Command. Executes command
    using console manager
'''
def cbRawCommand_returnPressed(self):
    # send command
    MonkeyCore.consoleManager().sendRawCommand( mOutput.cbRawCommand.currentText() )
    # clear lineedit
    mOutput.cbRawCommand.setCurrentIndex( -1 )


'''!
    Handler of finishing command with error. Prints information about error
    to Commands dock
    \param c Command, are finished
    \param e Error type
'''
def commandError(self, command, error ):
    QString s( tr( "* Error            : '%1'<br />" ).arg( colourText( command.text() ) ) )
    s.append( tr( "* Command          : %1<br />" ).arg( colourText( command.command() ) ) )
    s.append( tr( "* Arguments        : %1<br />" ).arg( colourText( command.arguments() ) ) )
    s.append( tr( "* Working Directory: %1<br />" ).arg( colourText( command.workingDirectory() ) ) )
    s.append( tr( "* Error            : #%1<br />" ).arg( colourText( QString.number( error ) ) ) )
    s.append( colourText( pConsoleManager.errorToString( error ), Qt.darkGreen ) )

    # appendOutput to console log
    appendInBox( colourText( s, Qt.blue ), Qt.red )
    
    # append finish/error step
    pConsoleManagerStep.Data data
    data[ pConsoleManagerStep.TypeRole ] = pConsoleManagerStep.Finish
    data[ Qt.DisplayRole ] = pConsoleManager.errorToString( error )
    appendStep( pConsoleManagerStep( data ) )


'''!
    Handler of finishing command

    Prints information about exit status to Commands tab
    \param c Finished command
    \param exitCode Exit code of process
    \param e Exit status of process
'''
def commandFinished(self, c, exitCode, e ):
    QString s( tr( "* Finished   : '%1'<br />" ).arg( colourText( c.text() ) ) )
    s.append( tr( "* Exit Code  : #%1<br />" ).arg( colourText( QString.number( exitCode ) ) ) )
    s.append( tr( "* Status Code: #%1<br />" ).arg( colourText( QString.number( e ) ) ) )
    #
    if e == QProcess.NormalExit and exitCode == 0:
        s.append( colourText( tr( "The process exited normally." ), Qt.darkGreen ) )
    elif e == QProcess.CrashExit:
        s.append( colourText( tr( "The process crashed." ), Qt.darkGreen ) )
    else:
        s.append( colourText( tr( "The exited with exit code %1" ).arg(exitCode), Qt.darkGreen ) )

    # appendOutput to console log
    appendInBox( colourText( s, Qt.blue ), Qt.red )
    
    # append finish step
    pConsoleManagerStep.Data data
    data[ pConsoleManagerStep.TypeRole ] = pConsoleManagerStep.Finish
    
    # add finish step
    if exitCode != 0:
        data[ Qt.DisplayRole ] = tr("Process finished with exit code %1").arg(exitCode)

    
    appendStep( pConsoleManagerStep( data ) )


'''!
    Handler of Ready Read event from runned command.

    Appends text, from process to Output dock
    \param a Text in the QByteArray format
'''
def commandReadyRead(self,   pCommand&, a ):
    # we check if the scroll bar is at maximum
    sb = mOutput.tbOutput.verticalScrollBar()
     oldValue = sb.value()
    atBottom = oldValue == sb.maximum()
    
    # appendOutput log
    mOutput.tbOutput.moveCursor( QTextCursor.End )
    '''
    cursor = mOutput.tbOutput.textCursor()
    format = cursor.blockCharFormat()
    if  format.foreground().color() != QColor( Qt.black ) :
        format.setForeground( QBrush( Qt.black ) )
        cursor.setBlockCharFormat( format )
        mOutput.tbOutput.setTextCursor( cursor )

    '''
    mOutput.tbOutput.insertPlainText( QTextCodec.codecForLocale().toUnicode( a ) )
    
    # restore position
    sb.setValue( atBottom ? sb.maximum() : oldValue )


'''!
    Handler of Command Started event

    Prints information about start to Commands dock
    \param c Command, are started
'''
def commandStarted(self, c ):
    QString s( tr( "* Started          : '%1'<br />" ).arg( colourText( c.text() ) ) )
    s.append( tr( "* Command          : %1<br />" ).arg( colourText( c.command() ) ) )
    s.append( tr( "* Arguments        : %1<br />" ).arg( colourText( c.arguments() ) ) )
    s.append( tr( "* Working Directory: %1" ).arg( colourText( c.workingDirectory() ) ) )
    # appendOutput to console log
    appendInBox( colourText( s, Qt.blue ), Qt.red )


'''!
    Handler of State Changed event from executed process.

    Prints information about change to Commands dock
    \param c Command
    \param s State of process
'''
def commandStateChanged(self, c, s ):
    QString ss
    switch ( s )
        case QProcess.NotRunning:
            ss = tr( "Not Running" )
            break
        case QProcess.Starting:
            ss = tr( "Starting" )
            # clear all tabs
            mStepModel.clear()
            mOutput.tbOutput.clear()
            mCommand.teLog.clear()
            break
        case QProcess.Running:
            ss = tr( "Running" )
            break

    # appendOutput to console log
    appendOutput( colourText( tr( "*** State changed to %1" ).arg( ss ), Qt.gray ) )
    appendLog( colourText( tr( "*** State changed to #%1 (%2) for command: '%3'" ).arg( s ).arg( ss ).arg( c.text() ), Qt.gray ) )


'''!
    Handler of Command Skipped event.

    Prints information to Commands dock
    \param c Command, was skipped
'''
def commandSkipped(self, c ):
    QString s( tr( "* Skipped          : '%1'<br />" ).arg( colourText( c.text() ) ) )
    s.append( tr( "* Command          : %1<br />" ).arg( colourText( c.command() ) ) )
    s.append( tr( "* Arguments        : %1<br />" ).arg( colourText( c.arguments() ) ) )
    s.append( tr( "* Working Directory: %1" ).arg( colourText( c.workingDirectory() ) ) )
    s.append( colourText( tr( "The command has been skipped due to previous error." ), Qt.darkGreen ) )
    # appendOutput to console log
    appendInBox( colourText( s, Qt.blue ), Qt.red )

