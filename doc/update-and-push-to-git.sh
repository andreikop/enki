#!/bin/sh

rm -rf /tmp/html
sphinx-build . /tmp/html
cd ..
git checkout gh-pages
rm -rf *
mv /tmp/html/* .
git add -A
git commit -m 'Documentation update'
git push
git checkout master

