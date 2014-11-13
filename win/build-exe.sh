#!/bin/sh
rm -rf build/ dist/
pyinstaller -y win/enki-sphinx.spec
mkdir dist/enki/enki/core
cp -r dist/sphinx-build/* dist/enki
# To do: copy over ctags, pylint.
dist/enki/enki-editor
