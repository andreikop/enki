'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UIUpdateChecker.h
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
#ifndef UIUPDATECHECKER_H
#define UIUPDATECHECKER_H

#include "ui_UIUpdateChecker.h"

#include <objects/pVersion.h>

#include <QDomDocument>
#include <QDateTime>

class QNetworkAccessManager
class QNetworkReply
class UpdateChecker

class UpdateItem
public:
    enum Type
        Updated,
        Id,
        Link,
        Title,
        Author,
        Content

    
    UpdateItem(  element = QDomElement() )
    
    bool operator<(  UpdateItem& other )
    bool operator>(  UpdateItem& other )
    bool operator<(  pVersion& other )
    bool operator>(  pVersion& other )
    
    QDateTime updated()
    QString id()
    QUrl link()
    QString title()
    QString author()
    QString content()
    QString toolTip()
    bool isFeatured()
    QString displayText()
    QString versionString()
    pVersion version()
    bool isValid()

protected:
    QMap<UpdateItem.Type, mDatas


class UIUpdateChecker : public QDialog, Ui.UIUpdateChecker
    Q_OBJECT

public:
    UIUpdateChecker( UpdateChecker* plugin, QWidget* = 0 )
    ~UIUpdateChecker()

protected:
    UpdateChecker* mPlugin
    static  QString mDownloadsUrl
    QNetworkAccessManager* mAccessManager

protected slots:
    void accessManager_finished( QNetworkReply* reply )
    void on_lwVersions_itemSelectionChanged()
    virtual void accept()


Q_DECLARE_METATYPE( UpdateItem )

#endif # UIUPDATECHECKER_H
