#
# To update the version, run:
#
#    make update VERSION=a.b.c
#

ID := Gaphor-x86_64
# Do not change version by hand!
VERSION := 2.1.1

DIST := dist

all: dist

dist: requirements.txt entrypoint.sh $(ID).AppImage

dep:
	pip install python_appimage

update: clean version appdata requirements.txt
	$(MAKE) clean all

version:
	sed -i "s/^VERSION .*/VERSION := ${VERSION}/" Makefile

appdata:
	sed -i '/  <releases>/a \ \ \ \ <release version="$(VERSION)" date="$(shell date +%Y-%m-%d)"/>' share/org.gaphor.Gaphor.appdata.xml

entrypoint.sh:
	cp entrypoint.sh.in entrypoint.sh

requirements.txt:
	poetry export --without-hashes -o ${CURDIR}/requirements.txt
	sed -i -r 's/(^.+);.*/\1/g' requirements.txt
	echo 'gaphor==${VERSION}' >> requirements.txt

$(ID).AppImage: requirements.txt entrypoint.sh
	python-appimage build app $(CURDIR)

clean:
	rm -f entrypoint.sh
	rm -f requirements.txt
	rm -f $(ID).AppImage

# for local testing:

run: $(ID).AppImage
	./$(ID).AppImage
