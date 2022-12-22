# Gaphor on Windows

Gaphor can be installed as with our our installer.
Check out the [Gaphor download page](https://gaphor.org/download.html#windows)
for details.

Older releases are available from [GitHub](https://github.com/gaphor/gaphor/releases).

[CI builds](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml) are also available.

## Development Environment

### Choco

We recommend using [Chocolately](https://chocolatey.org/) as a package manager
in Windows.

To install it, open PowerShell as an administrator, then execute:

```PowerShell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

To run local scripts in follow-on steps, also execute

```PowerShell
Set-ExecutionPolicy RemoteSigned
```

This allows for local PowerShell scripts
to run without signing, but still requires signing for remote scripts.

### Git

To setup a development environment in Windows first install
[Git](https://gitforwindows.org) by executing as an administrator:

```PowerShell
choco install git
```

### MSYS2

The development environment in the next step needs MSYS2 installed to provide
some Linux command line tools in Windows.

Keep PowerShell open as administrator and install [MSYS2](http://www.msys2.org/):

```PowerShell
choco install msys2
```

### GTK and Python with gvsbuild

gvsbuild provides a Python script helps you build the GTK library stack for
Windows using Visual Studio. By compiling GTK with Visual Studio, we can then
use a standard Python development environment in Windows.

First we will install the gvsbuild dependencies:
1. Visual C++ build tools workload for Visual Studio 2022 Build Tools
1. Python

#### Install Visual Studio 2022

With your admin PowerShell terminal:

```PowerShell
choco install visualstudio2022-workload-vctools
```

#### Install the Latest Python

In Windows, The full installer contains all the Python components and is the
best option for developers using Python for any kind of project.

For more information on how to use the official installer, please see the
[full installer instructions](https://docs.python.org/3/using/windows.html#windows-full).
The default installation options should be fine for use with Gaphor.

1. Install the latest Python version using the
[official installer](https://www.python.org/downloads/windows/).

2. Open a PowerShell terminal as a normal user and check the python version:

   ```PowerShell
   py -3.11 --version
   ```

#### Install Graphviz

Graphviz is used by Gaphor for automatic diagram formatting.

1. Install from Chocolately with administrator PowerShell:

   ```PowerShell
   choco install graphviz
   ```

2. Restart your PowerShell terminal as a normal user and check that the dot
   command is available:

   ```PowerShell
   dot -?
   ```

#### Install pipx

From the regular user PowerShell terminal execute:
```PowerShell
py -3.11 -m pip install --user pipx
py -3.11 -m pipx ensurepath
```

#### Install gvsbuild

From the regular user PowerShell terminal execute:

```PowerShell
pipx install gvsbuild
```

#### Build GTK

In the same PowerShell terminal, execute:

```PowerShell
gvsbuild build --enable-gi --py-wheel gobject-introspection gtk4 libadwaita gtksourceview5 pygobject pycairo adwaita-icon-theme hicolor-icon-theme
```
Grab a coffee, the build will take a few minutes to complete.

### Setup Gaphor

In the same PowerShell terminal, clone the repository:
```PowerShell
cd (to the location you want to put Gaphor)
git clone https://github.com/gaphor/gaphor.git
cd gaphor
```

Install Poetry
```PowerShell
pipx install poetry
poetry config virtualenvs.in-project true
```

Add GTK to your environmental variables:
```PowerShell
$env:Path = $env:Path + ";C:\gtk-build\gtk\x64\release\bin"
$env:LIB = "C:\gtk-build\gtk\x64\release\lib"
$env:INCLUDE = "C:\gtk-build\gtk\x64\release\include;C:\gtk-build\gtk\x64\release\include\cairo;C:\gtk-build\gtk\x64\release\include\glib-2.0;C:\gtk-build\gtk\x64\release\include\gobject-introspection-1.0;C:\gtk-build\gtk\x64\release\lib\glib-2.0\include;"
```

You can also edit your account's Environmental Variables to persist across
PowerShell sessions.

Install Gaphor's dependencies
```PowerShell
poetry install
```

Reinstall PyGObject and pycairo using gvsbuild wheels
```PowerShell
poetry run pip install --force-reinstall (Resolve-Path C:\gtk-build\build\x64\release\pygobject\dist\PyGObject*.whl)
poetry run pip install --force-reinstall (Resolve-Path C:\gtk-build\build\x64\release\pycairo\dist\pycairo*.whl)
```

Launch Gaphor!
```PowerShell
poetry run gaphor
```

### Debugging using Visual Studio Code

Start a new PowerShell terminal, and set current directory to the project folder:
```PowerShell
cd (to the location you put gaphor)
```

Ensure that path environment variable is set:
```PowerShell
$env:Path = "C:\gtk-build\gtk\x64\release\bin;" + $env:Path
```

Start Visual Studio Code:
```PowerShell
code .
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
[7-Zip](https://www.7-zip.org). To install them, open PowerShell as an
administrator, then execute:

```PowerShell
choco install nsis 7zip
```

Then build your installer using:

```PowerShell
poetry install --only main,packaging,automation
poetry build
poetry run poe package
poetry run poe win-installer
```
