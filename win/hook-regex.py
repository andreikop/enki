# ***************************************************
# hook-regex.py - PyInstaller hook file for ``regex``
# ***************************************************
# Enki uses ``pkg_resources`` to obtain the ``regex`` version. So, we need to
# copy over the ``regex`` metadata.
from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('regex')
