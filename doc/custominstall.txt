Custom Python Installation Location
###################################

This page is based on `custom installation locations <http://peak.telecommunity.com/DevCenter/EasyInstall#custom-installation-locations>`, from the PEAK site.


Unix/Linux 
----------

#. Create `$HOME/.pydistutils.cfg`:
   ::

    [install]
    install_lib = ~/.py-site-packages
    install_scripts = ~/bin

#. Create (or extend) the `PYTHONPATH` environment variable (for (ba)sh):
   ::

    export PYTHONPATH=~/.py-site-packages

#. Run `setup.py` script to fetch and install dependencies
   ::
 
    python setup.py install

Prefix `~/.py-site-packages` can be changed to something more suitable for your setup.

 **Note for Linux users:** Make sure you have the `python-dev` package installed for your Python version, as some code needs to be compiled (those are packages Gaphor depends on, not Gaphor itself).

 **Note for Ubuntu Linux users:** Make sure you have the `build-essential` package installed. This package installs header files and what more, required to compile the C-extensions of `zope.interface`.

Windows
-------

  **NOTE:** For Windows users it may be simpler to just forget about custom installation locations. Just follow the instructions on [wiki:Win32] and you should be set.

The Windows installation is almost the same as for Unix.

Replace `yourname` with your login name.

#. Distutils requires a HOME variable where it can find the configuration file. So in your Control Panel -> System -> Advanced -> Environment Variables add the following:
   ::

    HOME=C:\Documents and Settings\yourname\Home


#. Create a directory `C:\Documents and Settings\yourname\Home`. Also create `%HOME%\py-site-packages`.

#. Eventually add the Python directory to your `PATH` (default is `C:\Python26`)

#. Create (or extend) `PYTHONPATH` variable:
   ::

    PYTHONPATH=%HOME%\py-site-packages

#. Create a file `%HOME%\pydistutils.cfg` with the following content:
   ::

    [install]
    install_lib=$home\py-site-packages
    install_scripts=$home\bin

    [build]
    compiler=mingw32

Now you should be able to do `python setup.py install` from the command line.

If you are a developer you should definitely install MinGW from http://mingw.org and add MinGW's `bin` directory to your path.

For a good Subversion client for Windows have a look at `TortoiseSVN <http://tortoisesvn.tigris.org/>`.


Mac OS X
--------

Mac OS X is quite simple: place the following in your `$HOME/.pydistutils.cfg`:
::

 [install]
 install_lib = ~/Library/Python/$py_version_short/site-packages
 install_scripts = ~/bin


