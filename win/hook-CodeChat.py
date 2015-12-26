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
from PyInstaller.utils.hooks import get_package_paths
import os.path

# The ``template/`` directory contains data files to be copied. Get an
# absolute path to the CodeChat directory containing it.
pkg_base, pkg_dir = get_package_paths('CodeChat')
# -------------Source files------------  -----dest path-----
datas = [(os.path.join(pkg_dir, 'template', '*'), 'CodeChat/template')]

# This isn't imported by CodeChat directly, so include it for Sphinx's use.
hiddenimports = ['CodeChat.CodeToRestSphinx']
