# Windows Installer Build Scripts
We use msys2 for creating the Windows installer and development on Windows
because that is what PyGObject currently supports.

###  Use a Full MSYS2 Environment
- Download msys2 64-bit from https://msys2.org
- Follow instructions on https://msys2.org
- Execute C:\msys64\mingw64.exe
- Run `pacman -Syu` to update packages
- Run `pacman -S git` to install git
- Run git clone https://github.com/gaphor/gaphor.git
- Run cd gaphor/win_installer to end up where this README exists.
- Execute `./bootstrap.sh` to install all the needed dependencies.
- Now go to the source code `cd ../`
- Execute `python -m venv .venv` to create a virtualenv
- Activate the virtualenv with `source .venv/bin/activate`
- Install poetry with `pip install poetry`
- Install the dependencies with `poetry install` 
- Run gaphor by typing `gaphor

## Creating an Installer
Simply run `./build-installer.sh` and both the installer and the portable
installer should appear in this directory.

