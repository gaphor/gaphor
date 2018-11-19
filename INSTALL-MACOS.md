# Gaphor on macOS

Running Gaphor on MacOS is a bit more involved.

First make sure [Homebrew](https://brew.sh) is installed.

Then from the command line install the following:

    $ brew install gobject-introspection gtk+3

Now install the Python 3 bindings:

    $ brew install pygobject3 py3cairo

Before installing Gaphor, you may want to create a Virtual env:

    $ python3 -m venv .gaphor

Edit `.gaphor/bin/activate` and add the following line:

    export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
And enable the venv:
    
    $ source .gaphor/bin/activate

Now make sure you run Gaphor by using Python 3.


* Install Gaphas, the canvas widget:


    $ python3 setup.py develop


