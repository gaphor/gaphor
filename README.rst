
Gaphor
======
The UML modeling tool.

|Code style: black|


Prerequisites
~~~~~~~~~~~~~

Current minimum requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Currently PyGTK is required for Windows, macOS, and Linux.


Future minimum requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Gaphor will soon require **Python 3**. Legacy Python 2 will no longer be supported.

* If you're on macOS, you will soon need to be on 10.7 (Lion) or newer.

* If you're on Linux, you will soon need to have GTK+ 3.10 or later. This is the version
  that ships starting with Ubuntu 14.04 and Fedora 20. You will also soon need to install
  the Python 3 bindings to GTK+.

* We're working on Windows support


Quickstart
~~~~~~~~~~

To install, run the following::

    $ pip install gaphor

Note
^^^^^
Gaphor is currently incompatible with versions of gaphas newer than 0.7.2 as later versions of gaphas use PyGObject, but gaphor uses PyGTK.

Therefore, gaphas must be pinned to version 0.7.2 with::

    $ python2 -m pip install -I gaphas==0.7.2

If a newer version is already installed in your environment, make sure to uninstall gaphas again before pinning the version.


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
.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
