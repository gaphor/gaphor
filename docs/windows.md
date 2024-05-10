# Gaphor on Windows

Gaphor can be installed as with our installer.
Check out the [Gaphor download page](https://gaphor.org/download#windows)
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

To set up a development environment in Windows first install
[Git](https://gitforwindows.org) by executing as an administrator:

```PowerShell
choco install git
```

### GTK and Python with Gvsbuild

Gvsbuild provides pre-built GTK libraries for Windows. We will install
these libraries and Python.

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
   py -3.12 --version
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
py -3.12 -m pip install --user pipx
py -3.12 -m pipx ensurepath
```

#### Download GTK

Download the latest release asset at https://github.com/wingtk/gvsbuild/releases. The file will be
called GTK4_Gvsbuild_VERSION_x64.zip, where VERSION is the latest released version.

Unzip the GTK4_Gvsbuild_VERSION_x64.zip file to C:\gtk. For example with 7Zip:

```PowerShell
7z x GTK4_Gvsbuild_*.zip  -oC:\gtk -y
```

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
```

Add GTK to your environmental variables:
```PowerShell
$env:Path = $env:Path + ";C:\gtk\bin"
$env:LIB = "C:\gtk\lib"
$env:INCLUDE = "C:\gtk\include;C:\gtk\include\cairo;C:\gtk\include\glib-2.0;C:\gtk\include\gobject-introspection-1.0;C:\gtk\lib\glib-2.0\include;"
$env:XDG_DATA_HOME = "$HOME\.local\share"
```

You can also edit your account's Environmental Variables to persist across
PowerShell sessions.

Install Gaphor's dependencies
```PowerShell
poetry install
```

Install the git hook scripts
```Powershell
poetry run pre-commit install
```

Reinstall PyGObject and pycairo using gvsbuild wheels
```PowerShell
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\PyGObject*.whl)
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\pycairo*.whl)
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
$env:Path = "C:\gtk\bin;" + $env:Path
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
