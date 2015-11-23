: *********************************************************************************
: build_exe.bat - Build a self-contained executable bundle for the Enki application
: *********************************************************************************
: This is the first phase of the `build system <build.html>`_.
:
: Enki
: ====
: The following code builds and tests an Enki binary.
:
: Bundling
: --------
: This batch file creates a self-contained executable bundle
: of Enki using `PyInstaller <http://www.pyinstaller.org/>`_.
: PyInstaller transforms the Enki Python application into a
: standalone bundle. To do so, it needs hooks, which specify
: data files and hidden imports PyInstaller can't find. They are:
:
: * ``hook-enki.py``
: * ``hook-qutepart.py``
: * ``hook-CodeChat.py``
: * ``rthook_pyqt4.py``
:
: PyInstaller is invoked with the following `options
: <http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#options>`_:
:
: --noconfirm
:   Replace an existing executable folder or file without warning.
:
: --additional-hooks-dir=hook-path
:   Additional path to search for hook files.
:
: --hidden-import=modulename
:   Name an imported Python module that is not visible in your code.
:
: --exclude-module=MODULENAME
:   Optional module or package name (his Python name,
:   not path names) that will be ignored (as though
:   it was not found). Not yes in the docs; see
:   https://github.com/pyinstaller/pyinstaller/commit/b269a42079df2bc2fe30be0c1f0a3d0a9f9d8dfb.
:
: --name=name
:   Give a name for the specfile and the executable output. The default is the basename of the first script.
:
: --runtime-hook=path-to-hook-file
:   Specify a file with a custom runtime hook.
:
: --noconsole
:   On Windows and Mac OS X, do not create a console window
:   at run time for standard input/output.
:
: --icon=<FILE.ico>
:   Add an icon to the output executable. Specify an icon
:   FILE.ico to use that icon.
:
: ``bin\enki``
:   Enki entry point, from which Pyinstaller builds the application.
:
:pyinstaller --noconfirm --additional-hooks-dir=win --exclude-module=_tkinter --runtime-hook=win\rthook_pyqt4.py --noconsole --icon=icons\logo\enki.ico bin\enki
:
: Testing
: -------
: Run the bundled application to make sure it works.
:dist\enki\enki
:
: Sphinx
: ======
: The following code builds and tests a Sphinx binary. The sections follow the
: same flow as Enki's process above.
:
: Specify CodeChat as an import, since it's dynamically loaded by Sphinx.
:pause Press Enter to build and test Sphinx.
:pyinstaller --noconfirm --additional-hooks-dir=win --hidden-import=CodeChat --exclude-module=_tkinter win\sphinx-build.py
:dist\sphinx-build\sphinx-build
:
: Flake8
: ======
: This builds a flake8 binary.
:pause Press Enter to build and test Flake8.
:pyinstaller --noconfirm --exclude-module=_tkinter --name=flake8 C:\Python27\Lib\site-packages\flake8\__main__.py
:dist\flake8\flake8
:
: Combined Enki, Flake8, and Sphinx
: =================================
: This builds tthree binaries which can be placed in the same directory.
: See ``enki-all.spec`` for more details.
:
: Note: Existing build/ and dist/ directories from the standalone builds seem to
: confuse Pyinstaller. Start clean. The ``build_installer.bat`` file provides
: docs for the various rmdir/xoopy switches used below.
:pause Press Enter to build combined Enki and Sphinx binaries.
rmdir /q /s build dist
pyinstaller --noconfirm win\enki-all.spec
: Sphinx and flake8 binaries depend on Enki files, since they're combined. Copy
: them over.
xcopy /E /I /Q dist\sphinx-build dist\enki
xcopy /E /I /Q /Y dist\flake8 dist\enki
: Exclusing Tkinter still leaves two of its files around. Remove those.
del dist\enki\tcl85.dll
del dist\enki\tk85.dll
: Run to see if everything works.
dist\enki\enki
