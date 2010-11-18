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
/*!
	\file pTemplatesManager.h
	\date 2008-01-14T00:37:13
	\author Andrei KOPATS, Filepe AZEVEDO
	\brief Header for pTemplatesManager class
*/
#ifndef PTEMPLATESMANAGER_H
#define PTEMPLATESMANAGER_H

#include <objects/MonkeyExport.h>

#include "variablesmanager/VariablesManager.h"

#include <QApplication>
#include <QStringList>

class XUPItem;

typedef QHash <QString, QStringList> VarList;

/*
	NOTE Filenames can contain variables. Example: Project$name$.pro
	This files will be renamed
*/

/*!
	\brief Inmemory representation of template.
*/
struct Q_MONKEY_EXPORT pTemplate
{
	QString Name;							/*<! Name of template, which are displaying for user */
	QString Language;						/*<! Programming language */
	QString Type;							/*<! Type of template (Project, File..) */
	QString Description;					/*<! Desctiption of template. Shown on tooltip */
	QString Icon;							/*<! Path to template icon */
	QString Script;							/*<! Script for configure template. Currently support not implemented*/
	QString DirPath; 						/*<! Dirrectory, containing template */
	QStringList Files;						/*<! List of files of template */
	QStringList FilesToOpen;				/*<! List of files, which should be open after template creation */
	QStringList ProjectsToOpen;				/*<! List of project, which should be open after template creation */
	QStringList FilesToAdd;					/*<! List of files, which coult be added to some project, after creation */
	VarList Variables;
	
	/*!
		Compare two templates
	*/
	bool operator==( const pTemplate& t )
	{ return Name == t.Name && Language == t.Language && Type == t.Type &&
			Description == t.Description && Icon == t.Icon && Script == t.Script &&
			DirPath == t.DirPath && Files == t.Files && FilesToOpen == t.FilesToOpen &&
			ProjectsToOpen == t.ProjectsToOpen && FilesToAdd == t.FilesToAdd && Variables == t.Variables; }

};

/*!
	List of templates   BUG this comment not including to documentation
*/
typedef QList<pTemplate> TemplateList;

/*!
	\brief Implementation of Templates Manager module
	
	Allows to cteate files from template, configure template before creation of files, open files and projects, add new files to projects
*/
class Q_MONKEY_EXPORT pTemplatesManager : public QObject, public QSingleton<pTemplatesManager>
{
	Q_OBJECT
	friend class QSingleton<pTemplatesManager>;
	
private:
	pTemplatesManager( QObject* = QApplication::instance() );

public:
	pTemplate getTemplate( const QString& );
	TemplateList getTemplates();

	bool realiseTemplate( XUPItem* scope, const pTemplate& tmplate, const QString& codec, const VariablesManager::Dictionary& variables = VariablesManager::Dictionary() );
	
};

#endif // PTEMPLATESMANAGER_H
