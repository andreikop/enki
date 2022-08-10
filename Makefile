VERSION=$(shell ./setup.py --version)
AUTHOR=$(shell ./setup.py --author)
AUTHOR_EMAIL=$(shell ./setup.py --author-email)
PACKAGE_NAME=$(shell ./setup.py --name)
ARCHIVE=$(PACKAGE_NAME)-$(VERSION).tar.gz

ENV=DEBFULLNAME="$(AUTHOR)" DEBEMAIL=$(AUTHOR_EMAIL) EDITOR=nvim

DEBIGAN_ORIG_ARCHIVE=${PACKAGE_NAME}_${VERSION}.orig.tar.gz

DEB_BUILD_DIR=build/deb

OBS_REPO=home:hlamer:enki
OBS_REPO_DIR=build/obs_home_hlamer_enki



all install:
	@echo This Makefile does not build and install the project.
	@echo Use setup.py script
	@exit -1


bump-version:
	nvim enki/core/defines.py +9
	nvim rpm/enki.spec +8
	nvim win/Enki.iss +11


changelog-update:
	cd debian && \
		$(ENV) dch -v $(VERSION)-1~ubuntuseries1 -b --distribution ubuntuseries
	nvim rpm/enki.spec +105


dist/${ARCHIVE}:
	rm -rf dist
	./setup.py sdist


deb-obs: dist/${ARCHIVE}
	rm -rf ${DEB_BUILD_DIR}
	mkdir -p ${DEB_BUILD_DIR}
	cp dist/${ARCHIVE} ${DEB_BUILD_DIR}/${DEBIGAN_ORIG_ARCHIVE}
	cd ${DEB_BUILD_DIR} && tar -xf ${DEBIGAN_ORIG_ARCHIVE}
	cp -r debian ${DEB_BUILD_DIR}/${PACKAGE_NAME}-${VERSION}
	sed -i s/ubuntuseries/obs/g ${DEB_BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian/changelog
	cd ${DEB_BUILD_DIR}/${PACKAGE_NAME}-${VERSION} && $(ENV) debuild -us -uc -S

${OBS_REPO_DIR}:
	rm -rf ${OBS_REPO}
	osc co ${OBS_REPO} enki
	mkdir -p build
	mv ${OBS_REPO} ${OBS_REPO_DIR}

put-obs: ${OBS_REPO_DIR} deb-obs
	rm -f ${OBS_REPO_DIR}/enki/*
	cp rpm/enki.spec ${OBS_REPO_DIR}/enki
	cp dist/${ARCHIVE} ${OBS_REPO_DIR}/enki
	cp ${DEB_BUILD_DIR}/*.debian.tar.xz ${OBS_REPO_DIR}/enki
	cp ${DEB_BUILD_DIR}/*.orig.tar.gz ${OBS_REPO_DIR}/enki
	cp ${DEB_BUILD_DIR}/*.dsc ${OBS_REPO_DIR}/enki
	cd ${OBS_REPO_DIR}/enki && \
		osc addremove && \
		osc ci -m 'update by the publish script'

sdist:
	./setup.py sdist --formats=gztar,zip

help:
	@echo 'bump-version                Open version file to edit'
	@echo 'changelog-update            Update Debian and RedHat changelogs'
	@echo 'put-obs                     Upload version to OBS'
	@echo 'sdist                       Make source distribution'
