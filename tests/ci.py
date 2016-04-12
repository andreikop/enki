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
from utils import (xqt, pushd, chdir, build_os, system_identify, wget,
                   command_line_invoke, OS_Dispatcher, unzip, isfile)
import qutepart_appveyor
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
# Qutepart installs
# -----------------
# The argument of ``False`` omits ``system_identify`` output from qutepart's
# install; Enki has already printed this.
    def install_qutepart_Windows(self):
        qutepart_appveyor.install(False)

    def install_qutepart_Linux(self):
        qutepart_travis.install(False)

    def install_qutepart_OS_X(self):
        self.install_qutepart_Linux()
#
# Enki installs
# -------------
    def install_Windows(self):
        # ctags
        ctags_zip = os.path.join(DOWNLOADS, CTAGS_VER + '.zip')
        if not isfile(ctags_zip):
            wget('http://sourceforge.net/projects/ctags/files/ctags/5.8/{}.zip'.
                 format(CTAGS_VER), ctags_zip)
        unzip(ctags_zip, CTAGS_VER + '/ctags.exe')

    def install_Linux(self):
        xqt('sudo apt-get install -y ctags')

    def install_OS_X(self):
        xqt('brew install ctags')
#
# install
# =======
def install():
    system_identify()

    # First, install OS-independent items. Install the development version of
    # CodeChat, rather than the (older) released version on PyPI that the pip
    # install would do.
    xqt('git clone https://github.com/bjones1/CodeChat.git')
    with pushd('CodeChat'):
        xqt('python setup.py install')
    xqt('python -m pip install -U -r requirements.txt')

    # Install OS-dependent items.
    cid = CI_Dispatcher()
    # The qutepart install script assumes the working directory is qutepart.
    with pushd('qutepart'):
        cid.install_qutepart()
    cid.install()
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
