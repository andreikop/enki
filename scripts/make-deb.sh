#!/bin/bash

export DEBFULLNAME=`./setup.py --author`
export DEBEMAIL=`./setup.py --author-email`
VERSION=`./setup.py --version`
LICENSE=`./setup.py --license`
PACKAGE_NAME=`./setup.py --name`
ARCHIVE=dist/${PACKAGE_NAME}-${VERSION}.tar.gz
BUILD_DIR=${PACKAGE_NAME}-${VERSION}

./setup.py sdist

rm -rf build
mkdir build
cd build
tar -xf ../${ARCHIVE}
cd ${BUILD_DIR}

dh_make \
    --file=../../${ARCHIVE} \
    --copyright=${LICENSE} \
    --single \
    --createorig

cd debian && rm *.ex *.EX README.Debian && cd -
cp ../../debian/* debian
echo '2.7-' > debian/pyversions
debuild -S -us -uc
debuild -us -uc
