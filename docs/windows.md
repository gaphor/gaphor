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
1. Python

#### Install Visual Studio 2019
With your admin PowerShell terminal:

```PowerShell
choco install visualstudio2019-workload-vctools
```

#### Install the Latest Python

Download and install the latest version of Python:

1. Install from Chocolately with `choco install python` with admin PowerShell
1. Restart your PowerShell terminal as a normal user and check that `python --version` is correct.

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
cd C:\gtk-build\github\gvsbuild
python .\build.py build -p=x64 --vs-ver=16 --msys-dir=C:\tools\msys64 --enable-gi --py-wheel --gtk3-ver=3.24 gobject-introspection gtk3 pycairo pygobject gtksourceview adwaita-icon-theme hicolor-icon-theme
```
Grab a coffee, the build will take a few minutes to complete.

#### Setup Gaphor

In the same PowerShell terminal, clone the repository:
```PowerShell
cd (to the location you want to put Gaphor)
git clone https://github.com/gaphor/gaphor.git
```

Install Poetry (you may want to consider installing poetry via [pipx](https://pypi.org/project/pipx/), instead of pip):
```bash
PS > pip install --user poetry
PS > poetry config virtualenvs.in-project true
```

Install PyGObject and pycairo from gvsbuild
```PowerShell
PS > Get-ChildItem C:\gtk-build\build\x64\release\*\dist\*.whl | ForEach-Object -process { poetry run pip install $_ }
```

Install Gaphor's other dependencies
```PowerShell
PS > poetry install
```

Add GTK to your path:
```PowerShell
$env:Path = "C:\gtk-build\gtk\x64\release\bin;" + $env:Path
```

Launch Gaphor!
```PowerShell
PS > poetry run gaphor
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
    mingw-w64-x86_64-gtksourceview4 \
    mingw-w64-x86_64-pkgconf \
    mingw-w64-x86_64-cairo \
    mingw-w64-x86_64-gobject-introspection \
    mingw-w64-x86_64-python \
    mingw-w64-x86_64-python-pip \
    mingw-w64-x86_64-python-setuptools
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

### Debugging using Visual Studio Code

Start a new PowerShell terminal, and set current directory to the project folder:
```PowerShell
PS > cd (to the location you put gaphor)
```

Ensure that path environment variable is set:
```PowerShell
PS > $env:Path = "C:\gtk-build\gtk\x64\release\bin;" + $env:Path
```

Start Visual Studio Code:
```PowerShell
PS > code .
```

To start the debugger, execute the following steps:
1. Open `__main__.py` file from `gaphor` folder
2. Add a breakpoint on line `main(sys.argv)`
3. In the menu, select Run → Start debugging
4. Choose Select module from the list
5. Enter `gaphor` as module name

Visual Studio Code will start the application in debug mode, and will stop at main.

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
$ cd _packaging
$ mingw32-make all
$ cd windows
$ mingw32-make all
```
