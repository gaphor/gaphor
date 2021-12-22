FROM ubuntu:18.04
LABEL maintainer="dan@yeaw.me"

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

ENV PYTHON_VERSION "3.10.1"
ENV PYTHON_VERSION_SHORT "3.10"

# Enable source lists for build-dep
RUN sed -i -- 's/#deb-src/deb-src/g' /etc/apt/sources.list && \
    sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND=noninteractive
# Common dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    sudo \
    vim \
    wget
# Python dependencies
RUN apt-get install -y \
    libbz2-dev \
    libc6-dev \
    libffi-dev \
    libgdbm-dev \
    libgdbm-compat-dev \
    libncursesw5-dev \
    libreadline-gplv2-dev \
    libsqlite3-dev \
    libssl-dev \
    tk-dev \
    zlib1g-dev
# Python deadsnakes
RUN apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-venv \
    python3.10-distutils
# fontconfig dependencies
RUN apt-get build-dep -y \
    fontconfig \
    && apt-get install -y \
    uuid-dev \
    devscripts
# jhbuild dependencies
RUN apt-get install -y \
    apt-file \
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
    yelp-tools
# Dependency missed by jhbuild sysdeps
RUN apt-get install -y \
    libxrandr-dev

# Build updated fontconfig deb files
RUN apt-get source fontconfig
ENV FONTCONFIG_VERSION 2.13.1
RUN wget -q https://www.freedesktop.org/software/fontconfig/release/fontconfig-$FONTCONFIG_VERSION.tar.gz
WORKDIR fontconfig-2.12.6
RUN uupdate ../fontconfig-$FONTCONFIG_VERSION.tar.gz
WORKDIR /fontconfig-$FONTCONFIG_VERSION
RUN dpkg-buildpackage -us -uc -nc
WORKDIR /
RUN dpkg -i *.deb

# Build apt-file search index for jhbuild
RUN apt-file update

# Cleanup
RUN rm -rf /var/lib/apt/lists/*

ENV USER gnome
RUN useradd -m -u 1000 $USER

RUN echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/nopasswd

USER $USER

# Install jhbuild
ENV CHECKOUT /home/$USER/jhbuild/checkout
RUN mkdir -p $CHECKOUT
WORKDIR $CHECKOUT
RUN git clone --depth=1 https://gitlab.gnome.org/GNOME/jhbuild.git
WORKDIR $CHECKOUT/jhbuild
RUN ./autogen.sh --simple-install
RUN make
RUN make install
WORKDIR /home/$USER

ENV PATH "/home/$USER/.local/bin:$PATH"

# Configure jhbuild
run mkdir -p /home/$USER/.config
RUN echo "modules = ['gtk+-3', 'gtksourceview-4', 'gobject-introspection']" >> /home/$USER/.config/jhbuildrc
RUN echo "module_mesonargs['gtksourceview-4'] = '-D vapi=false'" >> /home/$USER/.config/jhbuildrc

# Build GTK, GtkSourceView, and gobject-introspection
# RUN jhbuild build

