Converting Enki to a binary
================

- Obtain the latest sources from `git clone https://github.com/hlamer/enki`.
- Install [Enki dependencies](../README.html#dependencies). For `ctags`, dowload the ctags binary for windows, then configure Enki to use it (Settings | Settings | Editor | Navigator, then browse to `ctags.exe`).
- Run it to make sure it works on Windows.
- Execute `win\build_exe.bat` from the root Enki directory.

Packaging
------------
- Install [Inno setup](http://www.jrsoftware.org/isdl.php) v. 5.x.
- Obtain the latest PyInstaller sources from `git clone https://github.com/pyinstaller/pyinstaller.git`.
- Execute `win\build_installer.bat` from the root Enki directory.
