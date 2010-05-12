BASE        ?= $(PWD)
GIT_HEAD     = $(BASE)/.git/$(shell cut -d\  -f2-999 .git/HEAD)
ROOTCMD      = fakeroot
BUILD_NUMBER ?= 1

debian/changelog: $(GIT_HEAD)
	git-dch -a --snapshot --snapshot-number=$(BUILD_NUMBER)

deb: debian/changelog
	dpkg-buildpackage -r$(ROOTCMD) -us -uc -b

sdist:
	python setup.py sdist

clean:
	rm -rf dist
	$(ROOTCMD) debian/rules clean
