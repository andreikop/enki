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
#INSTALL="sudo yum install -y" # Fedora
#
# Source code and installs
# ========================
# Put everything in ``enki_all``.
mkdir enki_all
cd enki_all
#
# CodeChat
# ========
$INSTALL mercurial
hg clone https://bitbucket.org/bjones/documentation CodeChat
cd CodeChat
sudo python setup.py develop
$PAUSE
cd ..
#
# Qutepart
# ========
# Fedora: pcre     pcre-devel   python-qt4
$INSTALL  libpcre3 libpcre3-dev python-qt4
git clone https://github.com/hlamer/qutepart.git
cd qutepart
sudo python setup.py install
$PAUSE
cd ..
#
# Enki
# ====
# Fedora: desktop-file-utils ctags
$INSTALL  desktop-file-utils exuberant-ctags
# Then install Python packages from pip, since apt-get packages are older.
sudo pip install -U mock markdown sphinx flake8 regex
git clone https://github.com/hlamer/enki.git
cd enki
$PAUSE
cd ..
#
# Python-markdown-mathjax
# =======================
# See https://github.com/mayoff/python-markdown-mathjax.
wget https://raw.githubusercontent.com/mayoff/python-markdown-mathjax/master/mdx_mathjax.py
MARKDOWN_PATH=`python -c 'import markdown; print markdown.__path__[0]'`
# Per the instructions, rename to mathjax.py and install in the markdown
# extensions folder.
sudo cp mdx_mathjax.py $MARKDOWN_PATH/extensions/mathjax.py

cd ..
