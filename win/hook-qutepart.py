# *****************************************************
# hook-qutepart.py - PyInstaller hook file for qutepart
# *****************************************************
# Pyinstaller can't know about data files used by qutepart. This hook informs
# Pyinstaller that these files must be included in the Enki bundle.
from PyInstaller.utils.hooks import collect_data_files

# Gather all non-Python files in the qutepart package.
datas = collect_data_files('qutepart')
