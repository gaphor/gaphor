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
[Git](https://gitforwindows.org) by executing as an adminstrator:

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

Download and install the latest version of Python:

1. Install from Chocolately with administrator PowerShell:

   ```PowerShell
   choco install python
   ```

2. Restart your PowerShell terminal as a normal user and check  the python version:

   ```PowerShell
   python --version
   ```

#### Install pipx

From the regular user PowerShell terminal execute:
```PowerShell
python -m pip install --user pipx
python -m pipx ensurepath
```

#### Install gvsbuild

From the regular user PowerShell terminal execute:

```PowerShell
pipx install gvsbuild
```

#### Build GTK

In the same PowerShell terminal, execute:

```PowerShell
gvsbuild build --enable-gi gobject-introspection gtk3 pycairo pygobject gtksourceview4 adwaita-icon-theme hicolor-icon-theme
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
```bash
pipx install poetry
poetry config virtualenvs.in-project true
```

Install Gaphor's other dependencies
```PowerShell
poetry install
```

Add GTK to your environmental variables:
```PowerShell
$gtk_path = "C:\gtk-build\gtk\x64\release"
$env:Path = $gtk_path + "\bin;" + $env:Path
$env:LIB = $gtk_path + "\lib"
$gtk_include = $gtk_path + "\include"
$env:INCLUDE = $gtk_include + "\cairo;" + $gtk_include + "\glib-2.0;"
$env:INCLUDE = $gtk_include + "\gobject-introspection-1.0;" + $env:INCLUDE
$env:INCLUDE = $gtk_path + "\lib\glib-2.0\include;" + $gtk_include + ";" + $env:INCLUDE
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
