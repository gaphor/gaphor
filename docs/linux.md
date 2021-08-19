# Gaphor on Linux

## Development Environment

To set up a development environment with Linux, you first need a fairly new
Linux distribution version. For example, the latest Ubuntu LTS or newer, Arch,
Debian Testing, SUSE Tumbleweed, or similar. Gaphor depends on newer versions of
GTK, and we don't test for backwards compatibility. You will also need the
latest stable version of Python. In order to get the latest stable version without
interfering with your system-wide Python version, we recommend that you install
[pyenv](https://github.com/pyenv/pyenv).

Install the pyenv [prerequisites](https://github.com/pyenv/pyenv/wiki/Common-build-problems)
first, and then install pyenv:

    $ curl https://pyenv.run | bash

Make sure you follow the instruction at the end of the installation
script to install the commands in your shell's rc file. Next install
the latest version of Python by executing:

    $ pyenv install 3.x.x

Where 3.x.x is replaced by the latest stable version of Python (pyenv should let you tab-complete available versions).

Next install the Gaphor prerequisites by installing the gobject
introspection and cairo build dependencies, for example, in Ubuntu
execute:

```bash
$ sudo apt-get install -y python3-dev python3-gi python3-gi-cairo
gir1.2-gtk-3.0 libgirepository1.0-dev libcairo2-dev libgtksourceview-4-dev
```

Install Poetry (you may want to consider [alternative methods](https://python-poetry.org/docs/#alternative-installation-methods-not-recommended)):
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
```

[Clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).

```bash
$ cd gaphor
# activate latest python for this project
$ pyenv local 3.x.x # 3.x.x is the version you installed earlier
$ poetry env use 3.x # ensures poetry /consistently/ uses latest major release
$ poetry config virtualenvs.in-project true
$ poetry install
$ poetry run gaphor
```

## Create a Flatpak Package

The main method that Gaphor is packaged for Linux is with a Flatpak package.
[Flatpak](https://flatpak.org) is a software utility for software deployment
and package management for Linux. It offer a sandbox environment in which
users can run application software in isolation from the rest of the system.

We distribute the official Flatpak using [Flathub](https://flathub.org), and
building of the image is done at the [Gaphor Flathub
repository](https://github.com/flathub/org.gaphor.Gaphor).

1. [Install Flatpak](https://flatpak.org/setup)

1. Install flatpak-builder

       $ sudo apt-get install flatpak-builder

1. Install the GNOME SDK

       $ flatpak install flathub org.gnome.Sdk 3.38

1. Clone the Flathub repository and install the necessary SDK:

       git clone https://github.com/flathub/org.gaphor.Gaphor.git
       $ cd org.gaphor.Gaphor
       $ make setup

1. Build Gaphor Flatpak

       $ make

1. Install the Flatpak

       $ make install

## Create an AppImage Package

[AppImage](https://appimage.org/) is a format for distributing portable software
on Linux without needing superuser permissions to install the application. The
AppImage file is one executable which contains both Gaphor and Python. It allows
Gaphor to be run on any AppImage supported Linux distribution without
installation or root access.

We build our AppImage by first bundling Gaphor with PyInstaller and then
converting it in to an AppImage.

1. Activate your virtualenv, `poetry shell`

1. `cd appimage`

1. `make update VERSION=x.x.x`

1. Build the AppImage by running `make all`

1. Test that Gaphor-x86_64.AppImage works by running `make run`

## Linux Distribution Packages

Examples of Gaphor and Gaphas RPM spec files can be found in [PLD
Linux](https://www.pld-linux.org/)
[repository](https://github.com/pld-linux/):

- https://github.com/pld-linux/python-gaphas
- https://github.com/pld-linux/gaphor

Please, do not hesitate to contact us if you need help to create a Linux
package for Gaphor or Gaphas.
