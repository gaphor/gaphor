# Gaphor on Linux

Gaphor can be installed as Flatpak on Linux, some distributions provide
packages. Check out the [Gaphor download page](https://gaphor.org/download/#linux)
for details.

Older releases are available from [GitHub](https://github.com/gaphor/gaphor/releases).

[CI builds](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml) are also available.

## Development Environment

There are two ways to set up a development environment:

1. [GNOME Builder](#gnome-builder), ideal for “drive by” contributions.
2. [A local environment](#a-local-environment).

### GNOME Builder

Open [GNOME Builder](https://flathub.org/apps/details/org.gnome.Builder) 43 or newer, [clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).
Check if the _Build Profile_ is set to `org.gaphor.Gaphor.json`. If so, hit the _Run_ button to start the application.


### A Local Environment

To set up a development environment with Linux, you first need a fairly new
Linux distribution version. For example, the latest Ubuntu LTS or newer, Arch,
Debian Testing, SUSE Tumbleweed, or similar. Gaphor depends on newer versions of
GTK, and we don't test for backwards compatibility. You will also need the
latest stable version of Python. In order to get the latest stable version without
interfering with your system-wide Python version, we recommend that you install
[pyenv](https://github.com/pyenv/pyenv).

Install the pyenv [prerequisites](https://github.com/pyenv/pyenv/wiki/Common-build-problems)
first, and then install pyenv:

```bash
curl https://pyenv.run | bash
```

Make sure you follow the instruction at the end of the installation
script to install the commands in your shell's rc file. Next install
the latest version of Python by executing:

```bash
pyenv install 3.x.x
```

Where 3.x.x is replaced by the latest stable version of Python (pyenv should let you tab-complete available versions).

Next install the Gaphor prerequisites by installing the gobject
introspection and cairo build dependencies, for example, in Ubuntu
execute:

```bash
sudo apt-get install -y python3-dev python3-gi python3-gi-cairo \
gir1.2-gtk-4.0 libgirepository-2.0-dev libcairo2-dev libgtksourceview-5-dev \
graphviz
```

For Redhat/RPM/Fedora based systems:

```bash
sudo dnf install python3-devel cairo-gobject-devel gobject-introspection-devel graphviz
```

Install [Poetry](https://python-poetry.org) using [pipx](https://pypa.github.io/pipx/):
```bash
pipx install poetry
```

Next, [clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository), after which you need to execute the following consecutive commands:

```bash
cd gaphor
# activate latest python for this project
pyenv local 3.x.x # 3.x.x is the version you installed earlier
poetry env use 3.x # ensures poetry /consistently/ uses latest major release
poetry install
poetry run pre-commit install
```
Now, you can run gaphor as
```bash
poetry run gaphor
```

NOTE: Gaphor requires GTK 4. It works best with GTK >=4.8 and libadwaita >=1.2.

### Debugging using Visual Studio Code

Before you start debugging you'll need to open Gaphor in vscode (the folder
containing `pyproject.toml`). You'll need to have the Python extension installed.

Create a file `.vscode/launch.json` with the following content:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Gaphor UI",
            "type": "python",
            "request": "launch",
            "module": "gaphor",
            "justMyCode": false,
            "env": {
                "GDK_BACKEND": "wayland"
            }
        }
    ]
}
```

`GDK_BACKEND` is added since VSCode by default uses XWayland (the X11 emulator).

## Create a Flatpak Package

The main method that Gaphor is packaged for Linux is with a Flatpak package.
[Flatpak](https://flatpak.org) is a software utility for software deployment
and package management for Linux. It offers a sandbox environment in which
users can run application software in isolation from the rest of the system.

We distribute the official Flatpak using [Flathub](https://flathub.org), and
building of the image is done at the [Gaphor Flathub
repository](https://github.com/flathub/org.gaphor.Gaphor).

1. [Install Flatpak](https://flatpak.org/setup)

2. Install flatpak-builder

       sudo apt-get install flatpak-builder

3. Install the GNOME SDK

       flatpak install flathub org.gnome.Sdk 43

4. Clone the Flathub repository and install the necessary SDK:

       git clone https://github.com/flathub/org.gaphor.Gaphor.git
       cd org.gaphor.Gaphor
       make setup

5. Build Gaphor Flatpak

       make

6. Install the Flatpak

       make install

## Linux Distribution Packages

Examples of Gaphor and Gaphas RPM spec files can be found in [PLD
Linux](https://www.pld-linux.org/)
[repository](https://github.com/pld-linux/):

- https://github.com/pld-linux/python-gaphas
- https://github.com/pld-linux/gaphor

There is also an [Arch User Repository (AUR) for
Gaphor](https://aur.archlinux.org/packages/python-gaphor) available for Arch
users.

Please, do not hesitate to contact us if you need help to create a Linux
package for Gaphor or Gaphas.
