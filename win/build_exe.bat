REM *********************************************************************************
REM build_exe.bat - Build a self-contained executable bundle for the Enki application
REM *********************************************************************************
REM This is the first phase of the `build system <build.html>`_.
REM
REM Enki
REM ====
REM The following code builds and tests a stand-alone Enki executable.
REM
REM Setup
REM -----
REM It's best to create a virtual environment which contains only the packages
REM needed by Enki. This causes PyInstaller to create a smaller binary, since
REM it won't find an include optional imports of unnecessary packages. The
REM following instructions were tested with 32-bit WinPython 3.3.4/Qt5.
REM
REM #. Open the Visual Studio Command Prompt (2010).
REM #. From that, run the WinPython Command Prompt.
REM #. Create a virtual environment named ``packaging``: ``python -m venv
REM    packaging``.
REM #. Activate it: ``packaging\Scripts\activate.bat``.
REM #. Upgrade pip: ``python -m pip install -U pip``.
REM #. Change to the PyInstaller directory and execute ``python setup.py
REM    install``. One of its dependences, ``pypiwin32``, will fail to install.
REM #. Install it, via ``python -m pip install -U pypiwin32 pefile``. This will succeed.
REM #. Manually copy ``sip.pyd`` and the ``PyQt5`` directory from Python's
REM    ``site-packages`` to ``packaging\lib\site-packages``.
REM #. Execute ``set
REM    QT_QPA_PLATFORM_PLUGIN_PATH <path to packaging>\packaging\lib\site-packages\PyQt5\plugins\platforms``.
REM    Otherwise, you get the error message ``This application failed to start
REM    because it could not find or load the Qt platform plugin "windows". \n\n
REM    Reinstalling the application may fix this problem.`` See http://stackoverflow.com/questions/17695027/pyqt5-failed-to-load-platform-plugin-windows-available-platforms-are-windo
REM #. Follow the directions in Qutepart's README.md to install Qutepart.
REM #. Change to the CodeChat directory, then execute ``python setup.py
REM    install``. This comes before the step below, so the latest version will
REM    supercede whatever's currently released on PyPI.
REM #. Change to the Enki directory, then execute ``python -m pip install -U -r
REM    requirements.txt``.
REM
REM Bundling
REM --------
REM This batch file creates a self-contained executable bundle
REM of Enki using `PyInstaller <http://www.pyinstaller.org/>`_.
REM PyInstaller transforms the Enki Python application into a
REM standalone bundle. To do so, it needs hooks, which specify
REM data files and hidden imports PyInstaller can't find. They are:
REM
REM * ``hook-enki.py``
REM * ``hook-qutepart.py``
REM * ``hook-CodeChat.py``
REM * ``hook-regex.py``
REM
REM PyInstaller is invoked with the following `options
REM <http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#options>`_:
REM
REM --noconfirm
REM   Replace an existing executable folder or file without warning.
REM
REM --additional-hooks-dir=hook-path
REM   Additional path to search for hook files.
REM
REM --hidden-import=modulename
REM   Name an imported Python module that is not visible in your code.
REM
REM --exclude-module=MODULENAME
REM   Optional module or package name (his Python name,
REM   not path names) that will be ignored (as though
REM   it was not found). Not yes in the docs; see
REM   https://github.com/pyinstaller/pyinstaller/commit/b269a42079df2bc2fe30be0c1f0a3d0a9f9d8dfb.
REM
REM --name=name
REM   Give a name for the specfile and the executable output. The default is
REM   the basename of the first script.
REM
REM --noconsole
REM   On Windows and Mac OS X, do not create a console window
REM   at run time for standard input/output.
REM
REM --icon=<FILE.ico>
REM   Add an icon to the output executable. Specify an icon
REM   FILE.ico to use that icon.
REM
REM ``bin\enki``
REM   Enki entry point, from which Pyinstaller builds the application.
REM
:rmdir /q /s build dist
:pyinstaller --noconfirm --additional-hooks-dir=win --exclude-module=_tkinter --noconsole --icon=icons\logo\enki.ico bin\enki
REM
REM Testing
REM -------
REM Run the bundled application to make sure it works.
:dist\enki\enki
REM
REM Sphinx
REM ======
REM The following code builds and tests a Sphinx binary. The sections follow
REM the same flow as Enki's process above.
REM
REM Specify CodeChat as an import, since it's dynamically loaded by Sphinx.
:pause Press Enter to build and test Sphinx.
:pyinstaller --noconfirm --additional-hooks-dir=win --hidden-import=CodeChat --exclude-module=_tkinter win\sphinx-build.py
:dist\sphinx-build\sphinx-build
REM
REM Flake8
REM ======
REM This builds a flake8 binary.
:pause Press Enter to build and test Flake8.
:pyinstaller --noconfirm --exclude-module=_tkinter --name=flake8 C:\Python27\Lib\site-packages\flake8\__main__.py
:dist\flake8\flake8
REM
REM Combined Enki, Flake8, and Sphinx
REM =================================
REM This builds three binaries which can be placed in the same directory.
REM See ``enki-all.spec`` for more details.
REM
REM Note: Existing build/ and dist/ directories from the standalone builds seem
REM to confuse Pyinstaller. Start clean. The ``build_installer.bat`` file
REM provides docs for the various rmdir/xoopy switches used below.
:pause Press Enter to build combined Enki and Sphinx binaries.
rmdir /q /s build dist
pyinstaller --noconfirm win\enki-all.spec
REM Sphinx and flake8 binaries depend on Enki files, since they're combined.
REM Copy them over.
xcopy /E /I /Q dist\sphinx-build dist\enki
xcopy /E /I /Q /Y dist\flake8 dist\enki
REM Excluding Tkinter still leaves two of its files around. Remove those.
del dist\enki\tcl*.dll
del dist\enki\tk*.dll
REM Run to see if everything works.
dist\enki\enki
