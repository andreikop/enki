#!/bin/bash

export DEBFULLNAME=`./setup.py --author`
export DEBEMAIL=`./setup.py --author-email`
VERSION=`./setup.py --version`
LICENSE=`./setup.py --license`
PACKAGE_NAME=`./setup.py --name`
ARCHIVE=../dist/${PACKAGE_NAME}-${VERSION}.tar.gz

./setup.py sdist


rm -rf build
mkdir build
cd build

dh_make \
    --packagename=mksv3_${VERSION} \
    --file=${ARCHIVE} \
    --copyright=${LICENSE} \
    --single

cd debian && rm *.ex *.EX README.Debian && cd -
cd ../files-for-deb && cp changelog control copyright ../build/debian && cd -
echo '2.7-' > debian/pyversions
debuild -us -uc
