#!/bin/bash

set -euo pipefail

export MSYS2_FC_CACHE_SKIP=1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pacman --noconfirm -Suy

pacman --noconfirm -S --needed \
    git \
    make \
    mingw-w64-"$MSYS2_ARCH"-freetype-2.10.1-1-any \
    mingw-w64-"$MSYS2_ARCH"-gcc \
    mingw-w64-"$MSYS2_ARCH"-gtk3 \
    mingw-w64-"$MSYS2_ARCH"-pkg-config \
    mingw-w64-"$MSYS2_ARCH"-cairo \
    mingw-w64-"$MSYS2_ARCH"-gobject-introspection \
    mingw-w64-"$MSYS2_ARCH"-python \
    mingw-w64-"$MSYS2_ARCH"-python-gobject \
    mingw-w64-"$MSYS2_ARCH"-python-cairo \
    mingw-w64-"$MSYS2_ARCH"-python-pip \

source "$DIR"/../venv
pip install pyinstaller
make translate
