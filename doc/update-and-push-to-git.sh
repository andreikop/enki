#!/bin/sh

rm -rf /tmp/html
sphinx-build . /tmp/html
cd ..
git checkout gh-pages || exit 1
rm -rf *
mv /tmp/html/* .
mv _static static
mv _sources sources
perl -pi -e "s/_sources/sources/g;" *.html
perl -pi -e "s/_static/static/g;" *.html
git add -A
git commit -m 'Documentation update'
git push
git checkout master

