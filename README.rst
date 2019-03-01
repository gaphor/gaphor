
Gaphor
======

The UML modeling tool.

|build| |license| |pypi| |downloads| |code style|

.. NOTE::
   The latest release of Gaphor (0.17.2) uses Python 2.x and PyGTK. The master version is using Python 3.x and PyGobject (GObject-introspection).
   Since a 1.0 version of Gaphas (the canvas component) has been released lately, also requiring PyGObject and not PyGTK, the 1.0 version of Gaphas
   is incompatible with Gaphor 0.17.2.

   Therefore, when installing Gaphor via pip, Gaphas must be pinned to version 0.7.2 with::

      $ python2 -m pip install -I gaphas==0.7.2

   If a newer version is already installed in your environment, make sure to uninstall Gaphas again before pinning the version.

Prerequisites
~~~~~~~~~~~~~

Minimum requirements
^^^^^^^^^^^^^^^^^^^^

This is the software that should be present on your system prior to installing Gaphor.

* Python 3.x (Python 2 is not supported!)
* GTK+3 and GObject-introspection

If you're on Linux, you will soon need to have GTK+ 3.10 or later. This is the version
that ships starting with Ubuntu 14.04 and Fedora 20. You will also soon need to install
the Python 3 bindings to GTK+.

If you're on macOS, you will soon need to be on 10.7 (Lion) or newer.
GTK+3 and GObject-introspection should be installed with `Homebrew`_::

    $ brew install gobject-introspection gtk+3

We're working on Windows support.

Quickstart
~~~~~~~~~~

The easiest way to get started is to set up a project specific Virtual Environment::

    $ source ./venv
    $ gaphor

Documentation
~~~~~~~~~~~~~

Documentation for Gaphor can be found on `Read The Docs`_.

Community
~~~~~~~~~

You can talk to the community through:

* The `gaphor`_ channel on Gitter.

Contributing
~~~~~~~~~~~~

If you experience problems with Gaphor, `log them on GitHub`_. If you
want to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _Read The Docs: https://gaphor.readthedocs.io
.. _gaphor: https://gitter.im/gaphor/Lobby
.. _log them on Github: https://github.com/gaphor/gaphor/issues
.. _fork the code: https://github.com/gaphor/gaphor
.. _submit a pull request: https://github.com/gaphor/gaphor/pulls
.. _Homebrew: https://brew.sh
.. |build| image:: https://travis-ci.com/gaphor/gaphor.svg?branch=master
    :target: https://travis-ci.com/gaphor/gaphor
.. |license| image:: https://img.shields.io/pypi/l/gaphor.svg
    :target: https://github.com/gaphor/gaphor/blob/master/LICENSE.txt
.. |pypi| image:: https://img.shields.io/pypi/v/gaphor.svg
    :target: https://pypi.org/project/gaphor/
.. |downloads| image:: https://pepy.tech/badge/gaphor
    :target: https://pepy.tech/project/gaphor
.. |code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

