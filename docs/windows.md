# Gaphor on Windows

Gaphor can be installed as with our installer.
Check out the [Gaphor download page](https://gaphor.org/download#windows)
for details.

Older releases are available from [GitHub](https://github.com/gaphor/gaphor/releases).

[CI builds](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml) are also available.

## Development Environment

### WinGet

We recommend using [WinGet](https://learn.microsoft.com/en-us/windows/package-manager/winget) as a package manager in
Windows. It is available on Windows 11 and modern versions of Windows 10 as a part of the App Installer.

If you have a slightly older version of Windows, you can alternatively use [Chocolatey](https://chocolatey.org) as a
package manager. After it is installed, execute `choco install` instead of the `winget install` commands below.

### Git

To set up a development environment in Windows first install
[Git](https://gitforwindows.org) by executing as an administrator:

```PowerShell
winget install git.git
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
   py -3.13 --version
   ```

#### Install Graphviz

Graphviz is used by Gaphor for automatic diagram formatting.

1. Install from WinGet with administrator PowerShell:

```PowerShell
winget install graphviz
```

#### Install pipx

From the regular user PowerShell terminal execute:

```PowerShell
py -3.13 -m pip install --user pipx
py -3.13 -m pipx ensurepath
```

#### Download GTK

Download the latest release asset at [https://github.com/wingtk/gvsbuild/releases](https://github.com/wingtk/gvsbuild/releases). The file will be
called `GTK4_Gvsbuild_VERSION_x64.zip`, where `VERSION` is the latest released version.

Unzip the `GTK4_Gvsbuild_VERSION_x64.zip` file to `C:\gtk`. For example with 7Zip:

```PowerShell
7z x GTK4_Gvsbuild_*.zip  -oC:\gtk -y
```

The resulting directory structure should look like:

```
C:\gtk
├── bin
├── include
├── lib
├── python
├── share
└── wheels
```

### Setup Gaphor

In the same PowerShell terminal, clone the repository:

```PowerShell
cd (to the location you want to put Gaphor)
git clone https://github.com/gaphor/gaphor.git
cd gaphor
```

Install Poetry:

```PowerShell
pipx install poetry
```

Add GTK to your environmental variables:

```PowerShell
$env:Path = $env:Path + ";C:\gtk\bin;C:\Program Files\Graphviz\bin"
$env:LIB = "C:\gtk\lib"
$env:INCLUDE = "C:\gtk\include;C:\gtk\include\cairo;C:\gtk\include\glib-2.0;C:\gtk\include\gobject-introspection-1.0;C:\gtk\lib\glib-2.0\include;"
$env:GI_TYPELIB_PATH = "C:\gtk\lib\girepository-1.0"
$env:XDG_DATA_HOME = "$env:userprofile\.local\share"
```

You can also edit your account's Environmental Variables to persist across
PowerShell sessions.

Install Gaphor's dependencies:

```PowerShell
poetry install
```

Reinstall PyGObject and pycairo using gvsbuild wheels:

```PowerShell
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\PyGObject*.whl)
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\pycairo*.whl)
```

Launch Gaphor!

```PowerShell
poetry run gaphor
```

### Setting Up A Plugin Workspace for Gaphor

When setting up a plugin workspace you need to perform the following steps:

```
cd (your project's workspace)
```

If your project does not already have a pyproject.toml file, create one. For details see the [Poetry
documentation](https://python-poetry.org/docs/basic-usage/). If you already have a .toml file, make sure you have gaphor
as a development dependency. For details see the [Gaphor Hello World Plugin](https://github.com/gaphor/gaphor_plugin_helloworld).

```PowerShell
poetry init
```

Install your project's dependencies. If you have made your project dependent upon Gaphor, this will pull in Gaphor.

```PowerShell
poetry install
```

Reinstall PyGObject and pycairo using gvsbuild wheels:

```PowerShell
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\PyGObject*.whl)
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\pycairo*.whl)
```

Note that if you have forgotten to reinstall PyGObject and pycairo, the first time you add an element to a diagram that
has text, gaphor will crash!

Launch Gaphor!

```PowerShell
poetry run gaphor
```

### Debugging using Visual Studio Code

Start a new PowerShell terminal, and set current directory to the project folder:

```
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

### Debugging Your Plugin Using Visual Studio Code

```
cd (your project's workspace)
```

Start gaphor:
1. In the VSCode menu, select Run → Start debugging
2. Choose Select module from the list
3. Enter `gaphor` as module name

Your plugin should appear under the Tools menu.

## Packaging for Windows

In order to create an exe installation package for Windows, we utilize
[PyInstaller](https://pyinstaller.org) which analyzes Gaphor to find all the
dependencies and bundle them in to a single folder. We then use a custom bash
script that creates a Windows installer using
[NSIS](https://nsis.sourceforge.io/Main_Page) and a portable installer using
[7-Zip](https://www.7-zip.org). To install them, open PowerShell as an
administrator, then execute:

```PowerShell
winget install nsis 7zip
```

Then build your installer using:

```PowerShell
poetry install --only main,packaging,automation
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\PyGObject*.whl)
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\pycairo*.whl)
poetry build
poetry run poe package
poetry run poe win-installer
```

## Limited Anaconda Install

Sometimes, it may be helpful to call Gaphor functionality from a python console on computers without the ability for a full development install (e.g., without administrative privileges). Because not all necessary Gaphor build dependencies (specifically,  `gtksourceview5` and `libadwaita`) are not available as anaconda packages, you will not be able to build the program or instantiate/run application classes like `Application` and `Session`.

However, this setup can still be helpful if you want to use or call Gaphor as a library in the context of a larger project. In these cases, Gaphor can be installed as a package in an anaconda environment using the following process:


### Create new anaconda environment

If you use anaconda for other projects, it's a good idea to create a new environment for Gaphor, so that its dependencies don't end up conflicting with your pre-existing development environment. To do this, run the following command from anaconda prompt:

```
conda create -n "gaphor"
conda activate gaphor
```

where ``gaphor`` can be any name desired for the environment.

### Update packages in the new environment

Get the most recent packages using:

```
conda update --all
```

### Install dependencies

The following Gaphor dependencies are installable from anaconda:

```
conda install graphviz
conda install -c conda-forge gobject-introspection gtk4 pygobject pycairo hicolor-icon-theme adwaita-icon-theme
```

Unfortunately, the `gtksourceview5` and `libadwaita` dependencies are not available as anaconda packages. So you may not be able to fully build/run the program in this environment.

### Set up your development environment

Now, to develop with Gaphor, you will want to set it up with your development. If you want to work with `ipython`, install it below:

```
conda install ipython ipykernel
```

#### VSCode Tips
VSCode should work out-of-the box if it is already installed. Just set 'gaphor' as the kernel in your VSCode Profile or notebook.

#### Spyder Tips
You can install spyder in this environment using `conda install spyder`.

If this does not work, (i.e., if `conda install spyder` reveals conflicts), you can instead use the following workaround:

```
conda install spyder-kernels=2.4
```

Then, in spyder, set 'gaphor' as your python interpreter

### Install Gaphor

From a python console running within your new anaconda environment, you may then install Gaphor using pip:

```
pip install gaphor
```
