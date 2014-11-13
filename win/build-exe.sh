#!/bin/sh
rm -rf build/ dist/
pyinstaller -y win/enki-sphinx.spec
mkdir dist/enki/enki/core
cp -r dist/sphinx-build/* dist/enki
cp /usr/bin/ctags dist/enki
dist/enki/enki-editor
