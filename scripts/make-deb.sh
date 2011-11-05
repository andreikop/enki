#!/bin/sh

export DEBFULLNAME='Andrei Kopats'

VERSION=`python -c 'import mks.core.defines; print mks.core.defines.PACKAGE_VERSION'`
ARCHIVE=`ls mksv3-*.tar.gz`

./scripts/make-release.sh

cd ubuntu
rm -rf debian mksv3*
dh_make \
    --packagename=mksv3_${VERSION} \
    --file=../${ARCHIVE} \
    --copyright=gpl2 \
    --email=hlamer@tut.by \
    --single

mv debian/menu.ex debian/menu
rm debian/*.ex debian/*.EX
cp changelog control copyright debian

#debuild -S


