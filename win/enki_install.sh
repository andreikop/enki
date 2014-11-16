#!/bin/sh
#
# *******************
# Enki install script
# *******************
# This script installs Enki and its dependencies from source. It is tested on
# Ubuntu 12.04.
#
# Common commands
# ===============
# Echo all commands.
set -o verbose
PAUSE="read -p Press_[Enter]_to_continue... junk"
INSTALL="sudo apt-get install -y"
#
# Source code and installs
# ========================
# Put everything in ``enki_all``.
mkdir enki_all
cd enki_all

# TRE
# ===
$INSTALL git build-essential autotools-dev automake gettext libtool autopoint zip python-pip python-dev python-setuptools
# See https://github.com/bjones1/tre.
git clone https://github.com/bjones1/tre.git
cd tre
./utils/autogen.sh
$PAUSE
./configure
$PAUSE
make
$PAUSE
sudo make install
$PAUSE
cd python
sudo python setup.py install
# Note: the line below should be added to your .bashrc,
export LD_LIBRARY_PATH=/usr/local/lib
$PAUSE
cd ../..

# Qutepart
# ========
$INSTALL libpcre3 libpcre3-dev python-qt4
# See https://github.com/hlamer/qutepart.
git clone https://github.com/bjones1/qutepart.git
cd qutepart
# See https://help.github.com/articles/adding-a-remote/.
git remote add upstream https://github.com/hlamer/qutepart.git
sudo python setup.py install
$PAUSE
cd ..

# Enki
# ====
$INSTALL desktop-file-utils exuberant-ctags python-pyparsing python-markdown python-sphinx pylint
sudo pip install CodeChat
# See https://github.com/bjones1/enki.
git clone https://github.com/bjones1/enki.git
cd enki
git remote add upstream https://github.com/hlamer/enki.git
$PAUSE
cd ..

# PyInstaller
# ===========
# See http://www.pyinstaller.org/.
git clone git://github.com/pyinstaller/pyinstaller.git
cd pyinstaller
sudo python setup.py install
$PAUSE
cd ..

cd ..
