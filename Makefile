VERSION=$(shell ./setup.py --version)
AUTHOR=$(shell ./setup.py --author)
AUTHOR_EMAIL=$(shell ./setup.py --author-email)
PACKAGE_NAME=$(shell ./setup.py --name)
ARCHIVE=$(PACKAGE_NAME)-$(VERSION).tar.gz

ENV=DEBFULLNAME="$(AUTHOR)" DEBEMAIL=$(AUTHOR_EMAIL) EDITOR=enki

DEBIGAN_ORIG_ARCHIVE=${PACKAGE_NAME}_${VERSION}.orig.tar.gz

ALL_SERIES = precise quantal raring

CURRENT_SERIES = $(shell lsb_release -cs)

all install:
	@echo This Makefile does not build and install the project.
	@echo Use setup.py script
	@exit -1

changelog-update:
	cd debian && \
		$(ENV) dch -v $(VERSION)-1~ubuntuseries1 -b --distribution ubuntuseries

dist/${ARCHIVE}:
	rm -rf dist
	./setup.py sdist

dsc-%: dist/${ARCHIVE}
	rm -rf build-$*
	mkdir build-$*
	cp dist/${ARCHIVE} build-$*/${DEBIGAN_ORIG_ARCHIVE}
	cd build-$* && tar -xf ${DEBIGAN_ORIG_ARCHIVE}
	cp -r debian build-$*/${PACKAGE_NAME}-${VERSION}
	sed -i s/ubuntuseries/$*/g build-$*/${PACKAGE_NAME}-${VERSION}/debian/changelog
	cd build-$*/${PACKAGE_NAME}-${VERSION} && $(ENV) debuild -us -uc -S
	cd build-$*/${PACKAGE_NAME}-${VERSION} && $(ENV) debsign ../*.changes

dput-%: dsc-%
	cd build-$* && dput enki-testing *.changes

dput-all: $(foreach series, $(ALL_SERIES), dput-$(series))
	echo

deb-$(CURRENT_SERIES): dsc-$(CURRENT_SERIES)
	cd build-$(CURRENT_SERIES)/$(PACKAGE_NAME)-$(VERSION) && debuild


sdist:
	./setup.py sdist --formats=gztar,zip
