Installing and running Enki
================

Download and install
-------------------------
git clone https://github.com/hlamer/enki
cd ..\enki
python setup.py install

Run
-----
cd bin
python enki

Packaging
------------
..\..\pyinstaller-git\pyinstaller.py --additional-hooks-dir=win -y bin\enki

Bugs
-----
Still trying to get navigator to work.
