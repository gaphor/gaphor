#!/bin/bash

set -euo pipefail

export MSYS2_FC_CACHE_SKIP=1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cp /etc/pacman.d/mirrorlist.mingw64 /etc/pacman.d/mirrorlist.backup
rankmirrors -r mingw64 -n 3 -v /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist.mingw64

pacman --noconfirm -Suy

pacman --noconfirm -S --needed \
    mingw-w64-"$MSYS2_ARCH"-make \
    mingw-w64-"$MSYS2_ARCH"-gcc \
    mingw-w64-"$MSYS2_ARCH"-gtk3 \
    mingw-w64-"$MSYS2_ARCH"-pkg-config \
    mingw-w64-"$MSYS2_ARCH"-cairo \
    mingw-w64-"$MSYS2_ARCH"-gobject-introspection \
    mingw-w64-"$MSYS2_ARCH"-python \
    mingw-w64-"$MSYS2_ARCH"-python-gobject \
    mingw-w64-"$MSYS2_ARCH"-python-cairo \
    mingw-w64-"$MSYS2_ARCH"-python-pip \

# shellcheck source=venv
source "$DIR"/../venv
pip install pyinstaller==3.6.0
mingw32-make translations
