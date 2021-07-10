# Gaphor on Windows

## Development Environment

### Choco
We recommend using [Chocolately](https://chocolatey.org/) as a package manager
in Windows.

To install it, open PowerShell as an administrator, then execute:

```PowerShell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

To run local scripts in follow-on steps, also execute
`Set-ExecutionPolicy RemoteSigned`. This allows for local PowerShell scripts
to run without signing, but still requires signing for remote scripts.

### Git
To setup a development environment in Windows first install
[Git](https://gitforwindows.org) by executing as an adminstrator:

```PowerShell
choco install git
```

### MSYS2
Both of the development environments in the next steps need MSYS2 installed.

Install [MSYS2](http://www.msys2.org/):

Keep PowerShell open as administrator and execute:
```PowerShell
choco install msys2
```

### GTK and Python with gvsbuild (recommended)
gvsbuild provides a Python script helps you build the GTK library stack for
Windows using Visual Studio. By compiling GTK with Visual Studio, we can then
use a standard Python development environment in Windows.

Note: gvsbuild says it requires msys2, but does it for our needs?

First we will install the gvsbuild dependencies:
1. Visual C++ build tools workload for Visual Studio 2019 Build Tools
1. Python 3.6 (yes, this version is pretty old)

#### Install Visual Studio 2019
With your admin PowerShell terminal:

```PowerShell
choco install visualstudio2019-workload-vctools
```

#### Install Python 3.6

1. Download [Python 3.6.8](https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64-webinstall.exe)
1. Launch the installer by double clicking on it
1. On the first screen of the installation wizard, leave the default options and
select Customize installation
1. On the Optional Features screen, select Next to keep the defaults
1. On the Advanced Options screen, unselect the two selected options
1. In the Customize install location field enter `C:\Python36` and select Install
1. Allow the installation to finish

#### Install gvsbuild
We have forked gvsbuild for now because gaphor has slightly newer dependency
requirements than the upstream project. If we can get our changes upstream,
then we'll switch back to using that version directly.

Open a new regular user PowerShell terminal and execute:

```PowerShell
mkdir C:\gtk-build\github
cd C:\gtk-build\github
git clone https://github.com/gaphor/gvsbuild.git

```

#### Build GTK

In the same PowerShell terminal, execute:

```PowerShell
C:\Python36\python.exe .\build.py build -p=x64 --vs-ver=16 --msys-dir=C:\tools\msys64 --enable-gi --py-wheel --gtk3-ver=3.24 gobject-introspection gtk3 pycairo pygobject adwaita-icon-theme hicolor-icon-theme
```
Grab a coffee, the build will take a few minutes to complete.

Once it is complete, add GTK to your path:
```PowerShell
$env:Path = "C:\gtk-build\gtk\x64\release\bin;" + $env:Path
```

#### Install the Latest Python for Gaphor

Download and install the latest version of Python. For this you have a few options:

1. Install from Chocolately with `choco install python` as an admin 
1. Install from the Windows Store
1. If you need to test with multiple versions of Python, install
[pyenv-win](https://github.com/pyenv-win/pyenv-win)

Restart your PowerShell terminal as a normal user and check that `python --version` is correct.

#### Setup Gaphor

In the same PowerShell terminal, clone the repository:
```PowerShell
cd (to the location you want to put Gaphor)
git clone https://github.com/gaphor/gaphor.git
```

Create and activate a virtual environment in which Gaphor can be installed.
```PowerShell
PS > cd gaphor
PS > python -m venv .venv
PS > .\.venv\Scripts\activate.ps1
```

Install and configure Poetry
```PowerShell
(.venv) PS > pip install poetry
(.venv) PS > poetry config virtualenvs.create false
```

Install PyGObject and pycairo from gvsbuild
```PowerShell
(.venv) PS > Get-ChildItem C:\gtk-build\build\x64\release\*\dist\*.whl | ForEach-Object -process { pip install $_ }
```

Install Gaphor's other dependencies and give it a try
```PowerShell
(.venv) PS > poetry install
(.venv) PS > gaphor
```

### GTK and Python with MSYS2 (alternative method)
MSYS2 provides a bash terminal, with Python and GTK compiled against GCC. This
is an alternative method to using gvsbuild above. The advantage is that you get
a full bash environment in Windows, the disadvantage is that Python is very
heavily patched to be built this way and often breaks.

1) Run `C:\tools\msys64\mingw64.exe` - the MINGW64 terminal window should pop up

```bash
$ pacman -Suy
$ pacman -S mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-gtk3 \
    mingw-w64-x86_64-pkgconf \
    mingw-w64-x86_64-cairo \
    mingw-w64-x86_64-gobject-introspection \
    mingw-w64-x86_64-python \
    mingw-w64-x86_64-python-pip \
    mingw-w64-x86_64-python-setuptools \
    mingw-w64-x86_64-python3.9
$ echo 'export PATH="/c/Program Files/Git/bin:$PATH"' >> ~/.bash_profile
```

Restart the MINGW64 terminal.

[Clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).

Create and activate a virtual environment in which Gaphor can be installed:
```bash
$ cd gaphor
$ python3.9 -m venv .venv
$ source .venv/bin/activate
```

Install and configure Poetry:
```bash
$ pip install poetry wheel
$ poetry config virtualenvs.create false
```

Install Gaphor and give it a try:
```bash
$ poetry install
$ poetry run gaphor
```

## Packaging for Windows

In order to create an exe installation package for Windows, we utilize
[PyInstaller](https://pyinstaller.org) which analyzes Gaphor to find all the
dependencies and bundle them in to a single folder. We then use a custom bash
script that creates a Windows installer using
[NSIS](https://nsis.sourceforge.io/Main_Page) and a portable installer using
[7-Zip](https://www.7-zip.org).

1. Follow the instructions for settings up a development environment above
1. Run ``C:\tools\msys64\mingw64.exe`` - a terminal window should pop up
```bash
$ source .venv/bin/activate
$ mingw32-make dist
$ cd packaging
$ mingw32-make all
$ cd windows
$ mingw32-make all
```
