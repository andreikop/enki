************************
Windows build system
************************
The Windows build system consists of a two-step process. First, the working Enki application, which runs under Python, is bundled into a self-contained executable bundle which no longer requires Python or any of Enki's dependencies (PyQt, etc.) to run. In the second step, this bundle is then packaged into a Windows installer. The two files below performs these tasks; next, the following instruction show how to use them.

 .. toctree::
    :maxdepth: 2

    build_exe.bat
    build_installer.bat
    
Converting Enki to a self-contained executable bundle
=====================================================
- Obtain the latest sources from ``git clone https://github.com/hlamer/enki``.
- Install `Enki dependencies <../README.html#dependencies>`_. For ``ctags``, dowload the ctags binary for windows, then configure Enki to use it (Settings | Settings | Editor | Navigator, then browse to ``ctags.exe``).
- Run it to make sure it works on Windows.
- Execute ``win\build_exe.bat`` from the root Enki directory.

Packaging the bundle into a Windows installer
=============================================
- Install `Inno setup <http://www.jrsoftware.org/isdl.php>`_ v. 5.x.
- Obtain the latest PyInstaller sources from ``git clone https://github.com/pyinstaller/pyinstaller.git``.
- Execute ``win\build_installer.bat`` from the root Enki directory.
