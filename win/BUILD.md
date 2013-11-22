Installing and running Enki
================

Download and install
-------------------------
    git clone https://github.com/hlamer/enki
    cd enki
    python setup.py install
    
Run
-----
    cd bin
    python enki
    
Create a binary
------------------
    cd enki\core\plugins\preview
    pyuic4 Preview.ui -f Preview_ui.py
    pyrcc4 ..\..\..\icons\enkiicons.qrc > enkiicons_rc.py
    cd ..\..\..
    ..\..\pyinstaller-git\pyinstaller.py --additional-hooks-dir=win -y bin\enki
    
Packaging
------------
To do.

Bugs
-----
Still trying to get navigator to work.
