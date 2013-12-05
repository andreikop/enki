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
: .. highlight:: bat
:
: ****************************************************************************************
: build_exe.bat - Build a self-contained executable bundle for the Enki application
: ****************************************************************************************
: This is the first phase of the :doc:`build system <build>`.
:
: Bundling
: ========
: This batch file creates a self-contained executable bundle of Enki using `PyInstaller <http://www.pyinstaller.org/>`_. PyInstaller transforms the Enki Python application into a standalone bundle. To do so, it needs hooks, which specify data files and hidden imports PyInstaller can't find. They are:
:
: .. toctree::
:    :maxdepth: 2
:
:    hook-enki.py
:    hook-qutepart.py
:    rthook_pyqt4.py
:
: PyInstaller is invoked with the following `options <http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#options>`_:
:
: -y
:   Replace an existing executable folder or file without warning.
:
: --additional-hooks-dir=hook-path
:   Additional path to search for hook files.
:
: --runtime-hook=path-to-hook-file
:   Specify a file with a custom runtime hook.
:
: ``bin\enki``
:   Enki entry point, from which Pyinstaller builds the application.
:
..\..\pyinstaller-git\pyinstaller.py --additional-hooks-dir=win --runtime-hook=win\rthook_pyqt4.py -y bin\enki
:
: Testing
: =======
: Run the bundled application to make sure it works.
dist\enki\enki
