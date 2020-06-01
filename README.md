# Gaphor <img src="logos/gaphor.svg" width="48">

[![Build state](https://github.com/gaphor/gaphor/workflows/Build/badge.svg)](https://github.com/gaphor/gaphor/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/f00974f5d7fe69fe4ecd/maintainability)](https://codeclimate.com/github/gaphor/gaphor/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f00974f5d7fe69fe4ecd/test_coverage)](https://codeclimate.com/github/gaphor/gaphor/test_coverage)
[![Docs build state](https://readthedocs.org/projects/gaphor/badge/?version=latest)](https://gaphor.readthedocs.io)
[![PyPI](https://img.shields.io/pypi/v/gaphor.svg)](https://pypi.org/project/gaphor)
[![Downloads](https://pepy.tech/badge/gaphor)](https://pepy.tech/project/gaphor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat)](https://github.com/RichardLitt/standard-readme)
[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/Gaphor/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![All Contributors](https://img.shields.io/badge/all_contributors-24-orange.svg?style=flat-square)](#contributors)


> Gaphor is the simple modeling tool for UML.

![Gaphor Demo](docs/images/gaphor-demo.gif)

Gaphor is a simple and easy to use modeling tool for UML. It is aimed at
beginning modelers who want a simple and fast tool so that they can focus on
learning modeling of software and systems. It is not a full featured enterprise
tool.

## :bookmark_tabs: Table of Contents

- [Background](#background)
- [Install](#floppy_disk-install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## :scroll: Background

Gaphor is a UML modeling application written in Python. It is designed to be
easy to use, while still being powerful. Gaphor implements a fully-compliant UML
2 data model, so it is much more than a picture drawing tool. You can use Gaphor
to quickly visualize different aspects of a system as well as create complete,
highly complex models.

Gaphor is designed around the following principles:

- Simplicity: The application should be easy to use. Only some basic knowledge of UML is required.
- Consistency: UML is a graphical modeling language, so all modeling is done in a diagram.
- Workability: The application should not bother the user every time they do something non-UML-ish.

Gaphor is built on [Gaphas](https://github.com/gaphor/gaphas), which provides
the foundational diagramming library. It is a GUI application that is built on
GTK and cairo, [PyGObject](https://pygobject.readthedocs.io/) provides access
to the GUI toolkit, and [PyCairo](https://pycairo.readthedocs.io/) to the 2D
graphics library.

## :floppy_disk: Install

### Windows
To install Gaphor on Windows you an use the [latest Gaphor.exe installer](https://github.com/gaphor/gaphor/releases).
There are two versions:
1. Full Windows installation
2. Portable installation

### Linux
To install Gaphor in Linux use Flatpak:
1. [Install Flatpak](https://flatpak.org/setup)
1. `flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo`
1. `flatpak install --user flathub org.gaphor.Gaphor`

#### Arch Linux

Can be installed from [AUR package](https://aur.archlinux.org/packages/python-gaphor/).

### macOS
We are still working on packaging GTK with Gaphor and it is currently an
installation pre-requisite.
1. Install [homebrew](https://brew.sh)
1. Open a terminal and execute:
```bash
$ brew install gobject-introspection gtk+3
```

Then install Gaphor on macOS using the [latest gaphor-macOS.dmg
installer](https://github.com/gaphor/gaphor/releases).


Note: Sometimes launching the app the first time after installation fails due
to macOS security settings, please attempt to launch it a 2nd time if this
happens.

### PyPI
If you have the latest stable version of Python installed and the Gaphor
dependencies installed, you can also install Gaphor using a wheel from PyPI.

If you don't have the latest stable version of Python and the Gaphor dependencies
installed, follow the development environment setup instructions in the next
section and instead of cloning the repository, create a
[virtual environment](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments),
and then execute the following:

```bash
$ pip install gaphor
$ gaphor
```

### Development

#### Windows

To setup a development environment in Windows:
1) Go to http://www.msys2.org/ and download the x86_64 installer
1) Follow the instructions on the page for setting up the basic environment
1) Run ``C:\msys64\mingw64.exe`` - a terminal window should pop up
```bash
$ pacman -Suy
$ pacman -S git mingw-w64-x86_64-gcc mingw-w64-x86_64-gtk3 \
mingw-w64-x86_64-pkg-config mingw-w64-x86_64-cairo \
mingw-w64-x86_64-gobject-introspection mingw-w64-x86_64-python \
mingw-w64-x86_64-python-gobject mingw-w64-x86_64-python-cairo \
mingw-w64-x86_64-python-pip
```

Ensure `/mingw64/bin` is added to your `PATH`:
```bash
$ export PATH=/mingw64/bin:$PATH
```

[Clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).

```bash
$ cd gaphor
$ source ./venv -S
$ poetry run gaphor
```

#### Linux
To setup a development environment with Linux, you first need the latest
stable version of Python. In order to get the latest stable version, we
recommend that you install [pyenv](https://github.com/pyenv/pyenv).
Install the pyenv
[prerequisites](https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites)
first, and then install pyenv:

```bash
$ curl https://pyenv.run | bash
```

Make sure you follow the instruction at the end of the installation script
to install the commands in your shell's rc file. Finally install the latest
version of Python by executing:

```bash
$ pyenv install 3.x.x
```
Where 3.x.x is replaced by the latest stable version of Python.

Next install the Gaphor prerequisites by installing the gobject introspection
and cairo build dependencies, for example, in Ubuntu execute:

```bash
$ sudo apt-get install -y python3-dev python3-gi python3-gi-cairo
    gir1.2-gtk-3.0 libgirepository1.0-dev libcairo2-dev
```
[Clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).

```
$ cd gaphor
$ source ./venv
$ poetry run gaphor
```

#### macOS
To setup a development environment with macOS:
1. Install [homebrew](https://brew.sh)
1. Open a terminal and execute:
```bash
$ brew install python3 gobject-introspection gtk+3
```
[Clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).
```
$ cd gaphor
$ source ./venv
$ poetry run gaphor
```

## :flashlight: Usage
### Creating models

Once Gaphor is started a new empty model is automatically created. The main
diagram is already open in the Diagram section.

Select an element you want to place, for example a Class, by clicking on the icon in
the Toolbox and click on the diagram. This will place a new
Class item instance on the diagram and add a new Class to the model (it shows
up in the Navigation). The selected tool will reset itself to
the Pointer tool if the option ''Diagram -> Reset tool'' is selected.

Some elements are not directly visible. The section in the toolbox is collapsed
and needs to be clicked first to reveal its contents.

Gaphor only has one diagram type, and it does not enforce which elements should
be placed on a diagram.

### Create a New Diagram

1. Use the Navigation to select an element that can contain a diagram (a
Package or Profile)
1. Select Diagram, and New diagram. A new diagram is created.

### Copy and Paste

Items in a diagram can be copied and pasted in the same diagram or other
diagrams. Pasting places an existing item in the diagram, but the item itself
is not duplicated. In other words, if you paste a Class object in a diagram,
the Class will be added to the diagram, but there will be no new Class in the
Navigation.

### Drag and Drop

Adding an existing element to a diagram is done by dragging the element from
the Navigation section onto a diagram. Diagrams and attribute/operations of a
Class show up in the Navigation but can not be added to a diagram.

Elements can also be dragged within the Navigation in order to rearrange them
in to different packages.


## :heart: Contributing

Thanks goes to these wonderful people ([emoji key](https://github.com/kentcdodds/all-contributors#emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/amolenaar"><img src="https://avatars0.githubusercontent.com/u/96249?v=4" width="100px;" alt=""/><br /><sub><b>Arjan Molenaar</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=amolenaar" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aamolenaar" title="Bug reports">🐛</a> <a href="https://github.com/gaphor/gaphor/commits?author=amolenaar" title="Documentation">📖</a> <a href="https://github.com/gaphor/gaphor/pulls?q=is%3Apr+reviewed-by%3Aamolenaar" title="Reviewed Pull Requests">👀</a> <a href="#question-amolenaar" title="Answering Questions">💬</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aamolenaar" title="Bug reports">🐛</a> <a href="#plugin-amolenaar" title="Plugin/utility libraries">🔌</a> <a href="https://github.com/gaphor/gaphor/commits?author=amolenaar" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/wrobell"><img src="https://avatars2.githubusercontent.com/u/105664?v=4" width="100px;" alt=""/><br /><sub><b>wrobell</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=wrobell" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=wrobell" title="Tests">⚠️</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Awrobell" title="Bug reports">🐛</a> <a href="#design-wrobell" title="Design">🎨</a></td>
    <td align="center"><a href="https://ghuser.io/danyeaw"><img src="https://avatars1.githubusercontent.com/u/10014976?v=4" width="100px;" alt=""/><br /><sub><b>Dan Yeaw</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=danyeaw" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=danyeaw" title="Tests">⚠️</a> <a href="https://github.com/gaphor/gaphor/commits?author=danyeaw" title="Documentation">📖</a> <a href="#platform-danyeaw" title="Packaging/porting to new platform">📦</a> <a href="#infra-danyeaw" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Adanyeaw" title="Bug reports">🐛</a> <a href="#question-danyeaw" title="Answering Questions">💬</a></td>
    <td align="center"><a href="https://github.com/melisdogan"><img src="https://avatars2.githubusercontent.com/u/33630433?v=4" width="100px;" alt=""/><br /><sub><b>melisdogan</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=melisdogan" title="Documentation">📖</a></td>
    <td align="center"><a href="http://www.boduch.ca"><img src="https://avatars2.githubusercontent.com/u/114619?v=4" width="100px;" alt=""/><br /><sub><b>Adam Boduch</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=adamboduch" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=adamboduch" title="Tests">⚠️</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aadamboduch" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/egroeper"><img src="https://avatars3.githubusercontent.com/u/535113?v=4" width="100px;" alt=""/><br /><sub><b>Enno Gröper</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=egroeper" title="Code">💻</a></td>
    <td align="center"><a href="https://pfeifle.tech"><img src="https://avatars2.githubusercontent.com/u/23027708?v=4" width="100px;" alt=""/><br /><sub><b>JensPfeifle</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=JensPfeifle" title="Documentation">📖</a></td>
  </tr>
  <tr>
    <td align="center"><a href="http://www.aejh.co.uk"><img src="https://avatars1.githubusercontent.com/u/927233?v=4" width="100px;" alt=""/><br /><sub><b>Alexis Howells</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=aejh" title="Documentation">📖</a></td>
    <td align="center"><a href="http://encolpe.wordpress.com"><img src="https://avatars1.githubusercontent.com/u/124361?v=4" width="100px;" alt=""/><br /><sub><b>Encolpe DEGOUTE</b></sub></a><br /><a href="#translation-encolpe" title="Translation">🌍</a></td>
    <td align="center"><a href="https://github.com/choff"><img src="https://avatars1.githubusercontent.com/u/309979?v=4" width="100px;" alt=""/><br /><sub><b>Christian Hoff</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=choff" title="Code">💻</a></td>
    <td align="center"><a href="https://oskuro.net/"><img src="https://avatars3.githubusercontent.com/u/929712?v=4" width="100px;" alt=""/><br /><sub><b>Jordi Mallach</b></sub></a><br /><a href="#translation-jmallach" title="Translation">🌍</a></td>
    <td align="center"><a href="https://github.com/tonytheleg"><img src="https://avatars3.githubusercontent.com/u/43508092?v=4" width="100px;" alt=""/><br /><sub><b>Tony</b></sub></a><br /><a href="#maintenance-tonytheleg" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/jischebeck"><img src="https://avatars0.githubusercontent.com/u/3011242?v=4" width="100px;" alt=""/><br /><sub><b>Jan</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ajischebeck" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://btibert3.github.io"><img src="https://avatars2.githubusercontent.com/u/203343?v=4" width="100px;" alt=""/><br /><sub><b>Brock Tibert</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ABtibert3" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="http://www.rmunoz.net"><img src="https://avatars2.githubusercontent.com/u/23944?v=4" width="100px;" alt=""/><br /><sub><b>Rafael Muñoz Cárdenas</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AMenda" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/mbessonov"><img src="https://avatars2.githubusercontent.com/u/172974?v=4" width="100px;" alt=""/><br /><sub><b>Mikhail Bessonov</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ambessonov" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://twitter.com/kapilvt"><img src="https://avatars3.githubusercontent.com/u/21650?v=4" width="100px;" alt=""/><br /><sub><b>Kapil Thangavelu</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Akapilt" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/DimShadoWWW"><img src="https://avatars2.githubusercontent.com/u/25516?v=4" width="100px;" alt=""/><br /><sub><b>DimShadoWWW</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ADimShadoWWW" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://nedko.arnaudov.name"><img src="https://avatars2.githubusercontent.com/u/96399?v=4" width="100px;" alt=""/><br /><sub><b>Nedko Arnaudov</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Anedko" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/Alexander-Wilms"><img src="https://avatars2.githubusercontent.com/u/3226457?v=4" width="100px;" alt=""/><br /><sub><b>Alexander Wilms</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AAlexander-Wilms" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://stevenliu216.github.io"><img src="https://avatars3.githubusercontent.com/u/1274417?v=4" width="100px;" alt=""/><br /><sub><b>Steven Liu</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Astevenliu216" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/ruimaciel"><img src="https://avatars3.githubusercontent.com/u/169121?v=4" width="100px;" alt=""/><br /><sub><b>Rui Maciel</b></sub></a><br /><a href="#ideas-ruimaciel" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/ezickler"><img src="https://avatars3.githubusercontent.com/u/3604310?v=4" width="100px;" alt=""/><br /><sub><b>Enno Zickler</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aezickler" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/tronta"><img src="https://avatars1.githubusercontent.com/u/5135577?v=4" width="100px;" alt=""/><br /><sub><b>tronta</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Atronta" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/actionless"><img src="https://avatars1.githubusercontent.com/u/1655669?v=4" width="100px;" alt=""/><br /><sub><b>Yauhen Kirylau</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=actionless" title="Documentation">📖</a> <a href="#platform-actionless" title="Packaging/porting to new platform">📦</a> <a href="#ideas-actionless" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aactionless" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://www.zorinos.com"><img src="https://avatars1.githubusercontent.com/u/34811668?v=4" width="100px;" alt=""/><br /><sub><b>albanobattistella</b></sub></a><br /><a href="#translation-albanobattistella" title="Translation">🌍</a></td>
    <td align="center"><a href="https://gavr123456789.gitlab.io/hugo-test/"><img src="https://avatars3.githubusercontent.com/u/30507409?v=4" width="100px;" alt=""/><br /><sub><b>gavr123456789</b></sub></a><br /><a href="#ideas-gavr123456789" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/Xander982"><img src="https://avatars2.githubusercontent.com/u/51178927?v=4" width="100px;" alt=""/><br /><sub><b>Xander982</b></sub></a><br /><a href="#content-Xander982" title="Content">🖋</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3AXander982" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/seryafarma"><img src="https://avatars0.githubusercontent.com/u/3274071?v=4" width="100px;" alt=""/><br /><sub><b>seryafarma</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=seryafarma" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the
[all-contributors](https://github.com/kentcdodds/all-contributors)
specification. Contributions of any kind are welcome!

1.  Check for open issues or open a fresh issue to start a discussion
    around a feature idea or a bug. There is a
    [first-timers-only](https://github.com/gaphor/gaphor/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aopen+label%3Afirst-timers-only)
    tag for issues that should be ideal for people who are not very
    familiar with the codebase yet.
2.  Fork [the repository](https://github.com/gaphor/gaphor) on
    GitHub to start making your changes to the **master** branch (or
    branch off of it).
3.  Write a test which shows that the bug was fixed or that the feature
    works as expected.
4.  Send a pull request and bug the maintainers until it gets merged and
    published. :smile:

See [the contributing file](CONTRIBUTING.md)!


## :copyright: License
Copyright (C) Arjan Molenaar and Dan Yeaw

Licensed under the [Apache License v2](LICENSE.txt).

Summary: You can do what you like with Gaphor, as long as you include the
required notices. This permissive license contains a patent license from the
contributors of the code.
