#!/bin/bash

#
# Script excects, that dist/ directory contains one .tar.gz archive
#

export DEBFULLNAME=`./setup.py --author`
export DEBEMAIL=`./setup.py --author-email`
PACKAGE_NAME=`./setup.py --name`
ARCHIVE=`ls dist/*.tar.gz`

# Version of archive, not a actual version from setup.py
# It might be needed to repack old versions
VERSION=${ARCHIVE/dist\/${PACKAGE_NAME}-/}
VERSION=${VERSION/.tar.gz/}

DEBIGAN_ORIG_ARCHIVE=${PACKAGE_NAME}_${VERSION}.orig.tar.gz
rm -r build
mkdir build
cd build

cp ../${ARCHIVE} ${DEBIGAN_ORIG_ARCHIVE}
tar -xf ${DEBIGAN_ORIG_ARCHIVE}
cd ${PACKAGE_NAME}-${VERSION}
cp -R ../../debian/ .
debuild -us -uc -S

debsign ../*.changes
