<h1 align="center"><img src="https://github.com/gaphor/gaphor/blob/main/data/logos/gaphor-logo-full.svg?raw=true" alt="Gaphor - SysML/UML Modeling" height="96"/></h1>

[![Build](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml/badge.svg)](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml?query=branch%3Amain)
[![Docs build state](https://readthedocs.org/projects/gaphor/badge/?version=latest)](https://docs.gaphor.org)
[![PyPI](https://img.shields.io/pypi/v/gaphor.svg)](https://pypi.org/project/gaphor)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gaphor)](https://pypistats.org/packages/gaphor)
[![Matrix](https://img.shields.io/badge/chat-on%20Matrix-success)](https://app.element.io/#/room/#gaphor_Lobby:gitter.im)

[![Maintainability](https://api.codeclimate.com/v1/badges/f00974f5d7fe69fe4ecd/maintainability)](https://codeclimate.com/github/gaphor/gaphor/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f00974f5d7fe69fe4ecd/test_coverage)](https://codeclimate.com/github/gaphor/gaphor/test_coverage)
[![Translation Status](https://hosted.weblate.org/widgets/gaphor/-/gaphor/svg-badge.svg)](https://hosted.weblate.org/engage/gaphor)
[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)
[![All Contributors.org](https://img.shields.io/github/all-contributors/gaphor/gaphor/main)](#contributors)


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

<a href='https://flathub.org/apps/org.gaphor.Gaphor'><img width='240' alt='Download on Flathub' title='Download on Flathub' src='https://dl.flathub.org/assets/badges/flathub-badge-en.svg'/></a>

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

Thanks goes to these wonderful people ([emoji key](https://github.com/kentcdodds/all-contributors#emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/2old4it"><img src="https://avatars.githubusercontent.com/u/76972837?v=4?s=100" width="100px;" alt="2old4it"/><br /><sub><b>2old4it</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3A2old4it" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/2old4this"><img src="https://avatars.githubusercontent.com/u/108221?v=4?s=100" width="100px;" alt="2old4this"/><br /><sub><b>2old4this</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3A2old4this" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/3fla1416"><img src="https://avatars.githubusercontent.com/u/108428517?v=4?s=100" width="100px;" alt="3fla1416"/><br /><sub><b>3fla1416</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3A3fla1416" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/abjurstrom-torch"><img src="https://avatars1.githubusercontent.com/u/62608984?v=4?s=100" width="100px;" alt="Adam Bjurstrom"/><br /><sub><b>Adam Bjurstrom</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aabjurstrom-torch" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.boduch.ca"><img src="https://avatars2.githubusercontent.com/u/114619?v=4?s=100" width="100px;" alt="Adam Boduch"/><br /><sub><b>Adam Boduch</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=adamboduch" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=adamboduch" title="Tests">⚠️</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aadamboduch" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/alensiljak"><img src="https://avatars.githubusercontent.com/u/462445?v=4?s=100" width="100px;" alt="Alen Šiljak"/><br /><sub><b>Alen Šiljak</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aalensiljak" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Alexander-Wilms"><img src="https://avatars2.githubusercontent.com/u/3226457?v=4?s=100" width="100px;" alt="Alexander Wilms"/><br /><sub><b>Alexander Wilms</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AAlexander-Wilms" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://www.aejh.co.uk"><img src="https://avatars1.githubusercontent.com/u/927233?v=4?s=100" width="100px;" alt="Alexis Howells"/><br /><sub><b>Alexis Howells</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=aejh" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Psycomentis06"><img src="https://avatars.githubusercontent.com/u/58190728?v=4?s=100" width="100px;" alt="Amor Ali"/><br /><sub><b>Amor Ali</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3APsycomentis06" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://ayanamy.is-a.dev/"><img src="https://avatars.githubusercontent.com/u/50583248?v=4?s=100" width="100px;" alt="Amy Y"/><br /><sub><b>Amy Y</b></sub></a><br /><a href="#translation-jy1263" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://andreizisu.webmonsters.ro"><img src="https://avatars.githubusercontent.com/u/317239?v=4?s=100" width="100px;" alt="Andrei"/><br /><sub><b>Andrei</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Amatzipan" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://anreji.de"><img src="https://avatars.githubusercontent.com/u/69592284?v=4?s=100" width="100px;" alt="Andrew"/><br /><sub><b>Andrew</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aanreji" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Seant-Dev"><img src="https://avatars.githubusercontent.com/u/62353416?v=4?s=100" width="100px;" alt="Antonio Mejia"/><br /><sub><b>Antonio Mejia</b></sub></a><br /><a href="#translation-Seant-Dev" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/amolenaar"><img src="https://avatars0.githubusercontent.com/u/96249?v=4?s=100" width="100px;" alt="Arjan Molenaar"/><br /><sub><b>Arjan Molenaar</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=amolenaar" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aamolenaar" title="Bug reports">🐛</a> <a href="https://github.com/gaphor/gaphor/commits?author=amolenaar" title="Documentation">📖</a> <a href="https://github.com/gaphor/gaphor/pulls?q=is%3Apr+reviewed-by%3Aamolenaar" title="Reviewed Pull Requests">👀</a> <a href="#question-amolenaar" title="Answering Questions">💬</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aamolenaar" title="Bug reports">🐛</a> <a href="#plugin-amolenaar" title="Plugin/utility libraries">🔌</a> <a href="https://github.com/gaphor/gaphor/commits?author=amolenaar" title="Tests">⚠️</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ajoga"><img src="https://avatars.githubusercontent.com/u/37543966?v=4?s=100" width="100px;" alt="Aurélien Joga"/><br /><sub><b>Aurélien Joga</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=ajoga" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Lutra-Fs"><img src="https://avatars.githubusercontent.com/u/36790218?v=4?s=100" width="100px;" alt="Bill ZHANG"/><br /><sub><b>Bill ZHANG</b></sub></a><br /><a href="#translation-Lutra-Fs" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bjornstromberg"><img src="https://avatars.githubusercontent.com/u/5454791?v=4?s=100" width="100px;" alt="Björn Strömberg"/><br /><sub><b>Björn Strömberg</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Abjornstromberg" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/blippost"><img src="https://avatars.githubusercontent.com/u/74373678?v=4?s=100" width="100px;" alt="Blippost"/><br /><sub><b>Blippost</b></sub></a><br /><a href="#ideas-Blippost" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bragefuglseth.dev"><img src="https://avatars.githubusercontent.com/u/91388039?v=4?s=100" width="100px;" alt="Brage Fuglseth"/><br /><sub><b>Brage Fuglseth</b></sub></a><br /><a href="#design-bragefuglseth" title="Design">🎨</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bglendenning"><img src="https://avatars.githubusercontent.com/u/8276428?v=4?s=100" width="100px;" alt="Brandan Glendenning"/><br /><sub><b>Brandan Glendenning</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=bglendenning" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://btibert3.github.io"><img src="https://avatars2.githubusercontent.com/u/203343?v=4?s=100" width="100px;" alt="Brock Tibert"/><br /><sub><b>Brock Tibert</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ABtibert3" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/can-lehmann"><img src="https://avatars.githubusercontent.com/u/85876381?v=4?s=100" width="100px;" alt="Can Lehmann"/><br /><sub><b>Can Lehmann</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=can-lehmann" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/choff"><img src="https://avatars1.githubusercontent.com/u/309979?v=4?s=100" width="100px;" alt="Christian Hoff"/><br /><sub><b>Christian Hoff</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=choff" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DKX47"><img src="https://avatars.githubusercontent.com/u/12964384?v=4?s=100" width="100px;" alt="DKX47"/><br /><sub><b>DKX47</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ADKX47" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://ghuser.io/danyeaw"><img src="https://avatars1.githubusercontent.com/u/10014976?v=4?s=100" width="100px;" alt="Dan Yeaw"/><br /><sub><b>Dan Yeaw</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=danyeaw" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=danyeaw" title="Tests">⚠️</a> <a href="https://github.com/gaphor/gaphor/commits?author=danyeaw" title="Documentation">📖</a> <a href="#platform-danyeaw" title="Packaging/porting to new platform">📦</a> <a href="#infra-danyeaw" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Adanyeaw" title="Bug reports">🐛</a> <a href="#question-danyeaw" title="Answering Questions">💬</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/dk-zero-cool"><img src="https://avatars.githubusercontent.com/u/1395583?v=4?s=100" width="100px;" alt="Daniel Bergløv"/><br /><sub><b>Daniel Bergløv</b></sub></a><br /><a href="#ideas-dk-zero-cool" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://fediscience.org/@Daniel_Hulse"><img src="https://avatars.githubusercontent.com/u/23367230?v=4?s=100" width="100px;" alt="Daniel Hulse"/><br /><sub><b>Daniel Hulse</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=hulsed" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.DanielNylander.se"><img src="https://avatars.githubusercontent.com/u/1206564?v=4?s=100" width="100px;" alt="Daniel Nylander"/><br /><sub><b>Daniel Nylander</b></sub></a><br /><a href="#translation-yeager" title="Translation">🌍</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DimShadoWWW"><img src="https://avatars2.githubusercontent.com/u/25516?v=4?s=100" width="100px;" alt="DimShadoWWW"/><br /><sub><b>DimShadoWWW</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ADimShadoWWW" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Texopolis"><img src="https://avatars.githubusercontent.com/u/88953534?v=4?s=100" width="100px;" alt="Douglas B"/><br /><sub><b>Douglas B</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=Texopolis" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://encolpe.wordpress.com"><img src="https://avatars1.githubusercontent.com/u/124361?v=4?s=100" width="100px;" alt="Encolpe DEGOUTE"/><br /><sub><b>Encolpe DEGOUTE</b></sub></a><br /><a href="#translation-encolpe" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/egroeper"><img src="https://avatars3.githubusercontent.com/u/535113?v=4?s=100" width="100px;" alt="Enno Gröper"/><br /><sub><b>Enno Gröper</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=egroeper" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ezickler"><img src="https://avatars3.githubusercontent.com/u/3604310?v=4?s=100" width="100px;" alt="Enno Zickler"/><br /><sub><b>Enno Zickler</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aezickler" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ercalvez"><img src="https://avatars.githubusercontent.com/u/45692523?v=4?s=100" width="100px;" alt="Ercalvez"/><br /><sub><b>Ercalvez</b></sub></a><br /><a href="#translation-Ercalvez" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bousse-e.univ-nantes.io"><img src="https://avatars.githubusercontent.com/u/5868014?v=4?s=100" width="100px;" alt="Erwan Bousse"/><br /><sub><b>Erwan Bousse</b></sub></a><br /><a href="#ideas-ebousse" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aebousse" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gnu-ewm"><img src="https://avatars.githubusercontent.com/u/73967801?v=4?s=100" width="100px;" alt="Eryk Michalak"/><br /><sub><b>Eryk Michalak</b></sub></a><br /><a href="#translation-gnu-ewm" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/fnogcps"><img src="https://avatars.githubusercontent.com/u/27527497?v=4?s=100" width="100px;" alt="Felipe Nogueira"/><br /><sub><b>Felipe Nogueira</b></sub></a><br /><a href="#translation-fnogcps" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Fell-x27"><img src="https://avatars.githubusercontent.com/u/18358207?v=4?s=100" width="100px;" alt="Fell-x27"/><br /><sub><b>Fell-x27</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AFell-x27" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.frandieguez.dev"><img src="https://avatars.githubusercontent.com/u/4584?v=4?s=100" width="100px;" alt="Fran Diéguez"/><br /><sub><b>Fran Diéguez</b></sub></a><br /><a href="#translation-frandieguez" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/FranciscoTGouveia"><img src="https://avatars.githubusercontent.com/u/93057203?v=4?s=100" width="100px;" alt="Francisco Gouveia"/><br /><sub><b>Francisco Gouveia</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=FranciscoTGouveia" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gbrlgian"><img src="https://avatars.githubusercontent.com/u/47647695?v=4?s=100" width="100px;" alt="Gabriel Gian"/><br /><sub><b>Gabriel Gian</b></sub></a><br /><a href="#translation-gbrlgian" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/liferooter"><img src="https://avatars.githubusercontent.com/u/54807745?v=4?s=100" width="100px;" alt="Gleb Smirnov"/><br /><sub><b>Gleb Smirnov</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aliferooter" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://gjstewart.net"><img src="https://avatars.githubusercontent.com/u/7083701?v=4?s=100" width="100px;" alt="Greg Stewart"/><br /><sub><b>Greg Stewart</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AGregJohnStewart" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Gytree"><img src="https://avatars.githubusercontent.com/u/28499079?v=4?s=100" width="100px;" alt="Gytree"/><br /><sub><b>Gytree</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AGytree" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.gunibert.de"><img src="https://avatars.githubusercontent.com/u/373597?v=4?s=100" width="100px;" alt="Günther Wagner"/><br /><sub><b>Günther Wagner</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Agwutz" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.hamishmb.com"><img src="https://avatars.githubusercontent.com/u/16725441?v=4?s=100" width="100px;" alt="Hamish Mcintyre-Bhatty"/><br /><sub><b>Hamish Mcintyre-Bhatty</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ahamishmb" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/HighKingofMelons"><img src="https://avatars.githubusercontent.com/u/27958428?v=4?s=100" width="100px;" alt="HighKingofMelons"/><br /><sub><b>HighKingofMelons</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AHighKingofMelons" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Linuxiness"><img src="https://avatars.githubusercontent.com/u/99252096?v=4?s=100" width="100px;" alt="Igor Lerinc"/><br /><sub><b>Igor Lerinc</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ALinuxiness" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bandism.net/"><img src="https://avatars.githubusercontent.com/u/22633385?v=4?s=100" width="100px;" alt="Ikko Ashimine"/><br /><sub><b>Ikko Ashimine</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=eltociear" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://boghma.com/"><img src="https://avatars.githubusercontent.com/u/87265559?v=4?s=100" width="100px;" alt="JACKADUX"/><br /><sub><b>JACKADUX</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AJACKADUX" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://jcrabill.weebly.com/"><img src="https://avatars.githubusercontent.com/u/5885545?v=4?s=100" width="100px;" alt="Jacob Crabill"/><br /><sub><b>Jacob Crabill</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AJacobCrabill" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://blogs.igalia.com/jaragunde/"><img src="https://avatars.githubusercontent.com/u/2900877?v=4?s=100" width="100px;" alt="Jacobo Aragunde Pérez"/><br /><sub><b>Jacobo Aragunde Pérez</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ajaragunde" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jischebeck"><img src="https://avatars0.githubusercontent.com/u/3011242?v=4?s=100" width="100px;" alt="Jan"/><br /><sub><b>Jan</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ajischebeck" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://eugentoptic44.codeberg.page/"><img src="https://avatars.githubusercontent.com/u/90517741?v=4?s=100" width="100px;" alt="Jean-Luc Tibaux"/><br /><sub><b>Jean-Luc Tibaux</b></sub></a><br /><a href="#translation-eUgEntOptIc44" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://pfeifle.tech"><img src="https://avatars2.githubusercontent.com/u/23027708?v=4?s=100" width="100px;" alt="JensPfeifle"/><br /><sub><b>JensPfeifle</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=JensPfeifle" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/vanillajonathan"><img src="https://avatars.githubusercontent.com/u/10222521?v=4?s=100" width="100px;" alt="Jonathan"/><br /><sub><b>Jonathan</b></sub></a><br /><a href="#ideas-vanillajonathan" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Avanillajonathan" title="Bug reports">🐛</a> <a href="#translation-vanillajonathan" title="Translation">🌍</a> <a href="https://github.com/gaphor/gaphor/commits?author=vanillajonathan" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://twitter.com/yonkeltron"><img src="https://avatars.githubusercontent.com/u/59451?v=4?s=100" width="100px;" alt="Jonathan E. Magen"/><br /><sub><b>Jonathan E. Magen</b></sub></a><br /><a href="#ideas-yonkeltron" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://jonnathanriquelmo.github.io/"><img src="https://avatars.githubusercontent.com/u/13298966?v=4?s=100" width="100px;" alt="JonnathanRiquelmo"/><br /><sub><b>JonnathanRiquelmo</b></sub></a><br /><a href="#translation-JonnathanRiquelmo" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://oskuro.net/"><img src="https://avatars3.githubusercontent.com/u/929712?v=4?s=100" width="100px;" alt="Jordi Mallach"/><br /><sub><b>Jordi Mallach</b></sub></a><br /><a href="#translation-jmallach" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/dlagg"><img src="https://avatars3.githubusercontent.com/u/44321931?v=4?s=100" width="100px;" alt="Jorge DLG"/><br /><sub><b>Jorge DLG</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Adlagg" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/0lione"><img src="https://avatars.githubusercontent.com/u/101414931?v=4?s=100" width="100px;" alt="João Correia"/><br /><sub><b>João Correia</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=0lione" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/h8672"><img src="https://avatars.githubusercontent.com/u/8805540?v=4?s=100" width="100px;" alt="Juha-Matti Kokkonen"/><br /><sub><b>Juha-Matti Kokkonen</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ah8672" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://jrueberg.de"><img src="https://avatars.githubusercontent.com/u/22551563?v=4?s=100" width="100px;" alt="Julius Rüberg"/><br /><sub><b>Julius Rüberg</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AToorero" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/JuliusBrueggemann"><img src="https://avatars.githubusercontent.com/u/35491022?v=4?s=100" width="100px;" alt="JuliusBrueggemann"/><br /><sub><b>JuliusBrueggemann</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AJuliusBrueggemann" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://kbdharun.dev"><img src="https://avatars.githubusercontent.com/u/26346867?v=4?s=100" width="100px;" alt="K.B.Dharun Krishna"/><br /><sub><b>K.B.Dharun Krishna</b></sub></a><br /><a href="#translation-kbdharun" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://twitter.com/kapilvt"><img src="https://avatars3.githubusercontent.com/u/21650?v=4?s=100" width="100px;" alt="Kapil Thangavelu"/><br /><sub><b>Kapil Thangavelu</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Akapilt" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/KhazAkar"><img src="https://avatars.githubusercontent.com/u/12693890?v=4?s=100" width="100px;" alt="KhazAkar"/><br /><sub><b>KhazAkar</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AKhazAkar" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.kianmeng.org"><img src="https://avatars.githubusercontent.com/u/134518?v=4?s=100" width="100px;" alt="Kian-Meng Ang"/><br /><sub><b>Kian-Meng Ang</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=kianmeng" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Lazerbeak12345"><img src="https://avatars.githubusercontent.com/u/22641188?v=4?s=100" width="100px;" alt="Lazerbeak12345"/><br /><sub><b>Lazerbeak12345</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ALazerbeak12345" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/LordSinSentido"><img src="https://avatars.githubusercontent.com/u/57022857?v=4?s=100" width="100px;" alt="Lordy"/><br /><sub><b>Lordy</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ALordSinSentido" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://monkington.github.io"><img src="https://avatars.githubusercontent.com/u/778856?v=4?s=100" width="100px;" alt="Mark Kennedy"/><br /><sub><b>Mark Kennedy</b></sub></a><br /><a href="#ideas-mrmonkington" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/commits?author=mrmonkington" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Amrmonkington" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/markdluethje"><img src="https://avatars.githubusercontent.com/u/31922494?v=4?s=100" width="100px;" alt="Mark-Daniel Lüthje"/><br /><sub><b>Mark-Daniel Lüthje</b></sub></a><br /><a href="#translation-markdluethje" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mathiascode"><img src="https://avatars.githubusercontent.com/u/8754153?v=4?s=100" width="100px;" alt="Mat"/><br /><sub><b>Mat</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=mathiascode" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kainne44"><img src="https://avatars.githubusercontent.com/u/50899654?v=4?s=100" width="100px;" alt="Matthew Maclaine"/><br /><sub><b>Matthew Maclaine</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Akainne44" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://bendiks.de"><img src="https://avatars.githubusercontent.com/u/8329544?v=4?s=100" width="100px;" alt="Maxim"/><br /><sub><b>Maxim</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aascaron37" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Mek101"><img src="https://avatars.githubusercontent.com/u/34246799?v=4?s=100" width="100px;" alt="Mek101"/><br /><sub><b>Mek101</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AMek101" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mvinca-bandwidth"><img src="https://avatars.githubusercontent.com/u/93543843?v=4?s=100" width="100px;" alt="Michael J. Vinca"/><br /><sub><b>Michael J. Vinca</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Amvinca-bandwidth" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/c4tachan"><img src="https://avatars.githubusercontent.com/u/2130211?v=4?s=100" width="100px;" alt="Michael Patrick Tkacik"/><br /><sub><b>Michael Patrick Tkacik</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ac4tachan" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mbessonov"><img src="https://avatars2.githubusercontent.com/u/172974?v=4?s=100" width="100px;" alt="Mikhail Bessonov"/><br /><sub><b>Mikhail Bessonov</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ambessonov" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.esco-medical.com/"><img src="https://avatars.githubusercontent.com/u/1454086?v=4?s=100" width="100px;" alt="Mikkel Aunsbjerg Jakobsen"/><br /><sub><b>Mikkel Aunsbjerg Jakobsen</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aaunsbjerg" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://linfindel.github.io"><img src="https://avatars.githubusercontent.com/u/116459177?v=4?s=100" width="100px;" alt="Nathan Hadley"/><br /><sub><b>Nathan Hadley</b></sub></a><br /><a href="#translation-linfindel" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://nedko.arnaudov.name"><img src="https://avatars2.githubusercontent.com/u/96399?v=4?s=100" width="100px;" alt="Nedko Arnaudov"/><br /><sub><b>Nedko Arnaudov</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Anedko" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/flatrick"><img src="https://avatars.githubusercontent.com/u/5464311?v=4?s=100" width="100px;" alt="Patrik"/><br /><sub><b>Patrik</b></sub></a><br /><a href="#ideas-flatrick" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.molgen.mpg.de"><img src="https://avatars.githubusercontent.com/u/9318792?v=4?s=100" width="100px;" alt="Paul Menzel"/><br /><sub><b>Paul Menzel</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=paulmenzel" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/pajakpawel"><img src="https://avatars.githubusercontent.com/u/32963953?v=4?s=100" width="100px;" alt="Paweł Pająk"/><br /><sub><b>Paweł Pająk</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Apajakpawel" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Petalzu"><img src="https://avatars.githubusercontent.com/u/106128925?v=4?s=100" width="100px;" alt="Petal"/><br /><sub><b>Petal</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=Petalzu" title="Documentation">📖</a> <a href="#translation-Petalzu" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/philwilkinson40"><img src="https://avatars.githubusercontent.com/u/27684871?v=4?s=100" width="100px;" alt="Phil_Smurf"/><br /><sub><b>Phil_Smurf</b></sub></a><br /><a href="#ideas-philwilkinson40" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/flipflop97"><img src="https://avatars.githubusercontent.com/u/13943260?v=4?s=100" width="100px;" alt="Philip Goto"/><br /><sub><b>Philip Goto</b></sub></a><br /><a href="#translation-flipflop97" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/rffontenelle"><img src="https://avatars.githubusercontent.com/u/1571783?v=4?s=100" width="100px;" alt="Rafael Fontenelle"/><br /><sub><b>Rafael Fontenelle</b></sub></a><br /><a href="#translation-rffontenelle" title="Translation">🌍</a> <a href="#ideas-rffontenelle" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.rmunoz.net"><img src="https://avatars2.githubusercontent.com/u/23944?v=4?s=100" width="100px;" alt="Rafael Muñoz Cárdenas"/><br /><sub><b>Rafael Muñoz Cárdenas</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AMenda" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/RenStone83"><img src="https://avatars.githubusercontent.com/u/106451678?v=4?s=100" width="100px;" alt="RenStone83"/><br /><sub><b>RenStone83</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ARenStone83" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://richardbamford.dev/"><img src="https://avatars.githubusercontent.com/u/1304898?v=4?s=100" width="100px;" alt="Richard Bamford"/><br /><sub><b>Richard Bamford</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ABambofy" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ruimaciel"><img src="https://avatars3.githubusercontent.com/u/169121?v=4?s=100" width="100px;" alt="Rui Maciel"/><br /><sub><b>Rui Maciel</b></sub></a><br /><a href="#ideas-ruimaciel" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.yakusha.net"><img src="https://avatars.githubusercontent.com/u/6218679?v=4?s=100" width="100px;" alt="Sabri Ünal"/><br /><sub><b>Sabri Ünal</b></sub></a><br /><a href="#translation-sabriunal" title="Translation">🌍</a> <a href="https://github.com/gaphor/gaphor/commits?author=sabriunal" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.uni-kassel.de/go/holzhauer"><img src="https://avatars.githubusercontent.com/u/1692563?v=4?s=100" width="100px;" alt="Sascha Holzhauer"/><br /><sub><b>Sascha Holzhauer</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AHolzhauer" title="Bug reports">🐛</a> <a href="https://github.com/gaphor/gaphor/commits?author=Holzhauer" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/SebCanet"><img src="https://avatars.githubusercontent.com/u/6362199?v=4?s=100" width="100px;" alt="SebCanet"/><br /><sub><b>SebCanet</b></sub></a><br /><a href="#ideas-SebCanet" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Seppli11"><img src="https://avatars.githubusercontent.com/u/9285506?v=4?s=100" width="100px;" alt="Sebi"/><br /><sub><b>Sebi</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ASeppli11" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/darkcircle"><img src="https://avatars.githubusercontent.com/u/1160498?v=4?s=100" width="100px;" alt="Seong-ho Cho"/><br /><sub><b>Seong-ho Cho</b></sub></a><br /><a href="#translation-darkcircle" title="Translation">🌍</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ser82-png"><img src="https://avatars.githubusercontent.com/u/83226922?v=4?s=100" width="100px;" alt="Sergej A."/><br /><sub><b>Sergej A.</b></sub></a><br /><a href="#translation-Ser82-png" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://blogs.gnome.org/sophieh/"><img src="https://avatars.githubusercontent.com/u/3466497?v=4?s=100" width="100px;" alt="Sophie Herold"/><br /><sub><b>Sophie Herold</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=sophie-h" title="Code">💻</a> <a href="#a11y-sophie-h" title="Accessibility">️️️️♿️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/artscoop"><img src="https://avatars.githubusercontent.com/u/1023091?v=4?s=100" width="100px;" alt="Steve Kossouho"/><br /><sub><b>Steve Kossouho</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aartscoop" title="Bug reports">🐛</a> <a href="https://github.com/gaphor/gaphor/commits?author=artscoop" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://stevenliu216.github.io"><img src="https://avatars3.githubusercontent.com/u/1274417?v=4?s=100" width="100px;" alt="Steven Liu"/><br /><sub><b>Steven Liu</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Astevenliu216" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Sycophantic-Witty"><img src="https://avatars.githubusercontent.com/u/94297113?v=4?s=100" width="100px;" alt="Sycophantic-Witty"/><br /><sub><b>Sycophantic-Witty</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ASycophantic-Witty" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/teunhoevenaars"><img src="https://avatars.githubusercontent.com/u/41649398?v=4?s=100" width="100px;" alt="Teun Hoevenaars"/><br /><sub><b>Teun Hoevenaars</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=teunhoevenaars" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.slide.nz"><img src="https://avatars.githubusercontent.com/u/47554072?v=4?s=100" width="100px;" alt="Thomas"/><br /><sub><b>Thomas</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ACoderThomasB" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tfirchau"><img src="https://avatars.githubusercontent.com/u/71006757?v=4?s=100" width="100px;" alt="Thomas Firchau"/><br /><sub><b>Thomas Firchau</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=tfirchau" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/TiemenSch"><img src="https://avatars.githubusercontent.com/u/7141863?v=4?s=100" width="100px;" alt="Tiemen Schuijbroek"/><br /><sub><b>Tiemen Schuijbroek</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ATiemenSch" title="Bug reports">🐛</a> <a href="https://github.com/gaphor/gaphor/commits?author=TiemenSch" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://tobiasbernard.com"><img src="https://avatars3.githubusercontent.com/u/1908896?v=4?s=100" width="100px;" alt="Tobias Bernard"/><br /><sub><b>Tobias Bernard</b></sub></a><br /><a href="#design-bertob" title="Design">🎨</a> <a href="#ideas-bertob" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/TomBous"><img src="https://avatars.githubusercontent.com/u/10131977?v=4?s=100" width="100px;" alt="TomBous"/><br /><sub><b>TomBous</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3ATomBous" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tomaszdrozdz"><img src="https://avatars.githubusercontent.com/u/14263613?v=4?s=100" width="100px;" alt="Tomasz Drożdż"/><br /><sub><b>Tomasz Drożdż</b></sub></a><br /><a href="#ideas-tomaszdrozdz" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tonytheleg"><img src="https://avatars3.githubusercontent.com/u/43508092?v=4?s=100" width="100px;" alt="Tony"/><br /><sub><b>Tony</b></sub></a><br /><a href="#maintenance-tonytheleg" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Viicos"><img src="https://avatars.githubusercontent.com/u/65306057?v=4?s=100" width="100px;" alt="Viicos"/><br /><sub><b>Viicos</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3AViicos" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Xander982"><img src="https://avatars2.githubusercontent.com/u/51178927?v=4?s=100" width="100px;" alt="Xander982"/><br /><sub><b>Xander982</b></sub></a><br /><a href="#content-Xander982" title="Content">🖋</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3AXander982" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/yantaozhao"><img src="https://avatars.githubusercontent.com/u/9587405?v=4?s=100" width="100px;" alt="YantaoZhao"/><br /><sub><b>YantaoZhao</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ayantaozhao" title="Bug reports">🐛</a> <a href="#ideas-yantaozhao" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/actionless"><img src="https://avatars1.githubusercontent.com/u/1655669?v=4?s=100" width="100px;" alt="Yauhen Kirylau"/><br /><sub><b>Yauhen Kirylau</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=actionless" title="Documentation">📖</a> <a href="#platform-actionless" title="Packaging/porting to new platform">📦</a> <a href="#ideas-actionless" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aactionless" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sz332"><img src="https://avatars.githubusercontent.com/u/8182138?v=4?s=100" width="100px;" alt="Zsolt Sandor"/><br /><sub><b>Zsolt Sandor</b></sub></a><br /><a href="#ideas-sz332" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Asz332" title="Bug reports">🐛</a> <a href="https://github.com/gaphor/gaphor/commits?author=sz332" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=sz332" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/njase"><img src="https://avatars.githubusercontent.com/u/20597737?v=4?s=100" width="100px;" alt="\s\m"/><br /><sub><b>\s\m</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=njase" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.zorinos.com"><img src="https://avatars1.githubusercontent.com/u/34811668?v=4?s=100" width="100px;" alt="albanobattistella"/><br /><sub><b>albanobattistella</b></sub></a><br /><a href="#translation-albanobattistella" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/alkis05"><img src="https://avatars.githubusercontent.com/u/5754055?v=4?s=100" width="100px;" alt="alkis05"/><br /><sub><b>alkis05</b></sub></a><br /><a href="#ideas-alkis05" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bayerl"><img src="https://avatars.githubusercontent.com/u/16454634?v=4?s=100" width="100px;" alt="bayerl"/><br /><sub><b>bayerl</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=bayerl" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/cloud-erik"><img src="https://avatars.githubusercontent.com/u/67910530?v=4?s=100" width="100px;" alt="cloud-erik"/><br /><sub><b>cloud-erik</b></sub></a><br /><a href="#ideas-cloud-erik" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/deifemu"><img src="https://avatars.githubusercontent.com/u/81991548?v=4?s=100" width="100px;" alt="deifemu"/><br /><sub><b>deifemu</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Adeifemu" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/freddii"><img src="https://avatars0.githubusercontent.com/u/7213207?v=4?s=100" width="100px;" alt="freddii"/><br /><sub><b>freddii</b></sub></a><br /><a href="#ideas-freddii" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/commits?author=freddii" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/freezed-or-frozen"><img src="https://avatars.githubusercontent.com/u/28558919?v=4?s=100" width="100px;" alt="freezed-or-frozen"/><br /><sub><b>freezed-or-frozen</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Afreezed-or-frozen" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/fu7mu4"><img src="https://avatars.githubusercontent.com/u/1885537?v=4?s=100" width="100px;" alt="fu7mu4"/><br /><sub><b>fu7mu4</b></sub></a><br /><a href="#translation-fu7mu4" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://gavr123456789.gitlab.io/hugo-test/"><img src="https://avatars3.githubusercontent.com/u/30507409?v=4?s=100" width="100px;" alt="gavr123456789"/><br /><sub><b>gavr123456789</b></sub></a><br /><a href="#ideas-gavr123456789" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://www.isijingi.co.za"><img src="https://avatars.githubusercontent.com/u/9532378?v=4?s=100" width="100px;" alt="ghillebrand"/><br /><sub><b>ghillebrand</b></sub></a><br /><a href="#ideas-ghillebrand" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/greedyj4ck"><img src="https://avatars.githubusercontent.com/u/33233389?v=4?s=100" width="100px;" alt="greedyj4ck"/><br /><sub><b>greedyj4ck</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Agreedyj4ck" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/johnvonlzf"><img src="https://avatars.githubusercontent.com/u/5709453?v=4?s=100" width="100px;" alt="johnvon"/><br /><sub><b>johnvon</b></sub></a><br /><a href="#translation-johnvonlzf" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jposada202020"><img src="https://avatars.githubusercontent.com/u/34255413?v=4?s=100" width="100px;" alt="jposada202020"/><br /><sub><b>jposada202020</b></sub></a><br /><a href="#translation-jposada202020" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kellenmoura"><img src="https://avatars0.githubusercontent.com/u/69016459?v=4?s=100" width="100px;" alt="kellenmoura"/><br /><sub><b>kellenmoura</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Akellenmoura" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/lightonflux"><img src="https://avatars.githubusercontent.com/u/1377943?v=4?s=100" width="100px;" alt="lightonflux"/><br /><sub><b>lightonflux</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Alightonflux" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/lukman83"><img src="https://avatars.githubusercontent.com/u/69509634?v=4?s=100" width="100px;" alt="lukman83"/><br /><sub><b>lukman83</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Alukman83" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/madiharvey"><img src="https://avatars.githubusercontent.com/u/136543386?v=4?s=100" width="100px;" alt="madiharvey"/><br /><sub><b>madiharvey</b></sub></a><br /><a href="#ideas-madiharvey" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Amadiharvey" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/matgaj"><img src="https://avatars.githubusercontent.com/u/10777373?v=4?s=100" width="100px;" alt="matgaj"/><br /><sub><b>matgaj</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Amatgaj" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mcdigregorio"><img src="https://avatars.githubusercontent.com/u/17177951?v=4?s=100" width="100px;" alt="mcdigregorio"/><br /><sub><b>mcdigregorio</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Amcdigregorio" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/melisdogan"><img src="https://avatars2.githubusercontent.com/u/33630433?v=4?s=100" width="100px;" alt="melisdogan"/><br /><sub><b>melisdogan</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=melisdogan" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mikekidner"><img src="https://avatars.githubusercontent.com/u/50702106?v=4?s=100" width="100px;" alt="mikekidner"/><br /><sub><b>mikekidner</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Amikekidner" title="Bug reports">🐛</a> <a href="https://github.com/gaphor/gaphor/commits?author=mikekidner" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=mikekidner" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/milotype"><img src="https://avatars.githubusercontent.com/u/43657314?v=4?s=100" width="100px;" alt="milotype"/><br /><sub><b>milotype</b></sub></a><br /><a href="#translation-milotype" title="Translation">🌍</a> <a href="https://github.com/gaphor/gaphor/commits?author=milotype" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mskorkowski"><img src="https://avatars.githubusercontent.com/u/90662755?v=4?s=100" width="100px;" alt="mskorkowski"/><br /><sub><b>mskorkowski</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Amskorkowski" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/noblevirk"><img src="https://avatars.githubusercontent.com/u/5385824?v=4?s=100" width="100px;" alt="noblevirk"/><br /><sub><b>noblevirk</b></sub></a><br /><a href="#ideas-noblevirk" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/nomisge"><img src="https://avatars.githubusercontent.com/u/16142147?v=4?s=100" width="100px;" alt="nomisge"/><br /><sub><b>nomisge</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Anomisge" title="Bug reports">🐛</a> <a href="#ideas-nomisge" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ovari"><img src="https://avatars.githubusercontent.com/u/17465872?v=4?s=100" width="100px;" alt="ovari"/><br /><sub><b>ovari</b></sub></a><br /><a href="#ideas-ovari" title="Ideas, Planning, & Feedback">🤔</a> <a href="#translation-ovari" title="Translation">🌍</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aovari" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/perovsek"><img src="https://avatars.githubusercontent.com/u/115713273?v=4?s=100" width="100px;" alt="perovsek"/><br /><sub><b>perovsek</b></sub></a><br /><a href="#translation-perovsek" title="Translation">🌍</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Aperovsek" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://peter88213.github.io"><img src="https://avatars.githubusercontent.com/u/42072564?v=4?s=100" width="100px;" alt="peter88213"/><br /><sub><b>peter88213</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Apeter88213" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/qsodev"><img src="https://avatars.githubusercontent.com/u/11365470?v=4?s=100" width="100px;" alt="qsodev"/><br /><sub><b>qsodev</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aqsodev" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/samirodj"><img src="https://avatars.githubusercontent.com/u/36422980?v=4?s=100" width="100px;" alt="samirodj"/><br /><sub><b>samirodj</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Asamirodj" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/seryafarma"><img src="https://avatars0.githubusercontent.com/u/3274071?v=4?s=100" width="100px;" alt="seryafarma"/><br /><sub><b>seryafarma</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=seryafarma" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/shobeira"><img src="https://avatars.githubusercontent.com/u/43518764?v=4?s=100" width="100px;" alt="shobeira"/><br /><sub><b>shobeira</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Ashobeira" title="Bug reports">🐛</a> <a href="#ideas-shobeira" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/icfmp"><img src="https://avatars.githubusercontent.com/u/71736258?v=4?s=100" width="100px;" alt="sib@c"/><br /><sub><b>sib@c</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Aicfmp" title="Bug reports">🐛</a> <a href="#ideas-icfmp" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tompkins-ct"><img src="https://avatars.githubusercontent.com/u/58485783?v=4?s=100" width="100px;" alt="tompkins-ct"/><br /><sub><b>tompkins-ct</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Atompkins-ct" title="Bug reports">🐛</a> <a href="#ideas-tompkins-ct" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tronta"><img src="https://avatars1.githubusercontent.com/u/5135577?v=4?s=100" width="100px;" alt="tronta"/><br /><sub><b>tronta</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Atronta" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/vikdevelop"><img src="https://avatars.githubusercontent.com/u/83600218?v=4?s=100" width="100px;" alt="vikdevelop"/><br /><sub><b>vikdevelop</b></sub></a><br /><a href="#translation-vikdevelop" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/wrobell"><img src="https://avatars2.githubusercontent.com/u/105664?v=4?s=100" width="100px;" alt="wrobell"/><br /><sub><b>wrobell</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/commits?author=wrobell" title="Code">💻</a> <a href="https://github.com/gaphor/gaphor/commits?author=wrobell" title="Tests">⚠️</a> <a href="https://github.com/gaphor/gaphor/issues?q=author%3Awrobell" title="Bug reports">🐛</a> <a href="#design-wrobell" title="Design">🎨</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/FDzhang"><img src="https://avatars.githubusercontent.com/u/42018389?v=4?s=100" width="100px;" alt="zhangxinqiang"/><br /><sub><b>zhangxinqiang</b></sub></a><br /><a href="#translation-FDzhang" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/oscfdezdz"><img src="https://avatars.githubusercontent.com/u/42654671?v=4?s=100" width="100px;" alt="Óscar Fernández Díaz"/><br /><sub><b>Óscar Fernández Díaz</b></sub></a><br /><a href="#translation-oscfdezdz" title="Translation">🌍</a> <a href="https://github.com/gaphor/gaphor/commits?author=oscfdezdz" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/zlv"><img src="https://avatars.githubusercontent.com/u/602210?v=4?s=100" width="100px;" alt="Евгений Лежнин"/><br /><sub><b>Евгений Лежнин</b></sub></a><br /><a href="#translation-zlv" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/BrainKicker"><img src="https://avatars.githubusercontent.com/u/30545094?v=4?s=100" width="100px;" alt="Пётр Сабанов"/><br /><sub><b>Пётр Сабанов</b></sub></a><br /><a href="#translation-BrainKicker" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/pinxue"><img src="https://avatars.githubusercontent.com/u/958237?v=4?s=100" width="100px;" alt="品雪"/><br /><sub><b>品雪</b></sub></a><br /><a href="https://github.com/gaphor/gaphor/issues?q=author%3Apinxue" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
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
    GitHub to start making your changes to the **main** branch (or
    branch off of it).
3.  Write a test which shows that the bug was fixed or that the feature
    works as expected.
4.  Send a pull request and bug the maintainers until it gets merged and
    published. :smile:

See [the contributing guide](CONTRIBUTING.md)!

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
