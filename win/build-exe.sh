#!/bin/sh
#
#
# ********************************************************************************************
# build-exe.sh - Shell script to build a Linux binary to Enki and its supporting applications.
# ********************************************************************************************
# Prepare
# =======
# Scraps from the previous build may disturb the current build. Get rid of it.
rm -rf build/ dist/
#
# Build
# =====
pyinstaller -y win/enki-sphinx.spec
#
# Combine
# =======
# Enki on Linux needs this directory to exist in order to work.
# It imports things relative to this path, fails if this path
# doesn't exist.
mkdir dist/enki/enki/core
cp -r dist/sphinx-build/* dist/enki
cp -r dist/pylint/* dist/enki
cp /usr/bin/ctags dist/enki
#
# Test
# ====
read -p "Press enter to run the resulting binary..." junk
dist/enki/enki-editor
#
# Package
# =======
read -p "Press enter to compress the resulting binary..." junk
cd dist
zip -r enki.zip enki
cd ..
