Gaphor Mac OS X application bundle builder
==========================================

This module is used to create OS X app bundles for Gaphor. Nothing secret.

GTK+ and friends should be installed in /usr/local, using [Homebrew][1].  This
script picks up those files, drops them in a bundle and changes the link
references.

As said, the binary parts have to be present on the system. The rest is done
with [pip][2] in a [venv][3].

[1]: http://github.com/amolenaar/homebrew
[2]: https://pypi.org/project/pip/
[3]: https://docs.python.org/3/library/venv.html
