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
# *********************************************
# hook-enki.py - PyInstaller hook file for Enki
# *********************************************
# PyInstaller can't find hidden imports (such as the
# dynamically-discovered plugins), not can it know about
# data files (such as ``.ui`` files). This hook informs
# PyInstaller that these files must be included in the Enki
# bundle.
from hookutils import collect_data_files

datas = (
    # Enki relies on a number of .ui files and some .json
    # files. Gather all these.
    collect_data_files('CodeChat') + [])
