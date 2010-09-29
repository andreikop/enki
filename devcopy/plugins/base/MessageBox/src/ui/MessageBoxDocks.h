'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, 
**             Andrei KOPATS aka hlamer <hlamer at tut by>
**                
** Project   : Monkey Studio Base Plugins
** FileName  : MessageBoxDocs.h
** Date      : 2008-01-14T00:40:08
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
    \file MessageBoxDocks.h
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, KOPATS
    \brief Header of MessageBoxDocks class
    
    File also contains classes of tabs of Message Box
    MessageBox
'''

#ifndef MESSAGEBOXDOCKS_H
#define MESSAGEBOXDOCKS_H

#include "ui_UIBuildStep.h"
#include "ui_UIOutput.h"
#include "ui_UICommand.h"

#include <objects/pIconManager.h>
#include <consolemanager/pConsoleManager.h>
#include <widgets/pDockWidgetTitleBar.h>
#include <coremanager/MonkeyCore.h>
#include <widgets/pMenuBar.h>

class pConsoleManagerStepModel

'''!
    Implementation of Build Steps tab of Message box
'''
class UIBuildStep : public pDockWidget, Ui.UIBuildStep
public:
    UIBuildStep( parent = 0 )
        : pDockWidget( parent )
        setObjectName( metaObject().className() )
        
        setupUi( self )
        lvBuildSteps.setAttribute( Qt.WA_MacShowFocusRect, False )
        lvBuildSteps.setAttribute( Qt.WA_MacSmallSize )
        
        titleBar().addAction( MonkeyCore.menuBar().action( "mView/aShowNextWarning" ), 0 )
        titleBar().addAction( MonkeyCore.menuBar().action( "mView/aShowNextError" ), 1 )
        titleBar().addSeparator( 2 )



'''!
    Implementation of Output tab of Message box
'''
class UIOutput : public pDockWidget, Ui.UIOutput
public:
    UIOutput( parent = 0 )
        : pDockWidget( parent )
        setObjectName( metaObject().className() )
        setupUi( self )
        lRawCommand.setAttribute( Qt.WA_MacShowFocusRect, False )
        lRawCommand.setAttribute( Qt.WA_MacSmallSize )
        cbRawCommand.setAttribute( Qt.WA_MacShowFocusRect, False )
        cbRawCommand.setAttribute( Qt.WA_MacSmallSize )
        tbOutput.setAttribute( Qt.WA_MacShowFocusRect, False )
        tbOutput.setAttribute( Qt.WA_MacSmallSize )



'''!
    Implementation of Commands tab of Message box
'''
class UICommand : public pDockWidget, Ui.UICommand
public:
    UICommand( parent = 0 )
        : pDockWidget( parent )
        setObjectName( metaObject().className() )
        setupUi( self )
        teLog.setAttribute( Qt.WA_MacShowFocusRect, False )
        teLog.setAttribute( Qt.WA_MacSmallSize )



'''!
    Implementation of GUI of MessageBox plugin
    
    Manages tabs, functionality of plugin. Appends and removes 
    information from docks, with signals from sources of information)
    Allows to show some tab of message box
'''
class MessageBoxDocks : public QObject
    Q_OBJECT
    friend class MessageBox
    
public:
    MessageBoxDocks( parent = 0 )
    ~MessageBoxDocks()
    
    QString colourText(  QString&,  QColor& = Qt.black )

protected:
    UIBuildStep* mBuildStep
    UIOutput* mOutput
    UICommand* mCommand
    pConsoleManagerStepModel* mStepModel

public slots:
    void appendOutput(  QString& )
    void appendLog(  QString& )
    void appendInBox(  QString&,  QColor& = Qt.red )
    void appendStep(  pConsoleManagerStep& step )
    void appendSteps(  pConsoleManagerStepList& steps )
    void showBuild()
    void showOutput()
    void showLog()
    void showNextWarning()
    void showNextError()

protected slots:
    void lvBuildSteps_activated(  QModelIndex& index )
    void cbRawCommand_returnPressed()
    void commandError(  pCommand& command, error )
    void commandFinished(  pCommand& command, exitCode, exitStatus )
    void commandReadyRead(  pCommand& command, data )
    void commandStarted(  pCommand& command )
    void commandStateChanged(  pCommand& command, state )
    void commandSkipped(  pCommand& command )


#endif # MESSAGEBOXDOCKS_H
