FROM ubuntu:18.04 AS build
LABEL maintainer="dan@yeaw.me"
LABEL org.opencontainers.image.source=https://github.com/gaphor/gaphor

# WORKDIR is not used to be compatible with GitHub Actions:
# https://docs.github.com/en/actions/creating-actions/dockerfile-support-for-github-actions#workdir

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PY_VERSION="3.11" \
    FONTCONFIG_VERSION="2.14.2" \
    GITHUB_CLI_VERSION="2.23.0" \
    DEBIAN_FRONTEND=noninteractive

# Enable source lists for build-dep
RUN sed -i -- 's/#deb-src/deb-src/g' /etc/apt/sources.list \
 && sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list

# Add packages / repositories for Python deadsnakes, PowerShell, and GitHub CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    software-properties-common \
    wget \
    git \
 && add-apt-repository ppa:deadsnakes/ppa \
 && add-apt-repository ppa:git-core/ppa \
 && wget -q https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb \
 && dpkg -i packages-microsoft-prod.deb \
 && wget -q https://github.com/cli/cli/releases/download/v${GITHUB_CLI_VERSION}/gh_${GITHUB_CLI_VERSION}_linux_amd64.deb \
 && dpkg -i gh_${GITHUB_CLI_VERSION}_linux_amd64.deb \
 && apt-get update && apt-get install -y --no-install-recommends \
`# Common dependencies` \
    build-essential \
`# GitHub Actions dependencies` \
    xvfb \
    powershell \
    gh \
`# jhbuild dependencies` \
    autoconf \
    automake \
    autopoint \
    bison \
    cargo  \
    desktop-file-utils \
    doxygen \
    flex \
    gettext \
    git \
    libcanberra-gtk3-dev \
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
    python3-lxml \
    python3-wheel \
    python3-setuptools \
    ragel \
    shared-mime-info \
    trang \
    xmlto \
    yelp-tools \
    libarchive-dev \
    libsqlite3-dev \
    libyaml-dev \
    cmake \
`# Dependency missed by jhbuild sysdeps` \
    libxrandr-dev \
`# Dependency for building a deb package` \
    devscripts \
`# Other Gaphor dependencies` \
    gnome-settings-daemon-schemas \
    graphviz \
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
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/* \
 && rm packages-microsoft-prod.deb

# Build updated fontconfig deb files
RUN wget -q https://www.freedesktop.org/software/fontconfig/release/fontconfig-$FONTCONFIG_VERSION.tar.gz \
 && apt-get update \
 && apt-get source fontconfig \
 && rm -rf /var/lib/apt/lists* \
 && cd /fontconfig-2.12.6 \
 && uupdate ../fontconfig-$FONTCONFIG_VERSION.tar.gz \
 && cd /fontconfig-$FONTCONFIG_VERSION \
 && dpkg-buildpackage --unsigned-source --unsigned-changes --no-pre-clean \
 && cd / \
 && dpkg -i *.deb \
 && rm *.deb *.ddeb *.tar.xz *.tar.bz2 *.dsc *.buildinfo *.changes \
 && rm -r /fontconfig-* \
`# Make Deadsnakes Python the default python3` \
 && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python$PY_VERSION 1

# Newer rust is needed by librsvg
RUN apt-get update \
  && apt-get remove -y rustc cargo \
  && apt-get install -y --no-install-recommends curl \
  && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
  && apt-get remove -y curl \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

ENV CHECKOUT=/root/jhbuild/checkout \
    LD_LIBRARY_PATH="/root/jhbuild/install/lib:/root/jhbuild/install/local/lib" \
    PKG_CONFIG_PATH="/root/jhbuild/install/lib/pkgconfig" \
    PATH="/root/jhbuild/install/bin:/root/jhbuild/install/local/bin:/root/.local/bin:/root/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/jhbuild/install/local/lib/python3.11/dist-packages" \
    PYTHONPATH="/root/jhbuild/install/local/lib/python3.11/dist-packages" \
    JHBUILD_RUN_AS_ROOT=""

# Install jhbuild
RUN mkdir -p $CHECKOUT \
 && cd $CHECKOUT \
 && git clone --depth=1 https://gitlab.gnome.org/GNOME/jhbuild.git \
 && cd $CHECKOUT/jhbuild \
 && ./autogen.sh --simple-install \
 && make \
 && make install

# Configure jhbuild
COPY jhbuildrc /root/.config/jhbuildrc

# Build GTK, GtkSourceView, and gobject-introspection
RUN jhbuild build \
 && rm -r /root/.config \
 && rm -r /root/.cache

# Environmental variable needed to run GTK for gsettings schema
ENV XDG_DATA_DIRS="/root/jhbuild/install/share:/usr/share"

# Install pipx
RUN python3 -m pip install pipx
ENV PIPX_BIN_DIR=/root/.local/bin
