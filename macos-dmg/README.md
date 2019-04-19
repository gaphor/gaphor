Gaphor Mac OS X application bundle builder
==========================================

This module is used to create OS X app bundles for Gaphor. Nothing secret.

GTK+ and friends should be installed in /usr/local, using [Homebrew][1].
Same with pygtk. This script picks up those files, changes the link references
and drops them in a bundle.

As said, the binary parts have to be present on the system. The rest is done
with [virtualenv][2] and [easy_install][3].

While most of the stuff is static, some configuration files of GTK+ don't like changing. Those files are fixed and put in $HOME/.gaphor/bundle.

[1]: http://github.com/amolenaar/homebrew
[2]: http://pypi.python.org/pypi/virtualenv
[3]: http://pypi.python.org/pypi/setuptools
