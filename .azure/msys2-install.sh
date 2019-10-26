#!/bin/bash

set -e

export MSYS2_FC_CACHE_SKIP=1

pacman --noconfirm -Suy

pacman --noconfirm -S --needed \
    git \
    mingw-w64-$MSYS2_ARCH-gcc \
    mingw-w64-$MSYS2_ARCH-gtk3 \
    mingw-w64-$MSYS2_ARCH-pkgconfig \
    mingw-w64-$MSYS2_ARCH-cairo \
    mingw-w64-$MSYS2_ARCH-python3 \
    mingw-w64-$MSYS2_ARCH-python3-gobject \
    mingw-w64-$MSYS2_ARCH-python3-cairo \
    mingw-w64-$MSYS2_ARCH-python3-pip \
    mingw-w64-$MSYS2_ARCH-python3-setuptools \
    mingw-w64-$MSYS2_ARCH-python3-zope.interface \
    mingw-w64-$MSYS2_ARCH-python3-coverage \
    mingw-w64-$MSYS2_ARCH-python3-pytest

pip3 install pycairo==1.18.0 PyGObject==3.30.4 gaphas==1.0.0 zope.component==4.5 tomlkit==0.5.3
pip3 install .