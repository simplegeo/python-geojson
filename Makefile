ROOTCMD       = fakeroot
SIGN_KEY     ?= nerds@simplegeo.com
BUILD_NUMBER ?= 1

.PHONY: debian/changelog

debian/changelog:
	-git branch -D changelog
	git checkout -b changelog
	git-dch -N $(shell python setup.py --version) -a --debian-branch changelog \
            --snapshot --snapshot-number=$(BUILD_NUMBER)

dist:
	mkdir -p $@

deb: debian/changelog dist
	dpkg-buildpackage -r$(ROOTCMD) -k$(SIGN_KEY)
	test -d dist/deb || mkdir -p dist/deb
	mv ../python-simplegeo-geojson_* dist/deb

sdist:
	python setup.py sdist

clean:
	rm -rf dist
	$(ROOTCMD) debian/rules clean
