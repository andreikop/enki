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
# Set up alias for repeated commands.
PAUSE="read -p Press_[Enter]_to_continue... junk"
INSTALL="sudo apt-get install -y"
#INSTALL="sudo yum install -y" # Fedora
#
# Source code and installs
# ========================
# Put everything in ``enki_all``.
mkdir enki_all
cd enki_all

# TRE
# ===
# Fedora: git gcc make                      automake gettext libtool gettext-devel zip python-devel python-pip
$INSTALL  git build-essential autotools-dev automake gettext libtool autopoint     zip python-dev   python-pip
# Upgrade pip first.
sudo pip install -U pip
# Then install Python packages from pip, since apt-get packages are older.
sudo pip install -U setuptools
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
# Note: the line below should be added to your .bashrc.
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
$PAUSE
cd ../..

# CodeChat
# ========
$INSTALL mercurial
hg clone https://bitbucket.org/bjones/documentation CodeChat
cd CodeChat
sudo python setup.py develop
$PAUSE
cd ..

# Qutepart
# ========
# Fedora: pcre     pcre-devel   python-qt4
$INSTALL  libpcre3 libpcre3-dev python-qt4
# See https://github.com/hlamer/qutepart.
git clone https://github.com/bjones1/qutepart.git
cd qutepart
sudo python setup.py install
$PAUSE
cd ..

# Enki
# ====
# Fedora: desktop-file-utils ctags
$INSTALL  desktop-file-utils exuberant-ctags # On Fedora, use ctags.
# Then install Python packages from pip, since apt-get packages are older.
sudo pip install -U mock markdown sphinx pylint
# See https://github.com/bjones1/enki.
git clone https://github.com/bjones1/enki.git
cd enki
$PAUSE
cd ..

# Python-markdown-mathjax
# =======================
# See https://github.com/mayoff/python-markdown-mathjax.
wget https://raw.githubusercontent.com/mayoff/python-markdown-mathjax/master/mdx_mathjax.py
MARKDOWN_PATH=`python -c 'import markdown; print markdown.__path__[0]'`
# Per the instructions, rename to mathjax.py and install in the markdown
# extensions folder.
sudo cp mdx_mathjax.py $MARKDOWN_PATH/extensions/mathjax.py

# PyInstaller
# ===========
# See http://www.pyinstaller.org/.
git clone git://github.com/pyinstaller/pyinstaller.git
cd pyinstaller
sudo python setup.py install
$PAUSE
cd ..

cd ..
