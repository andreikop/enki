VERSION=$(shell ./setup.py --version)
AUTHOR=$(shell ./setup.py --author)
AUTHOR_EMAIL=$(shell ./setup.py --author-email)
PACKAGE_NAME=$(shell ./setup.py --name)
ARCHIVE=$(PACKAGE_NAME)-$(VERSION).tar.gz

ENV=DEBFULLNAME="$(AUTHOR)" DEBEMAIL=$(AUTHOR_EMAIL) EDITOR=enki

DEBIGAN_ORIG_ARCHIVE=${PACKAGE_NAME}_${VERSION}.orig.tar.gz

all install:
	@echo This Makefile does not build and install the project.
	@echo Use setup.py script
	@exit -1

changelog-update:
	cd debian && \
		$(ENV) dch -v $(VERSION)-1~ppa1 -b --distribution lucid

dsc:
	rm -rf dist
	rm -rf build
	./setup.py sdist
	mkdir build
	cp dist/${ARCHIVE} build/${DEBIGAN_ORIG_ARCHIVE}
	cd build && tar -xf ${DEBIGAN_ORIG_ARCHIVE}
	cp -r debian build/${PACKAGE_NAME}-${VERSION}
	cd build/${PACKAGE_NAME}-${VERSION} && \
		$(ENV) debuild -us -uc -S

	cd build/${PACKAGE_NAME}-${VERSION} && \
		$(ENV) debsign ../*.changes

dput: dsc
	cd build && dput enki *.changes

deb: dsc
	cd build/enki-$(VERSION) && debuild

sdist:
	./setup.py sdist --formats=gztar,zip
