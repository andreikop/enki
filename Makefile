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


bump-version:
	enki enki/core/defines.py +10
	enki rpm/enki.spec +8
	enki win/Enki.iss +31


changelog-update:
	cd debian && \
		$(ENV) dch -v $(VERSION)-1~ubuntuseries1 -b --distribution ubuntuseries
	enki rpm/enki.spec +105


dist/${ARCHIVE}:
	rm -rf dist
	./setup.py sdist


deb-obs: dist/${ARCHIVE}
	rm -rf build/deb
	mkdir -p build/deb
	cp dist/${ARCHIVE} build/deb/${DEBIGAN_ORIG_ARCHIVE}
	cd build/deb && tar -xf ${DEBIGAN_ORIG_ARCHIVE}
	cp -r debian build/deb/${PACKAGE_NAME}-${VERSION}
	sed -i s/ubuntuseries/obs/g build/deb/${PACKAGE_NAME}-${VERSION}/debian/changelog
	cd build/deb/${PACKAGE_NAME}-${VERSION} && $(ENV) debuild -us -uc -S

build/obs_home_hlamer_enki:
	rm -rf home:hlamer:enki
	osc co home:hlamer:enki enki
	mkdir -p build
	mv home\:hlamer\:enki build/obs_home_hlamer_enki

put-obs: build/obs_home_hlamer_enki deb-obs
	rm -f build/obs_home_hlamer_enki/enki/*
	cp rpm/enki.spec build/obs_home_hlamer_enki/enki
	cp dist/${ARCHIVE} build/obs_home_hlamer_enki/enki
	cp build/*.debian.tar.gz build/obs_home_hlamer_enki/enki
	cp build/*.orig.tar.gz build/obs_home_hlamer_enki/enki
	cp build/*.dsc build/obs_home_hlamer_enki/enki
	cd build/obs_home_hlamer_enki/enki && \
		osc addremove && \
		osc ci -m 'update by the publish script'

sdist:
	./setup.py sdist --formats=gztar,zip

help:
	@echo 'bump-version                Open version file to edit'
	@echo 'changelog-update            Update Debian and RedHat changelogs'
	@echo 'put-obs                     Upload version to OBS'
	@echo 'sdist                       Make source distribution'
