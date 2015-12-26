# *********************************************
# hook-enki.py - PyInstaller hook file for Enki
# *********************************************
# PyInstaller can't find hidden imports (such as the
# dynamically-discovered plugins), not can it know about
# data files (such as ``.ui`` files). This hook informs
# PyInstaller that these files must be included in the Enki
# bundle.
from PyInstaller.utils.hooks import collect_submodules, \
    collect_data_files

hiddenimports = (
    # The plugins are dynamically loaded, making them a
    # hidden import.
    collect_submodules('enki.plugins') +
    # The colorbutton widget is loaded from a .ui file,
    # making it a hidden import. Not sure if others there
    # are or not, but they're certainly all needed.
    collect_submodules('enki.widgets'))

datas = (
    # Enki relies on a number of .ui files and some .json
    # files. Gather all these.
    collect_data_files('enki') +
    # Enki's dynamic plug system needs the plugin source
    # files available to be found by for os.listdir-type
    # operations. Gather them.
    collect_data_files('enki.plugins', True))
