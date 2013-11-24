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
    cd enki\core\plugins\preview
    pyuic4 Preview.ui -f Preview_ui.py
    # Hand edit last line of Preivew_ui.py to comment out #import enkiicons_rc
    ..\..\pyinstaller-git\pyinstaller.py --additional-hooks-dir=win -y bin\enki
    
Bugs
-----
Still trying to get navigator to work.
