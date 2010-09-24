'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UICtags2Api.h
** Date      : 2008-01-14T00:39:52
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
#ifndef UICTAGS2API_H
#define UICTAGS2API_H

#include "ui_UICtags2Api.h"

#include <QHash>
#include <QByteArray>

struct CtagsEntity
    CtagsEntity(  QString& s )
        mList = s.split( '\t' )


    QString getName()
        return mList.value( 0 ).trimmed()

    QString getFile()
        return mList.value( 1 ).trimmed()

    QString getAddress()
        return mList.value( 2 ).trimmed()

    QString getFieldValue(  QString& s )
        # field are format, old is only 3 part separated by '\t'
        if  mList.count() == 3 or s.isEmpty() :
            return QString()

        for ( i = 3; i < mList.count(); i++ )
            f = mList.at( i )
            # special case kind
            if  not f.contains( ':' ) and s == "kind" :
                return f.trimmed()
            # special case file
            if  f == "file:" :
                return getFile()
            # generic way
            l = f.split( ':' )
            if  l.at( 0 ) == s :
                return l.value( 1 ).trimmed().replace( "\\t", "\t" ).replace( "\\r", "\r" ).replace( "\\n", "\n" ).replace( "\\\\", "\\" )

        return QString()

    QString getKindValue()
        return getFieldValue( "kind" )

    QString getKindDefaultField()
        # get kind
         s = getKindValue()
        # if empty return null string
        if  s.isEmpty() :
            return QString()
        # get value
        if  s == "c" :
            return "class"
        elif  s == "d" :
            return QString()
        elif  s == "e" :
            return "enum"
        elif  s == "f" :
            return "function"
        elif  s == "F" :
            return "file"
        elif  s == "g" :
            return QString()
        elif  s == "m" :
            if  not getFieldValue( "class" ).isEmpty() :
                return "class"
            elif  not getFieldValue( "struct" ).isEmpty() :
                return "struct"
            return QString()

        elif  s == "p" :
            return QString()
        elif  s == "s" :
            return "struct"
        elif  s == "t" :
            return "typeref"
        elif  s == "u" :
            return "union"
        elif  s == "v" :
            return QString()
        return QString()

    QString getKindDefaultValue()
        return getFieldValue( getKindDefaultField() )


    QStringList mList


class UICtags2Api : public QDialog, Ui.UICtags2Api
    Q_OBJECT

public:
    UICtags2Api( QWidget* = 0 )
    ~UICtags2Api()

    QList<QByteArray> getFileContent(  QString& )

protected:
    QHash<QString, QList<QByteArray> > mFileCache

protected slots:
    void on_tbCtagsBinary_clicked()
    void on_cbGenerateFrom_currentIndexChanged( int )
    void on_tbBrowse_clicked()
    void on_tbSrcPathBrowse_clicked()
    bool processCtagsBuffer(  QByteArray& )
    bool processCtags(  QString& )
    bool processCtags2Api(  QString& )
    void accept()



#endif # UICTAGS2API_H
