# .. Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation,
#    either version 2 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#    PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General
#    Public License along with CodeChat.  If not, see
#    <http://www.gnu.org/licenses/>.
#
# *****************************************************
# hook-CodeChat.py - PyInstaller hook file for CodeChat
# *****************************************************
# PyInstaller can't find hidden imports (such as the
# dynamically-discovered plugins), not can it know about
# data files (such as ``.css`` files). This hook informs
# PyInstaller that these files must be included in the CodeChat
# bundle. See
# http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#using-hook-files
# for details.
from hookutils import get_package_paths
import os.path

# Confusion: just doing hiddenimports=('CodeChat'), or even
# hiddenimports=('CodeChat.CodeToRestSphinx') doesn't work
# (CodeChat.LanguageSpecificOptions won't be found). Why?
hiddenimports = ('CodeChat.CodeToRestSphinx', 'CodeChat.CodeToRest',
                 'CodeChat.LanguageSpecificOptions')

# The ``template/`` directory contains data files to be copied. Get an
# absolute path to the CodeChat directory containing it.
pkg_base, pkg_dir = get_package_paths('CodeChat')
##         -------------Source files------------  -----dest path-----
datas = [ (os.path.join(pkg_dir, 'template', '*'), 'CodeChat/template') ]
