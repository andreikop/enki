: .. Copyright (C) 2012-2013 Bryan A. Jones.
:
:    This file is part of Enki.
:
:    Enki is free software: you can redistribute it and/or
:    modify it under the terms of the GNU General Public
:    License as published by the Free Software Foundation,
:    either version 2 of the License, or (at your option)
:    any later version.
:
:    Enki is distributed in the hope that it will be useful,
:    but WITHOUT ANY WARRANTY; without even the implied
:    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
:    PURPOSE.  See the GNU General Public License for more
:    details.
:
:    You should have received a copy of the GNU General
:    Public License along with Enki.  If not, see
:    <http://www.gnu.org/licenses/>.
:
: *********************************************************************************
: build_exe.bat - Build a self-contained executable bundle for the Enki application
: *********************************************************************************
: This is the first phase of the `build system <build.html>`_.
:
: Combined Enki and Sphinx
: ========================
: Instead of running this file, simply execute ``pyinstaller
: win\enki-sphinx.spec`` to create both Enki and Sphinx binaries. Use this
: file to test Enki and Sphinx by themselves, and produce updated
: ``enki.spec`` and ``sphinx-build.spec`` files. See ``enki-ephinx.spec``
: for more details.
:
: Enki
: ====
: The following code builds and tests an Enki binary.
:
: Bundling
: --------
: This batch file creates a self-contained executable bundle
: of Enki using `PyInstaller <http://www.pyinstaller.org/>`_.
: PyInstaller transforms the Enki Python application into a
: standalone bundle. To do so, it needs hooks, which specify
: data files and hidden imports PyInstaller can't find. They are:
:
: * ``hook-enki.py``
: * ``hook-qutepart.py``
: * ``rthook_pyqt4.py``
:
: PyInstaller is invoked with the following `options
: <http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#options>`_:
:
: --noconfirm
:   Replace an existing executable folder or file without warning.
:
: --additional-hooks-dir=hook-path
:   Additional path to search for hook files.
:
: --hidden-import=modulename
:   Name an imported Python module that is not visible in your code.
:
: --runtime-hook=path-to-hook-file
:   Specify a file with a custom runtime hook.
:
: --noconsole
:   On Windows and Mac OS X, do not create a console window
:   at run time for standard input/output.
:
: --icon=<FILE.ico>
:   Add an icon to the output executable. Specify an icon
:   FILE.ico to use that icon.
:
: ``bin\enki``
:   Enki entry point, from which Pyinstaller builds the application.
:
:pyinstaller --noconfirm --additional-hooks-dir=win --runtime-hook=win\rthook_pyqt4.py --noconsole --icon=icons\logo\enki.ico bin\enki
:
: Testing
: -------
: Run the bundled application to make sure it works.
:dist\enki\enki
pause Press Enter to build and test Sphinx.
:
: Sphinx
: ======
: The following code builds and tests a Sphinx binary. The sections follow the
: same flow as Enki's process above.
:
: Specify CodeChat as an import, since it's dynamically loaded by Sphinx.
pyinstaller --noconfirm --hidden-import=CodeChat win\sphinx-build.py
dist\sphinx-build\sphinx-build
