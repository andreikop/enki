# *******************************************
# ci.py - Continuous integration setup script
# *******************************************
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import sys
import os
import os.path
#
# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
# Add the path to the ``ci_utils`` so we can import from it.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                '..', 'qutepart', 'tests', 'ci')))
from utils import (xqt, pushd, build_os, system_identify, wget, mkdir,
                   command_line_invoke, OS_Dispatcher, unzip, isfile)
import qutepart_travis
from qutepart_appveyor import DOWNLOADS
#
# A repeated version specifier for ctags. When updating this, make sure to
# change the path in the call to ``wget`` as well.
CTAGS_VER = 'ctags58'
#
#
# CI_Dispatcher
# =============
# This provides OS-specific installation of needed packages.
class CI_Dispatcher(OS_Dispatcher):
#
# Enki installs
# -------------
    def install_Windows(self):
        # ctags
        mkdir(DOWNLOADS)
        ctags_zip = os.path.join(DOWNLOADS, CTAGS_VER + '.zip')
        if not isfile(ctags_zip):
            wget('http://sourceforge.net/projects/ctags/files/ctags/5.8/{}.zip'.
                 format(CTAGS_VER), ctags_zip)
        unzip(ctags_zip, CTAGS_VER + '/ctags.exe')
        xqt('dir')

    def install_Linux(self):
        # Need to install Qutepart dependencies the wheel can't capture, plus Enki
        # dependencies. Installing ``libstdc++6`` fixes ``ImportError: /usr/lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.18' not found (required by /home/travis/virtualenv/python3.5.2/lib/python3.5/site-packages/PyQt5/Qt/lib/libQt5WebEngineCore.so.5)`` on Appveyor.
        xqt('sudo apt-get install -y ctags libpcre3-dev libegl1-mesa libstdc++6')

    def install_OS_X(self):
        xqt('brew install ctags pcre')
#
# install
# =======
def install():
    system_identify()

    # Install OS-dependent items.
    cid = CI_Dispatcher()
    cid.install()

    if build_os == 'Linux':
        qutepart_travis.set_display()
        xqt('sh -e /etc/init.d/xvfb start')
    xqt('python -m pip install -e .')

#
# test
# ====
def test():
    if build_os == 'Windows':
        # The PATH can't be set in install_, since changes to the environment
        # get lost when Python quits.
        os.environ['PATH'] = CTAGS_VER + '\\;' + os.environ['PATH']
    else:
        qutepart_travis.set_display()

    with pushd('tests'):
        xqt('python run_all.py')
#
# main
# ====
def main():
    command_line_invoke(install, test)

if __name__ == '__main__':
    main()
