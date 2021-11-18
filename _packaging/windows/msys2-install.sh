#!/bin/bash

set -euo pipefail

export MSYS2_FC_CACHE_SKIP=1

pacman --noconfirm -Suy

pacman --noconfirm -S --needed \
    git \
    upx \
    mingw-w64-x86_64-make \
    mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-gtk3 \
    mingw-w64-x86_64-gtksourceview4 \
    mingw-w64-x86_64-pkgconf \
    mingw-w64-x86_64-nsis \
    mingw-w64-x86_64-cairo \
    mingw-w64-x86_64-gobject-introspection \
    mingw-w64-x86_64-python \
    mingw-w64-x86_64-python-pip \
    mingw-w64-x86_64-python-setuptools
