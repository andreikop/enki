from hookutils import collect_submodules, collect_data_files

hiddenimports = (
    # The plugins are dynamically loaded, making them a hidden import.
    collect_submodules('enki.plugins') +
    # The preview plugin's .ui file needs QtWebKit, making it hidden as well.
    ['PyQt4.QtWebKit'])

datas = (
# Enki relies on a number of .ui files and some .json files. Gather all these.
    collect_data_files('enki') +
# Enki's dynamic plug system needs the plugin available for os.listdir-type operations to be found. Gather than.
    collect_data_files('enki.plugins', True))


# Contents of revised hook-PyQt4.QtWebKit.py, which doesn't get processed for some reason...
#-----------------------------------------------------------------------------
# Copyright (c) 2013, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
from hookutils import get_package_paths

hiddenimports += ["sip", "PyQt4.QtCore", "PyQt4.QtGui", "PyQt4.QtNetwork", "PyQt4._qt", "PyQt4.uic.widget-plugins.qtwebkit.py"]

# Need to include PyQt4.uic.widget-plugins.qtwebkit.py as a file, so it will be dynamically loaded by uic.
pkg_base, pkg_dir = get_package_paths('PyQt4.uic')
datas += [(pkg_dir + '/widget-plugins/qtwebkit.py', 'PyQt4/uic/widget-plugins')]
