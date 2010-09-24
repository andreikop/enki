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
	\file ClassBrowserSettings.h
	\date 2009-05-01
	\author Filipe AZEVEDO
	\brief Settings widget of ClassBrowser plugin
*/
#ifndef FILEBROWSERSETTINGS_H
#define FILEBROWSERSETTINGS_H

#include <qCtagsSense.h>

#include <QWidget>

class ClassBrowser;
class QComboBox;
class pPathListEditor;
class pStringListEditor;
class QGroupBox;
class QLabel;
class QLineEdit;
class QToolButton;

/*!
	Settigs widget of ClassBrowser plugin
	
	Allows to edit the system include paths etc
*/
class ClassBrowserSettings : public QWidget
{
	Q_OBJECT
	
public:
	ClassBrowserSettings( ClassBrowser* plugin, QWidget* parent = 0 );

protected:
	ClassBrowser* mPlugin;
	QComboBox* cbIntegrationMode;
	pPathListEditor* mPathEditor;
	pStringListEditor* mStringEditor;
	QGroupBox* gbUseDBFileName;
	QLabel* lDBFileName;
	QLineEdit* leDBFileName;
	QToolButton* tbDBFileName;

protected slots:
	void tbDBFileName_clicked();
	void applySettings();

signals:
	void propertiesChanged( const qCtagsSenseProperties& properties );
};

#endif // FILEBROWSERSETTINGS_H
