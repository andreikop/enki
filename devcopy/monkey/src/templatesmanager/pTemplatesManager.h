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
    \file pTemplatesManager.h
    \date 2008-01-14T00:37:13
    \author Andrei KOPATS, AZEVEDO
    \brief Header for pTemplatesManager class
'''
#ifndef PTEMPLATESMANAGER_H
#define PTEMPLATESMANAGER_H

#include <objects/MonkeyExport.h>

#include "variablesmanager/VariablesManager.h"

#include <QApplication>
#include <QStringList>

class XUPItem

typedef QHash <QString, VarList

'''
    NOTE Filenames can contain variables. Example: Project$name$.pro
    This files will be renamed
'''

'''!
    \brief Inmemory representation of template.
'''
struct Q_MONKEY_EXPORT pTemplate
    QString Name;                            '''<not  Name of template, are displaying for user '''
    QString Language;                        '''<not  Programming language '''
    QString Type;                            '''<not  Type of template (Project, File..) '''
    QString Description;                    '''<not  Desctiption of template. Shown on tooltip '''
    QString Icon;                            '''<not  Path to template icon '''
    QString Script;                            '''<not  Script for configure template. Currently support not implemented'''
    QString DirPath;                         '''<not  Dirrectory, template '''
    QStringList Files;                        '''<not  List of files of template '''
    QStringList FilesToOpen;                '''<not  List of files, should be open after template creation '''
    QStringList ProjectsToOpen;                '''<not  List of project, should be open after template creation '''
    QStringList FilesToAdd;                    '''<not  List of files, coult be added to some project, creation '''
    VarList Variables
    
    '''!
        Compare two templates
    '''
    bool operator==(  pTemplate& t )
    { return Name == t.Name and Language == t.Language and Type == t.Type and
            Description == t.Description and Icon == t.Icon and Script == t.Script and
            DirPath == t.DirPath and Files == t.Files and FilesToOpen == t.FilesToOpen and
            ProjectsToOpen == t.ProjectsToOpen and FilesToAdd == t.FilesToAdd and Variables == t.Variables;



'''!
    List of templates   BUG self comment not including to documentation
'''
typedef QList<pTemplate> TemplateList

'''!
    \brief Implementation of Templates Manager module
    
    Allows to cteate files from template, template before creation of files, files and projects, files to projects
'''
class Q_MONKEY_EXPORT pTemplatesManager : public QObject, QSingleton<pTemplatesManager>
    Q_OBJECT
    friend class QSingleton<pTemplatesManager>
    
private:
    pTemplatesManager( QObject* = QApplication.instance() )

public:
    pTemplate getTemplate(  QString& )
    TemplateList getTemplates()

    bool realiseTemplate( XUPItem* scope, tmplate, codec, variables = VariablesManager.Dictionary() )
    


#endif # PTEMPLATESMANAGER_H
