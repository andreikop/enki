VERSION=$(shell ./setup.py --version)
AUTHOR=$(shell ./setup.py --author)
AUTHOR_EMAIL=$(shell ./setup.py --author-email)

all install:
	@echo This Makefile does not build and install the project.
	@echo Use setup.py script
	@exit -1

changelog-update:
	cd debian && DEBFULLNAME="$(AUTHOR)" DEBEMAIL=$(AUTHOR_EMAIL) dch -v $(VERSION)-1~lucid1 -b

dsc:
	rm -rf dist
	./setup.py sdist
	./scripts/make-deb.sh

dput: dsc
	cd build && dput ppa:monkeystudio/ppa *.changes

deb: dsc
	cd build/mksv3-$(VERSION) && debuild