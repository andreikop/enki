/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pFileManager.h
** Date      : 2008-01-14T00:37:20
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
#ifndef PFILEMANAGER_H
#define PFILEMANAGER_H

#include <objects/MonkeyExport.h>

#include <QObject>
#include <QPoint>
#include <QMap>
#include <QStringList>

class pAbstractChild;
class XUPProjectItem;
class XUPItem;
class MkSShellInterpreter;

class Q_MONKEY_EXPORT pFileManager : public QObject
{
    Q_OBJECT
    friend class MonkeyCore;
    friend class pWorkspace;

public:
    // associations related members
    void clearCommand( const QString& type = QString::null );
    void addCommand( const QString& type, const QStringList& suffixes );
    void addCommand( const QString& type, const QString& suffix );
    void setCommand( const QString& type, const QStringList& suffixes );
    void setCommand( const QString& type, const QString& suffix );
    void removeCommand( const QString& type, const QStringList& suffixes );
    void removeCommand( const QString& type, const QString& suffix );
    const QMap<QString, QStringList>& associations() const;
    QStringList associations( const QString& type ) const;
    void generateScript();
    
    // Returns pointer to editor, if file is opened. Null - if not opened
    pAbstractChild* openedDocument( const QString& fileName ) const;
    // return a file buffer, if file is open, the current live buffer is return, else the physically one.
    QString fileBuffer( const QString& fileName, const QString& codec, bool& ok ) const;
    // compute the modified buffers list
    void computeModifiedBuffers();

    XUPProjectItem* currentProject() const;
    QString currentProjectFile() const;
    QString currentProjectPath() const;
    pAbstractChild* currentDocument() const;
    QString currentDocumentFile() const;
    QString currentDocumentPath() const;
    XUPItem* currentItem() const;
    QString currentItemFile() const;
    QString currentItemPath() const;

protected:
    QMap<QString, QStringList> mAssociations; // language, suffixes
    
    pFileManager( QObject* parent = 0 );
    
    void initializeInterpreterCommands();
    static QString commandInterpreter( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data );

public slots:
    pAbstractChild* openFile( const QString& fileName, const QString& codec );
    void closeFile( const QString& fileName );
    void goToLine( const QString& fileName, const QPoint& position, const QString& codec, int selectionLength = 0 );
    void openProject( const QString& fileName, const QString& codec );

signals:
    // files
    void documentOpened( pAbstractChild* document );
    void documentChanged( pAbstractChild* document );
    void documentModifiedChanged( pAbstractChild* document, bool modified );
    void documentAboutToClose( pAbstractChild* document );
    void documentClosed( pAbstractChild* document );
    void documentReloaded( pAbstractChild* document );
    void currentDocumentChanged( pAbstractChild* document );
    void buffersChanged( const QMap<QString, QString>& entries );
    // projects
    void opened( XUPProjectItem* project );
    void aboutToClose( XUPProjectItem* project );
    void currentChanged( XUPProjectItem* project );
    void currentChanged( XUPProjectItem* currentProject, XUPProjectItem* previousProject );
};

#endif // PFILEMANAGER_H
