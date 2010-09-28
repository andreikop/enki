/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : Settings.h
** Date      : 2008-01-14T00:37:11
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
#ifndef SETTINGS_H
#define SETTINGS_H

#include <objects/pSettings.h>

struct LexerStyle
{
    LexerStyle() {}
    LexerStyle( int i, int c, bool e, const QString& f, int p )
    { id = i; color = c; eolfill = e; font = f; paper = p; }
    
    int id;
    int color;
    bool eolfill;
    QString font;
    int paper;
};

typedef QList<LexerStyle> LexerStyleList;

class Q_MONKEY_EXPORT Settings : public pSettings
{
    Q_OBJECT
    
public:
    enum StoragePath
    {
        SP_PLUGINS = -1,
        SP_APIS,
        SP_TEMPLATES,
        SP_TRANSLATIONS,
        SP_SCRIPTS
    };
    
    Settings( QObject* = 0 );
    
    QString storageToString( Settings::StoragePath type ) const;
    QStringList storagePaths( Settings::StoragePath type ) const;
    void setStoragePaths( Settings::StoragePath type, const QStringList& paths );
    
    QString homeFilePath( const QString& filePath ) const;
    QString homePath( Settings::StoragePath type ) const;
    
    virtual void setDefaultSettings();
    void setDefaultCppSyntaxHighlight();
    void setDefaultLexerProperties( const QFont& font, bool write );

protected:
    QStringList storagePathsOutOfBox( Settings::StoragePath type, const QString& appPath ) const;
};

#endif // SETTINGS_H
