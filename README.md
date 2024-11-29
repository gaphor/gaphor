<h1 align="center"><img src="https://github.com/gaphor/gaphor/blob/main/data/logos/gaphor-logo-full.svg?raw=true" alt="Gaphor - SysML/UML Modeling" height="96"/></h1>

[![Build](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml/badge.svg)](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml?query=branch%3Amain)
[![Docs build state](https://readthedocs.org/projects/gaphor/badge/?version=latest)](https://docs.gaphor.org)
[![PyPI](https://img.shields.io/pypi/v/gaphor.svg)](https://pypi.org/project/gaphor)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gaphor)](https://pypistats.org/packages/gaphor)
[![All Contributors.org](https://img.shields.io/github/all-contributors/gaphor/gaphor/main)](https://github.com/gaphor/gaphor/blob/main/CONTRIBUTORS.md)
[![Matrix](https://img.shields.io/badge/chat-on%20Matrix-success)](https://app.element.io/#/room/#gaphor_Lobby:gitter.im)

[![Maintainability](https://api.codeclimate.com/v1/badges/f00974f5d7fe69fe4ecd/maintainability)](https://codeclimate.com/github/gaphor/gaphor/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f00974f5d7fe69fe4ecd/test_coverage)](https://codeclimate.com/github/gaphor/gaphor/test_coverage)
[![Translation Status](https://hosted.weblate.org/widgets/gaphor/-/gaphor/svg-badge.svg)](https://hosted.weblate.org/engage/gaphor)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9512/badge)](https://www.bestpractices.dev/projects/9512)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)


Gaphor is a UML and SysML modeling application written in Python.
It is designed to be easy to use, while still being powerful. Gaphor implements a fully-compliant UML 2 data model, so it is much more than a picture drawing tool. You can use Gaphor to quickly visualize different aspects of a system as well as create complete, highly complex models.

<img alt="Gaphor Demo" src="https://raw.githubusercontent.com/gaphor/gaphor/main/docs/images/gaphor-demo.gif" style="display: block; margin: 2em auto">

## 📑 Table of Contents

- [📑 Table of Contents](#-table-of-contents)
- [📜 Background](#-background)
- [💾 Install](#-install)
- [🔦 Usage](#-usage)
- [♥ Contributing](#-contributing)
  - [🌍 Translations](#-translations)
  - [♿️ Code of Conduct](#️-code-of-conduct)
- [©️ License](#️-license)

## 📜 Background

Gaphor is a UML and SysML modeling application written in Python. We designed
it to be easy to use, while still being powerful. Gaphor implements a
fully-compliant UML 2 data model, so it is much more than a picture drawing
tool. You can use Gaphor to quickly visualize different aspects of a system as
well as create complete, highly complex models.

Gaphor is designed around the following principles:

- Simplicity: The application should be easy to use. Only some basic knowledge of UML or SysML is required.
- Consistency: UML is a graphical modeling language, so all modeling is done in a diagram.
- Workability: The application should not bother the user every time they do something non-UML-ish.

Gaphor is a GUI application. It has a modern [GTK](https://gtk.org)-based interface and uses
[Cairo](https://www.cairographics.org/) for consistent rendering.

Gaphor is a library.
You can use it from [scripts and Jupyter notebooks](https://docs.gaphor.org/en/latest/scripting.html)
and interact with models programmatically.

Non-Goals:

- Generating UML diagrams from source code. [pynsource](https://github.com/abulka/pynsource) or [pyreverse](https://github.com/pylint-dev/pylint/tree/main/pylint/pyreverse) might be what you are looking for.
- Generating source code from diagrams or creating other concrete executable artifacts including use of fUML or ALF.

Although it would be possible to incorporate these features, these aren't the
goals of this project. However, if these are important capabilities for you,
you may be able to extend Gaphor by creating a
[plugin](https://docs.gaphor.org/en/latest/service_oriented.html#example-plugin).

## 💾 Install

<a href='https://flathub.org/apps/org.gaphor.Gaphor'><img alt='Download on Flathub' title='Download on Flathub' src='https://flathub.org/api/badge?svg&locale=en'/></a>

You can find [the latest version](https://gaphor.org/download) on the
[gaphor.org website](https://gaphor.org/download). Gaphor ships installers for
macOS and Windows. Those can be found there. The Python package is also
[available on PyPI](https://pypi.org/project/gaphor/).

All releases are available on
[GitHub](https://github.com/gaphor/gaphor/releases/).

If you want to start developing on Gaphor, have a look at the [Installation
section of our documentation](https://docs.gaphor.org/en/latest/).

## 🔦 Usage

If using Gaphor for the first time you will be presented with a greeter dialog
at startup in which you can select one of 5 models available to you to work in:
- **Generic:** (or blank) template
- **UML:** *Unified Modeling Language* template
- **SysML:** *Systems Modeling Language* template
- **RAAML:** *Risk Analysis and Assessment Modeling language* template
- **C4 Model:** *a lean graphical notation technique for modelling the architecture of software systems* template

After you select a template, the main Gaphor window will load, and you will be
ready to start modeling. Gaphor will automatically select the correct profile
based on the template that you selected, but you can also select other modeling
profiles if needed by clicking on the button next to the Profile dropdown menu
at the top of your window.

To select an element you want to place, for example a Class, click on the icon
in the Toolbox and then again on the diagram. This will place a new Class item
on the diagram and add a new Class to the model (it shows up in the
[Model Browser](https://docs.gaphor.org/en/latest/getting_started.html#model-browser)).

Portions of the toolbox may also be collapsed depending on the type of diagram
you are modeling with. You can expand the collapsed portions of the toolbox if
needed.

If you want to know more, please read our documentation on https://docs.gaphor.org.

## ♥ Contributing

Over 150 people that helped out building Gaphor. Too many to show in this readme.
You can find them in [CONTRIBUTORS file](CONTRIBUTORS.md).

Would you like to contribute to the development of Gaphor?
There are many ways in which you can help out:

* Review and update documentation.
* Open discussions on a feature/bug/idea
* Fix an [open issue](https://github.com/gaphor/gaphor/issues)
* Tell other people about Gaphor.

We appreciate contributions of any kind.
This project follows the
[all-contributors](https://github.com/kentcdodds/all-contributors)
specification. Contributions of any kind are welcome!

More info on how you can contribute can be found in [the contributing guide](CONTRIBUTING.md)!

### 🌍 Translations

Translation of Gaphor is mostly done using
[Weblate](https://hosted.weblate.org/projects/gaphor/gaphor/).

For the Linux Flatpak, the desktop entry comment string can be translated at our
[Flatpak
repository](https://github.com/flathub/org.gaphor.Gaphor/blob/master/share/org.gaphor.Gaphor.desktop).

Thank you so much for your effort in helping us keep it available in many
languages!

<a href="https://hosted.weblate.org/engage/gaphor/">
<img src="https://hosted.weblate.org/widgets/gaphor/-/glossary/multi-auto.svg" alt="Translation status" />
</a>

### ♿️ Code of Conduct

We value your participation and want everyone to have an enjoyable and
fulfilling experience. As a [GNOME Circle](https://circle.gnome.org/) project,
all participants are expected to follow the GNOME [Code of
Conduct](https://conduct.gnome.org) and to show respect,
understanding, and consideration to one another. Thank you for helping make this
a welcoming, friendly community for everyone.

## ©️ License

Copyright © The Gaphor Development Team

Licensed under the [Apache License v2](LICENSES/Apache-2.0.txt).

Summary: You can do what you like with Gaphor, as long as you include the
required notices. This permissive license contains a patent license from the
contributors of the code.
