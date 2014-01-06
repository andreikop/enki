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
: .. highlight:: bat
:
: *****************************************************************
: build_installer.bat - Package the bundle into a Windows installer
: *****************************************************************
: This is the second phase of the :doc:`build system
: <build>`. It packages a bundled executable version of the
: program, together with its source code, into a single
: installer.
:
: Gather files
: ------------
: First, this script gathers the following components needed
: to create a package, placing everything to be packaged
: into ``dist/all``.
:
: **Note:** this should only by run after a successfull
: execution of :doc:`build_exe.bat <build_exe.bat>`, which
: creates the executable. Git should have all changes
: committed.
:
: ==============   ========================   ======================
: Component        Source                     Dest
: ==============   ========================   ======================
: The executable   ``dist/code_chat``         ``dist/all/bin``
: Source code      Git repo in ``./``         ``dist/all/src``
: ==============   ========================   ======================
:
: This script makes use of several DOS commands with flags.
: A quick reference:
:
: For ``rmdir``:
:
: /S      Removes all directories and files in the specified
:         directory in addition to the directory itself.
:         Used to remove a directory tree.
: /Q      Quiet mode, do not ask if ok to remove a directory
:         tree with /S
:
: For ``xcopy``:
:
: /E           Copies directories and subdirectories,
:              including empty ones.
: /I           If destination does not exist and copying
:              more than one file, assumes that destination
:              must be a directory.
:
: Create a clean ``dist/all`` directory and enter it.
mkdir dist
cd dist
rmdir /q /s all
mkdir all
cd all
:
: Copy over the source code with no intermediate files by
: cloning the repo then removing the repo files.
git clone ..\.. src
rmdir /q /s src\.git
:
: Copy over the executable
xcopy /E /I ..\enki bin
:
: Copy over the ctags executable.
copy ..\..\..\ctags58\ctags.exe bin
:
: Package
: -------
: .. toctree::
:    :hidden:
:
:    Enki.iss
:
: The :doc:`Enki.iss <Enki.iss>` script then packages
: everything in ``dist/all`` into a single installer.

"C:\Program Files\Inno Setup 5\ISCC.exe" win\Enki.iss
