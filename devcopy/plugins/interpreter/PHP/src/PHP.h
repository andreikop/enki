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
#ifndef PHP_H
#define PHP_H

#include <pluginsmanager/InterpreterPlugin.h>

class PHP : public InterpreterPlugin
    Q_OBJECT
    Q_INTERFACES( BasePlugin InterpreterPlugin CLIToolPlugin )

protected:    
    void fillPluginInfos()
    virtual bool install()
    virtual bool uninstall()
public:
    PHP()
    ~PHP()
    # BasePlugin
    virtual QWidget* settingsWidget()
    # CLIToolPlugin
    virtual pCommandList defaultCommands()
    virtual QStringList availableParsers()
    # InterpreterPlugin
    virtual pCommand defaultInterpretCommand()


#endif # PHP_H
