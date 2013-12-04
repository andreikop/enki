# **********************************************************
# rthook_pyqt4.py - PyInstaller run-time hook file for PyQt4
# **********************************************************
# Enki uses the `v2 api <http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html>`_ for ``QString``. Tell PyInstaller about that, following the `recipe <http://www.pyinstaller.org/wiki/Recipe/PyQtChangeApiVersion>`_.

import sip
sip.setapi('QString', 2)
