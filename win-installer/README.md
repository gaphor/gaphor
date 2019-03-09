# Windows Installer Build Scripts
We use msys2 for creating the Windows installer and development on Windows
because that is what PyGObject currently supports.

## Development
For developing on Windows you have two choices.

#### 1. Use an Existing Gaphor Installation Plus a Git Checkout:
- Clone the git repo with some git client
- Download and install the latest [installer
build](https://github.com/gaphor/gaphor/releases/download/latest/gaphor-latest-installer.exe)
- Go to setup.py in the git checkout and run C:\Program
Files\Gaphor\bin\python.exe setup.py run.

#### 2. Use a Full MSYS2 Environment
- Download msys2 64-bit from https://msys2.org
- Follow instructions on https://msys2.org
- Execute C:\msys64\mingw64.exe
- Run `pacman -Syu` to update packages
- Run `pacman -S git` to install git
- Run git clone https://github.com/gaphor/gaphor.git
- Run cd gaphor/win_installer to end up where this README exists.
- Execute `./bootstrap.sh` to install all the needed dependencies.
- Now go to the source code `cd ../`
- To run Gaphor execute `python3 setup.py run`

## Creating an Installer
Simply run `./build.sh [git-tag]` and both the installer and the portable
installer should appear in this directory.

You can pass a git tag ./build.sh release-1.0.0 to build a specific tag or pass
nothing to build master. Note that it will clone from this repository and not
from github so any commits present locally will be cloned as well.

## Updating an Existing Installer
We directly follow msys2 upstream so building the installer two weeks later
might result in newer versions of dependencies being used. To reduce the risk of
stable release breakage you can use an existing installer and just install a
newer Gaphor version into it and then repack it:

`./rebuild.sh gaphor-1.0.0-installer.exe [git-tag]`