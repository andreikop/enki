'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pFileManager.h
** Date      : 2008-01-14T00:37:20
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
#ifndef PFILEMANAGER_H
#define PFILEMANAGER_H

#include <objects/MonkeyExport.h>

#include <QObject>
#include <QPoint>
#include <QMap>
#include <QStringList>

class pAbstractChild
class XUPProjectItem
class XUPItem
class MkSShellInterpreter

class Q_MONKEY_EXPORT pFileManager : public QObject
    Q_OBJECT
    friend class MonkeyCore
    friend class pWorkspace

public:
    # associations related members
    void clearCommand(  type = QString.null )
    void addCommand(  QString& type, suffixes )
    void addCommand(  QString& type, suffix )
    void setCommand(  QString& type, suffixes )
    void setCommand(  QString& type, suffix )
    void removeCommand(  QString& type, suffixes )
    void removeCommand(  QString& type, suffix )
     QMap<QString, associations()
    QStringList associations(  QString& type )
    void generateScript()
    
    # Returns pointer to editor, file is opened. Null - if not opened
    pAbstractChild* openedDocument(  QString& fileName )
    # return a file buffer, file is open, current live buffer is return, the physically one.
    QString fileBuffer(  QString& fileName, codec, ok )
    # compute the modified buffers list
    void computeModifiedBuffers()

    XUPProjectItem* currentProject()
    QString currentProjectFile()
    QString currentProjectPath()
    pAbstractChild* currentDocument()
    QString currentDocumentFile()
    QString currentDocumentPath()
    XUPItem* currentItem()
    QString currentItemFile()
    QString currentItemPath()

protected:
    QMap<QString, mAssociations; # language, suffixes
    
    pFileManager( parent = 0 )
    
    void initializeInterpreterCommands()
    static QString commandInterpreter(  QString& command, arguments, result, interpreter, data )

public slots:
    pAbstractChild* openFile(  QString& fileName, codec )
    void closeFile(  QString& fileName )
    void goToLine(  QString& fileName, position, codec, selectionLength = 0 )
    void openProject(  QString& fileName, codec )

signals:
    # files
    void documentOpened( pAbstractChild* document )
    void documentChanged( pAbstractChild* document )
    void documentModifiedChanged( pAbstractChild* document, modified )
    void documentAboutToClose( pAbstractChild* document )
    void documentClosed( pAbstractChild* document )
    void documentReloaded( pAbstractChild* document )
    void currentDocumentChanged( pAbstractChild* document )
    void buffersChanged(  QMap<QString, entries )
    # projects
    void opened( XUPProjectItem* project )
    void aboutToClose( XUPProjectItem* project )
    void currentChanged( XUPProjectItem* project )
    void currentChanged( XUPProjectItem* currentProject, previousProject )


#endif # PFILEMANAGER_H
