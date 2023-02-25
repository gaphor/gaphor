#
# To update the version, run:
#
#    make update VERSION=a.b.c
#

ID := Gaphor-x86_64
# Do not change version by hand!
VERSION := 2.17.0

BUILD := build
DIST := dist

all: dist

dist:
	./build-appimage.sh

update: version appdata

version:
	sed -i "s/^VERSION .*/VERSION := ${VERSION}/" Makefile

appdata:
	sed -i '/  <releases>/a \ \ \ \ <release version="$(VERSION)" date="$(shell date +%Y-%m-%d)"/>' org.gaphor.Gaphor.appdata.xml
