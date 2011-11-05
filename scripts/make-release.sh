#!/bin/sh

VERSION=`python -c 'import mks.core.defines; print mks.core.defines.PACKAGE_VERSION'`
git archive --format=tar --prefix=mksv3-${VERSION}/ HEAD | gzip > mksv3-${VERSION}.tar.gz
