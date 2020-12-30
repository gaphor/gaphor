#
# To update the version, run:
#
#    make update VERSION=a.b.c
#

ID := Gaphor-x86_64
# Do not change version by hand!
VERSION := 2.1.1

BUILD := build
DIST := dist

all: dist

dist: $(DIST)/$(ID).AppImage

update: clean version appdata
	$(MAKE) clean all

version:
	sed -i "s/^VERSION .*/VERSION := ${VERSION}/" Makefile

appdata:
	sed -i '/  <releases>/a \ \ \ \ <release version="$(VERSION)" date="$(shell date +%Y-%m-%d)"/>' share/org.gaphor.Gaphor.appdata.xml

$(DIST)/$(ID).AppImage:
	./build-appimage.sh

lint: $(DIST)/$(ID).AppImage
	./appdir-lint.sh $(DIST)/AppRun

clean:
	rm -f entrypoint.sh
	rm -rf $(BUILD)
	rm -rf $(DIST)
	rm -rf pyinstvenv
	rm -f $(subst $(notdir $(CURDIR)),,$(CURDIR))gaphor-script.py

# for local testing:

run: $(ID).AppImage
	./$(ID).AppImage
