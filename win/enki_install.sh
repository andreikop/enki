#!/bin/sh
#
# *******************
# Enki install script
# *******************
# This script installs Enki and its dependencies from source. It is tested on
# Ubuntu 12.04. Some testing is done on Fedora; see comments below.
#
# Common commands
# ===============
# Echo all commands.
set -o verbose
# Set up aliases for repeated commands.
PAUSE="read -p Press_[Enter]_to_continue... junk"
INSTALL="sudo apt-get install -y"
# Fedora
#INSTALL="sudo yum install -y"
#
# Source code and installs
# ========================
# Put everything in ``enki_all``.
mkdir enki_all
cd enki_all
#
# Qutepart
# ========
# Fedora: pcre     pcre-devel   python3-pyqt5
$INSTALL  libpcre3 libpcre3-dev python3-pyqt5
git clone https://github.com/hlamer/qutepart.git
cd qutepart
sudo python setup.py develop
$PAUSE
cd ..
#
# Enki
# ====
# Fedora: desktop-file-utils ctags
$INSTALL  desktop-file-utils exuberant-ctags
# Then install Python packages from pip, since apt-get packages are older.
sudo pip install -U mock markdown sphinx flake8 regex CodeChat
git clone https://github.com/hlamer/enki.git
cd enki
sudo python setup.py develop
$PAUSE
cd ..

cd ..
