FROM ubuntu:18.04 AS build
LABEL maintainer="dan@yeaw.me"
LABEL org.opencontainers.image.source=https://github.com/gaphor/gaphor

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PY_VERSION="3.10" \
    FONTCONFIG_VERSION="2.13.1" \
    DEBIAN_FRONTEND=noninteractive

# Enable source lists for build-dep
RUN sed -i -- 's/#deb-src/deb-src/g' /etc/apt/sources.list && \
    sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list

# Python deadsnakes
RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common \
 && add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update && apt-get install -y --no-install-recommends \
`# Common dependencies` \
    build-essential \
    wget \
`# jhbuild dependencies` \
    autoconf \
    automake \
    autopoint \
    bison \
    desktop-file-utils \
    doxygen \
    flex \
    gettext \
    git \
    libcups2-dev \
    libdbus-1-dev \
    libegl1-mesa-dev \
    libffi-dev \
    libgl1-mesa-dev \
    libgraphviz-dev \
    libicu-dev \
    libjpeg-turbo8-dev \
    libpcre3-dev \
    libtool \
    libx11-dev \
    libxcursor-dev \
    libxext-dev \
    libxft-dev \
    libxi-dev \
    libxkbcommon-dev \
    libxkbcommon-x11-dev \
    libxml2-dev \
    libxrender-dev \
    libxslt1-dev \
    libxtst-dev \
    make \
    ninja-build \
    patch \
    pkg-config \
    python \
    python-gi-dev \
    python3 \
    python3-dbus \
    python3-dev \
    python3-flake8 \
    python3-pytest \
    ragel \
    shared-mime-info \
    trang \
    xmlto \
    yelp-tools \
`# Dependency missed by jhbuild sysdeps` \
    libxrandr-dev \
`# Dependency for building a deb package` \
    devscripts \
`# Python deadsnakes` \
    python$PY_VERSION \
    python$PY_VERSION-dev \
    python$PY_VERSION-venv \
    python$PY_VERSION-distutils \
 && python$PY_VERSION -m ensurepip --upgrade \
 && python$PY_VERSION -m pip install --upgrade pip \
 && python$PY_VERSION -m pip install --upgrade requests urllib3 \
`# fontconfig dependencies` \
 && apt-get build-dep -y fontconfig \
 && apt-get install -y --no-install-recommends uuid-dev \
 && rm -rf /var/lib/apt/lists/*

# Build updated fontconfig deb files
RUN wget -q https://www.freedesktop.org/software/fontconfig/release/fontconfig-$FONTCONFIG_VERSION.tar.gz \
 && apt-get update \
 && apt-get source fontconfig \
 && rm -rf /var/lib/apt/lists*
WORKDIR /fontconfig-2.12.6
RUN uupdate ../fontconfig-$FONTCONFIG_VERSION.tar.gz
WORKDIR /fontconfig-$FONTCONFIG_VERSION
RUN dpkg-buildpackage --unsigned-source --unsigned-changes --no-pre-clean
WORKDIR /
RUN dpkg -i *.deb \
 && rm *.deb \
 && rm -r /fontconfig-* \
`# Make Deadsnakes Python the default python3` \
 && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python$PY_VERSION 1

ENV CHECKOUT=/root/jhbuild/checkout \
    LD_LIBRARY_PATH="/root/jhbuild/install/lib" \
    PKG_CONFIG_PATH="/root/jhbuild/install/lib/pkgconfig" \
    PATH="/root/jhbuild/install/bin:/root/.local/bin:$PATH" \
    JHBUILD_RUN_AS_ROOT=""

# Install jhbuild
RUN mkdir -p $CHECKOUT
WORKDIR $CHECKOUT
RUN git clone --depth=1 https://gitlab.gnome.org/GNOME/jhbuild.git
WORKDIR $CHECKOUT/jhbuild
RUN ./autogen.sh --simple-install \
 && make \
 && make install
WORKDIR /

# Configure jhbuild
COPY jhbuildrc /root/.config/jhbuildrc

# Build GTK, GtkSourceView, and gobject-introspection
RUN jhbuild build
