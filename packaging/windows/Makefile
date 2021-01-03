help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/^\([a-z]*\):.*## /  \1\t/' | expand -t14

all: dist

windows-dep:
	pacman -S --needed --noconfirm p7zip dos2unix upx mingw-w64-x86_64-nsis mingw-w64-x86_64-wget

dist: windows-dep 
	./build-win-installer.sh

.PHONY: windows-dep all help dist
