ROOTCMD      = fakeroot
BUILD_NUMBER ?= 1

.PHONY: debian/changelog

debian/changelog:
	git-dch -a --snapshot --snapshot-number=$(BUILD_NUMBER)

deb: debian/changelog
	dpkg-buildpackage -r$(ROOTCMD) -us -uc -b

sdist:
	python setup.py sdist

clean:
	rm -rf dist
	$(ROOTCMD) debian/rules clean
