Gaphor on Linux
===============

Examples of Gaphor and Gaphas RPM spec files can be found in `PLD Linux <https://www.pld-linux.org/>`_
`repository <https://github.com/pld-linux/>`_:

 * https://github.com/pld-linux/python-gaphas
 * https://github.com/pld-linux/gaphor

Please, do not hesitate to contact us if you need help to create a Linux package
for Gaphor or Gaphas.

Development Environment
-----------------------

To setup a development environment with Linux, you first need the latest
stable version of Python. In order to get the latest stable version, we
recommend that you install `pyenv <https://github.com/pyenv/pyenv>`_.
Install the pyenv `prerequisites <https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites>`_
first, and then install pyenv:


    $ curl https://pyenv.run | bash


Make sure you follow the instruction at the end of the installation script
to install the commands in your shell's rc file. Finally install the latest
version of Python by executing:

    $ pyenv install 3.x.x

Where 3.x.x is replaced by the latest stable version of Python.

Next install the Gaphor prerequisites by installing the gobject introspection
and cairo build dependencies, for example in Ubuntu execute:


    $ sudo apt-get install -y python3-dev python3-gi python3-gi-cairo
    gir1.2-gtk-3.0 libgirepository1.0-dev libcairo2-dev

`Clone the repository <https://help.github.com/en/articles/cloning-a-repository>`_.

    $ cd gaphor
    $ source ./venv
    $ poetry run gaphor
