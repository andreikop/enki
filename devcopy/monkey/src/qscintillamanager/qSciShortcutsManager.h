/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : qSciShortcutsManager.h
** Date      : 2008-01-14T00:37:07
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
#ifndef QSCISHORTCUTSMANAGER
#define QSCISHORTCUTSMANAGER

#include <objects/MonkeyExport.h>
#include <objects/QSingleton.h>

#include <QApplication>
#include <QIcon>

/*QScintilla using set of shorctuts. Class clearing this shortcuts, and, if need
to do QSintilla's action, sending to it message. It's need for replacing 
QScintilla's own shourcuts with Monkey Studio actions. Because actions can be 
configured, and can be used in the macroses.
Message will be sended to current editor.
*/
class pEditor;


struct SciAction
{
    SciAction (QString _name, QString _text, QIcon _icon, QString _defaultShortcut, QString _toolTip, int _messageCode):
        name (_name), text (_text), icon (_icon), defaultShortcut (_defaultShortcut), toolTip (_toolTip), messageCode (_messageCode){};
    QString name;
    QString text;
    QIcon icon;
    QString defaultShortcut;
    QString toolTip;
    int messageCode;
};


class Q_MONKEY_EXPORT qSciShortcutsManager: public QObject, public QSingleton<qSciShortcutsManager>
{
    Q_OBJECT
    friend class QSingleton<qSciShortcutsManager>;
protected:
    qSciShortcutsManager (QObject* parent = QApplication::instance());

protected:
    QList<SciAction> sactions;

protected slots:    
    void keyBoardShortcutPressed ();
};

#endif //QSCISHORTCUTSMANAGER
