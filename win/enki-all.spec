# .. -*- mode: python -*-
#
# *************
# enki-all.spec
# *************
# This file instructs Pyinstaller to build a binary containing both Enki,
# flake8, and Sphinx executables.
#
# Procedure to create this file:
#
# #. Run ``win\build_exe.bat`` and test. This creates working
#    ``enki.spec``, ``flake8.spec`` and ``sphinx-build.spec`` files.
# #. Combine these files according to the `Pyinstaller merge docs
#    <http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#multipackage-bundles>`_.
#    These steps are illustrated in the comments below.
# #. Run ``win\build_exe.bat`` again; the third build is the combined version.
#
# Imports
# =======
import os.path
import flake8
#
# Analysis
# ========
# Per the `Pyinstaller merge docs`_, first create uniquely-named analysis
# objects for both programs.
enki_a = Analysis(['../bin/enki'],
  pathex=['.'],
  hiddenimports=[],
  hookspath=['win'],
  runtime_hooks=['win/rthook_pyqt4.py'],
  excludes=['_tkinter'])

sphinx_a = Analysis(['sphinx-build.py'],
  pathex=['.'],
  hiddenimports=['CodeChat'],
  hookspath=['win'],
  runtime_hooks=[],
  excludes=['_tkinter'])

# Provide the OS-dependent location of flake8's __main__.py file.
flake8_a = Analysis([os.path.join(flake8.__path__[0], '__main__.py')],
  pathex=['.'],
  hiddenimports=[],
  hookspath=None,
  runtime_hooks=None,
  excludes=['_tkinter'])
#
# Merge
# =====
# Next, eliminate duplicate libraries and modules. Listing Enki first seems to
# place all libraries and modules there.
MERGE(
    (enki_a, 'enki', 'enki'),
    (sphinx_a, 'sphinx', 'sphinx'),
    (flake8_a, 'flake8', 'flake8'))
#
# Produce binaries
# ================
# Finally, produce the binaries. Note that the resulting Sphinx binary doesn't
# work as is, since it has no libraries bundled with it. Instead, it needs to
# be copied to the Enki directory before being executed.
enki_pyz = PYZ(enki_a.pure)
enki_exe = EXE(enki_pyz,
  enki_a.scripts,
  exclude_binaries=True,
  name='enki',
  debug=False,
  strip=None,
  upx=True,
  console=False,
  icon='icons/logo/enki.ico')
enki_coll = COLLECT(enki_exe,
  enki_a.binaries,
  enki_a.zipfiles,
  enki_a.datas,
  strip=None,
  upx=True,
  name='enki')

sphinx_pyz = PYZ(sphinx_a.pure)
sphinx_exe = EXE(sphinx_pyz,
  sphinx_a.scripts,
  exclude_binaries=True,
  name='sphinx-build',
  debug=False,
  strip=None,
  upx=True,
  console=True)
sphinx_coll = COLLECT(sphinx_exe,
  sphinx_a.binaries,
  sphinx_a.zipfiles,
  sphinx_a.datas,
  strip=None,
  upx=True,
  name='sphinx-build')

flake8_pyz = PYZ(flake8_a.pure)
flake8_exe = EXE(flake8_pyz,
  flake8_a.scripts,
  exclude_binaries=True,
  name='flake8',
  debug=False,
  strip=None,
  upx=True,
  console=True)
flake8_coll = COLLECT(flake8_exe,
  flake8_a.binaries,
  flake8_a.zipfiles,
  flake8_a.datas,
  strip=None,
  upx=True,
  name='flake8')

