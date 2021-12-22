FROM ubuntu:18.04
LABEL maintainer="dan@yeaw.me"

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

ENV PYTHON_VERSION "3.10.1"
ENV PYTHON_VERSION_SHORT "3.10"

RUN sed -i -- 's/#deb-src/deb-src/g' /etc/apt/sources.list && \
    sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get build-dep -y \
    fontconfig \
  && apt install -y \
    apt-file \
    autoconf \
    automake \
    autopoint \
    bison \
    build-essential \
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
    libxrandr-dev \
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
    sudo \
    trang \
    uuid-dev \
    vim \
    wget \
    xmlto \
    yelp-tools \
  && rm -rf /var/lib/apt/lists/*
RUN apt-file update

RUN mkdir -p /opt

# Install Python
# WORKDIR /opt
# RUN wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
# RUN tar xvf Python-$PYTHON_VERSION.tgz
# WORKDIR /opt/Python-$PYTHON_VERSION
# RUN ./configure --enable-optimizations
# RUN make
# RUN make altinstall
# RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python$PYTHON_VERSION_SHORT 1
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python$PYTHON_VERSION_SHORT 1

# Build Fontconfig
WORKDIR /opt
ENV FONTCONFIG_VERSION 2.13.1
RUN wget https://www.freedesktop.org/software/fontconfig/release/fontconfig-$FONTCONFIG_VERSION.tar.gz
RUN tar xzvf fontconfig-$FONTCONFIG_VERSION.tar.gz
WORKDIR fontconfig-$FONTCONFIG_VERSION
RUN ./configure
RUN make
RUN make install
ENV PKG_CONFIG_PATH=/usr/local/lib:$PKG_CONFIG_PATH

ENV USER gnome
RUN useradd -m -u 1000 $USER

RUN echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/nopasswd

USER $USER

run mkdir -p /home/$USER/.config
RUN echo "modules = ['gtk+-3', 'gtksourceview-4', 'gobject-introspection']\n" > /home/$USER/.config/jhbuildrc

ENV PATH "/home/$USER/.local/bin:$PATH"

WORKDIR /home/$USER
RUN git clone --depth=1 https://gitlab.gnome.org/GNOME/jhbuild.git
WORKDIR /home/$USER/jhbuild
RUN ./autogen.sh --simple-install
RUN make
RUN make install

