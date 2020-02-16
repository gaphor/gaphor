# Windows Installer Build Scripts
We use msys2 for creating the Windows installer and development on Windows
because that is what PyGObject currently supports.

##  Use a Full MSYS2 Environment
- Download msys2 64-bit from https://msys2.org
- Follow instructions on https://msys2.org
- Execute `C:\msys64\mingw64.exe`
- Run `pacman -Syu` to update packages
- Run `pacman -S git` to install git
- Run `git clone https://github.com/gaphor/gaphor.git`
- Execute `win-installer/msys2-install.sh` to install all the needed dependencies.
- Run gaphor by typing `gaphor`

## Creating an Installer
Simply run `win-installer/build-installer.sh` and both the installer and the portable
installer should appear in this directory.

