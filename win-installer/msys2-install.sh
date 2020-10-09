#!/bin/bash

set -euo pipefail

export MSYS2_FC_CACHE_SKIP=1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cp /etc/pacman.d/mirrorlist.mingw64 /etc/pacman.d/mirrorlist.backup
rankmirrors -r mingw64 -n 3 -v /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist.mingw64
echo "$(cat /etc/pacman.d/mirrorlist.mingw64)"

pacman --noconfirm -Suy

pacman --noconfirm -S --needed \
    mingw-w64-x86_64-make \
    mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-gtk3 \
    mingw-w64-x86_64-pkg-config \
    mingw-w64-x86_64-cairo \
    mingw-w64-x86_64-gobject-introspection \
    mingw-w64-x86_64-python \
    mingw-w64-x86_64-python-gobject \
    mingw-w64-x86_64-python-cairo \
    mingw-w64-x86_64-python-pip \

# shellcheck source=venv
source "$DIR"/../venv
pip install pyinstaller==3.6.0
mingw32-make translations
