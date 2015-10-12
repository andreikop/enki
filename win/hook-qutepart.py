# .. Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of Enki.
#
#    Enki is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation,
#    either version 2 of the License, or (at your option)
#    any later version.
#
#    Enki is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#    PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General
#    Public License along with Enki.  If not, see
#    <http://www.gnu.org/licenses/>.
#
# *****************************************************
# hook-qutepart.py - PyInstaller hook file for qutepart
# *****************************************************
# Pyinstaller can't know about data files used by qutepart. This hook informs
# Pyinstaller that these files must be included in the Enki bundle.
from PyInstaller.utils.hooks import collect_data_files

# Gather all non-Python files in the qutepart package.
datas = collect_data_files('qutepart')
