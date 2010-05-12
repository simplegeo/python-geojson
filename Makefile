ROOTCMD      = fakeroot
BUILD_NUMBER ?= 1

.PHONY: debian/changelog

debian/changelog:
	-git branch -D changelog
	git checkout -b changelog
	git-dch -a --debian-branch changelog --snapshot \
            --snapshot-number=$(BUILD_NUMBER)

deb: debian/changelog
	dpkg-buildpackage -r$(ROOTCMD) -us -uc -b

sdist:
	python setup.py sdist

clean:
	rm -rf dist
	$(ROOTCMD) debian/rules clean
