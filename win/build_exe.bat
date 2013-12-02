: .. Copyright (C) 2012-2013 Bryan A. Jones.
:
:    This file is part of Enki.
:
:    Enki is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
:
:    Enki is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
:
:    You should have received a copy of the GNU General Public License along with Enki.  If not, see <http://www.gnu.org/licenses/>.
:
:
: .. highlight:: BatchLexer
:
: ******************************************************************************
: build_exe.bat - Build a self-contained executable for the Enki application
: ******************************************************************************
: This file creates a Windows executable using `Pyinstaller <http://www.pyinstaller.org/>`_. It *must* be run from the Enki root directory, not the win subdirectory where it resides. `Options <http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#options>`_ are:
:
: -y
:   Replace an existing executable folder or file without warning.
:
: --additional-hooks-dir=hook-path
:  Additional path to search for hook files.
:
: --runtime-hook=path-to-hook-file
 	Specify a file with a custom runtime hook.
:
: ``bin\enki``
:   Enki entry point, from which Pyinstaller builds the application.
:
..\..\pyinstaller-git\pyinstaller.py --additional-hooks-dir=win --runtime-hook=win\pyi_rth_qt4plugins.py -y bin\enki
:
: Run the application to make sure it works. This also updates the generated documentation for packaging.
dist\enki\enki
