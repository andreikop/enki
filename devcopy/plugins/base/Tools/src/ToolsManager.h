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
#ifndef TOOLSMANAGER_H
#define TOOLSMANAGER_H

#include <QApplication>
#include <QVariant>

class MkSShellInterpreter;
class QAction;
class QFileIconProvider;

class ToolsManager : public QObject
{
    Q_OBJECT
    friend class UIToolsEdit;
    friend class UIDesktopTools;

public:
    enum Type
    {
        UserEntry = 0,
        DesktopEntry
    };
    
    struct Tool
    {
        Tool( const QString& _caption, const QString& _fileIcon, const QString& _filePath, const QString& _workingPath,
            bool _desktopEntry = false, bool _useConsoleManager = false )
        {
            caption = _caption;
            fileIcon = _fileIcon;
            filePath = _filePath;
            workingPath = _workingPath;
            desktopEntry = _desktopEntry;
            useConsoleManager = _useConsoleManager;
        }
        
        Tool()
        {
            desktopEntry = false;
            useConsoleManager = false;
        }

        QString caption;
        QString fileIcon;
        QString filePath;
        QString workingPath;
        bool desktopEntry;
        bool useConsoleManager;
    };
    
    typedef QList<Tool> Tools;
    
    ToolsManager( QObject* = 0 );
    ~ToolsManager();
    
    QString scriptFilePath() const;
    ToolsManager::Tools tools( ToolsManager::Type type ) const;
    
    // interpreter commands
    void setCommand( const QString& caption, const QString& fileIcon, const QString& filePath, const QString& workingPath, bool desktopEntry, bool useConsoleManager );
    void unsetCommand( const QString& caption );
    void clearCommand();
    void updateMenuCommand();
    
    static QIcon icon( const QString& filePath, const QString& optionnalFilePath = QString::null );

public slots:
    void updateMenuActions();
    void editTools_triggered();
    void toolsMenu_triggered( QAction* );
    
protected:
    static QFileIconProvider* mIconProvider;
    ToolsManager::Tools mTools;
    
    bool writeTools( const ToolsManager::Tools& tools ) const;
    
    // interpreter handling
    void initializeInterpreterCommands( bool initialize );
    static QString commandInterpreter( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data );
};

Q_DECLARE_METATYPE( ToolsManager::Tool )

#endif // TOOLSMANAGER_H
